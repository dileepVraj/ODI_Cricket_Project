# Team Engine Compliance Audit - Final Report
**File Audited:** `formats/odi/engines/team_engine.py`
**Audit Series:** AUDIT-01 through AUDIT-05
**Date:** 2026-03-05
**Conducted By:** AI Audit Agent
**Reviewed By:** Architect

---

## Section 1 - Audit Overview

| Audit | Scope | Status |
|-------|-------|--------|
| AUDIT-01 | Baseline bouncer run | COMPLETE |
| AUDIT-02 | Layer classification | COMPLETE |
| AUDIT-03 | Mandate compliance - Part 0 | COMPLETE |
| AUDIT-04 | Topology compliance - Part 1 | COMPLETE |
| AUDIT-05 | Final report assembly | COMPLETE |

---

## Section 2 - File Classification

**Layer Role:** Domain Core / Concrete Strategy
**Applicable Mandates:** M1, M2, M3, M4
**Derived Laws In Scope:**
  Zero-Literal, Derivative Literal,
  Visual Silence, Anti-Grease, I/O Air-Gap
**Classification Conflict:** NO

---

## Section 3 - Baseline Bouncer Result

**Result:** PASS
**Violations Detected by Bouncer:** 0
**Interpretation:** The engine passes all
10 mechanical compliance rules. Deeper
audit required for full Part 0 and Part 1
compliance - bouncer is a floor, not a
ceiling.

---

## Section 4 - Mandate Compliance (Part 0)

### 4.1 Summary Table

| Mandate / Law               | Verdict | Violations |
|-----------------------------|---------|------------|
| M1 - Functional Core        | PASS    |     0      |
| M2 - Hexagonal Purity       | PASS    |     0      |
| M3 - DOD                    | PASS    |     0      |
| M4 - SRP                    | PASS    |     0      |
| Zero-Literal Law            | FAIL    |     1      |
| Derivative Literal Law      | PASS    |     0      |
| Visual Silence Law          | PASS    |     0      |
| Anti-Grease Law             | PASS    |     0      |
| I/O Air-Gap Law             | PASS    |     0      |

### 4.2 Violation Detail

### [VIOLATION-001]
**Mandate / Law:** Zero-Literal Law
**Severity:** MEDIUM
**Line(s):** 91
**Code Snippet:**
`if isinstance(value, (list, tuple)) and len(value) >= 2:`
**Why it fails:** Uses raw numeric literal `2` in Domain Core logic without named manifest-backed constant.

### 4.3 False Positives

#### [FP-001] - Zero-Literal Law
**Line:** 91
**Code:** `if isinstance(value, (list, tuple)) and len(value) >= 2:`
**Flagged As:** Zero-Literal violation - raw integer `2` in Domain Core
**Dismissed Because:** This is a structural guard clause verifying minimum tuple
  unpackability. The integer `2` carries no
  cricket domain meaning - it is not a
  tactical window, match limit, year
  threshold, or fallback value. The
  Zero-Literal Law targets domain constants
  only. Structural integer guards of this
  kind are explicitly exempt.
**Architect Decision:** DISMISSED - 2026-03-05
**Pattern Note:** Future agents auditing
  engine files should apply this same
  exemption to structural guard clauses
  using small integers (>= 2, > 1 etc.)
  where the integer has no cricket domain
  meaning. Do not re-raise this pattern
  as a violation.

---

## Section 5 - Topology Compliance (Part 1)

### 5.1 Summary Table

| Check                        | Verdict | Violations |
|------------------------------|---------|------------|
| Layer Map - Directory        | PASS    |     0      |
| Layer Map - Responsibility   | PASS    |     0      |
| Paradigm 1 - Manifest Sync   | PASS    |     0      |
| Paradigm 2 - DAL Fortress    | PASS    |     0      |
| Paradigm 3 - ABC Contract    | FAIL    |     11     |
| Paradigm 3 - Format Defaults | PASS    |     0      |
| Paradigm 4 - ETL Immutability| PASS    |     0      |
| Paradigm 5 - Pre-Computed    | PASS    |     0      |
| Import Organisation          | PASS    |     0      |

### 5.2 Violation Detail

### [VIOLATION-T001]
**Paradigm / Check:** Paradigm 3 - ABC Contract (`analyze_home_fortress`)
**Severity:** HIGH
**Line(s):** `core/interfaces/team_interface.py:100`, `formats/odi/engines/team_engine.py:139`
**Code Snippet:**
`ABC: (self, stadium_name: str, home_team: str, opp_team: str = 'All', years_back: int = 10, recorder: Any = None, match_context: Optional[core.interfaces.team_interface.MatchContext] = None) -> List[Dict[str, Any]]`
`CON: (self, stadium_name: 'str', home_team: 'str', opp_team: 'str' = 'All', years_back: 'int' = 0, recorder: 'Optional[RecorderPort]' = None, match_context: 'Optional[TeamMatchContext]' = None) -> 'ComparisonReportRows'`
**Why it fails:** Abstract signature and concrete signature are not exact matches (default values and type contract differ).

