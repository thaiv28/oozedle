# Work log

Newest first. One entry per substantive change: what changed, checks actually run, remaining limits. At most 150 words each.

## 2026-10-21 — Stats pages and publishing workflows

Added Field Board player and tournament pages, leaderboard season/search controls, sortable ledgers, and a root-relative 404. Page contexts are computed in `site.py`; fractional source values are preserved. Added offline build/link tests, publish checks/build/deploy/keepalive and a manual Pages redirect workflow. Removed the old site and scripts. Checks: `uv run --no-sync ruff format`, `ruff check`, `pytest -q` (27 passed), and the real-data site build (51 players, 17 tournaments, 12 data warnings); JS syntax and diff whitespace checks passed. Plain `uv run` crashed in macOS system configuration; headless Chrome/Firefox aborted, so desktop/phone visuals and browser interactions remain unverified. Publishing remains in progress until the workflow runs on main; no deployment or redirect run was attempted.

## 2026-10-21 — Game rebuilt in the "Field Board" design

New Jinja2 site (`oozedle/site.py`, `templates/`, `static/`): the daily game picks one puzzle a day from any season in the browser, with arrow-only feedback, saved progress, share text, yesterday's answer and a season switch. Design chosen through impeccable (comp-led): approved comp `.impeccable/mocks/comp-1.png`; fonts Cossette Titre and Sofia Sans Condensed, self-hosted. Added AGENTS.md and steering docs. Checks: hero gate passed at 89% against the comp (phone capture, 390×585 @2.63x); the user accepted the first viewport; pytest and ruff pass. Limits: stats pages and publishing not built yet; old `oozedle/stats.py` and `scripts/setup_site.py` still present.

## 2026-10-21 — Drive sync, workbook parser, tidy dataset

`oozedle/drive.py`, `parse.py`, `dataset.py` and the sync/check scripts. Synced all 17 workbooks (4 new 2026 ones). Checks: pytest (offline fixtures), `check_data.py` on real data: 51 players, 92 games, 1,756 player-game rows; 12 warnings, all reviewed (see `tech.md`).
