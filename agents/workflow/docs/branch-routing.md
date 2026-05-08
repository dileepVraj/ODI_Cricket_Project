# Branch Routing

Use the worktree folder that matches the kind of files you are changing.

## Folders

- `C:\Vantage\.worktrees\backend` for backend code:
  - `api/`
  - `cockpit/`
  - `config/`
  - `core/`
  - `formats/`
  - `tests/`
  - `scripts/`

- `C:\Vantage\.worktrees\frontend` for frontend code:
  - `frontend/`

- `C:\Vantage` for repo workflow and agent docs:
  - `agents/`
  - `docs/`
  - `plans/`
  - `.claude/`
  - `AGENTS.md`
  - `CLAUDE.md`
  - `GEMINI.md`

- `C:\Vantage\.worktrees\main` for stable branch work:
  - only when the task is meant for `main`

## Rule Of Thumb

If a task touches only one area, work in that folder and commit from there.

If a task touches more than one area, split it into separate tasks and commit each part from the matching worktree.

## What Git Does

Git does not auto-pick a branch from a file path.
The branch is chosen by the folder you are working in.

## Safe Default

When unsure:

1. Check which folder the files belong to.
2. Open the matching worktree.
3. Make the changes there.
4. Commit from that folder.
