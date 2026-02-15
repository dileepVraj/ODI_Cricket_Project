# 🏏 ODI MATCH PACK — GENERATION PROTOCOL v2.1

> **Purpose:** Generate a single, self-contained JSON "Intelligence Report" for any upcoming ODI match.
> The pack must be readable by both a human analyst and an AI agent — every number must speak for itself through structured context and plain-English narrative.

---

## ⏱️ TIMELINE STRATEGY (Why These Windows Matter)

Every data window in this document is calibrated for **ODI cricket** specifically. ODI is a format where:
- Teams play **15–25 ODIs per year**, meaning 5 years ≈ 75–125 matches per team.
- A team **tours a specific country once every 3–4 years**, so country-specific data is sparse.
- The **ICC ODI World Cup cycle is 4 years** — this is the natural "era" of a squad generation.
- Pitches get relaid and grounds renovated roughly every **5–7 years**.
- Two specific teams meet at one specific venue **once every 5–10 years** — extremely sparse data.

| Data Type | Window | Rationale |
|---|---|---|
| **Global H2H** | 4Y (Primary) + 8Y (Secondary) | 4Y = 1 WC cycle (current squad). 8Y = 2 WC cycles (broader context). |
| **Recent Form** | Last 10 matches | 5 matches can be a single bilateral series. 10 gives pattern recognition across 2–3 series. |
| **Country H2H** | 8Y | Tours happen every 3–4Y. 8Y guarantees at least 2 touring cycles (6–12 matches). |
| **Home Dominance / Away Performance** | 4Y | 1 WC cycle. Captures current era's home/away strength. |
| **Fortress Check** | 10Y | Venue data is sparse (~3–5 ODIs/year at a ground). 10Y = 30–50 matches = reliable sample. |
| **Venue Matchup (H vs A at Venue)** | 15Y | Extremely sparse. Two specific teams at one venue may produce only 3–6 matches in a decade. 15Y maximises sample while staying within modern cricket era. |
| **Toss Bias** | 7Y | Pitch behaviour is moderately stable. 7Y = 20–40 matches = statistically meaningful. Older data risks pre-renovation pitch profiles. |
| **Phase Analysis** | 4Y | ODI phase tactics evolve (New Ball rules, Batting Powerplay abolished in 2015). 4Y = 1 WC cycle = current tactical era. |
| **Player Form** | Last 10 matches | Captures 2–3 series. More reliable than 5 matches for spotting genuine form vs one-off results. |
| **Tactical Matrix / Matchups** | All-Time | Batter vs bowling type / specific bowler are rare events. Maximum sample needed. |

---

## 🔑 GOLDEN RULES

1. **No Raw Dumps.** Every engine result must be transformed into a structured dictionary before entering the JSON. Flat `[{Metric, Value}]` lists from Jupyter display functions are **forbidden**.
2. **No HTML in Data.** All `<span>` tags, color codes, and emoji decorators must be stripped. The JSON carries pure numbers; styling is the UI's job.
3. **Every Section = Data + Context + Narrative.** No exceptions.
   - `Data`: Clean numerical metrics (dict, not list).
   - `Context`: Computed tags, comparisons, gaps.
   - `Narrative`: 1–3 sentence human-readable explanation of what the numbers mean.
4. **Executive Summary First.** The JSON opens with a `Verdict` object — a 3-line TL;DR that an analyst can read in 10 seconds.
5. **Debug keys are separate.** `MATCH_IDS` and audit trails go under a `_debug` key, not inline with analytical data.

---

## 📐 JSON SCHEMA (Target Output Structure)

