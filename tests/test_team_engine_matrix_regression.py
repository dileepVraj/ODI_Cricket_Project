import pandas as pd

from core.services.builder._matrix_generator import MatrixReportGenerator


def test_generate_matrix_report_does_not_raise_name_error_on_overall_block():
    matches = pd.DataFrame(
        [
                {
                    "team_bat_1": "Sri Lanka",
                    "team_bat_2": "England",
                    "winner": "Sri Lanka",
                    "status": "Included",
                    "score_inn1": 280,
                    "score_inn2": 240,
                    "match_id": "m1",
                    "start_date": "2024-01-01",
                },
                {
                    "team_bat_1": "England",
                    "team_bat_2": "Sri Lanka",
                    "winner": "England",
                    "status": "Included",
                    "score_inn1": 250,
                    "score_inn2": 210,
                    "match_id": "m2",
                    "start_date": "2024-01-02",
                },
                {
                    "team_bat_1": "Sri Lanka",
                    "team_bat_2": "India",
                    "winner": "India",
                    "status": "Included",
                    "score_inn1": 240,
                    "score_inn2": 230,
                    "match_id": "m3",
                    "start_date": "2024-01-03",
                },
            ]
        )

    report = MatrixReportGenerator._generate_matrix_report(
        matches,
        "Sri Lanka",
        "PERFORMANCE MATRIX: ASIA",
        False,
        lambda df: df.copy(),
        lambda df: df.to_dict("records"),
    )

    assert isinstance(report, list)
    assert len(report) > 0
    assert "Mat" in report[0]
