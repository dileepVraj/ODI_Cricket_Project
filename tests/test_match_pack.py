"""
tests/test_match_pack.py
Integration tests for the Match Pack transformer and interpreter modules.
Updated for v3.1 with new slim H2H, fixed dominance keys, and section descriptions.
"""
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.transformer import (
    transform_h2h_report,
    transform_h2h_slim,
    transform_venue_bias,
    transform_team_form,
    transform_dominance_matrix,
    transform_squad_comparison,
)
from core.interpreter import MatchInterpreter


# =============================================================================
# MOCK DATA
# =============================================================================

MOCK_H2H_RAW = [
    {"Metric": "Matches", "Value": "20"},
    {"Metric": "Tie/NR", "Value": "2"},
    {"Metric": "Win %", "Value": "60%"},
    {"Metric": "---", "Value": "---"},
    {"Metric": "Home Wins", "Value": "12"},
    {"Metric": "Bat 1st", "Value": "7"},
    {"Metric": "Bat 2nd", "Value": "5"},
    {"Metric": "---", "Value": "---"},
    {"Metric": "Away Wins", "Value": "6"},
    {"Metric": "Bat 1st", "Value": "4"},
    {"Metric": "Bat 2nd", "Value": "2"},
    {"Metric": "---", "Value": "---"},
    {"Metric": "Overall Avg 1st", "Value": "275 (18)"},
    {"Metric": "Overall Avg 2nd", "Value": "250 (18)"},
    {"Metric": "Avg Winning Score", "Value": "290 (10)"},
    {"Metric": "---", "Value": "---"},
    {"Metric": "Home Avg 1st", "Value": "285 (10)"},
    {"Metric": "Home Highest 1st", "Value": "350"},
    {"Metric": "Home Lowest 1st", "Value": "180"},
    {"Metric": "Home Avg Win", "Value": "300 (7)"},
    {"Metric": "Home Low Defended", "Value": "220"},
    {"Metric": "---", "Value": "---"},
    {"Metric": "Away Avg 1st", "Value": "260 (8)"},
    {"Metric": "Away Highest 1st", "Value": "320"},
    {"Metric": "Away Lowest 1st", "Value": "150"},
    {"Metric": "Away Avg Win", "Value": "280 (4)"},
    {"Metric": "Away Low Defended", "Value": "240"},
    {"Metric": "---", "Value": "---"},
    {"Metric": "Home Avg 2nd", "Value": "265 (10)"},
    {"Metric": "Home Highest Chase", "Value": "310"},
    {"Metric": "Home Avg Succ Chase", "Value": "290 (5)"},
    {"Metric": "Home Avg Fail Chase", "Value": "230 (5)"},
    {"Metric": "---", "Value": "---"},
    {"Metric": "Away Avg 2nd", "Value": "240 (8)"},
    {"Metric": "Away Highest Chase", "Value": "270"},
    {"Metric": "Away Avg Succ Chase", "Value": "260 (2)"},
    {"Metric": "Away Avg Fail Chase", "Value": "200 (6)"},
    {"Metric": "MATCH_IDS", "Value": "1,2,3,4,5"},
]

# Mock for EVEN H2H (50-50) — bug fix test
MOCK_H2H_EVEN = [
    {"Metric": "Matches", "Value": "10"},
    {"Metric": "Tie/NR", "Value": "0"},
    {"Metric": "Win %", "Value": "50%"},
    {"Metric": "---", "Value": "---"},
    {"Metric": "Home Wins", "Value": "5"},
    {"Metric": "Bat 1st", "Value": "3"},
    {"Metric": "Bat 2nd", "Value": "2"},
    {"Metric": "---", "Value": "---"},
    {"Metric": "Away Wins", "Value": "5"},
    {"Metric": "Bat 1st", "Value": "2"},
    {"Metric": "Bat 2nd", "Value": "3"},
] + [{"Metric": f"placeholder_{i}", "Value": "-"} for i in range(26)]

MOCK_VENUE_BIAS = {
    "Period": "Last 7 years",
    "Matches analyzed": "30",
    "Bias Verdict": "BAT FIRST 🏏",
    "Win % Batting First": "60% (18)",
    "Win % Chasing": "40% (12)",
    "Avg 1st innings score": "280 (30)",
    "Avg 2nd innings score": "260 (30)",
    "MATCH_IDS": "1,2,3",
}

