# Work log

## 2026-10-22 — Share link with https://

The share text now ends with `https://oozedle.thaiv.dev` so every chat app (Discord included) makes it a link and can show the preview card. Checks: share text captured in headless Chrome, pytest, ruff.

## 2026-10-22 — Share opens the phone share sheet

On touch devices with the Web Share API (iOS Safari, Android Chrome), Share calls `navigator.share({text})`, opening the system sheet (Messages, Copy, ...); closing the sheet does nothing; other failures fall back to copying. Desktops still copy. Checks: headless Chrome with a stubbed `navigator.share` on a touch profile (sheet called with the share text; cancel leaves the button alone) and a desktop profile (copies), pytest, ruff.

## 2026-10-22 — AMA/10 on player tournament rows

Each tournament row on a player page shows that tournament's (shrunk) Adj. MA per 10, labelled "ADV" beside the number, after T; hover, tap or focus shows "Adjusted MA / 10 points" (CSS tooltip, `.tip`; `tips.js` keeps a tap on it from opening the row). The Advanced page's one-line description now says "Elo" instead of "USAU rating". Checks: pytest, ruff, localhost at 1280 and 390.

## 2026-10-22 — Win% on the Players table

Box score view adds Win% (wins ÷ decided games played, ties excluded; "—" with none) after W–L, rendered server-side and recomputed by `tables.js` after season filtering; sortable. Checks: pytest, ruff, localhost at 1280 and 390 (no overflow), season filter and sort.

## 2026-10-22 — Advanced page method folded

One line under the heading says how MA and Adj. MA are computed; the Margin added and Opponent adjustment tables (and the ratings source) sit in a closed "How MA is calculated" disclosure. "Advanced" joins the header nav (current on the Advanced and ranking pages); the Players page link to it is gone. Removed the site footer ("Stats from Ooze's tournament stat sheets.") and the game's "Name the player. 6 guesses." line. Checks: pytest, ruff, build, localhost at 390 and 1280 (closed and opened).

## 2026-10-22 — Rankings per 10

Best tournament performances (now with a per-10 column) and best seasons (Advanced top 10 and full pages) now rank by shrunk Adj. MA per 10 instead of total Adj. MA: 2026 had 44 games and 824 team points against 25/412 (2024) and 23/397 (2025), so totals favoured it (8 of the top 10). Greatest careers (renamed) and best-at-each-tournament still rank by total; the latter links to `advanced/tournaments.html` (all 17 tournaments, most recent first, each with its top line). New `tournaments.yml` overrides a season's order where Drive creation times are wrong (2026: the Alumni Game sheet predates Regionals'); it applies site-wide. Checks: pytest, ruff, build, localhost.

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
