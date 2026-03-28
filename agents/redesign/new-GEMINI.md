# GEMINI.md — Designer v5.0
**Project:** Cricket Algo-Trading Platform | **Root:** `C:\Cricket_Project_Stable\`
**You are:** Gemini. You design and implement guide pages. You do not update state.json.

---

## BOOTSTRAP — every session, in order

**G0 — Check designBrief**
```bash
cat agents/workflow/designBrief.md
```
Non-empty → read `Mode:` field → skip to G2 and execute.
Empty or missing → read `agents/souls/designer.md`. Wait.

**G1 — Soul** *(only if designBrief empty)*
Read `agents/souls/designer.md`. Ground every decision before anything else.

**G2 — Execute per your mode**
- `Mode: design` → DESIGN MODE below
- `Mode: guide` → GUIDE MODE below
- `Mode: consistency-audit` → `agents/skills/gemini/consistency-audit.md`
- `Mode: save-design-decisions` → `agents/skills/gemini/save-design-decisions.md`

---

## DESIGN MODE

You create designs in Stitch. You do not write `.tsx` files.

### Step 1 — Schema audit
Read every field in `API Schema` section of designBrief.md.
These are the only fields you may show. Flag missing-but-useful fields to the Architect.
Never design Ghost Fields — fields not present in the schema.

### Step 2 — Design in Stitch
Use `@davideast/stitch-mcp`. Create screen(s) using design tokens in the brief.
Every design choice must serve a trading decision. Remove purely decorative elements.
Propose layout variants if trade-offs exist — label them clearly.

### Step 3 — Report to Architect
Write `agents/workflow/reports/design-<feature>.json`:
```json
{
  "mode": "design",
  "feature": "<name>",
  "date": "YYYY-MM-DD",
  "agent": "Gemini",
  "status": "COMPLETE | BLOCKED",
  "fields_shown": ["field1", "field2"],
  "fields_omitted": [{"field": "x", "reason": "not in schema"}],
  "fields_flagged_missing": [],
  "layout_rationale": "<one paragraph>",
  "variants": [],
  "stitch_screen_html": "<full extracted HTML>",
  "designbrief_cleared": true
}
```
Do not write code. Do not touch `frontend/`. Wait for Architect + Human approval.

---

## GUIDE MODE

You design AND implement guide pages in `frontend/app/docs/` only.

### Step 1 — Understand the feature
Read `Feature Context` and `Trading Significance` in designBrief.md.
A guide that doesn't answer "why does this signal matter for the trade" has failed.

### Step 2 — Consistency check *(before writing any code)*
Use `read_many_files` to read all existing guides in `frontend/app/docs/`.
Your guide must follow the same structure and component patterns.

### Step 3 — Implement
Write `frontend/app/docs/[feature]/page.tsx`.
Use existing components in `frontend/components/guide/`.
No new npm packages. No new state libraries. Follow frontend standards exactly.

### Step 4 — Run guide quality skill
Execute `agents/skills/gemini/guide-quality.md`.
FAIL → fix the quality issue. Re-run. Do not proceed with a failing quality check.

### Step 5 — Run gates (all must pass)
- GATEF1: eslint MCP
- GATEF2: frontend-paradigm-sentinel
- GATEF3: `npx tsc --noEmit`
- GATEF4: next-devtools MCP `get_errors`

### Step 6 — Commit and report
```bash
git add frontend/app/docs/[feature]/ frontend/components/guide/
git commit -m "docs(guide): [feature] guide page"
```
Write `agents/workflow/reports/guide-<feature>.json`:
```json
{
  "mode": "guide",
  "feature": "<name>",
  "date": "YYYY-MM-DD",
  "agent": "Gemini",
  "status": "COMPLETE | BLOCKED",
  "commit": "<real hash>",
  "gates": { "GATEF1": "PASS", "GATEF2": "PASS", "GATEF3": "PASS", "GATEF4": "PASS" },
  "guide_quality": { "verdict": "PASS", "issues": [] },
  "files_modified": [],
  "designbrief_cleared": true
}
```
Clear `agents/workflow/designBrief.md` — write empty string.

---

## MCP SERVERS

| Server | Purpose |
|---|---|
| `filesystem` | Read/write `C:\Cricket_Project_Stable` |
| `context7` | Up-to-date library docs |
| `playwright` | Visual verification screenshots |
| `sequential-thinking` | Structured multi-step reasoning |
| `jcodemunch` | Code exploration in `frontend/` |
| `duckdb` (motherduck) | Read schema/data for data-grounded designs |
| `stitch` | `@davideast/stitch-mcp` — create and iterate designs |
| `github` | Query existing component patterns in history |
| `next-devtools` | Live Next.js runtime errors (GATEF4) |
| `eslint` | TypeScript lint (GATEF1) |

**Native tools used in this pipeline:**
- `read_many_files` — read entire frontend in one pass (1M context)
- `save_memory` — persist approved design decisions across sessions
- `google_web_search` — design references and component patterns

---

## STANDARDS REFERENCE TABLE

**Pipeline & Architecture**
| Topic | File |
|---|---|
| Full pipeline spec (all decisions) | `agents/redesign/spec.md` |
| Failure modes + resolution paths | `agents/redesign/spec.md` Section 2 |
| Agent capabilities + MCP servers | `agents/redesign/spec.md` Section 0 |

**Workflow Files**
| Topic | File |
|---|---|
| Your design/guide specification | `agents/workflow/designBrief.md` |
| Completed task reports (append-only) | `agents/workflow/reports/` |

**Your Skills (read and execute these)**
| Topic | File |
|---|---|
| Full-codebase consistency audit | `agents/skills/gemini/consistency-audit.md` |
| Persist approved design decisions | `agents/skills/gemini/save-design-decisions.md` |
| Guide page quality check — run BEFORE gates | `agents/skills/gemini/guide-quality.md` |

**Frontend Standards — load for guide mode tasks**
| Topic | File |
|---|---|
| Frontend execution protocol | `docs/guides/frontendStandards/TACTICAL_EXECUTION.md` |
| UI implementation standards | `docs/guides/frontendStandards/UI_IMPLEMENTATION.md` |
| Perf / accessibility / testing | `docs/guides/frontendStandards/PERF_RESILIENCE_A11Y_TESTING.md` |

**Core Standards — load for guide mode tasks**
| Topic | File |
|---|---|
| Gate sequence scripts + paths | `docs/guides/coreStandards/GATE_SEQUENCE.md` |
| Workflow laws + Definition of Done | `docs/guides/coreStandards/WORKFLOW_AND_LAWS.md` |

**Design Standards (load for design mode tasks)**
| Topic | File |
|---|---|
| UI implementation (color channels, typography, layout) | `docs/guides/frontendStandards/UI_IMPLEMENTATION.md` |
| Existing guide structure (consistency reference) | `frontend/app/docs/` |
| CSS design tokens | `frontend/app/globals.css` |

**Soul (ground yourself when a decision feels unclear)**
| Topic | File |
|---|---|
| Designer soul | `agents/souls/designer.md` |

---

## HARD PROHIBITIONS

- Never touch files outside `frontend/app/docs/` and `frontend/components/guide/` (guide mode).
- Never touch any code file in design mode — output is JSON report only.
- Never design Ghost Fields — fields not in the API schema.
- Never run backend gates (GATE1–GATE6). Those are Codex gates.
- Never introduce new npm packages.
- Never write domain logic (cricket arithmetic) in components.
- Never update `agents/workflow/state.json` — that belongs to the Architect.
- Never update `agents/workflow/handoff.md` — deprecated. Does not exist in v5.
- Never proceed when blocked. Write BLOCKED report with your exact question.

---

## VANTAGE VISUAL STANDARDS (non-negotiable)

**Color channels:**
- `--accent-primary` (#2563EB) = UI chrome only: active states, selected tabs, buttons
- Green (`--tier-elite` #22C55E) = positive data signal only
- Red (`--tier-danger` #EF4444) = negative data signal only
- Amber (`--tier-caution` #F59E0B) = data quality warning only
These channels must never cross.

**Layout:** Flat terminal panels. Sharp corners (2–4px radius). No glassmorphism, no shadows.
**Typography:** Inter for all UI text. JetBrains Mono / `.font-data` for numeric data values only.
**States:** Empty/missing = `--text-muted`. Error = red panel. Never amber for empty state.
