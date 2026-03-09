---
name: frontend-lint-sentinel
description: Frontend compliance scanner. Detects 12 common rule violations across tsx/ts files covering raw fetch calls, type safety, CSS tokens, icon libraries, accessibility, and test framework compliance.
---

# Frontend Lint Sentinel

Auto-scans all `.tsx` and `.ts` files under `frontend/` for rule violations defined in `ENGINEERING_STANDARDS_FRONTEND.md` sections 2.2A and 2.2B.

## Mission

Catch the most common frontend violations before they reach code review. Each check maps to a numbered hard-fail rule in the standards document.

## Trigger Condition

Run this gate whenever any `.tsx` or `.ts` file under `frontend/` is modified.

## Gate Command

```powershell
python core/gen_ai/skills/validators/frontend/frontend-lint-sentinel/scripts/run_frontend_lint.py --root .
```

Pass condition: zero violations reported.

## Checks Performed

| # | Rule | Description |
|---|------|-------------|
| 1 | 2.2A-R1 | Raw `fetch()` call outside `lib/api.ts` |
| 2 | 2.2A-R6 | `: any` in type annotations (`: unknown` is exempt — idiomatic defensive typing for type guard parameters and boundary function inputs. Only `: any` is flagged.) |
| 3 | 2.2A-R7 | Hardcoded manifest function/category key strings in component files |
| 4 | 2.2A-R13 | Hardcoded format strings (`"odi"`, `"t20i"`, `"the_hundred"`) as raw literals |
| 5 | 2.2B-R1 | Raw hex colour values outside `globals.css` |
| 6 | 2.2B-R4 | Non-lucide-react icon library imports |
| 7 | 2.2B-R5 | Inline `font-family:` style declarations — CSS files are exempt: `font-family` declarations in `.css` files are correct and expected. Only flags `font-family` in `.tsx`/`.ts` component files. |
| 8 | 2.2B-R6 | `@keyframes` definitions in component files |
| 9 | 2.2C-R1 | Non-`React.lazy()` renderer imports in `FunctionRenderer.tsx` |
| 10 | 2.2D-R3 | TypeScript interfaces in `lib/types.ts` missing `@schema` JSDoc |
| 11 | 2.2E-R1 | Icon-only `<button>` elements without `aria-label` attribute |
| 12 | 2.2E-R2 | `onClick` on `<div>` or `<span>` requires `role="button"` and `tabIndex`. Hard fail: either attribute missing. |
| 13 | 2.2E-R3 | Error/result containers must have `aria-live` or `role="alert"`. Detection: `className` containing `error`, `alert`, `danger`, `result`, `output`, or `response`. Hard fail: matching container without the required attribute. |
| 14 | 2.2F-R1 | Non-Vitest test framework imports |
| 15 | 2.2A-R14 | No setInterval or setTimeout calling /execute/ endpoint |
| 16 | 2.2C-R3 | No inline object/array literals as props. Exception: `style={{}}` with runtime-computed layout values (`width`, `height`, `top`, `left`, `right`, `bottom`, `transform`) is permitted. Hard fail: `prop={{...}}` non-layout, or `prop={[...]}` |

## Output Format

Matches boundary-sentinel format:

```
PASS: zero violations
```

or on failure:

```
FAIL: N violation(s) found

[RULE 2.2A-R1] Raw fetch() outside lib/api.ts
  frontend/components/foo/Bar.tsx:42:5

[RULE 2.2B-R1] Raw hex colour outside globals.css
  frontend/components/layout/Nav.tsx:18:3
```

## Exit Contract

- `PASS` — zero violations. Gate cleared.
- `FAIL` — one or more violations. Fix all before proceeding. Do not suppress checks.
