# Landing Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `/landing` format-selection page — a standalone pre-shell screen where users pick Gender → Category → Format before entering the main app.

**Architecture:** Next.js App Router route groups are used to isolate the landing page from the main app shell. The root layout (`app/layout.tsx`) is stripped to html+body+fonts only. A new `app/(shell)/layout.tsx` provides TopBar/Sidebar/ContextBar for all existing app routes. The landing page at `app/landing/` gets its own minimal layout with no shell. The landing page itself is a single `"use client"` component managing local state (3 useState hooks) with an inline SVG background.

**Tech Stack:** Next.js 14 App Router, TypeScript, Tailwind CSS (token-only classes), React useState, next/navigation useRouter, Lucide icons

**Spec:** `docs/superpowers/specs/2026-03-22-landing-page-design.md`
**Standards:** `docs/guides/frontendStandards/TACTICAL_EXECUTION.md`, `UI_IMPLEMENTATION.md`, `PERF_RESILIENCE_A11Y_TESTING.md`

---

## File Map

| Action | File | Responsibility |
|--------|------|----------------|
| MODIFY | `frontend/app/layout.tsx` | Strip to html+body+fonts only — no shell |
| CREATE | `frontend/app/(shell)/layout.tsx` | Shell layout: AppProvider + TopBar + Sidebar + ContextBar |
| CREATE | `frontend/app/(shell)/page.tsx` | Dashboard page (exact copy of current `app/page.tsx`) |
| CREATE | `frontend/app/(shell)/loading.tsx` | Dashboard loading skeleton (exact copy of current `app/loading.tsx`) |
| CREATE | `frontend/app/landing/layout.tsx` | Minimal layout — just renders children, no shell |
| CREATE | `frontend/app/landing/page.tsx` | Landing page — SVG background + wordmark + selection card + footer |
| CREATE | `frontend/components/common/CricketGeometry.tsx` | Inline SVG background component (pitch + arcs + glow) |

---

## Task 1: Restructure app/ to use route groups

**Why:** The root `app/layout.tsx` currently renders TopBar/Sidebar/ContextBar for every route. The landing page must not have these. Next.js route groups (`(shell)`) let us scope the shell to only the routes that need it.

**Standards note — intentional deviation from TACTICAL_EXECUTION Rule 9:** Rule 9 states "the persistent shell lives in `app/layout.tsx` and never unmounts." This plan moves the shell to `app/(shell)/layout.tsx`. This is correct and intentional — Rule 9 was written before landing-page isolation was required. Route groups are the proper Next.js App Router mechanism for this. The shell still never unmounts for any route inside `(shell)/`; the rule's intent is preserved. Self-audit checklist item 13 ("no out-of-scope files touched") is satisfied — this refactor is explicitly in task scope.

**Files:**
- Modify: `frontend/app/layout.tsx`
- Create: `frontend/app/(shell)/layout.tsx`
- Create: `frontend/app/(shell)/page.tsx`
- Create: `frontend/app/(shell)/loading.tsx`

- [ ] **Step 1: Strip the root layout to html+body+fonts only**

Edit `frontend/app/layout.tsx` to remove AppProvider, TopBar, Sidebar, ContextBar. Keep only the html/body wrapper and font injection:

```tsx
import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Vantage | Strategic Algo Exchange",
  description:
    "AI-powered cricket analysis for algo-trading. " +
    "Venue intelligence, rivalry analysis, score prediction, and match-day packs.",
  icons: {
    icon: "/icon.png",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
```

- [ ] **Step 2: Create `frontend/app/(shell)/layout.tsx`**

This layout wraps all existing app routes with the shell. It is identical to what `app/layout.tsx` had before — minus the html/body wrapper (root layout owns that):

```tsx
import { Suspense } from "react";
import { AppProvider } from "@/lib/context";
import TopBar from "@/components/layout/TopBar";
import Sidebar from "@/components/layout/Sidebar";
import ContextBar from "@/components/layout/ContextBar";

export default function ShellLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AppProvider>
      <TopBar />
      <div className="app-shell">
        <Sidebar />
        <div className="app-main">
          <Suspense fallback={<div className="context-bar" aria-hidden="true" />}>
            <ContextBar />
          </Suspense>
          <main className="app-content">
            {children}
          </main>
        </div>
      </div>
    </AppProvider>
  );
}
```

- [ ] **Step 3: Create `frontend/app/(shell)/page.tsx`**

