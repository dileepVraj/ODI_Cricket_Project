---
name: systematic-debugging
description: Root-cause-first debugging process for unexpected errors, test failures, and broken behaviour in the Cricket platform. Invoked inline by Claude when something breaks during implementation or in production. No fixes before root cause is confirmed.
---

# Systematic Debugging

**Iron Law: no fix attempt before root cause is confirmed.**

Guessing wastes tokens and creates new bugs. Every fix attempt without evidence is a gamble. This process takes 10 minutes and saves hours.

## When to Invoke

- Unexpected error during implementation
- A gate fails that was passing before
- The browser shows wrong output after a change
- An API returns unexpected data
- A bouncer violation appears that wasn't there before
- "It was working and now it isn't"

---

## Phase 1 — Establish What Changed

Before reading any error message, answer this:

**What is the last change that could have caused this?**

```bash
git log --oneline -5
git diff HEAD~1 --stat
```

If the failure appeared after a specific commit — that commit is suspect until proven innocent. Read its diff before anything else.

If the failure appeared without any recent change — the environment changed (dependency update, data change, dev server restart). Note this.

---

## Phase 2 — Read the Error, All of It

Do not skim. Read the full error output including:
- The exception type and message
- The full stack trace (file path + line number)
- Any preceding warnings that were being ignored

Common mistakes:
- Reading only the last line of a Python traceback (the symptom) instead of the first `File "..."` line (the source)
- Ignoring `Warning:` lines in frontend console output that precede the error
- Missing the "caused by" chain in nested exceptions

Write down: **the exact file and line where the failure originates**, not where it surfaces.

---

## Phase 3 — Gather Evidence (don't guess yet)

Run targeted diagnostics based on what broke.

### Frontend broke (visual or runtime)

```bash
# Check what CSS is actually compiled and served
# Open browser devtools: Elements → Computed styles on the broken element
# Check which class names are on the element vs what's in globals.css
```

Use Playwright to inspect the live DOM:
```js
// Check computed styles
window.getComputedStyle(document.querySelector('.target-class')).display

// Check if CSS rule exists in loaded stylesheets
Array.from(document.styleSheets)
  .flatMap(s => { try { return Array.from(s.cssRules) } catch { return [] } })
  .filter(r => r.selectorText?.includes('target-class'))
```

If compiled CSS is missing a class that exists in globals.css → Turbopack stale cache. Make a real content edit to globals.css to trigger recompile.

### Gate failed

Read the gate's exact output — every line. Gates output `file:line:col` references. Go to that exact location.

```bash
# F1 — lint violations
python core/gen_ai/skills/validators/frontend/frontend-lint-sentinel/scripts/run_frontend_lint.py --root .

# F2 — paradigm violations
python core/gen_ai/skills/validators/frontend/frontend-paradigm-sentinel/scripts/run_frontend_paradigm.py --root .

# Bouncer
python core/utils/compliance_bouncer.py --root .
```

Do not touch code until you have read the `file:line` the gate reported.

### API returned wrong data

```bash
# Hit the endpoint directly
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"function": "...", "params": {...}}'
```

Trace backwards through the stack:
1. What did the API return? (raw JSON)
2. What did the serializer emit? (read `api/serializers.py`)
3. What did the engine return? (add a `print()` or check the engine method directly)
4. What data did the calculator produce? (check the intermediate DataFrame)

### Backend computation wrong

```python
# Use DuckDB MCP or a scratch script to query the raw data
# Verify the DataFrame at the point of failure
import duckdb
conn = duckdb.connect("formats/odi/data/odi.duckdb")
df = conn.execute("SELECT ... FROM balls WHERE ...").df()
print(df.head())
print(df.dtypes)
print(df.shape)
```

Verify assumptions:
- Does the column you're filtering on actually exist? (`df.columns`)
- Are the values the type you expect? (`df.dtypes`)
- Is the DataFrame empty at the point of filtering? (`df.empty`)

---

## Phase 4 — State the Root Cause

Before writing any fix, complete this sentence out loud:

> "The root cause is **[specific thing]** at **[file:line]** because **[reason]**."

If you cannot complete that sentence specifically — you do not have root cause yet. Return to Phase 3.

Vague root causes that are not ready:
- "Something is wrong with the CSS" — not ready
- "The gate is failing" — not ready
- "The API is returning bad data" — not ready

Ready root causes:
- "The `.landing-root` CSS class is not in the compiled stylesheet because Turbopack cached the pre-landing version of globals.css" — ready
- "The bouncer is failing because `_matchup_single_batter` at line 733 uses `Any` in its return type annotation" — ready
- "The F2 gate fails because `MatchupCard.tsx` line 84 does `threat_rating === 'ELITE'` which is domain arithmetic in a component" — ready

---

## Phase 5 — Fix and Verify

1. Make the smallest possible change that addresses the root cause.
2. Re-run whatever failed (gate, test, visual check) immediately after.
3. If it still fails — this was not the root cause. Return to Phase 3 with the new evidence. Do not layer a second fix on top.
4. If after 3 distinct fix attempts the issue persists — stop. Present the evidence to the human. Do not loop.

---

## Platform-Specific Notes

**Turbopack / CSS not updating**
Turbopack on Windows can serve stale CSS. If a CSS class exists in `globals.css` but is missing from the compiled stylesheet, make a real content edit to `globals.css` (add/change a comment or value) to force a recompile. A whitespace-only change may not trigger it.

**DuckDB locked**
If DuckDB throws a lock error, another process is holding the connection. Check for a running dev server or notebook that opened the database. Restart it.

**Bouncer reports pre-existing violations**
Run `git stash` and re-run the bouncer. If the violation exists on the stashed state, it is pre-existing and not caused by your change. Document it in the report as pre-existing. Do not fix violations outside your task scope.

**TypeScript error in unrelated file**
If `tsc` reports an error in a file you did not touch, check whether your change modified a type that file imports. The error is yours — trace the import chain.
