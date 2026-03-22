# Button Loading State — Design Spec
# Date: 2026-03-22
# Status: APPROVED

---

## Summary

Add `isLoading` and `loadingLabel` props to the existing `Button` primitive
(`frontend/components/common/Button.tsx`) to support the loading pattern
defined in the Frontend Overhaul Plan (Section 11).

---

## New Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `isLoading` | `boolean` | `false` | When true, replaces children with spinner + label and disables the button |
| `loadingLabel` | `string` | `"Analysing..."` | Text shown alongside spinner during loading state |

---

## Behaviour

### When `isLoading={true}`
- Button is set to `disabled` — prevents double-submit
- Children replaced with: inline SVG spinner + `loadingLabel` text
- Spinner: 14x14px SVG arc, `animate-spin`, inherits text color
- Gap between spinner and label handled by existing `gap: 8px` on `.btn-*` classes
- Disabled styling (opacity 0.5, cursor not-allowed) applied via existing CSS

### When `isLoading={false}` (default)
- Zero change to rendered output — fully backwards compatible

---

## Scope

- **File modified:** `frontend/components/common/Button.tsx` only
- **No CSS changes** — existing `.btn-*:disabled` rules handle the visual state
- **No new dependencies** — spinner uses inline SVG + Tailwind `animate-spin`
- **Variant-agnostic** — works identically across primary, ghost, and danger variants

---

## What Does Not Change

- `globals.css` — untouched
- All existing `<Button>` usage — backwards compatible (new props are optional)
- Component interface — existing props unchanged

---

## Plan Reference

Frontend Overhaul Plan Section 11 (Loading Strategy):
> "Button shows inline spinner + 'Analysing...' text, button is disabled during the request"