Copy the contents of `frontend/app/page.tsx` verbatim into `frontend/app/(shell)/page.tsx`. No changes to the content.

- [ ] **Step 4: Create `frontend/app/(shell)/loading.tsx`**

Copy the contents of `frontend/app/loading.tsx` verbatim into `frontend/app/(shell)/loading.tsx`. No changes.

- [ ] **Step 5: Delete the now-redundant files**

```bash
rm frontend/app/page.tsx
rm frontend/app/loading.tsx
```

- [ ] **Step 6: Verify dev server still loads dashboard**

Start dev server: `cd frontend && npm run dev`
Navigate to `http://localhost:3000/`
Expected: Dashboard loads correctly with TopBar, Sidebar, ContextBar intact.
If broken — do not proceed. Fix the route group structure first.

- [ ] **Step 7: Commit**

```bash
git add frontend/app/layout.tsx frontend/app/(shell)/layout.tsx frontend/app/(shell)/page.tsx frontend/app/(shell)/loading.tsx
git rm frontend/app/page.tsx frontend/app/loading.tsx
git commit -m "refactor(app): extract shell into route group for landing page isolation"
```

---

## Task 2: CricketGeometry background component

**Why:** The SVG background is visually complex enough to live in its own file. This keeps `page.tsx` under the 300-line limit and makes the geometry independently reviewable.

**Files:**
- Create: `frontend/components/common/CricketGeometry.tsx`

- [ ] **Step 1: Create the component**

```tsx
// frontend/components/common/CricketGeometry.tsx
// Full-page SVG background: cricket pitch lines + trajectory arcs + radial glow.
// Static — no animation. Pointer events disabled so it never intercepts clicks.

export default function CricketGeometry() {
  return (
    <svg
      aria-hidden="true"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        zIndex: 0,
        pointerEvents: "none",
      }}
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <radialGradient id="pitchGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="rgba(99,102,241,0.10)" />
          <stop offset="100%" stopColor="rgba(99,102,241,0)" />
        </radialGradient>
      </defs>

      {/* Radial glow bloom centered on pitch */}
      <ellipse
        cx="50%"
        cy="72%"
        rx="350"
        ry="350"
        fill="url(#pitchGlow)"
      />

      {/* Cricket pitch rectangle — centered horizontally, lower 40% */}
      <rect
        x="calc(50% - 40px)"
        width="80"
        y="60%"
        height="300"
        fill="none"
        stroke="#6366F1"
        strokeWidth="1.5"
        strokeOpacity="0.25"
      />

      {/* Crease lines — top, one-third, bottom of pitch */}
      <line x1="calc(50% - 40px)" y1="60%" x2="calc(50% + 40px)" y2="60%"
        stroke="#6366F1" strokeWidth="1" strokeOpacity="0.20" />
      <line x1="calc(50% - 40px)" y1="calc(60% + 100px)" x2="calc(50% + 40px)" y2="calc(60% + 100px)"
        stroke="#6366F1" strokeWidth="1" strokeOpacity="0.20" />
      <line x1="calc(50% - 40px)" y1="calc(60% + 300px)" x2="calc(50% + 40px)" y2="calc(60% + 300px)"
        stroke="#6366F1" strokeWidth="1" strokeOpacity="0.20" />

      {/* Ball trajectory arcs — bezier curves crossing canvas diagonally */}
      <path
        d="M -100 800 C 300 400, 700 600, 1200 100"
        fill="none" stroke="#A5B4FC" strokeWidth="1.5" strokeOpacity="0.22"
      />
      <path
        d="M 200 900 C 500 300, 900 700, 1600 200"
        fill="none" stroke="#A5B4FC" strokeWidth="1.5" strokeOpacity="0.18"
      />
      <path
        d="M 1500 850 C 1100 400, 600 650, 50 150"
        fill="none" stroke="#A5B4FC" strokeWidth="1.5" strokeOpacity="0.20"
      />
      <path
        d="M 100 50 C 400 500, 1000 200, 1550 700"
        fill="none" stroke="#A5B4FC" strokeWidth="1.5" strokeOpacity="0.15"
      />
    </svg>
  );
}
```

Note: SVG `calc()` in attribute values is not supported in all renderers. Use percentage + fixed offset approximations instead for `rect` x position: `x="calc(50% - 40px)"` should be replaced with a viewBox-relative approach. See Step 2.

