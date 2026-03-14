# Architectural Mandates 1–4
# Part of: coreStandards
# Used by: all backend tasks, all frontend tasks
# NOT included: Mandates 5–6 (live layer — Phase 12 only, see MANDATES_5_6_LIVE.md)
# Source: ENGINEERING_STANDARDS_BACKEND.md Part 0 (authoritative)

**Core Directive:** "Assume data is dirty, boundaries are strict, and trust is zero."

---

## HOW TO READ THIS FILE

Before applying any mandate, you must first classify the file you are working on. Every file in this codebase has a **layer role** — a single primary responsibility that determines which mandates apply to it.

**How to classify any file — ask what its primary job is:**

| If the file's primary job is... | Its layer role is... | Mandates that apply |
|---|---|---|
| Performing calculations — taking data in, returning results out | **Domain Core** | Mandates 1, 2, 3, 4 |
| Mapping HTTP requests to domain functions, serializing responses | **Interface Adapter** | Mandates 2, 4 |
| Reading from or writing to the database | **Data Access** | Mandates 2, 4 |
| Rendering UI components, displaying data | **UI Adapter** | Mandate 4 |
| Extracting, transforming, or loading data into the database | **ETL Infrastructure** | Mandate 4 |
| Managing live match state, scraping, broadcasting live updates | **Live Layer** | Mandates 5, 6 |

**A file's layer role is determined by what it does — not where it lives.**

If a new file is added anywhere in the codebase that performs analytical calculations, it is a Domain Core file and Mandates 1, 2, 3, and 4 apply to it immediately — regardless of its directory path. The current project topology (which directories exist today) is documented in SYSTEM_TOPOLOGY.md. This file governs the principles. SYSTEM_TOPOLOGY.md maps those principles to the current structure. When the structure changes, SYSTEM_TOPOLOGY.md is updated. This file never changes.

---

## Mandate 1: Functional Core, Imperative Shell

**APPLIES TO:** Any file whose primary responsibility is analytical calculation. You can identify these files because they accept data structures (DataFrames, dicts, TypedDicts) as inputs and return computed results (primitives, TypedDicts, dataclasses) as outputs. They contain mathematical or statistical logic. They do not orchestrate, do not serve HTTP requests, and do not manage state.

**PRINCIPLE:**
A Domain Core file is a pure function at the architectural level. It takes data in. It returns data out. It has no memory of previous calls. It has no awareness of the outside world. Given identical inputs, it ALWAYS produces identical outputs. This is not a style preference — it is what makes the calculations testable, debuggable, and trustworthy in a trading context. You cannot trust a win probability produced by a function that also writes to a database, reads from a file, or depends on a global variable — because you cannot reproduce its output in isolation.

**What this means in practice:**
During the execution of any Domain Core function — from the moment it is called to the moment it returns — the function MUST NOT:
- Read from a database
- Write to a database
- Read from a file
- Write to a file
- Make a network request
- Access or modify a global variable
- Produce any output other than its return value
- Call any function that does any of the above

All data the function needs MUST arrive as parameters. All results MUST be returned explicitly. Nothing enters or leaves through side channels.

**VIOLATIONS — apply to any file with a Domain Core layer role:**
```python
# VIOLATION — queries database mid-calculation
def analyze_venue(self, venue: str) -> VenueReport:
    df = self.dal.get_matches(venue=venue)    # I/O inside Domain Core
    return self._calculate(df)

# VIOLATION — reads a file mid-calculation
def load_weights(self) -> Dict[str, float]:
    with open("weights.json") as f:           # File I/O inside Domain Core
        return json.load(f)

# VIOLATION — modifies global state as a side effect
def calculate_win_rate(self, df: pd.DataFrame) -> float:
    result = (df["winner"] == self.team).mean()
    GLOBAL_CACHE["last_result"] = result      # Global mutation inside Domain Core
    return result

# CORRECT — all data arrives as parameters, result returned explicitly
def analyze_venue(
    self,
    match_df: pd.DataFrame,
    venue: str
) -> VenueReport:
    filtered = match_df[match_df["venue"] == venue]
    return self._calculate(filtered)
```

**HARD STOP:** If you are working on a Domain Core file and it performs any I/O, reads any file, or touches any global variable during execution — stop the task immediately and report a Critical Boundary Violation before making any other change.

---

## Mandate 2: Hexagonal Purity (The Air Gap)

**APPLIES TO:** Any file whose layer role is Domain Core or Data Access. This mandate defines what these files are forbidden from knowing about.

