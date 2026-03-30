# Function Quality Guide
**Date:** 2026-03-27
**Purpose:** Checklist and process for making every function analytically sound, domain-correct, and production-ready before any UI work begins.

---

## The Core Principle

> Fix the brain before the face.

Every function must be trustworthy before it is presented. A well-designed UI that surfaces wrong signals is more dangerous than an ugly UI with correct signals — because it looks credible while misleading the operator.

---

## The Build Order (Non-Negotiable)

```
Phase 1 — Fix all function logic (domain knowledge)
          One function at a time
          Each function returns correct data + Key Findings

Phase 2 — Define the new visual design system once
          Global rules for color, layout, Key Findings component
          Decided once, applied everywhere — not per function

Phase 3 — Apply visual design to all cards
          Consistent because rules are set before touching any card

Phase 4 — Build Match Brief screen
          Calls fixed functions, uses new design system
          Built last — everything it depends on must be ready first
```

**Never mix Phase 1 and Phase 2.** Fix logic first, redesign visuals after. Mixing both per function leads to visual inconsistency across cards.

---

## Phase 1: The Function-by-Function Process

For each existing function, work through these steps in order:

### Step 1 — Understand What It Currently Does
- What question does this function answer?
- What data does it pull from the database?
- What does it return to the frontend?
- What are the current parameter inputs (teams, venue, years)?

### Step 2 — Domain Knowledge Audit
Ask: *"Does this function calculate what a cricket analyst would actually want to know, using the right data, the right filters, and the right thresholds?"*

Check each of the following:

**Data Correctness**
- [ ] Is the data being filtered correctly (format, date range, teams)?
- [ ] Are extras, no-balls, and wides handled correctly in run calculations?
- [ ] Are abandoned matches and no-results excluded where appropriate?
- [ ] Are DLS-affected matches handled or flagged?

**Statistical Soundness**
- [ ] Is the sample size sufficient? Flag results with fewer than 10 matches as low confidence.
- [ ] Are recent matches weighted more heavily than old ones where recency matters?
- [ ] Are averages skewed by outlier matches? Consider median alongside mean where appropriate.
- [ ] Does the function account for era differences (high-scoring era vs low-scoring era)?

**Cricket Domain Correctness**
- [ ] Are phase boundaries correct? Powerplay = overs 1-10, Middle = 11-40, Death = 41-50 for ODI.
- [ ] Is "batting first win rate" calculated correctly — only completed matches, not no-results?
- [ ] Are player matchup stats filtered to relevant innings and phase context?
- [ ] Does toss impact exclude neutral venue matches where appropriate?
- [ ] Are H2H records filtered to the correct format (ODI only)?

**Context Sensitivity**
- [ ] Does the function use the right time window for its purpose? (See time window reference below.)
- [ ] Does it distinguish home vs away vs neutral venue where relevant?
- [ ] Are results weighted by match importance where applicable (World Cup vs dead rubber)?

### Step 3 — Define Key Findings Logic
Every function must generate a `key_findings` list alongside its data. This logic lives in Python — never in the frontend.

For each stat the function returns, define:
- What threshold makes this stat a **signal** vs. **noise**?
- What is the signal **direction** — is high good or bad for the batting team?
- What **tier** does this signal belong to? (green / teal / amber / red)
- What is the plain-English sentence that describes this finding?

**Example — Venue Bias Function:**

| Stat | Noise range | Signal threshold | Tier | Finding text |
|---|---|---|---|---|
| Bat first win rate | 45–55% | >62% or <38% | Green if >62%, Red if <38% | "Batting first wins X% here — strong first-innings advantage" |
| Toss impact | <10% swing | >15% swing | Amber | "Toss matters here — winning toss correlates with X% win rate" |
| Death overs economy | 8.0–8.8 | >9.2 | Amber | "Death overs run expensive here — avg economy X" |
| Sample size | — | <10 matches | Amber always | "Low sample size — X matches only, treat with caution" |

These thresholds must be defined by cricket domain knowledge, not guessed. If unsure, consult the cricket-domain agent.

### Step 4 — Validate Against Real Data
Before marking a function as done:
- [ ] Run the function against at least 3 different match contexts (different venues, different team combinations)
- [ ] Do the Key Findings make cricket sense for each result?
- [ ] Does the function return gracefully when data is sparse (e.g. two teams that have rarely met)?
- [ ] Does it handle edge cases — teams that have never played at a venue, players with fewer than 5 innings, etc.?

### Step 5 — Mark Complete
Only mark a function complete when:
- [ ] Domain audit passed
- [ ] Key Findings logic implemented and tested
- [ ] Edge cases handled
- [ ] Output reviewed by operator and makes cricketing sense

---

## Time Window Reference

