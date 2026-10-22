"""Synchronize the public season workbooks."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from oozedle.config import RAW_DIR  # noqa: E402
from oozedle.drive import listing_fingerprint, sync  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--fingerprint", action="store_true")
    args = parser.parse_args()
    if args.fingerprint:
        fingerprint = listing_fingerprint()
        print(fingerprint)
        code = 0
    else:
        result = sync(force=args.force)
        fingerprint = result.fingerprint
        counts = ", ".join(
            f"{len(getattr(result, name))} {name}"
            for name in ("downloaded", "unchanged", "removed", "skipped", "failed")
        )
        failures = f" Failed: {', '.join(result.failed)}." if result.failed else ""
        print(f"{counts}.{failures} Fingerprint: {fingerprint}")
        code = int(
            bool(result.failed)
            and any(
                not any((RAW_DIR / str(season)).glob("*.xlsx")) for season in result.failed_seasons
            )
        )
    if output := os.environ.get("GITHUB_OUTPUT"):
        with Path(output).open("a") as stream:
            stream.write(f"fingerprint={fingerprint}\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
