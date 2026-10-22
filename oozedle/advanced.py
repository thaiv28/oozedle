"""Reproducible game-margin linear models and derived advanced stats."""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class LinearFit:
    names: tuple[str, ...]
    coef: tuple[float, ...]
    intercept: float
    low: tuple[float, ...]
    high: tuple[float, ...]
    r2: float
    cv_r2: float
    n: int


@dataclass(frozen=True)
class MarginModel:
    weights: dict[str, float]
    scoring: LinearFit


def game_totals(ds) -> pd.DataFrame:
    """Use player sums, restricted to games with per-game player records."""
    stats = ["assists", "goals", "blocks", "turnovers"]
    totals = ds.player_games.groupby("game_id", as_index=False)[stats].sum()
    games = ds.games[["game_id", "tournament_id", "season", "goals_for", "goals_against"]]
    frame = games.merge(totals, on="game_id", validate="one_to_one")
    frame["margin"] = (frame.goals_for - frame.goals_against).astype(float)
    return frame[["game_id", "tournament_id", "season", "margin", *stats]]


def _r2(y, predicted):
    total = np.sum((y - y.mean()) ** 2)
    return float(1 - np.sum((y - predicted) ** 2) / total) if total else 0.0


def fit(frame, columns, target="margin", n_boot=2000, folds=10, seed=0) -> LinearFit:
    """OLS, pooled shuffled out-of-fold R², and game bootstrap slope intervals."""
    names = tuple(columns)
    y = frame[target].to_numpy(dtype=float)
    n = len(y)
    if not n:
        raise ValueError("Cannot fit a margin model without games")
    x = np.column_stack([np.ones(n), frame[list(names)].to_numpy(dtype=float)])
    coefficients = np.linalg.lstsq(x, y, rcond=None)[0]
    predictions = np.empty(n)
    if n > 1:
        order = np.random.default_rng(seed).permutation(n)
        for test in np.array_split(order, min(folds, n)):
            train = np.ones(n, dtype=bool)
            train[test] = False
            predictions[test] = x[test] @ np.linalg.lstsq(x[train], y[train], rcond=None)[0]
    else:
        predictions[:] = y
    rng = np.random.default_rng(seed)
    samples = np.empty((n_boot, len(names)))
    for i in range(n_boot):
        indices = rng.integers(0, n, n)
        samples[i] = np.linalg.lstsq(x[indices], y[indices], rcond=None)[0][1:]
    low, high = np.percentile(samples, [2.5, 97.5], axis=0)
    return LinearFit(
        names,
        tuple(coefficients[1:]),
        float(coefficients[0]),
        tuple(low),
        tuple(high),
        _r2(y, x @ coefficients),
        _r2(y, predictions),
        n,
    )


def fit_margin_model(ds) -> MarginModel:
    frame = game_totals(ds)
    frame["S"] = (frame.assists + frame.goals) / 2
    scoring = fit(frame, ("S", "blocks", "turnovers"))
    return MarginModel(
        dict(
            assists=scoring.coef[0] / 2,
            goals=scoring.coef[0] / 2,
            blocks=scoring.coef[1],
            turnovers=scoring.coef[2],
        ),
        scoring,
    )


def margin_added(row, weights) -> float:
    return float(sum(row[key] * weight for key, weight in weights.items()))


def per10(value, points_played) -> float | None:
    return 10 * value / points_played if points_played >= 20 else None


@dataclass(frozen=True)
class Shrinkage:
    """Per-10 rates pulled toward the team rate, as if each player also played
    `prior_points` more points at `mean_rate` (empirical Bayes)."""

    prior_points: float
    mean_rate: float

    def per10(self, value: float, points_played: float) -> float | None:
        if points_played <= 0:
            return None
        if np.isinf(self.prior_points):
            return 10 * self.mean_rate
        return (
            10 * (value + self.prior_points * self.mean_rate) / (points_played + self.prior_points)
        )


def fit_shrinkage(games: pd.DataFrame, mean_rate: float) -> Shrinkage:
    """Method of moments on per-game lines (player_id, points_played, value).

    Per-point noise comes from each player's games around their own rate; the true
    spread between players is what remains of the observed spread after that noise.
    prior_points = noise variance / true-skill variance.
    """
    lines = games[games.points_played > 0]
    totals = lines.groupby("player_id")[["value", "points_played"]].sum()
    if len(totals) < 2 or len(lines) <= len(totals):
        return Shrinkage(0.0, mean_rate)
    own = lines.player_id.map(totals.value / totals.points_played)
    residual = lines.value / lines.points_played - own
    noise = float((lines.points_played * residual**2).sum() / (len(lines) - len(totals)))
    rates = totals.value / totals.points_played
    observed = float(np.average((rates - mean_rate) ** 2, weights=totals.points_played))
    skill = observed - noise * len(totals) / float(totals.points_played.sum())
    return Shrinkage(noise / skill if skill > 0 else float("inf"), mean_rate)


@dataclass(frozen=True)
class Difficulty:
    a: float
    b: float
    n_rated: int
    n_fit: int
    r2: float
    gap_min: float
    gap_max: float
    gap_mean: float

    def factor(self, gap: float) -> float:
        if np.isnan(gap):
            return 1.0
        clamped = np.clip(gap, self.gap_min, self.gap_max)
        return float(np.exp(-self.b * (clamped - self.gap_mean)))


def fit_difficulty(ds, weights, game_ratings) -> Difficulty:
    """Fit game MA per score point against opponent-minus-Ooze ratings."""
    lines = ds.player_games.copy()
    lines["ma"] = sum(lines[key] * weight for key, weight in weights.items())
    sums = lines.groupby("game_id").ma.sum()
    games = ds.games.set_index("game_id").join(game_ratings[["gap"]])
    rated = games[np.isfinite(games.gap)]
    rate = sums.reindex(games.index) / (games.goals_for + games.goals_against)
    usable = np.isfinite(games.gap) & np.isfinite(rate) & (rate > 0)
    gaps = games.loc[usable, "gap"].to_numpy(dtype=float)
    y = np.log(rate[usable].to_numpy(dtype=float))
    a = b = r2 = 0.0
    if len(y):
        x = np.column_stack([np.ones(len(y)), gaps])
        a, b = np.linalg.lstsq(x, y, rcond=None)[0]
        r2 = _r2(y, x @ np.array([a, b]))
    return Difficulty(
        float(a),
        float(b),
        len(rated),
        len(y),
        r2,
        float(rated.gap.min()) if len(rated) else 0.0,
        float(rated.gap.max()) if len(rated) else 0.0,
        float(rated.gap.mean()) if len(rated) else 0.0,
    )
