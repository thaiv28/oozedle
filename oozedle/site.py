"""Render the static site from a Dataset into OUTPUT_DIR."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

from oozedle.advanced import (
    MarginModel,
    fit_difficulty,
    fit_margin_model,
    fit_shrinkage,
    margin_added,
    per10,
)
from oozedle.config import OUTPUT_DIR, ROOT
from oozedle.dataset import Dataset
from oozedle.ratings import game_ratings, load_aliases, load_ratings

TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
EPOCH = "2026-10-21"  # puzzle #1
MIN_POINTS = 5  # lines with fewer points played are too thin to guess
SITE_URL = "https://oozedle.thaiv.dev/"  # link previews need absolute URLs


def game_data(ds: Dataset) -> dict:
    """The compact JSON the game reads: tournaments, players and every stat line."""
    tournaments = ds.tournaments.sort_values(["season", "order"]).reset_index(drop=True)
    t_index = {tid: i for i, tid in enumerate(tournaments.tournament_id)}
    players = ds.players.sort_values("name").reset_index(drop=True)
    p_index = {pid: i for i, pid in enumerate(players.player_id)}
    rows = ds.player_tournaments[ds.player_tournaments.points_played > 0].copy()
    rows["t"] = rows.tournament_id.map(t_index)
    rows["p"] = rows.player_id.map(p_index)
    rows = rows.sort_values(["t", "p"])
    stats = ["points_played", "assists", "goals", "blocks", "turnovers"]
    return {
        "epoch": EPOCH,
        "minPoints": MIN_POINTS,
        "seasons": sorted(int(s) for s in tournaments.season.unique()),
        "tournaments": [
            {"id": r.tournament_id, "name": r.name, "season": int(r.season)}
            for r in tournaments.itertuples()
        ],
        "players": [{"name": r.name, "slug": r.player_id} for r in players.itertuples()],
        "lines": [
            [int(r.t), int(r.p), *(int(getattr(r, s)) for s in stats)] for r in rows.itertuples()
        ],
    }


HERO_FIXTURE = {
    "players": ["Colin", "Farmer", "Hugo", "Mithu", "Rowan"],
    # answer Mithu: 20 PP, 2 A, 3 G, 1 B, 2 T gives the approved comp's arrows
    "lines": {
        "Colin": [18, 3, 3, 1, 4],
        "Farmer": [25, 2, 1, 2, 1],
        "Hugo": [12, 3, 2, 1, 2],
        "Mithu": [20, 2, 3, 1, 2],
        "Rowan": [15, 4, 1, 3, 2],
    },
}


def hero_game_data() -> dict:
    """Synthetic data that reproduces the approved comp's board (puzzle #214)."""
    names = HERO_FIXTURE["players"]
    return {
        "epoch": "2026-03-22",
        "minPoints": MIN_POINTS,
        "seasons": [2024, 2025, 2026],
        "tournaments": [{"id": "2026-pdq", "name": "PDQ", "season": 2026}],
        "players": [{"name": n, "slug": n.lower()} for n in names],
        "lines": [[0, i, *HERO_FIXTURE["lines"][n]] for i, n in enumerate(names)],
        "override": {
            "date": "2026-10-21",
            "dateLabel": "Tue Oct 21",  # the comp's words, kept verbatim for the hero gate
            "number": 214,
            "tournament": 0,
            "answer": names.index("Mithu"),
            "guesses": [names.index(n) for n in ("Rowan", "Farmer", "Colin")],
            "yesterday": {"name": "Hugo", "pool": "SVR 2026", "stats": [12, 3, 2, 1, 2]},
        },
    }