```json
{
  "Metadata": {
    "home_team": "Sri Lanka",
    "away_team": "England",
    "venue": "R.Premadasa Stadium, Colombo",
    "match_date": "2026-02-11",
    "match_time": "14:30 IST",
    "toss": "Away Won & Batting",
    "pitch_report": "Dry, cracks visible, turn expected.",
    "generated_at": "2026-02-11 10:30:00"
  },

  "Executive_Summary": {
    "prediction": "Sri Lanka slight favourites at home despite recent poor form.",
    "key_factors": [
      "Fortress venue: SL win 63% here (21/33 matches, 10Y).",
      "England's away record is poor: 27% win rate in last 5Y.",
      "Pitch favours spin — SL have 3 specialist spinners vs ENG's 1."
    ],
    "risk_alerts": [
      "SL recent form is COLD (1/5 wins).",
      "England won 2 of last 3 matches in this same series."
    ],
    "condition_adjustments": "SPIN_BOOST (dry pitch) | TOSS_ADVANTAGE (Away elected to BAT)"
  },

  "Chapter_1_Macro_Context": { "..." },
  "Chapter_2_Battlefield": { "..." },
  "Chapter_3_Tactical_Engine": { "..." },
  "Chapter_4_Player_Intelligence": { "..." },
  "_debug": { "match_ids": {}, "engine_versions": {} }
}
```

---

## 📖 CHAPTER 1: MACRO CONTEXT (Global Standing)

**Goal:** Establish the historical power balance between the two teams.

---

### 1.1 Global Head-to-Head

**Engine:** `analyze_global_h2h(home, away, years_back)`
**Timelines:** 4 Years (Primary — 1 WC Cycle), 8 Years (Secondary — 2 WC Cycles)
**Timeline Label in Output:** Must include `"timeline": "Last 4 Years"` in data.

**Output Schema:**
```json
{
  "h2h_5y": {
    "data": {
      "matches_played": 7,
      "home_wins": 2,
      "away_wins": 4,
      "no_result": 1,
      "home_win_pct": 33,
      "batting_first": {
        "home_avg_score": 216,
        "home_highest": 271,
        "home_lowest": 166,
        "away_avg_score": 256,
        "away_highest": 357,
        "away_lowest": 156
      },
      "chasing": {
        "home_avg_score": 304,
        "home_highest_chase": 160,
        "away_avg_score": 239,
        "away_highest_chase": 244
      }
    },
    "context": {
      "dominance": "AWAY_DOMINANT",
      "intensity": "ONE_SIDED",
      "win_gap": 34,
      "batting_first_advantage": "AWAY",
      "chasing_advantage": "AWAY"
    },
    "narrative": "England dominate this rivalry with a 67% win rate over 5 years (4 wins from 7 matches). Sri Lanka's average batting first score of 216 is 40 runs below England's 256, suggesting a significant gap in batting depth. England are also stronger chasers (avg 239 vs SL's 304 in 1 failed chase)."
  },
  "h2h_10y": { "..." }
}
```

**Interpretation Rules:**
| Tag | Condition |
|---|---|
| `DOMINANT` | Win% > 65% |
| `COMPETITIVE` | Win% between 45–55% |
| `ONE_SIDED` | Win% gap > 20 points |
| `HOME_SPECIALIST` | Home win% > 60% but away win% < 40% |

**Narrative must answer:** *"Who owns this rivalry, and is the gap widening or narrowing?"*

---

### 1.2 Recent Form (Momentum Check)

**Engine:** `analyze_team_form(team, limit=10)`
**Timeline:** Last 10 matches (~6–18 months). 10 matches covers 2–3 bilateral series, filtering out one-off flukes.
**Run 3x per team (6 total calls):**

| # | Filter | Purpose |
|---|---|---|
| 1 | Global (All Opponents, All Regions) | Overall momentum |
| 2 | In Host Continent/Region | Conditions-specific form |
| 3 | Against This Opponent Only | Rivalry momentum |

**Output Schema:**
```json
{
  "home_form": {
    "global": {
      "data": {
        "sequence": ["L", "L", "W", "L", "L"],
        "wins": 1,
        "losses": 4,
        "matches": [
          {"date": "2026-01-27", "opponent": "England", "result": "LOSS", "margin": "53 runs"}
        ]
      },
      "context": {
        "momentum": "COLD",
        "trend": "DECLINING",
        "streak": "2 consecutive losses"
      },
      "narrative": "Sri Lanka are in dire form — just 1 win from their last 5 ODIs. The 2-match losing streak to England suggests a confidence problem heading into this match."
    },
    "in_region": { "..." },
    "vs_opponent": { "..." }
  }
}
```

**Interpretation Rules:**
| Tag | Condition |
|---|---|
| `HOT` | 4+ wins out of 5 |
| `STABLE` | 2–3 wins out of 5 |
| `COLD` | 0–1 wins out of 5 |
| `TRENDING_UP` | Last 2 matches are wins after earlier losses |
| `TRENDING_DOWN` | Last 2 matches are losses after earlier wins |

