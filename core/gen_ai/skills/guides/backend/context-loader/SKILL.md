---
name: context-loader
description: Load startup context for Cricket platform tasks by reading SESSION_STATE, selecting scope-specific standards attachments, injecting a phase-awareness block, and flagging stale session state. Use this skill at task bootstrap whenever scope is backend, frontend, or architecture.
---

# Context Loader

Load required startup context before implementation begins. This skill reads session state, selects scope-specific standards attachments in deterministic order, injects phase-awareness guardrails, applies stale-state checks, and confirms readiness.

## Defaults

- Session source: `docs/ai/SESSION_STATE.md`
- Input: `task_scope` = `backend` | `frontend` | `architecture`
- Output: ordered file list + phase-awareness block + readiness confirmation
- Stale-state rule: warn when `Last Updated` is more than 7 days older than today's date

## Scripts

- `context-loader.md`
  - Prompt template for extracting current phase/task metadata
  - Scope-based attach mapping
  - Phase-awareness injection block
  - Stale-state warning output rule
  - Final context-loaded confirmation output

## Typical Usage

1. Invoke from Step 1 in a task prompt before any code changes.
2. Invoke from agent configuration bootstrap before task execution.

## Execution Rules

- MUST invoke for `backend`, `frontend`, and `architecture` tasks before coding.
- MUST parse `SESSION_STATE.md` for current phase, active task, priority queue top item, and blockers.
- MUST produce the ordered attach list for the given scope.
- MUST output the phase-awareness block.
- MUST output the stale warning before proceeding when session state age exceeds 7 days.
