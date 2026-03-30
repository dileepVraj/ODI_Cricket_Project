# SKILL: reviewer
# Agent: Codex (main agent — reads this to invoke the reviewer subagent)
# When: After all gates pass, before commit
# Purpose: Invoke the permanent CODEX-REVIEWER skill in a fresh subagent

---

## WHAT THE REVIEWER IS

The CODEX-REVIEWER is a permanent reusable skill installed at:
`C:\Users\khaisar jaha\.codex\skills\codex-reviewer\`

Its identity, rules, and output format are defined there permanently.
You do not define or re-embed the reviewer's persona here.
You only collect the right inputs and invoke it correctly.

---

## STEP 1 — Collect inputs

Gather the following before spawning. Everything must be passed explicitly —
the subagent has no shared memory with you and no independent filesystem access.

1. Full contents of `agents/workflow/taskFile.md`
2. Full contents of every file listed under FILES IN SCOPE in the taskFile
3. Raw terminal output from the last assertion run (after implementation)
   - Calculator/engine/service task: required — capture verbatim
   - Frontend/infra task: pass `N/A - non-calculator task`
4. The expected assertion value from the Verification Matrix (or `null`)
5. List of files actually modified: `git diff --cached --name-only`

---

## STEP 2 — Spawn the subagent

Use `spawn_agent`. Reference the skill in the initial prompt:

```
Use $codex-reviewer as CODEX-REVIEWER for this task. Return one JSON verdict only.

TASK ID: TASK-XXX

=== TASK SPEC ===
<full contents of agents/workflow/taskFile.md>

=== IMPLEMENTATION FILES ===
--- <file path 1> ---
<full file contents>

--- <file path 2> ---
<full file contents>

(repeat for every file in FILES IN SCOPE)

=== ASSERTION EXPECTED ===
<expected value from Verification Matrix, or null>

=== ASSERTION OUTPUT (raw terminal) ===
<verbatim terminal output from running assertion.py after implementation>

=== FILES ACTUALLY MODIFIED ===
<one path per line from git diff --cached --name-only>
```

---

## STEP 3 — Wait for the verdict

Use `wait_agent` to receive the subagent's response.
The reviewer returns one JSON object and nothing else.
If the response is not valid JSON — treat it as `"verdict": "FAIL"` with
`"issues": ["reviewer returned non-JSON output"]`.

---

## STEP 4 — Act on the verdict

**PASS** (every AC SATISFIED, assertion.match true or null, scope_clean true):
→ Proceed to Phase 6 (commit-report).

**FAIL**:
→ Read the specific failure reason in the verdict.
→ Fix only what failed — do not re-implement from scratch.
→ Re-run the assertion if it was a calculator task.
→ Re-run only gates affected by the fix.
→ Increment round counter.
→ Spawn a NEW subagent for the next review round — do not reuse the prior instance.
→ Round 3 FAIL → write BLOCKED report. Do not retry further.

---

## HARD RULES

- Never review the work yourself. You implemented it — you are not independent.
- Always spawn a fresh subagent for each round. `$codex-reviewer` is reusable;
  any single running instance of it is not.
- Never pass `fork_context`. Pass raw artifacts explicitly as shown in Step 2.
- If the reviewer skill is missing or fails to load — write BLOCKED report immediately.
  Do not attempt inline review as a fallback.