**Narrative must answer:** *"Is this team riding a wave or drowning?"*

---

### 1.3 Country-Specific H2H

**Engine:** `analyze_country_h2h(home, away, country, years_back=8)`
**Timeline:** Last 8 Years (2 WC Cycles). Tours to a specific country happen every 3–4 years; 8Y guarantees 2+ touring cycles.

Same schema as 1.1 but filtered to matches played in the home team's country only.

**Narrative must answer:** *"Does the away team struggle specifically in this country?"*

---

### 1.4 Home Dominance Record

**Engine:** `analyze_home_dominance(home_team, years_back=4)`
**Timeline:** Last 4 Years (1 WC Cycle). Captures the current squad generation's home record.

**Output Schema:**
```json
{
  "data": {
    "overall": { "matches": 33, "wins": 20, "losses": 11, "win_pct": 64 },
    "vs_top_teams": { "matches": 18, "wins": 9, "win_pct": 50 },
    "vs_this_opponent": { "matches": 3, "wins": 1, "win_pct": 33 }
  },
  "context": {
    "home_strength": "STRONG",
    "opponent_specific": "VULNERABLE"
  },
  "narrative": "Sri Lanka win 64% of home matches overall (strong). But against England specifically at home, they've won only 1 out of 3 (33%) — this opponent neutralises the home advantage."
}
```

**Narrative must answer:** *"Is the home advantage real, or does this opponent neutralise it?"*

---

### 1.5 Away Performance Record

**Engine:** `analyze_away_performance(away_team, years_back=4)`
**Timeline:** Last 4 Years (1 WC Cycle). Matches the home dominance window for fair comparison.

Same structure as 1.4 but for the away team's record when travelling.

**Narrative must answer:** *"Is this away team comfortable travelling, or do they collapse outside home?"*

---

## 🏟️ CHAPTER 2: THE BATTLEFIELD (Venue Intelligence)

**Goal:** Understand the venue's personality — its scoring patterns, its biases, its history.

---

### 2.1 Fortress Check

**Engine:** `analyze_home_fortress(venue, home_team, years_back=10)`
**Timeline:** Last 10 Years

**Output Schema:**
```json
{
  "data": {
    "matches": 35,
    "home_wins": 21,
    "visitor_wins": 12,
    "home_win_pct": 63,
    "home_batting_first": { "avg_score": 250, "avg_winning_score": 271, "lowest_defended": 203 },
    "visitors_chasing": { "avg_score": 206, "highest_successful_chase": 277 }
  },
  "context": {
    "fortress_status": "CONFIRMED",
    "batting_first_bias": "STRONG",
    "defend_threshold": 203,
    "chase_ceiling": 277
  },
  "narrative": "R.Premadasa Stadium is a confirmed fortress for Sri Lanka (63% win rate, 21/33 matches over 10 years). SL win primarily by batting first and defending — their average winning score is 271 and the lowest they've successfully defended is 203. Visitors have never chased above 277 here."
}
```

**Interpretation Rules:**
| Tag | Condition |
|---|---|
| `FORTRESS_CONFIRMED` | Home win% > 60% at venue |
| `NEUTRAL_GROUND` | Home win% 45–55% |
| `VISITOR_FRIENDLY` | Home win% < 45% |

**Narrative must answer:** *"What score is 'safe' to defend here? What's the highest successful chase?"*

---

### 2.2 Venue Head-to-Head

**Engine:** `analyze_venue_matchup(venue, home, away, years_back=15)`
**Timeline:** Last 15 Years. Two specific teams at one venue is the sparsest data in the pack. 15Y maximises sample while staying within modern ODI era (post-2011 rule changes).

Same schema as 2.1 but filtered to matches between these two specific teams at this venue.

**Narrative must answer:** *"Does the fortress hold against THIS specific opponent?"*

---

### 2.3 Toss Bias

**Engine:** `analyze_venue_bias(venue, years_back=7)`
**Timeline:** Last 7 Years. Balances recency (current pitch behaviour) with sample size (20–40 matches). Avoids pre-renovation data while capturing enough matches for statistical significance.

