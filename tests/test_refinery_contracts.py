import pandas as pd
from pathlib import Path

from formats.odi.utils.refinery_script import rebuild_intelligence_layer


def _make_master_rows():
    base = {
        "match_id": "m1",
        "start_date": "2024-01-01",
        "venue": "IND_BANGALORE",
        "winner": "Sri Lanka",
        "wides": 0,
        "noballs": 0,
        "extras": 0,
        "wicket_type": None,
        "player_dismissed": None,
    }
    return [
        {
            **base,
            "batting_team": "Sri Lanka",
            "bowling_team": "England",
            "innings": 1,
            "over_num": 9,
            "ball_rank": 1,
            "ball": 9.1,
            "striker": "SL Player 1",
            "non_striker": "SL Player 2",
            "bowler": "ENG Player 1",
            "runs_off_bat": 1,
        },
        {
            **base,
            "batting_team": "Sri Lanka",
            "bowling_team": "England",
            "innings": 1,
            "over_num": 10,
            "ball_rank": 1,
            "ball": 10.1,
            "striker": "SL Player 1",
            "non_striker": "SL Player 2",
            "bowler": "ENG Player 1",
            "runs_off_bat": 2,
        },
        {
            **base,
            "batting_team": "England",
            "bowling_team": "Sri Lanka",
            "innings": 2,
            "over_num": 39,
            "ball_rank": 1,
            "ball": 39.1,
            "striker": "ENG Player 1",
            "non_striker": "ENG Player 2",
            "bowler": "SL Player 1",
            "runs_off_bat": 3,
        },
        {
            **base,
            "batting_team": "England",
            "bowling_team": "Sri Lanka",
            "innings": 2,
            "over_num": 40,
            "ball_rank": 1,
            "ball": 40.1,
            "striker": "ENG Player 1",
            "non_striker": "ENG Player 2",
            "bowler": "SL Player 1",
            "runs_off_bat": 4,
        },
    ]


def test_refinery_phase_boundaries_and_clean_player_contract(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    master_path = data_dir / "FINAL_ODI_MASTER.csv"
    player_stats_path = data_dir / "processed_player_stats.csv"
    player_batting_path = data_dir / "processed_player_batting_stats.csv"
    player_bowling_path = data_dir / "processed_player_bowling_stats.csv"
    metadata_path = data_dir / "player_metadata.csv"
    phase_path = data_dir / "processed_phase_stats.csv"

    pd.DataFrame(_make_master_rows()).to_csv(master_path, index=False)

    cfg = {
        "label": "Test ODI",
        "data_file": str(master_path),
        "player_stats_file": str(player_stats_path),
        "player_batting_stats_file": str(player_batting_path),
        "player_bowling_stats_file": str(player_bowling_path),
        "metadata_file": str(metadata_path),
        "phase_stats_file": str(phase_path),
        "phases": {
            "pp": {"start": 0, "end": 9, "label": "Powerplay (1-10)"},
            "mid": {"start": 10, "end": 39, "label": "Middle (11-40)"},
            "dth": {"start": 40, "end": 49, "label": "Death (41-50)"},
        },
    }

    rebuild_intelligence_layer(cfg)

    phase_df = pd.read_csv(phase_path)
    inn1 = phase_df[phase_df["innings"] == 1].iloc[0]
    inn2 = phase_df[phase_df["innings"] == 2].iloc[0]

    assert int(inn1["pp_runs"]) == 1
    assert int(inn1["mid_runs"]) == 2
    assert int(inn2["mid_runs"]) == 3
    assert int(inn2["dth_runs"]) == 4
    assert {"pp_balls", "mid_balls", "dth_balls"}.issubset(set(phase_df.columns))

    combined = pd.read_csv(player_stats_path)
    assert "runs_off_bat" not in combined.columns
    assert "extras" not in combined.columns
    assert {"player", "team", "opponent", "innings", "runs", "balls", "dismissals", "role", "context"}.issubset(set(combined.columns))

    batting = pd.read_csv(player_batting_path)
    bowling = pd.read_csv(player_bowling_path)
    assert batting["role"].eq("batting").all()
    assert bowling["role"].eq("bowling").all()
    assert {"strike_rate", "average"}.issubset(set(batting.columns))
    assert {"economy", "strike_rate", "average", "legal_balls"}.issubset(set(bowling.columns))
