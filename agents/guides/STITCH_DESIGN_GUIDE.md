# Stitch Design Guide for Project Vantage
# Use this file as context whenever asking an LLM to design a screen using Stitch MCP.
# It tells Stitch what the app looks like, what tokens exist, and what data is real.

---

## WHAT THIS APP IS

Project Vantage is a **dark, professional cricket trading tool** for a solo operator.
It is used pre-match to analyse historical data (win probabilities, venue bias, player
matchups, form ratings) and to manage Betfair back/lay trades.

**This is a desktop web application.** It runs in a browser on a laptop or desktop
monitor. It is NOT a mobile app. Do NOT design for small screens, touch targets,
bottom navigation bars, or single-column stacked layouts. All designs MUST assume
a minimum viewport width of 1280px and a mouse/keyboard user.

Think Bloomberg terminal meets Linear.app -- tightly packed data, dark background,
electric-blue accents, monospace numbers, no decorative flourishes.

---

## VISUAL IDENTITY (non-negotiable)

| Attribute | Description |
|---|---|
| **Mood** | Dark fintech / command-line professional |
| **Background** | Near-black obsidian (#0D1117 base, #141920 cards) |
| **Primary accent** | Electric blue #6366F1 |
| **Data accent** | Amber #F59E0B |
| **Semantic tiers** | Green (elite), Teal (strong), Amber (caution), Red (danger) |
| **Typography** | Monospace for data/numbers; sans-serif (Inter) for UI labels |
| **Border radius** | Tight -- 2px to 8px maximum. Never pill-shaped cards. |
| **Density** | High. Pack content tightly. Minimal whitespace. |
| **Icons** | Lucide icons only (Zap, ChevronRight, Trophy, etc.) |
| **No decorations** | No gradients on card bodies, no illustrations, no drop shadows on text |

**Reference aesthetic:** Linear.app settings page + Bloomberg terminal + shadcn/ui dark mode.

---

## COLOR TOKENS (use these names in every design decision)

### Backgrounds (dark to slightly less dark)
| Token | Hex | Use |
|---|---|---|
| `--bg-base` | #0D1117 | Page background, input backgrounds |
| `--bg-surface` | #141920 | Cards, panels, sidebars |
| `--bg-elevated` | #1A2130 | Modals, dropdowns, elevated cards |
| `--bg-hover` | #212A3A | Hover state backgrounds |

### Accents
| Token | Hex | Use |
|---|---|---|
| `--accent-ui` | #6366F1 | Active states, buttons, focus borders, tab indicators |
| `--accent-ui-hover` | #7274F3 | Hover on blue elements |
| `--accent-data` | #F59E0B | Data highlights, amber badges, stat emphasis |

### Semantic tier colours (used for badges, labels, status indicators)
| Token | Hex | Meaning |
|---|---|---|
| `--tier-elite` | #22C55E | Top/positive/success |
| `--tier-strong` | #14B8A6 | Above average/good |
| `--tier-caution` | #F59E0B | Warning/below average |
| `--tier-danger` | #EF4444 | Critical/failure/error |

### Text
| Token | Use |
|---|---|
| `--text-primary` (#E2E8F0) | Main content text |
| `--text-secondary` (#64748B) | Supporting text, descriptions |
| `--text-muted` (#4B5563) | Labels, placeholders |
| `--text-disabled` (#2D3748) | Disabled elements |

### Borders
| Token | Use |
|---|---|
| `--border-subtle` | Dividers between sections (barely visible) |
| `--border-default` | Standard card and input borders |
| `--border-strong` | Prominent separators |
| `--border-accent` | Focused inputs, active card top border |

---

## TYPOGRAPHY RULES

**Two fonts only:**
- **UI labels, buttons, navigation:** Inter / system sans-serif
- **Numbers, data, stats, odds:** JetBrains Mono (monospace), tabular numbers

**Scale (from smallest to largest):**
- `text-2xs` (0.60rem) -- uppercase section labels ("VENUE", "BACK ODDS")
- `text-xs` (0.65rem) -- helper/hint text
- `text-sm` (0.72rem) -- form inputs, body text
- `text-base` (0.80rem) -- primary body / sub-headings
- `text-md` (0.875rem) -- card titles, stat values
- `text-lg` (1rem) -- section headings
- `text-xl` (1.25rem) -- page titles
- `text-2xl` (1.5rem) -- large cockpit headings

**Label convention:** All field labels are UPPERCASE, letter-spacing 0.1em, text-muted
color, font-size text-2xs. Example: "HOME TEAM", "BACK ODDS", "MATCH DATE".

---

## SPACING SYSTEM (4px base unit)

| Token | Size | Common use |
|---|---|---|
| `--space-1` | 4px | Tight internal gaps |
| `--space-2` | 8px | Gap between chips, inline items |
| `--space-3` | 12px | Form field internal padding |
| `--space-4` | 16px | Between form fields, card internal gap |
| `--space-5` | 20px | Card/panel padding |
| `--space-6` | 24px | Page-level section padding |
| `--space-8` | 32px | Between major blocks |

---

## NAMED COMPONENT CLASSES (always use these, never reinvent)

### Buttons
- `.btn-primary` -- Electric blue background, white text. The single primary CTA per form.
- `.btn-ghost` -- Transparent, border, muted text. Used for secondary/cancel actions.
- `.btn-danger` -- Red-tinted background, red text. Used only for destructive actions.

### Badges (tier system -- backend pre-computes the tier, frontend just maps it)
- `.badge-elite` -- Green-tinted background, green text. Top performer.
- `.badge-strong` -- Teal-tinted background, teal text. Above average.
- `.badge-caution` -- Amber-tinted background, amber text. Warning.
- `.badge-danger` -- Red-tinted background, red text. Critical / failed.
- `.badge-live` -- Green with a pulsing dot. LIVE status indicator.
- `.badge-format` -- Neutral, elevated background. Format labels (ODI, IPL).

### Cards
- `.card-base` -- Standard info card. Elevated bg, subtle border, shadow.
- `.card-active` -- Active/selected card. Adds accent-blue top border + inset glow.
- `.card-signal` -- Positive signal card. Left border green, elite-tinted background.
- `.card-module` -- Dashboard module card. Clickable, 160px min-height, hover reveals top border.

### Inputs
- `.context-input` -- Standard select or text input. 32px min-height, default border,
  base background. Focus: accent border + blue glow ring.

### Cockpit-specific
- `.cockpit-module` -- Outer wrapper for the trading cockpit (24px padding, flex column, gap 16px).
- `.cockpit-panel` -- Right-side detail panels. Surface bg, border, large shadow.
- `.cockpit-tabs` -- Tab switcher. Inline-flex, surface bg, 4px padding.
- `.cockpit-tab-active` -- Active tab: elevated bg, accent bottom border, semibold.
- `.cockpit-match-setup` -- Form container. Surface bg, default border, radius-md.

---

## LAYOUT PATTERNS (copy these grids exactly)

### Dashboard module grid
3 columns, 16px gap, clickable `.card-module` cards.

### Match setup form
3-column grid, 24px gap. Each cell: label (uppercase, muted) above an input.
Fields: Home Team | Away Team | Venue | Match Date | Season | Toss Selection.

### Odds selector (inline, 3 fields in one row)
Fixed-width controls in one row:
- Team select: 8ch wide
- Back odds input: 6ch wide, center-aligned text
- Lay odds input: 6ch wide, center-aligned text

### Stat summary block (3-up or 4-up grid)
Small chips in a grid. Each chip has:
- UPPERCASE label (text-2xs, muted, 0.1em tracking)
- Value below (monospace font, semibold, primary text)

### Trade list row
Flex row. Left: match info (teams, date, badge). Center: odds pair. Right: action button.

### Form footer
Flex row, border-top (subtle), 16px padding-top, 24px gap.
- Error/success message on the left (auto margin-right).
- Primary action button on the right (min 160px wide).

---

## DATA FIELDS THAT ACTUALLY EXIST

Only design screens using these real data fields. Do not invent fields.

### Match context
- `homeTeam` -- team name string (e.g., "India", "Mumbai Indians")
- `awayTeam` -- team name string
- `venue` -- stadium name (e.g., "Wankhede Stadium, Mumbai")
- `matchDate` -- ISO date string
- `season` -- year integer (e.g., 2025)
- `tossSelection` -- one of: HOME_FIELD | HOME_BAT | AWAY_FIELD | AWAY_BAT

### Trading inputs
- `bankroll` -- positive decimal, INR currency
- `homeGround` -- one of: FAV (favourite) | UG (underdog) | NEU (neutral)
- `oddsBeforeToss.selectedTeam` -- team name
- `oddsBeforeToss.backOdds` -- decimal number
- `oddsBeforeToss.layOdds` -- decimal number
- `oddsAfterToss.selectedTeam` -- same shape as before-toss odds
- `oddsAfterToss.backOdds` -- decimal number
- `oddsAfterToss.layOdds` -- decimal number

### Trade record (returned from backend)
- `id` -- trade ID integer
- `team_1`, `team_2` -- team name strings
- `favourite_team` -- team name string
- `home_ground` -- FAV | UG | NEU
- `stadium` -- venue ID string
- `match_date` -- ISO date string
- `season` -- year integer
- `toss_winner`, `toss_decision` -- string or null (available after toss)
- `bankroll` -- float
- `back_odds_before_toss`, `lay_odds_before_toss` -- floats
- `back_odds_after_toss`, `lay_odds_after_toss` -- floats
- `selected_team_before_toss`, `selected_team_after_toss` -- strings
- `opening_odds` -- float or null

### P&L and bullet legs
- `bullet_number` -- 0 to 3 (each trade can have up to 4 legs)
- `odds` -- float
- `stake` -- float, INR
- `profit` / `loss` -- float, INR
- `status` -- "Open" | "Closed" | "Pending Toss"

### Analysis output (from backend engines)
- Win probability, venue bias score, player matchup rating -- all returned as floats
- Tier flags (`is_elite`, `is_strong`, etc.) -- pre-computed booleans from Python backend
- Do NOT design threshold logic in the UI; the backend sends the badge tier directly

---

## WHAT NOT TO DESIGN

These things look plausible but do not exist in this app:

- Live ball-by-ball commentary or scorecard
- Player stats tables (batting average, bowling economy as primary panels)
- League standings / points tables
- User authentication screens (no login, single operator)
- Notifications or alert feeds
- Charts with real-time updating data (analysis is pre-match only)
- Map views of venues
- Social / sharing features
- Any currency other than INR for stakes/bankroll
- Any odds format other than decimal back/lay pairs

---

## STITCH-SPECIFIC INSTRUCTIONS

When using Stitch MCP to generate or edit a screen:

1. **Reference this color palette explicitly** -- tell Stitch "use a dark theme with
   background #0D1117, card surfaces #141920, accent #6366F1".

2. **Match the density** -- tell Stitch "high-density, compact layout, minimal padding,
   Bloomberg-style data grid aesthetic".

3. **Monospace data** -- specify "numbers and odds values should use monospace / tabular
   font rendering, not proportional".

4. **Tight radius** -- tell Stitch "border radius 4-6px maximum, not pill shapes".

5. **No invented fields** -- only use data fields listed in the "DATA FIELDS THAT ACTUALLY
   EXIST" section above. If Stitch suggests a field not listed there, remove it.

6. **Named classes first** -- tell Stitch to use the named utility classes listed above
   rather than inventing custom CSS (glass-card, badge-elite, btn-primary, etc.).

7. **Label style** -- all input labels should be UPPERCASE, letter-spaced, text-muted,
   very small font. Never sentence-case labels above form fields.

8. **Four-tier badge only** -- when displaying any performance or status indicator, use
   only the four tier badges (elite, strong, caution, danger). Never invent new badge
   colors or tiers.

9. **Backend decides tier** -- never design threshold logic in the UI mock. If you need
   to show a badge, mark it as "tier driven by backend flag" in the spec.

10. **Form footer pattern** -- every form ends with: error/success text on the left,
    primary button on the right. Never put the button inside the form grid.

---

## SCREEN ANATOMY (reference for new page designs)

```
+--------------------------------------------------+
| TOPBAR (48px)  VANTAGE logo | Format button      |
+--------------------------------------------------+
| FORMAT TABS (56px)  ODI | IPL | Trading Dashboard |
+--------+----------------------------------------+
|        |  CONTEXT BAR (56px)                    |
| SIDE   |  Venue | Home Team | Away Team | Years  |
| BAR    +----------------------------------------+
| 240px  |  MAIN CONTENT AREA                     |
|        |  (scrollable, 24px padding)             |
|        |                                         |
|        |  Cards / Analysis Output / Forms        |
+--------+-----------------------------------------+
```

**Cockpit (Trading Dashboard) replaces MAIN CONTENT:**
```
+--------------------------------------------------+
| COCKPIT HEADER  "Trade Cockpit" | format tabs    |
+--------------------------------------------------+
| LEFT PANEL (2/3 width)  RIGHT PANEL (1/3 width)  |
| Pending trades list     |  Active trade detail   |
| or history table        |  or close-trade form   |
+--------------------------------------------------+
```

---

## QUICK REFERENCE -- COMMON PATTERNS

### Stat chip
```
+------------------+
| LABEL (2xs, muted, uppercase)   |
| Value (md, semibold, monospace) |
+------------------+
```

### Field group
```
FIELD LABEL          <- 2xs, uppercase, muted, letter-spaced
+----------------+
| Input / Select |  <- context-input, 32px height
+----------------+
helper text           <- xs, secondary color
```

### Odds row
```
[ Team Select (8ch) ]  [ Back (6ch) ]  [ Lay (6ch) ]
```

### Trade list row
```
[ Team A vs Team B | 24 Apr 2025 ]  [badge-caution NEU]  [2.5 / 2.75]  [View ->]
```

### Badge + label pattern
```
<span class="badge-elite">Top Venue Record</span>
<span class="text-2xs text-muted uppercase">last 5 matches</span>
```

---

*Keep this file referenced whenever a design task goes to Stitch.*
*Last updated: 2026-04-23*
