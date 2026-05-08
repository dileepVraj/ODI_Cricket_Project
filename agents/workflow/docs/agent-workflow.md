# Agent Workflow

Use this flow every time you start a task.

1. Identify the file area.
   - `frontend/` means use the frontend worktree.
   - `api/`, `core/`, `cockpit/`, `config/`, `formats/`, `tests/`, `scripts/` mean use the backend worktree.
   - `agents/`, `docs/`, `plans/`, `.claude/`, and repo instructions mean use the docs worktree at the repo root.

2. Open the matching worktree before editing.
   - Backend: `C:\Vantage\.worktrees\backend`
   - Frontend: `C:\Vantage\.worktrees\frontend`
   - Docs or workflow: `C:\Vantage`
   - Stable branch work: `C:\Vantage\.worktrees\main`

3. Make only the files for that area.
   - Do not mix backend and frontend changes in one commit unless the task clearly needs both.
   - Keep local junk out of commits.

4. Commit from the worktree you opened.
   - The branch is chosen by the folder you are in.
   - Git does not auto-route files by path.

5. If a task spans more than one area, split it.
   - Make one commit per worktree.
   - Keep each commit small and easy to review.

6. Before pushing, check the worktree status.
   - Clean worktree means the branch is ready.
   - Dirty worktree means something still needs attention.
