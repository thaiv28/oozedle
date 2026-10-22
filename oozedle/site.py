"""Render the static site from a Dataset into OUTPUT_DIR."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from oozedle.config import OUTPUT_DIR, ROOT
from oozedle.dataset import Dataset

TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
EPOCH = "2026-10-22"  # puzzle #1
MIN_POINTS = 5  # lines with fewer points played are too thin to guess


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

    def asset_url(self, path: str, root: str) -> str:
        """Static URL with a content hash so browsers pick up changes."""
        if path not in self._hashes:
            digest = hashlib.sha256((STATIC_DIR / path).read_bytes()).hexdigest()[:10]
            self._hashes[path] = digest
        return f"{root}static/{path}?v={self._hashes[path]}"

    def render(self, template: str, dest: str, **context) -> None:
        depth = dest.count("/")
        root = "../" * depth
        html = self.env.get_template(template).render(
            root=root, asset=lambda p: self.asset_url(p, root), **context
        )
        target = self.out / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html)

    def copy_static(self) -> None:
        shutil.copytree(STATIC_DIR, self.out / "static", dirs_exist_ok=True)


def to_json(data: dict) -> str:
    """JSON safe to inline in a <script> element."""
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")


def build(ds: Dataset, out: Path = OUTPUT_DIR) -> None:
    if out.exists():
        shutil.rmtree(out)
    site = Site(out)
    site.copy_static()
    site.render("index.html.j2", "index.html", game_json=to_json(game_data(ds)))


def build_hero(out: Path) -> None:
    """The game page on the comp's fixture, for the impeccable hero gate."""
    if out.exists():
        shutil.rmtree(out)
    site = Site(out)
    site.copy_static()
    site.render("index.html.j2", "index.html", game_json=to_json(hero_game_data()))
