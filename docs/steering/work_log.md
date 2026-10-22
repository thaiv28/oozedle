# Work log

Newest first. One entry per substantive change: what changed, checks actually run, remaining limits. At most 150 words each.

## 2026-10-21 — Live on oozedle.thaiv.dev

Merged the revamp; the first `publish.yml` run on main deployed (check, build, deploy green). Verified live: home, players, a player page, a tournament page and the favicon return 200, and a missing page returns 404. Ran `pages-redirect.yml`: thaiv28.github.io/oozedle and the year pages redirect (checked with curl). Pages stays on to serve the redirect; docs corrected. Set the repo homepage. Recorded that "Juice" is not an alias. Updated impeccable to 4.7.0; `impeccable doctor` reports only an unset `buildPath`.

## 2026-10-21 — Finish review fixes

Impeccable finish review (two rounds, fresh reviewer): fix, then fix with all eight items resolved or disclosed. Changes: phone tables drop Tourn./GP and "#" under 520px and use auto layout (no table or page overflow at 390, measured); board scales again at ≥1100px; season rail styled as chips; text column heads left, narrow "#" column; current-row number 19px. Bug found while capturing: an ended game left the guess form visible (`display: grid` beat `[hidden]`); fixed globally. Checks: pytest, ruff, headless loss and win play-throughs, share text, focus capture, PR CI (check and build green, live Drive sync 17/17). Limit: the responsive gate stays open by decision (it compares desktop to the phone comp); recorded with `build-phase note`.

## 2026-10-21 — Visual pass on the whole site

Batched desktop (1440) and phone (390) review of every page type. Fixed: stats pages' top bar and footer now share the 960px measure; career row fits phones; lighter link underlines in tables; game board scales up at ≥720px; share header reads "SVR 2026"; SVG favicon; puzzle #1 is 2026-10-21; disclosure marker redrawn. Played a full game headless (autocomplete, unknown-name error, loss, share text, reload restores progress, record, season switch) and exercised leaderboard season/search/sort. Checks: pytest, ruff, impeccable detect (clean). Limit: impeccable's responsive gate compares the desktop capture to the phone comp and fails by construction (51%); not chased.

## 2026-10-21 — Stats pages and publishing workflows

Added Field Board player and tournament pages, leaderboard season/search controls, sortable ledgers, and a root-relative 404. Page contexts are computed in `site.py`; fractional source values are preserved. Added offline build/link tests, publish checks/build/deploy/keepalive and a manual Pages redirect workflow. Removed the old site and scripts. Checks: `uv run --no-sync ruff format`, `ruff check`, `pytest -q` (27 passed), and the real-data site build (51 players, 17 tournaments, 12 data warnings); JS syntax and diff whitespace checks passed. Plain `uv run` crashed in macOS system configuration; headless Chrome/Firefox aborted, so desktop/phone visuals and browser interactions remain unverified. Publishing remains in progress until the workflow runs on main; no deployment or redirect run was attempted.

## 2026-10-21 — Game rebuilt in the "Field Board" design

New Jinja2 site (`oozedle/site.py`, `templates/`, `static/`): the daily game picks one puzzle a day from any season in the browser, with arrow-only feedback, saved progress, share text, yesterday's answer and a season switch. Design chosen through impeccable (comp-led): approved comp `.impeccable/mocks/comp-1.png`; fonts Cossette Titre and Sofia Sans Condensed, self-hosted. Added AGENTS.md and steering docs. Checks: hero gate passed at 89% against the comp (phone capture, 390×585 @2.63x); the user accepted the first viewport; pytest and ruff pass. Limits: stats pages and publishing not built yet; old `oozedle/stats.py` and `scripts/setup_site.py` still present.

## 2026-10-21 — Drive sync, workbook parser, tidy dataset

`oozedle/drive.py`, `parse.py`, `dataset.py` and the sync/check scripts. Synced all 17 workbooks (4 new 2026 ones). Checks: pytest (offline fixtures), `check_data.py` on real data: 51 players, 92 games, 1,756 player-game rows; 12 warnings, all reviewed (see `tech.md`).
