# UI Implementation Standards
# Part of: frontendStandards
# Load for: any task creating or modifying visual components
# Critical for: renderer tasks, badge/badge-tier decisions, CSS tokens
# Source: ENGINEERING_STANDARDS_FRONTEND.md Part 2.2B (authoritative)

---

## 2.2B UI Implementation Standards

**1. CSS VARIABLE SYSTEM — Mandatory Token Usage:**
All styling for colours, spacing, radius, shadows, and transitions MUST utilize the CSS custom properties defined in `frontend/app/globals.css`. Raw hex values, hardcoded pixel values for non-intrinsic spacing, and raw `rgba()` colours that duplicate existing design tokens are strictly forbidden. UI components MUST be theme-aware by relying on these tokens.
- **Background layers:** `--bg-deepest`, `--bg-base`, `--bg-surface`, `--bg-elevated`, `--bg-hover`, `--bg-active`
- **Accent palette:** `--accent-primary` (Electric Blue), `--accent-secondary` (Purple), `--accent-tertiary` (Cyan), `--accent-glow`, `--accent-glow-strong`
- **Semantic tiers:** `--tier-elite` (green), `--tier-strong` (teal), `--tier-caution` (amber), `--tier-danger` (red)
- **Text hierarchy:** `--text-primary`, `--text-secondary`, `--text-muted`, `--text-disabled`
- **Borders:** `--border-subtle`, `--border-default`, `--border-strong`, `--border-accent`
- **Glassmorphism:** `--glass-bg`, `--glass-border`, `--glass-blur`
- **Shadows:** `--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--shadow-glow`
- **Layout dimensions:** `--sidebar-width`, `--sidebar-collapsed-width`, `--topbar-height`, `--context-bar-height`
- **Transitions:** `--transition-fast`, `--transition-normal`, `--transition-slow`
- **Border radius:** `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-xl`
- **Grounded in:** `frontend/app/globals.css` (:root block).

**Hard Fail:** Any raw hex colour (e.g., `#3B82F6`) or `rgba()` value found in a component that has an equivalent token above.

**2. NAMED UTILITY CLASSES — Use Before Inventing:**
The design system provides a set of high-level named utility classes in `globals.css` that encapsulate complex styles (glassmorphism, gradients, component primitives). These MUST be used as the primary styling mechanism before writing arbitrary Tailwind utility strings or custom CSS.
- **Available Classes:** `glass-card`, `glass-card-hover`, `gradient-text`, `gradient-text-purple`, `btn-primary`, `btn-ghost`, `badge`, `badge-elite`, `badge-strong`, `badge-caution`, `badge-danger`, `format-tab`, `sidebar-item`, `sidebar-group-label`, `context-input`, `fn-count`, `skeleton`, `animate-fade-in`, `animate-slide-in`, `animate-spin`, `animate-pulse-glow`.
- **Grounded in:** `frontend/app/globals.css` (Utility classes block).

**Hard Fail:** Reimplementing a glass card or primary button as a string of inline Tailwind classes when the named class (e.g., `.glass-card`) exists.

**3. FOUR-TIER BADGE SEMANTIC SYSTEM:**
Status and performance indicators MUST strictly adhere to the 4-tier semantic badge system. The selection of the badge class (`badge-elite`, `badge-strong`, etc.) MUST be driven by pre-computed flags from the backend. The frontend is forbidden from calculating tier thresholds.
- **Tier Mapping:**
  - `badge-elite` → Positive/Top Tier (`--tier-elite` green)
  - `badge-strong` → Good/Above Average (`--tier-strong` teal)
  - `badge-caution` → Warning/Below Average (`--tier-caution` amber)
  - `badge-danger` → Critical/Failure (`--tier-danger` red)
- **Grounded in:** `frontend/app/globals.css` and TACTICAL_EXECUTION.md Rule 5.

**Hard Fail:** Any component performing a numeric comparison (e.g., `avg > 50 ? 'badge-elite' : ...`) to decide a badge class.

**4. ICON LIBRARY — lucide-react Only:**
`lucide-react` is the silver-bullet icon library for this platform. No other icon packages (Heroicons, FontAwesome, etc.) are permitted. Icon sizing MUST be controlled via the `size` prop to ensure consistency; using CSS `width`/`height` attributes on icons is forbidden.
- **Grounded in:** Observed pattern in `page.tsx`, `FunctionRenderer.tsx`, and `FormatSelector.tsx`.

