# Work log

## 2026-10-22 — Rankings per 10

Best tournament performances (now with a per-10 column) and best seasons (Advanced top 10 and full pages) now rank by shrunk Adj. MA per 10 instead of total Adj. MA: 2026 had 44 games and 824 team points against 25/412 (2024) and 23/397 (2025), so totals favoured it (8 of the top 10). Greatest careers (renamed) and best-at-each-tournament still rank by total. Checks: pytest, ruff, build, localhost.

## 2026-10-22 — Advanced pages trimmed

Removed explanatory copy at the user's request: the MA and opponent-adjustment sentences, the fit and shrinkage lines, Model details, and the ranking pages' count line. Tables, "All …" links, hidden captions and the ratings source credit stay. The Players link now reads "Advanced"; player pages no longer link there. Checks: pytest, ruff, build.

## 2026-10-22 — Adj. MA rankings

The Advanced page shows the ten best tournament performances, seasons and careers by Adj. MA, each linking to a full sortable page (`advanced/performances.html`, `seasons.html`, `careers.html`; one `ranking.html.j2`, rows in `ranking_rows.html.j2`). `tables.js` takes a per-table default sort (`data-sort`) and now sorts "−" values as negatives (they previously sank as non-numbers). Checks: pytest (link check caught a missing `with context` on the macro import), ruff, localhost at 390 and 1280.

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
