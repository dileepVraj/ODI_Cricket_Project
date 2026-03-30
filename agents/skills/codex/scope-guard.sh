#!/bin/bash
# scope-guard — pre-commit hook
# Reads agents/workflow/scope.json and rejects commits touching out-of-scope files

SCOPE_FILE="agents/workflow/scope.json"

# If no scope.json exists, no active task — allow commit (human commits always pass)
if [ ! -f "$SCOPE_FILE" ]; then
  exit 0
fi

# Get staged files
STAGED=$(git diff --cached --name-only)

# Extract allowed files from scope.json
ALLOWED=$(python3 -c "
import json, sys
with open('$SCOPE_FILE') as f:
    data = json.load(f)
for p in data.get('allowed_files', []):
    print(p)
")

# Check each staged file against allowed list
VIOLATIONS=()
while IFS= read -r file; do
  if [ -z "$file" ]; then continue; fi
  FOUND=false
  while IFS= read -r allowed; do
    if [ "$file" = "$allowed" ]; then
      FOUND=true
      break
    fi
  done <<< "$ALLOWED"
  if [ "$FOUND" = false ]; then
    VIOLATIONS+=("$file")
  fi
done <<< "$STAGED"

# Also always allow workflow files (reports, scope.json itself)
# and tests/contracts/ — contract files graduated from assertion.py by commit-report skill
FINAL_VIOLATIONS=()
for v in "${VIOLATIONS[@]}"; do
  if [[ "$v" != agents/workflow/* ]] && [[ "$v" != tests/contracts/* ]]; then
    FINAL_VIOLATIONS+=("$v")
  fi
done

if [ ${#FINAL_VIOLATIONS[@]} -gt 0 ]; then
  echo ""
  echo "SCOPE GUARD — COMMIT REJECTED"
  echo "The following files are not in agents/workflow/scope.json:"
  for v in "${FINAL_VIOLATIONS[@]}"; do
    echo "  - $v"
  done
  echo ""
  echo "If scope needs to expand: Claude updates scope.json and re-authorises."
  echo "Task ID: $(python3 -c \"import json; d=json.load(open('$SCOPE_FILE')); print(d.get('task_id','unknown'))\")"
  echo ""
  exit 1
fi

exit 0
