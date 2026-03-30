# Venue Bias Overhaul — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enrich `analyze_venue_bias` from a raw win-count aggregator into a statistically rigorous, trader-actionable venue intelligence tool — and replace the generic `ReportCard` renderer with a purpose-built `VenueBiasCard` that surfaces all enriched signals clearly.

**Architecture:** Six new helper functions added to `venue_calculator.py` each own one enrichment concern (confidence interval, sample reliability, score distribution, score extremes, bias trend, toss intelligence). `VenueBiasReport` TypedDict is extended with their outputs. A new `venue_bias_card` output type is registered in the manifest and wired to a new `VenueBiasCard` React component.

**Tech Stack:** Python / pandas (backend), TypeScript / React / Tailwind CSS tokens (frontend), pytest (tests)

---

## Scope Note

This plan has two independent phases: **Backend** (Tasks 1–4) and **Frontend** (Tasks 5–7). Backend can be completed and tested in isolation before the frontend is touched. The frontend depends on the extended `VenueBiasReport` shape produced by the backend.

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `core/interfaces/team_types.py` | Add 6 new TypedDicts + extend `VenueBiasReport` |
| Modify | `core/calculators/team/venue_calculator.py` | Add 6 helper functions, call them in `_build_bias_report` |
| Modify | `formats/odi/manifest.py` | Register `venue_bias_card` output type; update `venue_bias` function entry |
| Create | `tests/test_venue_bias_enrichment.py` | Unit tests for every new helper |
| Create | `frontend/components/renderers/VenueBiasCard.tsx` | Dedicated renderer for enriched bias data |
| Modify | `frontend/lib/types.ts` | Add `VenueBiasData` TypeScript interface |
| Modify | `frontend/components/renderers/FunctionRenderer.tsx` | Add `venue_bias_card` case |

---

## Task 1: Extend TypedDicts in `team_types.py`

**Files:**
- Modify: `core/interfaces/team_types.py` (find `class VenueBiasReport`)

- [ ] **Step 1: Write the failing import test**

Create `tests/test_venue_bias_enrichment.py`:

```python
"""Unit tests for enriched venue bias calculator helpers."""
import pytest
import pandas as pd
from core.calculators.team.venue_calculator import (
    _wilson_confidence_interval,
    _sample_reliability,
    _score_stats,
    _score_distribution,
    _score_extremes,
    _bias_trend,
    _toss_intelligence,
)
```

- [ ] **Step 2: Run to confirm ImportError**

```bash
pytest tests/test_venue_bias_enrichment.py -v
```
Expected: `ImportError` — helpers don't exist yet.

- [ ] **Step 3: Add TypedDicts before `VenueBiasReport` in `team_types.py`**

Locate `class VenueBiasReport(TypedDict):` (~line 349). Insert immediately before it:

```python
class VenueBiasCI(TypedDict):
    lower: int
    upper: int

class VenueScoreStats(TypedDict):
    min: int
    max: int
    median: int
    std: int

class VenueScoreDistribution(TypedDict):
    inn1: VenueScoreStats
    inn2: VenueScoreStats

class VenueScoreExtremes(TypedDict):
    lowest_defended: int | None
    highest_chased: int | None

class VenueBiasTrend(TypedDict):
    direction: str  # STRENGTHENING | WEAKENING | STABLE | INSUFFICIENT_DATA
    recent_pct: int | None
    historical_pct: int | None

class VenueTossIntelligence(TypedDict):
    chose_bat_win_pct: int | None
    chose_bowl_win_pct: int | None
    toss_match_count: int
    data_available: bool
```

- [ ] **Step 4: Extend `VenueBiasReport` with new fields**

Add these fields to `VenueBiasReport` (after `derived_badges`):

```python
confidence_interval: VenueBiasCI
sample_reliability: str
score_distribution: VenueScoreDistribution | None
score_extremes: VenueScoreExtremes
bias_trend: VenueBiasTrend
toss_intelligence: VenueTossIntelligence
```

- [ ] **Step 5: Commit**

```bash
git add core/interfaces/team_types.py tests/test_venue_bias_enrichment.py
git commit -m "feat(types): add enriched VenueBiasReport TypedDicts and test scaffold"
```

---

## Task 2: Implement helper functions in `venue_calculator.py`

**Files:**
- Modify: `core/calculators/team/venue_calculator.py` (add helpers above `_bias_verdict`)

- [ ] **Step 1: Write all helper unit tests first**

Append to `tests/test_venue_bias_enrichment.py`:

