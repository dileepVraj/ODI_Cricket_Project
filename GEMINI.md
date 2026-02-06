# 🤖 GEMINI Agent Protocols & Governance

This document defines the **Behavioral & Operational Rules** for the AI Agent (Gemini) working on the Cricket Algo-Trader project.
It complements `DEV_GUIDE.md` (Technical Arch) by defining *HOW* the Agent should work.

---

## 🧠 1. The "Living Memory" Protocol (CRITICAL)

The `AI_MEMORY.md` file is your brain. If you don't update it, you have amnesia.

### 📜 The Rules:
1.  **Update Frequency:** You MUST update `AI_MEMORY.md` at the end of **every** significant task (Refactor, Bug Fix, Feature).
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
    *   Strictly follow protocols defined in `DEV_GUIDE.md` and `AI_MEMORY.md`.
    *   If you don't know, **READ THE FILE** first.

---

## 🎓 3. Advanced Engineering Protocols

### A. The "Source of Truth" Rule
*   **Never Hardcode:** Use `config.teams` for Colors and Roles.
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
*   **Dynamic Coverage:** Do not hardcode "Top 10 Teams". Use `venues.py` or dynamic discovery to cover ALL entities.

---

## ✅ 5. Definition of Done (The "Handover" Protocol)

1.  **Documentation First:** A feature is **NOT DONE** until a `REGRESSION_GUIDE.md` exists in its test folder.
2.  **Logic Verification:** Green tests are not enough. You must manually verify the *logic* of the Golden Master (e.g., does "Bat First Win %" make sense mathematically?).
3.  **Memory Update:** `AI_MEMORY.md` must be updated with the location of the new feature and its regression suite.
4.  **Bug Documentation:** If a bug was fixed, a formal report MUST be created in `docs/bug_fixes/` following the `YYYY-MM-DD_short_name.md` format.
5.  **Artifact Check:** Ensure `task.md` and `walkthrough.md` reflect the final state.