MOCK_FORM = {
    "summary_code": ["W", "W", "L", "L", "L", "L", "W", "L", "L", "W"],
    "matches": [
        {"Result": "✅ WIN", "vs": "India", "Score": "250/8"},
        {"Result": "✅ WIN", "vs": "Pakistan", "Score": "220/6"},
    ],
    "MATCH_IDS": "10,11,12",
}

# Mock for dominance matrix — uses ACTUAL engine keys (Mat, Won, Lost)
MOCK_DOMINANCE = [
    {"Opponent": "⚡ OVERALL", "Mat": 50, "Won": 34, "Lost": 14, "Tie/NR": 2, "Win %": "71%", "Last 5": "W W L W W"},
    {"Opponent": "India", "Mat": 10, "Won": 7, "Lost": 3, "Tie/NR": 0, "Win %": "70%", "Last 5": "W W W L W"},
    {"Opponent": "Australia", "Mat": 8, "Won": 6, "Lost": 2, "Tie/NR": 0, "Win %": "75%", "Last 5": "W W W W L"},
    {"Opponent": "England", "Mat": 12, "Won": 8, "Lost": 4, "Tie/NR": 0, "Win %": "67%", "Last 5": "L W W W W"},
]


# =============================================================================
# TRANSFORMER TESTS
# =============================================================================

class TestTransformer:
    """Tests for transformer module."""

    def test_h2h_slim_has_no_averages(self):
        """Slim H2H should NOT contain batting averages."""
        result = transform_h2h_slim(MOCK_H2H_RAW, "India", "England")
        assert "batting_first" not in result
        assert "chasing" not in result
        assert "venue_averages" not in result
        assert result["matches_played"] == 20
        assert result["home_wins"] == 12
        assert result["away_wins"] == 6

    def test_h2h_full_has_averages(self):
        """Full H2H should contain batting averages for fortress/venue sections."""
        result = transform_h2h_report(MOCK_H2H_RAW, "India", "England")
        assert "batting_first" in result
        assert "chasing" in result
        assert result["batting_first"]["home_avg_score"] == 285
        assert result["chasing"]["home_highest_chase"] == 310

    def test_h2h_no_match_ids(self):
        """Transform output should NOT contain _match_ids."""
        result = transform_h2h_slim(MOCK_H2H_RAW, "India", "England")
        assert "_match_ids" not in result

    def test_venue_bias_clean(self):
        """Venue bias should strip emojis and parse all fields."""
        result = transform_venue_bias(MOCK_VENUE_BIAS)
        assert result["verdict"] == "BAT FIRST"
        assert result["bat_first_win_pct"] == 60
        assert result["chase_win_pct"] == 40
        assert result["score_drop_2nd_innings"] == 20
        assert result["period"] == "Last 7 years"
        assert "_match_ids" not in result

    def test_team_form_no_match_details(self):
        """Form output should NOT include individual match details."""
        result = transform_team_form(MOCK_FORM, "England")
        assert "matches" not in result
        assert result["wins"] == 4
        assert result["losses"] == 6
        assert result["win_pct"] == 40
        assert "_match_ids" not in result

    def test_dominance_matrix_correct_keys(self):
        """Dominance transform should parse Mat/Won/Lost keys (not Played/P)."""
        result = transform_dominance_matrix(MOCK_DOMINANCE, "Sri Lanka")
        # OVERALL row should be skipped — we calculate our own totals
        assert result["overall"]["matches"] == 30  # 10+8+12 (excluding OVERALL)
        assert result["overall"]["wins"] == 21  # 7+6+8
        assert result["overall"]["win_pct"] == 70
        assert len(result["vs_opponents"]) == 3
        assert result["vs_opponents"][0]["opponent"] == "India"
        assert result["vs_opponents"][0]["played"] == 10

    def test_dominance_form_guide(self):
        """Dominance should capture Last 5 form guide."""
        result = transform_dominance_matrix(MOCK_DOMINANCE, "Sri Lanka")
        assert result["vs_opponents"][0]["form"] is not None

    def test_empty_data_handling(self):
        """All transforms should return error dict for empty input."""
        assert "error" in transform_h2h_slim(None, "", "")
        assert "error" in transform_h2h_slim([], "", "")
        assert "error" in transform_venue_bias(None)
        assert "error" in transform_team_form(None, "")
        assert "error" in transform_dominance_matrix(None, "")


