# 🎯 The Mission: Beating the Market

**Objective:** Build a **Cricket Algo-Trading Intelligence System**.

This is not a stats scraper. This is not a "Cricinfo Clone."
This is a machine designed to calculate **True Odds** and identify **Market Edges**.

---

## 💡 The "Edge" Philosophy

Most public analysis relies on broad averages (e.g., "Kohli averages 50").
We win by isolating **Contextual Signal** from the noise.

### 1. Granularity is King
*   **The Market:** Looks at Match Winners.
*   **We Look At:** Balls.
*   **Why:** A single 4-run over in the 48th over changes the game. We track every single delivery to model momentum shifts that the market misses.

### 2. Context Over Totals
*   **The Market:** "Venue Avg: 280".
*   **We Look At:** "Venue Avg Chasing > 8 RPO under lights."
*   **Why:** A "Good Batting Pitch" might be a "Graveyard" in the second innings. Our engines (`TeamEngine`, `Predictor`) focus on these specific slices.

### 3. TruthBridge (Zero Tolerance for Drift)
*   **The Problem:** A single missing match or wrong data point can flip a probability model from "Value Buy" to "Stay Away."
*   **The Solution:** The **Truth Bridge**.
    *   Every analysis is Fingerprinted (`MATCH_IDS`).
    *   If the data drifts, the system self-diagnoses.
    *   **Trust is Binary:** Data is either 100% Correct or 0% Useful.

---

## 🏗️ The Engineering Standard: Neuro-Symbolic

To achieve this, the system uses a **Neuro-Symbolic** architecture:

*   **🧠 Symbolic (The Engine):** Deterministic, hard-coded logic (`CricketAnalyzer`).
    *   *Role:* Calculates stats, runs simulations, enforcing the rules of cricket.
    *   *Trait:* Never guesses. Pure Math.
*   **🤖 Neural (The Agent):** Adaptive, intent-driven navigation (Me).
    *   *Role:* Understands "Find me a venue bias" and translates it into the correct Engine calls.
    *   *Trait:* Flexible navigation, strict adherence to the Engine's truth.

---

### 📉 The Bottom Line
We are building a machine that turns **Raw Cricket Data** into **Financial Confidence**.
Every feature, refactor, and bug fix must serve this goal.
