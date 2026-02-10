# 🌉 The Truth Bridge: Technical Architecture Guide

Welcome to the **Truth Bridge**. This document explains how our quality control system works. We will explain it first as if you are 5 years old, and then dive into the advanced engineering logic that keeps our Cricket Algo-Trader 100% accurate.

---

## 🧸 Section 1: Explaining to a 5-Year-Old

Imagine you have a big box of Lego sets. You built a perfect castle yesterday, and you took a **photo** of it. 

Today, you decided to change how you build castles (you changed the "rules"). But you want to make sure you didn't accidentally break the tower or lose a dragon.

1.  **The Photo (Ground Truth):** This is our "Memory." It remembers exactly what the castle looked like before.
2.  **The New Castle (Engine Output):** This is what the computer builds today using the new rules.
3.  **The Robot Helper (Truth Bridge):** The robot looks at the **Photo** and the **New Castle** at the same time.
    - If they are the same: The robot gives you a **Green Sticker** (PASS).
    - If they are different: The robot checks its special glasses. 
    - **Data Drift:** If the robot sees you just added *new* Legos to the box, it says "It's different, but that's okay! You just have more pieces now."
    - **Logic Regression:** If the robot sees you used the *same* pieces but built the tower crooked, it screams "ERROR! You broke the rules!"

---

## ⚙️ Section 2: Standout Technical Logics (v2.5)

The Truth Bridge isn't just a simple "A == B" check. It uses advanced **Auto-Diagnosis** to tell the difference between a bug and a data update.

### 1. The Fingerprint Protocol (`MATCH_IDS`)
Every time an engine (like `TeamEngine`) calculates stats, it bundles a hidden list of every Match ID it used. This is our "Fingerprint."
- **Why?** If a Win % changes from 60% to 62%, we need to know *why*.
- **Logic:** We compare the Fingerprint of the "Old Photo" (Truth) vs. the "New Build" (Engine).

### 2. The 4 States of Diagnosis
When a test fails, the system automatically applies one of these four tags in `report.json`:

| Diagnosis | Meaning | Action Required |
| :--- | :--- | :--- |
| **LOGIC_REGRESSION** | Match IDs are identical, but the math is different. | **FIX THE CODE.** You introduced a bug. |
| **DATA_DRIFT** | New IDs are in the engine but not the truth. | **RE-SEED.** The logic is fine; the data just grew. |
| **FILTERING_REGRESSION** | Engine is seeing *fewer* matches than before. | **CHECK FILTERS.** Did you accidentally exclude matches? |
| **COMPLEX_DRIFT** | The IDs have shifted completely. | **MANUAL AUDIT.** Too many changes to auto-verify. |

### 3. Structural Loyalty & The Facade
We never load raw CSVs in our tests. We always use the `CricketAnalyzer` (The Facade).
- **Rule:** This ensures that the test environment exactly mirrors the production environment, including how we clean venue names and handle missing data.

---

## ⚖️ Section 3: Standout Rules for Developers

To keep the Truth Bridge strong, we follow these "Golden Rules":

1.  **The "Snapshot" First Rule:** Before you refactor an engine, you MUST run it in `SEED_MODE="1"`. This captures the "Before" photo.
2.  **Zero Hardcoding:** Our tests never hardcode team colors or roles. They always import from `config.teams`. If you change a color in config, the entire bridge updates automatically.
3.  **Atomic Verification:** We don't just check the total. We check three layers:
    - **Layer 1 (The Header):** Overall team stats.
    - **Layer 2 (The Matrix):** Performance against every opponent.
    - **Layer 3 (The Matchups):** Detailed player-vs-player history.
4.  **Headless Execution:** All test runners are built to run without needing a browser or Jupyter notebook, making them perfect for fast, automated CI/CD pipelines.

---

## 🚀 Summary
The Truth Bridge is the **Guardian of Logic**. It allows us to move fast and change complex code without ever worrying about breaking the "Truth" of our cricket analytics.
