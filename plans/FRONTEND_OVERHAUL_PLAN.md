# Frontend Overhaul Plan — Project Vantage
# Status: IN PROGRESS — execution underway
# Last Updated: 2026-03-23

---

## 1. DECISION: Full Rebuild From Scratch

All existing frontend components will be deleted and rebuilt from scratch.
This is not a patch or a style refresh — it is a complete re-architecture.

### Why Full Delete Was Justified
- Every component uses arbitrary Tailwind syntax (`[display:flex]`, `[padding:24px]`)
  which defeats the purpose of a utility framework and is unreadable
- The design is baked into component structure — patching globals.css does not fix it
- The architecture is changing (SPA → page-based), so scaffolding components go away anyway
- 40+ components all with slightly inconsistent styling that cannot be unified by patching

### What Is Being Preserved (Conceptually)
- The manifest-driven architecture — frontend reads from API manifest, never hardcodes modules
- The context bar pattern — persistent global filters (team, venue, innings) across all modules
- The component folder structure — common / layout / inputs / renderers

---

## 2. ARCHITECTURE CHANGE: SPA → Page-Based Routing

### Old Approach (being abandoned)
- Single page at `/` with hash-based navigation (`#phase-analysis`, `#venue-intel`)
- `CategoryScreen` component acts as a giant content switcher
- `activeCategory` React state drives what is shown
- Browser back/forward broken — no real URLs

### New Approach
- Next.js App Router with nested layouts
- Each module gets a real URL: `/phase-analysis`, `/venue-intel`, `/player/[id]` etc.
- Root `layout.tsx` renders the persistent shell (topbar + sidebar + context bar)
- Each `page.tsx` renders its own module content
- Browser history works naturally
- Deep linking works — URLs are shareable and bookmarkable

### Route Structure (implemented)
```
app/
  layout.tsx              <- Root layout (font loading, body wrapper) — DONE
  landing/
    page.tsx              <- /landing — format selector gate — DONE
  (shell)/
    layout.tsx            <- Shell: TopBar + Sidebar + ContextBar (persistent) — DONE
    page.tsx              <- / Dashboard — DONE
    loading.tsx           <- Dashboard skeleton — DONE
    [categoryKey]/
      page.tsx            <- /[any-module] — catch-all, manifest-driven — DONE
      loading.tsx         <- Module skeleton — DONE
```

**Decision: single catch-all route instead of N named pages.**
The manifest declares what modules exist. Hardcoding 8 separate route folders
would duplicate logic and break manifest-driven architecture. One `[categoryKey]`
dynamic route serves all modules — the manifest key becomes the URL segment.
`/phase-analysis`, `/venue-intel`, `/fortress` etc. all resolve to the same
page component, which looks up the category from the manifest by key.

### Context Bar State: React Context → URL Search Params
Currently: team/venue/innings stored in React Context (lost on navigation)
New approach: stored in URL search params
Example: `/phase-analysis?home=India&away=Australia&venue=MCG&innings=1&matches=15`
Benefit: deep links carry full filter state, shareable, bookmarkable

---

## 3. DESIGN SYSTEM: Obsidian Command (Model 5 — Dark Fintech Pro)

Design direction: Bloomberg Terminal precision meets Linear.app refinement.
No glassmorphism. Solid surfaces only. Dense but deliberate.

### 3.1 Color Tokens

#### Background Layers (darkest to lightest)
```
--bg-base:        #0D1117   <- page canvas, shell background
--bg-surface:     #141920   <- primary content areas
--bg-elevated:    #1A2130   <- cards, panels, sidebar
--bg-hover:       #212A3A   <- hover states, active rows
```

#### Accent Colors
```
--accent-ui:      #6366F1   <- Indigo — UI chrome: buttons, active states, focus rings, sidebar active
--accent-ui-hover:#7274F3   <- Indigo hover
--accent-data:    #F59E0B   <- Amber — live data numbers, run rates, signals (market's voice)
```

#### Tier / Semantic Colors (4-tier badge system)
```
--tier-elite:     #22C55E   <- Green  — top performance signal
--tier-strong:    #14B8A6   <- Teal   — solid performance
--tier-caution:   #F59E0B   <- Amber  — warning / below average
--tier-danger:    #EF4444   <- Red    — poor / high risk signal
```

