# FRONTEND COMPLIANCE FIX PLAN
**Date:** 2026-03-07
**Source audit:** AUDIT-complianceTest.md (post-sprint compliance verification, TASK-030 to TASK-041)
**Prepared by:** Compliance review pass
**Status:** Awaiting architect sign-off before execution

---

## OVERVIEW

The post-sprint compliance review identified 8 net-new violations (NEW-01 through NEW-08),
5 unresolved original violations (from AUDIT-F10) without documented deferral, and
confirmed that one unblocked TODO item (FunctionRenderer.tsx:38) was not executed.

This plan organises all fixes into four tasks (TASK-042 through TASK-045) ordered by
priority, plus one deferred group (TASK-046) blocked on manifest schema extensions.

---

## PRIORITY CLASSIFICATION

| Priority | Condition | Action |
|----------|-----------|--------|
| P0 — Blocking | Accessibility regressions introduced in the sprint | Fix before resuming TASK-010 |
| P1 — Immediate | Unblocked TODO not executed; confirmed unresolved from audit | Fix in next frontend slot |
| P2 — Scheduled | Structural violations (line count, domain logic, raw colours) | Dedicate a frontend sprint |
| P3 — Deferred | Blocked on manifest schema slots not yet available | Park in ICEBOX with TODO |

---

## TASK-042 — Input Label Accessibility Fix
**Priority:** P0 — Blocking (regressions introduced in TASK-040)
**Scope:** Frontend
**Blocked by:** Nothing
**Estimated effort:** Small — 3 files, mechanical change

### Problem
Three components created during the TASK-040 decomposition sprint have `<label>` elements
that are not programmatically associated with their controls. Screen readers will not
announce field labels when these inputs receive focus. This is a direct accessibility
regression introduced by the sprint.

### Findings addressed
- NEW-03: `ExtraInputText.tsx:28–33` — `<label>` is a sibling of `<textarea>/<input>`, no `htmlFor`
- NEW-04: `ExtraInputSelect.tsx:72–77` — `<label>` is a sibling of `<select>`, no `htmlFor`
- NEW-05: `ExtraInputCombobox.tsx:108–113` — `<label>` is a sibling of filter `<input>` and
  `<AccessibleCombobox>`, no `htmlFor`. The filter `<input>` has `aria-label` but the
  `<label>` element is semantically orphaned.

### Fix specification

**ExtraInputText.tsx**
- Add `id` to the `<textarea>` and `<input>` elements, derived from `field.label` or a
  stable `useId()` hook value.
- Add `htmlFor={id}` to the `<label>`.
- Pattern: `const inputId = useId();` — `<label htmlFor={inputId}>` — `<input id={inputId} />`

**ExtraInputSelect.tsx**
- Same pattern: `useId()` → `id` on `<select>` → `htmlFor` on `<label>`.

**ExtraInputCombobox.tsx**
- The `<label>` should wrap or reference the filter `<input>`.
- Use `useId()` for the filter input id.
- Add `htmlFor={filterId}` to the `<label>` so it associates with the visible text filter.
- `<AccessibleCombobox>` already manages its own internal aria via `useId()`.

### Files to modify
- `frontend/components/inputs/ExtraInputText.tsx`
- `frontend/components/inputs/ExtraInputSelect.tsx`
- `frontend/components/inputs/ExtraInputCombobox.tsx`

### Acceptance criteria
- [ ] Every `<label>` in the three files has `htmlFor` pointing to an `id` on its control
- [ ] `useId()` used (not hardcoded string ids) to guarantee uniqueness on repeated renders
- [ ] No `htmlFor` targeting a non-existent `id`
- [ ] Bouncer pass

---

## TASK-043 — FunctionRenderer Type Migration (Unblocked TODO)
**Priority:** P1 — Immediate (explicitly tagged TODO TASK-038, unblocked, not executed)
**Scope:** Frontend
**Blocked by:** Nothing
**Estimated effort:** Small — 1 function move + 1 import update

