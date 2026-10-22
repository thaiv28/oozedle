"""Fetch USAU college men's team ratings into ratings/<season>.csv (run locally, not in CI).

    uv run --with playwright python scripts/fetch_ratings.py [SEASON ...]

Past seasons come from Wayback Machine snapshots of frisbee-rankings.com (now
Ultiworld's Projected Rankings); the current season comes from the live page,
which sits behind Cloudflare, so it is loaded in the installed Chrome (a window
opens off-screen briefly). Set CHROME to use another browser binary.
"""

from __future__ import annotations

import csv
import os
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ratings"
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
LIVE = "https://projectedrankings.ultiworld.com/usau/college/men"
# The latest archived snapshot of each finished season.
SOURCES = {
    2024: "https://web.archive.org/web/20240419090629id_/https://www.frisbee-rankings.com/usau/college/men",
    2025: "https://web.archive.org/web/20250403125921id_/https://www.frisbee-rankings.com/usau/college/men",
    2026: LIVE,
}
BID = re.compile(r"\s+(AC|GL|ME|NE|NC|NW|OV|SC|SE|SW)\s+\d+$")


def team_name(raw: str) -> str:
    """One spelling across eras: drop bid labels ("SW 2"); "-B" becomes " [B]"."""
    name = BID.sub("", " ".join(raw.split()))
    return re.sub(r"-([B-E])$", r" [\1]", name)


def parse(html: str) -> tuple[str, list[dict]]:
    soup = BeautifulSoup(html, "html.parser")
    as_of = re.search(r"(?:updated|Updated) through ([^\n·]+?)(?:\s{2,}|\n|$)", soup.get_text("\n"))
    rows = []
    for tr in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
        if len(cells) < 5 or not cells[0].isdigit() or not cells[4]:
            continue  # header rows, and teams listed without a rating
        rows.append(
            {
                "rank": int(cells[0]),
                "team": team_name(cells[2]),
                "record": cells[3],
                "rating": float(cells[4]),
            }
        )
    return (as_of.group(1).strip() if as_of else ""), rows


def fetch_live() -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME, headless=False, args=["--window-position=-2000,0"]
        )
        page = browser.new_page()
        page.goto(LIVE, wait_until="commit", timeout=90000)
        page.wait_for_selector("table tr td", state="attached", timeout=90000)
        page.wait_for_timeout(1500)
        html = page.content()
        browser.close()
    return html


def main(seasons: list[int]) -> None:
    OUT.mkdir(exist_ok=True)
    for season in seasons:
        url = SOURCES[season]
        html = fetch_live() if url == LIVE else requests.get(url, timeout=120).text
        as_of, rows = parse(html)
        if len(rows) < 100:
            raise SystemExit(f"{season}: only {len(rows)} rows parsed from {url}")
        path = OUT / f"{season}.csv"
        with path.open("w", newline="") as f:
            f.write(f"# USAU college men, {season} season; data through {as_of}; source {url}\n")
            writer = csv.DictWriter(f, fieldnames=["rank", "team", "record", "rating"])
            writer.writeheader()
            writer.writerows(rows)
        print(f"{season}: {len(rows)} teams, through {as_of or '?'} -> {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main([int(s) for s in sys.argv[1:]] or sorted(SOURCES))
