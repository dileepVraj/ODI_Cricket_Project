F01 — Structural Map + Directory Classification
Read the following files before doing anything else:

ENGINEERING_STANDARDS_FRONTEND.md (full)
PROJECT_CONTEXT.md sections 6 and 7
SESSION_STATE.md

TASK: Produce a structural map of the frontend codebase. This is a read-only classification step. Zero code changes.
Step 1 — Inventory
List every file under frontend/ recursively. For each file record:

File path (relative to frontend/)
Layer role (UI Adapter / ETL Infrastructure / other — classify per Part 0 of the standards)
Primary responsibility in one sentence

Step 2 — Directory Contract Audit
The directory contract (2.2B Rule 10) specifies four directories:

components/layout/ — navigation, shell, bars
components/renderers/ — output renderers + FunctionRenderer dispatcher
components/inputs/ — squad builders, extra input fields, forms
components/common/ — shared primitives used by multiple layers

For every component file found, record which directory it currently lives in and whether that placement is COMPLIANT or VIOLATION against the contract. Flag any directories that exist but are not in the contract (e.g. navigation/, animations/).
Step 3 — File Count Summary
Produce a count table:

Total files by directory
Total components by layer role
Any file over 300 lines (flag name + line count)
Any file over 500 lines (flag as WARNING)
Any file over 800 lines (flag as VIOLATION)


CONSTRAINTS

Zero code changes
Do not open or read file contents beyond what is needed to classify and count
Do not run any compliance gates — that is F02 onwards
Do not infer violations beyond directory placement and file size at this step


REPORT FORMAT
Return exactly this structure:

F01 — STRUCTURAL MAP
=====================

INVENTORY TABLE
[file | layer role | responsibility]

DIRECTORY CONTRACT AUDIT
[file | current directory | COMPLIANT / VIOLATION / UNCLASSIFIED]

ANOMALOUS DIRECTORIES
[directory | files contained | contract status]

FILE SIZE FLAGS
[file | line count | WARNING / VIOLATION]

SUMMARY
Total files: N
COMPLIANT placements: N
VIOLATIONS: N
UNCLASSIFIED: N
Size warnings: N
Size violations: N
F01 STATUS: COMPLETE

