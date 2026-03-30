# SKILL: save-design-decisions
# Agent: Gemini
# When: After any design is approved by human (after designBrief approval)
# Purpose: Persist approved design tokens, layout decisions, and UI laws to Gemini's
#          native memory so future sessions don't re-read all standards files

---

## WHEN CLAUDE INVOKES THIS

After human approves a design, Claude adds to designBrief.md:
```
Mode: save-design-decisions
Decisions to save: [list of approved decisions from this session]
```
Then invokes Gemini.

---

## GEMINI EXECUTION STEPS

### Step 1 — Read the decisions list
Read `agents/workflow/designBrief.md`. Extract the `Decisions to save:` list.

### Step 2 — Format each decision for memory
Each decision must be structured as:
- **What was decided** (the specific rule or token value)
- **Why** (the reasoning — what trading or UX need it serves)
- **Applies to** (which component types, which contexts)

Example:
```
Decision: Score Banding grid uses 4 equal-width columns with teal highlight on highest band.
Why: Equal columns allow scan comparison across bands; teal on highest draws trader eye to
     the dominant scoring zone immediately.
Applies to: All future score-range visualisation components.
```

### Step 3 — Save to Gemini memory
Use the `save_memory` tool for each decision.
Tag each memory with: `[DESIGN-DECISION]` prefix so they can be retrieved as a group.

### Step 4 — Confirm saves
Write to `agents/workflow/reports/design-decisions-saved.json`:
```json
{
  "saved": ["decision 1 summary", "decision 2 summary"],
  "date": "YYYY-MM-DD",
  "total_saved": <N>
}
```

---

## NOTES

- This eliminates the need to re-read UI_IMPLEMENTATION.md and PERF_RESILIENCE docs
  in every Gemini session — the distilled rules live in Gemini's memory
- Human must approve decisions before they are saved — Gemini does not self-decide
  what to persist
- If a previous decision is superseded by a new one, note the supersession explicitly
  in the new memory entry so Gemini knows which takes precedence
