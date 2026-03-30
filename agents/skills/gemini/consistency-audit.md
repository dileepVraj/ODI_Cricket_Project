# SKILL: consistency-audit
# Agent: Gemini
# When: Before any design brief is approved, or when Claude suspects pattern drift
# Purpose: Use Gemini's 1M context to read the entire frontend and validate a new
#          component or design decision against all existing patterns in one pass

---

## WHEN CLAUDE INVOKES THIS

Claude writes to `agents/workflow/designBrief.md` with Mode: consistency-audit.
Claude invokes: `gemini -p "Read GEMINI.md. Then read agents/workflow/designBrief.md and execute." --yolo`

---

## GEMINI EXECUTION STEPS

### Step 1 — Load full frontend context
Use `read_many_files` to read the entire frontend directory in one pass:
- `frontend/components/` (all .tsx files)
- `frontend/app/` (all page.tsx files)
- `frontend/lib/types.ts`, `frontend/lib/api.ts`, `frontend/lib/icons.ts`
- `frontend/app/globals.css`

Do not curate. Read everything. This is why you have 1M tokens.

### Step 2 — Read the new component/design
Read the specific file or design described in the designBrief.md under `Target:`.

### Step 3 — Run consistency checks
For each category below, check the new component against patterns found in Step 1:

**CSS tokens:** Does it use only CSS variables from globals.css? Any raw hex/rgba?
**Typography:** Numeric data uses `.font-data` / JetBrains Mono. UI text uses Inter. Violations?
**Color channels:**
  - `--accent-primary` = UI chrome only (active states, buttons)
  - Green (`--tier-elite`) = positive data signals only
  - Red (`--tier-danger`) = negative data signals only
  - Amber (`--tier-caution`) = data quality warnings only
  Cross-channel violations?
**Component placement:** Is it in the correct directory (`renderers/`, `layout/`, `common/`, `inputs/`)?
**SRP:** Is the file under 300 lines? If over — enumerate every function and its single responsibility.
**TypeScript:** Any `any`? API shapes in `lib/types.ts` with `@schema` JSDoc?
**Domain logic:** Any cricket arithmetic in the component? Should be in the engine.
**Existing patterns:** Does it duplicate a pattern already in `common/` or `renderers/`?

### Step 4 — Write audit report
Write to `agents/workflow/reports/consistency-audit-<component-name>.json`:
```json
{
  "audit": "consistency-audit",
  "target": "<component name>",
  "date": "YYYY-MM-DD",
  "verdict": "CLEAN | VIOLATIONS",
  "checks": {
    "css_tokens": {"status": "CLEAN", "violations": []},
    "typography": {"status": "CLEAN", "violations": []},
    "color_channels": {"status": "CLEAN", "violations": []},
    "placement": {"status": "CLEAN", "violations": []},
    "srp": {"status": "CLEAN", "line_count": 184, "violations": []},
    "typescript": {"status": "CLEAN", "violations": []},
    "domain_logic": {"status": "CLEAN", "violations": []},
    "duplication": {"status": "CLEAN", "existing_similar": []}
  },
  "summary": "<one paragraph — what was found, what was clean>"
}
```

verdict is CLEAN only if all checks are CLEAN.

---

## NOTES

- This skill exists because no other agent has the context window to read the full frontend
- Run this before any new renderer or layout component is approved by Claude
- Claude reads the JSON verdict and presents findings to human if violations exist