```python
# ── Wilson CI ───────────────────────────────────────────────────────────────

def test_wilson_ci_zero_denominator():
    result = _wilson_confidence_interval(0, 0)
    assert result == {"lower": 0, "upper": 0}

def test_wilson_ci_fifty_percent():
    result = _wilson_confidence_interval(5, 10)
    assert result["lower"] < 50 < result["upper"]

def test_wilson_ci_high_confidence():
    # 20/20 wins — upper must be 100, lower well above 50
    result = _wilson_confidence_interval(20, 20)
    assert result["lower"] > 70
    assert result["upper"] == 100

def test_wilson_ci_low_confidence():
    # 1/2 — very wide interval expected
    result = _wilson_confidence_interval(1, 2)
    assert result["upper"] - result["lower"] > 50

# ── Sample reliability ───────────────────────────────────────────────────────

def test_sample_reliability_low():
    assert _sample_reliability(8) == "LOW_SAMPLE"

def test_sample_reliability_boundary_low():
    assert _sample_reliability(9) == "LOW_SAMPLE"

def test_sample_reliability_moderate():
    assert _sample_reliability(10) == "MODERATE"
    assert _sample_reliability(24) == "MODERATE"

def test_sample_reliability_reliable():
    assert _sample_reliability(25) == "RELIABLE"
    assert _sample_reliability(100) == "RELIABLE"

# ── Score stats ──────────────────────────────────────────────────────────────

def test_score_stats_empty_series():
    result = _score_stats(pd.Series([], dtype=float))
    assert result == {"min": 0, "max": 0, "median": 0, "std": 0}

def test_score_stats_basic():
    result = _score_stats(pd.Series([200, 250, 300]))
    assert result["min"] == 200
    assert result["max"] == 300
    assert result["median"] == 250

# ── Score extremes ───────────────────────────────────────────────────────────

def _make_results_df(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)

def test_score_extremes_lowest_defended():
    df = _make_results_df([
        {"match_id": 1, "winner": "TeamA", "team_bat_1": "TeamA", "team_bat_2": "TeamB", "score_inn1": 220, "start_date": "2023-01-01"},
        {"match_id": 2, "winner": "TeamA", "team_bat_1": "TeamA", "team_bat_2": "TeamB", "score_inn1": 180, "start_date": "2023-01-02"},
        {"match_id": 3, "winner": "TeamB", "team_bat_1": "TeamA", "team_bat_2": "TeamB", "score_inn1": 310, "start_date": "2023-01-03"},
    ])
    result = _score_extremes(df)
    assert result["lowest_defended"] == 180

def test_score_extremes_highest_chased():
    df = _make_results_df([
        {"match_id": 1, "winner": "TeamB", "team_bat_1": "TeamA", "team_bat_2": "TeamB", "score_inn1": 310, "start_date": "2023-01-01"},
        {"match_id": 2, "winner": "TeamB", "team_bat_1": "TeamA", "team_bat_2": "TeamB", "score_inn1": 275, "start_date": "2023-01-02"},
        {"match_id": 3, "winner": "TeamA", "team_bat_1": "TeamA", "team_bat_2": "TeamB", "score_inn1": 220, "start_date": "2023-01-03"},
    ])
    result = _score_extremes(df)
    assert result["highest_chased"] == 310

def test_score_extremes_no_defended():
    # All matches won by chasing team
    df = _make_results_df([
        {"match_id": 1, "winner": "TeamB", "team_bat_1": "TeamA", "team_bat_2": "TeamB", "score_inn1": 300, "start_date": "2023-01-01"},
    ])
    result = _score_extremes(df)
    assert result["lowest_defended"] is None

# ── Bias trend ───────────────────────────────────────────────────────────────

def _make_trend_df(bat1_wins_per_half: tuple[int, int], total_per_half: int) -> pd.DataFrame:
    rows = []
    mid = pd.Timestamp("2021-01-01")
    for i in range(total_per_half):
        winner = "TeamA" if i < bat1_wins_per_half[0] else "TeamB"
        rows.append({"match_id": i, "winner": winner, "team_bat_1": "TeamA", "team_bat_2": "TeamB",
                     "score_inn1": 250, "start_date": pd.Timestamp("2019-01-01") + pd.Timedelta(days=i * 30)})
    for i in range(total_per_half):
        winner = "TeamA" if i < bat1_wins_per_half[1] else "TeamB"
        rows.append({"match_id": total_per_half + i, "winner": winner, "team_bat_1": "TeamA", "team_bat_2": "TeamB",
                     "score_inn1": 250, "start_date": mid + pd.Timedelta(days=i * 30)})
    return pd.DataFrame(rows)

def test_bias_trend_strengthening():
    df = _make_trend_df((6, 9), 10)  # historical 60%, recent 90%
    result = _bias_trend(df, 100)
    assert result["direction"] == "STRENGTHENING"
    assert result["recent_pct"] > result["historical_pct"]

def test_bias_trend_weakening():
    df = _make_trend_df((9, 4), 10)  # historical 90%, recent 40%
    result = _bias_trend(df, 100)
    assert result["direction"] == "WEAKENING"

def test_bias_trend_stable():
    df = _make_trend_df((6, 6), 10)  # historical 60%, recent 60%
    result = _bias_trend(df, 100)
    assert result["direction"] == "STABLE"

def test_bias_trend_insufficient_data():
    df = _make_trend_df((2, 2), 2)  # only 4 matches total
    result = _bias_trend(df, 100)
    assert result["direction"] == "INSUFFICIENT_DATA"
    assert result["recent_pct"] is None

# ── Toss intelligence ────────────────────────────────────────────────────────

def test_toss_intelligence_no_columns():
    df = pd.DataFrame([{"match_id": 1, "winner": "A", "team_bat_1": "A", "team_bat_2": "B"}])
    result = _toss_intelligence(df, 100)
    assert result["data_available"] is False
    assert result["chose_bat_win_pct"] is None

def test_toss_intelligence_chose_bat_wins():
    df = pd.DataFrame([
        {"match_id": i, "winner": "TeamA", "team_bat_1": "TeamA", "team_bat_2": "TeamB",
         "toss_winner": "TeamA", "toss_decision": "bat", "start_date": "2023-01-01"}
        for i in range(4)
    ] + [
        {"match_id": 10 + i, "winner": "TeamB", "team_bat_1": "TeamA", "team_bat_2": "TeamB",
         "toss_winner": "TeamA", "toss_decision": "bat", "start_date": "2023-01-01"}
        for i in range(1)
    ])
    result = _toss_intelligence(df, 100)
    assert result["data_available"] is True
    assert result["chose_bat_win_pct"] == 80  # 4/5

def test_toss_intelligence_mixed_decisions():
    df = pd.DataFrame([
        {"match_id": 1, "winner": "TeamA", "team_bat_1": "TeamA", "team_bat_2": "TeamB",
         "toss_winner": "TeamA", "toss_decision": "bat", "start_date": "2023-01-01"},
        {"match_id": 2, "winner": "TeamA", "team_bat_1": "TeamB", "team_bat_2": "TeamA",
         "toss_winner": "TeamA", "toss_decision": "field", "start_date": "2023-01-02"},
    ])
    result = _toss_intelligence(df, 100)
    assert result["data_available"] is True
    assert result["chose_bat_win_pct"] == 100
    assert result["chose_bowl_win_pct"] == 100
```

