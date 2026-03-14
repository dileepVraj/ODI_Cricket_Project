# Known Intentional Patterns (KIPs)
# Part of: backendStandards
# Load for: any task touching formats/odi/engines/team_engine.py ONLY
# Do NOT load for unrelated engine tasks — these KIPs are file-specific
# Source: ENGINEERING_STANDARDS_BACKEND.md Part 7 (authoritative)

---

## PART 7: KNOWN INTENTIONAL PATTERNS — DO NOT FIX

These are documented behaviours in engine files that are architecturally intentional. They may look like bugs or oversights to a static analyser or an agent reading the code for the first time. They are not. Do not modify, remove, or work around them.

---

### [KIP-001] Constructor parameter discard in TeamEngine

**File:** `formats/odi/engines/team_engine.py`
**Line:** 26
**Code:** `_ = (match_df, phase_df, dal)`

**What it looks like:** Three constructor parameters accepted then immediately discarded.

**Why it is correct:** The engine is stateless by design. All data arrives per-request via `match_context`. The parameters exist to maintain a consistent constructor interface across all engine implementations. Discarding them is intentional.

**Hard Stop:** Do NOT remove the discard pattern. Do NOT assign or store these parameters. Do NOT raise warnings about unused arguments.

---

### [KIP-002] _context_match_df called before its visible definition

**File:** `formats/odi/engines/team_engine.py`
**Line:** 51
**Code:** `return self._compute_reference_date(self._context_match_df(match_context))`

**What it looks like:** Method `_context_match_df` is called in the upper section of the file but its definition is not visible nearby.

**Why it is correct:** The method is defined in the lower section of the same file. This is a file layout choice — not a missing method. Python resolves instance methods at call time, not at definition order.

**Hard Stop:** Do NOT add a duplicate definition of `_context_match_df` in the upper section of the file. Do NOT raise a missing method error without first reading the complete file.

---

*Part of backendStandards — load ONLY when task touches formats/odi/engines/team_engine.py.*
*Authoritative source: ENGINEERING_STANDARDS_BACKEND.md Part 7*