class Site:
    def __init__(self, out: Path = OUTPUT_DIR):
        self.out = out
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATES_DIR),
            autoescape=select_autoescape(["html", "j2"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._hashes: dict[str, str] = {}
        self.env.filters["statnum"] = statnum

    def asset_url(self, path: str, root: str) -> str:
        """Static URL with a content hash so browsers pick up changes."""
        if path not in self._hashes:
            digest = hashlib.sha256((STATIC_DIR / path).read_bytes()).hexdigest()[:10]
            self._hashes[path] = digest
        return f"{root}static/{path}?v={self._hashes[path]}"

    def render(self, template: str, dest: str, root: str | None = None, **context) -> None:
        depth = dest.count("/")
        root = "../" * depth if root is None else root
        html = self.env.get_template(template).render(
            root=root,
            asset=lambda p: self.asset_url(p, root),
            absolute_asset=lambda p: self.asset_url(p, SITE_URL),
            page_url=SITE_URL + ("" if dest == "index.html" else dest),
            **context,
        )
        target = self.out / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html)

    def copy_static(self) -> None:
        shutil.copytree(STATIC_DIR, self.out / "static", dirs_exist_ok=True)


def to_json(data: dict | list) -> str:
    """JSON safe to inline in a <script> element."""
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")


def build(ds: Dataset, out: Path = OUTPUT_DIR, ratings_dir: Path = ROOT / "ratings") -> None:
    if out.exists():
        shutil.rmtree(out)
    site = Site(out)
    site.copy_static()
    site.render("index.html.j2", "index.html", game_json=to_json(game_data(ds)))
    model = fit_margin_model(ds)
    context = stats_context(ds, model, ratings_dir)
    site.render("players.html.j2", "players.html", **context)
    site.render("advanced.html.j2", "advanced.html", **context)
    site.render("tournaments.html.j2", "tournaments.html", **context)
    for player in context["players"]:
        site.render("player.html.j2", f"players/{player['player_id']}.html", player=player)
    for tournament in context["tournaments"]:
        site.render(
            "tournament.html.j2",
            f"tournaments/{tournament['tournament_id']}.html",
            tournament=tournament,
        )
    for kind in ("performances", "seasons", "careers"):
        site.render("ranking.html.j2", f"advanced/{kind}.html", kind=kind, **context)
    site.render("404.html.j2", "404.html", root="/")


def build_hero(out: Path) -> None:
    """The game page on the comp's fixture, for the impeccable hero gate."""
    if out.exists():
        shutil.rmtree(out)
    site = Site(out)
    site.copy_static()
    site.render("index.html.j2", "index.html", game_json=to_json(hero_game_data()))


STAT_COLUMNS = ["points_played", "assists", "goals", "blocks", "turnovers"]
TOTAL_COLUMNS = [*STAT_COLUMNS, "games_played", "wins", "losses"]


def number(value):
    """Keep fractional source values and emit whole numbers as ints."""
    if pd.isna(value):
        return None
    return int(value) if float(value).is_integer() else float(value)


def totals(frame) -> dict:
    values = {key: number(frame[key].sum()) for key in TOTAL_COLUMNS}
    values["tournaments"] = int(frame.tournament_id.nunique())
    return values


def statnum(value, decimals=None):
    """Display missing values and use the mathematical minus glyph."""
    if value is None:
        return "—"
    text = f"{value:.{decimals}f}" if decimals is not None else str(value)
    if float(text) == 0:
        text = text.lstrip("-")  # no "−0.0" from rounding a small negative
    return text.replace("-", "−")


def stats_context(
    ds: Dataset, model: MarginModel | None = None, ratings_dir: Path = ROOT / "ratings"
) -> dict:
    """Precompute page joins, ordering, and totals; templates only present values."""

    model = model or fit_margin_model(ds)

    ratings = load_ratings(ratings_dir)
    aliases = load_aliases(Path(ratings_dir) / "aliases.yml")
    rated_games = game_ratings(ds, ratings, aliases)
    difficulty = fit_difficulty(ds, model.weights, rated_games)
    factors = rated_games.gap.map(difficulty.factor)
    player_tournaments = ds.player_tournaments.copy()
    player_games = ds.player_games.copy()
    player_games["factor"] = player_games.game_id.map(factors)
    tournament_factors = {}
    for tid, frame in ds.games.groupby("tournament_id"):
        points = frame.goals_for + frame.goals_against
        tournament_factors[tid] = (
            float(np.average(frame.game_id.map(factors), weights=points))
            if points.sum() > 0
            else 1.0
        )
    player_factors = {}
    for key, frame in player_games.groupby(["player_id", "tournament_id"]):
        player_factors[key] = (
            float(np.average(frame.factor, weights=frame.points_played))
            if frame.points_played.sum() > 0
            else tournament_factors.get(key[1], 1.0)
        )
    player_tournaments["adj_ma"] = [
        margin_added(row._asdict(), model.weights)
        * player_factors.get(
            (row.player_id, row.tournament_id), tournament_factors.get(row.tournament_id, 1.0)
        )
        for row in player_tournaments.itertuples()
    ]

    game_lines = player_games.assign(
        value=sum(player_games[key] * weight for key, weight in model.weights.items())
        * player_games.factor.fillna(1.0)
    )
    points = float(player_tournaments.points_played.sum())
    mean_rate = float(player_tournaments.adj_ma.sum()) / points if points else 0.0
    shrinkage = fit_shrinkage(game_lines, mean_rate)

    def aggregate(frame):
        return dict(totals(frame), adj_ma=float(frame.adj_ma.sum()))

    def advanced(row):
        row["ma"] = margin_added(row, model.weights)
        row["ma_per10"] = per10(row["ma"], row["points_played"])
        row.setdefault("adj_ma", row["ma"])
        row["adj_ma_per10"] = shrinkage.per10(row["adj_ma"], row["points_played"])
        return row

    def records(frame):
        return [
            {
                key: number(value) if isinstance(value, (int, float)) else value
                for key, value in row.items()
            }
            for row in frame.to_dict("records")
        ]

    people = {p["player_id"]: p for p in records(ds.players)}
    tournaments = records(ds.tournaments.sort_values(["season", "order"]))
    by_id = {t["tournament_id"]: t for t in tournaments}
    games = {}
    for game in records(ds.games.sort_values("index")):
        rating = rated_games.loc[game["game_id"]]
        game["opponent_rating"] = number(rating.opponent_rating)
        game["factor"] = difficulty.factor(rating.gap) if np.isfinite(rating.gap) else None
        games[game["game_id"]] = game
    for t in tournaments:
        tid = t["tournament_id"]
        t["games_list"] = [g for g in games.values() if g["tournament_id"] == tid]
        t["has_clean_holds"] = any(g["clean_holds"] is not None for g in t["games_list"])
        box = records(player_tournaments[player_tournaments.tournament_id == tid])
        for line in box:
            line["name"] = people[line["player_id"]]["name"]
            advanced(line)
        t["box"] = sorted(box, key=lambda r: (-r["points_played"], r["name"]))
    season_rows = []
    for season, frame in ds.tournaments.groupby("season", sort=True):
        ts = [t for t in tournaments if t["season"] == season]
        for i, t in enumerate(ts):
            t["previous"] = ts[i - 1] if i else None
            t["next"] = ts[i + 1] if i + 1 < len(ts) else None
        season_rows.append(
            dict(
                season=int(season),
                count=len(ts),
                tournaments=ts,
                wins=int(frame.wins.sum()),
                losses=int(frame.losses.sum()),
            )
        )
    players = []
    season_lines = []
    for pid, frame in player_tournaments.groupby("player_id"):
        player = dict(people[pid], career=advanced(aggregate(frame)))
        seasons = []
        for season, lines in frame.groupby("season", sort=True):
            row = advanced(dict(season=int(season), **aggregate(lines)))
            seasons.append(row)
            season_lines.append(dict(player_id=pid, name=player["name"], **row))
        years = [s["season"] for s in seasons]
        player["year_range"] = str(years[0]) if len(years) == 1 else f"{years[0]}–{years[-1]}"
        player["season_rows"] = list(reversed(seasons))
        entries = []
        for row in records(frame):
            t = by_id[row["tournament_id"]]
            entry = advanced(dict(row, name=t["name"], order=t["order"]))
            lines = ds.player_games[
                (ds.player_games.player_id == pid)
                & (ds.player_games.tournament_id == t["tournament_id"])
            ]
            entry["games_list"] = [
                advanced(dict(games[line["game_id"]], **{s: line[s] for s in STAT_COLUMNS}))
                for line in records(lines)
            ]
            entry["games_list"].sort(key=lambda g: g["index"])
            entries.append(entry)
        player["tournament_rows"] = sorted(
            entries, key=lambda r: (r["season"], r["order"]), reverse=True
        )
        players.append(player)
    players.sort(key=lambda p: (-p["career"]["points_played"], p["name"]))
    performances = [
        dict(line, tournament_name=t["name"], season=t["season"])
        for t in tournaments
        for line in t["box"]
    ]
    performances.sort(key=lambda r: (-r["adj_ma"], r["name"], r["tournament_id"]))
    best = {}
    for line in performances:
        best.setdefault(line["tournament_name"], line)
    by_adj = lambda r: (-r["adj_ma"], r["name"])  # noqa: E731
    best_seasons = sorted(season_lines, key=by_adj)
    best_careers = sorted(
        (
            dict(p["career"], player_id=p["player_id"], name=p["name"], seasons=p["year_range"])
            for p in players
        ),
        key=by_adj,
    )
    return dict(
        all_performances=performances,
        all_seasons=best_seasons,
        all_careers=best_careers,
        best_seasons=best_seasons[:10],
        best_careers=best_careers[:10],
        model=model,
        difficulty=difficulty,
        ratings_available=bool(ratings),
        adjustment_pct=100 * (1 - np.exp(100 * difficulty.b)),
        gap_factors=[
            dict(gap=gap, factor=difficulty.factor(gap)) for gap in (-1000, -500, 0, 500, 1000)
        ],
        season_ratings=[
            dict(
                season=year,
                rating=number(r.teams[aliases[0]]),
                rank=r.ranks[aliases[0]],
                as_of=r.as_of,
            )
            for year, r in sorted(ratings.items())
            if aliases[0] in r.teams
        ],
        best_performances=performances[:10],
        best_tournaments=[best[name] for name in sorted(best)],
        players=players,
        tournaments=tournaments,
        season_rows=list(reversed(season_rows)),
        players_json=to_json(
            dict(
                weights=model.weights,
                shrink=dict(
                    # JSON has no infinity; a huge prior is the same in practice
                    prior_points=min(shrinkage.prior_points, 1e9),
                    mean_rate=shrinkage.mean_rate,
                ),
                lines=season_lines,
            )
        ),
        shrinkage=shrinkage,
    )
