"""ODI-specific configuration constants."""

ODI_FORMAT_CONFIG = {
    "label": "Men's ODI",
    "db_file": "formats/odi/data/odi.duckdb",
    "data_file": "formats/odi/data/FINAL_ODI_MASTER.csv",
    "squads_file": "formats/odi/data/MATCH_SQUADS.csv",
    "info_file": "formats/odi/data/MATCH_INFO.csv",
    "player_stats_file": "formats/odi/data/processed_player_stats.csv",
    "metadata_file": "formats/odi/data/player_metadata.csv",
    "phase_stats_file": "formats/odi/data/processed_phase_stats.csv",
    "json_source_dir": "formats/odi/data/json_source",
    "phases": {
        "pp": {"start": 0, "end": 10, "label": "Powerplay (1-10)"},
        "mid": {"start": 11, "end": 40, "label": "Middle (11-40)"},
        "dth": {"start": 41, "end": 50, "label": "Death (41-50)"},
    },
    "total_overs": 50,

    # Prediction Model Constants (ODI-calibrated)
    "venue_baseline_default": 280,
    "standard_batting_potential": 300,
    "min_bat_avg_cap": 5.0,
    "max_bat_avg_cap": 60.0,
    "standard_bowling_economy": 5.5,
    "min_bowls_filter": 60,
    "prediction_margin": 15,
    "modern_bowling_economy": 5.85,
    "modern_bowling_sr": 34.0,
    "critical_bat_depth": 7,
}