**PRINCIPLE:**
The cricket domain — calculating a win probability, a player's economy rate, a venue bias — is completely blind to the infrastructure that surrounds it. A Domain Core file does not know whether it is being called by a FastAPI server, a Jupyter notebook, a unit test, or a command-line script. It does not know that DuckDB exists. It does not know that JSON exists. It speaks one language: DataFrames in, TypedDicts out.

This is the Hexagonal Architecture guarantee: you can swap the entire infrastructure — replace FastAPI with Flask, replace DuckDB with PostgreSQL, replace Next.js with Vue — and the domain core does not change by a single line. That guarantee is only maintained if the domain core is never allowed to import from the infrastructure layer.

**The Air Gap — data flows in one direction only:**
```
Infrastructure (api/, scripts/, frontend/)
        ↓  DataFrames and validated inputs flow inward
    Domain Core (engines, calculators, services)
        ↓  TypedDicts and primitives flow outward
Infrastructure (api/, scripts/, frontend/)
```

Nothing else crosses this boundary. No infrastructure object, no framework class, no database connection, no HTTP request or response ever enters the domain core.

**How to identify an infrastructure import:**
An import is an infrastructure import if the imported module has knowledge of how data is stored, served, rendered, or transmitted. If removing it would require knowing about the database engine, the web framework, the filesystem layout, or the network — it is an infrastructure import and it does not belong in a Domain Core file.

**VIOLATIONS — apply to any file with a Domain Core or Data Access layer role:**
```python
# VIOLATION — database framework imported in Domain Core
import duckdb                              # Database awareness
from sqlalchemy.orm import Session         # ORM awareness

# VIOLATION — web framework imported in Domain Core
from fastapi import HTTPException          # Framework awareness
import requests                            # Network awareness
from flask import request                  # Framework awareness

# VIOLATION — filesystem access in Domain Core
import os                                  # Filesystem awareness
from pathlib import Path                   # Filesystem awareness
import json                                # Acceptable only for data structures,
                                           # not for json.load(open(...)) patterns

# VIOLATION — API layer object passed into Domain Core
def analyze(self, request: Request) -> dict:   # FastAPI Request in domain
    team = request.json["team"]
    ...

# CORRECT — Domain Core imports only domain types and standard computation
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from core.interfaces.team_types import VenueReport, FormatRulesMap
from core.interfaces.player_interface import PlayerProfile
```

**HARD STOP:** Any infrastructure import found in a Domain Core file is a Critical Boundary Violation. Stop the task. Remove the import. Report the violation before proceeding with any other change.

---

## Mandate 3: Data-Oriented Design (DOD) — Hardware-Aware Computation

**APPLIES TO:** Any file that performs operations on collections of data — DataFrames, arrays, lists of records, or any structure containing more than one row. This includes Domain Core files, calculators, services, and any utility that processes tabular data.

**PRINCIPLE:**
How you write a calculation determines whether it runs in 2 milliseconds or 20 seconds on this hardware. On the Ryzen 5 3500U, a scalar Python loop over a DataFrame row-by-row is 10 to 100 times slower than the equivalent vectorized NumPy or Pandas operation — because scalar loops cannot use the CPU's SIMD instruction set or fill the L3 cache efficiently. In a trading tool where latency matters, this is not a style preference. It is a correctness requirement.

**Hardware reality — understand this before writing any calculation:**
The application runs on a Ryzen 5 3500U with approximately 4 GB of usable RAM after the operating system, IDE, and browser have taken their share. There is no cloud. There is no more RAM. Every calculation must be written with this constraint as a first-class concern — not as an afterthought.

**The core rule:**
Every operation that processes more than one row of data MUST be expressed as a vectorized operation using NumPy or Pandas. The CPU processes entire arrays in parallel using SIMD instructions. Python loops process one element at a time. These are not equivalent approaches with different syntax — they are fundamentally different execution models with a 10–100× performance difference on this hardware.

**How to identify a vectorization violation:**
A vectorization violation exists when you can see a Python `for` loop, `.iterrows()`, or `.itertuples()` being used to compute a result that could be expressed as a Pandas or NumPy operation across the whole array at once.

**VIOLATIONS — apply to any file performing tabular data operations:**
```python
# VIOLATION — scalar loop with row-by-row calculation
results = []
for index, row in df.iterrows():
    results.append(row["runs"] / row["balls"] * 100)
strike_rates = pd.Series(results)

# VIOLATION — itertuples is equally forbidden
for row in df.itertuples():
    if row.wickets > 3:
        high_impact.append(row.player)

# VIOLATION — manual index access in a loop
economy_rates = []
for i in range(len(df)):
    economy_rates.append(df.iloc[i]["runs"] / df.iloc[i]["overs"])

# CORRECT — vectorized arithmetic across the entire array simultaneously
strike_rates = (df["runs"] / df["balls"] * 100)

# CORRECT — boolean mask, no loop
high_impact = df[df["wickets"] > 3]["player"].tolist()

# CORRECT — vectorized column arithmetic
economy_rates = df["runs"] / df["overs"]
```

