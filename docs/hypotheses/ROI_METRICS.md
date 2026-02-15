# 📉 ROI-Driven Metrics & Hypotheses

This document outlines the analytical hypotheses behind our cricket metrics and how they translate to trading value (ROI).

---

## 1. Dot Ball % (Pressure Metric)
**Hypothesis:** Teams with a high Dot Ball % in the Middle Overs (11-40) are statistically more likely to trigger a collapse than teams that rotate strike, even if the latter have a lower strike rate.

**Trading Signal:**
- **Trigger:** If Team A (Bowling) has a Dot Ball % > 50% for 3 consecutive overs.
- **Action:** Lay the batting team or Back the bowling team for "Next Wicket".
- **Backtest Focus:** Correlate 3-over Dot Ball clusters with high-probability wicket events.

---

## 2. Phase Dominance (Momentum Metric)
**Hypothesis:** Winning the Powerplay (1-10) in an ODI provides a +25% win probability boost, but losing the Middle Phase (11-40) cancels this out 80% of the time.

**Trading Signal:**
- **Trigger:** Team B outscores Team A by > 2.0 RPO in the Middle Phase.
- **Action:** Hedge position if originally backed Team A.
- **Backtest Focus:** Verify "Middle Phase" RPO delta vs Match Winner.

---

## 3. Boundary Drought index
**Hypothesis:** A boundary drought exceeding 18 balls in the Death Overs (41-50) indicates a mental block or extreme tactical superiority, leading to a sub-par total.

**Trading Signal:**
- **Trigger:** 18 balls without a 4 or 6 in the final 10 overs.
- **Action:** Unders on Total Team Runs market.
- **Backtest Focus:** Final Score delta from expected score at ball 240.

---

## 4. Spin-Choke Probability
**Hypothesis:** Wrist Spinners with an Economy < 4.5 on dry pitches (ID: 'Dry_Turf') increase the required run rate by an average of 1.2 per ball in the second innings.

**Trading Signal:**
- **Trigger:** Leg-spinner starting 2nd spell with target score > 150 needed.
- **Action:** Back the bowling team during the leg-spinner's over.
- **Backtest Focus:** RRR growth rate during spin spells on specific pitch types.