- [ ] **Step 2: Fix SVG coordinate strategy**

SVG attributes do not support CSS `calc()`. Use a fixed viewBox to make coordinates predictable.

**SVG hex exception — accepted:** SVG presentation attributes (`stroke`, `fill`, `stopColor`) cannot use CSS `var()` reliably in all renderers. Raw hex values `#6366F1` (accent-ui) and `#A5B4FC` (light indigo) are accepted exceptions for SVG geometry attributes only. These map directly to design tokens but must be hardcoded in this context. Not a standards violation.

```tsx
export default function CricketGeometry() {
  // ViewBox: 1440 x 900 (standard desktop target)
  // Pitch: centered at x=720, lower section starting at y=540
  const pitchX = 680;   // 720 - 40 (half pitch width)
  const pitchY = 540;
  const pitchW = 80;
  const pitchH = 300;

  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 1440 900"
      preserveAspectRatio="xMidYMid slice"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        zIndex: 0,
        pointerEvents: "none",
      }}
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <radialGradient id="pitchGlow" cx="50%" cy="75%" r="35%">
          <stop offset="0%" stopColor="rgba(99,102,241,0.10)" />
          <stop offset="100%" stopColor="rgba(99,102,241,0)" />
        </radialGradient>
      </defs>

      {/* Radial glow */}
      <rect width="1440" height="900" fill="url(#pitchGlow)" />

      {/* Pitch rectangle */}
      <rect
        x={pitchX} y={pitchY}
        width={pitchW} height={pitchH}
        fill="none"
        stroke="#6366F1" strokeWidth="1.5" strokeOpacity="0.25"
      />

      {/* Crease lines */}
      <line x1={pitchX} y1={pitchY} x2={pitchX + pitchW} y2={pitchY}
        stroke="#6366F1" strokeWidth="1" strokeOpacity="0.20" />
      <line x1={pitchX} y1={pitchY + 100} x2={pitchX + pitchW} y2={pitchY + 100}
        stroke="#6366F1" strokeWidth="1" strokeOpacity="0.20" />
      <line x1={pitchX} y1={pitchY + pitchH} x2={pitchX + pitchW} y2={pitchY + pitchH}
        stroke="#6366F1" strokeWidth="1" strokeOpacity="0.20" />

      {/* Trajectory arcs */}
      <path d="M -100 800 C 300 400, 700 600, 1300 100"
        fill="none" stroke="#A5B4FC" strokeWidth="1.5" strokeOpacity="0.22" />
      <path d="M 200 920 C 500 300, 900 700, 1600 200"
        fill="none" stroke="#A5B4FC" strokeWidth="1.5" strokeOpacity="0.18" />
      <path d="M 1550 850 C 1100 400, 600 650, 50 150"
        fill="none" stroke="#A5B4FC" strokeWidth="1.5" strokeOpacity="0.20" />
      <path d="M 100 50 C 400 500, 1000 200, 1550 720"
        fill="none" stroke="#A5B4FC" strokeWidth="1.5" strokeOpacity="0.15" />
    </svg>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/components/common/CricketGeometry.tsx
git commit -m "feat(landing): add CricketGeometry SVG background component"
```

---

## Task 3: Landing page layout and page

**Files:**
- Create: `frontend/app/landing/layout.tsx`
- Create: `frontend/app/landing/page.tsx`

- [ ] **Step 1: Create `frontend/app/landing/layout.tsx`**

Minimal layout — just renders children. No shell. The root layout provides html+body.

```tsx
export default function LandingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
```

- [ ] **Step 2: Define the format options data**

At the top of `page.tsx`, define the format map. This is static config — not domain logic in a component, just data lookup:

