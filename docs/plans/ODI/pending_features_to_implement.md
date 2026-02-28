Mate, based on your vision for a Quantitative In-Play Trading Terminal and the gap analysis we just ran, here is the exact architectural backlog of the features your ODI engine is currently missing.

These are not standard cricket statistics; these are the **Alpha Generators**—the mathematical models that will allow you to see the true probability of a match before the bookmaker's algorithms adjust.

Here is the exact list of what we need to build to complete the ODI Quant Terminal:

### 1. The Core Infrastructure Gaps

* **The Stealth Live Scraper:** A Python service that pings free data sources (like Cricbuzz or ESPN) every 10 seconds to extract the exact `LiveMatchState` (score, overs, striker, non-striker, current bowler) without needing a paid API.
* **The Pydantic Live State Contract:** A strict data schema that standardizes live match data so the math engines can read it instantly without crashing.

### 2. The Conditional Baselines (The "Lego Blocks")

* **Conditional Phase Matrix:** (What we just discussed). Calculating average runs and collapse rates for a specific phase (e.g., Overs 41-50) strictly grouped by the *number of wickets lost* entering that phase at a specific venue.
* **Live Bowling Resource Tracker:** A function that analyzes the scorecard and calculates exactly how many overs of Pace vs. Spin are remaining, and maps the specific bowlers to those remaining overs.
* **Entry Point Analysis:** A model that calculates a batter's expected strike rate and survival probability based on the *exact match state* they walk into (e.g., coming in at 20/3 vs. coming in at 150/2).
* **Proxy Covariates Engine:** Since you don't have live weather or pitch data, we need a mathematical function that infers the pitch condition (e.g., "Turning Track" or "Flat Deck") by analyzing the run rate and spin economy of the *first 6 overs*, adjusting the second innings predictions automatically.

### 3. The In-Play Hazard Models

* **Dot Ball Pressure Index:** A mathematical hazard-rate model that calculates the surging probability of a wicket falling (or a boundary being hit) on the *next ball* based on the number of consecutive dot balls previously bowled. Bookies struggle to price momentum; this algorithm prices it perfectly.
* **Live Granular Matchups:** A real-time engine that doesn't just look at the current striker vs. bowler, but also calculates the historical vulnerability of the *next two batters in the dugout* against the opposition's remaining bowlers.

### 4. The Endgame Engine

* **The Monte Carlo Simulator:** This is the "God Function" you described earlier. It doesn't use a single SQL query. It takes the `LiveMatchState`, loads the remaining `Bowling Resources`, looks at the `Granular Matchups`, and rolls the probability dice to simulate the remaining balls of the match 10,000 times.

This simulator will spit out the **True Par Score** and the **True Win Probability**, giving you the ultimate green light/red light on whether to place your bet.

---

### The Blueprint is Set

We cannot build the Monte Carlo simulator until we have the Lego blocks (the Conditional Baselines).

As we discussed in the previous step, do you want to proceed with building the first block: **The Conditional Phase Matrix** SQL query? Or do you want to start with building the **Live Bowling Resource Tracker**?

# ---------------------------------------------------------------------------------------------

* How about implementing teams record aganist bowling type?
