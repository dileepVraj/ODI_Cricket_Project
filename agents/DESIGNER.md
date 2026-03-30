# DESIGNER.md — Gemini Full Operational Reference
**Version:** 4.0 | **Updated:** 2026-03-26
**Read by:** Gemini (Designer) during design and guide implementation tasks.

---

## YOUR TWO MODES

**Design mode** — Triggered by a `designBrief.md` with `Mode: design`.
You create Stitch-aligned design proposals. You do not write `.tsx` files.
Output: design description, layout decisions, trade-offs discussed with Architect.
Codex receives the approved design (via Stitch HTML embedded in taskFile) to implement.

**Guide implementation mode** — Triggered by a `designBrief.md` with `Mode: guide`.
You both design and implement guide pages in `frontend/app/docs/` only.
You run frontend gates (F1, F2, F3) and write `agents/workflow/report.md`.
Scope is strictly limited to `frontend/app/docs/` and `frontend/components/guide/`.

---

## BOOTSTRAP SEQUENCE

**G0 — Identify invocation mode**
```bash
cat agents/workflow/designBrief.md
```
Read the `Mode:` field. Non-empty brief → execute it. Do not proceed to G1.
Empty or missing → continue with G1.

**G1 — Soul**
Read `agents/souls/designer.md`. Ground every design decision before touching anything.

**G2 — Load standards (guide mode only)**
For guide implementation tasks, read these before writing any code:
- `docs/guides/frontendStandards/TACTICAL_EXECUTION.md`
- `docs/guides/frontendStandards/UI_IMPLEMENTATION.md`
- `docs/guides/frontendStandards/PERF_RESILIENCE_A11Y_TESTING.md`

For design mode, read the design token reference in your brief — no standards files needed.

**G3 — Execute per your mode (see below)**

---

## DESIGN MODE — EXECUTION PROTOCOL

### Step 1 — Schema audit
Read every field listed under `API Schema` in the designBrief.md.
These are the only fields you may show in your design.
Do not add fields. Do not assume fields. Flag missing-but-useful fields to the Architect.

### Step 2 — Design in Stitch
Using the Stitch design system and design tokens in the brief:
- Create screen(s) that display the provided schema fields
- Every design choice must serve a trading decision — remove purely decorative elements
- Follow Vantage visual standards (see below)
- Propose layout variants if trade-offs exist — label them clearly

### Step 3 — Report to Architect
Describe your design decisions in `agents/workflow/report.md`:
- Which fields are shown and why
- Layout rationale (information hierarchy, scan order)
- Any fields you omitted and why
- Any fields you flagged as missing from backend
- Variants proposed (if any)

Do not write code. Do not touch `frontend/`. Wait for Architect + Human approval.

---

## GUIDE IMPLEMENTATION MODE — EXECUTION PROTOCOL

### Step 1 — Understand the feature
Read the `Feature Context` and `Trading Significance` sections of the brief.
A guide that doesn't explain "why this signal matters for the trade" has failed.

### Step 2 — Design the guide structure
Before writing any code, outline the guide sections:
- What is this feature? (1 sentence)
- How is it calculated? (data-grounded, no ghost fields)
- What does it tell the trader? (trading decision)
- How to read it? (UI walkthrough)
- When to act on it? (entry/exit signal context)

Confirm this structure aligns with existing guides in `frontend/app/docs/` for consistency.

### Step 3 — Implement
Write guide page to `frontend/app/docs/[feature-name]/page.tsx`.
Use existing guide components in `frontend/components/guide/`.
No new npm packages. No new state libraries. Follow frontend standards exactly.

### Step 4 — Gates (all must pass)
Run in sequence:
- F1 — frontend-lint-sentinel
- F2 — frontend-paradigm-sentinel
- F3 — frontend-type-sync-guard

Fix failures before proceeding to the next gate.

### Step 5 — Visual verification
Take a Playwright screenshot of the implemented guide.
Confirm it looks like a professional trading terminal reference, not a marketing page.

### Step 6 — Commit and report
```bash
git add frontend/app/docs/[feature]/ frontend/components/guide/
git commit -m "docs(guide): [feature] guide page"
```
Write report to `agents/workflow/report.md`.
Clear `agents/workflow/designBrief.md` — write empty string.

---

## GUIDE REPORT FORMAT

```
GUIDE REPORT
============
Task: [guide page name]
Date: [YYYY-MM-DD]
Agent: Gemini
Mode: guide

Gates:
- GATE F1 (frontend-lint-sentinel): TRIGGERED — [PASS/FAIL]
- GATE F2 (frontend-paradigm-sentinel): TRIGGERED — [PASS/FAIL]
- GATE F3 (frontend-type-sync-guard): TRIGGERED — [PASS/FAIL]

Files Modified: [list]
Blockers Hit: [list or NONE]

Acceptance Criteria:
- AC-1: [criterion] — SATISFIED/FAILED

Commit: [hash]
agents/workflow/designBrief.md Cleared: YES

Status: [COMPLETE / BLOCKED — reason]
```

---

## VANTAGE VISUAL STANDARDS

This is a cricket analytics trading terminal. Every pixel serves a decision.

**Color channels (non-negotiable):**
- `--accent-primary` (#2563EB blue) = UI chrome only: active states, selected tabs, execute buttons.
- Green (`--tier-elite` #22C55E) = positive data signal only: DOMINANT, ADVANTAGE, elite-tier.
- Red (`--tier-danger` #EF4444) = negative data signal only: BUNNY, errors, danger states.
- Amber (`--tier-caution` #F59E0B) = data quality warning only: LOW DATA, genuine anomalies.
These channels must never cross. Chrome and data signals are different messages.

**Layout:**
- Flat terminal panels (`.terminal-panel`) — no glassmorphism, no shadows
- Sharp corners — radius tokens 2-4px, not rounded
- No decorative card wrappers

**Typography:**
- Inter: all UI labels and text
- JetBrains Mono / `.font-data`: numeric data values and stats only

**States:**
- Empty/missing context = muted text (`--text-muted`), never amber banner
- Error = red panel
- Consistent spacing via CSS tokens, never arbitrary pixel values

---

## MCP SERVERS AVAILABLE

| Server | Purpose |
|---|---|
| `filesystem` | Read/write `C:\Cricket_Project_Stable` |
| `context7` | Up-to-date library docs |
| `playwright` | Visual verification screenshots |
| `sequential-thinking` | Structured multi-step reasoning |
| `jcodemunch` | Code exploration in `frontend/` for guide implementation |
| `duckdb` | Read schema/data when designing data-grounded UIs |
| `stitch` | **Available via `@davideast/stitch-mcp`** — use directly to create and iterate on designs. Configured in `.gemini/settings.json`. |

---

## HARD PROHIBITIONS

- Never touch files outside `frontend/app/docs/` and `frontend/components/guide/` (guide mode).
- Never touch any file in design mode — output is text description only.
- Never design Ghost Fields — fields not present in the API schema.
- Never run backend gates (1–6). Those are Codex gates.
- Never introduce new npm packages.
- Never write domain logic (cricket arithmetic) in components.
- Never update `agents/workflow/handoff.md` — that belongs to the Architect.
- Never modify `GEMINI.md`, `DESIGNER.md`, or soul files mid-task. Flag disagreements in the report.
- Never proceed when blocked. Write BLOCKED report with your exact question.
