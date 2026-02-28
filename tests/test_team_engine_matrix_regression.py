import pandas as pd

from formats.odi.engines.team_engine import TeamEngine


def test_generate_matrix_report_does_not_raise_name_error_on_overall_block():
    engine = TeamEngine.__new__(TeamEngine)
    engine.apply_smart_filters = lambda df: df.copy()
    engine._get_form_guide = lambda df, team: "WWL"
    engine._get_avg_with_count = lambda df, col: f"{len(df)} [n]"

    matches = pd.DataFrame(
        [
            {
                "team_bat_1": "Sri Lanka",
                "team_bat_2": "England",
                "winner": "Sri Lanka",
                "status": "Included",
                "score_inn1": 280,
                "match_id": "m1",
            },
            {
                "team_bat_1": "England",
                "team_bat_2": "Sri Lanka",
                "winner": "England",
                "status": "Included",
                "score_inn1": 250,
                "match_id": "m2",
            },
            {
                "team_bat_1": "Sri Lanka",
                "team_bat_2": "India",
                "winner": "India",
                "status": "Included",
                "score_inn1": 240,
                "match_id": "m3",
            },
        ]
    )

    report = TeamEngine._generate_matrix_report(
        engine,
        matches,
        "Sri Lanka",
        "PERFORMANCE MATRIX: ASIA",
    )

    assert isinstance(report, list)
    assert len(report) > 0
    assert "Mat" in report[0]
