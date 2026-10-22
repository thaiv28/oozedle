---
name: Oozedle
description: A daily player-guessing game and stat record book, laid out like the laminated schedule sheet zip-tied to the fence at an ultimate tournament.
colors:
  board: "#f7f6ee"
  board-raised: "#fbfaf7"
  ink: "#0a0a0a"
  ink-soft: "#55534d"
  marker-orange: "#ff5a1f"
  marker-orange-pressed: "#e84c13"
  orange-ink: "#c2410c"
  arrow-up: "#2563eb"
  arrow-down: "#d9480f"
  rule: "#cecdc6"
  rule-strong: "#b9b7af"
typography:
  display:
    fontFamily: "Cossette Titre, Sofia Sans Condensed, sans-serif"
    fontSize: "156px"
    fontWeight: 700
    lineHeight: 0.86
    letterSpacing: "-0.03em"
  page-head:
    fontFamily: "Cossette Titre, Sofia Sans Condensed, sans-serif"
    fontSize: "clamp(56px, 14vw, 104px)"
    fontWeight: 700
    lineHeight: 0.86
  headline:
    fontFamily: "Cossette Titre, Sofia Sans Condensed, sans-serif"
    fontSize: "38px"
    fontWeight: 700
    lineHeight: 1
  title:
    fontFamily: "Cossette Titre, Sofia Sans Condensed, sans-serif"
    fontSize: "22px"
    fontWeight: 700
    lineHeight: 1.1
  body:
    fontFamily: "Sofia Sans Condensed, Arial Narrow, sans-serif"
    fontSize: "16px"
    fontWeight: 600
    lineHeight: 1.35
    fontFeature: "tnum"
  player-name:
    fontFamily: "Sofia Sans Condensed, Arial Narrow, sans-serif"
    fontSize: "22px"
    fontWeight: 800
    lineHeight: 1.35
  label:
    fontFamily: "Sofia Sans Condensed, Arial Narrow, sans-serif"
    fontSize: "14px"
    fontWeight: 700
    lineHeight: 1.35
rounded:
  none: "0"
  sm: "3px"
spacing:
  gutter: "12px"
  gap: "8px"
  row-h: "42px"
  control-h: "44px"
  stat-w: "46px"
  col-max: "640px"
  col-wide: "960px"
components:
  button-guess:
    backgroundColor: "{colors.marker-orange}"
    textColor: "#ffffff"
    typography: "{typography.title}"
    rounded: "{rounded.sm}"
    height: "44px"
    padding: "0 16px"
  button-guess-hover:
    backgroundColor: "{colors.marker-orange-pressed}"
  button-guess-disabled:
    backgroundColor: "{colors.rule-strong}"
  input-guess:
    backgroundColor: "{colors.board-raised}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    height: "44px"
    padding: "0 12px"
  chip-season:
    backgroundColor: "{colors.board}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "6px 10px"
  chip-season-selected:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.board}"
  mark-same:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.board}"
    width: "31px"
    height: "30px"
  result-panel:
    backgroundColor: "{colors.board-raised}"
    textColor: "{colors.ink}"
    padding: "14px 14px 16px"
---

# Design System: Oozedle

## Overview

**Creative North Star: "The Field Board"**

Oozedle looks like the laminated schedule and bracket sheet zip-tied to the fence at a college ultimate tournament: white board stock, black marker type, ruled boxes, and one orange marker used to circle the thing that is happening now. Every page is a sheet someone posted for teammates who already know the names. Nothing is decorated; information is the decoration.

The first screen is a posting, not an app. A huge field number ("#214") sits left of a vertical rule, with the date, the pool label (tournament and year) and the instruction at its right; a six-row ruled table fills the middle; the guess control sits directly under it. Stats pages are the same sheet at a wider measure: big title, ruled ledgers, a row of season chips. The system explicitly refuses the Wordle tile grid and the stats-dashboard card stack.

Dense, flat, legible one-handed on a phone. Copy is minimal and never shames a player: no worst lists, no bottom-of-leaderboard callouts.

