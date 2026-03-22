# Landing Page Design Spec
# Date: 2026-03-22
# Status: APPROVED

---

## Overview

Landing page for VANTAGE — the format selection gate before the main app shell loads.
User completes Gender → Category → Format, then enters the app.
This is a standalone route (`/landing`) with no shell (no TopBar, no Sidebar, no ContextBar).

---

## Background Layer

- Canvas background: `#0D1117`
- Full-page SVG layer (position: fixed, top: 0, left: 0, width: 100%, height: 100%, z-index: 0, pointer-events: none)
- SVG contents:
  - Cricket pitch rectangle: centered horizontally, lower 40% of screen, ~80px wide × 300px tall
    stroke: `#6366F1`, stroke-opacity: 0.25, stroke-width: 1.5, fill: none
  - Crease lines: 3 horizontal lines across pitch (top crease, bottom crease, one-third line)
    stroke: `#6366F1`, stroke-opacity: 0.20, stroke-width: 1
  - 4 ball trajectory arc curves: smooth bezier curves crossing the full canvas diagonally
    stroke: `#A5B4FC`, stroke-opacity: 0.22, stroke-width: 1.5
  - Radial glow at pitch center: large circle (r=350), radial gradient from rgba(99,102,241,0.10) to transparent
- Static — no animation

---

## Top-Left Wordmark

- `"VANTAGE"` — Inter, weight 600, 13px, color `#64748B`
- `"v2.0"` — same style, color `#4B5563`
- Position: top-left, padding 16px 20px
- z-index: 10
- Terminal app header feel — not a hero logo

---

## Selection Card

- Position: centered both axes (flexbox, full viewport height)
- Max-width: 480px, width: 100%
- Background: `#1A2130` (solid — no glassmorphism, no backdrop-filter)
- Border: 1px solid rgba(255,255,255,0.09)
- Border-radius: 6px (--radius-md)
- Padding: 32px 40px
- z-index: 10

### Card Header
- `"STRATEGIC ALGO EXCHANGE"` — Inter, 10px, weight 600, uppercase, letter-spacing 0.15em, color `#4B5563`
- Margin-bottom: 24px

### Step 01 — Select Gender
- Label: `"01 — SELECT GENDER"` — Inter, 10px, weight 700, uppercase, color `#4B5563`, margin-bottom 8px
- Two chips side by side (equal width, gap 8px):
  - `"Men's"` / `"Women's"`

### Step 02 — Select Category
- Label: `"02 — SELECT CATEGORY"` — same label style, margin-top 16px, margin-bottom 8px
- Two chips side by side (equal width, gap 8px):
  - `"Internationals"` / `"Domestic Leagues"`

### Step 03 — Select Format
- Label: `"03 — SELECT FORMAT"` — same label style, margin-top 16px, margin-bottom 8px
- Chip grid (2 columns, gap 8px). Options depend on Steps 1+2:
  - Men's Internationals:   ODI / T20I / Test
  - Men's Domestic:         IPL / BBL / PSL / CPL / The Hundred
  - Women's Internationals: ODI / T20I / Test
  - Women's Domestic:       WBBL / WPL

### Chip States
- Unselected: background rgba(255,255,255,0.05), border 1px solid rgba(255,255,255,0.10), text rgba(255,255,255,0.65)
- Selected: background `#6366F1`, border 1px solid `#6366F1`, text white, box-shadow: 0 0 16px rgba(99,102,241,0.30)
- All chips: padding 9px 16px, border-radius 4px (--radius-sm), Inter weight 500, font-size 13px, cursor pointer

### Divider
- 1px solid rgba(255,255,255,0.06), margin: 20px 0

### CTA Button
- Text: `"Enter Vantage →"`
- Full width, background `#6366F1`, text white, Inter weight 700, 14px
- Padding: 12px, border-radius: 4px
- Box-shadow: 0 0 20px rgba(99,102,241,0.25)
- Appears only after Step 3 (format) is selected — hidden/disabled before that
- On click: router.push to `/?format=<selected>` (main app shell with format in URL)

### Path Summary
- Below CTA button, centered
- Example: `"Men's · Internationals · T20I"` — Inter, 11px, color rgba(255,255,255,0.30)
- Updates live as user selects each step

---

## Footer

- Text: `"VANTAGE v2.0 · Algo-Trading Intelligence Platform"`
- Inter, 11px, color `#4B5563`, centered
- Position: absolute bottom, padding-bottom 20px

---

## Responsive / Min-Width

- Minimum supported width: 1280px (matches app-wide desktop-only policy)
- Below 1280px: show standard desktop-required message (reuse app-wide pattern)

---

## What Is NOT Here

- No TopBar, no Sidebar, no ContextBar — this is pre-shell
- No glassmorphism / backdrop-filter anywhere
- No animation on background geometry
- No "More..." chip — format list is complete per the combinations above
- No step progress dots (cascading inline steps replace the need)

---

## Files to Create

- `frontend/app/landing/page.tsx` — the landing page component
- `frontend/app/landing/layout.tsx` — layout that excludes the main shell (no TopBar/Sidebar)
- No `loading.tsx` needed — no async data fetch on this page

---

## Stitch Reference

Project: Vantage Landing Page (Stitch project ID: 2039621545729899643)
Screen: VANTAGE - Algo-Trading (Geometric Background)
Approved: 2026-03-22
