"""ODI-specific configuration constants."""

ODI_FORMAT_CONFIG = {
    "label": "Men's ODI",
    "db_file": "formats/odi/data/odi.duckdb",
    "data_file": "formats/odi/data/FINAL_ODI_MASTER.csv",
    "squads_file": "formats/odi/data/MATCH_SQUADS.csv",
    "info_file": "formats/odi/data/MATCH_INFO.csv",
    "player_stats_file": "formats/odi/data/processed_player_stats.csv",
    "player_batting_stats_file": "formats/odi/data/processed_player_batting_stats.csv",
    "player_bowling_stats_file": "formats/odi/data/processed_player_bowling_stats.csv",
    "metadata_file": "formats/odi/data/player_metadata.csv",
    "phase_stats_file": "formats/odi/data/processed_phase_stats.csv",
    "json_source_dir": "formats/odi/data/json_source",
    "conversion_audit_file": "formats/odi/reports/conversion_audit.json",
    "reconciliation_audit_file": "formats/odi/reports/reconciliation_audit.json",
    "max_unresolved_venue_ratio": 0.25,
    "phases": {
        # over_num is 0-based in master data:
        # 0-9 => overs 1-10, 10-39 => overs 11-40, 40-49 => overs 41-50
        "pp": {"start": 0, "end": 9, "label": "Powerplay (1-10)"},
        "mid": {"start": 10, "end": 39, "label": "Middle (11-40)"},
        "dth": {"start": 40, "end": 49, "label": "Death (41-50)"},
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
    "competitive_chase_threshold": 200,
}


ODI_COUNTRY_PREFIX_MAP = {
    "India": "IND_",
    "England": "ENG_",
    "Australia": "AUS_",
    "South Africa": "SA_",
    "New Zealand": "NZ_",
    "Sri Lanka": "SL_",
    "West Indies": "WI_",
    "Pakistan": "PAK_",
    "Bangladesh": "BAN_",
}
