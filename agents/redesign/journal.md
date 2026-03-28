# Pipeline Redesign — Session Journal

---

## Session 1 — 2026-03-27
Topic: Pipeline Guarantees (Section 1)
Status: COMPLETE
Decisions made:
  - 10 guarantees written to spec.md Section 1 (G1–G10)
  - Architecture verdict: sequential + human gates is correct — research confirms it
  - The problem is mechanical, not architectural
  - Closest proven analog: GitHub Squad (coordinator + specialists + append-only state)
  - Key research sources: Cognition, Anthropic, Osmani, Galileo, GitHub Squad
  - LangGraph/CrewAI rejected as too heavy — human gates already solve the concurrency problem
Open questions resolved post-session:
  - G2: throwaway assertion script written by Codex BEFORE implementation, based on
    Verification Matrix. Raw output embedded in report. Deleted after task. No test suite.
  - G3: updated to match — per-task ephemeral verification, not pytest gate.
    Test suite deliberately absent — stale Golden Master problem. Functions will be
    overhauled; assertions written fresh per task as overhaul happens.
  - G9 (scope verification): pre-commit hook reading scope.json — still open for Session 5.
  - TDD order confirmed: Matrix → assertion → implement → run → delete.
Pick up next: Session 2 — Failure Modes (Section 2)
  Read spec.md Section 1 first. Then define: what failure states can exist, which are
  recoverable, which are terminal, and what the escalation path is for each.

---

## Session 2 — 2026-03-27
Topic: Failure Modes (Section 2) + Structural Communication Rule
Status: COMPLETE
Decisions made:
  - STRUCTURAL RULE added: Human ↔ Claude only. Codex/Gemini write reports, Claude reads
    and interprets. Human never sees raw agent output. Claude is sole interface.
  - 8 failure modes defined (F1–F8) with recovery paths, retry limits, escalation
  - F4 (BLOCKED): Claude resolves if fix is in workflow files only. Nothing in core/api/formats/.
    No retry limit — BLOCKED is a question, not a failure.
  - F6 (Partial phase): No auto-revert. Human decides with exact options presented by Claude.
  - F7 (AC mismatch): 1 round only. Spec failure owned by Claude. Second failure = new task.
  - F2/F3: 3 rounds each. Terminal → Claude presents specific failure info to human.
  - F5 (Scope violation): Zero retries. Commit rejected by hook. Codex re-runs after scope fix.
  - F8 (Context loss): F8 appearing = G4/G5 violated. Fix the protocol, not the instance.
Open questions: none
Pick up next: Session 3 — Communication Protocol (Section 3)
  How agents exchange information. Replace markdown-prose IPC with structured, append-only,
  schema-enforced files. Define every file, its format, its owner, its lifecycle.

---

## Session 3 — 2026-03-28
Topic: Agent Capabilities (Section 0) + Skills
Status: COMPLETE
Decisions made:
  - Section 0 written: Codex capabilities, Gemini capabilities, MCP servers per agent
  - REVIEWER subagent pattern adopted (Section 0C): solves G2 elegantly within one Codex
    invocation. Reviewer has clean context, reads spec + implementation independently,
    returns structured JSON verdict before main agent can commit.
  - Gemini's 1M context window assigned to consistency-audit skill — reads full frontend
    in one pass, impossible for any other agent.
  - Gemini's save_memory tool assigned to save-design-decisions skill — eliminates
    re-reading standards files in every session.
  - Reports changed from markdown to JSON: agents/workflow/reports/TASK-XXX.json
  - 4 Codex skills created: pre-task, reviewer, commit-report, scope-guard
  - 3 Gemini skills created: consistency-audit, save-design-decisions, guide-quality
  - MCP servers confirmed: github, eslint, next-devtools, semgrep, python-lft,
    mcp-server-git, mcp-server-motherduck (replace current duckdb-mcp)
Open questions:
  - scope-guard.sh needs to be installed as a git hook during pipeline setup — add to
    Session 5 (State & Handoff) as a setup step
  - report-schema.json (for --output-schema flag) not yet written — needed before
    Codex can use structured JSON output. Add to Session 5.
Pick up next: Session 4 — Verification & Gate Layer (Section 4)
  Replace honor-system QA with: Reviewer subagent + gate sequence + structured output.
  Define exact gate scripts, what they check, how failures are reported.

---