**Output Schema:**
```json
{
  "data": {
    "matches_analyzed": 28,
    "bat_first_wins": 16,
    "bat_first_win_pct": 57,
    "chase_wins": 10,
    "chase_win_pct": 35,
    "avg_1st_innings": 235,
    "avg_2nd_innings": 205
  },
  "context": {
    "verdict": "BAT_FIRST",
    "strength": "MODERATE",
    "score_drop_2nd_innings": 30,
    "toss_winner_advantage": true
  },
  "narrative": "This venue favours batting first (57% win rate). Average 1st innings score is 235, but 2nd innings drops to 205 — a 30-run depression suggesting the pitch deteriorates. Teams winning the toss should strongly consider batting first."
}
```

**Combined with Match Context:**
- If Toss = "Home Won & Batting" AND Venue Bias = "BAT_FIRST" → `TOSS_ALIGNED` tag.
- If Toss = "Away Won & Bowling" AND Venue Bias = "BAT_FIRST" → `TOSS_MISALIGNED` tag.

**Narrative must answer:** *"Does batting first or chasing give you a measurable edge here?"*

---

## ⚡ CHAPTER 3: TACTICAL ENGINE (Phase & Conditions)

**Goal:** Break the match into phases and identify where each team is strong or weak.

---

### 3.1 Phase Analysis

**Engine:** `analyze_venue_phases(venue, home, away, years=4)`
**Timeline:** Last 4 Years (1 WC Cycle). Phase-wise trends evolve every WC cycle. 4Y captures the current tactical era while providing enough venue-level sample.

**Output Schema:**
```json
{
  "data": {
    "timeline": "Last 4 Years (1 WC Cycle)",
    "venue_baseline": {
      "powerplay": { "avg_runs": 46.8, "avg_wickets": 1.5 },
      "middle": { "avg_runs": 133.4, "avg_wickets": 4.2 },
      "death": { "avg_runs": 57.8, "avg_wickets": 2.3 }
    },
    "home_at_venue": {
      "powerplay": { "avg_runs": 43.6, "avg_wickets": 1.2 },
      "middle": { "avg_runs": 128.0, "avg_wickets": 3.8 },
      "death": { "avg_runs": 62.0, "avg_wickets": 2.5 }
    },
    "away_at_venue": {
      "powerplay": { "avg_runs": 40.0, "avg_wickets": 1.8 },
      "middle": { "avg_runs": 110.0, "avg_wickets": 4.5 },
      "death": { "avg_runs": 130.0, "avg_wickets": 2.0 }
    },
    "global_habits": {
      "batting_first": {
        "home_pp_runs": 47.0, "away_pp_runs": 50.1,
        "home_mid_runs": 140.8, "away_mid_runs": 147.6,
        "home_dth_runs": 55.5, "away_dth_runs": 62.0
      },
      "chasing": {
        "home_mid_wkts": 3.8, "away_mid_wkts": 3.7,
        "home_dth_runs": 48.0, "away_dth_runs": 58.0
      }
    }
  },
  "context": {
    "powerplay_advantage": "AWAY",
    "middle_overs_advantage": "HOME",
    "death_overs_advantage": "AWAY",
    "alerts": ["SL collapses while chasing", "SLOW_PITCH_START"],
    "phase_dominance": "AWAY_CONTROLS_DEATH",
    "biggest_gap": { "phase": "death", "difference": 68, "favours": "AWAY" }
  },
  "narrative": "England score significantly more in the death overs at this venue (130 avg vs SL's 62). This 68-run gap is the biggest tactical disparity. However, SL control the middle overs at this venue (128 avg vs ENG's 110) — the accumulation phase is their strength. SL's powerplay at this venue (43.6) is below the venue baseline (46.8), suggesting conservative starts. Globally, England outscore SL in all three phases when batting first (PP: 50.1 vs 47.0, Mid: 147.6 vs 140.8, Death: 62.0 vs 55.5)."
}
```

**Narrative must answer:** *"Which phase of the innings decides the match, and who controls it?"*

---

### 3.2 Condition Weighting (Pitch + Time + Toss)

This is not an engine call — it's the **Interpreter's** job to adjust the entire pack.