- [ ] **Step 2: Run tests — all should fail with ImportError**

```bash
pytest tests/test_venue_bias_enrichment.py -v
```
Expected: All fail, `ImportError`.

- [ ] **Step 3: Implement all helpers in `venue_calculator.py`**

Insert the following block directly above `def _bias_verdict` (~line 317):

```python
def _wilson_confidence_interval(wins: int, total: int, z: float = 1.96) -> dict[str, int]:
    if total == 0:
        return {"lower": 0, "upper": 0}
    p = wins / total
    z2n = z**2 / total
    centre = (p + z2n / 2) / (1 + z2n)
    margin = (z * (p * (1 - p) / total + z2n / (4 * total)) ** 0.5) / (1 + z2n)
    return {
        "lower": max(0, int((centre - margin) * 100)),
        "upper": min(100, int((centre + margin) * 100)),
    }


def _sample_reliability(total: int) -> str:
    if total < 10:
        return "LOW_SAMPLE"
    if total < 25:
        return "MODERATE"
    return "RELIABLE"


def _score_stats(scores: "pd.Series") -> dict[str, int]:
    clean = scores.dropna()
    if clean.empty:
        return {"min": 0, "max": 0, "median": 0, "std": 0}
    return {
        "min": int(clean.min()),
        "max": int(clean.max()),
        "median": int(clean.median()),
        "std": int(clean.std()),
    }


def _score_distribution(valid_stats: "pd.DataFrame") -> "dict | None":
    if valid_stats.empty:
        return None
    return {
        "inn1": _score_stats(valid_stats["score_inn1"].dropna()),
        "inn2": _score_stats(valid_stats["score_inn2"].dropna()),
    }


def _score_extremes(valid_results: "pd.DataFrame") -> "dict[str, int | None]":
    matches_first = valid_results.groupby("match_id").first()
    defended = matches_first.loc[matches_first["winner"] == matches_first["team_bat_1"], "score_inn1"]
    chased = matches_first.loc[matches_first["winner"] == matches_first["team_bat_2"], "score_inn1"]
    return {
        "lowest_defended": int(defended.min()) if not defended.empty else None,
        "highest_chased": int(chased.max()) if not chased.empty else None,
    }


def _bias_trend(valid_results: "pd.DataFrame", percent_scale: int) -> dict:
    matches_first = valid_results.groupby("match_id").first().reset_index()
    if len(matches_first) < 6:
        return {"direction": "INSUFFICIENT_DATA", "recent_pct": None, "historical_pct": None}
    matches_first = matches_first.sort_values("start_date")
    midpoint = len(matches_first) // 2
    historical = matches_first.iloc[:midpoint]
    recent = matches_first.iloc[midpoint:]

    def _bat1_pct(df: "pd.DataFrame") -> int:
        wins = int((df["winner"] == df["team_bat_1"]).sum())
        return _safe_percent(wins, len(df), percent_scale)

    h_pct = _bat1_pct(historical)
    r_pct = _bat1_pct(recent)
    gap = r_pct - h_pct
    direction = "STRENGTHENING" if gap >= 6 else ("WEAKENING" if gap <= -6 else "STABLE")
    return {"direction": direction, "recent_pct": r_pct, "historical_pct": h_pct}


def _toss_intelligence(valid_results: "pd.DataFrame", percent_scale: int) -> dict:
    if "toss_winner" not in valid_results.columns or "toss_decision" not in valid_results.columns:
        return {"chose_bat_win_pct": None, "chose_bowl_win_pct": None, "toss_match_count": 0, "data_available": False}
    matches_first = valid_results.groupby("match_id").first().reset_index()
    toss_df = matches_first.dropna(subset=["toss_winner", "toss_decision"])
    if toss_df.empty:
        return {"chose_bat_win_pct": None, "chose_bowl_win_pct": None, "toss_match_count": 0, "data_available": False}

    decision = toss_df["toss_decision"].str.lower()
    bat_df = toss_df[decision.str.contains("bat", na=False)]
    bowl_df = toss_df[decision.str.contains("bowl|field", na=False)]

    def _toss_win_pct(df: "pd.DataFrame") -> "int | None":
        if df.empty:
            return None
        wins = int((df["winner"] == df["toss_winner"]).sum())
        return _safe_percent(wins, len(df), percent_scale)

    return {
        "chose_bat_win_pct": _toss_win_pct(bat_df),
        "chose_bowl_win_pct": _toss_win_pct(bowl_df),
        "toss_match_count": len(toss_df),
        "data_available": True,
    }
```

