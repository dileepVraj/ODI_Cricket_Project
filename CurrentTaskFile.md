TASK: Add Rule 5.11 (mandatory disk verify) to TASK_PROTOCOL.md

MANDATORY READS — DO THESE FIRST, IN ORDER:
1. Read: docs/ai/TASK_PROTOCOL.md — Section 5 (Hard Rules) only
2. Output: "CONTEXT LOADED — Section 5 read, current rules 5.1 through 5.10 confirmed"

Do NOT touch any file until you have output that confirmation.

BASELINE BOUNCER — mandatory:
Run: python core/utils/compliance_bouncer.py --root .
Record full output as before-snapshot.

CONTEXT:
Two incidents this sprint where file writes never landed on disk:
- TASK-064: agent described the split in chat, reported COMPLETE, file unchanged
- TASK-064-REDO: agent read stale cached context instead of actual disk state,
  reported 470 lines when disk had 560

Neither incident would have been caught without manual verification.
The protocol has no rule requiring agents to confirm writes landed on disk.
Rule 5.11 closes this gap permanently.

THE FIX — append Rule 5.11 to Section 5 of TASK_PROTOCOL.md:

### Rule 5.11 — Mandatory disk verify after every file write

After writing or modifying any file, the agent MUST immediately verify
the write landed correctly on disk before proceeding to the next step.

Verification is not optional and cannot be skipped.

For every file modified, run:

  # Confirm file exists and line count is in expected range
  wc -l <filepath>

  # Confirm key markers are present
  grep -c "<expected_marker>" <filepath>

  # Confirm absent identifiers are not present (for strip/refactor tasks)
  grep -l "<stripped_identifier>" <filepath> || echo "ABSENT: confirmed"

If any check fails:
- STOP immediately
- Do NOT proceed to the next file or next task step
- Report as BLOCKED with exact mismatch details
- Await architect instruction before retrying

A task report MUST include disk verify results for every file modified.
A task marked COMPLETE without disk verify results is invalid.

TASK STEPS:

Step 1 — Open docs/ai/TASK_PROTOCOL.md.
  Locate the end of Section 5 — after Rule 5.10.
  Append Rule 5.11 exactly as specified above.
  Do not modify any existing rule.
  Do not modify any other section.

Step 2 — DISK VERIFY — mandatory:
  Run:
    grep -n "Rule 5.11" docs/ai/TASK_PROTOCOL.md
  Expected: 1 hit on the rule header line.
  If not found — STOP. Report BLOCKED.

  Run:
    grep -c "wc -l\|grep -c\|ABSENT" docs/ai/TASK_PROTOCOL.md
  Expected: 3 hits minimum.
  If fewer — STOP. Report BLOCKED.

Step 3 — Run gates:
  GATE 5: follow paradigm-sentinel SKILL.md
  GATE 6:
    python core/utils/compliance_bouncer.py --root .
    Must match baseline.

CONSTRAINTS:
- Modify ONLY docs/ai/TASK_PROTOCOL.md
- Do NOT modify any existing rule in Section 5
- Do NOT modify any other section
- Do NOT touch any source files, validator scripts, or SKILL.md files
- Do NOT touch core/data_access.py, core/interfaces/team_types.py, api/serializers.py
- api.ts has pre-existing uncommitted changes — do not stage, commit, or touch it
- No Phase 12 references
- Do not update AI_MEMORY.md — it is deprecated

REPORT FORMAT: Use CLAUDE.md Part 7 template exactly.
Append after Status:

Rule 5.11 Addition Summary:
  File modified: docs/ai/TASK_PROTOCOL.md
  Rule added: 5.11 — Mandatory disk verify after every file write
  Disk verify grep hits on Rule 5.11 header: [N — expected 1]
  Disk verify grep hits on verify commands: [N — expected 3+]
  Gate 5: PASS
  Bouncer before/after: PASS/PASS