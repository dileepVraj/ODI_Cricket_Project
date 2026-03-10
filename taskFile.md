I want to do a full project cleanup — go through every directory in 
C:\Cricket_Project_Stable and identify files that are unnecessary, 
redundant, or no longer serving any purpose.

I want you to AUDIT ONLY first — do not delete or modify anything.

Produce a report organised by directory listing:
1. Files that are safe to delete (with reason why)
2. Files that are uncertain (need architect review before touching)
3. Files that must stay (core to the project)

Rules:
- Do NOT touch anything under frontend/node_modules/
- Do NOT touch anything under .git/
- Do NOT touch any file in docs/ai/ — that is human-write-only
- Do NOT delete any file during this audit — read only
- Flag any file that looks like dead scaffolding, 
  temp output, duplicate, or orphaned script
- Cross-reference against imports and usages before 
  flagging anything as deletable — do not flag a file 
  as unused without checking if something imports it

Produce the report as a structured markdown document. 
Do not make any changes until I review and approve the report.