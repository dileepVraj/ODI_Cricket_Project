import json
from pathlib import Path

import duckdb
import pandas as pd
import pytest

from formats.odi.utils.json_converter import run_json_conversion
from scripts.maintenance.etl_reconciliation_report import run_reconciliation_checks


def _make_valid_match_json() -> dict:
    sl_players = [f"SL Player {i}" for i in range(1, 13)]
    eng_players = [f"ENG Player {i}" for i in range(1, 13)]
    return {
        "info": {
            "dates": ["2024-01-01"],
            "venue": "M. Chinnaswamy Stadium",
            "city": "Bengaluru",
            "match_type": "ODI",
            "gender": "male",
            "competition": "ICC Cricket World Cup",
            "event": {"name": "World Cup", "match_number": 25},
            "neutral_venue": 0,
            "teams": ["Sri Lanka", "England"],
            "outcome": {"winner": "Sri Lanka", "by": {"wickets": 8}},
            "players": {
                "Sri Lanka": sl_players,
                "England": eng_players,
            },
            "toss": {"winner": "England", "decision": "field"},
        },
        "innings": [
            {
                "team": "Sri Lanka",
                "overs": [
                    {
                        "over": 0,
                        "deliveries": [
                            {
                                "batter": "SL Player 1",
                                "non_striker": "SL Player 2",
                                "bowler": "ENG Player 1",
                                "runs": {"batter": 1, "extras": 0},
                            }
                        ],
                    }
                ],
            },
            {
                "team": "England",
                "overs": [
                    {
                        "over": 0,
                        "deliveries": [
                            {
                                "batter": "ENG Player 1",
                                "non_striker": "ENG Player 2",
                                "bowler": "SL Player 1",
                                "runs": {"batter": 0, "extras": 0},
                            }
                        ],
                    }
                ],
            },
        ],
    }


def _make_converter_config(tmp_path: Path) -> dict:
    data_dir = tmp_path / "data"
    json_dir = data_dir / "json_source"
    json_dir.mkdir(parents=True, exist_ok=True)
    return {
        "label": "Test ODI",
        "json_source_dir": str(json_dir),
        "data_file": str(data_dir / "FINAL_ODI_MASTER.csv"),
        "squads_file": str(data_dir / "MATCH_SQUADS.csv"),
        "info_file": str(data_dir / "MATCH_INFO.csv"),
        "conversion_audit_file": str(data_dir / "conversion_audit.json"),
    }


def test_json_converter_strict_mode_fails_on_broken_file(tmp_path: Path) -> None:
    cfg = _make_converter_config(tmp_path)
    src = Path(cfg["json_source_dir"])

    (src / "valid_match.json").write_text(json.dumps(_make_valid_match_json()), encoding="utf-8")
    (src / "broken_match.json").write_text("{ invalid json", encoding="utf-8")

    with pytest.raises(RuntimeError):
        run_json_conversion(cfg, strict=True, allow_partial=False)

    assert not Path(cfg["data_file"]).exists()
    assert Path(cfg["conversion_audit_file"]).exists()


def test_json_converter_partial_mode_writes_outputs_and_audit(tmp_path: Path) -> None:
    cfg = _make_converter_config(tmp_path)
    src = Path(cfg["json_source_dir"])

    (src / "valid_match.json").write_text(json.dumps(_make_valid_match_json()), encoding="utf-8")
    (src / "broken_match.json").write_text("{ invalid json", encoding="utf-8")

    audit = run_json_conversion(cfg, strict=True, allow_partial=True)

    assert audit["files_failed"] == 1
    assert Path(cfg["data_file"]).exists()

    df = pd.read_csv(cfg["data_file"])
    assert "over_num" in df.columns
    assert "ball_rank" in df.columns


def test_json_converter_outputs_rich_match_info_columns(tmp_path: Path) -> None:
    cfg = _make_converter_config(tmp_path)
    src = Path(cfg["json_source_dir"])
    (src / "valid_match.json").write_text(json.dumps(_make_valid_match_json()), encoding="utf-8")

    run_json_conversion(cfg, strict=True, allow_partial=False)

    info_df = pd.read_csv(cfg["info_file"])
    expected_cols = {
        "city",
        "match_type",
        "gender",
        "competition",
        "event_name",
        "event_match_number",
        "outcome_by_wickets",
        "toss_winner",
        "toss_decision",
        "neutral_venue",
    }
    assert expected_cols.issubset(set(info_df.columns))