### Problem
`FunctionRenderer.tsx:38–41` defines `isJsonRecordArray()` locally with a comment
`// TODO TASK-038: move to lib/types.ts narrowing`. TASK-038 is complete. The unblock
condition has passed. This function belongs in `lib/types.ts` alongside `isJsonRecord`
and all other payload narrowing utilities. Leaving it in FunctionRenderer creates a
precedent of duplicating narrowing logic across files.

### Findings addressed
- NEW-08: `FunctionRenderer.tsx:38–41` — `isJsonRecordArray` not migrated to `lib/types.ts`

### Fix specification
1. Add `isJsonRecordArray` to `lib/types.ts` as an exported function, immediately after
   or alongside `isJsonRecord` (or other closely related guards).
2. Add `@schema` JSDoc comment consistent with the existing pattern in `lib/types.ts`.
3. In `FunctionRenderer.tsx`, replace the local definition with an import from `@/lib/types`.
4. Remove the `// TODO TASK-038` comment.

### Files to modify
- `frontend/lib/types.ts` (add export)
- `frontend/components/renderers/FunctionRenderer.tsx` (remove local def, add import)

### Acceptance criteria
- [ ] `isJsonRecordArray` exported from `lib/types.ts` with `@schema` JSDoc
- [ ] `FunctionRenderer.tsx` imports `isJsonRecordArray` from `@/lib/types`
- [ ] No local definition of `isJsonRecordArray` remains in `FunctionRenderer.tsx`
- [ ] No TODO TASK-038 comment remains
- [ ] Bouncer pass

---

## TASK-044 — CategoryScreen Structural Remediation
**Priority:** P2 — Scheduled
**Scope:** Frontend
**Blocked by:** Nothing
**Estimated effort:** Medium — architectural decomposition + type migration

### Problem
`CategoryScreen.tsx` has four distinct violations, all in the same file.
They should be fixed in one pass to avoid partial states.

### Findings addressed
- NEW-06 / A4: 497 lines — exceeds 300-line limit
- A5: `buildExecuteParams()` (lines 109–145) is payload derivation logic in a component
- A6: Three inline `as` casts — lines 49, 66, 81 — on manifest API data
- NEW-01 / B1: Four `rgba()` literals — lines 349, 398, 411, 451

### Fix specification