**Hard Fail:** Any import from `heroicons`, `react-icons`, `@phosphor-icons/react`, or other icon libraries.

**5. FONT SYSTEM — Two-Font Rule:**
The UI enforces a strict dual-font system. Body text, labels, and UI controls use the monospace font for a "terminal" aesthetic. Statistical and numeric data use a high-readability sans-serif font with tabular numbers to prevent horizontal shifting.
- **Body/UI:** `var(--font-text)` (Cascadia Code).
- **Numeric/Stats:** `var(--font-numeric)` (Segoe UI / Inter). Apply via `.font-numeric` class or `data-numeric="true"`.
- **Grounded in:** `frontend/app/globals.css` (:root and .font-numeric block).

**Hard Fail:** Applying `font-family` directly via inline style or arbitrary Tailwind for numeric data blocks.

**6. ANIMATION — Design System Animations Only:**
All UI animations MUST use the standardized keyframes and classes defined in the design system. Custom `@keyframes` or transition durations MUST NOT be defined within individual component files or CSS modules.
- **Entrance:** Use `animate-fade-in` or `animate-slide-in`.
- **Loading:** Use `skeleton` class for layout shimmers; use `animate-spin` on a `Loader2` icon for spinners.
- **Grounded in:** `frontend/app/globals.css` (Animations block).

**Hard Fail:** Any `@keyframes` definition found inside a `.tsx` file or a component-specific CSS file.

**7. RENDERER PATTERN — One File Per Output Type:**
To maintain SRP and scalability, every `output_type` declared in a backend manifest MUST have exactly one corresponding renderer component located in `components/renderers/`. All rendering dispatch logic MUST be centralized in `FunctionRenderer.tsx`.
- **Workflow:** Register key in manifest → Add case to `FunctionRenderer` switch → Implement file in `components/renderers/`.
- **Grounded in:** `frontend/components/renderers/FunctionRenderer.tsx` architecture.

**Hard Fail:** Rendering an `output_type` (e.g., `comparison_table`) inline within `page.tsx` or a general layout component.

**8. EMPTY AND FALLBACK STATES:**
Renderers MUST handle null, undefined, or empty data arrays gracefully. Silent failure (returning `null`) is forbidden. Components MUST utilize the `EmptyState` primitive for empty data and the `FallbackBanner` must be triggered if a specific renderer cannot be matched.
- **Requirement:** Use `<EmptyState />` for no-data scenarios.
- **Fallback:** `FunctionRenderer` MUST provide a visual fallback (e.g., raw JSON view with a warning) for unknown types.
- **Grounded in:** `frontend/components/renderers/FunctionRenderer.tsx` (Null check and fallback logic).

**Hard Fail:** Any renderer component returning an empty fragment `<></>` or `null` when its primary data prop is empty.

**9. LAYOUT COMPONENT PATTERN:**
Layout components (navigation, sidebars, headers) MUST be decoupled from domain-specific data props. They read their configuration (active format, available formats, manifest status) directly from the `useAppContext` hook.
- **Requirement:** Use `fmt.has_manifest` to control enabled/disabled states for format-selection UI.
- **Forbidden:** Passing the list of formats or the active manifest as a prop from `page.tsx` into a layout component.
- **Grounded in:** `frontend/components/layout/FormatSelector.tsx`.

**Hard Fail:** Any component in `components/layout/` receiving manifest or format data as props instead of reading from context.

**10. COMPONENT PLACEMENT — Directory Contract:**
Components MUST be placed strictly according to their architectural role. Cross-directory imports are only permitted in a "downward" direction towards `common/` or `lib/`.
- `components/layout/`: Navigation, Topbar, Sidebar, FormatSelector.
- `components/renderers/`: Output-specific data renderers and the `FunctionRenderer` dispatcher.
- `components/inputs/`: Squad Builders, Extra Input Fields, forms.
- `components/common/`: Primitives used by multiple layers (Badges, Loaders, EmptyState).
- **Grounded in:** Frontend directory structure and `FunctionRenderer.tsx` import patterns.

**Hard Fail:** A data renderer component placed in `layout/` or a layout-shell component placed in `renderers/`.

---

*Part of frontendStandards — load for tasks creating or modifying visual components.*
*Authoritative source: ENGINEERING_STANDARDS_CORE.md*