Each analysis type has an appropriate historical window. Use these as defaults — do not let the operator set these on the Match Brief. The Deep Dive terminal may allow override.

| Analysis Type | Default Window | Reason |
|---|---|---|
| Venue profile / bias | Last 8–10 years | Need volume; ground conditions change slowly |
| Venue toss impact | Last 8–10 years | Ground conditions change slowly |
| Phase benchmarks at venue | Last 8–10 years | Era normalisation needed |
| H2H record | Last 5 years | Squad composition changes; older data less relevant |
| Team form | Last 10 matches | Form is recent by definition |
| Player matchups | Last 3–5 years | Player careers evolve |
| Fortress report | All time | Historical dominance is a long-term pattern |
| Player career stats | All available | Career context needs full history |

---

## Signal Threshold Reference (Starting Point)

These are starting thresholds. Refine based on data observation.

| Stat | Low confidence | Signal | Strong signal |
|---|---|---|---|
| Bat first win rate | 45–55% (noise) | >60% or <40% | >68% or <32% |
| Toss impact on win rate | <10% (noise) | >15% | >25% |
| Death overs economy | <8.5 (normal) | >9.0 | >9.5 |
| Powerplay average runs | 45–55 (normal) | >60 or <40 | >65 or <35 |
| H2H win rate | 40–60% (balanced) | >65% or <35% | >75% or <25% |
| Sample size warning | — | <15 matches | <8 matches |
| Player average | 30–45 (normal) | >50 or <20 | >60 or <15 |
| Player economy rate | 5.0–6.0 (normal) | >6.5 or <4.5 | >7.0 or <4.0 |

---

## Checklist Before Introducing a New Function

A new function must pass every item on this checklist before it gets built.

### 1. The Question Test
- [ ] What specific question does this function answer?
- [ ] Is this question one the operator genuinely needs answered before or during a match?
- [ ] Is this question already answered by an existing function? If yes — extend that function, don't add a new one.

### 2. The Data Test
- [ ] Does our CricSheet / DuckDB data actually support this function?
- [ ] Which tables does it need? (matches / balls / player_stats / phase_stats / squads)
- [ ] Are the required columns available in those tables?
- [ ] What is the minimum sample size needed for this function to be meaningful? Is that sample size achievable with our data?

**Hard stop:** If the data does not exist in the database, the function does not get built. No exceptions. Do not build functions that require data we don't have (weather, pitch reports, live odds, historical betting prices).

### 3. The Module Test
- [ ] Which existing module does this function belong to?
- [ ] If it doesn't fit any existing module, does it justify a new module? (A new module requires at least 3–4 functions minimum — one function does not make a module.)

### 4. The Duplication Test
- [ ] List every existing function that touches similar data. Does this new function overlap with any of them?
- [ ] If overlap exists, can the existing function be extended rather than a new one created?

### 5. The Domain Knowledge Test
- [ ] What does cricket domain knowledge say this function should calculate?
- [ ] What are the signal thresholds for its Key Findings?
- [ ] What edge cases exist in cricket that this function must handle?
- [ ] Has the logic been reviewed against cricket analyst standards before building?

### 6. The Output Test
- [ ] What does this function return? List every field.
- [ ] What does the Key Findings logic look like for this function?
- [ ] What card/renderer type will display this output?
- [ ] Does an existing renderer cover it, or does a new one need to be built?

---

## Checklist Before Introducing a New Module

A new module is a significant addition. It requires more justification than a new function.

- [ ] What is the module's theme — what family of questions does it answer?
- [ ] List every function that would live in this module (minimum 3, ideally 4–6).
- [ ] Does each of those functions pass the new function checklist above?
- [ ] Does this module overlap with any existing module? If yes — extend the existing module.
- [ ] Does our data support the full module, not just one or two functions in it?
- [ ] Has the module been reviewed against the operator's actual pre-match research workflow? Does it fill a real gap?

---

## Things to Never Do

- **Never build a function to display data you don't have.** No workarounds, no placeholder data, no "we'll add this later."
- **Never define signal thresholds in the frontend.** All `key_findings` logic lives in Python.
- **Never add a function because it sounds interesting.** Only add it because the operator needs it to make a better decision.
- **Never skip the domain knowledge audit** on an existing function just because it appears to work. "Appears to work" and "calculates the right thing" are not the same.
- **Never build a new module for a single function.** One function without a home goes into the closest existing module.
- **Never mark a function complete without testing it against real data** in at least 3 different contexts.

---

## The Match Brief Dependency

The Match Brief screen is built last. It depends on:
- All functions it calls being Phase 1 complete (domain correct + Key Findings)
- The visual design system being Phase 2 complete (global rules set)

Do not begin Match Brief screen work until both conditions are met. The Brief is only as good as the functions underneath it.
