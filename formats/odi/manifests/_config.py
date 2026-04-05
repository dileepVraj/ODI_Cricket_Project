from formats.odi.config.players import BOWLER_STYLES, PLAYER_ROLES

TACTICAL_THRESHOLDS = {
    "unmapped_min_balls": 6,
    "form_window_matches": 10,
    "structural_weakness_avg_max": 25,
    "dominant_matchup_avg_min": 50,
    "threat_min_balls": 20,
    "threat_dominant_balls": 30,
    "threat_dominant_sr": 120,
    "threat_threat_sr_outs0": 105,
    "threat_threat_avg_outs1": 45,
    "threat_threat_sr_outs1": 100,
    "threat_advantage_sr": 95,
    "threat_advantage_avg": 30,
    "threat_watchful_avg": 25,
    "threat_watchful_sr": 90,
    "threat_dominated_outs": 2,
    "threat_dominated_avg": 22,
    "threat_bunny_outs": 3,
    "threat_bunny_avg": 18,
    "recency_w_0_12": 1.0,
    "recency_w_12_24": 0.6,
    "recency_w_24_36": 0.3,
    "recency_w_36_plus": 0.1,
    "confidence_2_min": 30,
    "confidence_3_min": 50,
    "confidence_4_min": 100,
    "confidence_5_min": 200,
    "competitive_chase_threshold": 200,
    "low_sample_min_matches": 3,
    "bias_win_pct_min": 55,
    "strong_bias_gap_min": 15,
    "phase_start_year_default": 2015,
}

SPORT_CONSTANTS = {
    "balls_per_over": 6,
    "percent_scale": 100,
    "all_out_wickets": 10,
}

ENGINE_DEFAULTS = {
    "recent_match_ids_limit": 3,
    "recent_context_fallback_years": 5,
    "venue_stats_fallback_years": 50,
    "squad_backscan_match_limit": 3,
    "unmapped_min_balls_fallback": 6,
}

PLAYER_RULES = {
    "default_years_window": 10,
    "last_xi_match_limit": 11,
    "profile_years_default": 10,
    "milestone_century": 100,
    "milestone_half_century": 50,
    "profile_sr_min_balls": 60,
    # ARCH-DEC-03: rounding precision
    "stat_precision_avg": 0,
    "stat_precision_rate": 1,
    # ARCH-DEC-03: innings thresholds (replaces min_innings_threshold)
    "min_innings_career": 20,
    "min_innings_context": 5,
    "min_innings_form": 3,
}

PLAYER_CONTEXT_TYPES = {
    "vs_team": "vs_team",
    "at_venue": "at_venue",
    "batting": "batting",
    "bowling": "bowling",
    "all": "All",
}

FORMAT_RULES = {
    "max_overs": 50,
    "min_balls_for_completed_innings": 270,  # Used to filter rain-affected/shortened matches if not all-out/chased.
    "phases": {
        "powerplay": [0, 9],
        "middle": [10, 39],
        "death": [40, 49],
    },
    "par_score_baseline": 180,
    "tactical_thresholds": TACTICAL_THRESHOLDS,
    "SPORT_CONSTANTS": SPORT_CONSTANTS,
    "style_map": BOWLER_STYLES,
    "player_roles": PLAYER_ROLES,
    "default_player_role": "All-Rounder",
    "default_years_window": 5,
    "engine_defaults": ENGINE_DEFAULTS,
    "player_rules": PLAYER_RULES,
    "player_context_types": PLAYER_CONTEXT_TYPES,
}
