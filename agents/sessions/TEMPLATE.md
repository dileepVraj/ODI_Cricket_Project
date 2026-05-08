# Session Notes Template
**Reference file — not a real session. Shows all section types and rules.**

---

## Plan: TASK-XXX — short description
**Status:** PENDING
**What:** One sentence describing what the plan covers.
**Key decisions:**
- Non-obvious choice #1 and why
- Non-obvious choice #2 and why
**Plan file:** `agents/plans/<filename>.md`
**Next:** Write taskFile for TASK-XXX

---

## Task: TASK-XXX — short description
**Status:** DONE
**What:** One sentence describing what was implemented.
**Commit:** `abc1234` — commit message here
**Gate state:** GATE5P PASS | violations_delta: 0
**Next:** TASK-XXX or idle

---

## Discussion: topic title
**Status:** DONE
**What:** One sentence describing what was discussed.
**Key decisions:**
- Decision or conclusion #1
- Decision or conclusion #2
**Next:** Action item, or "none"

---

## Carry-Forward: original section name
**Carried from:** YYYY-MM-DD
**Status:** PENDING  ← (or IN PROGRESS)
[Full content of the section copied from the previous day's file]

---

# Rules (read before writing any section)

1. One file per calendar day — `agents/sessions/YYYY-MM-DD.md`
2. Append new sections — never rewrite the whole file
3. Max 10 lines per section — no walls of text
4. DONE sections stay as historical record — never carried forward
5. PENDING and IN PROGRESS sections are carried forward in full to the next day's file
6. After writing any section, output one line: `> Session notes updated.`
7. Write only after human confirms (plan approval, discussion conclusion)
   Exception: Task sections after B8 green signal are written automatically