### [VIOLATION-T002]
**Paradigm / Check:** Paradigm 3 - ABC Contract (`analyze_venue_matchup_structured`)
**Severity:** HIGH
**Line(s):** `core/interfaces/team_interface.py:113`, `formats/odi/engines/team_engine.py:166`
**Code Snippet:**
`ABC: (self, stadium_name: str, home_team: str, opp_team: str, years_back: int = 5, match_context: Optional[core.interfaces.team_interface.MatchContext] = None) -> core.interfaces.team_interface.MatchIntelligenceData`
`CON: (self, stadium_name: 'str', home_team: 'str', opp_team: 'str', years_back: 'int' = 0, match_context: 'Optional[TeamMatchContext]' = None) -> 'VenueMatchupReport'`
**Why it fails:** Abstract signature and concrete signature are not exact matches (default value and return type differ).

### [VIOLATION-T003]
**Paradigm / Check:** Paradigm 3 - ABC Contract (`analyze_venue_phases`)
**Severity:** HIGH
**Line(s):** `core/interfaces/team_interface.py:125`, `formats/odi/engines/team_engine.py:193`
**Code Snippet:**
`ABC: (self, stadium_id: str, home_team: Optional[str] = None, away_team: Optional[str] = None, years: int = 5, recorder: Any = None, match_context: Optional[core.interfaces.team_interface.MatchContext] = None) -> Dict[str, Any]`
`CON: (self, stadium_id: 'str', home_team: 'Optional[str]' = None, away_team: 'Optional[str]' = None, years: 'int' = 0, recorder: 'Optional[RecorderPort]' = None, match_context: 'Optional[TeamMatchContext]' = None) -> 'VenuePhasesReport'`
**Why it fails:** Abstract signature and concrete signature are not exact matches (default value and type contract differ).

### [VIOLATION-T004]
**Paradigm / Check:** Paradigm 3 - ABC Contract (`analyze_venue_bias`)
**Severity:** HIGH
**Line(s):** `core/interfaces/team_interface.py:138`, `formats/odi/engines/team_engine.py:223`
**Code Snippet:**
`ABC: (self, stadium_name: str, years_back: int = 10, recorder: Any = None, match_context: Optional[core.interfaces.team_interface.MatchContext] = None) -> Optional[Dict[str, Any]]`
`CON: (self, stadium_name: 'str', years_back: 'int' = 0, recorder: 'Optional[RecorderPort]' = None, match_context: 'Optional[TeamMatchContext]' = None) -> 'Optional[VenueBiasReport]'`
**Why it fails:** Abstract signature and concrete signature are not exact matches (default value and return type differ).

### [VIOLATION-T005]
**Paradigm / Check:** Paradigm 3 - ABC Contract (`analyze_global_h2h`)
**Severity:** HIGH
**Line(s):** `core/interfaces/team_interface.py:149`, `formats/odi/engines/team_engine.py:248`
**Code Snippet:**
`ABC: (self, home_team: str, opp_team: str, years_back: int = 5, match_context: Optional[core.interfaces.team_interface.MatchContext] = None) -> Dict[str, Any]`
`CON: (self, home_team: 'str', opp_team: 'str', years_back: 'int' = 0, match_context: 'Optional[TeamMatchContext]' = None) -> 'ComparisonReportRows'`
**Why it fails:** Abstract signature and concrete signature are not exact matches (default value and return type differ).

### [VIOLATION-T006]
**Paradigm / Check:** Paradigm 3 - ABC Contract (`analyze_country_h2h`)
**Severity:** HIGH
**Line(s):** `core/interfaces/team_interface.py:160`, `formats/odi/engines/team_engine.py:270`
**Code Snippet:**
`ABC: (self, home_team: str, opp_team: str = 'All', country_name: Optional[str] = None, years_back: int = 10, recorder: Optional[Any] = None, match_context: Optional[core.interfaces.team_interface.MatchContext] = None) -> List[Dict[str, Any]]`
`CON: (self, home_team: 'str', opp_team: 'str' = 'All', country_name: 'Optional[str]' = None, years_back: 'int' = 0, recorder: 'Optional[RecorderPort]' = None, match_context: 'Optional[TeamMatchContext]' = None) -> 'ComparisonReportRows'`
**Why it fails:** Abstract signature and concrete signature are not exact matches (default value and return type differ).

