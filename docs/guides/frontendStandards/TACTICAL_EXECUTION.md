# Tactical Frontend Execution Rules
# Part of: frontendStandards
# Load for: any frontend task (component creation, modification, bug fix)
# Source: ENGINEERING_STANDARDS_FRONTEND.md Part 2.2A (authoritative)

---

## 2.2A Tactical Frontend Execution Rules

Every rule in this section is a hard constraint.

**1. The API Wrapper Mandate:**
All communication with the backend MUST flow through the standardized wrappers in `frontend/lib/api.ts` (e.g., `executeFunction()`). Direct use of the raw `fetch()` API or third-party libraries (Axios, etc.) inside React components is strictly forbidden. This ensures centralized handling of origin prefixes, headers, and error parsing.
**Hard Fail:** Any `fetch()` call found outside `lib/api.ts`.

**2. Strict Tailwind CSS:**
All styling MUST be implemented using standard Tailwind CSS utility classes referencing design tokens from `globals.css`. The use of React inline `style={{}}` attributes is forbidden except for values that are computed at runtime (e.g., dynamic chart coordinates or progress bar widths). Use of arbitrary value syntax (e.g., `[padding:24px]`, `[display:flex]`, `[color:#6366F1]`) is strictly forbidden — it bypasses the token system, produces unreadable code, and defeats the purpose of Tailwind. Use named CSS custom properties (`var(--token-name)`) via the token system instead.
**Hard Fail:** Any arbitrary Tailwind value syntax `[property:value]` found in any `.tsx` or `.ts` file.

**3. Global App State Purity:**
The application uses two approved mechanisms for global state:
- **URL Search Params** — REQUIRED for all filter/context values (Home Team, Away Team, Venue, Innings, Match Count). These MUST live in the URL so they persist across page navigation, support deep linking, and survive refresh. Use Next.js `useSearchParams()` and `router.replace()` to read and write these values.
- **React Context (`useAppContext()`)** — REQUIRED for app-level state that is NOT filter data: manifest data, available formats, active format, teams list, venues list, loading states.
Introduction of external state management libraries (Redux, Zustand, MobX, Jotai) is forbidden unless explicitly approved by the architect. Local Component State (`useState`) is permitted ONLY for concerns that are strictly local to the UI (e.g., `activeTab`, `isExpanded`, `isLoading`).
**Hard Fail:** Any filter/context value (team, venue, innings, match count) stored in React Context instead of URL search params.

**4. Component Modularity & SRP:**
The Single Responsibility Principle is the primary law. The 300-line limit is a signal that triggers mandatory SRP analysis — it is not the goal. A 290-line file that does two things is a violation. A 310-line file with one clear responsibility must still be analysed, not merely truncated.

When a file breaches 300 lines or fails the responsibility test, the agent MUST perform a full structural deconstruction:

- **Logical Decoupling:** Identify every distinct responsibility the file holds (state management, data transformation, UI rendering, execution orchestration, etc.). Each responsibility that can stand alone becomes a candidate for extraction into a dedicated file.
- **Cohesion Audit:** For each extracted module, verify it handles exactly one part of the pipeline. If a module cannot be described without the word "and", it has not been split correctly.
- **Interface Design:** Define clean prop boundaries between the orchestrator and its sub-components. Props must be explicit — no implicit coupling through shared mutable state or context side-effects.
- **Describe Without "And" Test:** If you cannot describe a component's responsibility in one sentence without using "and", it violates SRP. This test applies to every file before and after the split.

Merely moving lines into a new file to stay under 300 is a Hard Fail. The result must be structurally cleaner, not just numerically smaller.

Components MUST be placed in the appropriate `components/` subdirectory based on their role (`layout/`, `renderers/`, `inputs/`, `common/`).

**5. No Domain Logic (Pre-Computed Payload Mandate):**
React components MUST remain "Visual-Deaf." They are forbidden from performing cricket domain logic, statistical formulas, or deriving UI states from raw numbers. No `val.match()` for string parsing, no `if (n < 3)` for sample size checks, and no badge colour derivation. All such decisions MUST be pre-computed by the Python backend and delivered as explicit flags or tagged primitives.
**Hard Stop:** Any React component performing arithmetic or statistical comparison on API response data to generate UI tokens is a Hard Fail.