**Rules:**
| Input | Keyword Detection | Effect |
|---|---|---|
| Pitch: "dry", "cracks", "turn", "dust" | `SPIN_BOOST` | +20% weight to spin bowling metrics |
| Pitch: "green", "grass", "seam", "moisture" | `SEAM_BOOST` | +15% weight to pace bowling metrics |
| Time: "night", "14:30+", "sunset" | `DEW_FACTOR` | Chase advantage elevated |
| Toss: "Home Won & Batting" + Bias = BAT_FIRST | `TOSS_ALIGNED` | Home advantage amplified |
| Toss: "Away Won & Batting" + Bias = BAT_FIRST | `COUNTER_TOSS` | Away seized toss advantage |

---

## 🎯 CHAPTER 4: PLAYER INTELLIGENCE (Squad & Matchups)

**Goal:** Move from team-level to individual-level analysis.
**Timeline:** All-Time (50 Years) for career stats, Last 10 matches for form.

---

### 4.1 Squad Comparison

**Engine:** `compare_squads(home, home_xi, away, away_xi, venue, years=50)`
**Timeline:** All-Time (Career Stats)

**Output Schema:**
```json
{
  "data": {
    "home": {
      "combined_caps": 403,
      "total_runs": 10385,
      "centuries": 16,
      "fifties": 59,
      "total_wickets": 227
    },
    "away": {
      "combined_caps": 309,
      "total_runs": 8075,
      "centuries": 12,
      "fifties": 45,
      "total_wickets": 166
    }
  },
  "context": {
    "experience_advantage": "HOME",
    "batting_depth_advantage": "HOME",
    "bowling_depth_advantage": "HOME",
    "experience_gap": 94
  },
  "narrative": "Sri Lanka's XI is significantly more experienced (403 caps vs 309). They have a 2,310-run advantage in career ODI runs and 61 more career wickets. This experience edge is particularly relevant on a deteriorating pitch."
}
```

---

### 4.2 Player Form & Venue Metrics

**Source:** `Detailed Player Statistics & Venue Metrics` section from `compare_squads`
**Timeline:** Last 10 matches (Overall Form) + Career at Venue

This section captures **each player's current batting and bowling form** based on their role, including their record at the current venue.

**Output Schema (per player):**
```json
{
  "player": "BKG Mendis",
  "role": "Top-Order Batter",
  "batting_form": {
    "overall_last_5": {
      "innings": 5,
      "runs": 187,
      "average": 37.4,
      "strike_rate": 82.0,
      "highest": 75,
      "form_rating": "IN_FORM"
    },
    "vs_opponent_last_5": {
      "innings": 3,
      "runs": 112,
      "average": 37.3,
      "strike_rate": 78.5,
      "form_rating": "STEADY"
    },
    "at_venue": {
      "innings": 8,
      "runs": 312,
      "average": 44.6,
      "strike_rate": 85.2,
      "highest": 92,
      "venue_rating": "VENUE_SPECIALIST"
    }
  },
  "bowling_form": {
    "overall_last_10": {
      "matches": 10,
      "overs": 42,
      "wickets": 8,
      "economy": 5.2,
      "average": 27.4,
      "strike_rate": 31.5,
      "best_figures": "3/28",
      "form_rating": "IN_FORM"
    },
    "vs_opponent_last_10": {
      "matches": 3,
      "overs": 14,
      "wickets": 4,
      "economy": 4.8,
      "average": 16.8,
      "form_rating": "ELITE_FORM"
    },
    "at_venue": {
      "matches": 5,
      "overs": 22,
      "wickets": 9,
      "economy": 4.5,
      "average": 11.0,
      "venue_rating": "VENUE_SPECIALIST"
    }
  },
  "narrative": "Mendis is in steady batting form (avg 37.4 in last 10 innings) and has a strong record at this venue (avg 44.6 in 8 innings). He averages 37.3 against England in recent matches. A key batter who knows these conditions well."
}
```

#### Batting Form Rating Rules (ODI)

ODI batting benchmarks: Elite average > 45, Good average 30–45, Expected par ~30.