```tsx
type Gender = "mens" | "womens";
type Category = "internationals" | "domestic";
type FormatSlug =
  | "odi" | "t20i" | "test"
  | "ipl" | "bbl" | "psl" | "cpl" | "the-hundred"
  | "wbbl" | "wpl";

interface FormatOption {
  label: string;
  slug: FormatSlug;
}

const FORMAT_OPTIONS: Record<Gender, Record<Category, FormatOption[]>> = {
  mens: {
    internationals: [
      { label: "ODI", slug: "odi" },
      { label: "T20I", slug: "t20i" },
      { label: "Test", slug: "test" },
    ],
    domestic: [
      { label: "IPL", slug: "ipl" },
      { label: "BBL", slug: "bbl" },
      { label: "PSL", slug: "psl" },
      { label: "CPL", slug: "cpl" },
      { label: "The Hundred", slug: "the-hundred" },
    ],
  },
  womens: {
    internationals: [
      { label: "ODI", slug: "odi" },
      { label: "T20I", slug: "t20i" },
      { label: "Test", slug: "test" },
    ],
    domestic: [
      { label: "WBBL", slug: "wbbl" },
      { label: "WPL", slug: "wpl" },
    ],
  },
};

const GENDER_LABELS: Record<Gender, string> = {
  mens: "Men's",
  womens: "Women's",
};

const CATEGORY_LABELS: Record<Category, string> = {
  internationals: "Internationals",
  domestic: "Domestic Leagues",
};
```

- [ ] **Step 3: Build the SelectionChip sub-component**

```tsx
interface ChipProps {
  label: string;
  selected: boolean;
  onClick: () => void;
  fullWidth?: boolean;
}

function SelectionChip({ label, selected, onClick, fullWidth }: ChipProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={fullWidth ? { gridColumn: "1 / -1" } : undefined}
      className={[
        "landing-chip",
        selected ? "landing-chip--selected" : "landing-chip--unselected",
      ].join(" ")}
    >
      {label}
    </button>
  );
}
```

- [ ] **Step 4: Build the StepLabel sub-component**

```tsx
function StepLabel({ children }: { children: React.ReactNode }) {
  return <p className="landing-step-label">{children}</p>;
}
```

- [ ] **Step 5: Build the main LandingPage component**

```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import CricketGeometry from "@/components/common/CricketGeometry";

// ... (type definitions, FORMAT_OPTIONS, GENDER_LABELS, CATEGORY_LABELS, sub-components from above)

export default function LandingPage() {
  const router = useRouter();
  // Blank state on every mount — spec requires landing always starts fresh.
  // useState(null) satisfies this: Next.js App Router fully remounts client
  // components on navigation to a new route, so bfcache state restoration
  // is not a concern here. No useEffect reset needed.
  const [gender, setGender] = useState<Gender | null>(null);
  const [category, setCategory] = useState<Category | null>(null);
  const [format, setFormat] = useState<FormatSlug | null>(null);

  function handleGenderSelect(g: Gender) {
    setGender(g);
    setCategory(null);
    setFormat(null);
  }

  function handleCategorySelect(c: Category) {
    setCategory(c);
    setFormat(null);
  }

  function handleFormatSelect(f: FormatSlug) {
    setFormat(f);
  }

  function handleEnter() {
    if (!gender || !category || !format) return;
    router.push(`/?gender=${gender}&category=${category}&format=${format}`);
  }

  const formatOptions = gender && category ? FORMAT_OPTIONS[gender][category] : [];
  const isCtaEnabled = gender !== null && category !== null && format !== null;

  // Build path summary (show only selected segments)
  const pathParts: string[] = [];
  if (gender) pathParts.push(GENDER_LABELS[gender]);
  if (category) pathParts.push(CATEGORY_LABELS[category]);
  if (format) {
    const found = formatOptions.find((o) => o.slug === format);
    if (found) pathParts.push(found.label);
  }
  const pathSummary = pathParts.join(" · ");

  return (
    <div className="landing-root" style={{ backgroundColor: "var(--bg-base)" }}>
      <CricketGeometry />

      {/* Wordmark */}
      <header className="landing-wordmark" aria-label="Vantage">
        <span className="landing-wordmark-name">VANTAGE</span>
        <span className="landing-wordmark-version">v2.0</span>
      </header>

      {/* Selection card */}
      <main className="landing-center" role="main">
        <div className="landing-card" aria-label="Format selection">
          <p className="landing-subtitle">STRATEGIC ALGO EXCHANGE</p>

          {/* Step 01 — Gender */}
          <StepLabel>01 — SELECT GENDER</StepLabel>
          <div className="landing-chip-row">
            <SelectionChip
              label="Men's"
              selected={gender === "mens"}
              onClick={() => handleGenderSelect("mens")}
            />
            <SelectionChip
              label="Women's"
              selected={gender === "womens"}
              onClick={() => handleGenderSelect("womens")}
            />
          </div>

          {/* Step 02 — Category */}
          <StepLabel>02 — SELECT CATEGORY</StepLabel>
          <div className="landing-chip-row">
            <SelectionChip
              label="Internationals"
              selected={category === "internationals"}
              onClick={() => handleCategorySelect("internationals")}
            />
            <SelectionChip
              label="Domestic Leagues"
              selected={category === "domestic"}
              onClick={() => handleCategorySelect("domestic")}
            />
          </div>

          {/* Step 03 — Format */}
          <StepLabel>03 — SELECT FORMAT</StepLabel>
          <div className="landing-chip-grid">
            {formatOptions.map((opt, idx) => {
              const isOrphan =
                formatOptions.length % 2 !== 0 &&
                idx === formatOptions.length - 1;
              return (
                <SelectionChip
                  key={opt.slug}
                  label={opt.label}
                  selected={format === opt.slug}
                  onClick={() => handleFormatSelect(opt.slug)}
                  fullWidth={isOrphan}
                />
              );
            })}
          </div>

          <div className="landing-divider" aria-hidden="true" />

          {/* CTA */}
          <button
            type="button"
            className="landing-cta"
            onClick={handleEnter}
            disabled={!isCtaEnabled}
            aria-disabled={!isCtaEnabled}
          >
            Enter Vantage →
          </button>

          {pathSummary && (
            <p className="landing-path-summary" aria-live="polite">
              {pathSummary}
            </p>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="landing-footer">
        <p>VANTAGE v2.0 · Algo-Trading Intelligence Platform</p>
      </footer>
    </div>
  );
}
```