- [ ] **Step 4: Run tests — all helpers should now pass**

```bash
pytest tests/test_venue_bias_enrichment.py -v
```
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add core/calculators/team/venue_calculator.py tests/test_venue_bias_enrichment.py
git commit -m "feat(calculator): add venue bias enrichment helpers with tests"
```

---

## Task 3: Wire helpers into `_build_bias_report`

**Files:**
- Modify: `core/calculators/team/venue_calculator.py` — update `_build_bias_report`

- [ ] **Step 1: Write integration test for the full payload shape**

Append to `tests/test_venue_bias_enrichment.py`:

```python
# ── Full payload integration ─────────────────────────────────────────────────

def _make_full_df() -> pd.DataFrame:
    """12-match dataset with toss data, scores, and dates spanning 3 years."""
    rows = []
    for i in range(12):
        bat_first_wins = i % 3 != 0  # 8 bat-first wins, 4 chase wins
        rows.append({
            "match_id": i,
            "winner": "TeamA" if bat_first_wins else "TeamB",
            "team_bat_1": "TeamA",
            "team_bat_2": "TeamB",
            "score_inn1": 240 + i * 5,
            "score_inn2": 220 + i * 4,
            "balls_inn1": 300,
            "balls_inn2": 280,
            "toss_winner": "TeamA",
            "toss_decision": "bat" if i % 2 == 0 else "field",
            "start_date": pd.Timestamp("2021-01-01") + pd.Timedelta(days=i * 60),
            "venue": "Test Ground",
            "venue_id": "test_ground",
        })
    return pd.DataFrame(rows)


def test_full_bias_report_has_enriched_fields():
    from core.calculators.team.venue_calculator import calculate_venue_bias_payload
    import pandas as pd

    df = _make_full_df()
    ctx = {
        "stadium_id": "test_ground",
        "years_back": 5,
        "reference_date": pd.Timestamp("2024-01-01"),
        "min_balls_for_completed_innings": 200,
        "percent_scale": 100,
        "bias_win_pct_min": 55,
        "strong_bias_gap_min": 15,
    }
    result = calculate_venue_bias_payload(df, ctx)
    report = result["report"]
    assert report is not None
    assert "confidence_interval" in report
    assert "lower" in report["confidence_interval"]
    assert "upper" in report["confidence_interval"]
    assert "sample_reliability" in report
    assert report["sample_reliability"] == "MODERATE"  # 12 matches
    assert "score_distribution" in report
    assert report["score_distribution"] is not None
    assert "inn1" in report["score_distribution"]
    assert "score_extremes" in report
    assert "lowest_defended" in report["score_extremes"]
    assert "highest_chased" in report["score_extremes"]
    assert "bias_trend" in report
    assert report["bias_trend"]["direction"] in ("STRENGTHENING", "WEAKENING", "STABLE", "INSUFFICIENT_DATA")
    assert "toss_intelligence" in report
    assert report["toss_intelligence"]["data_available"] is True
```

- [ ] **Step 2: Run — should fail because `_build_bias_report` doesn't return new fields yet**

```bash
pytest tests/test_venue_bias_enrichment.py::test_full_bias_report_has_enriched_fields -v
```
Expected: FAIL — KeyError on `confidence_interval`.

- [ ] **Step 3: Update `_build_bias_report` to call all helpers**

In `venue_calculator.py`, find `_build_bias_report` (~line 347). Replace the `report` dict construction with:

```python
def _build_bias_report(
    valid_results: pd.DataFrame,
    valid_stats: pd.DataFrame,
    context: VenueBiasContext,
    bat1_wins: int,
    chase_wins: int,
    bat1_pct: int,
    chase_pct: int,
) -> VenueBiasReport:
    venue_id = VenueService._resolve_venue_output_label(valid_results, context["stadium_id"])
    total = int(valid_results["match_id"].nunique())
    tie_nr_pct = max(0, context["percent_scale"] - bat1_pct - chase_pct)
    report: VenueBiasReport = {
        "venue_id": venue_id,
        "period": context["years_back"],
        "total_matches": total,
        "bat1_wins": bat1_wins,
        "chase_wins": chase_wins,
        "bat1_win_pct": bat1_pct,
        "chase_win_pct": chase_pct,
        "bias_verdict": _bias_verdict(bat1_pct, chase_pct, context["bias_win_pct_min"]),
        "avg_1st_inn": _normalize_none_marker(ReportBuilder._get_avg_with_count(valid_stats, "score_inn1")),
        "avg_2nd_inn": _normalize_none_marker(ReportBuilder._get_avg_with_count(valid_stats, "score_inn2")),
        "percent_breakdown": {"bat_first": bat1_pct, "chase": chase_pct, "tie_nr": tie_nr_pct},
        "highlight_flags": {"has_strong_bias": abs(bat1_pct - chase_pct) >= context["strong_bias_gap_min"]},
        "derived_badges": [],
        "MATCH_IDS": ",".join(valid_results["match_id"].astype(str).unique().tolist()) or None,
        "raw_matches": SerializationService.serialize_raw_matches(valid_results),
        # Enrichments
        "confidence_interval": _wilson_confidence_interval(bat1_wins, total),
        "sample_reliability": _sample_reliability(total),
        "score_distribution": _score_distribution(valid_stats),
        "score_extremes": _score_extremes(valid_results),
        "bias_trend": _bias_trend(valid_results, context["percent_scale"]),
        "toss_intelligence": _toss_intelligence(valid_results, context["percent_scale"]),
    }
    return report
