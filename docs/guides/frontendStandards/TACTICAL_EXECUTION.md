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
All styling MUST be implemented using Tailwind CSS utility classes. The use of React inline `style={{}}` attributes is forbidden except for values that are computed at runtime (e.g., dynamic chart coordinates or progress bar widths). Use of arbitrary value syntax (e.g., `[padding:24px]`) is permitted and encouraged for high-precision layouts to avoid custom CSS bloat.

**3. Global App State Purity:**
The application MUST use React Context (`useAppContext()` from `lib/context.tsx`) as the exclusive mechanism for global state. Introduction of external state management libraries (Redux, Zustand, MobX, Jotai) is forbidden unless explicitly approved by the architect. Local Component State (`useState`) is permitted ONLY for concerns that are strictly local to the UI (e.g., `activeTab`, `isExpanded`, `isLoading`).

**4. Component Modularity & SRP:**
Individual React components MUST NOT exceed a 300-line limit. If a component exceeds this threshold, it MUST be decomposed into focused sub-components. Follow the "Describe without and" test: if you cannot describe a component's responsibility without using the word "and", it violates the Single Responsibility Principle. Components MUST be placed in the appropriate `components/` subdirectory based on their role (`layout/`, `renderers/`, `inputs/`).

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

**9. Hash-Based Navigation Pattern:**
Switching between analysis categories MUST be handled via hash-based deep linking using `window.history.replaceState()`. This allows users to bookmark specific analysis screens without polluting the browser's back-stack or triggering full page reloads. Avoid using Next.js `router.push()` for internal view transitions that do not change the base page.
**Alignment:** URL state management and context sync pattern — bidirectional sync with window.history.replaceState() as established in frontend/lib/context.tsx. No back-stack pollution.

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