# =============================================================================
# INTERPRETER TESTS
# =============================================================================

class TestInterpreter:
    """Tests for interpreter module."""

    def setup_method(self):
        self.interp = MatchInterpreter()

    def test_h2h_at_50_says_evenly_matched(self):
        """At exactly 50%, narrative should say 'evenly split', NOT 'X leads'."""
        data = transform_h2h_slim(MOCK_H2H_EVEN, "India", "England")
        result = self.interp.interpret_h2h(data, "India", "England", "Last 4 Years")
        assert "evenly split" in result["narrative"]
        assert "India lead" not in result["narrative"]
        assert "England lead" not in result["narrative"]

    def test_h2h_section_description_present(self):
        """Every interpreted section should have a section_description."""
        data = transform_h2h_slim(MOCK_H2H_RAW, "India", "England")
        result = self.interp.interpret_h2h(data, "India", "England", "Last 4 Years")
        assert "section_description" in result
        assert len(result["section_description"]) > 20

    def test_h2h_context_has_reasoning(self):
        """Context tags should have reasoning strings."""
        data = transform_h2h_slim(MOCK_H2H_RAW, "India", "England")
        result = self.interp.interpret_h2h(data, "India", "England", "Last 4 Years")
        assert "dominance_reasoning" in result["context"]
        assert "intensity_reasoning" in result["context"]

    def test_form_trend_logic_fixed(self):
        """England's form: W,W,L,L,L,L,W,L,L,W — 4W/6L should NOT be TRENDING_UP."""
        data = transform_team_form(MOCK_FORM, "England")
        result = self.interp.interpret_form(data, "Global")
        # With 4W/6L, last 5 (W,W,L,L,L) = 2W/3L
        # 1st half (older 5): W,L,L,W → 40% WR
        # 2nd half (recent 5): W,W,L,L,L → 40% WR
        # Diff = 0 → should be FLAT, not TRENDING_UP
        assert result["context"]["trend"] != "TRENDING_UP"
        assert "trend_reasoning" in result["context"]

    def test_form_section_description_present(self):
        """Form should have section_description."""
        data = transform_team_form(MOCK_FORM, "England")
        result = self.interp.interpret_form(data, "Global")
        assert "section_description" in result

    def test_fortress_section_description(self):
        """Fortress should have section_description."""
        data = transform_h2h_report(MOCK_H2H_RAW, "India", "All")
        result = self.interp.interpret_fortress(data, "India")
        assert "section_description" in result
        assert "fortress_reasoning" in result["context"]

    def test_toss_bias_section_description(self):
        """Toss bias should have section_description."""
        data = transform_venue_bias(MOCK_VENUE_BIAS)
        result = self.interp.interpret_toss_bias(data)
        assert "section_description" in result
        assert "strength_reasoning" in result["context"]

    def test_dominance_section_description(self):
        """Dominance should have section_description."""
        data = transform_dominance_matrix(MOCK_DOMINANCE, "Sri Lanka")
        result = self.interp.interpret_dominance(data, "Sri Lanka", "HOME")
        assert "section_description" in result
        assert "strength_reasoning" in result["context"]

    def test_dominance_correct_narrative(self):
        """Dominance narrative should show correct percentages."""
        data = transform_dominance_matrix(MOCK_DOMINANCE, "Sri Lanka")
        result = self.interp.interpret_dominance(data, "Sri Lanka", "HOME")
        assert "70%" in result["narrative"]
        assert "21/30" in result["narrative"]

    def test_conditions_spin_boost(self):
        """Spin keywords should trigger SPIN_BOOST."""
        result = self.interp.interpret_conditions("dry, cracks visible", "", "")
        assert "SPIN_BOOST" in result["adjustments"]

    def test_conditions_dew_factor(self):
        """Evening match should trigger DEW_FACTOR."""
        result = self.interp.interpret_conditions("", "evening, sunset", "")
        assert "DEW_FACTOR" in result["adjustments"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