**Part 1 — Extract execute helpers to lib/**
Create `frontend/lib/executeHelpers.ts` (or extend `lib/types.ts` with non-type exports
if the architect prefers a single lib file).

Move the following pure functions out of CategoryScreen.tsx:
- `parsePositiveInteger(value: unknown): number | null`
- `resolveSquadBuilderConfig(extraInputs: unknown): SquadBuilderConfig`
- `getExtraInputFields(extraInputs: unknown): Record<string, ExtraInputFieldConfig>`
- `getMissingContext(requiredContext, contextValues): string[]`
- `buildExecuteParams(args): Record<string, unknown>`
- `formatExecuteError(err: unknown): string`

These are pure functions with no React dependencies — they belong in lib/, not a component.
CategoryScreen.tsx imports and calls them; it does not define them.

**Part 2 — Eliminate inline `as` casts**
- `CategoryScreen.tsx:49` — `extraInputs as Record<string, unknown>`:
  Replace with a typed narrowing check (pattern already established in `lib/types.ts`
  using `isRecord`-style guards). The `isExtraInputFieldConfig` guard can be moved to
  lib/executeHelpers.ts alongside the other helpers.
- `CategoryScreen.tsx:66` — `rawSquadBuilder as Record<string, unknown>`:
  Same pattern — narrowing check before property access.
- `CategoryScreen.tsx:81` — `value as Record<string, unknown>` inside `isExtraInputFieldConfig`:
  Move the guard to lib/, use `isRecord()` from lib/types.ts as the base check.

**Part 3 — Replace rgba() with CSS tokens**
The four banner divs use raw rgba colours for caution (amber), info (blue), and danger (red).
Map to existing CSS variable equivalents:

| Current rgba | Intended semantic | Replacement token |
|---|---|---|
| `rgba(245,_158,_11,_0.08)` | Caution background | `var(--tier-caution-bg)` or `var(--bg-caution)` |
| `rgba(245,_158,_11,_0.25)` | Caution border | `var(--border-caution)` |
| `rgba(59,_130,_246,_0.08)` | Info background | `var(--bg-info)` or `var(--accent-glow)` |
| `rgba(59,_130,_246,_0.25)` | Info border | `var(--border-accent)` |
| `rgba(239,_68,_68,_0.08)` | Danger background | `var(--bg-danger)` or token equivalent |
| `rgba(239,_68,_68,_0.25)` | Danger border | `var(--border-danger)` |

NOTE: Before substituting, verify the target tokens exist in `globals.css`. If they do
not exist, add them to globals.css as new semantic tokens rather than keeping raw rgba.
Do not substitute one non-token value for another.

**Part 4 — Verify line count**
After extracting the 6 helper functions (approximately 100 lines), CategoryScreen.tsx
should be well under 300 lines. Verify before closing the task.

### Files to modify
- `frontend/components/layout/CategoryScreen.tsx` (remove helpers, remove as casts, fix rgba)
- `frontend/lib/executeHelpers.ts` (new file — pure helper functions)
- `frontend/app/globals.css` (add semantic tokens if missing)

### Acceptance criteria
- [ ] CategoryScreen.tsx is under 300 lines
- [ ] No inline `as` casts on manifest/API data in CategoryScreen.tsx
- [ ] `buildExecuteParams` and related helpers live in `lib/executeHelpers.ts`
- [ ] No `rgba()` literals in CategoryScreen.tsx — CSS tokens only
- [ ] All new tokens added to globals.css follow existing naming convention
- [ ] Bouncer pass

---

## TASK-045 — Mechanical Cleanup Pass
**Priority:** P2 — Scheduled (can run alongside TASK-044 or after)
**Scope:** Frontend
**Blocked by:** Nothing
**Estimated effort:** Small — 4 targeted, isolated fixes

### Problem
Four small violations that do not require structural decisions — each is a one-to-two
line change in a known location.

### Findings addressed
- NEW-02 / B5: `CountUp.tsx:82` — `[font-variant-numeric:tabular-nums]` should be `font-numeric`
- NEW-07 / B1: `page.tsx:203` — `[background:${color}15]` invalid CSS (CSS var + hex suffix)
- F09-V05: `CategoryScreen.tsx:477–481` — loading skeleton not announced to screen readers
- A6: `ContextBar.tsx:44` — `(field as (typeof field) & { placeholder?: unknown })` inline cast

### Fix specification

**CountUp.tsx:82**
Replace `[font-variant-numeric:tabular-nums]` with the `font-numeric` Tailwind utility class.
Verify `font-numeric` is configured in `tailwind.config.js` as a custom utility.
If not present, add it in tailwind config referencing `var(--font-numeric)`.

**page.tsx:203 (StatCard)**
The `color` prop is a CSS variable string (`"var(--accent-primary)"`).
`[background:${color}15]` produces `background: var(--accent-primary)15` — invalid CSS.
Fix: pass the color as a CSS variable name only (e.g., `"accent-primary"`) and construct
the class using a token-safe pattern, OR replace with a `style` prop using a named
CSS variable and an `opacity` token, OR introduce a `StatCard` colour variant prop that
maps to defined CSS utility classes. The simplest compliant fix is to replace the
inline interpolation with a pre-defined set of variant classes:
```
const variantClass: Record<string, string> = {
    "var(--accent-primary)": "stat-card-primary",
    ...
}
```
And define `.stat-card-primary { background: var(--accent-primary-glow); color: var(--accent-primary); }`
in globals.css. Alternatively, the architect may choose to add `--accent-primary-bg`,
`--accent-secondary-bg` etc. as explicit opacity tokens in globals.css.

**CategoryScreen.tsx loading announcement**
At line 477, the loading container wrapping `<SkeletonLoader>` has no ARIA announcement.
Add `aria-busy="true"` and `aria-label="Loading analysis..."` to the loading container div,
or add `role="status"` to `<SkeletonLoader>` itself.

**ContextBar.tsx:44**
Replace:
```tsx
const placeholder = (field as (typeof field) & { placeholder?: unknown }).placeholder;
return typeof placeholder === "string" ? placeholder : undefined;
```
With a direct narrowing check without the `as` cast:
```tsx
const raw = (field as Record<string, unknown>)["placeholder"];
```
Or preferably: extend the `ContextField` type in `lib/api.ts` (or `lib/types.ts`) to
include an optional `placeholder?: string` field, removing the need for any cast.

### Files to modify
- `frontend/components/common/CountUp.tsx`
- `frontend/app/page.tsx`
- `frontend/app/globals.css` (if new tokens added for StatCard)
- `frontend/components/layout/CategoryScreen.tsx` (loading announcement)
- `frontend/components/layout/ContextBar.tsx` (as cast removal)

### Acceptance criteria
- [ ] CountUp.tsx uses `font-numeric` class, not `[font-variant-numeric:tabular-nums]`
- [ ] `font-numeric` is resolvable (exists in tailwind.config.js or globals.css)
- [ ] StatCard background uses a valid CSS token pattern — no `${var}15` interpolation
- [ ] CategoryScreen loading container announces loading state to screen readers
- [ ] ContextBar.tsx has no `as` casts on manifest field data
- [ ] Bouncer pass

---

## TASK-046 — Manifest-Gated Deferred Items
**Priority:** P3 — Blocked (park in ICEBOX)
**Scope:** Frontend
**Blocked by:** Manifest schema extensions (team selector slot, source registry slot,
  navigation config slot) — none currently available
**Estimated effort:** Medium when unblocked

### Problem
Five violations from the original AUDIT-F10 and the compliance review remain active but
are genuinely blocked on manifest features that do not exist yet. These are not deferrable
by choice — the fix pattern requires config data that the manifest does not yet provide.
Each has a corresponding TODO comment in the code.

### Items

**F04-V03 — `"dashboard"` hardcoded as category key in page.tsx**
- `page.tsx:52, 53, 75` use `"dashboard"` as a string literal to gate routing and rendering.
- Fix requires a manifest navigation root config entry (e.g., `manifest.navigation.default_view`)
  so the key is not hardcoded in the component.
- Blocked: manifest has no navigation config slot.
- TODO comment location: none currently — add one when parking this item.

**F06-V03 — `"teams"` and `"venues"` source strings in ContextBar.tsx**
- `ContextBar.tsx:36, 49` branch on `field.source === "teams"` and `field.source === "venues"`.
- Fix requires a manifest source registry that maps source identifiers to their data
  providers, so ContextBar reads behaviour from manifest rather than matching strings.
- Blocked: manifest source registry not yet defined.
- TODO comment location: `ContextBar.tsx:71` (partial — covers team case only).

**F06-V05 — `"dashboard"` key in Sidebar.tsx `DASHBOARD_ITEM` constant**
- `Sidebar.tsx:26–31` hardcodes the dashboard navigation item including its key `"dashboard"`.
- Fix requires manifest to declare the root/home navigation entry.
- Blocked: same as F04-V03.
- TODO comment location: none — add one.

**F06-V08 (QuickLinks) — link definitions as props, not manifest**
- `QuickLinks.tsx:13` — TODO already logged, correctly blocked on manifest navigation config.
- No action required beyond confirming the TODO is in place.

**ExtraInputSelect.tsx / ExtraInputCombobox.tsx — hardcoded API path strings**
- `ExtraInputSelect.tsx:33` — `"/context/host_countries"` matched by string
- `ExtraInputCombobox.tsx:31, 35` — `"/context/players/"` and `"{team}"` matched by string
- Fix requires a manifest source registry that maps source identifiers to typed providers.
- TODO comment location: `ExtraInputSelect.tsx:67` (covers the select case).
  `ExtraInputCombobox.tsx` has no TODO — add one.

### Acceptance criteria (for when unblocked)
- [ ] Manifest declares navigation root config, team source, venue source identifiers
- [ ] `"dashboard"`, `"teams"`, `"venues"` string literals removed from all logic branches
- [ ] ExtraInputSelect and ExtraInputCombobox source resolution reads from manifest registry
- [ ] All TODO comments in the above files removed on completion
- [ ] Bouncer pass

---

## EXECUTION ORDER

```
P0 (now, before resuming TASK-010):
  TASK-042 — Input label accessibility

P1 (next frontend slot, can be a single session):
  TASK-043 — FunctionRenderer type migration

P2 (next dedicated frontend sprint):
  TASK-044 — CategoryScreen structural remediation
  TASK-045 — Mechanical cleanup pass
  (TASK-044 and TASK-045 can run in parallel — no shared files)

P3 (blocked — park):
  TASK-046 — Manifest-gated deferred items
```

---

## VIOLATIONS STATUS MATRIX

| Finding | Source | Addressed by | Status |
|---------|--------|-------------|--------|
| NEW-01 (rgba in CategoryScreen) | NEW | TASK-044 | Scheduled |
| NEW-02 (font-variant-numeric in CountUp) | NEW | TASK-045 | Scheduled |
| NEW-03 (ExtraInputText label) | NEW | TASK-042 | P0 — fix now |
| NEW-04 (ExtraInputSelect label) | NEW | TASK-042 | P0 — fix now |
| NEW-05 (ExtraInputCombobox label) | NEW | TASK-042 | P0 — fix now |
| NEW-06 (CategoryScreen 497 lines) | NEW | TASK-044 | Scheduled |
| NEW-07 (StatCard invalid CSS) | NEW | TASK-045 | Scheduled |
| NEW-08 (isJsonRecordArray not migrated) | NEW | TASK-043 | P1 — fix next |
| A4 (CategoryScreen line count) | AUDIT-F10 | TASK-044 | Scheduled |
| A5 (buildExecuteParams domain logic) | AUDIT-F10 | TASK-044 | Scheduled |
| A6 (as casts in CategoryScreen) | AUDIT-F10 | TASK-044 | Scheduled |
| A6 (as cast in ContextBar) | AUDIT-F10 | TASK-045 | Scheduled |
| B1 (rgba in CategoryScreen) | AUDIT-F10 | TASK-044 | Scheduled |
| B5 (font-variant-numeric in CountUp) | AUDIT-F10 | TASK-045 | Scheduled |
| B8 (return null — multiple) | AUDIT-F10 | Not scheduled — see note |
| F04-V03 ("dashboard" in page.tsx) | AUDIT-F10 | TASK-046 | Blocked |
| F05-V02 (FunctionRenderer unknown fallback) | AUDIT-F10 | Not scheduled — see note |
| F06-V03 ("teams"/"venues" in ContextBar) | AUDIT-F10 | TASK-046 | Blocked |
| F06-V05 ("dashboard" in Sidebar) | AUDIT-F10 | TASK-046 | Blocked |
| F09-V05 (loading not announced) | AUDIT-F10 | TASK-045 | Scheduled |

### Notes on unscheduled items

**B8 — return null in multiple files:**
`CategoryScreen.tsx:192`, `page.tsx:88`, `ExtraInputRenderer.tsx:43`, `PlayerSearch.tsx:49`,
`QuickLinks.tsx:17`. The Rule 8 standard targets "empty data" states. Some of these
(PlayerSearch when full, ExtraInputRenderer when no fields) are conditional render guards,
not empty data scenarios. The genuine empty-data nulls (CategoryScreen, page.tsx) are
loading-state gaps. Recommend the architect decide: either add EmptyState/skeleton for
the no-manifest case, or explicitly document these as "conditional render, not empty data"
exceptions. Not scheduled until architect decision.

**F05-V02 — FunctionRenderer unknown type fallback:**
The inline `<FallbackBanner>` + `<pre>` block for unrecognised output types is a known
weak point in the dispatch contract. The correct fix is to add all valid output types to
the manifest and remove the fallback entirely, or introduce a registered fallback renderer.
This is blocked on manifest output type coverage. Not scheduled — park with TASK-046.

---

*End of fix plan — 2026-03-07*
*Companion document: AUDIT-complianceTest.md*
*Tasks to create: TASK-042, TASK-043, TASK-044, TASK-045, TASK-046*