- [ ] **Step 6: Add landing page CSS classes to globals.css**

Add these classes to `frontend/app/globals.css`. Use CSS custom properties — no raw hex, no arbitrary Tailwind:

```css
/* ─── Landing Page ─────────────────────────────────────────── */

.landing-root {
  position: relative;
  min-height: 100vh;
  min-width: 1280px;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-base);
}

.landing-wordmark {
  position: relative;
  z-index: 10;
  padding: var(--space-4) var(--space-5);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.landing-wordmark-name {
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: var(--weight-semibold);
  color: var(--text-secondary);
  letter-spacing: 0.04em;
}

.landing-wordmark-version {
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: var(--weight-medium);
  color: var(--text-muted);
}

.landing-center {
  position: relative;
  z-index: 10;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-8) var(--space-4);
}

.landing-card {
  width: 100%;
  max-width: 480px;
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 32px 40px;
}

.landing-subtitle {
  font-family: var(--font-ui);
  font-size: var(--text-2xs);
  font-weight: var(--weight-semibold);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: var(--space-6);
}

.landing-step-label {
  font-family: var(--font-ui);
  font-size: var(--text-2xs);
  font-weight: var(--weight-bold);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-top: var(--space-4);
  margin-bottom: var(--space-2);
}

.landing-step-label:first-of-type {
  margin-top: 0;
}

.landing-chip-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-2);
}

.landing-chip-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-2);
}

.landing-chip {
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: var(--weight-medium);
  padding: 9px var(--space-4);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background-color var(--transition-fast), border-color var(--transition-fast), color var(--transition-fast);
  text-align: center;
  border-width: 1px;
  border-style: solid;
}

.landing-chip--unselected {
  /* --border-subtle = rgba(255,255,255,0.05) — exact token match for background */
  background-color: var(--border-subtle);
  /* --border-default = rgba(255,255,255,0.09) — spec says 0.10, using token (0.01 rounding accepted) */
  border-color: var(--border-default);
  color: rgba(255, 255, 255, 0.65);
}

.landing-chip--unselected:hover {
  /* rgba(255,255,255,0.09) = --border-default; used for bg on hover */
  background-color: var(--border-default);
  /* --border-strong = rgba(255,255,255,0.12) — spec says 0.18; no token at 0.18, raw value used */
  border-color: rgba(255, 255, 255, 0.18);
  color: rgba(255, 255, 255, 0.80);
}

.landing-chip--selected {
  background-color: var(--accent-ui);
  border-color: var(--accent-ui);
  /* #ffffff has no token; used as pure white on indigo — accepted exception */
  color: #ffffff;
  /* --border-accent = rgba(99,102,241,0.30) — exact token match */
  box-shadow: 0 0 16px var(--border-accent);
}

.landing-divider {
  height: 1px;
  background-color: rgba(255, 255, 255, 0.06);
  margin: var(--space-5) 0;
}

.landing-cta {
  width: 100%;
  background-color: var(--accent-ui);
  /* #ffffff has no token; pure white on indigo — accepted exception */
  color: #ffffff;
  font-family: var(--font-ui);
  font-size: 14px;
  font-weight: var(--weight-bold);
  padding: 12px;
  border-radius: var(--radius-sm);
  border: none;
  cursor: pointer;
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.25);
  transition: background-color var(--transition-fast), box-shadow var(--transition-fast);
}

.landing-cta:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  box-shadow: none;
}

.landing-cta:not(:disabled):hover {
  background-color: var(--accent-ui-hover);
  box-shadow: 0 0 28px rgba(99, 102, 241, 0.40);
}

.landing-path-summary {
  font-family: var(--font-ui);
  font-size: 11px;
  color: rgba(255, 255, 255, 0.30);
  text-align: center;
  margin-top: var(--space-3);
  min-height: 16px;
}

.landing-footer {
  position: relative;
  z-index: 10;
  text-align: center;
  padding-bottom: var(--space-5);
}

.landing-footer p {
  font-family: var(--font-ui);
  font-size: 11px;
  color: var(--text-muted);
}
```

