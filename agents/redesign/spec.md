# Pipeline Redesign — Specification
# Status: IN PROGRESS
# Last updated: 2026-03-28 (Session 3)

---

## SECTION 0 — AGENT CAPABILITIES & TOOLS
*(What each agent actually is, what it can do, what MCP servers it runs)*
*(Session 3 — 2026-03-28)*

---

### CODEX — Executor

**Model:** Configured model (OpenAI or compatible)
**Invocation:** `codex exec --full-auto --output-schema agents/workflow/report-schema.json`
**Context window:** ~128K tokens
**Strengths:** CI/automation, structured JSON output, parallel subagents, OTel observability

**Native capabilities used in this pipeline:**
- `--output-schema` — forces structured JSON report (replaces freeform markdown report)
- `--json` — streams all events as JSON Lines; Claude reads for scope/failure detection
- Subagents — spawns a REVIEWER subagent with clean context after implementation (see Section 0C)
- Shell execution, file read/write, git operations via shell

**MCP servers (Codex):**
| Server | Purpose |
|---|---|
| `filesystem` | Read/write `C:\Cricket_Project_Stable` |
| `context7` | Up-to-date library docs |
| `playwright` | Visual acceptance screenshots + Playwright tests |
| `sequential-thinking` | Structured multi-step reasoning |
| `jcodemunch` | Code exploration and symbol search |
| `duckdb` (motherduck) | Query `formats/odi/data/odi.duckdb` directly |
| `cricket` | Live cricket domain context |
| `github` | Auto-create PRs, query CI status, search code |
| `eslint` | TypeScript lint gate from inside agent loop |
| `next-devtools` | Live Next.js runtime errors and hydration failures |
| `semgrep` | Security scan on Python files before commit |
| `python-lft` | ruff + mypy from inside agent loop |
| `mcp-server-git` | Controlled git operations as discrete tools |

**Skills (Codex — defined in `agents/skills/codex/`):**
- `pre-task` — baseline bouncer, scope.json write, standards load
- `reviewer` — subagent: reads implementation + spec, runs assertion, validates ACs, returns JSON verdict
- `commit-report` — structured commit + JSON report emit
- `scope-guard` — pre-commit hook: reads scope.json, rejects out-of-scope staged files

---

### GEMINI — Designer

**Model:** gemini-3-flash (or gemini-2.5-pro for large-context tasks)
**Invocation:** `gemini -p "Read GEMINI.md. Then read agents/workflow/designBrief.md and execute." --yolo`
**Context window:** 1,000,000 tokens
**Strengths:** Full-codebase reads in one pass, native memory persistence, multimodal input

**Native capabilities used in this pipeline:**
- `read_many_files` — ingest entire codebase in one pass for consistency checks
- `save_memory` — persist approved design tokens, component patterns, UI laws across sessions
- `google_web_search` — grounded search for design references, component patterns
- `web_fetch` — fetch external resources inline

**MCP servers (Gemini):**
| Server | Purpose |
|---|---|
| `filesystem` | Read/write `C:\Cricket_Project_Stable` |
| `context7` | Up-to-date library docs |
| `playwright` | Visual verification screenshots |
| `sequential-thinking` | Structured multi-step reasoning |
| `jcodemunch` | Code exploration in `frontend/` |
| `duckdb` (motherduck) | Read schema/data when designing data-grounded UIs |
| `stitch` | `@davideast/stitch-mcp` — create and iterate on Stitch designs |
| `github` | Query existing PRs, check component patterns in history |
| `next-devtools` | Live Next.js runtime errors during guide implementation |
| `eslint` | Lint guide page TypeScript during guide implementation |

**Skills (Gemini — defined in `agents/skills/gemini/`):**
- `consistency-audit` — reads full codebase (1M context), validates new component against all existing patterns
- `save-design-decisions` — persists approved tokens, layout decisions, UI laws to Gemini memory
- `guide-quality` — validates guide pages: trading narrative present, no ghost fields, no marketing language

---

### SECTION 0C — REVIEWER SUBAGENT (inside Codex)

This is the solution to G2 (no self-grading). Codex natively supports spawning subagents
with independent context. After implementation, the main Codex agent spawns a REVIEWER
subagent with a clean context — no knowledge of how the implementation was written.

