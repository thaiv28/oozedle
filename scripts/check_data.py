"""Inspect local stats and optionally export tidy CSV tables."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from oozedle.dataset import build_dataset  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path)
    args = parser.parse_args()
    dataset = build_dataset()
    for season, tournaments in dataset.tournaments.groupby("season", sort=True):
        print(f"{season}:")
        for row in tournaments.sort_values("order").itertuples():
            print(f"  {row.order}. {row.name}: {row.wins}-{row.losses}")
    print(
        f"{len(dataset.players)} players, {len(dataset.games)} games, "
        f"{len(dataset.player_games)} player_games"
    )
    for warning in dataset.warnings:
        print(f"Warning: {warning}")
    if args.csv:
        dataset.write_csv(args.csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