#### Text Hierarchy
```
--text-primary:   #E2E8F0   <- main readable text
--text-secondary: #64748B   <- supporting text, descriptions
--text-muted:     #4B5563   <- labels, group headers, placeholders
--text-disabled:  #2D3748   <- disabled state text
```

#### Border Colors
```
--border-subtle:  rgba(255,255,255,0.05)  <- ghost borders, table rows
--border-default: rgba(255,255,255,0.09)  <- inputs, cards
--border-strong:  rgba(255,255,255,0.12)  <- hover borders
--border-accent:  rgba(99,102,241,0.30)   <- indigo focus/active borders
```

#### Semantic Banner Colors
```
--bg-caution:     rgba(245,158,11,0.10)
--border-caution: rgba(245,158,11,0.25)
--bg-danger:      rgba(239,68,68,0.10)
--border-danger:  rgba(239,68,68,0.25)
--bg-info:        rgba(99,102,241,0.10)
--border-info:    rgba(99,102,241,0.25)
--bg-elite:       rgba(34,197,94,0.08)
--border-elite:   rgba(34,197,94,0.20)
```

### 3.2 Typography

#### Fonts
```
--font-ui:    'Inter', system-ui, sans-serif           <- all UI text
--font-data:  'JetBrains Mono', 'Cascadia Code', monospace  <- all numeric data
```

Two psychological zones:
- Inter = Operational Control (labels, headings, navigation, descriptions)
- JetBrains Mono = Market Intelligence (run rates, percentages, odds, counts)

#### Type Scale
```
--text-2xs:   0.60rem   <- group labels, section headers (uppercase)
--text-xs:    0.65rem   <- captions, fine print
--text-sm:    0.72rem   <- badge text, small labels
--text-base:  0.80rem   <- sidebar items, input labels, body small
--text-md:    0.875rem  <- standard body, data values
--text-lg:    1rem      <- card titles, section headers
--text-xl:    1.25rem   <- page titles
--text-2xl:   1.5rem    <- major headings
--text-display: 2.5rem  <- large data display numbers (run rates etc.)
```

#### Font Weights
```
--weight-normal:   400
--weight-medium:   500
--weight-semibold: 600
--weight-bold:     700
```

### 3.3 Spacing Scale (4px base unit)
```
--space-1:   4px
--space-2:   8px
--space-3:   12px
--space-4:   16px
--space-5:   20px
--space-6:   24px
--space-8:   32px
--space-10:  40px
--space-12:  48px
```

### 3.4 Border Radius (Tight-Tech — no pill shapes)
```
--radius-xs:  2px   <- table cells, small badges
--radius-sm:  4px   <- buttons, inputs, pills, badges
--radius-md:  6px   <- cards, panels, modals
--radius-lg:  8px   <- large containers (reserved)
```

### 3.5 Shadows
```
--shadow-sm:    0 1px 3px rgba(0,0,0,0.30)
--shadow-md:    0 4px 16px rgba(0,0,0,0.35)
--shadow-lg:    0 8px 32px rgba(0,0,0,0.50)
--shadow-glow:  0 0 0 3px rgba(99,102,241,0.20)    <- focus ring glow
```

### 3.6 Transitions
```
--transition-fast:   150ms cubic-bezier(0.4, 0, 0.2, 1)
--transition-normal: 250ms cubic-bezier(0.4, 0, 0.2, 1)
--transition-slow:   350ms cubic-bezier(0.4, 0, 0.2, 1)
```

### 3.7 Layout Dimensions
```
--sidebar-width:           240px
--sidebar-collapsed-width: 60px
--topbar-height:           48px
--context-bar-height:      44px
```

---

## 4. COMPONENT SPECIFICATIONS

### 4.1 Buttons

