"""Render the link-preview card and the home-screen icon (run when the design changes).

    uv run --with playwright python scripts/render_og.py

Writes static/og/card.png (1200x630) from scripts/og_card.html and
static/apple-touch-icon.png (180x180) from static/favicon.svg. Uses the
installed Chrome; set CHROME to another browser binary if needed.
"""

from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def main() -> None:
    card = ROOT / "static/og/card.png"
    icon = ROOT / "static/apple-touch-icon.png"
    card.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME)
        page = browser.new_page(viewport={"width": 1200, "height": 630})
        page.goto((ROOT / "scripts/og_card.html").as_uri())
        page.evaluate("document.fonts.ready")
        page.screenshot(path=card)
        page = browser.new_page(viewport={"width": 180, "height": 180})
        svg = (ROOT / "static/favicon.svg").read_text()
        page.set_content(
            f"<style>body{{margin:0}}svg{{width:180px;height:180px;display:block}}</style>{svg}"
        )
        page.screenshot(path=icon)
        browser.close()
    print(f"Wrote {card.relative_to(ROOT)} and {icon.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