## Session 4 — 2026-03-28
Topic: Verification & Gate Layer (Section 4)
Status: COMPLETE
Decisions made:
  - Full verification sequence: assertion → gates → Reviewer → commit. Order is fixed.
  - Gates run before Reviewer. Reviewer never reviews broken code.
  - 8 backend gates (added GATE5S semgrep-security, GATE5T python-type-check)
  - 4 frontend gates (added GATEF4 next-devtools live runtime check)
  - All gate output is JSON — feeds directly into TASK-XXX.json report
  - Baseline/delta rule: task cannot increase violation count. Pre-existing = allowed, new = FAIL.
  - Gate failure protocol: fix specific gate, re-run it, move on. Max 3 rounds per gate.
  - Reviewer position: after all gates PASS. Checks intent not structure.
  - Claude's post-call review: spot-check only. Primary QA is now automated.
  - report-schema.json structure defined — gates + reviewer + assertion all JSON
Open questions:
  - GATEF4 (next-devtools) requires dev server running. If not running it's SKIPPED.
    Claude must decide whether to require manual check. Acceptable trade-off for now.
  - Gate scripts (boundary-sentinel, duckdb-lint-ops, etc.) are existing scripts.
    Their output format needs updating to JSON. This is an implementation task, not a
    design decision — flag for Codex when pipeline is implemented.
Pick up next: Session 5 — State & Handoff Mechanism (Section 5)
  Replace 25-line prose handoff.md with structured, machine-readable state.
  Define every persistent file, its schema, its lifecycle, and setup steps
  (including scope-guard hook installation, report-schema.json).

---

## Session 5 — 2026-03-28
Topic: State & Handoff Mechanism (Section 5)
Status: COMPLETE
Decisions made:
  - handoff.md REPLACED by agents/workflow/state.json (structured JSON, 10 fields)
  - state.json written and seeded with TASK-165 as last completed
  - report-schema.json written to agents/workflow/report-schema.json (actual file, not just spec)
  - agents/workflow/reports/ directory created (append-only, permanent audit trail)
  - Session startup protocol defined: read state.json → check active task → load context → ready
    Replaces C0-C5 bootstrap. No soul files on every session. One file, one protocol.
  - Complete file system map defined: which files are permanent vs ephemeral vs active-only
  - Claude's changed behaviour summarised: reads JSON not prose, writes state.json not handoff.md,
    green signal requires schema-valid report not just prose COMPLETE
Open questions:
  - scope-guard.sh needs to be installed as actual git hook. Setup step documented.
    Will be done as first implementation task after Session 6.
  - Gate scripts (boundary-sentinel etc.) output format needs updating to JSON.
    Implementation task for Codex — not a design decision.
Pick up next: Session 6 — Agent Instructions (Section 6)
  Rewrite CLAUDE.md, AGENTS.md, GEMINI.md from scratch based on spec.
  These are the governing documents the agents actually read. Must reflect all decisions
  from Sessions 1-5 precisely. Short, structured, no redundancy across files.

---

## Session 6 — 2026-03-28
Topic: Agent Instructions (Section 6) — drafts written
Status: COMPLETE — AWAITING HUMAN APPROVAL BEFORE GOING LIVE
Decisions made:
  - new-CLAUDE.md: bootstrap reads state.json, invokes with --output-schema,
    green signal is a checklist not prose, small tweak rule narrowed
  - new-AGENTS.md: 6-phase execution (pre-task → implement → assertion → gates →
    reviewer → commit-report), new gate IDs, reports to TASK-XXX.json not report.md
  - new-GEMINI.md: 4 modes (design/guide/consistency-audit/save-design-decisions),
    JSON reports, guide-quality skill before gates, native tools referenced
  - All three files are SHORT (~80 lines each). Complexity is in skills + spec.
  - No redundancy across files — each agent reads one file, references spec for detail
Open questions: none — spec is complete
Next steps (in order, after human approval of drafts):
  1. Human reviews agents/redesign/new-CLAUDE.md, new-AGENTS.md, new-GEMINI.md
  2. On approval: replace live CLAUDE.md, AGENTS.md, GEMINI.md
  3. Install scope-guard pre-commit hook
  4. Update gate scripts to output JSON (Codex task)
  5. Archive handoff.md (git history — do not delete, just stop writing to it)
  6. Verify state.json and reports/ are tracked by git (not in .gitignore)

SPEC STATUS: ALL 6 SECTIONS COMPLETE
  Section 0: Agent capabilities + MCP servers + Reviewer subagent
  Section 1: 10 pipeline guarantees (G1-G10)
  Section 2: 8 failure modes (F1-F8) with resolution paths
  Section 3: Communication protocol (structural rule — human↔Claude only)
  Section 4: Verification + gate layer (gates → Reviewer → commit)
  Section 5: State + handoff (state.json replaces handoff.md)
  Section 6: Agent instructions (3 draft files awaiting approval)