**6. TypeScript Strict Mode:**
All frontend code MUST be written in strict TypeScript. The use of `any` or `unknown` as a final type for domain data is forbidden. All API response shapes MUST be defined as interfaces in `lib/api.ts` or `lib/types.ts`. Favor type guards (e.g., `isExtraInputFieldConfig`) or dedicated parser functions (e.g., `parsePositiveInteger`) over inline `as` casts to maintain type safety.

**7. Manifest-Driven Rendering:**
The UI MUST be a dynamic reflection of the backend manifest. Hardcoding function keys, category keys, or output type names in React components is forbidden. If a feature or category is not declared in the active format's manifest, it MUST NOT be rendered. The UI acts as a generic dispatcher for manifest-registered capabilities.
**Hard Stop:** Any React component that hardcodes a specific function key (e.g., `venue_intel`) to trigger a unique layout not defined by the manifest-contract is a Hard Fail.

**8. Standardized Error Handling:**
Every call to `executeFunction()` MUST be wrapped in a `try/catch` block. Errors MUST be processed by a dedicated formatter (e.g., `formatExecuteError`) to provide user-friendly feedback. React components are forbidden from rendering raw `err.message` or technical stack traces from the backend.

**9. Page-Based Navigation Pattern:**
The application uses Next.js App Router with nested layouts for all navigation. Each analysis module is a dedicated route (e.g., `/phase-analysis`, `/venue-intel`, `/player/[id]`). Navigation MUST use Next.js `router.push()` or `<Link>` components — never `window.history.replaceState()` or hash-based navigation.
- The persistent shell (TopBar, Sidebar, ContextBar) lives in `app/layout.tsx` and never unmounts
- Each module is a `page.tsx` under its own route folder
- Filter state (team, venue, innings) travels with navigation via URL search params — `router.push('/phase-analysis?home=India&away=Australia&venue=MCG')`
- Sidebar `onCategorySelect` calls `router.push()` to the module route, not a state setter
**Hard Fail:** Any `window.history.replaceState()`, `window.location.hash`, or hash-based navigation pattern in any component file.

**10. Async Effect Cancellation:**
Every `useEffect` hook performing asynchronous operations (API calls) MUST implement a cancellation guard (e.g., `let cancelled = false`). The cleanup function MUST set this guard to `true`. Every state setter within the async path MUST check the guard before execution to prevent memory leaks and race conditions on unmounted components.

**11. Manifest-Driven Input Rendering:**
Optional UI elements like the `SquadBuilder` or `ExtraInputRenderer` MUST be rendered conditionally based on the active function's `extra_inputs` definition in the manifest. Configuration for these builders (e.g., `maxPlayers`) MUST be resolved via dedicated helper functions (e.g., `resolveSquadBuilderConfig`) rather than hardcoded defaults in the UI layer.

**12. Execute Parameter Construction:**
Gathering parameters for an API call MUST be handled by a dedicated builder function (e.g., `buildExecuteParams`). Constructing large parameter dictionaries inline inside event handlers or `useEffect` hooks is forbidden as it obscures the data contract and complicates testing.

**13. Format String Agnosticism:**
React components MUST NOT contain hardcoded format strings (e.g., `"odi"`, `"t20i"`). All format-specific context MUST be derived from the `activeFormat` and `manifest` provided by `useAppContext()`. UI labels, icons, and rules MUST flow from the manifest rather than local constants.

**14. No Polling on Execute Endpoints:**
Implementing live updates by calling standard analytical endpoints (e.g., `/execute/`) on a timer (`setInterval`/`setTimeout`) is a violation of the system architecture. Historical analysis endpoints are high-latency and not orchestrated for live state.
**Hard Stop:** Any `setInterval` or `setTimeout` implementation found calling the `/execute/` endpoint is a Critical Architecture Violation.

**15. No Unapproved State Libraries:**
The use of `useAppContext()` and the established `lib/context.tsx` pattern is the non-negotiable standard for global state. Introduction of any new state management library (Zustand, Redux, etc.) is strictly forbidden without explicit written approval from the Human Architect and a corresponding version increment in `ENGINEERING_STANDARDS_CORE.md`.
**Alignment:** Mandate 4 SRP (one state mechanism, one reason to change) + Paradigm 3 (no tight coupling to specific libraries)

---

*Part of frontendStandards — load for every frontend task.*
*Authoritative source: ENGINEERING_STANDARDS_CORE.md*