### [VIOLATION-T007]
**Paradigm / Check:** Paradigm 3 - ABC Contract (`analyze_home_dominance`)
**Severity:** HIGH
**Line(s):** `core/interfaces/team_interface.py:173`, `formats/odi/engines/team_engine.py:296`
**Code Snippet:**
`ABC: (self, home_team: str, years_back: int = 10, recorder: Optional[Any] = None, match_context: Optional[core.interfaces.team_interface.MatchContext] = None) -> List[Dict[str, Any]]`
`CON: (self, home_team: 'str', years_back: 'int' = 0, recorder: 'Optional[RecorderPort]' = None, match_context: 'Optional[TeamMatchContext]' = None) -> 'MatrixReportRows'`
**Why it fails:** Abstract signature and concrete signature are not exact matches (default value and return type differ).

### [VIOLATION-T008]
**Paradigm / Check:** Paradigm 3 - ABC Contract (`analyze_away_performance`)
**Severity:** HIGH
**Line(s):** `core/interfaces/team_interface.py:184`, `formats/odi/engines/team_engine.py:318`
**Code Snippet:**
`ABC: (self, team_name: str, years_back: int = 5, recorder: Optional[Any] = None, match_context: Optional[core.interfaces.team_interface.MatchContext] = None) -> List[Dict[str, Any]]`
`CON: (self, team_name: 'str', years_back: 'int' = 0, recorder: 'Optional[RecorderPort]' = None, match_context: 'Optional[TeamMatchContext]' = None) -> 'MatrixReportRows'`
**Why it fails:** Abstract signature and concrete signature are not exact matches (default value and return type differ).

### [VIOLATION-T009]
**Paradigm / Check:** Paradigm 3 - ABC Contract (`analyze_global_performance`)
**Severity:** HIGH
**Line(s):** `core/interfaces/team_interface.py:195`, `formats/odi/engines/team_engine.py:340`
**Code Snippet:**
`ABC: (self, team_name: str, years_back: int = 5, match_context: Optional[core.interfaces.team_interface.MatchContext] = None) -> List[Dict[str, Any]]`
`CON: (self, team_name: 'str', years_back: 'int' = 0, match_context: 'Optional[TeamMatchContext]' = None) -> 'MatrixReportRows'`
**Why it fails:** Abstract signature and concrete signature are not exact matches (default value and return type differ).

### [VIOLATION-T010]
**Paradigm / Check:** Paradigm 3 - ABC Contract (`analyze_continent_performance`)
**Severity:** HIGH
**Line(s):** `core/interfaces/team_interface.py:205`, `formats/odi/engines/team_engine.py:359`
**Code Snippet:**
`ABC: (self, team_name: str, continent: str, opp_team: str = 'All', years_back: int = 5, match_context: Optional[core.interfaces.team_interface.MatchContext] = None) -> List[Dict[str, Any]]`
`CON: (self, team_name: 'str', continent: 'str', opp_team: 'str' = 'All', years_back: 'int' = 0, match_context: 'Optional[TeamMatchContext]' = None) -> 'MatrixReportRows | ComparisonReportRows'`
**Why it fails:** Abstract signature and concrete signature are not exact matches (default value and return type differ).

### [VIOLATION-T011]
**Paradigm / Check:** Paradigm 3 - ABC Contract (`analyze_team_form`)
**Severity:** HIGH
**Line(s):** `core/interfaces/team_interface.py:217`, `formats/odi/engines/team_engine.py:383`
**Code Snippet:**
`ABC: (self, team_name: str, opp_team: str = 'All', continent: str = 'All', limit: int = 5, recorder: Any = None, match_context: Optional[core.interfaces.team_interface.MatchContext] = None) -> List[Dict[str, Any]]`
`CON: (self, team_name: 'str', opp_team: 'str' = 'All', continent: 'str' = 'All', limit: 'int' = 0, recorder: 'Optional[RecorderPort]' = None, match_context: 'Optional[TeamMatchContext]' = None) -> 'TeamFormRows'`
**Why it fails:** Abstract signature and concrete signature are not exact matches (default value and return type differ).

### 5.3 ABC Contract Verification

| Abstract Method | Implemented | Signature Match |
|-----------------|-------------|-----------------|
| analyze_home_fortress | YES | NO |
| analyze_venue_matchup_structured | YES | NO |
| analyze_venue_phases | YES | NO |
| analyze_venue_bias | YES | NO |
| analyze_global_h2h | YES | NO |
| analyze_country_h2h | YES | NO |
| analyze_home_dominance | YES | NO |
| analyze_away_performance | YES | NO |
| analyze_global_performance | YES | NO |
| analyze_continent_performance | YES | NO |
| analyze_team_form | YES | NO |