```

- [ ] **Step 4: Run the full test suite**

```bash
pytest tests/test_venue_bias_enrichment.py -v
```
Expected: All PASS.

- [ ] **Step 5: Run existing match pack tests to confirm no regressions**

```bash
pytest tests/test_match_pack.py -v
```
Expected: All PASS.

- [ ] **Step 6: Commit**

```bash
git add core/calculators/team/venue_calculator.py tests/test_venue_bias_enrichment.py
git commit -m "feat(calculator): wire enriched fields into _build_bias_report"
```

---

## Task 4: Register `venue_bias_card` output type in manifest

**Files:**
- Modify: `formats/odi/manifest.py`

- [ ] **Step 1: Add `venue_bias_card` to `output_types` list**

Find the `"output_types"` list (~line 192). Add `"venue_bias_card"` to it:

```python
"output_types": [
    "report",
    "table",
    "squad_comparison",
    "comparison_table",
    "matrix_table",
    "form_table",
    "profile_card",
    "prediction_card",
    "matchup_table",
    "download_json",
    "phase_analysis",
    "venue_matchup_report",
    "home_fortress",
    "venue_bias_card",   # <-- add this
],
```

- [ ] **Step 2: Update the `venue_bias` function entry's `output_type`**

Find the `venue_bias` function entry (~line 226). Change `"output_type": "report"` to `"output_type": "venue_bias_card"`. Also update `discover_bullets` to reflect the enriched output:

```python
{
    "key": "venue_bias",
    "label": "Toss/Bias Analysis",
    "icon": "coin",
    "engine_class": "TeamEngine",
    "engine_method": "analyze_venue_bias",
    "required_context": ["venue", "years"],
    "output_type": "venue_bias_card",
    "output_schema": {
        "type": "key_value_list",
        "fields": [
            "venue_id", "total_matches", "bat1_win_pct", "chase_win_pct",
            "bias_verdict", "sample_reliability", "confidence_interval",
            "score_distribution", "score_extremes", "bias_trend", "toss_intelligence",
        ],
    },
    "discover_bullets": [
        "Bat-first vs chase win split with a 95% confidence interval — know how reliable the number is",
        "Score extremes: the lowest total ever defended and highest ever chased at this ground",
        "Bias trend: whether the venue's toss advantage is strengthening or weakening over time",
        "Toss intelligence: win rate when the toss winner chose to bat vs chose to bowl",
    ],
},
```

- [ ] **Step 3: Run execute schema tests to ensure manifest is still valid**

```bash
pytest tests/test_etl_integrity_gates.py -v -k "manifest"
```
Expected: PASS (or no manifest-specific tests — check output).

- [ ] **Step 4: Commit**

```bash
git add formats/odi/manifest.py
git commit -m "feat(manifest): register venue_bias_card output type"
```

---

## Task 5: Add `VenueBiasData` TypeScript type

**Files:**
- Modify: `frontend/lib/types.ts`

- [ ] **Step 1: Read `frontend/lib/types.ts` and find where to add the type**

Look for existing venue-related types or the end of the type definitions block.

- [ ] **Step 2: Add the interface**

```typescript
export interface VenueBiasCI {
    lower: number;
    upper: number;
}

export interface VenueScoreStats {
    min: number;
    max: number;
    median: number;
    std: number;
}

export interface VenueScoreDistribution {
    inn1: VenueScoreStats;
    inn2: VenueScoreStats;
}

export interface VenueScoreExtremes {
    lowest_defended: number | null;
    highest_chased: number | null;
}

export interface VenueBiasTrend {
    direction: "STRENGTHENING" | "WEAKENING" | "STABLE" | "INSUFFICIENT_DATA";
    recent_pct: number | null;
    historical_pct: number | null;
}

export interface VenueTossIntelligence {
    chose_bat_win_pct: number | null;
    chose_bowl_win_pct: number | null;
    toss_match_count: number;
    data_available: boolean;
}

export interface VenueBiasData {
    venue_id: string;
    period: number;
    total_matches: number;
    bat1_wins: number;
    chase_wins: number;
    bat1_win_pct: number;
    chase_win_pct: number;
    bias_verdict: string;
    avg_1st_inn: string | number | null;
    avg_2nd_inn: string | number | null;
    percent_breakdown: { bat_first: number; chase: number; tie_nr: number };
    highlight_flags: { has_strong_bias: boolean };
    confidence_interval: VenueBiasCI;
    sample_reliability: "LOW_SAMPLE" | "MODERATE" | "RELIABLE";
    score_distribution: VenueScoreDistribution | null;
    score_extremes: VenueScoreExtremes;
    bias_trend: VenueBiasTrend;
    toss_intelligence: VenueTossIntelligence;
}
```

- [ ] **Step 3: Run type-check**

```bash
cd frontend && npx tsc --noEmit
```
Expected: No new errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/lib/types.ts
git commit -m "feat(types): add VenueBiasData TypeScript interface"
```