def test_json_converter_outputs_squad_status_columns(tmp_path: Path) -> None:
    cfg = _make_converter_config(tmp_path)
    src = Path(cfg["json_source_dir"])
    (src / "valid_match.json").write_text(json.dumps(_make_valid_match_json()), encoding="utf-8")

    run_json_conversion(cfg, strict=True, allow_partial=False)

    squads_df = pd.read_csv(cfg["squads_file"])
    expected_cols = {"player_order", "is_playing_xi", "player_status", "source"}
    assert expected_cols.issubset(set(squads_df.columns))
    assert squads_df["is_playing_xi"].isin([True, False]).all()
    assert bool((~squads_df["is_playing_xi"]).any())


def _build_minimal_db(db_path: Path, *, duplicate_key: bool = False, unresolved_venue: bool = False) -> None:
    con = duckdb.connect(str(db_path))
    try:
        con.execute(
            """
            CREATE TABLE balls (
                match_id VARCHAR,
                innings INTEGER,
                over_num INTEGER,
                ball_rank INTEGER,
                ball DOUBLE,
                batting_team VARCHAR,
                bowling_team VARCHAR,
                runs_off_bat INTEGER,
                extras INTEGER,
                wides INTEGER,
                noballs INTEGER,
                wicket_type VARCHAR,
                venue VARCHAR,
                venue_id VARCHAR,
                start_date DATE
            )
            """
        )
        rows = [
            ("m1", 1, 0, 1, 0.1, "Sri Lanka", "England", 1, 0, 0, 0, None, "IND_BANGALORE", "IND_BANGALORE", "2024-01-01"),
            ("m1", 2, 0, 1, 0.1, "England", "Sri Lanka", 0, 0, 0, 0, None, "IND_BANGALORE", "IND_BANGALORE", "2024-01-01"),
        ]
        if duplicate_key:
            rows.append(
                ("m1", 1, 0, 1, 0.1, "Sri Lanka", "England", 4, 0, 0, 0, None, "IND_BANGALORE", "IND_BANGALORE", "2024-01-01")
            )
        con.executemany(
            """
            INSERT INTO balls VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

        venue_id = None if unresolved_venue else "IND_BANGALORE"
        con.execute(
            """
            CREATE TABLE matches (
                match_id VARCHAR,
                start_date DATE,
                venue VARCHAR,
                venue_id VARCHAR,
                team_bat_1 VARCHAR,
                team_bat_2 VARCHAR,
                winner VARCHAR,
                year INTEGER,
                season INTEGER,
                score_inn1 INTEGER,
                score_inn2 INTEGER,
                balls_inn1 INTEGER,
                balls_inn2 INTEGER,
                wickets_inn1 INTEGER,
                wickets_inn2 INTEGER
            )
            """
        )
        con.execute(
            """
            INSERT INTO matches VALUES
            ('m1', '2024-01-01', 'IND_BANGALORE', ?, 'Sri Lanka', 'England', 'Sri Lanka', 2024, 2024, 250, 240, 300, 300, 10, 10)
            """,
            [venue_id],
        )
    finally:
        con.close()


def test_reconciliation_passes_for_minimal_valid_db(tmp_path: Path) -> None:
    db_path = tmp_path / "ok.duckdb"
    _build_minimal_db(db_path)

    report = run_reconciliation_checks(
        db_path=str(db_path),
        max_unresolved_venue_ratio=0.5,
        fail_on_error=False,
    )

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["hard_failures"] == 0


def test_reconciliation_flags_duplicate_delivery_identity(tmp_path: Path) -> None:
    db_path = tmp_path / "dup.duckdb"
    _build_minimal_db(db_path, duplicate_key=True)

    report = run_reconciliation_checks(
        db_path=str(db_path),
        max_unresolved_venue_ratio=0.5,
        fail_on_error=False,
    )

    assert report["summary"]["status"] == "fail"
    failed_checks = {c["name"] for c in report["checks"] if c["status"] == "fail"}
    assert "duplicate_delivery_identity" in failed_checks


def test_reconciliation_flags_unresolved_venue_ratio(tmp_path: Path) -> None:
    db_path = tmp_path / "venue.duckdb"
    _build_minimal_db(db_path, unresolved_venue=True)

    report = run_reconciliation_checks(
        db_path=str(db_path),
        max_unresolved_venue_ratio=0.0,
        fail_on_error=False,
    )

    assert report["summary"]["status"] == "fail"
    failed_checks = {c["name"] for c in report["checks"] if c["status"] == "fail"}
    assert "unresolved_venue_ratio" in failed_checks
