"""Local USAU ratings and explicit workbook-opponent aliases."""

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from oozedle.config import ROOT


@dataclass(frozen=True)
class Ratings:
    teams: dict[str, float]
    ranks: dict[str, int]
    as_of: str
    source: str


def load_ratings(directory: Path = ROOT / "ratings") -> dict[int, Ratings]:
    result = {}
    for path in sorted(Path(directory).glob("*.csv")):
        if not path.stem.isdigit():
            continue
        comment = path.read_text().splitlines()[0].removeprefix("#").strip()
        date = re.search(r"data through\s+([^;]+)", comment)
        source = re.search(r"source\s+(.+)", comment)
        frame = pd.read_csv(path, comment="#")
        result[int(path.stem)] = Ratings(
            dict(zip(frame.team, frame.rating.astype(float))),
            dict(zip(frame.team, frame["rank"].astype(int))),
            date.group(1).strip() if date else comment,
            source.group(1).strip() if source else comment,
        )
    return result


def load_aliases(path: Path) -> tuple[str, dict[str, str | None]]:
    data = (yaml.safe_load(path.read_text()) or {}) if path.exists() else {}
    return data.get("ooze", ""), data.get("opponents") or {}


def game_ratings(ds, ratings, aliases) -> pd.DataFrame:
    ooze, opponents = aliases
    rows = []
    for game in ds.games.itertuples():
        season = ratings.get(int(game.season))
        teams = season.teams if season else {}
        opponent = teams.get(opponents.get(game.opponent), np.nan)
        own = teams.get(ooze, np.nan)
        rows.append((game.game_id, opponent, own, opponent - own))
    return pd.DataFrame(
        rows, columns=["game_id", "opponent_rating", "ooze_rating", "gap"]
    ).set_index("game_id")
