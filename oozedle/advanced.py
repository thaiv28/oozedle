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
    possession: LinearFit


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
    possession = fit(frame, ("blocks", "turnovers"))
    return MarginModel(
        dict(
            assists=scoring.coef[0] / 2,
            goals=scoring.coef[0] / 2,
            blocks=scoring.coef[1],
            turnovers=scoring.coef[2],
        ),
        scoring,
        possession,
    )


def margin_added(row, weights) -> float:
    return float(sum(row[key] * weight for key, weight in weights.items()))


def per10(value, points_played) -> float | None:
    return 10 * value / points_played if points_played >= 20 else None
