# 🤖 GEMINI Agent Protocols & Governance

This document defines the **Behavioral & Operational Rules** for the AI Agent (Gemini) working on the Cricket Algo-Trader project.
It complements `docs/guides/DEV_GUIDE.md` (Technical Arch) by defining *HOW* the Agent should work.

---

## 🧠 1. The "Living Memory" Protocol (CRITICAL)

The `docs/ai/AI_MEMORY.md` file is your brain. If you don't update it, you have amnesia.

### 📜 The Rules:
1.  **Update Frequency:** You MUST update `docs/ai/AI_MEMORY.md` at the end of **every** significant task (Refactor, Bug Fix, Feature).
2.  **Anti-Patterns & Post-Mortem:**
    *   **Trigger:** If you made a mistake that caused a bug (e.g., "Assumed column 'batting_team' existed" or "Loaded raw CSV in test instead of Facade").
    *   **Action:** You **MUST** log this in the `## 🧱 Anti-Patterns & Lessons Learned` section.
    *   **Format:** `[Mistake] -> [Consequence] -> [Fix/Prevention]`.
    *   **Goal:** Prevent future sessions from repeating your errors.
3.  **Session History:** Log your changes reverse-chronologically so the next agent knows where you left off.

---

## 🛑 2. Strict Coding Standards (The "Zero-Destruction" Policy)

1.  **NO LAZY PLACEHOLDERS:** Never output `// ... code remains same`. Rewrite the full function/file.
2.  **PRESERVE & EXTEND (Strict):**
    *   You are **FORBIDDEN** from deleting existing functions or logic unless you are explicitly improving/enhancing it or applying a new feature that supersedes it.
    *   *Constraint:* If you touch a file, the functionality of untargeted features must remain 100% intact.
3.  **ATOMIC UPDATES:** If fixing one function, output *only* that function (unless the user asks for the full file).
4.  **SAFETY CHECK:** Verify you haven't dropped methods before overwriting a file.
5.  **ZERO HALLUCINATIONS:**
    *   Do not guess imports, variable names, or file paths.
    *   Strictly follow protocols defined in `docs/guides/DEV_GUIDE.md` and `docs/ai/AI_MEMORY.md`.
    *   If you don't know, **READ THE FILE** first.

---

## 🎓 3. Advanced Engineering Protocols

### A. The "Source of Truth" Rule
*   **Never Hardcode:** Use `config/shared/team_colors.py` and `formats/odi/config/players.py` for Colors and Roles.
*   **Why:** Centralized config = Instant global updates.

### B. The "Defensive Data" Rule
*   **Assume Dirty Data:** Always check `if col in df.columns`.
*   **Safe Math:** `a / b` must be `a / b if b > 0 else 0`.
*   **Context:** Cricket data has weird edge cases (DNB, Rain, Abandoned).

### C. The "Test Parity" Rule
*   **Rule:** Test Environments must mirror Production Logic.
*   **Implementation:** 
    *   **NEVER** use `pd.read_csv()` in regression tests.
    *   **ALWAYS** use `CricketAnalyzer(filepath)` (The Facade) to load data.
    *   *Reason:* The Facade applies standardization (Venue Names, Columns) that raw CSV loading misses.

---

## 🧪 4. Testing Strategy
*   **Golden Masters:** Use JSON snapshots for complex outputs (Venue Bias, H2H).
*   **Dynamic Coverage:** Do not hardcode "Top 10 Teams". Use `config/shared/venues.py` or dynamic discovery to cover ALL entities.

---

## ✅ 5. Definition of Done (The "Handover" Protocol)

1.  **Documentation First:** A feature is **NOT DONE** until a `REGRESSION_GUIDE.md` exists in its test folder.
2.  **Logic Verification:** Green tests are not enough. You must manually verify the *logic* of the Golden Master (e.g., does "Bat First Win %" make sense mathematically?).
3.  **Memory Update:** `docs/ai/AI_MEMORY.md` must be updated with the location of the new feature and its regression suite.
4.  **Bug Documentation:** If a bug was fixed, a formal report MUST be created in `docs/bug_fixes/` following the `YYYY-MM-DD_short_name.md` format.
5.  **Artifact Check:** Ensure `task.md` and `walkthrough.md` reflect the final state.

---

## 🌐 6. Frontend Development Rules (CRITICAL)

### 📍 Roadmap
**All frontend work MUST follow the phased roadmap:**
`docs/plans/FRONTEND_ROADMAP.md`

### 📐 Design Specification
**The manifest-driven architecture is defined in:**
`docs/design/UI_SPEC.md` (V5)

### 🛑 Frontend Agent Rules

#### Rule F1: Phase Sequential
- Phases 0-8 are **sequential dependencies**. NEVER skip phases.
- Check the STATUS TRACKER in `FRONTEND_ROADMAP.md` before starting.
- Complete the current phase fully before advancing.

#### Rule F2: Manifest Is Law
- The UI is 100% driven by `formats/{fmt}/manifest.py`.
- NEVER hardcode sidebar items, screens, tabs, or navigation in React.
- If a function isn't in the manifest, it doesn't exist in the UI.
- If you add a new engine function, add it to the manifest FIRST.