**What the Reviewer subagent receives:**
- The taskFile (the spec: ACs, Verification Matrix, FILES IN SCOPE)
- The implemented files (read fresh — not from main agent's memory)
- The throwaway assertion script and its raw output

**What the Reviewer subagent does:**
1. Reads the spec independently
2. Reads every implemented file independently
3. Checks each AC: satisfied or not — with a one-line reason
4. Reads assertion output: does actual output match expected?
5. Checks scope: did any file outside FILES IN SCOPE get modified?
6. Returns structured JSON verdict:

```json
{
  "verdict": "PASS | FAIL",
  "acs": [
    {"id": "AC-1", "status": "SATISFIED", "reason": "..."},
    {"id": "AC-2", "status": "FAILED",    "reason": "..."}
  ],
  "assertion": {"expected": "...", "actual": "...", "match": true},
  "scope_clean": true,
  "issues": []
}
```

**Why this solves G2:**
- The Reviewer has genuinely different context than the Implementer
- It cannot be influenced by the implementation choices it didn't make
- The verdict is in the report before Claude ever sees it
- Claude's post-call review becomes a spot-check, not the primary verification

**Hard rules for the Reviewer subagent:**
- Read-only. No file writes, no shell commands, no commits.
- Does not communicate with the main agent — returns JSON to Codex's orchestrator.
- If the Reviewer cannot determine AC status (missing info), it returns `"status": "UNKNOWN"` — not SATISFIED.
- A FAIL verdict from the Reviewer stops the task. Main agent fixes, Reviewer re-runs.

---

## STRUCTURAL RULE — COMMUNICATION TOPOLOGY
*(Governs all sections. No exceptions.)*

```
Human ←→ Claude only.
Codex  →  Claude  (via report files — never directly to human)
Gemini →  Claude  (via report files — never directly to human)
```

Codex and Gemini do not address the human. They write reports. Claude reads them,
interprets them, and decides what — if anything — to communicate to the human.

When Codex is BLOCKED, the human never sees the raw BLOCKED report. Claude reads it,
determines if it can resolve directly, and either resolves silently or presents a
clean summary to the human with a clear decision required. The human speaks back to
Claude. Claude updates the taskFile. Claude re-invokes Codex.

This applies to every failure mode, every escalation, every question.
Claude is the sole interface between the pipeline and the human.

---

## SECTION 1 — PIPELINE GUARANTEES
*(What the pipeline must always be true of — non-negotiable)*
*(Grounded in: Cognition, Anthropic, GitHub Squad, Osmani, Galileo research — Session 1)*

Each guarantee is binary: the pipeline either satisfies it or has failed, regardless of
how clean the code looks or what the report says.

---

### G1 — Silent failure is impossible to miss

Before every agent invocation, the current state of the repo (last commit hash + timestamp)
is written to a file. After invocation, that file is read and compared automatically.
If nothing changed — no new commit, no updated report — the pipeline stops and alerts.
This detection must never rely on Claude's in-session memory.

*Research basis: GitHub Squad's pre/post state snapshot. Cognition: "context engineering
over architecture" — the system must engineer its own failure detection.*

---

### G2 — No agent is the final judge of its own work

An agent that implements a task cannot be the sole verifier that the task is complete.
For calculator/engine/service tasks: a throwaway assertion script is written BEFORE
implementation begins (based on the Verification Matrix concrete example). Codex runs it
after implementing, and the raw terminal output is embedded in the report — not Codex's
claim about the output, the actual output. Claude reads the number, not the checkbox.
For frontend tasks: Playwright screenshot output is embedded in the report.
The implementing agent's report is evidence, not verdict.

No persistent test suite. Assertion scripts are deleted after the task completes.
This eliminates staleness — there is nothing to go stale.

*Research basis: GitHub Squad's independent reviewer rule. Osmani: TDD forces correct
behaviour specification before implementation — prevents "testing what the code does"
instead of "testing what the code should do."*

---

### G3 — Logic correctness is proven by execution, not inspection

For any task touching calculators, engines, or services: the Verification Matrix defines
`input → expected output` before Codex writes any code. This is the spec. The throwaway
assertion script (see G2) formalises that matrix row into executable code. The function
must make the assertion pass — if it fails, the function is wrong, not the assertion.

Order is non-negotiable:
  1. Verification Matrix filled (Claude, before taskFile is written)
  2. Assertion script written (Codex, before function is implemented)
  3. Function implemented (Codex, to make assertion pass)
  4. Assertion run — raw output embedded in report
  5. Assertion script deleted

"The code looks correct" is not a passing criterion.
No test suite. No pytest gate. Verification is per-task, ephemeral, and execution-based.

*Research basis: "The bottleneck is no longer generation. It's verification." — Osmani.
Deliberately no persistent test suite — deleted tests were stale Golden Master artifacts
that described what code did, not what it should do. Per-task assertions replace them.*

---

### G4 — Every decision survives a session boundary

Nothing that matters lives only in conversation context. Every approved plan, every design
decision, every AC, every gate result is written to a file before the session that produced
it ends. If Claude's context is cleared mid-task, the next session reads the files and
resumes without loss. "Resume without loss" means: knows what was decided, what was built,
what passed, what is next.

*Research basis: Osmani's "AGENTS.md compound learning" — human-curated persistent context
across sessions is a top-3 leverage factor. LangGraph's checkpointing for resumable
execution.*

---

### G5 — Every phase is permanently auditable

Task reports are never overwritten. Each phase of each task writes to its own file
(e.g. `reports/TASK-166-phase-A.md`). The full record — what was asked, what was built,
which gates ran, what they returned, which ACs passed or failed — is readable for any
past task at any future point. Overwriting a report to start the next phase is forbidden.

*Research basis: GitHub Squad's append-only `decisions.md`. "One agent ignoring its spec
infects downstream agents with flawed context" — Galileo. Phase A's audit trail must
survive Phase C.*

---

### G6 — Context transfer is complete, not summarised

When Claude hands a task to Codex via taskFile.md, the file contains the full decision
trace: what was decided, why, what alternatives were rejected, what the exact expected
output looks like (field by field), and what a correct implementation produces for a
specific known input. A taskFile that omits the reasoning behind a constraint gives Codex
a compressed context that will produce a compressed (wrong) result.

*Research basis: Cognition: "share full agent traces, not just individual messages."
Osmani: "spec precision is the highest-leverage input — a vague spec multiplies errors
across the entire fleet."*

---

### G7 — An incomplete spec cannot start a task

If the taskFile for a calculator/engine task has any blank cell in the Verification Matrix,
the task does not start. This check is performed by Claude before invocation — not by
Codex after reading the file. Claude holds the gate, not the agent being dispatched.
A task that is not fully specified is not ready to be assigned.

*Research basis: Workflow_and_Laws.md "Field Contract Law" — validated as correct by
research. Osmani: "spec quality determines output quality more than any other factor."*

---

### G8 — Hard iteration limits with a defined exit

Every agent invocation has a maximum retry count (3). On the third failure, the pipeline
does not retry. It writes a terminal BLOCKED state to the task report, preserves all
artifacts, and escalates to the human with: what failed, what was tried, what the
decision point is. "Keep trying" is not a protocol. Endless loops are a documented
production failure mode.

*Research basis: Galileo failure mode #5 — endless loops. Anthropic: "MAX_ITERATIONS=8
per agent; forced reflection before retry." Production content pipeline: "max 3 iterations
before human escalation."*

---

### G9 — Scope is verified, not trusted

After every agent commit, the pipeline checks that no files outside the declared scope
(FILES IN SCOPE in taskFile) were modified. This is a diff check against the task's
declared scope, run before the report is accepted. An agent that modifies out-of-scope
files has violated the task contract, regardless of whether the modification looks benign.

*Research basis: Galileo: "context blindness causes agents to make locally correct but
globally incoherent decisions" — scope enforcement is the structural defence against this.*

---

### G10 — Human-curated context only

State files that persist between sessions (handoff, task history, agent instructions) are
written or reviewed by a human or Claude acting as Architect — never auto-generated by the
implementing agent. An agent that writes its own persistent context creates a feedback loop
that degrades future performance.

*Research basis: Osmani: "LLM-generated AGENTS.md offers no benefit and can marginally
reduce success rates (~3%). Human-written context improves outcomes by ~4%." Applies
directly to Codex writing handoff.md entries.*

---

## SECTION 2 — FAILURE MODES
*(What must never happen — and what is acceptable/recoverable)*
*(Session 2 — 2026-03-27)*

All failure modes route through Claude. Codex and Gemini write reports. Claude interprets
and decides. The human is involved only when Claude cannot resolve without a decision.

---

### FAILURE STATE TAXONOMY

| ID | Name | Recoverable? | Who resolves? | Max retries |
|---|---|---|---|---|
| F1 | Silent failure | Yes (if git clean) | Claude detects, human confirms retry | 1 re-invoke |
| F2 | Assertion failure | Yes | Codex fixes → Claude re-invokes | 3 rounds |
| F3 | Gate failure | Yes | Codex fixes → Claude re-invokes | 3 rounds |
| F4 | BLOCKED | Yes | Claude resolves or presents to human | No limit on questions |
| F5 | Scope violation | Terminal for that commit | Claude diagnoses, human authorises scope change | 0 retries |
| F6 | Partial phase | Terminal | Claude presents options, human decides | 0 retries |
| F7 | AC mismatch | Yes (once) | Claude rewrites spec, re-invokes once | 1 round |
| F8 | Context loss | Terminal for task | Human reviews git log, decides | 0 retries |

---

### F1 — Silent Failure

**What it is:** Agent invoked, CLI returns, but pre-call state file shows no new commit
and no updated report. The agent did nothing, crashed, or produced no output.

**Detection:** Automatic. Claude compares pre-call state file (last commit hash) against
post-call git log. No diff → silent failure confirmed. Never relies on Claude's memory.

**Resolution path:**
```
Claude checks git status:
  │
  ├── Git clean (no commits, no staged changes)
  │     → Claude informs human: "Agent ran but produced nothing. Git is clean."
  │       Human confirms. Claude re-invokes once.
  │       Second silent failure → human decides whether to debug agent setup.
  │
  ├── New commits exist, no report
  │     → Claude informs human: "Work done (commit: [hash]) but no report written."
  │       Claude re-invokes: "Work done. Write report only."
  │
  └── Partial staged changes, no commit
        → Claude informs human: exact files staged, no commit made.
          Human decides: commit manually, discard, or investigate.
          Claude does NOT re-invoke — partial state is ambiguous.
```

---

### F2 — Assertion Failure

**What it is:** Codex ran the throwaway assertion script (written before implementation,
based on the Verification Matrix). The actual output did not match expected output.
The function is logically wrong.

**Resolution path:**
```
Round 1: Codex reads assertion output → fixes implementation → re-runs assertion.
Round 2: Same. Claude reads both reports looking for pattern in the failure.
Round 3: Same. If still failing:
  → Terminal. Claude reads all three failure outputs.
  → Claude presents to human:
      - What the assertion expected
      - What the function returned across all 3 rounds
      - Whether the Verification Matrix itself might be wrong (matrix error vs code error)
  → Human decides: fix the matrix (replan) or investigate the data.
```

**Important:** If the assertion keeps failing with the same wrong value, it's likely the
Verification Matrix concrete example was wrong. Claude must flag this explicitly —
it is an Architect error, not a Codex error.

---

### F3 — Gate Failure

**What it is:** One or more gates (boundary-sentinel, manifest-contract-verifier,
compliance_bouncer, frontend-lint-sentinel, etc.) returned FAIL.

**Resolution path:**
```
Round 1: Codex reads gate output → fixes violation → re-runs gate.
Round 2: Same.
Round 3: Same. If still failing:
  → Terminal. Claude reads the gate output directly.
  → Claude presents to human:
      - Which gate failed
      - Which specific rule was violated
      - Which file and line
      - Whether this is a pre-existing violation (baseline drift) or new
  → Human decides: fix the violation, waive it (with justification), or
    change the gate configuration.
```

**Pre-existing violations:** If the baseline bouncer snapshot shows the violation existed
before the task, it is a pre-existing issue. Claude notes this. It does not block the
task — but it must be recorded in the task report and addressed in a separate task.

---

### F4 — BLOCKED

**What it is:** Codex cannot proceed because the taskFile is ambiguous, a required file
is missing, the scope is unclear, or an unexpected state exists in the codebase.
Codex stops immediately and writes a BLOCKED report with its exact question.
This is correct behaviour — not a failure of Codex.

**Resolution path:**
```
Claude reads the BLOCKED report:
  │
  ├── Resolvable by Claude (Small Tweak Rule applies):
  │     Fix is in agents/workflow/ files (taskFile, designBrief, scope.json)
  │     or pure config/doc files. Nothing inside core/, api/, or formats/.
  │     → Claude fixes directly, re-invokes Codex. Human not involved.
  │
  └── Requires human decision:
        → Claude summarises to human in plain language:
            "Codex is blocked. The question is: [one clear sentence]."
            "Options: [A] or [B]."
          Human answers. Claude updates taskFile. Claude re-invokes Codex.
```

**No retry limit on F4.** BLOCKED is a question, not a failure. Multiple questions
in sequence are fine — each one resolved before re-invoking.

---

### F5 — Scope Violation

**What it is:** Pre-commit hook reads `agents/workflow/scope.json` and finds that staged
files include paths not declared in FILES IN SCOPE. The commit is rejected.

**Resolution path:**
```
Claude reads the hook output (which files were out of scope):
  │
  ├── Codex touched an unlisted file it genuinely needed
  │     → Claude decides: was the omission a planning error?
  │       YES → Claude updates scope.json, informs human why, re-invokes.
  │       NO  → Claude presents to human. Human decides whether to expand scope.
  │
  └── Codex modified a file it had no reason to touch
        → Terminal. Claude presents to human with exact files and diff.
          Human decides: discard changes, or investigate why Codex went out of scope.
```

**Zero retries on scope violation.** The commit was rejected — no partial state exists.
Codex re-runs with corrected scope after Claude updates scope.json.

---

### F6 — Partial Phase Commit

**What it is:** A multi-phase task (MULTI-PHASE-A → MULTI-PHASE-C) has Phase A commits
on main but Phase B or C fails terminally. The repo contains verified Phase A work
but the full task cannot complete.

**Resolution path:**
```
Claude presents to human — exactly this information:
  - Phase A commits: [hash list] — what they contain
  - Why Phase B/C failed terminally: [one paragraph, specific]
  - Option A: git revert [hashes] — rolls back Phase A, clean slate, start over
  - Option B: keep Phase A, fix the Phase B/C spec, re-invoke for that phase only
  - Claude's recommendation with reasoning

Human decides. Claude executes the chosen option.
```

**No auto-revert.** Phase A was verified PASS. Auto-reverting verified work destroys
confirmed-correct output based on a downstream failure. Human makes this call.

---

### F7 — AC Mismatch

**What it is:** Gates pass, assertion passes, but Claude's implementation review finds
the code does not satisfy the intent of an AC. The implementation is structurally
correct but wrong for the task. This is an Architect error — the spec was ambiguous
enough to permit a wrong-but-plausible implementation.

**Resolution path:**
```
Claude identifies exactly which AC failed and why the implementation misses it.
Claude rewrites that AC (and any related Verification Matrix rows) to be unambiguous.
Claude re-invokes Codex once with the corrected spec.

If the second attempt also misses the intent:
  → Terminal. Claude presents to human:
      - What the AC was trying to express
      - What both implementations produced
      - Whether the AC itself needs fundamental rethinking
  → Human clarifies intent. Claude rebuilds the relevant spec section from scratch.
  → New task invocation (not a retry of the original task).
```

**1 round only.** F7 is a spec failure, not a code failure. Three rounds of Codex
against an ambiguous spec produces three different wrong implementations.
Claude owns this failure — it wrote the ambiguous spec.

---

### F8 — Context Loss

**What it is:** Claude starts a new session and the combination of handoff + journal +
task reports does not contain enough information to determine the current task state.
What was in progress, what phase was active, what was already committed — unknown.

**Resolution path:**
```
Claude runs: git log --oneline -10
Claude reads: agents/redesign/journal.md (latest session entry)
Claude reads: agents/workflow/reports/ (all reports for the active task, if any)

If state can be reconstructed from files alone:
  → Claude resumes. Notes in journal that context loss occurred.

If state cannot be reconstructed:
  → Claude presents to human:
      - Last known state from git log
      - What is unclear
      - Options: treat current git state as the baseline and continue,
        or restart the task from the last verified phase.
  → Human decides. Claude writes a full journal entry before proceeding.
```

**Prevention is the fix.** F8 should never occur if G4 (every decision in files) and
G5 (append-only reports) are upheld. F8 appearing in production means G4 or G5 was
violated — flag it and fix the protocol, not just the instance.

---

## SECTION 3 — COMMUNICATION PROTOCOL
*(How agents talk to each other — replaces markdown file IPC)*

[ SESSION 3 ]

---

## SECTION 4 — VERIFICATION & GATE LAYER
*(Replaces honor-system QA and lint-only gates)*
*(Session 4 — 2026-03-28)*

---

### PHILOSOPHY

Gates catch structural/style violations. The Reviewer catches intent violations.
Neither alone is sufficient. Both together mean: code that reaches Claude has already
passed automated structure checks AND an independent intent review.

"The code looks correct" is never a gate result. Every gate returns PASS or FAIL with
a specific reason, line number, and rule violated — or nothing to report.

All gate output is JSON. It feeds directly into the task report (TASK-XXX.json).
No prose. No interpretation required.

---

### FULL VERIFICATION SEQUENCE

```
pre-task skill
    │
    ▼
ASSERTION written (calculator tasks only — before implementation)
    │
    ▼
IMPLEMENTATION
    │
    ▼
ASSERTION run → raw output captured
    │
    ▼
GATE SEQUENCE (backend and/or frontend — see triggers below)
    │
    ▼
REVIEWER subagent (clean context — reads spec + implementation + assertion output)
    │
    ├── REVIEWER: FAIL → fix → loop back to ASSERTION run (max 3 rounds total)
    └── REVIEWER: PASS → commit-report skill → task complete
```

Order is fixed. Gates before Reviewer. Reviewer before commit.
No commit until Reviewer returns PASS.

---

### BACKEND GATE SEQUENCE

Triggered by which layers the task touches (set in pre_call_state.json).

| Gate | ID | Trigger | What it checks |
|---|---|---|---|
| boundary-sentinel | GATE1 | Any `core/` file modified | Layer boundary violations — domain core importing from API layer, etc. |
| duckdb-lint-ops | GATE2 | Any `calculators/` `engines/` `services/` modified | DuckDB operation patterns — no raw SQL strings, correct connection usage |
| manifest-contract-verifier | GATE3 | Any `manifest.py` or engine file modified | All engine output fields registered in manifest, no ghost fields |
| serialization-guard | GATE4 | Any `api/serializers.py` or engine return type modified | Serializer matches TypedDict, no additive-only breakage |
| semgrep-security | GATE5S | Any `core/` `api/` `formats/` Python file modified | Security scan: injection, hardcoded secrets, unsafe eval, unsafe deserialization |
| python-type-check | GATE5T | Any Python file modified | ruff + mypy — type errors, unused imports, style violations |
| paradigm-sentinel | GATE5P | Always | Coding paradigm compliance — no I/O in execute path, no visual strings from domain core |
| compliance-bouncer | GATE6 | Always — last | Full compliance scan. Compares violation count against baseline in pre_call_state.json |

**Gate 6 baseline rule:** Post-task violation count must equal baseline count.
New violations introduced by this task = FAIL, regardless of pre-existing violations.
Pre-existing violations are noted in the report but do not block the task.

**Gate output format (each gate writes to stdout as JSON when --json passed):**
```json
{
  "gate": "GATE5S",
  "status": "FAIL",
  "triggered": true,
  "violations": [
    {
      "file": "core/calculators/team/venue_calculator.py",
      "line": 47,
      "rule": "hardcoded-secret",
      "message": "Hardcoded API key found"
    }
  ],
  "violation_count": 1
}
```

---

### FRONTEND GATE SEQUENCE

| Gate | ID | Trigger | What it checks |
|---|---|---|---|
| eslint-sentinel | GATEF1 | Any `.tsx` `.ts` modified | ESLint via MCP — TypeScript lint, React rules, import order |
| frontend-paradigm-sentinel | GATEF2 | Always after F1 | No domain logic in components, no raw hex/rgba, no arbitrary Tailwind |
| type-sync-guard | GATEF3 | Always | `npx tsc --noEmit` — full TypeScript strict check, zero new errors |
| next-devtools-check | GATEF4 | Always | Query Next.js MCP for live runtime errors, hydration failures, build errors |

**GATEF4 detail:** Requires dev server running (`npm run dev`). Codex queries the
`next-devtools` MCP for `get_errors` — any errors not present in the pre-task baseline
are a FAIL. Pre-existing errors are noted but do not block.

**GATEF4 exception:** If dev server is not running, GATEF4 is SKIPPED with a note.
Claude decides whether to require a manual check before accepting the report.

---

### REVIEWER SUBAGENT — POSITION AND ROLE

The Reviewer runs after all gates pass. If any gate is FAIL, the Reviewer does not run —
fixing gate violations first prevents the Reviewer from reviewing broken code.

**What the Reviewer adds that gates cannot:**
- Gates check structure. The Reviewer checks intent.
- Gates don't read ACs. The Reviewer checks every AC against the actual implementation.
- Gates don't check the Verification Matrix result. The Reviewer checks assertion output.
- Gates don't check scope. The Reviewer cross-checks FILES IN SCOPE against what was touched.

**Reviewer failure after gates pass** means the code is structurally correct but wrong
for the task. This is F7 (AC mismatch) — Claude owns the fix (rewrite the ambiguous AC).

---

### GATE CLASSIFICATION TABLE

| Task type | Backend gates | Frontend gates |
|---|---|---|
| bug-fix (backend) | 1,2,3,4,5S,5T,5P,6 | — |
| new-feature (backend) | 1,2,3,4,5S,5T,5P,6 | — |
| refactor (backend) | 5T,5P,6 | — |
| frontend-bug-fix | — | F1,F2,F3,F4 |
| frontend-new-component | — | F1,F2,F3,F4 |
| full-stack | 1,2,3,4,5S,5T,5P,6 | F1,F2,F3,F4 |
| validator-fix | 6 | — |
| infra/hook | 6 | — |

---

### GATE FAILURE PROTOCOL

On any gate FAIL:
1. Codex reads the gate's JSON output — identifies specific file, line, rule
2. Codex fixes the violation
3. Codex re-runs the failed gate only (not the full sequence)
4. If gate passes → continue sequence from next gate
5. Round counter increments on each fix attempt per gate
6. Round 3 fail → terminal (F3 failure mode) → write BLOCKED report, Claude diagnoses

**Gates do not cascade retry.** Fix the specific gate that failed, re-run it, move on.
Do not re-run earlier gates unless the fix touches a file that triggers them again.

---

### PRE-EXISTING VIOLATION HANDLING

Before any task, `pre_call_state.json` records baseline violation count from compliance_bouncer.

After the task, GATE6 runs compliance_bouncer again.
- Same count or lower → PASS (task did not introduce new violations)
- Higher count → FAIL (task introduced new violations — must fix before committing)
- Pre-existing violations are logged in the report under `pre_existing_violations`
  but are never a blocker for the current task

This means a task can complete with pre-existing violations in the repo, as long as it
didn't add new ones. Pre-existing violations are tracked and addressed in dedicated
clean-up tasks.

---

### REPORT SCHEMA (feeds Section 5)

Every gate writes JSON to stdout. Codex's commit-report skill aggregates:

**Note:** `gates` is an **array** (not an object keyed by gate ID). OpenAI structured
output requires `additionalProperties: false` on all objects, which forbids
dynamic keys. Array format is the canonical representation. Gate ID is carried
inside each element as `gate_id`.

```json
{
  "gates": [
    {"gate_id": "GATE1",  "triggered": false, "status": "SKIPPED", "violations": []},
    {"gate_id": "GATE2",  "triggered": true,  "status": "PASS",    "violations": []},
    {"gate_id": "GATE3",  "triggered": true,  "status": "PASS",    "violations": []},
    {"gate_id": "GATE4",  "triggered": false, "status": "SKIPPED", "violations": []},
    {"gate_id": "GATE5S", "triggered": true,  "status": "PASS",    "violations": []},
    {"gate_id": "GATE5T", "triggered": true,  "status": "PASS",    "violations": []},
    {"gate_id": "GATE5P", "triggered": true,  "status": "PASS",    "violations": []},
    {"gate_id": "GATE6",  "triggered": true,  "status": "PASS",    "violations": []},
    {"gate_id": "GATEF1", "triggered": false, "status": "SKIPPED", "violations": []},
    {"gate_id": "GATEF2", "triggered": false, "status": "SKIPPED", "violations": []},
    {"gate_id": "GATEF3", "triggered": false, "status": "SKIPPED", "violations": []},
    {"gate_id": "GATEF4", "triggered": false, "status": "SKIPPED", "violations": []}
  ],
  "reviewer": { "<full Reviewer JSON verdict>" },
  "assertion": {
    "ran": true,
    "expected": "62.5",
    "actual": "62.5",
    "match": true,
    "raw_output": "ASSERTION PASSED: {'bat_first_win_pct': 62.5}"
  }
}
```

Claude reads this JSON. No interpretation of prose needed.
A task with all gates PASS + reviewer PASS + assertion match true = verified PASS.
Claude's post-call review becomes a spot-check for edge cases, not the primary QA.

---

## SECTION 5 — STATE & HANDOFF MECHANISM
*(Replaces 25-line prose handoff.md)*
*(Session 5 — 2026-03-28)*

---

### PHILOSOPHY

State must survive every failure mode: session boundary, context compression,
mid-task crash, partial phase commit. If it can't be read from a file by a
fresh Claude session with zero conversation history — it does not exist.

Prose is for humans. State files are for machines. Claude reads machine-readable
state, interprets it, and presents it to humans. The state files are never
for direct human consumption.

---

### FILE SYSTEM — COMPLETE MAP

```
agents/
  workflow/
    state.json              ← PERMANENT. Claude's session anchor. Replaces handoff.md.
    taskFile.md             ← Active task only. Cleared after complete/blocked-resolved.
    designBrief.md          ← Active design only. Cleared after Gemini executes.
    scope.json              ← Active task only. Written by pre-task, cleared by commit-report.
    pre_call_state.json     ← Written before invocation, cleared by commit-report.
    assertion.py            ← Written by pre-task, deleted by commit-report.
    report-schema.json      ← PERMANENT. Used by --output-schema flag. Never cleared.
    reports/                ← PERMANENT. Append-only. One file per task. Never deleted.
      TASK-166.json
      TASK-167-blocked.json
      TASK-168.json
      consistency-audit-<component>.json
      guide-quality-<feature>.json
      design-decisions-saved.json
  skills/
    codex/                  ← Codex skill definitions
    gemini/                 ← Gemini skill definitions
  redesign/
    spec.md                 ← This file
    journal.md              ← Session journal
```

---

### STATE.JSON — THE SESSION ANCHOR

Replaces `handoff.md` entirely. Machine-readable. Claude reads this at every session start.
Written by Claude only. Never written by Codex or Gemini.

**Schema:**
```json
{
  "schema_version": 1,
  "last_completed_task": "TASK-165",
  "last_commit": "5835942",
  "gate_baseline_violations": 0,
  "active": {
    "task_id": null,
    "phase": null,
    "agent": null,
    "invoked_at": null,
    "pre_call_commit": null
  },
  "dirty_files": [],
  "standing_notices": [],
  "next": "ready"
}
```

**Field definitions:**

| Field | What it means | Who writes it |
|---|---|---|
| `last_completed_task` | Task ID of last verified PASS | Claude after green signal |
| `last_commit` | Hash of last verified commit | Claude after green signal |
| `gate_baseline_violations` | Compliance bouncer count after last green signal | Claude after green signal |
| `active.task_id` | Task currently in progress (null if idle) | Claude before invocation |
| `active.phase` | SOLO / MULTI-PHASE-A / MULTI-PHASE-C | Claude before invocation |
| `active.agent` | Codex / Gemini | Claude before invocation |
| `active.invoked_at` | ISO timestamp of CLI invocation | Claude before invocation |
| `active.pre_call_commit` | Commit hash before invocation (G1 detection) | Claude before invocation |
| `dirty_files` | Files with known issues not yet addressed | Claude, manually |
| `standing_notices` | Cross-task warnings (pre-existing violations, etc.) | Claude, manually |
| `next` | "ready" / "awaiting human" / "phase-B pending" | Claude after each transition |

**Lifecycle:**
- Claude writes `active.*` fields before every agent invocation
- Claude clears `active.*` (sets to null) after green signal
- Claude updates `last_*` fields after green signal
- Claude never clears `dirty_files` or `standing_notices` without explicit resolution
- Codex and Gemini never touch state.json

---

### SESSION STARTUP PROTOCOL (replaces CLAUDE BOOTSTRAP C0-C5)

Every new Claude session runs this sequence before anything else:

```
Step 1 — Read state.json
  active.task_id is null  → idle, ready for new task
  active.task_id not null → task was in progress when session ended

Step 2 — If active task exists:
  Read agents/workflow/reports/<active.task_id>*.json (latest report for this task)
  Compare active.pre_call_commit against git log --oneline -1
    Same hash → agent ran but produced nothing (F1 — silent failure)
    Different hash → commits exist since invocation — read them
  Determine: COMPLETE, BLOCKED, or SILENT FAILURE
  Follow failure mode protocol from Section 2

Step 3 — Load context
  Read agents/workflow/taskFile.md (if active task)
  Read last 3 reports from reports/ for recent context
  Read standing_notices from state.json

Step 4 — Ready
  Inform human of current state in one sentence.
  Wait for instruction.
```

This replaces the C0–C5 bootstrap entirely. No soul files to read on every session
(souls are embedded in agent instructions — loaded once, not every session).
No handoff.md to interpret. One structured file, one protocol.

---

### REPORTS/ DIRECTORY — APPEND-ONLY RULES

- One JSON file per task: `TASK-XXX.json`
- BLOCKED states: `TASK-XXX-blocked-R1.json`, `TASK-XXX-blocked-R2.json` (round number)
- Multi-phase: `TASK-XXX-phase-A.json`, `TASK-XXX-phase-C.json`
- Non-task audits: `consistency-audit-<name>.json`, `guide-quality-<name>.json`
- Files are NEVER deleted, NEVER overwritten
- Claude reads the full reports/ dir at session start for a task that was in progress
- Reports are the permanent audit trail — they answer "what happened in TASK-X" forever

---

### REPORT-SCHEMA.JSON — STRUCTURED OUTPUT CONTRACT

Written once during setup. Used by `codex exec --output-schema agents/workflow/report-schema.json`.
Forces Codex to emit a JSON report conforming to this schema — not freeform markdown.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TaskReport",
  "type": "object",
  "required": ["task_id", "agent", "status", "commit", "gates", "reviewer", "acs"],
  "properties": {
    "task_id":    {"type": "string"},
    "date":       {"type": "string", "format": "date"},
    "agent":      {"type": "string", "enum": ["Codex", "Gemini"]},
    "status":     {"type": "string", "enum": ["COMPLETE", "BLOCKED"]},
    "commit":     {"type": ["string", "null"]},
    "baseline_violations": {"type": "integer"},
    "post_task_violations": {"type": "integer"},
    "violations_delta":     {"type": "integer"},
    "gates": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["triggered", "status"],
        "properties": {
          "triggered": {"type": "boolean"},
          "status":    {"type": "string", "enum": ["PASS", "FAIL", "SKIPPED"]},
          "violations":{"type": "array"}
        }
      }
    },
    "reviewer": {
      "type": "object",
      "required": ["verdict"],
      "properties": {
        "verdict": {"type": "string", "enum": ["PASS", "FAIL", "NOT_RUN"]},
        "acs":     {"type": "array"},
        "assertion": {"type": "object"},
        "scope_clean": {"type": "boolean"}
      }
    },
    "acs": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "status"],
        "properties": {
          "id":     {"type": "string"},
          "status": {"type": "string", "enum": ["SATISFIED", "FAILED", "UNKNOWN"]},
          "reason": {"type": "string"}
        }
      }
    },
    "files_modified":    {"type": "array", "items": {"type": "string"}},
    "scope_violations":  {"type": "array", "items": {"type": "string"}},
    "blockers_hit":      {"type": "array"},
    "taskfile_cleared":  {"type": "boolean"}
  }
}
```

Claude validates the report against this schema. A report that doesn't conform to
the schema is treated as a silent failure (F1) — the agent did not complete correctly.

---

### SETUP STEPS (run once when pipeline is initialised)

```bash
# 1. Create reports directory
mkdir -p agents/workflow/reports

