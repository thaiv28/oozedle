# Tech

## Stack

Python ≥ 3.12 with uv; pandas, openpyxl, gdown (plus requests and BeautifulSoup for the folder listing), Jinja2. Frontend: hand-written CSS, vanilla JS, self-hosted fonts, no build step. Tests: pytest; lint: ruff.

## Data source

One Drive folder per season (`SEASON_FOLDERS` in `oozedle/config.py`), each holding Google Sheets files named "<Tournament> Stats". The tournament name is the file name minus " Stats". Seasons are the spring college season (2024, 2025, 2026 so far). A parent folder that would let new seasons appear on their own is not wired up yet: add a season by adding its folder ID.

## Sync (`oozedle/drive.py`, `scripts/sync_data.py`)

- `list_folder` fetches the folder page (`?hl=en`) and parses the `_DRIVE_ivd` script the way gdown does. Each entry gives id, name, MIME type, and created/modified times (entry indexes 9 and 10, epoch ms).
- Sheets are exported as `.xlsx` through `gdown.download` on the `/export?format=xlsx` URL; uploaded `.xlsx` files download by ID. Each download goes to a temp file, must open in openpyxl, then replaces `data/raw/<season>/<name>.xlsx`. Three attempts, 10 s apart.
- A file is re-downloaded only when its Drive modified time differs from `data/raw/manifest.json` (or `--force`). Files no longer listed are deleted. A failed download keeps the old copy; a failed listing leaves that season untouched.
- `--fingerprint` prints a hash of the listing (season, id, modified) without downloading; CI uses it to skip unchanged builds.

## Workbook layouts (`oozedle/parse.py`)

Every workbook's first sheet is **Summary**:

- **Player block:** the header row is the first row containing "Points Played". Stat columns are found by label ("Blocks" or "D's"; "Turnovers" or "Turns"). Names are in column 0 until the first empty one. A row with no stats means the player didn't play. A row with text in a stat cell (joke rows, e.g. "Pants: on") is skipped with a warning.
- **Game block:** found by the "Goals Scored" cell (column 11 or 12). Opponent labels are in the row above it, until the first blank; rows below give goals given, total points, team blocks, turnovers and, in some 2026 sheets, clean holds. Goals can be fractional (one 15.5). If there are no labels but one value column, it is a single game against "Alumni" (the 2026 Alumni Game).

Per-game player lines:

- **Layout A (2024–2025):** one sheet per player; row 0 holds opponents in Summary order, then "Total".
- **Layout B (2026):** one sheet per game with A1 = "Name", in Summary order. Its per-player sheets are ignored.

Games are matched **by position**, never by name (opponents repeat: "Chico" twice, "SJSU1"/"SJSU2"). `opponent` drops a trailing game-number suffix. If the per-game sheet/column count differs from the game count (the Alumni Game's sheets are stale copies of SVR), per-game data is dropped; a single-game workbook then gets its lines from the Summary.

## Tables (`oozedle/dataset.py`)

`build_dataset()` returns pandas tables plus `warnings`:

- `tournaments`: `tournament_id` (`<season>-<slug>`), season, name, `order` (by Drive created time within the season), games, W-L, goals for/against.
- `games`: `game_id` (`<tournament_id>-g<n>`), opponent, score, result, team blocks/turnovers, clean holds.
- `player_games`: one row per player per game played.
- `player_tournaments`: Summary totals (authoritative), games played, W-L in games played.
- `players`: `player_id` (slug of the canonical name), seasons, tournament count.

Names map through `players.yml` aliases. Validation warns when per-game sums differ from Summary totals, when player goals in a game exceed the team's, and on empty workbooks. Known warnings: the 2025 Stanford Open's player sheets carry PDQ's opponent headers (values are right) and two games' goal sums exceed the score; the Spartan Showdown joke rows; the Alumni Game's stale sheets.

## Site (`oozedle/site.py`, `scripts/build_site.py`)

- `build()` wipes `output/`, copies `static/`, and renders templates. `asset()` appends a content hash to static URLs. Pages at depth use the `root` prefix for links.
- **Game:** `game_data()` inlines tournaments, players and every stat line with points played > 0 as `#game-data` JSON. `game.js` picks the day's answer in the browser: the Pacific date and season filter (`all` or a year) are hashed (FNV-1a) into the pool of lines with at least `MIN_POINTS` (5) points played. Puzzle #1 is `EPOCH` (2026-10-21). Guesses are limited to that tournament's roster; feedback is up/down/same per stat. Progress and the win record live in `localStorage` (the game works without it).
- **Stats:** `players.html`, `players/<player_id>.html`, `tournaments.html`, `tournaments/<tournament_id>.html`, and `404.html` use the shared base. Page context (totals, joins, ordering) is precomputed in `site.py`. `tables.js` sorts ledger tables and filters/reaggregates the players leaderboard by season and search; server-rendered totals work without JavaScript. The 404 uses root-relative links.
- **Hero fixture:** `build_site.py --hero DIR` renders the game on synthetic data reproducing the approved design comp (#214, PDQ 2026, Rowan/Farmer/Colin). Used only for impeccable's comp diff.

## Advanced stats

`oozedle/advanced.py` fits once per build; stats contexts keep full precision until display. Box +/- = assists + goals + blocks − turnovers (integer). Margin added (MA) = wA·A + wG·G + wB·B + wT·T, displayed to one decimal. Totals use authoritative Summary totals, including the Alumni Game.

Training uses one row per game with `player_games`: sum player A, G, B, T; target is float goals_for − goals_against. M1 fits margin = c0 + c1·S + c2·B + c3·T, S=(A+G)/2, with numpy ordinary least squares and an intercept. MA weights are wA=wG=c1/2, wB=c2, wT=c3; the intercept is excluded. M2 fits margin = d0 + d1·B + d2·T on the same games.

Both report coefficients, in-sample R², n, pooled out-of-fold R² from 10 shuffled folds (`default_rng(0)`), and 95% coefficient intervals from 2,000 game resamples (a separate `default_rng(0)`, 2.5/97.5 percentiles). Tiny test datasets use at most n folds. Per 10 = 10 × stat / points played; display one decimal, or “—” below 20 points played and sort missing values last.

The leaderboard and tournament box score share Box/Advanced switches, persisted as `?view=advanced` alongside `?season=`. Leaderboard JSON contains weights and season totals; filtering recomputes advanced values. Player pages show career/season advanced ledgers. `advanced.html` explains both models and lists best tournament performances and the best line per tournament name across seasons.

## Testing

`tests/conftest.py` writes synthetic workbooks in both layouts (plus the Alumni case) with openpyxl; no test touches the network. `test_real_data.py` runs only when `data/raw/manifest.json` exists. `test_steering.py` guards the docs.
