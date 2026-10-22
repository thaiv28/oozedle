# Current state

## Shipped

- Drive sync for the 2024, 2025 and 2026 season folders (17 workbooks), with change detection from Drive modified times.
- Parser for both workbook layouts and the Alumni Game special case; tidy tables with validation warnings.
- The daily game ("Field Board" design): one puzzle a day from any season, a season switch, arrow-only feedback, saved progress, share text, yesterday's answer, a personal record.
- Published at oozedle.thaiv.dev by `publish.yml` (first deploy 2026-10-21); the old GitHub Pages URL redirects there.
- Players leaderboard with season/search/sort controls, player career/season/tournament pages, tournaments list and box scores, and 404.

- +/- and margin added (MA) on the leaderboard, player and tournament pages, and an Advanced page (branch `advanced-stats`, local only).

## Known limits

- No line data: the sheets don't record who was on the field each point, so there is no on-field +/-.
- New season folders must be added to `SEASON_FOLDERS` by hand until the parent Drive folder is wired in.
- Some source sheets have data-entry noise (see the known warnings in `tech.md`); values are shown as written.
- Player identity is by first name or nickname; merges need `players.yml`.

## Future work

- Wire the parent Drive folder so new seasons are discovered automatically.
- Advanced stats: usage and best single-game performances.
- A simple opponent-strength Elo from game scores.
