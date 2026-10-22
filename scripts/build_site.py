"""Build the static site into output/ from the synced workbooks.

uv run python scripts/build_site.py            # site from data/raw
uv run python scripts/build_site.py --hero DIR # game page on the design comp's fixture
"""

from __future__ import annotations

import argparse
from pathlib import Path

from oozedle.config import OUTPUT_DIR
from oozedle.dataset import build_dataset
from oozedle.site import build, build_hero


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--hero", type=Path, help="write only the fixture game page here")
    args = parser.parse_args()
    if args.hero:
        build_hero(args.hero)
        print(f"Hero fixture written to {args.hero}")
        return
    ds = build_dataset()
    build(ds, args.out)
    print(
        f"Built {args.out}: {len(ds.players)} players, {len(ds.tournaments)} tournaments, "
        f"{len(ds.warnings)} data warnings (scripts/check_data.py lists them)"
    )


if __name__ == "__main__":
    main()