| Rating | Condition |
|---|---|
| `ELITE_FORM` | Average > 45 in last 10 innings |
| `IN_FORM` | Average 30–45 |
| `STEADY` | Average 18–30 |
| `OUT_OF_FORM` | Average < 18 AND innings >= 5 |
| `DNB` | Did not bat in filter window |
| `SMALL_SAMPLE` | < 5 innings in filter |

#### Batting Venue Rating Rules (ODI)

| Rating | Condition |
|---|---|
| `VENUE_SPECIALIST` | Average > 40 at venue AND innings >= 5 |
| `COMFORTABLE` | Average 25–40 at venue |
| `STRUGGLES_HERE` | Average < 18 at venue AND innings >= 4 |
| `NO_VENUE_DATA` | 0 innings at venue |

#### Bowling Form Rating Rules (ODI)

ODI bowling benchmarks: Elite economy < 4.5, Good economy 4.5–5.5, Par economy ~5.5, Expensive > 6.5. Elite average < 25, Good average 25–35.

| Rating | Condition |
|---|---|
| `ELITE_FORM` | Economy < 4.5 AND Wickets/Match >= 2.0 in last 10 matches |
| `IN_FORM` | Economy < 5.5 AND Wickets/Match >= 1.5 |
| `STEADY` | Economy 5.5–6.5 OR Wickets/Match between 1.0–1.5 |
| `EXPENSIVE` | Economy > 6.5 regardless of wickets |
| `OUT_OF_FORM` | Economy > 7.0 OR 0 wickets in last 5+ matches bowled |
| `DNB` | Did not bowl in filter window |
| `SMALL_SAMPLE` | < 5 matches bowled in filter |

#### Bowling Venue Rating Rules (ODI)

| Rating | Condition |
|---|---|
| `VENUE_SPECIALIST` | Average < 25 at venue AND Economy < 5.0 AND matches >= 3 |
| `EFFECTIVE` | Average 25–35 AND Economy < 5.5 at venue |
| `STRUGGLES_HERE` | Average > 45 OR Economy > 6.5 at venue AND matches >= 3 |
| `NO_VENUE_DATA` | 0 matches bowled at venue |

**Narrative must answer:** *"Is this player in form? Do they like this venue? How do they perform against this specific opponent?"*

---

### 4.3 Tactical Matrix (Batting vs Bowling Archetypes)

**Source:** `TacticalMatrix` from `compare_squads`
**Timeline:** All-Time (Career Stats)

#### A. Bowling Roster (Per Team)

Before the batter-vs-archetype matrix, the pack must list each team's bowling resources with their types. This tells the AI which bowling archetypes are actually present in the match.

**Output Schema:**
```json
{
  "bowling_roster": {
    "home": [
      { "bowler": "JDF Vandersay", "type": "Leg Spin", "role": "Lead Spinner" },
      { "bowler": "DN Wellalage", "type": "Slow Left-Arm Orthodox", "role": "2nd Spinner" },
      { "bowler": "DM de Silva", "type": "Off Spin", "role": "Part-Time Spinner" },
      { "bowler": "AM Fernando", "type": "Right-Arm Fast/Medium", "role": "Lead Pacer" }
    ],
    "away": [
      { "bowler": "AU Rashid", "type": "Leg Spin", "role": "Lead Spinner" },
      { "bowler": "J Overton", "type": "Right-Arm Fast/Medium", "role": "Lead Pacer" },
      { "bowler": "SM Curran", "type": "Left-Arm Fast/Medium", "role": "All-Rounder" }
    ],
    "pitch_suitability": {
      "home_spin_bowlers": 3,
      "away_spin_bowlers": 1,
      "verdict": "HOME_SPIN_ADVANTAGE",
      "narrative": "Sri Lanka have 3 specialist spinners (Vandersay, Wellalage, de Silva) vs England's lone spinner Rashid. On this dry, turning pitch, SL's bowling attack is far better suited to the conditions."
    }
  }
}
```

#### B. Batter vs Archetype Matrix