---

## Task 6: Build `VenueBiasCard` component

**Files:**
- Create: `frontend/components/renderers/VenueBiasCard.tsx`

The component has five visual sections stacked vertically. Read `frontend/components/renderers/FortressReport.tsx` before implementing — follow the same token and layout conventions used there.

**Visual structure:**

```
[1] HERO ROW
    Venue name (large) + verdict badge (BAT FIRST / BOWL FIRST / NEUTRAL)
    Subtitle: "N matches · Y years" + sample reliability chip

[2] WIN SPLIT BAR
    "BAT FIRST N%"  [████████████░░░░░░] "CHASE N%"
    Below bar: "95% confidence: Lo%–Hi%"

[3] SCORE INTEL GRID  (2 columns)
    Col 1: Avg 1st Inn / min / max / σ
    Col 2: Avg 2nd Inn / min / max / σ
    Col 3: Lowest Defended (or — if null)
    Col 4: Highest Chased (or — if null)

[4] BIAS TREND STRIP
    "Historical N% → Recent N%  [ARROW] DIRECTION"
    Hidden if direction === "INSUFFICIENT_DATA"

[5] TOSS INTELLIGENCE PANEL
    "Chose to Bat: N% win  |  Chose to Bowl: N% win  (N matches)"
    Hidden if data_available === false
```

- [ ] **Step 1: Create `VenueBiasCard.tsx`**