#### Rule F3: No Format-Specific Frontend Code
- The frontend MUST be format-agnostic.
- NEVER write `if (format === 'odi')` in React components.
- All format-specific behavior comes from the manifest.
- Exception: adding new `output_type` renderers (but these are generic).

#### Rule F4: Don't Touch the Engines
- Headless engines (`TeamEngine`, `PlayerEngine`, `PredictorEngine`) are STABLE.
- Do NOT modify engine behavior to fit the UI.
- The API layer is an ADAPTER — it wraps engines, doesn't change them.
- Non-JSON-friendly outputs → fix in `api/serializers.py`, not the engine.

#### Rule F5: Update Roadmap Status
- After completing any frontend work, update the STATUS TRACKER
  in `docs/plans/FRONTEND_ROADMAP.md` (mark tasks `[x]`).
- Also update `docs/ai/AI_MEMORY.md` session history.

---

## 🚀 7. Onboarding Protocol (New Agent Bootstrap)

**Every new AI agent session MUST start by reading these files IN ORDER:**

### Step 1: Understand the Mission (30 seconds)
Read `docs/ai/AI_MEMORY.md` — this is the landing page. It tells you:
- Current sprint and phase
- What was done recently (session history)
- Links to all context modules

### Step 2: Know the Rules (60 seconds)
Read these files in the `## 📂 Context Modules` section of `AI_MEMORY.md`:
- `docs/context/active_state.md` — Current architecture, anti-patterns
- `docs/guides/ENGINEERING_STANDARDS.md` — Coding constitution

### Step 3: Understand the Architecture (If Modifying Code)
- `docs/architecture/applicationArchitecture.md` — Full architecture diagram
- `docs/guides/DEV_GUIDE.md` — Developer onboarding guide
- `docs/guides/TECHNICAL_DOCUMENTATION.md` — File-by-file reference

### Step 4: Frontend-Specific (If Doing UI/API Work)
- `docs/plans/FRONTEND_ROADMAP.md` — Phase tracker
- `docs/design/UI_SPEC.md` — V5 Manifest-Driven Design

### 🚨 DO NOT START CODING UNTIL YOU HAVE READ THE RELEVANT FILES ABOVE.

---

## 📝 8. Documentation Auto-Update Protocol (CRITICAL — NEW)

### 🔴 THE RULE:
**After ANY significant code change (refactor, bug fix, feature, architecture change), you MUST update the relevant documentation files BEFORE marking the task as done.**

### 📋 Auto-Update Checklist:

| Trigger | Files to Update |
|---------|----------------|
| **Any code change** | `docs/ai/AI_MEMORY.md` (session history) |
| **Architecture change** (new file, renamed file, new pattern) | `docs/context/active_state.md` (Architecture State section) |
| **Architecture change** (new file, renamed file, new pattern) | `docs/architecture/applicationArchitecture.md` (directory structure + diagrams) |
| **Architecture change** (new file, renamed file, new pattern) | `docs/guides/DEV_GUIDE.md` (directory structure) |
| **Architecture change** (new file, renamed file, new pattern) | `docs/guides/TECHNICAL_DOCUMENTATION.md` (file-by-file reference) |
| **New coding rule or pattern established** | `docs/guides/ENGINEERING_STANDARDS.md` |
| **Bug fix** | `docs/context/active_state.md` (Anti-Patterns section) |
| **New anti-pattern discovered** | `docs/context/active_state.md` (Anti-Patterns section) |
| **Frontend work completed** | `docs/plans/FRONTEND_ROADMAP.md` (status tracker) |
| **Project milestone reached** | `README.md` (roadmap table) |
| **Session handover needed** | `docs/handovers/handover.md` |

### ❌ What NOT to Update:
- `docs/MISSION_STATEMENT.md` — Evergreen philosophy, rarely changes
- `docs/context/context_101.md` — Evergreen explainer
- `docs/hypotheses/ROI_METRICS.md` — Trading hypotheses, only update when new hypothesis added
- `docs/design/UI_SPEC.md` — Only update when UI design changes
- `REGRESSION_GUIDE.md` files — Only update when test suite changes

### ⚡ Quick Reference: Which Docs Have What
| Document | Contains |
|----------|----------|
| `AI_MEMORY.md` | Sprint status, session history, context links |
| `active_state.md` | Architecture state, pipeline, anti-patterns, coding constraints |
| `applicationArchitecture.md` | Architecture diagrams (Mermaid), layer breakdown, design patterns |
| `DEV_GUIDE.md` | Directory structure, data pipeline, operational workflows, coding standards |
| `TECHNICAL_DOCUMENTATION.md` | File-by-file reference, tech stack, caching, design patterns |
| `ENGINEERING_STANDARDS.md` | Coding principles, achievement status, roadmap |
| `handover.md` | Project overview for new agents/developers |
| `README.md` | Public-facing project overview |

### 🎯 Goal:
**Any new AI agent or developer should be able to understand the ENTIRE project by reading only the core docs — without having to reverse-engineer the codebase.**