- [ ] **Step 7: Run the F1–F3 gates**

```bash
cd frontend
# F1 — lint
npx eslint . --ext .ts,.tsx --max-warnings 0

# F2 — paradigm (no arbitrary Tailwind, no inline styles except runtime)
# Manual check: grep for '[' in landing files
grep -n "\[" app/landing/page.tsx components/common/CricketGeometry.tsx || echo "PASS — no arbitrary Tailwind"

# F3 — TypeScript
npx tsc --noEmit
```

All three must pass before F4.

- [ ] **Step 8: Run the F4 visual acceptance gate**

Start dev server: `npm run dev`
Navigate to `http://localhost:3000/landing`

Visual checklist against spec:
- [ ] **Blank state (before any selection):** Step 03 format grid is empty — acceptable, label still visible
- [ ] Background is `#0D1117` — no white, no gray
- [ ] Indigo pitch rectangle and arc lines visible in background
- [ ] "VANTAGE v2.0" wordmark top-left, muted color, small
- [ ] Selection card centered, solid dark background, no blur
- [ ] "STRATEGIC ALGO EXCHANGE" subtitle visible
- [ ] All 3 step labels visible (01, 02, 03)
- [ ] Men's chip selected (indigo), Women's unselected
- [ ] Category chips both unselected
- [ ] Format chips present (ODI/T20I/Test for Men's International)
- [ ] CTA button visible but disabled (opacity dimmed) before format selected
- [ ] Clicking a format chip enables CTA
- [ ] Path summary updates as steps are selected
- [ ] Changing Gender clears Category and Format selections
- [ ] Clicking "Enter Vantage →" navigates to `/?gender=mens&category=internationals&format=t20i`
- [ ] Footer text visible bottom-center
- [ ] Dashboard at `/` still loads correctly with shell

- [ ] **Step 9: Commit**

```bash
git add frontend/app/landing/layout.tsx frontend/app/landing/page.tsx frontend/app/globals.css
git commit -m "feat(landing): implement Landing Page with format selector and cricket geometry background"
```

---

## Task 4: Write workflow report

After all gates pass, write `workflow/report.md` using the Part 7 format from CLAUDE.md.
Agent: Claude. Gates F1–F4 all triggered. Mark out-of-scope files as NONE.

---

## Desktop-Required Message

The spec requires: "Below 1280px: show standard desktop-required message (reuse app-wide pattern)."
`min-width: 1280px` on `.landing-root` enforces this via horizontal scroll rather than a message.
If the main app shell implements a full-screen desktop-required overlay via a global CSS class or root-level wrapper, confirm whether that mechanism is inherited by the landing route (it will not be if it lives in the shell layout). If it is not inherited, a follow-up task must add the landing-specific overlay. This is out of scope for this plan but must not be forgotten.

---

## Acceptance Criteria

- `/landing` loads without TopBar/Sidebar/ContextBar
- SVG geometry is visible (indigo lines, not plain black canvas)
- 3-step selection works: cascading chips, reset on step change
- Orphan chip spans full width when alone in last row
- CTA disabled until all 3 steps complete
- Path summary shows progressive segments
- `router.push` fires with all 3 URL params on CTA click
- Dashboard at `/` still works — shell not broken by refactor
- F1 (lint), F2 (paradigm), F3 (type), F4 (visual) all PASS