```tsx
"use client";

import { Shield, Target, TrendingUp, TrendingDown, Minus, AlertTriangle } from "lucide-react";
import CountUp from "@/components/common/CountUp";
import EmptyState from "@/components/common/EmptyState";
import type { VenueBiasData } from "@/lib/types";

interface VenueBiasCardProps {
    data: Record<string, unknown>;
}

function isVenueBiasData(d: Record<string, unknown>): d is VenueBiasData {
    return typeof d.bat1_win_pct === "number" && typeof d.chase_win_pct === "number";
}

const RELIABILITY_STYLES: Record<string, string> = {
    LOW_SAMPLE: "badge-caution",
    MODERATE: "badge-neutral",
    RELIABLE: "badge-elite",
};

const RELIABILITY_LABELS: Record<string, string> = {
    LOW_SAMPLE: "Low sample",
    MODERATE: "Moderate sample",
    RELIABLE: "Reliable sample",
};

const TREND_ICON = {
    STRENGTHENING: <TrendingUp size={14} />,
    WEAKENING: <TrendingDown size={14} />,
    STABLE: <Minus size={14} />,
    INSUFFICIENT_DATA: <Minus size={14} />,
};

const TREND_LABEL: Record<string, string> = {
    STRENGTHENING: "Strengthening",
    WEAKENING: "Weakening",
    STABLE: "Stable",
    INSUFFICIENT_DATA: "Insufficient data",
};

function StatCell({ label, value, sub }: { label: string; value: string | number | null; sub?: string }) {
    return (
        <div className="py-3.5 px-4 [background:var(--bg-elevated)] [border-radius:var(--radius-md)] [border:1px_solid_var(--border-subtle)]">
            <div className="text-[0.7rem] tracking-[0.05em] [color:var(--text-disabled)] font-semibold uppercase mb-1">
                {label}
            </div>
            <div className="text-[1.15rem] font-extrabold [color:var(--text-primary)] font-data">
                {value === null || value === undefined ? (
                    <span className="[color:var(--text-disabled)]">—</span>
                ) : typeof value === "number" ? (
                    <CountUp end={value} decimals={0} duration={1.0} />
                ) : (
                    value
                )}
            </div>
            {sub && (
                <div className="text-[0.7rem] [color:var(--text-disabled)] mt-0.5 font-data">{sub}</div>
            )}
        </div>
    );
}

export default function VenueBiasCard({ data }: VenueBiasCardProps) {
    if (!data || !isVenueBiasData(data)) {
        return <EmptyState message="No bias data available." />;
    }

    const {
        venue_id,
        total_matches,
        period,
        bat1_win_pct,
        chase_win_pct,
        bias_verdict,
        sample_reliability,
        confidence_interval,
        score_distribution,
        score_extremes,
        bias_trend,
        toss_intelligence,
        percent_breakdown,
    } = data;

    const tieNrPct = percent_breakdown?.tie_nr ?? 0;
    const verdictLabel = bias_verdict === "bat_first"
        ? "Bat First Venue"
        : bias_verdict === "bowl_first"
        ? "Bowl First Venue"
        : "Neutral Venue";
    const verdictClass = bias_verdict === "bat_first"
        ? "[color:var(--accent-primary)] [border-color:var(--border-accent)] [background:var(--accent-glow)]"
        : bias_verdict === "bowl_first"
        ? "[color:var(--accent-secondary)] [border-color:var(--accent-secondary)] [background:var(--bg-active)]"
        : "[color:var(--text-secondary)] [border-color:var(--border-subtle)] [background:var(--glass-bg)]";

    return (
        <div className="flex flex-col gap-5">

            {/* 1. HERO ROW */}
            <div className="flex items-start justify-between flex-wrap gap-3">
                <div>
                    <div className="text-[0.7rem] tracking-[0.06em] [color:var(--text-disabled)] font-semibold uppercase mb-1">
                        Venue
                    </div>
                    <div className="text-xl font-bold [color:var(--text-primary)]">{venue_id}</div>
                    <div className="text-[0.78rem] [color:var(--text-disabled)] mt-1">
                        <span className="font-data">{total_matches}</span> matches · <span className="font-data">{period}</span> years
                    </div>
                </div>
                <div className="flex flex-col items-end gap-2">
                    <div className={`inline-flex items-center gap-1.5 py-1.5 px-3.5 [border-radius:var(--radius-lg)] border font-bold text-[0.82rem] tracking-[0.03em] ${verdictClass}`}>
                        {bias_verdict === "bat_first" ? <Shield size={14} /> : bias_verdict === "bowl_first" ? <Target size={14} /> : <TrendingUp size={14} />}
                        {verdictLabel}
                    </div>
                    {sample_reliability && (
                        <span className={`badge ${RELIABILITY_STYLES[sample_reliability] ?? "badge-neutral"} text-[0.7rem]`}>
                            {RELIABILITY_LABELS[sample_reliability] ?? sample_reliability}
                        </span>
                    )}
                </div>
            </div>

            {/* 2. WIN SPLIT BAR */}
            <div className="[background:var(--bg-elevated)] [border-radius:var(--radius-lg)] px-5 py-4 [border:1px_solid_var(--border-subtle)]">
                <div className="flex justify-between mb-2.5 text-[0.82rem] font-bold">
                    <span className="[color:var(--accent-primary)]">
                        <Shield size={13} className="inline align-middle mr-1" />
                        Bat First <span className="font-data">{bat1_win_pct}%</span>
                    </span>
                    {tieNrPct > 0 && (
                        <span className="[color:var(--text-disabled)] text-[0.75rem]">
                            Tie/NR <span className="font-data">{tieNrPct}%</span>
                        </span>
                    )}
                    <span className="[color:var(--accent-secondary)]">
                        Chase <span className="font-data">{chase_win_pct}%</span>
                        <Target size={13} className="inline align-middle ml-1" />
                    </span>
                </div>
                <div className="flex h-2.5 rounded-full overflow-hidden [background:var(--bg-active)]">
                    <div
                        className="[background:linear-gradient(90deg,_var(--accent-primary),_var(--accent-tertiary))] transition-[width] duration-500 ease-out"
                        style={{ width: `${bat1_win_pct}%` }}
                    />
                    {tieNrPct > 0 && (
                        <div
                            className="[background:var(--text-disabled)] opacity-40 transition-[width] duration-500 ease-out"
                            style={{ width: `${tieNrPct}%` }}
                        />
                    )}
                    <div
                        className="[background:linear-gradient(90deg,_var(--accent-secondary),_var(--accent-primary))] transition-[width] duration-500 ease-out"
                        style={{ width: `${chase_win_pct}%` }}
                    />
                </div>
                {confidence_interval && (
                    <div className="mt-2 text-[0.72rem] [color:var(--text-disabled)] text-center">
                        95% confidence: <span className="font-data [color:var(--text-secondary)]">{confidence_interval.lower}%</span>
                        {" – "}
                        <span className="font-data [color:var(--text-secondary)]">{confidence_interval.upper}%</span>
                        {" "}bat-first
                    </div>
                )}
            </div>

            {/* 3. SCORE INTEL GRID */}
            <div className="grid grid-cols-[repeat(auto-fill,minmax(160px,1fr))] gap-2.5">
                <StatCell
                    label="Avg 1st Inn"
                    value={score_distribution?.inn1.median ?? null}
                    sub={score_distribution ? `min ${score_distribution.inn1.min} · max ${score_distribution.inn1.max} · σ${score_distribution.inn1.std}` : undefined}
                />
                <StatCell
                    label="Avg 2nd Inn"
                    value={score_distribution?.inn2.median ?? null}
                    sub={score_distribution ? `min ${score_distribution.inn2.min} · max ${score_distribution.inn2.max} · σ${score_distribution.inn2.std}` : undefined}
                />
                <StatCell
                    label="Lowest Defended"
                    value={score_extremes?.lowest_defended ?? null}
                />
                <StatCell
                    label="Highest Chased"
                    value={score_extremes?.highest_chased ?? null}
                />
            </div>

            {/* 4. BIAS TREND STRIP */}
            {bias_trend && bias_trend.direction !== "INSUFFICIENT_DATA" && (
                <div className="flex items-center gap-2.5 px-4 py-3 [background:var(--bg-elevated)] [border-radius:var(--radius-md)] [border:1px_solid_var(--border-subtle)]">
                    <div className="text-[0.7rem] tracking-[0.05em] [color:var(--text-disabled)] font-semibold uppercase min-w-[80px]">
                        Bias Trend
                    </div>
                    <div className="text-[0.82rem] [color:var(--text-secondary)] font-data">
                        Historical <span className="[color:var(--text-primary)] font-bold">{bias_trend.historical_pct}%</span>
                        {" → "}
                        Recent <span className="[color:var(--text-primary)] font-bold">{bias_trend.recent_pct}%</span>
                    </div>
                    <div className={`inline-flex items-center gap-1 text-[0.78rem] font-bold ml-auto ${
                        bias_trend.direction === "STRENGTHENING"
                            ? "[color:var(--accent-positive)]"
                            : bias_trend.direction === "WEAKENING"
                            ? "[color:var(--accent-warning)]"
                            : "[color:var(--text-disabled)]"
                    }`}>
                        {TREND_ICON[bias_trend.direction]}
                        {TREND_LABEL[bias_trend.direction]}
                    </div>
                </div>
            )}

            {/* 5. TOSS INTELLIGENCE PANEL */}
            {toss_intelligence?.data_available && (
                <div className="px-4 py-3.5 [background:var(--bg-elevated)] [border-radius:var(--radius-md)] [border:1px_solid_var(--border-subtle)]">
                    <div className="text-[0.7rem] tracking-[0.05em] [color:var(--text-disabled)] font-semibold uppercase mb-2.5">
                        Toss Intelligence · <span className="font-data">{toss_intelligence.toss_match_count}</span> matches with toss data
                    </div>
                    <div className="flex gap-6 flex-wrap">
                        <div>
                            <div className="text-[0.72rem] [color:var(--text-disabled)]">Chose to Bat</div>
                            <div className="text-[1.1rem] font-extrabold [color:var(--accent-primary)] font-data">
                                {toss_intelligence.chose_bat_win_pct !== null ? `${toss_intelligence.chose_bat_win_pct}%` : "—"}
                            </div>
                            <div className="text-[0.68rem] [color:var(--text-disabled)]">toss winner win rate</div>
                        </div>
                        <div className="w-px [background:var(--border-subtle)] self-stretch" />
                        <div>
                            <div className="text-[0.72rem] [color:var(--text-disabled)]">Chose to Bowl</div>
                            <div className="text-[1.1rem] font-extrabold [color:var(--accent-secondary)] font-data">
                                {toss_intelligence.chose_bowl_win_pct !== null ? `${toss_intelligence.chose_bowl_win_pct}%` : "—"}
                            </div>
                            <div className="text-[0.68rem] [color:var(--text-disabled)]">toss winner win rate</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Low sample warning */}
            {sample_reliability === "LOW_SAMPLE" && (
                <div className="flex items-center gap-2 px-3.5 py-2.5 [background:var(--bg-active)] [border-radius:var(--radius-md)] [border:1px_solid_var(--accent-warning)] [color:var(--accent-warning)] text-[0.78rem]">
                    <AlertTriangle size={14} />
                    Fewer than 10 matches — treat all percentages as indicative only.
                </div>
            )}
        </div>
    );
}
```

