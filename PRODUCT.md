# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Current Ooze players and alumni (Ooze is a college ultimate frisbee team). They open the site on their phones, usually from a link in the team group chat, play the daily puzzle, paste their result back into the chat, then look up their own and their teammates' stats. They know every name on the roster and every tournament; nothing needs explaining to an outsider.

## Product Purpose

Oozedle is a daily game first. Each day it hides one player's stat line from one tournament (points played, assists, goals, blocks, turnovers); you have six guesses to name the player, and each guess shows whether the hidden line is higher, lower or equal in every stat. The share text is the point of the ritual. Success: the team plays it daily and argues about it in the chat.

After the game, the site is the team's record book: all-time player stats accumulated across every tournament the team has kept stats for, a page per player with their full history, and a page per tournament.

## Positioning

It is built from the team's own stat-keeping spreadsheets, so every number is a real line someone on the team recorded. No other product has this data.

## Operating Context

- Source of truth: one Google Sheets workbook per tournament ("<Tournament> Stats"), in one Drive folder per season (2024, 2025 and 2026 so far). The build syncs them with gdown and rebuilds the site automatically when a sheet is added or edited.
- Seasons follow the college spring season; a season's tournaments are ordered by when their sheet was created.
- Shared via the group chat; most visits are on phones, often one-handed.
- Fully static site (Python + Jinja2 build, vanilla JS, no framework), hosted at oozedle.thaiv.dev.

## Capabilities and Constraints

- Stats per player per game: points played, assists, goals, blocks (called "D's" in 2024–2025 sheets), turnovers. Per game: score, team blocks and turnovers, clean holds (some 2026 games only).
- No line data: the sheets don't record who was on the field each point, so there is no true on-field +/-.
- Names are first names or nicknames as written in the sheets; one person can appear under two names (merged with an alias map).
- The daily puzzle changes at midnight Pacific and is the same for everyone.
- Future work: basic advanced stats (box +/-, per-point rates, what team stats predict wins, best performances by tournament and year).

## Brand Commitments

None. No team colors, logo or required tone carry over from the old site.

## Evidence on Hand

The stat workbooks (17 tournaments across 2024–2026). No photos, logos, or player bios exist; don't fabricate them.

## Product Principles

1. The daily game is the front door; everything else is one tap away from a finished game.
2. Every number traces back to a sheet the team kept; never invent or round away what the sheet says.
3. Built for a teammate on a phone in a group chat: fast, legible, shareable.
4. Celebrate performances; don't shame anyone. No "worst" lists or bottom-of-leaderboard callouts.

## Accessibility & Inclusion

Guess feedback must never rely on color alone (arrows and numbers carry it too). The game must be fully playable by keyboard.
