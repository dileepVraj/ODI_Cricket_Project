# ARCHITECT.md — Claude Full Operational Reference
**Version:** 4.0 | **Updated:** 2026-03-26
**Read by:** Claude (Architect) during session bootstrap and task execution.

---

## BOOTSTRAP SEQUENCE (Claude reads this on every session start)

**C0 — Soul**
Read `agents/souls/architect.md`. Let it ground every decision before anything else.

**C1 — State**
Read `agents/workflow/handoff.md`. This is your only source of current context.
If handoff is empty or missing — ask the human what they want to work on.

**C2 — Classify the request**
- New feature / overhaul → C2B then C3
- Bug fix / tweak / clear spec → C3 directly
- Backend task → C4 (taskFile for Codex)
- Frontend with design scope → C4D (designBrief for Gemini) then C4 (taskFile for Codex)
- Function guide → C4G (designBrief for Gemini — Gemini implements)
- Verification needed → C5
- Something broken → invoke systematic-debugging skill

**C2B — Brainstorm** (new features / overhauls only)
Invoke `core/gen_ai/skills/.system/brainstorm-intake/SKILL.md`.
Confirm spec before writing plan.

**C3 — Plan**
Read relevant source files. Write `agents/workflow/plan.md` (DRAFT).
Wait for human approval before proceeding.

**C4 — TaskFile for Codex**
Write `agents/workflow/taskFile.md` per `agents/workflow/taskFileTemplate.md`.
Include READ FIRST with exact standards paths based on task scope.
For frontend tasks: embed Stitch screen HTML (if design was approved) in the TASK PROMPT section.
Confirm with human before invoking Codex.

**C4D — DesignBrief for Gemini** (design scope or function guide with design)
Write `agents/workflow/designBrief.md`. Must include:
- Feature context and "why" (trading decision this serves)
- Exact API schema fields — extract from source, no assumptions
- Vantage design token reference (globals.css variables)
- Existing component patterns to match
- Acceptance criteria for the design
Invoke Gemini. Review design with human. On approval → extract Stitch screen HTML for C4.

**C4G — DesignBrief for Gemini** (function guide — Gemini implements)
Write `agents/workflow/designBrief.md`. Must include:
- Feature being explained and its trading significance
- API fields the guide will reference
- Existing guide structure for consistency (check `frontend/app/docs/`)
- ACs including gate requirements
Invoke Gemini. Gemini designs and implements. Proceed to C5.

**C5 — Verify**
After every CLI invocation (Codex or Gemini), run post-call validation (see below).
Then dispatch `core/gen_ai/skills/.system/verification-agent/SKILL.md`.
Pass: task ID, scope, files modified, acceptance criteria.
PASS → update `agents/workflow/handoff.md`. FAIL → fix + re-dispatch (max 3 rounds).

---

## CLI INVOCATION

**Codex (backend + frontend tasks):**
```powershell
codex exec -s danger-full-access --output-schema agents/workflow/report-schema.json -C "C:\Cricket_Project_Stable" "Read AGENTS.md. Then read agents/workflow/taskFile.md and execute the task."
```
Timeout: **1800000ms**. Always set on Bash tool call.

**Gemini (design + guide tasks):**
```bash
gemini -p "Read GEMINI.md. Then read agents/workflow/designBrief.md and execute." --yolo
```

---

## POST-CALL VALIDATION (run after every CLI invocation, in order)

**Step 1 — Did report.md change?**
```bash
stat -c "%Y %n" agents/workflow/report.md 2>/dev/null || echo "report.md missing"
```
Compare to pre-call snapshot. Unchanged or missing → SILENT FAILURE.

**Step 2 — Read and validate report.md:**
- `Agent:` matches the agent invoked
- `Status:` present — COMPLETE or BLOCKED
- Commit hash is real (not NONE) — required for COMPLETE
- `agents/workflow/taskFile.md Cleared: YES` (or designBrief for Gemini) — required for COMPLETE
- All triggered gates show PASS

**Step 3 — Cross-check git log:**
```bash
git log --oneline -3
```
Hash in report must exist in actual git log. Claims commits but git shows none → SILENT FAILURE.

**Step 4 — Implementation review:**
Read every file listed under `Files Modified:` in the report.
Review actual implementation against task acceptance criteria.

For ALL tasks:
- Does this code do what the task asked?
- Are there standards violations the gates didn't catch?

For any task touching `core/calculators/`, `core/services/`, or `formats/*/engines/` — MANDATORY Logic Trace. No exceptions:
1. You wrote the Verification Matrix when you created the taskFile. Use it — it is in your session context.
   The report.md also has a `Verification Matrix:` line confirming Codex's verification status.
2. Read the implementation. For each field in the matrix: trace the formula in the code against the concrete example you planned. Confirm the output matches.
3. If the report says `Verification Matrix: BLOCKED` → hard stop, do not proceed.
   If the report says `N/A` for a calculator/engine task → Codex skipped it. Flag it, do not accept as COMPLETE.
4. "The code looks structurally reasonable" is not verification. Tracing the formula is verification.

If implementation is wrong → flag immediately. Do NOT proceed to Step 5.

**Step 5 — Report field verification:**
All gates, ACs, hash, scope — final check before green signal.

---

## SILENT FAILURE PROTOCOL

Occurs when CLI returns but report.md was not written or not updated.

```bash
git log --oneline -5
git status --short
```

Report to human: which agent, which task, that report.md was not written, what git shows.

| Git state | Recommended action |
|---|---|
| Commits exist, no report | Re-invoke: "Work done (commit: [hash]). Write report only." |
| No commits, no report | Safe full re-invoke — repo unchanged |
| Partial commits | DO NOT re-invoke. Human must review first. |

Claude does NOT retry automatically. Human must confirm.

---

## BLOCKED PROTOCOL

When agent writes `Status: BLOCKED`:
1. Read the blocker from `Blockers Hit:` in the report
2. Can Claude resolve directly (Small Tweak Rule — ≤3 files, not registered, no gates)?
   - YES → fix it, inform human
   - NO → explain resolution path to human
3. Human relays resolution to the agent
4. Agent continues, writes new report
5. Claude re-reads and re-validates

---

## SMALL TWEAK RULE (Claude direct edits)

Claude may edit files directly when ALL true:
- ≤3 files modified
- Not engine / calculator / service layer
- Not a registered file (`core/data_access.py` `core/interfaces/team_types.py` `api/serializers.py`)
- No gate validation needed

This rule covers config tweaks, doc updates, minor bug fixes in thin layers.

---

## MULTI-PHASE SEQUENCING

Default: Backend (Codex) → Design (Gemini, if needed) → Frontend (Codex).

Exception — Frontend first, Backend second, only when ALL true:
- Frontend change is on existing, stable API (no new endpoints, no type changes)
- Backend change is independent (engine optimisation, no API contract change)
- Claude explicitly states the justification in the plan

---

## HANDOFF RULES

- Update `agents/workflow/handoff.md` only after giving green signal on a verified report.
- Max 25 lines of content.
- Must contain: what completed, what's next, any standing dirty file notices.
- This file replaces SESSION_STATE.md entirely. It is the only state that persists between sessions.
