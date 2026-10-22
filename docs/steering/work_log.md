# Work log

## 2026-10-22 — Shrunk Adj. MA per 10

Adj. MA per 10 is now shrunk toward the team rate (empirical Bayes): k ≈ 49 prior points, team rate 0.97 per 10, fit each build from per-game adjusted lines. Replaces the 20-point cutoff for that column; leaderboard JS uses the same k and rate after season filtering. Career leaders: Rowan 1.72, Hugo 1.67, Peter 1.60. Checks: new unit tests (formula, recovery of k on synthetic data), pytest, ruff, server vs browser values compared on localhost.

## 2026-10-22 — Roles page and Plays most like removed

Removed `roles.html`, `roles.js`, its CSS, links and docs, and the "Plays most like" line on player pages, at the user's request. Checks: pytest, ruff, build; grep finds no roles references.

## 2026-10-21 — Opponent adjustment and Roles

Added local USAU ratings joins, the log MA-per-point difficulty fit, and Summary-based Adj. MA weighted by each player's game PP. Leaderboard season filtering sums adjusted totals; tournament games show ratings/factors with a shared view switch. Added the season/career Roles map, accessible chart ledger, player search paths, and nearest-season “Plays most like” links.

Observed a=−0.542857721, b=−0.001131162; R²=0.394630409; 82 rated games, 80 fitted. Played-game factors range 0.311791–3.107335; rating gaps −1011.29–1021.30.

Checks: Ruff format/check, pytest (37 passed), JS syntax, static UI review, and real build (51 players, 17 tournaments, 12 existing warnings) passed. Browser launch was denied by the sandbox, so desktop/390px visual inspection remains unverified. No network, commits, or publishing.

## 2026-10-22 — Link previews

Added Open Graph/Twitter tags, a canonical link and an apple-touch icon to every page, with absolute URLs; player and tournament pages describe themselves (e.g. "2024–2026 · 13 tournaments · 68 games · MA 52.8"). The 1200×630 card is a committed render of `scripts/og_card.html` (`scripts/render_og.py`). Checks: pytest (new tag test), ruff, built pages inspected; the live card verified after deploy. Limit: the card is static; it can't show the day's puzzle.

## 2026-10-21 — Colored guess arrows

Up arrows are blue (#2563eb, 4.8:1 on the board) and down arrows a deeper orange (#d9480f, 4.0:1), matching the share text's 🟦/🟧; the `=` block stays ink, and the glyphs still carry the meaning. Tokens `--arrow-up` / `--arrow-down`; DESIGN.md updated (exempt from the One Marker rule). Checks: contrast computed, fixture board rendered at 390, pytest and ruff pass.

## 2026-10-21 — Guess list reopens on click

After a guess the input keeps focus, so clicking it fired no `focus` event and the player list stayed closed. `game.js` now also opens the list on `click`. Checks: headless Chrome at 390 (tap) and 1280 (click): after a guess, a tap/click shows all 20 remaining names; typing still filters; clearing restores the full list. pytest and ruff pass.

## 2026-10-21 — Advanced page trimmed to MA

Removed the "What wins games" section (blocks-and-turnovers model) and the held-out-fit sentence from `advanced.html`; dropped the second model from `advanced.py`. Model details keep MA's intercept, R² and CV R². Checks: pytest, ruff, build, page rendered on localhost.

## 2026-10-21 — Drop box plus/minus

+/- dropped: without point-by-point lines it is only a box-score count; MA kept. Removed the derived count, columns, copy, and tests; MA and per-10 views remain. Checks: `uv run --no-sync ruff format`, `ruff check`, `pytest -q` (30 passed), real-data site build (51 players, 17 tournaments, 12 warnings), and source grep (no matches).

Newest first. One entry per substantive change: what changed, checks actually run, remaining limits. At most 150 words each.

## 2026-10-21 — Advanced stats (local)

Added box +/-, per-10 rates, regression-weighted margin added, shared Box/Advanced column switches, player advanced totals, and the Advanced model/performance page. Summary totals remain authoritative. On 92 real games, M1 intercept −11.9013, S/B/T coefficients 1.3265/0.3516/−0.1685, CV R² 0.8402; M2 intercept 0.1674, B/T 1.1515/−0.5762, CV R² 0.6083. Both use 2,000 bootstrap resamples and shuffled 10-fold predictions. Checks: `uv run --no-sync ruff format`, `ruff check`, `pytest -q` (30 passed), real-data build (51 players, 17 tournaments), and design detector (advisories only). Plain `uv run` crashes in macOS system configuration; desktop/phone browser verification unavailable because headless Chrome aborts. Local only; no commit or deployment.

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
