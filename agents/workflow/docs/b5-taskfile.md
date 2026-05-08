# B5 — TaskFile Protocol

Write `agents/workflow/taskFile.md` per `agents/workflow/taskFileTemplate.md`.
For calculator/engine/service tasks: Verification Matrix must be fully filled before
writing the taskFile. Blank cells = task not ready. Do not assign.

## Assertion Script (calculator/engine/service tasks only)

Write `agents/workflow/assertion.py` BEFORE the taskFile.
This is a Claude action — not a shell command, not Codex.

Source: the Verification Matrix concrete example column only.
Do not consult the codebase. Do not read the function being implemented.
The assertion must encode what the matrix says, not what the code will do.

Translation: one row → one assert block:
```python
# THROWAWAY — delete after task complete. Written by Claude, run by Codex.
# Task: <TASK-ID> | Field: <field_name>
# Matrix row: <concrete input> → <expected output>
from <module> import <function>
result = <function>(<concrete_input>)
assert result["<field>"] == <expected_value>, f"ASSERTION FAILED: expected <expected_value>, got {result['<field>']}"
print("ASSERTION PASSED:", result)
```

Write the taskFile only after assertion.py is saved.
Codex does not rewrite assertion.py — if it is missing, Codex blocks.

Confirm with human before invoking.