# 2. Install scope-guard pre-commit hook
cp agents/skills/codex/scope-guard.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# 3. Write initial state.json
cat > agents/workflow/state.json << 'EOF'
{
  "schema_version": 1,
  "last_completed_task": "TASK-165",
  "last_commit": "5835942",
  "gate_baseline_violations": 0,
  "active": {
    "task_id": null,
    "phase": null,
    "agent": null,
    "invoked_at": null,
    "pre_call_commit": null
  },
  "dirty_files": [],
  "standing_notices": [],
  "next": "ready"
}
EOF

# 4. Write report-schema.json (copy schema from spec Section 5)
# → agents/workflow/report-schema.json

# 5. Add state.json and reports/ to .gitignore exceptions
#    (they must be committed — they are the audit trail)
# → ensure agents/workflow/reports/ is NOT in .gitignore
# → ensure agents/workflow/state.json is NOT in .gitignore
```

---

### WHAT CLAUDE DOES DIFFERENTLY (summary of changes from old pipeline)

| Old behaviour | New behaviour |
|---|---|
| Reads handoff.md (25 lines prose) | Reads state.json (structured JSON) |
| Remembers pre-call timestamp in conversation | Writes active.pre_call_commit to state.json |
| Reads markdown report, interprets it | Validates JSON report against schema |
| Updates handoff.md after green signal | Updates state.json (5 specific fields) |
| Calls it "green signal" based on prose report | Calls it green when: all gates PASS + reviewer PASS + assertion match + schema valid |
| Handoff lost if context compresses | state.json survives any context event |

---

## SECTION 6 — AGENT INSTRUCTIONS
*(New CLAUDE.md / AGENTS.md / GEMINI.md)*
*(Session 6 — 2026-03-28)*

Draft files written to `agents/redesign/`. Awaiting human approval before replacing live files.

| File | Draft location | Replaces |
|---|---|---|
| new-CLAUDE.md | `agents/redesign/new-CLAUDE.md` | `CLAUDE.md` |
| new-AGENTS.md | `agents/redesign/new-AGENTS.md` | `AGENTS.md` |
| new-GEMINI.md | `agents/redesign/new-GEMINI.md` | `GEMINI.md` |

**Key changes from v4.0 to v5.0:**

CLAUDE.md:
- Bootstrap reads state.json instead of handoff.md
- Invocation uses --output-schema flag (structured JSON report)
- Post-call validation is schema check + green signal checklist, not prose interpretation
- state.json update protocol replaces handoff.md update protocol
- Small Tweak Rule narrowed: workflow files only, never core/api/formats/frontend

AGENTS.md:
- E2 step replaced with "run pre-task skill" (pre-task.md)
- Execution sequence now has 6 explicit phases with Reviewer in Phase 5
- Gates reference new gate IDs (GATE5S, GATE5T, GATEF4)
- Reports go to agents/workflow/reports/TASK-XXX.json — never report.md
- BLOCKED report format is JSON, not markdown
- Hard prohibition added: never write to report.md (deprecated)

GEMINI.md:
- New modes: consistency-audit, save-design-decisions (in addition to design/guide)
- Design mode report is JSON with stitch_screen_html embedded
- Guide mode includes guide-quality skill before gates
- Native tools (read_many_files, save_memory) explicitly referenced
- handoff.md prohibition added (deprecated in v5)

**Implementation tasks before going live (in order):**
1. Install scope-guard pre-commit hook
2. Gate scripts output format updated to JSON (Codex task)
3. Replace CLAUDE.md, AGENTS.md, GEMINI.md with drafts after human approval
4. Archive old workflow files (handoff.md → git history only)
5. Verify state.json and reports/ are not in .gitignore