**Primary**
- Background: --accent-ui (#6366F1)
- Text: white, Inter, --text-md, --weight-semibold
- Padding: 10px 20px
- Radius: --radius-sm (4px)
- No shadow, no gradient
- Hover: background --accent-ui-hover (#7274F3)
- Disabled: opacity 0.5, cursor not-allowed

**Ghost**
- Background: transparent
- Border: 1px solid --border-strong
- Text: --text-secondary
- Hover: background --bg-hover, text --text-primary, border --border-strong

**Danger**
- Background: rgba(239,68,68,0.15)
- Border: 1px solid rgba(239,68,68,0.30)
- Text: --tier-danger (#EF4444)

**All buttons:** flex row, icon+text gap 8px, --radius-sm, --transition-fast

---

### 4.2 Badges / Tier Chips
- Font: Inter, --text-sm (0.72rem), --weight-bold
- Padding: 2px 10px
- Radius: --radius-xs (2px) — intentionally sharp

| Variant | Background | Border | Text |
|---|---|---|---|
| elite | rgba(34,197,94,0.15) | rgba(34,197,94,0.25) | #22C55E |
| strong | rgba(20,184,166,0.15) | rgba(20,184,166,0.25) | #14B8A6 |
| caution | rgba(245,158,11,0.15) | rgba(245,158,11,0.25) | #F59E0B |
| danger | rgba(239,68,68,0.15) | rgba(239,68,68,0.25) | #EF4444 |
| live | rgba(34,197,94,0.12) | none | #22C55E + pulsing dot |
| format | --bg-elevated | --border-default | --text-primary |

---

### 4.3 Stat Pills
- Background: --bg-elevated (#1A2130)
- Border: 1px solid --border-subtle
- Radius: --radius-sm (4px)
- Padding: 6px 12px
- Layout: label on top, value below
- Label: Inter, --text-2xs, --weight-bold, uppercase, 0.1em tracking, --text-muted
- Value: JetBrains Mono, --text-md, --weight-semibold, color varies by signal tier

---

### 4.4 Inputs (Text, Select, Combobox)
- Background: --bg-elevated (#1A2130)
- Border: 1px solid --border-default
- Text: --text-primary, Inter, --text-base
- Placeholder: --text-muted
- Padding: 8px 12px
- Radius: --radius-sm (4px)
- Focus: border 1px solid --accent-ui, box-shadow --shadow-glow
- Error: border 1px solid --tier-danger, error text below in --tier-danger --text-xs
- Disabled: opacity 0.5, cursor not-allowed
- Label above input: Inter, --text-2xs, --weight-bold, uppercase, 0.1em tracking, --text-muted

---

### 4.5 Cards

**Base Card**
- Background: --bg-elevated (#1A2130)
- Border: 1px solid --border-subtle
- Radius: --radius-md (6px)
- Shadow: --shadow-md
- Padding: 16px

**Active / Highlighted Card**
- Same as base + top border 2px solid --accent-ui
- Subtle indigo glow on border: rgba(99,102,241,0.12)

**Signal Card (Elite)**
- Same as base + left border 3px solid --tier-elite
- Background tint: rgba(34,197,94,0.04)

---

### 4.6 Data Table

- Header row: --bg-surface, text --text-muted, uppercase, --text-2xs, --weight-bold, 0.08em tracking, padding 8px 12px
- Body rows: alternating --bg-elevated / --bg-surface (zebra)
- Active row: --bg-hover, left border 3px solid --accent-ui
- Cell padding: 10px 12px
- Numbers: JetBrains Mono, --text-md, color by tier
- No divider lines between rows — spacing only
- Radius on table container: --radius-md

---

### 4.7 Skeleton Loaders
- Base: --bg-elevated (#1A2130)
- Shimmer highlight: --bg-hover (#212A3A)
- Animation: left-to-right shimmer, 1.5s infinite
- Radius: --radius-sm

---

### 4.8 Sidebar Items
- Default: text --text-secondary, Inter --text-base, --weight-medium
- Hover: text --text-primary, background --bg-hover
- Active: text white, background rgba(99,102,241,0.10), left border 3px solid --accent-ui, --weight-semibold
- Group labels: --text-2xs, --weight-bold, uppercase, 0.1em tracking, --text-muted, margin-top 20px

---

### 4.9 Scrollbar
- Width: 6px
- Track: transparent
- Thumb: --bg-hover (#212A3A)
- Thumb hover: --text-muted (#4B5563)
- Radius: 3px

---

## 5. COMPONENT BUILD ORDER (Layer-by-Layer)

Build strictly in this order. No layer skips.

```
LAYER 1 — Design Tokens                                         DONE
  globals.css with all CSS custom properties above

LAYER 2 — Primitives (no business logic, no cricket knowledge)  DONE
  Button (primary / ghost / danger / disabled / icon+text)
  Badge (elite / strong / caution / danger / live / format)
  StatPill (label + value)
  Input (text / select / combobox / slider / error state)
  Card (base / active / signal)
  Skeleton (bar / block / row)
  Divider
  Tooltip

LAYER 3 — Composites (domain-aware, built from primitives)      DONE
  TopBar (wordmark + format tabs + live indicator)
  Sidebar (grouped nav from manifest + collapse toggle)
  ContextBar (filter fields from manifest)
  PhaseCard (StatPills + Badge + relative bar)
  PlayerCard (profile + stats)
  DataTable (header + rows + tier coloring)
  FilterNotice (amber banner with filter summary)
  PageHeader (title + icon + subtitle)

LAYER 4 — Pages                                                 IN PROGRESS
  /landing                    DONE
  / (Dashboard)               DONE
  /[categoryKey] (all modules) DONE — catch-all route, manifest-driven

LAYER 5 — Renderer Polish (per output_type)                     NEXT
  Each renderer in components/renderers/ reviewed against actual API output.
  Broken or ugly renderers fixed one by one. No spec needed — fix what looks wrong.
  Priority: phase-analysis, venue-intel, fortress, h2h, player, predictors.
  Note: CategoryBanners.tsx uses arbitrary Tailwind — rewrite during this phase.
```

---

## 6. MANIFEST-DRIVEN PATTERN (must survive rebuild)

The frontend NEVER hardcodes module names, sidebar items, or context fields.
Everything is driven by the manifest fetched from GET /api/manifest at load time.

- Sidebar items: built from manifest.categories
- Context bar fields: built from manifest.context_fields
- Navigation root: from manifest.navigation_root
- Function list per module: from category.functions

This means adding a backend module auto-appears in the frontend with zero frontend changes.

---

## 7. SHELL LAYOUT DECISIONS (RESOLVED)

### TopBar
- Contains: logo/wordmark (left) + selected format label only
- Format label examples: "Men's · IPL", "Men's · T20I", "Women's · ODI"
- Format label is clickable — returns user to landing page to change format
- No global search, no user profile, no notifications, no extra controls
- Intentionally minimal — format context is the only persistent state shown

### Format Selection Flow (Landing Page — before app shell loads)
User completes this flow before entering the main app:
  Step 1: Select Gender        -> Men's / Women's
  Step 2: Select Category      -> Internationals / Domestic Leagues
  Step 3: Select Format
    Men's Internationals       -> ODI / T20I / Test
    Men's Domestic Leagues     -> IPL / BBL / PSL / CPL / The Hundred / etc.
    Women's Internationals     -> ODI / T20I / Test
    Women's Domestic Leagues   -> WBBL / WPL / etc.
Once format selected -> main app shell loads, all modules scoped to that format.

### Sidebar
- Default state: expanded (240px) on every load
- Collapse toggle available but does not persist across sessions

### Context Bar
- Dynamic per page — each page declares its own required fields
- Common fields (Home Team, Away Team, Venue) retain their value across page navigation
- State stored in URL search params — switching pages preserves shared filter values
- Fields irrelevant to the current page simply do not appear
- Manifest drives which fields each module requires

---

## 8. LANDING PAGE DECISIONS (RESOLVED)

### Layout
- Full-screen cricket stadium photograph background (floodlit night match, cinematic wide-angle)
- Dark gradient overlay: top rgba(13,17,23,0.75) to bottom rgba(13,17,23,0.95)
- Stadium visible but subdued — UI sits clearly on top

### Content — Vertical centered stack
- "VANTAGE" wordmark: Inter 4rem weight 800 letter-spacing -0.03em, white with indigo glow (#A5B4FC)
- Subtitle: "Strategic Algo Exchange" — Inter 0.9rem weight 400, rgba(255,255,255,0.45), uppercase 0.15em tracking
- Three-step selection card (centered, max-width 560px)
- Step progress dots above card (indigo = active, dim = inactive)
- Version footer: "VANTAGE v2.0 · Algo-Trading Intelligence Platform" — dim, bottom center

### Selection Card
- bg rgba(20,25,32,0.90), border 1px solid rgba(255,255,255,0.10), border-radius 12px, padding 40px 48px
- backdrop-filter blur(8px) — ONLY on this card, nowhere else in the app
- Three cascading steps visible on one card (no separate screens):
  Step 1: Gender         -> Men's / Women's
  Step 2: Category       -> Internationals / Domestic Leagues
  Step 3: Format         -> chips grid (options change based on steps 1+2)
    Men's Internationals   -> ODI / T20I / Test
    Men's Domestic         -> IPL / BBL / PSL / CPL / The Hundred / etc.
    Women's Internationals -> ODI / T20I / Test
    Women's Domestic       -> WBBL / WPL / etc.

### Button States
- Unselected: bg rgba(255,255,255,0.06), border rgba(255,255,255,0.10), text rgba(255,255,255,0.70)
- Selected: bg #6366F1, border #6366F1, white text, glow box-shadow 0 0 20px rgba(99,102,241,0.35)

### CTA
- "Enter Vantage →" — full-width, bg #6366F1, white, Inter 1rem weight 700, glow shadow
- Appears only after format is selected (not before)
- Path summary below button: "Men's · Internationals · T20I" in rgba(255,255,255,0.35)

### Note on background image
- Stitch cannot render real photographs — the mockup approximates the background
- In implementation Gemini will use a real floodlit cricket stadium image as background
- All other design decisions (layout, card, typography, colors) are locked from the mockup

---

## 9. DASHBOARD / HOME PAGE DECISIONS (RESOLVED)

### Approach
Option A — Quick Launch launchpad. No data, no stats. Pure module navigation grid.

### Layout
- Page header: Home icon (indigo) + "Dashboard" title + subtitle showing selected format
- 3×3 module grid (9 cards), 16px gap
- Footer info strip below grid

### Module Cards
- bg #1A2130, border rgba(255,255,255,0.07), radius 6px
- Hover: border rgba(99,102,241,0.30), bg #1E2638, top border 2px solid #6366F1
- Content: icon square (36x36, indigo bg) + module name + description + function count
- Arrow (→) top-right corner

### Module Accent Split
- Analysis modules (Venue, Rivalry, Phase, Player): indigo accent (#6366F1)
- Prediction modules (Score Predictor, Win Probability): amber accent (#F59E0B)

### Context Bar on Dashboard
- Shows only HOME TEAM + AWAY TEAM dropdowns (minimal — no analysis context needed yet)
- Helper text: "Set match context to begin analysis"

### Footer Strip
- Info hint: "Set Home Team and Away Team in the context bar above to unlock venue-specific analysis"
- Right: "9 modules available"

---

## 10. ERROR AND EMPTY STATE DECISIONS (RESOLVED)

### Empty States
Triggered when API returns successfully but with no data.
- No illustrations, no cartoon faces, no generic "Oops!"
- Centered inside content area: muted module icon + bold heading + specific subtext + action button
- Heading: "No data found" (or module-specific variant)
- Subtext: specific reason — e.g. "No T20I matches found for India vs Australia at MCG with current filters"
- Action button: "Adjust Filters" or "Clear Filters" (ghost button style)
- Color: all muted — icon in #4B5563, heading in #64748B, subtext in #4B5563

### Level 1 — Component Error (one card/section fails)
Triggered when a single API call inside a card fails. Rest of page continues working.
- Inline error banner INSIDE the failing card only — does not affect other cards
- Red left border (3px solid #EF4444) on the card
- Content: small danger icon + "Failed to load" + specific message + small "Retry" text link
- Background: rgba(239,68,68,0.06) tint inside the card
- No toast notifications — inline only so the error stays visible and is tied to its component

### Level 2 — Page Error (entire module fails to load)
Triggered when the main data fetch for a page fails entirely.
- Replace page content area with centered error state
- Icon: AlertCircle in #EF4444
- Heading: "Failed to load [Module Name]" — Inter weight 700 #E2E8F0
- Subtext: error message or "Unable to reach the analysis engine. Check your connection." — #64748B
- One retry button (primary style) — retrying is useful here, transient network issues are common
- Sidebar and topbar remain fully functional

### Level 3 — App-Level Error (manifest fails, app cannot boot)
Triggered when GET /api/manifest fails and the app cannot initialise.
- Full screen error — shell cannot render, standalone centered layout on #0D1117 base
- VANTAGE wordmark at top (so user knows which app this is)
- Large AlertCircle icon in #EF4444
- Heading: "Unable to connect to Vantage" — Inter 1.25rem weight 700 #E2E8F0
- Specific instructions (not a retry button):
  1. "Ensure the Vantage backend is running on port 8000"
  2. "Check your network connection"
  3. "Run: python -m uvicorn api.main:app --reload"
- No retry button — instructions are more honest and useful than automated retry
- Footer: "Error details: [error message in monospace]" — collapsible, for debugging

---

## 11. LOADING STRATEGY DECISIONS (RESOLVED)

### Page Loading — Skeletons via Next.js Suspense
- Every route gets a `loading.tsx` file alongside its `page.tsx`
- `loading.tsx` renders skeleton shapes matching that page's layout
- Next.js App Router automatically shows `loading.tsx` while page data fetches
- No manual loading state management — framework handles it
- No spinners for page-level loading anywhere in the app
- Skeleton shapes are Layer 2 primitives (already in design system)
- When data arrives: real content replaces skeletons with a fade-in transition

### Form Submissions / Triggered Analysis — Spinner Inside Button
- When user clicks "Run Analysis" or any submit action:
  - Button shows inline spinner + "Analysing..." text
  - Button is disabled during the request
  - Previous results remain visible until new results arrive
  - New results fade in when ready — no full skeleton replacement
- No spinners anywhere except inside buttons during active submissions

---

## 12. RESPONSIVE STRATEGY DECISIONS (RESOLVED)

### Desktop Only
- Minimum supported width: 1280px
- Below 1280px: show a full-screen message — "Vantage requires a desktop browser (1280px minimum)"
- No tablet breakpoints, no mobile layouts, no responsive compromises
- Desktop quality is never degraded to accommodate smaller screens
- Mobile support is a separate future project — not in scope for this rebuild

---

## 13. RENDERER POLISH STRATEGY (REVISED)

### Why the Stitch-first approach was dropped
The original plan required a Stitch mockup for each module before building.
This is now superseded because:
- All modules are reachable via the `[categoryKey]` catch-all route
- The renderers already exist (built in the old SPA era) and produce real output
- The right workflow is: navigate → run a function → see what looks broken → fix it
- Stitch cannot render real API data, making mockups less useful than the running app

### Revised process — Navigate, identify, fix
1. Navigate to a module in the running app
2. Set context (teams, venue) in the context bar
3. Run a function — observe the result
4. If the renderer looks correct → move on
5. If broken or ugly → fix that specific renderer component
6. Repeat per module

### Renderer Status
| # | Module | Route | Renderer(s) | Status |
|---|---|---|---|---|
| 1 | Phase Analysis | /phase-analysis | PhaseAnalysisCard | REVIEW NEEDED |
| 2 | Venue Intel | /venue-intel | VenueMatchupReport | REVIEW NEEDED |
| 3 | Fortress | /fortress | FortressReport | REVIEW NEEDED |
| 4 | H2H Global | /h2h | GlobalH2HReport | REVIEW NEEDED |
| 5 | H2H Country | /h2h | CountryH2HReport | REVIEW NEEDED |
| 6 | Player Profile | /player | PlayerProfileCard, PlayerBattingIntel, PlayerBowlingIntel | REVIEW NEEDED |
| 7 | Score Predictor | /score-predictor | PredictionCard | REVIEW NEEDED |
| 8 | Win Probability | /win-probability | PredictionCard | REVIEW NEEDED |

### Also flagged for cleanup
- `CategoryBanners.tsx` — uses arbitrary Tailwind throughout. Rewrite during renderer polish phase.
- `CategoryScreen.tsx` — orphaned SPA component. Can be deleted once renderers are verified.

---

## 14. WHAT GEMINI MUST NOT DO

- Must not use arbitrary Tailwind syntax like [display:flex] or [padding:24px]
- Must not hardcode module names, routes, or sidebar items
- Must not use glassmorphism (backdrop-filter, blur)
- Must not use border-radius above 8px anywhere
- Must not use pill-shaped buttons (no rounded-full on buttons)
- Must not skip the layer order — no page before its composites exist
- Must not add inline styles except where Tailwind genuinely cannot express it
- Must use JetBrains Mono for ALL numeric data values without exception
- Must use Inter for ALL UI text without exception

---

*This document is the source of truth for the frontend overhaul.*
*Update it as decisions are made. Do not execute any task until Section 7 checklist is resolved.*