- [ ] **Step 2: Run type-check**

```bash
cd frontend && npx tsc --noEmit
```
Expected: No errors.

- [ ] **Step 3: Run lint**

```bash
cd frontend && npx next lint
```
Expected: No errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/components/renderers/VenueBiasCard.tsx
git commit -m "feat(ui): add VenueBiasCard renderer for enriched bias data"
```

---

## Task 7: Wire `VenueBiasCard` into `FunctionRenderer`

**Files:**
- Modify: `frontend/components/renderers/FunctionRenderer.tsx`

- [ ] **Step 1: Add lazy import**

After line 24 (after `MatchAuditSection` import), add:

```tsx
const VenueBiasCard = lazy(() => import("./VenueBiasCard"));
```

- [ ] **Step 2: Add switch case**

Inside the `switch (outputType)` block, after the `"home_fortress"` case (~line 133), add:

```tsx
case "venue_bias_card":
    if (isJsonRecord(mainData)) {
        renderedOutput = wrapRenderer(<VenueBiasCard data={mainData} />, "Unable to render venue bias card.");
    }
    break;
```

- [ ] **Step 3: Run type-check and lint**

```bash
cd frontend && npx tsc --noEmit && npx next lint
```
Expected: Clean.

- [ ] **Step 4: Start dev server and visually verify**

```bash
cd frontend && npm run dev
```

Navigate to Venue Intelligence → Toss/Bias Analysis. Select any venue with good data (e.g., Wankhede, MCG). Verify:
- Hero row shows venue name, verdict badge, sample reliability chip
- Win split bar renders with confidence interval label below
- Score intel grid shows all 4 cells (Avg 1st, Avg 2nd, Lowest Defended, Highest Chased)
- Bias trend strip appears with direction and arrow
- Toss intelligence panel shows if toss data available
- Low sample warning appears for thin venues

- [ ] **Step 5: Run C5F self-audit items 1, 2, 3, 7, 8, 11, 12, 16**

Check `VenueBiasCard.tsx` line count:
```bash
wc -l frontend/components/renderers/VenueBiasCard.tsx
```
If > 300 lines, extract `StatCell`, `TossIntelPanel`, `BiasTrendStrip` into separate files.

- [ ] **Step 6: Commit**

```bash
git add frontend/components/renderers/FunctionRenderer.tsx
git commit -m "feat(renderer): wire VenueBiasCard to venue_bias_card output type"
```

---

## Final Verification

- [ ] Run full backend test suite: `pytest tests/ -v`
- [ ] Run frontend type-check: `cd frontend && npx tsc --noEmit`
- [ ] Run frontend lint: `cd frontend && npx next lint`
- [ ] Visually verify on at least 3 venues: one with 30+ matches, one with ~12, one with <10 (confirms LOW_SAMPLE warning)
- [ ] Confirm toss intelligence panel is hidden for venues where `data_available: false`
- [ ] Confirm bias trend strip is hidden when `direction === "INSUFFICIENT_DATA"`
