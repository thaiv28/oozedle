# AGENTS.md

Guidance for AI coding agents (and humans) working in this repo.

## Read before work

Read only what your change touches. If your task came with a spec naming files and docs, read those and skip this list.

- **Always:** the newest work-log entries, `python3 scripts/work_log.py recent 5` (not the whole file). Search [the archive](docs/steering/work_log_archive.md) with `grep` when a topic may have been tried before.
- **Data sync, workbook parsing, tables, site build, file layout, tests:** [Tech](docs/steering/tech.md).
- **Feature status, known limits, future work:** [Current state](docs/steering/current_state.md).
- **CI, publishing, hosting, secrets:** [Deployment](docs/steering/deployment.md).
- **Templates, CSS, JS:** `PRODUCT.md`, `DESIGN.md` and the surface briefs in `.impeccable/surfaces/`. Use the impeccable skill.

Read large docs by section (`grep -n '^## '`, then the lines you need), not whole.

Code and the synced workbooks are the source of truth. If a document disagrees with them, verify the behavior and correct the document in the same change. The user's latest instructions override these docs.

## Required document updates

- **Every substantive code or behavior change:** add a dated entry at the top of `docs/steering/work_log.md` with what changed, the checks actually run, and any remaining limit.
- **Feature status, known limit, or future work changes:** update `docs/steering/current_state.md` in the same change. Future-work ideas go in its **Future work** section, not only in chat. Remove items once they ship.
- **Sync, parser, tables, site build, file or test layout change:** update `docs/steering/tech.md`.
- **CI, publishing, schedules, secrets, or AWS resources change:** update `docs/steering/deployment.md`.
- **Visual design or UI components change:** update `DESIGN.md`.
- Documentation-only work still gets a short work-log entry. Don't claim a check you did not run.

`uv run pytest -q` includes `tests/test_steering.py`, which fails when code changed (uncommitted) without a `work_log.md` change, or when a changed doc passes its word budget.

### Work log

`work_log.md` keeps the newest entries. The pre-commit hook (`.githooks/pre-commit`) runs `scripts/work_log.py rotate` when a commit touches the log: past 15 entries, all but the newest 10 move to the top of `work_log_archive.md`. Entries are at most 150 words. Enable the hook once per clone (worktrees share it): `git config core.hooksPath .githooks`.

## What this is

Oozedle is a daily guessing game for Ooze, a college ultimate frisbee team, plus the team's all-time stat book. Stats come from one Google Sheets workbook per tournament ("<Tournament> Stats") in one Drive folder per season. `scripts/sync_data.py` mirrors them with gdown, `oozedle/` parses them into tidy tables, and `scripts/build_site.py` renders a static site into `output/`, published to https://oozedle.thaiv.dev (S3 + CloudFront) by `.github/workflows/publish.yml`.

## Quick commands

```bash
uv sync                                     # install (Python >= 3.12, managed by uv)
uv run python scripts/sync_data.py          # mirror Drive workbooks into data/raw (skips unchanged)
uv run python scripts/check_data.py         # tournaments, W-L, and every data warning
uv run python scripts/build_site.py         # render output/
python3 -m http.server -d output 8000       # preview
uv run pytest -q                            # tests (offline; synthetic workbooks)
uv run ruff format && uv run ruff check     # format and lint (CI checks both)
```

`data/` and `output/` are gitignored build artifacts. Never commit them.

### Worktrees

Agents work in a separate worktree (see the global `AGENTS.md`). A new one has no `data/`. Either sync (about 30 s, network) or copy the main checkout's (`MAIN`):

```bash
git worktree add ../oozedle-<branch> -b <branch> <base> && cd ../oozedle-<branch>
uv sync && git config core.hooksPath .githooks
cp -R "$MAIN/data" .        # or: uv run python scripts/sync_data.py
```

Copy `data/`, don't symlink it: sync rewrites and deletes files there.

## Layout

| Path | Purpose |
|---|---|
| `oozedle/config.py` | Paths and the season → Drive folder map (`SEASON_FOLDERS`) |
| `oozedle/drive.py` | Drive folder listing (with created/modified times) and gdown downloads |
| `oozedle/parse.py` | One workbook → Summary totals, games, per-game player lines |
| `oozedle/dataset.py` | All workbooks → `players`, `tournaments`, `games`, `player_games`, `player_tournaments`, plus warnings |
| `oozedle/site.py` | Jinja2 rendering, game JSON, the design-comp hero fixture |
| `players.yml` | Alias map: raw sheet name → canonical player name |
| `templates/`, `static/` | Jinja2 templates; hand-written CSS, vanilla JS, self-hosted fonts |
| `.impeccable/` | Design comps, surface briefs, design system sidecar |

## Conventions

- **Workbooks are read by label, games by position.** Stat columns are found by their header text; per-game sheets/columns map to the Summary's game list by order, because opponent names repeat. See `tech.md` before touching the parser.
- **Summary totals are authoritative.** Per-game rows are validated against them; disagreements are warnings, never silent fixes.
- **Never invent or round away data.** A suspicious value stays as written and gets a warning in `check_data.py`.
- **Frontend: no build step and no framework.** Tokens live at the top of `static/css/site.css`. Icons are inline SVG. JS that writes HTML builds DOM nodes (`el()` in `game.js`), never `innerHTML` with data.
- **Feedback never relies on color alone** (arrows, struck names, filled blocks carry it).
- **Site copy is minimal.** Every word must be necessary; no "worst" lists or callouts that shame a player.
- **Static asset URLs** go through `asset()` in templates, which appends a content hash.

## Gotchas

- Google Drive throttles anonymous downloads. `sync_data.py` retries each file on its own and keeps the old copy on failure; don't loop on it while developing.
- GitHub disables scheduled workflows after 60 days without repo activity; `publish.yml` re-enables itself each run (see `deployment.md`).
- The daily puzzle is picked in the browser from the Pacific date, so a data change mid-day can change that day's puzzle.

## Before you finish a change

1. `uv run pytest -q` passes (including the steering guard).
2. If you touched parsing or the dataset, run `scripts/check_data.py` on real data and compare the warnings.
3. For any UI change, build, preview at desktop and phone widths, and keep copy minimal.
4. Inspect the diff and make the document updates above match the code. State anything you did not verify.