**The memory corollary:**
Vectorization and memory are linked. A scalar loop that builds a Python list and then converts it to a NumPy array creates two full copies of the data simultaneously. A vectorized operation works in-place on the existing array. On 4 GB of RAM, the difference between these two approaches can determine whether the application runs or crashes during a live session.

**HARD STOP:** Any `.iterrows()`, `.itertuples()`, or Python `for` loop used to compute a mathematical result that could be vectorized is a Critical Violation. Stop the task. Rewrite the operation as a vectorized expression. Do not add the loop and plan to fix it later.

---

## Mandate 4: Single Responsibility Principle (SRP) — One Reason to Change

**APPLIES TO:** Every file in the codebase without exception. SRP is not a Domain Core rule. It is a universal rule. It applies to API files, engine files, utility files, frontend components, ETL scripts, and test files equally.

**PRINCIPLE:**
A unit of code — whether a function, a class, or a file — has a Single Responsibility when you can describe its entire purpose without using the word "and."

If you find yourself saying "this function filters the data AND calculates the win rate" — that is two responsibilities. If you say "this file handles venue analysis AND player matching AND form calculation" — that is three responsibilities. Each "and" is a decomposition boundary that must be resolved before the code is considered complete.

**Why this matters beyond clean code:**
SRP is what makes this codebase survivable as it grows. A function with one responsibility has one reason to change. A function with three responsibilities has three reasons to change — and every change to one responsibility risks breaking the other two. In a trading tool that will expand to multiple formats and live match analysis, functions that do too many things become unmaintainable faster than any other form of technical debt.

**The decomposition hierarchy — apply at the correct level:**

| What you observe | What it means | How to fix it |
|---|---|---|
| A function does two things | Function-level SRP violation | Split into two private methods in the same class |
| A class manages two concerns | Class-level SRP violation | Split into two classes |
| An engine handles two analytical domains | Module-level SRP violation | Extract one domain into a dedicated Calculator class |
| A file has three or more domains | File-level SRP violation | Split into multiple files, each owning one domain |

**The 30-line rule — understood correctly:**
The engineering standards state that a function exceeding 30 lines MUST be decomposed. This is a heuristic — a reliable warning sign — not the definition of SRP itself. A function that exceeds 30 lines is almost always doing more than one thing. But the question to ask is not "is this function over 30 lines?" — it is "can I describe this function's purpose without using the word 'and'?" If yes and it happens to be 35 lines, document the justification. If no and it is only 20 lines, decompose it anyway — because SRP is about responsibility, not line count.

**The file-size corollary:**
A file exceeding 500 lines is a warning. A file exceeding 800 lines is a violation requiring decomposition before new features are added. The correct decomposition at the file level is to extract focused Calculator classes, each owning one analytical domain — for example: `VenueCalculator`, `FormCalculator`, `MatchupCalculator`, `PhaseCalculator`.

**VIOLATIONS — apply to every file in the codebase:**
```python
# VIOLATION — function does two things (filtering AND calculating)
def get_venue_win_rate(
    self, match_df: pd.DataFrame, venue: str
) -> float:
    # Responsibility 1: filter
    venue_df = match_df[match_df["venue"] == venue]
    home_df = venue_df[venue_df["team_bat_1"] == self.team]
    # Responsibility 2: calculate
    wins = (home_df["winner"] == self.team).sum()
    return wins / len(home_df) if len(home_df) > 0 else 0.0

# CORRECT — one function, one responsibility
def _filter_venue_matches(
    self, match_df: pd.DataFrame, venue: str
) -> pd.DataFrame:
    venue_df = match_df[match_df["venue"] == venue]
    return venue_df[venue_df["team_bat_1"] == self.team]

def _calculate_win_rate(self, df: pd.DataFrame) -> float:
    if len(df) == 0:
        return 0.0
    return (df["winner"] == self.team).sum() / len(df)

def get_venue_win_rate(
    self, match_df: pd.DataFrame, venue: str
) -> float:
    filtered = self._filter_venue_matches(match_df, venue)
    return self._calculate_win_rate(filtered)
```

**HARD STOP:** Any new function submitted for review that cannot be described without using the word "and" is rejected without exception. Decompose it first, then submit.

---

*Part of coreStandards — load alongside SYSTEM_TOPOLOGY.md for full architectural context.*
*Authoritative source: ENGINEERING_STANDARDS_CORE.md*
