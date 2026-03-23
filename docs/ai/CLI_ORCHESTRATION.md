# CLI_ORCHESTRATION.md — Claude CLI Protocol
**Applies to:** Backend tasks only. Claude invokes Codex via PowerShell CLI.
**Frontend tasks are executed directly by Claude — no CLI invocation needed.**

---

## CLI Command

```powershell
codex exec --full-auto -C "C:\Cricket_Project_Stable" "Read CLAUDE.md. Then read workflow/taskFile.md and execute the backend task."
```

Timeout: **1800000ms (30 minutes)**. Default 2-minute timeout will kill the agent mid-task.

The `Orchestration` field in taskFile.md tells Codex whether this is SOLO or MULTI-PHASE-A.

---

## Pre-Call Snapshot (MANDATORY before every CLI invocation)

```bash
stat -c "%Y %n" workflow/report.md 2>/dev/null || echo "report.md does not exist"
```

Store this timestamp. It is the baseline for post-call validation.

---

## Post-Call Report Validation (MANDATORY after every CLI invocation)

**Step 1 — Did report.md change?**
```bash
stat -c "%Y %n" workflow/report.md 2>/dev/null || echo "report.md missing"
```
Compare to pre-call snapshot.
- Unchanged or missing → SILENT FAILURE (see below)
- Changed → proceed to Step 2

**Step 2 — Read and validate report.md content:**
```bash
cat workflow/report.md
```
Check:
- `Agent:` field matches the agent invoked
- `Status:` is present (COMPLETE or BLOCKED)
- Both commit hashes are real (not NONE) — required for COMPLETE
- `workflow/taskFile.md Cleared: YES` — required for COMPLETE

**Step 3 — Cross-check git log:**
```bash
git log --oneline -3
```
If report claims commits exist but git log shows none since pre-call → SILENT FAILURE.

---

## After Post-Call Validation

0. Dispatch `verification-agent` first (always — before acting on the report):
   Skill: `core/gen_ai/skills/.system/verification-agent/SKILL.md`
   Pass: task ID, scope=backend, files from report.md, acceptance criteria.
   PASS → proceed. FAIL → flag exact failures. Do not proceed.

1. All gates PASS + real commit hashes + taskFile cleared + no scope violations → PASS
2. Any gate FAIL or constraint violation → FAILED — inform human with exact details
3. Status: BLOCKED → read blocker, diagnose, inform human (see Unblock below)
4. Silent failure detected → Silent Failure Protocol (see below)

---

## Unblock Protocol

If Codex writes `Status: BLOCKED`:
- Claude reads the blocker question
- Claude resolves directly (Small Tweak Rule) OR explains resolution to human
- Human relays resolution to Codex for continuation
- Claude does NOT re-invoke CLI until blocker is resolved and human confirms

---

## Silent Failure Protocol

A silent failure occurs when CLI returns but report.md was not written or not updated.

**Step 1 — Establish what happened:**
```bash
git log --oneline -5
git status --short api/   # or relevant directory
```

**Step 2 — Inform human:**
- Which agent was invoked and what task
- That report.md was not written (silent failure)
- What git log shows (commits made or not)
- Recommended action (see below)

**Step 3 — Recommended actions based on git log:**
- Commits exist, no report → agent completed work but drifted on reporting.
  Re-invoke with: "The task work is done (commit: [hash]). Write the report to workflow/report.md only. Do not redo the implementation."
- No commits, no report → agent failed before any changes. Safe to re-invoke normally.
- Partial commits → do NOT re-invoke. Human must review before deciding.

Claude does NOT re-invoke automatically on silent failure. Human must confirm.

---

## Multi-Phase Report Preservation

After verifying Phase A, Claude saves key Phase A data (task ID, commit hash, gate results)
to a brief internal note before Phase B overwrites `workflow/report.md`.
On completion, Claude presents a combined summary of both phases to the human.

---

## Sequencing Rule (Multi-Phase Tasks)

Default: Codex (backend) first → Claude (frontend) second.

EXCEPTION — Claude (frontend) first ONLY IF:
- Frontend change is entirely on an existing, stable API (no new endpoints, no type changes)
- Backend change is independent (e.g. engine optimisation with no API contract changes)
- Claude explicitly states the justification when writing the plan
