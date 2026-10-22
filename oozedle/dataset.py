"""Build tidy, validated tables from local tournament workbooks."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, fields
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import yaml

from oozedle.config import MANIFEST, PLAYERS_FILE, RAW_DIR, TOURNAMENTS_FILE
from oozedle.parse import STATS, PlayerLine, parse_workbook

COLUMNS = {
    "players": "player_id name first_season last_season seasons tournaments".split(),
    "tournaments": (
        "tournament_id season name slug order created modified games wins losses "
        "goals_for goals_against"
    ).split(),
    "games": (
        "game_id tournament_id season index opponent opponent_label goals_for goals_against "
        "result team_points team_blocks team_turnovers clean_holds"
    ).split(),
    "player_games": (
        "player_id game_id tournament_id season points_played assists goals blocks turnovers result"
    ).split(),
    "player_tournaments": (
        "player_id tournament_id season points_played assists goals blocks turnovers "
        "games_played wins losses"
    ).split(),
}


@dataclass
class Dataset:
    players: pd.DataFrame
    tournaments: pd.DataFrame
    games: pd.DataFrame
    player_games: pd.DataFrame
    player_tournaments: pd.DataFrame
    warnings: list[str]

    def write_csv(self, directory: Path) -> None:
        """Write each tidy table with headers and no pandas index."""
        directory.mkdir(parents=True, exist_ok=True)
        for name in COLUMNS:
            getattr(self, name).to_csv(directory / f"{name}.csv", index=False)


def load_manifest() -> list[dict]:
    """Read the synchronized file metadata, or return an empty listing."""
    return json.loads(MANIFEST.read_text())["files"] if MANIFEST.exists() else []


def load_aliases(path: Path = PLAYERS_FILE) -> dict[str, str]:
    """Read the optional raw-name to canonical-name map."""
    if not path.exists():
        return {}
    return (yaml.safe_load(path.read_text()) or {}).get("aliases") or {}


def slugify(s: str) -> str:
    """Make an ASCII identifier suitable for URLs and table joins."""
    ascii_name = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")


def load_order(path: Path = TOURNAMENTS_FILE) -> dict[int, list[str]]:
    """Per-season tournament order overrides: {season: [tournament name, ...]}."""
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text()) or {}
    return {int(season): list(names) for season, names in (data.get("order") or {}).items()}


def tournament_name(entry: dict) -> str:
    name = Path(entry["name"]).stem if entry["name"].endswith(".xlsx") else entry["name"]
    return name.removesuffix(" Stats")


def _created_key(entry: dict) -> tuple:
    value = entry.get("created")
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None
    if stamp and stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=UTC)
    return (
        int(entry["season"]),
        entry.get("_local_only", False),
        stamp is None,
        stamp or datetime.max.replace(tzinfo=UTC),
        entry["name"],
    )


def build_dataset(
    raw_dir: Path = RAW_DIR,
    manifest: list[dict] | None = None,
    aliases: dict[str, str] | None = None,
    order: dict[int, list[str]] | None = None,
) -> Dataset:
    """Parse local inputs, merge aliases, and report consistency problems."""
    manifest = list(load_manifest() if manifest is None else manifest)
    aliases = load_aliases() if aliases is None else aliases
    warnings: list[str] = []
    known = {entry["path"] for entry in manifest}
    for path in sorted(raw_dir.glob("*/*.xlsx")):
        relative = path.relative_to(raw_dir).as_posix()
        if relative not in known and path.parent.name.isdigit():
            manifest.append(
                dict(
                    season=int(path.parent.name),
                    name=path.stem,
                    path=relative,
                    created=None,
                    modified=None,
                    _local_only=True,
                )
            )
            warnings.append(f"{relative}: workbook missing from manifest")
    tables: dict[str, list[dict]] = {name: [] for name in COLUMNS}
    people: dict[str, dict] = {}
    orders: dict[int, int] = defaultdict(int)
    order = load_order() if order is None else order

    def chronological(entry: dict) -> tuple:
        # Listed tournaments first, in the listed order; the rest by Drive creation time.
        listed = order.get(int(entry["season"]), [])
        name = tournament_name(entry)
        position = listed.index(name) if name in listed else len(listed)
        season, *rest = _created_key(entry)
        return (season, position, *rest)

    for entry in sorted(manifest, key=chronological):
        season = int(entry["season"])
        path = raw_dir / entry["path"]
        if not path.exists():
            warnings.append(f"{entry['path']}: manifest workbook missing locally")
            continue
        workbook = parse_workbook(path)
        warnings.extend(f"{entry['path']}: {warning}" for warning in workbook.warnings)
        name = tournament_name(entry)
        slug = slugify(name)
        tid = f"{season}-{slug}"
        orders[season] += 1
        if not workbook.games:
            warnings.append(f"{tid}: zero games")
        if not workbook.summary:
            warnings.append(f"{tid}: zero players")
        tables["tournaments"].append(
            dict(
                tournament_id=tid,
                season=season,
                name=name,
                slug=slug,
                order=orders[season],
                created=entry.get("created"),
                modified=entry.get("modified"),
                games=len(workbook.games),
                wins=sum(g.goals_for > g.goals_against for g in workbook.games),
                losses=sum(g.goals_for < g.goals_against for g in workbook.games),
                goals_for=sum(g.goals_for for g in workbook.games),
                goals_against=sum(g.goals_against for g in workbook.games),
            )
        )

        def merge(lines: list[PlayerLine], warn: bool = False) -> dict[str, dict]:
            merged: dict[str, dict] = {}
            raw_names: dict[str, set[str]] = defaultdict(set)
            for line in lines:
                canonical = aliases.get(line.name, line.name).strip()
                pid = slugify(canonical)
                raw_names[pid].add(line.name)
                if pid not in merged:
                    merged[pid] = {stat: 0 for stat in STATS}
                    merged[pid]["name"] = canonical
                for stat in STATS:
                    merged[pid][stat] += getattr(line, stat)
            if warn:
                for pid, names in raw_names.items():
                    if len(names) > 1:
                        warnings.append(
                            f"{tid}: merged aliases for {pid}: {', '.join(sorted(names))}"
                        )
            return merged

        summary = merge(workbook.summary, warn=True)
        per_player: dict[str, list[dict]] = defaultdict(list)
        for game in workbook.games:
            gid = f"{tid}-g{game.index}"
            result = (
                "W"
                if game.goals_for > game.goals_against
                else "L"
                if game.goals_for < game.goals_against
                else "T"
            )
            tables["games"].append(
                dict(
                    game_id=gid,
                    tournament_id=tid,
                    season=season,
                    result=result,
                    **{f.name: getattr(game, f.name) for f in fields(game)},
                )
            )
            lines = merge(workbook.player_games.get(game.index, []))
            if sum(line["goals"] for line in lines.values()) > game.goals_for:
                warnings.append(f"{gid}: sum of player goals exceeds goals_for")
            for pid, line in lines.items():
                row = dict(
                    player_id=pid,
                    game_id=gid,
                    tournament_id=tid,
                    season=season,
                    result=result,
                    **{s: line[s] for s in STATS},
                )
                tables["player_games"].append(row)
                per_player[pid].append(row)
        for pid, line in summary.items():
            played = per_player[pid]
            differing = [s for s in STATS if sum(r[s] for r in played) != line[s]]
            if workbook.player_games and differing:
                warnings.append(
                    f"{tid}: {line['name']} per-game totals differ: {', '.join(differing)}"
                )
            tables["player_tournaments"].append(
                dict(
                    player_id=pid,
                    tournament_id=tid,
                    season=season,
                    **{s: line[s] for s in STATS},
                    games_played=len(played),
                    wins=sum(r["result"] == "W" for r in played),
                    losses=sum(r["result"] == "L" for r in played),
                )
            )
            person = people.setdefault(pid, dict(name=line["name"], seasons=set(), tournaments=0))
            person["seasons"].add(season)
            person["tournaments"] += 1
    for pid, person in sorted(people.items()):
        seasons = sorted(person["seasons"])
        tables["players"].append(
            dict(
                player_id=pid,
                name=person["name"],
                first_season=min(seasons),
                last_season=max(seasons),
                seasons=",".join(map(str, seasons)),
                tournaments=person["tournaments"],
            )
        )
    frames = {name: pd.DataFrame(rows, columns=COLUMNS[name]) for name, rows in tables.items()}
    for column in ("team_points", "team_blocks", "team_turnovers", "clean_holds"):
        frames["games"][column] = frames["games"][column].astype("Int64")
    return Dataset(**frames, warnings=warnings)