**Output Schema (per batter):**
```json
{
  "player": "BKG Mendis",
  "role": "Top-Order Batter",
  "vs_archetypes": {
    "leg_spin": { "avg": 65.8, "balls_faced": 94, "rating": "ELITE" },
    "right_arm_fast": { "avg": 33.0, "balls_faced": 87, "rating": "MODERATE" },
    "off_spin": { "avg": 71.8, "balls_faced": 95, "rating": "ELITE" },
    "slow_left_arm": { "avg": 42.4, "balls_faced": 72, "rating": "STRONG" },
    "left_arm_fast": { "avg": 75.0, "balls_faced": 90, "rating": "ELITE" }
  },
  "relevant_opponent_bowlers": ["AU Rashid (Leg Spin)", "J Overton (RAF/M)"],
  "narrative": "Mendis is excellent against spin (avg 65.8 vs Leg Spin, 71.8 vs Off Spin) but vulnerable to right-arm pace (avg 33.0). England's Rashid (Leg Spin) is unlikely to trouble him, but Overton (pace) could exploit his weakness."
}
```

**Rating Rules:**
| Rating | Average |
|---|---|
| `ELITE` | > 60 AND balls > 50 |
| `STRONG` | 40–60 AND balls > 30 |
| `MODERATE` | 25–40 |
| `VULNERABLE` | < 25 AND balls > 20 |
| `INSUFFICIENT_DATA` | balls < 15 |

**No HTML. No `<span>` tags. Raw numbers only.**

**Narrative must answer:** *"Which bowler types threaten this batter, and does the opposition actually have those bowlers in their XI?"*

---

### 4.4 Head-to-Head Matchups (Batter vs Specific Bowler)

**Source:** `Matchups` from `compare_squads`
**Timeline:** All-Time (Career Stats)

**Output Schema:**
```json
{
  "matchup": "BKG Mendis vs AU Rashid",
  "data": {
    "balls_faced": 45,
    "runs_scored": 38,
    "dismissals": 2,
    "average": 19.0,
    "strike_rate": 84.4
  },
  "context": {
    "tag": "BUNNY_ALERT",
    "danger_level": "HIGH"
  },
  "narrative": "Rashid has dismissed Mendis twice in 45 balls at an average of just 19. Given the spin-friendly conditions, this is a critical matchup — England should use Rashid early against Mendis."
}
```

**Tag Rules:**
| Tag | Condition |
|---|---|
| `BUNNY_ALERT` | Dismissals ≥ 3 AND Average < 20 |
| `HIGH_RISK` | Dismissals ≥ 2 AND Average < 25 |
| `PLAYER_DOMINANCE` | Average > 50 AND SR > 100 |
| `SAFE_MATCHUP` | Dismissals = 0 AND Balls > 12 |
| `SMALL_SAMPLE` | Balls < 12 |

---

## 📋 IMPLEMENTATION CHECKLIST

### Data Transformation Layer (New Requirement)
The core engines return Jupyter-formatted data (lists, HTML). A **transformation layer** must sit between the engine and the JSON:

```
Engine Output (raw) → Transformer (strip HTML, restructure) → Interpreter (add context) → JSON
```

1. `_transform_h2h_report(raw_list)` → Converts flat `[{Metric,Value}]` into nested dict.
2. `_transform_tactical_matrix(raw_list)` → Strips `<span>` HTML and extracts `_raw` values.
3. `_transform_matchups(raw_dict)` → Cleans and restructures matchup data.

### File Ownership

| File | Responsibility |
|---|---|
| `reports/match_pack_generator.py` | Orchestrator — calls engines, applies transformers, writes JSON |
| `core/interpreter.py` | Context engine — adds tags, narratives, condition weights |
| `core/transformer.py` | **NEW** — converts raw engine output into clean structured dicts |
| `interface.py` | UI trigger — Match Context inputs + Generate button |

---

## ✅ QUALITY GATE (Definition of Done)

A generated Match Pack **passes** if:
1. ✅ JSON is valid and parseable by `json.load()`.
2. ✅ Every section has `data`, `context`, and `narrative` keys.
3. ✅ Zero HTML tags anywhere in the JSON.
4. ✅ Zero `[{Metric, Value}]` flat lists — all data is structured dicts.
5. ✅ `Executive_Summary` exists with `prediction`, `key_factors`, and `risk_alerts`.
6. ✅ `MATCH_IDS` are in `_debug`, not in analytical sections.
7. ✅ Condition weights correctly reflect the pitch/time/toss inputs.
8. ✅ Narratives are specific (contain numbers), not generic ("Team A is dominant").
