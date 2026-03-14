# Performance, Resilience, Accessibility & Testing Standards
# Part of: frontendStandards
# Load for: any frontend task (covers implementation quality gates)
# Contains: 2.2C (3 perf rules), 2.2D (3 resilience rules), 2.2E (3 a11y rules), 2.2F (4 testing rules)
# Source: ENGINEERING_STANDARDS_FRONTEND.md Parts 2.2C–2.2F (authoritative)

---

## 2.2C — Performance Standards (3 rules)

**Rule 1 — Lazy Loading Renderers**
All renderer components imported in `FunctionRenderer.tsx` MUST use `React.lazy()` with a `Suspense` fallback wrapping the switch dispatch block. Eager importing 11+ renderer components on initial load is forbidden. `Suspense` fallback MUST use the `skeleton` class from `globals.css` — not a spinner.
**Hard Fail:** any eager import of a renderer component in `FunctionRenderer.tsx`.

**Rule 2 — Memoisation Discipline**
`useMemo` and `useCallback` MUST only be used when the value is demonstrably expensive to recompute or when referential stability is required to prevent child re-renders. Wrapping every value in `useMemo` as a default is forbidden — it adds overhead without benefit in most cases.
**Required cases:** manifest-derived derived values computed in effects, callback props passed to memoised child components.
**Hard Fail:** `useMemo` or `useCallback` wrapping primitive values or simple variable lookups.

**Rule 3 — No Inline Object/Array Props**
Inline object literals and array literals passed as props (e.g. `style={{}}` or `value={[]}`) create new references on every render and cause unnecessary child re-renders. These MUST be extracted to constants outside the component or wrapped in `useMemo`.
**Exception:** the existing inline `style={{}}` exemption from Rule 2 (runtime-computed progress bar widths) applies here too.
**Hard Fail:** any object or array literal passed as a prop that is not runtime-computed.

---

## 2.2D — Resilience Standards (3 rules)

**Rule 1 — Error Boundaries — Renderer Isolation**
Every output rendered by `FunctionRenderer` MUST be wrapped in a React Error Boundary. A single renderer throwing MUST NOT crash `CategoryScreen` or the entire page. Error Boundary MUST display a recoverable error state using `badge-danger` and `btn-ghost` retry — never a blank screen. Place Error Boundary component in `components/common/`.
**Hard Fail:** any renderer output not wrapped in an Error Boundary.

**Rule 2 — Error Boundary Placement Rule**
Error Boundaries MUST be placed at the renderer dispatch level — wrapping `FunctionRenderer` output in `CategoryScreen` — not inside individual renderer components. Individual renderers MUST throw on bad data — they MUST NOT catch their own errors silently.
**Hard Fail:** `try/catch` inside a renderer component swallowing a render error.

**Rule 3 — Backend Type Sync Contract**
Every TypeScript type in `frontend/lib/types.ts` that maps to a backend Pydantic schema MUST include a JSDoc comment in this exact format:
`/** @schema {PydanticClassName} in {python_file_path} */`
Silent drift between backend output shape and frontend type is a Hard Fail on any API response change task. When a backend schema changes, the corresponding frontend type MUST be updated in the same task — not deferred.
**Hard Fail:** any type in `lib/types.ts` mapping to a backend schema without the `@schema` JSDoc comment.

---

## 2.2E — Accessibility Standards (3 rules)

**Rule 1 — Interactive Element Labels**
Every interactive element that does not contain visible text MUST have an `aria-label` or `aria-labelledby` attribute. This includes icon-only buttons, format tabs with only an emoji label, and sidebar items that collapse to icon-only on narrow viewports.
**Hard Fail:** any `<button>` or `<a>` element containing only an icon with no `aria-label`.

**Rule 2 — Keyboard Navigation**
All interactive elements MUST be reachable and operable via keyboard. Tab order MUST follow visual reading order. `Execute` button, format tabs, function tabs, and sidebar items MUST be focusable and respond to `Enter`/`Space`.
**Hard Fail:** any `onClick` handler on a non-interactive element (`div`, `span`) without a corresponding `onKeyDown` handler and `role="button"` with `tabIndex={0}`.

**Rule 3 — Loading and Error State Announcements**
Loading states and error states MUST be announced to screen readers via `aria-live="polite"` regions. The execute result container MUST have `aria-live="polite"` so result arrival is announced without interrupting the user. Error messages MUST have `role="alert"` so they are announced immediately.
**Hard Fail:** any error display or result container without the correct `aria-live` or `role` attribute.

---

## 2.2F — Testing Standards (4 rules)

**Rule 1 — Testing Stack**
Frontend tests MUST use Vitest as the test runner and React Testing Library for component tests. No other testing framework may be introduced. Test files MUST be colocated with components using the pattern: `ComponentName.test.tsx`.
**Hard Fail:** any `Jest`, `Mocha`, `Enzyme`, or other testing framework import in test files.

**Rule 2 — What Must Be Tested**
The following MUST have test coverage:
- `FunctionRenderer`: one test per `output_type` verifying correct renderer is mounted
- `lib/api.ts`: all error code paths (422, 5xx, network failure)
- `lib/context.tsx`: format switching clears `contextValues`, manifest load sets `years` default correctly
- Type guard functions: all branches of `isExtraInputFieldConfig()`, `resolveSquadBuilderConfig()`, `extractEnrichedData()`
**Hard Fail:** a new renderer added without a corresponding `FunctionRenderer` routing test.

**Rule 3 — What Must Not Be Tested**
Do not write tests for:
- CSS class names or visual styling
- Tailwind class presence
- Internal implementation details of hooks
- Third-party library behaviour
Tests assert behaviour and output — not implementation.

**Rule 4 — Test Data — No Hardcoded Format Keys**
Test fixtures MUST NOT hardcode format keys like `"odi"` as magic strings. Use a `TEST_FORMAT` constant defined once at the top of the test file.
**Hard Fail:** `"odi"` or any format key as a raw string literal inside a test assertion or mock payload.

---

*Part of frontendStandards — load for every frontend task.*
*Authoritative source: ENGINEERING_STANDARDS_CORE.md*