**Key Characteristics:**
- One heavy display face for every number and head, one condensed text face for everything else.
- Hairline rules do the work of boxes, cards, and shadows.
- A single orange marker, once per view.
- Feedback is carried by shape (arrows, solid blocks, strike-through), never by color.
- Mobile-first, one narrow column, scaling up in steps.

## Colors

Warm white board stock, near-black marker ink, grey-green hairlines, and one saturated orange. The only other hues are the two guess-arrow colors.

### Primary
- **Marker Orange** (#ff5a1f): the single "this is current/active" signal. Used for the Guess button fill, the current row's number, the active sort triangle in ledger headers, the focus ring (3px outline), and the input caret. Hover deepens to #e84c13.
- **Arrow Up** (#2563eb) and **Arrow Down** (#d9480f): guess-board arrows only, matching the share text's 🟦 and 🟧. Both clear 3:1 on the board (4.8 and 4.0). The `=` block stays ink.
- **Orange Ink** (#c2410c): the darker orange used only for text on the board (the form note under the guess control), where plain marker orange would be too light to read.

### Neutral
- **Board Stock** (#f7f6ee): page background; also the fill of sticky first columns, season chips, and the player search field.
- **Raised Board** (#fbfaf7): the one step lighter surface, for the guess input, the combobox list, and the result panel.
- **Marker Ink** (#0a0a0a): all text, heavy rules (2px result panel border, 1.5px chip borders), selected chips and the selected combobox option (inverted to Board Stock text), and the equals block.
- **Soft Ink** (#55534d): secondary text only: record labels, "next puzzle" note, footer, small tournament subtext.
- **Hairline Rule** (#cecdc6): 1px table grids, section rules, topbar and footer borders.
- **Strong Rule** (#b9b7af): input borders, link underlines at rest, disabled button fill.

### Named Rules
**The One Marker Rule.** Orange marks exactly one current or active thing per view: the Guess button, the current row number, or the active sort triangle. If a second thing wants orange, it is wrong; make it ink. The deeper Arrow Down orange on guess arrows is a feedback color, not a marker, and is exempt.

**The Never-Color-Alone Rule.** No state is communicated by color. Higher/lower is an arrow, equal is a solid block, wrong is struck through, selected is inverted ink. Color may reinforce, never carry.

## Typography

**Display Font:** Cossette Titre 700 (fallback Sofia Sans Condensed, sans-serif), self-hosted woff2.
**Body Font:** Sofia Sans Condensed 600/700/800 (fallback Arial Narrow, sans-serif), self-hosted woff2.

**Character:** A chunky, slightly quirky display face against a tall, tight grotesk: signage over spreadsheet. The display face owns numerals and heads; the condensed face owns names and reading text. Tabular figures are on globally (`font-variant-numeric: tabular-nums`).

### Hierarchy
- **Field Number** (Cossette 700, 88px phone / 132px at 720 / 156px at 1100, line-height 0.86, letter-spacing -0.03em): the "#214" puzzle number only.
- **Page Head** (Cossette 700, clamp(56px, 14vw, 104px), 0.86): player and tournament page titles.
- **Pool Label** (Cossette 700, 38px / 54px / 64px, 1): tournament and year on the game header.
- **Ledger Title** (Cossette 700, 32px, 1): section heads on stats pages. Career-totals cells use the same face at clamp(20px, 5.8vw, 32px).
- **Title** (Cossette 700, 22px, 1.1): section heads ("Yesterday"), result verdict at 26px, the Guess button at 23px, season chips at 18px.
- **Player Name** (Sofia 800, 22px phone / 25px / 28px, one line, ellipsis): guessed names in the board.
- **Body** (Sofia 600, 16px, 1.35): default text; 18px at weight 800 for fact lines and ledger row heads.
- **Label** (Sofia 700/800, 14-18px): column headers (800, 18px), nav (700, 14px), footnotes (14px).

### Named Rules
**The Two-Voice Rule.** Display face for numbers and heads, condensed face for words. Never set a sentence in the display face, never a headline number in the condensed one.

## Layout

Mobile-first and column-based. The game board lives in a centered column capped at 640px with a 12px gutter; at 1100px the cap becomes 760px. Stats pages use `main.wide`, a 960px column; the topbar and footer widen to match.

The board's metrics are tokens that step up together: row height 42px / 52px (720px) / 58px (1100px); stat column 46px / 64px / 80px; number column 25px / 34px / 40px; input and button height 44px / 52px. The guess form is a two-column grid (input, then a 113px / 150px button) with a 12px top margin and 8px gap. Sections below the board are separated by a full-viewport-width 1px rule with 13px top margin and 10px padding.

Breakpoints actually used: 519px (tournament rows narrow their five stat columns from 48px to 32px), 520px (tables trim columns), 720px (board scales up), 1100px (board scales up again).

Tables: ruled 1px in Hairline Rule on every cell. Text columns are left-aligned, numeric columns centered, with tabular figures. Ledger first columns are sticky on horizontal scroll. Below 520px, tables drop their lowest-value columns (the rank column of numbered ledgers, the second and third columns of trimmed ledgers) instead of scrolling the page; ledgers keep an overflow wrapper only as a backstop.

Spacing rhythm is tight and board-like: 4/6/8/12/14/16px steps, 24-28px between major blocks.

## Elevation & Depth

Flat. No gradients, textures, or card stacks; surfaces differ by at most one tint step (Board Stock to Raised Board) and are separated by rules. Depth is expressed by line weight: 1px hairline for structure, 1.5px for controls, 2px for the result panel, heavy ink for the inverted selected state.

### Shadow Vocabulary
- **Combobox list** (`box-shadow: 0 6px 18px rgb(20 20 20 / 0.14)`): the only shadow in the system. It lifts the player suggestion list, which opens upward over the table.
- **Input focus ring** (`box-shadow: 0 0 0 2px var(--ink)` plus ink border): not depth, a hard focus doubling of the input border.

### Named Rules
**The Flat Sheet Rule.** Nothing floats except the open combobox list. A new surface gets a rule, not a shadow.

## Shapes

Square and ruled. Controls (inputs, button, season chips, rail chips) take a 3px corner; the stats-page search field, the stats season buttons, tables, and the result panel are fully square (0). No pills, no circles. Silhouettes are rectangles on a grid; the only non-rectangular forms are the guess arrows, the disclosure triangle (7x8px, clip-path) and the sort triangle (8x7px).

**Guess marks** are inline SVG built in game.js. Up and down are stroked line arrows (3px stroke, square caps; viewBox 18x24, drawn 18x24px on phone, 22x28 at 720). Equal is a filled block: a 31x30px ink rectangle (38x36 at 720) holding a white double bar (viewBox 14x10, drawn 14x10, 17x12 at 720). Each mark is a `role="img"` with a label such as "More goals" or "Same blocks".

## Components

### Buttons
- **Shape:** 3px corners, 44px tall (52px at 720).
- **Primary (Guess):** Marker Orange fill, white Cossette 700 text at 23px, 0 16px padding. The only orange-filled control. Hover #e84c13 over 120ms. Disabled: Strong Rule grey fill, not-allowed cursor.
- **Ink variant:** Marker Ink fill, hover #2c2c2c, used by Share in the result panel.
- **Focus:** the global 3px orange outline with 2px offset.

### Chips (season switch and rail)
- **Style:** Board Stock fill, 1.5px ink border (1px on stats-page buttons), 3px corners on links, display face 18px, min-width 52px.
- **State:** the selected season is inverted (ink fill, board text; `aria-current` or `aria-pressed`). The rail on the tournaments page sizes each chip by its share of the season's tournaments; hover inverts.

The Box/Advanced view switch reuses the season chip style: ink borders, inverted selected state via `aria-pressed`, and the same display face. A shared button group changes ledger columns and preserves its choice in the URL; switching to Advanced sorts by Adj. MA. One tournament switch drives both ledgers.

### Inputs / Fields
- **Guess input:** Raised Board fill, 1.5px Strong Rule border, 3px corners, 18px Sofia 600, orange caret. Focus swaps the border to ink and doubles it with a 2px ink box-shadow ring (no browser outline).
- **Combobox list:** opens above the input, Raised Board, 1.5px ink border, max 220px tall, scrolling. Options are 18px/700; the highlighted option inverts to ink.
- **Form note:** 15px Orange-Ink text under the control for brief, non-shaming messages.
- **Player search (stats):** square, 1px Strong Rule border, 200px wide, 40px tall.

### Guess board (signature)
A fixed-layout, six-row, ruled table: number column, player column, and five stat columns (PP, A, G, B, T). The current row's number is Marker Orange; empty rows keep their rule lines. A submitted guess shows the name in 800 weight and one mark per stat; a wrong guess stays on the board with its name struck through (2.5px line), never removed. A new row "posts" by a 260ms clip-path wipe, staggered 40ms per stat cell, only under `prefers-reduced-motion: no-preference`.

### Result panel
Replaces the guess control when the game ends: 2px ink border, Raised Board fill, 14px padding. Verdict in display face at 26px, the answer at 18px/800, the stat line at 16px/700, then actions (Share, an ink button) and a Soft Ink "next puzzle" note. Tone is plain; losing reveals the answer without comment.

### Ledgers (stats tables)
Collapsed borders on a 1px Hairline grid, 40px rows, 6px 10px padding, nowrap. Headers 17px/800; row heads 18px/800, left-aligned; numbers centered. Sortable headers are buttons with an 8x7px Marker Orange triangle on the active sort only. Links inside tables are underlined 1px in Strong Rule, darkening on hover. Career totals row uses display-face numerals.

### Charts
Roles uses a single-series SVG dot chart, with no legend or border box. Dots are ink at 0.55 opacity with a 2px board ring; sqrt(PP) sets radii from 5–13px. Hairline rule grids and 13px soft-ink ticks match the ledgers. Search highlights matching dots and their season-order paths in orange while fading others to 0.2; focus has a visible ring. Linked dots have ≥12px hit radii, HTML tooltips, and a disclosed data ledger. A responsive viewBox keeps the chart at 0.75× width on desktop and square below 520px.

### Tournament rows
A grid of one flexible name column and five stat columns (48px, 32px under 519px), 48px minimum height, ruled underneath. Rows are `details` disclosures with a 7x8px ink triangle that rotates 90deg when open.

### Navigation
Slim 40px topbar with a 1px rule beneath: OOZEDLE wordmark (display face, 30px) left; Players and Tournaments right (14px/700, 22px gap). Links are plain text; hover and the current page are underlined. No hamburger, no drawer. Prev/next tournament links sit between two 1px rules.

## Do's and Don'ts

### Do:
- **Do** separate content with 1px rules in #cecdc6 and give it hierarchy with type size and weight.
- **Do** use Marker Orange (#ff5a1f) for one current/active thing per view.
- **Do** encode every state in shape or text as well as color: arrows, solid equals block, strikethrough, inversion, a labeled `role="img"` on each mark.
- **Do** center numbers and left-align text, with tabular figures, in every table.
- **Do** drop low-value columns under 520px rather than scroll a table sideways.
- **Do** build new game surfaces mobile-first inside the 640px column and scale at 720px and 1100px; stats surfaces use the 960px column.
- **Do** keep copy short and neutral, and celebrate performances.
- **Do** keep every control keyboard reachable with the visible orange focus outline.

### Don't:
- **Don't** add shadows (except the combobox list), gradients, textures, or cards.
- **Don't** return to a Wordle-style tile grid or a dashboard card stack.
- **Don't** use color alone for any state, and don't add green/red correctness colors.
- **Don't** use orange for decoration, links, or a second item in the same view.
- **Don't** shame players: no "worst" lists, no bottom-of-table callouts, no mocking loss copy.
- **Don't** set sentences in the display face or numbers in the condensed face.
- **Don't** use pills, circles, or radii above 3px.
- **Don't** invent photos, logos, or bios; none exist.

## Not canonized

Defects the build carries, recorded so future surfaces do not inherit them: the Guess button sets white text on #ff5a1f (about 3:1), acceptable only because the label is large bold display type, so do not reuse that pairing for small text; the 519px and 520px breakpoints are close together and unreconciled; the 3px corner is applied inconsistently (stats search and season buttons are square).
