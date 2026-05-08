# State.json Write Protocol

Every write to `agents/workflow/state.json` — whether active block, green signal, or abandon —
must follow this sequence. No exceptions.

## Step 1 — Backup current state
Before writing anything, copy the current contents of state.json to `state.json.bak`:
Read state.json → write identical contents to `agents/workflow/state.json.bak`.
If state.json does not exist yet (first run) → skip backup, proceed to write.

## Step 2 — Write new state
Write the updated state.json with the full file contents (not a partial patch).
Always include all fields. Never write a partial JSON object.

## Step 3 — Verify write
Read state.json back immediately after writing.
Confirm it parses as valid JSON and `schema_version` is present.
If verification fails → restore from state.json.bak and inform human.