### 5.4 Manifest Sync Verification

| Engine Method   | In Manifest | Signature Match |
|-----------------|-------------|-----------------|
| analyze_home_fortress | YES | YES |
| analyze_venue_matchup_structured | YES | YES |
| analyze_venue_phases | YES | YES |
| analyze_venue_bias | YES | YES |
| analyze_global_h2h | YES | YES |
| analyze_country_h2h | YES | YES |
| analyze_home_dominance | YES | YES |
| analyze_away_performance | YES | YES |
| analyze_global_performance | YES | YES |
| analyze_continent_performance | YES | YES |
| analyze_team_form | YES | YES |

---

## Section 6 - Combined Findings Summary

| Category              | Count |
|-----------------------|-------|
| Bouncer violations    |   0   |
| Part 0 violations     |   1   |
| Part 1 violations     |   11  |
| False positives       |   1   |
| **Total real violations** | **11** |

### Severity Breakdown

| Severity | Part 0 | Part 1 | Total |
|----------|--------|--------|-------|
| CRITICAL |   0    |   0    |   0   |
| HIGH     |   0    |   11   |   11  |
| MEDIUM   |   1    |   0    |   1   |
| **Total**|   1    |   11   |   12  |

---

## Section 7 - Architect Decisions Log

| Decision | Detail | Date |
|----------|--------|------|
| FP-001 dismissed | len(value) >= 2 is structural guard, not domain constant | 2026-03-05 |
| ABC is stale | Engine return types are more advanced - ABC must be updated to match engine, not vice versa | 2026-03-05 |
| Refactor scope | Only `core/interfaces/team_interface.py` in scope - not team_types.py, not team_engine.py | 2026-03-05 |
| Stale dataclasses | VenueStats, TeamMatchup, FormGuide, TeamVenueStats, MatchIntelligenceData must be zero-reference checked before removal | 2026-03-05 |

---

## Section 8 - Refactor Readiness

**Overall Compliance:** NON-COMPLIANT
**Blocker Count (CRITICAL):** 0
**High Severity Count:** 11
**Root Cause:** ABC contract in
  `core/interfaces/team_interface.py` is
  stale - all 11 HIGH violations are
  signature mismatches where the engine
  has evolved beyond the ABC definition.

**Single Refactor Task Required:**
  Update `core/interfaces/team_interface.py`
  to match the engine's current typed
  signatures. The engine is the source
  of truth. The ABC must catch up.

**Pre-Refactor Checks Required:**
  1. Zero-reference check on all stale
     dataclasses before removal
  2. Stop-state-trace-confirm before
     touching any file in core/interfaces/
  3. Post-refactor bouncer pass required
     on formats/odi/engines/team_engine.py

**Estimated Impact:** LOW - changes are
  additive type improvements. No logic
  changes. No behaviour changes.

---

## Section 9 - Audit Status
**AUDIT-05:** COMPLETE
**Audit Series:** CLOSED
**Next Action:** Refactor task for
  `core/interfaces/team_interface.py`

## Section 10 — Architect Observations

These are NOT violations. They are documented
behaviours that are architecturally intentional.
Future agents MUST NOT treat these as bugs
or attempt to fix them.

---

### [OBS-001] — Constructor silently discards
match_df, phase_df, dal parameters
**File:** `formats/odi/engines/team_engine.py`
**Line:** 26
**Code:**
`_ = (match_df, phase_df, dal)`
**What it looks like:** Three constructor
  parameters are accepted then immediately
  discarded.
**Why it is correct:** The engine is stateless
  by design. All data arrives per-request via
  `match_context` — not at construction time.
  The parameters are accepted to maintain a
  consistent constructor interface across
  engine implementations. Discarding them
  is intentional — not an oversight.
**Do NOT:** Remove the parameters, add
  assignment logic, or raise warnings about
  unused arguments.
**Architect sign-off:** 2026-03-05

---

### [OBS-002] — _context_match_df called in
_context_reference_date but not visible in
upper file section
**File:** `formats/odi/engines/team_engine.py`
**Line:** 51
**Code:**
`return self._compute_reference_date(
    self._context_match_df(match_context))`
**What it looks like:** Method
  `_context_match_df` is called but not
  defined in the visible portion of the file
  (lines 1-95).
**Why it is correct:** The method is defined
  in the truncated section of the file
  (lines 178-228 were not visible during
  architect review). This is a standard
  private helper method — its absence from
  the visible section is a file truncation
  artefact, not a missing method.
**Do NOT:** Add a duplicate definition of
  `_context_match_df` or raise a missing
  method error without first checking the
  full file.
**Architect sign-off:** 2026-03-05