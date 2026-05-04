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

# -- Literal Registries (used by GATE6 compliance_bouncer) -----------------
# Moved here from formats/odi/manifest.py in TASK-185a.
# Phase 11.2: Engine literal registry for compliance-bouncer
ENGINE_LITERAL_REGISTRY = ['CricketAnalyzer', 'match_id', 'player', 'date', 'team', "Missing required format rule '", "'. Define it in manifest FORMAT_RULES and pass it into PlayerEngine.", "Invalid tactical threshold '", "': ", '. Expected integer.', "Missing required format rule 'default_player_role'. Define it in manifest FORMAT_RULES and pass it into PlayerEngine.", "Missing required format rule 'default_years_window'. Define it in manifest FORMAT_RULES and pass it into PlayerEngine.", "Invalid format rule 'default_years_window': ", "Format rule 'default_years_window' must be > 0.", "Invalid engine default '", "Missing engine default '", "' in FORMAT_RULES['engine_defaults'].", 'reference_date', 'D', "Invalid reference_date rule '%s': %s", '_reference_date', 'Invalid years value: ', 'years must be > 0.', "Missing tactical threshold '", "' in FORMAT_RULES['tactical_thresholds'].", 'is_playing_xi', 'start_date', 11, 'batting_team', 'striker', 'non_striker', 'bowling_team', 'bowler', 'coerce', '_', '|', 'squad_metrics', 'player_stats', 'style_metrics', 'average_raw', 'STRUCTURAL_WEAKNESS', ' struggles vs ', ' (Avg ', ')', 'DOMINANT_MATCHUP', ' dominates ', 'runs_off_bat', 'sum', 'count', 'player_dismissed', 'Balls', 'Runs', 'Outs', 'Style', 'IsBunny', 'Avg', 'SR', 100, 'Bowler', 'Batter', 'records', 'context', 'vs_team', 'role', 'batting', 'runs', 'innings', 'dismissals', 'balls', 'bowling', 60, 'N/A', 'opponent', 'at_venue', "Missing required format rule 'min_balls_for_completed_innings'. Define it in manifest FORMAT_RULES and pass it into TeamEngine.", "Invalid format rule 'min_balls_for_completed_innings': ", "Format rule 'min_balls_for_completed_innings' must be > 0.", "Missing required format rule 'phases'. Define it in manifest FORMAT_RULES and pass it into TeamEngine.", "Missing required format rule 'tactical_thresholds'. Define it in manifest FORMAT_RULES and pass it into TeamEngine.", '_tactical_thresholds', 'status', 'string', 'included', 'excluded (no result)', 'excluded (short 2nd)', 'Visitors', 'vs ', 'team_bat_1', 'team_bat_2', 'FORTRESS REPORT (', 'win_pct', 'tie_nr', 'name', 'stats', 'avg_1st', '-', 'avg_2nd', 'avg_win_score', 'has_low_sample_warnings', 'has_form_guide', 'winner', 'tie', 'no result', 'nan', 'none', 'Batting 1st Avg', 'avg', 'Avg Winning Score', 'avg_win', 'Chasing Avg', ' ', ' (n=', 'gray', 'high', 'high_1st', 'low', 'low_1st', 'avg_1st_win', 'low_def', 'low_defended', 'high_chased', 'succ', 'avg_succ', 'fail', 'avg_fail', 'score_inn2', 'score_inn1', 'last_5_home', 'last_5_away', ',', 'phase_df', 'phase_overs', 'pp', 'mid', 'dth', 'balls_inn1', 'wickets_inn1', 'balls_inn2', 'wickets_inn2', '.', 'abandoned', 'min_first_innings_balls', 'min_first_innings_overs', 'keep_all_outs', 'keep_successful_chases', 'drop_short_no_result_only', 'MATCH_IDS', 'start_year', 'bat_first', 'home_team_pp_runs', 'pp_runs', 'away_team_pp_runs', 'home_team_pp_wkts', 'pp_wkts', 'away_team_pp_wkts', 'home_team_mid_runs', 'mid_runs', 'away_team_mid_runs', 'home_team_mid_wkts', 'mid_wkts', 'away_team_mid_wkts', 'home_team_dth_runs', 'dth_runs', 'away_team_dth_runs', 'home_team_dth_wkts', 'dth_wkts', 'away_team_dth_wkts', 'chasing', 'rr', 'away', 'scenario_rows', 'NEUTRAL', 'BAT FIRST', 'BOWL FIRST', 'period', 'total_matches', 'bat1_win_pct', 'chase_win_pct', 'avg_1st_inn', 'avg_2nd_inn', 'percent_breakdown', 'chase', 'highlight_flags', 'has_strong_bias', 'derived_badges', 'raw_matches', 'GLOBAL RIVALRY REPORT', 'HOME COUNTRY', 'HOST COUNTRY REPORT (', 'DOMINANCE MATRIX', 'AWAY PERFORMANCE MATRIX', 'GLOBAL PERFORMANCE MATRIX', 'Global', 'REGIONAL RIVALRY REPORT (', 'PERFORMANCE MATRIX: ']

ENGINE_LITERAL_REGISTRY += [
    "Missing required 'match_context'. Inject match_df/phase_df/reference_date/tactical_thresholds per request.",
    "Invalid match_context reference_date: ",
    "Missing required format rule 'SPORT_CONSTANTS'. Define it in manifest FORMAT_RULES and pass it into TeamEngine.",
    "Invalid SPORT_CONSTANTS value '",
    "Missing SPORT_CONSTANTS key '",
    "' in FORMAT_RULES['SPORT_CONSTANTS'].",
    "VISITOR_TEAM",
    "FORTRESS_REPORT",
    "neutral",
    "bowl_first",
    "GLOBAL_RIVALRY_REPORT",
    "HOST_COUNTRY_REPORT",
    "DOMINANCE_MATRIX",
    "AWAY_PERFORMANCE_MATRIX",
    "GLOBAL_PERFORMANCE_MATRIX",
    "REGIONAL_RIVALRY_REPORT",
    "REGIONAL_PERFORMANCE_MATRIX",
    "rows",
    "payload",
    "report",
]


ENGINE_LITERAL_REGISTRY += [
    # TASK-027a: Player engine literal registrations
    # PLAYER_RULES numeric constant keys
    "default_years_window",
    "last_xi_match_limit",
    "profile_years_default",
    "milestone_century",
    "milestone_half_century",
    "profile_sr_min_balls",
    "stat_precision_avg",
    "stat_precision_rate",
    "min_innings_career",
    "min_innings_context",
    "min_innings_form",
    # PLAYER_CONTEXT_TYPES values absent from the original engine registry
    "all",
    "All",
    0,
    20,
    5,
    3,
    "Invalid ",
    " '",
    "tactical threshold",
    "Invalid format rule '",
    "Format rule '",
    "' must be > 0.",
    "engine default",
    "avg_runs",
    "is_dismissal",
    "Other",
    "Team",
]

ENGINE_LITERAL_REGISTRY += [
    "NEW MATCHUP",
    "LOW DATA",
    "BUNNY",
    "DOMINATED",
    "WATCHFUL",
    "DOMINANT",
    "THREAT",
    "ADVANTAGE",
    "CONTESTED",
    "_runs_off_bat_num",
    "_is_out",
    "_weight",
    365,
    730,
    1095,
    "_weighted_runs",
    "_weighted_outs",
    "ThreatRating",
    "WeightedBalls",
    "WeightedRuns",
    "WeightedOuts",
    "Confidence",
    "DismissalStructural",
    "DismissalCaught",
    "DismissalOther",
    "_dismissal_structural",
    "_dismissal_caught",
    "_dismissal_other",
    "PP_",
    "Mid_",
    "Death_",
    "PP_Balls",
    "PP_Runs",
    "PP_Outs",
    "PP_Avg",
    "PP_SR",
    "PP_ThreatRating",
    "Mid_Balls",
    "Mid_Runs",
    "Mid_Outs",
    "Mid_Avg",
    "Mid_SR",
    "Mid_ThreatRating",
    "Death_Balls",
    "Death_Runs",
    "Death_Outs",
    "Death_Avg",
    "Death_SR",
    "Death_ThreatRating",
]

ENGINE_LITERAL_REGISTRY += [
    # TASK-158: New matchup stats column names
    "Inn1_",
    "Inn2_",
    "_is_boundary",
    "_is_wide",
    "_is_dot",
    "MatchCount",
    "BoundaryBalls",
    "BoundaryRate",
    "DotBalls",
    "DotBallRate",
    "WideBalls",
    "PP_MatchCount",
    "Mid_MatchCount",
    "Death_MatchCount",
    "Inn1_Balls",
    "Inn1_Avg",
    "Inn1_SR",
    "Inn1_ThreatRating",
    "Inn2_Balls",
    "Inn2_Avg",
    "Inn2_SR",
    "Inn2_ThreatRating",
    "VenueFiltered",
    # TASK-158: Column validation error/warning messages
    "context_df missing required matchup columns: ",
    "context_df missing optional matchup columns (degraded output): %s",
]

ENGINE_LITERAL_REGISTRY += [
    # TASK-165: Venue bias calculator — bias trend and toss intelligence thresholds
    8,   # minimum matches per window required for bias trend computation
    12,  # gap threshold (pct points) for trend direction; minimum toss group size
    "chose_bat_count",   # VenueTossIntelligence TypedDict key
    "chose_bowl_count",  # VenueTossIntelligence TypedDict key
]

# Phase 11.2: Service literal registry for compliance-bouncer
SERVICE_LITERAL_REGISTRY = ['match_df', 'get', "Non-fatal enrichment lookup issue for key '%s': %s", 'keys', 'Non-fatal enrichment key extraction issue: %s', 'strftime', '%Y-%m-%d', "Non-fatal date normalization issue for value '%s': %s", 'elite', 'excluded', 'caution', 'error', 'danger', 'muted', 'inn', 'score_inn', 'wickets_inn', 'wicket', 'balls_inn', 'ball', '/', ' (', '.1f', 'Included', 'status_tone', 'team_engine', 'apply_smart_filters', '_mid_str', 'match_ids', 'Opponent', 'OVERALL', 'Metric', 'Value', 'match_audit', 'inn1', 'inn2', 'bat', '2', '✅ Included', '☔ Excluded (No Result)', '☔ Excluded (Short 1st)', '☔ Excluded (Short 2nd)', '☔ Excluded', '*', 'stadium_name', 'home_team', 'opp_team', 'years_back', 'continent', 'home_xi', 'batting_players', 'away_xi', 'bowling_players', 'team_a_name', 'team_b_name', 'team_a_players', 'team_b_players', 'opposition', 'away_team', 'team_name', 'opposition_bowlers', 'batter', 'bowlers', 'get_player_profile', 'limit', 'time', 'toss', 'pitch', 'persist', 'dal', 'is_legal_ball', 'average', 'strike_rate', 'highest_score', 'centuries', 'fifties', 'CricketAPI', 'PlayerService fallback failed: ', ' [', ']', 'home_team_ref', 'Matches Played', 'Tied / No Result', ' Win %', '%', ' Last 5', '--- HOME PERFORMANCE ---', 'Total Wins', 'Won Batting 1st (Defended)', 'Won Batting 2nd (Chased)', '--- VISITOR PERFORMANCE ---', '--- VENUE AVERAGES ---', 'Overall Avg 1st Innings', 'Overall Avg 2nd Innings', 'Avg 1st Innings Winning Score', '--- BATTING 1ST (', ') ---', 'Average 1st Innings', 'Highest 1st Innings', 'Lowest 1st Innings', 'Lowest Defended Score', '--- CHASING (', 'Average 2nd Innings', 'Highest Chased', 'Avg Successful Chase', 'Avg Failed Chase', 'Overview', '---', '- ', 'row_kind', 'section', 'display_metric', 'section_label', 'section_tone', 'value_tone', 'is_zero_or_empty', 'meta', 'metric', '0', 'win %', 'India', 'Australia', 'England', 'South Africa', 'New Zealand', 'Pakistan', 'Sri Lanka', 'West Indies', 'Bangladesh', 'Afghanistan', 'Mat', 'Won', 'Lost', 'Tie/NR', 'Win %', 'form_guide', ' Avg (1st)', 'Opp Avg (1st)', 'cell_tones', 'is_overall', '% win rate', '🔹 OVERALL', 'Overall benchmark', 'Player', 'SquadComparison', 'TacticalMatrix', 'Matchups', 'PlayerStats', 'Result', 'WIN', 'TIE', 'NR', 'LOSS', 'Int64', '<NA>', '(1st)', '(2nd)', 'TeamScore', 'OppScore', 'Venue', 'Date', 'RawResult', 'ResultTone', 'ResultSymbol', 'W', 'L', 'T', 'wins', 'losses', 'ties_or_nr', 'total', 'form_summary', 'is_win', 'Result: ', '\\[(\\d+)\\]', 45, 'strong', 30, 'BAT', 'primary', 'BOWL', 'CHASE', 'secondary', 'slate', '#', '[0-9a-fA-F]{6}', 16, 255.0, 4, 360, 255, 'blue', 85, 160, 'emerald', 35, 65, 'amber', 330, 'rose', 'violet', 'batting 1st', 'visitor', 'overall', 'tertiary', '✅', '🤝', '🌧️', '❌', 'Bunny Alert', 'bunny_alert', ', ', 'player_role', 'batting_form', 'DNB', 'bowling_form', 'batting_average', 'venue_runs', 'venue_batting_activity', 'Role', 'Inns', 'Bat Form', 'Bat Avg', 'vs Opp', 'vs_opposition_average', 'Ven Inns', 'venue_innings', 'Ven Runs', 'Ven Avg', 'venue_average', 'Ven HS', 'venue_high_score', 'Bowl Form', 'Bowl Econ', 'bowling_economy', 'Ven Econ', 'venue_economy', 'Ven Wkts', 'venue_wickets', 'Ven Matches', 'venue_matches', 'Unmapped', '_raw', 'model_dump', 'Team A', 'Team B', 'metrics_a', 'metrics_b', 'Caps (Combined)', 'caps', 'Avg Caps / Player', 'avg_caps', 'Total Runs', '100s', '50s', 'Total Wickets', 'wickets', '5W Hauls', 'five_wkt_hauls', 'XI Size', 'Years Window', 'player_stats_a', 'player_stats_b', 500, 'max_rows must be a positive integer.', '[]', 'iso', 'bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket', 'index', 'wicket_type', 'int64', 'float64', 'object', 'last', 'rank', 'runs_num', 'is_out', 'left', 'entry', 'wides_num', 'wides', 'noballs_num', 'noballs', 'is_wkt', 'legal_ball', 'total_runs', 'legal_balls', 'wkts', 'nunique', 'bool', 'empty', 'Non-fatal team phase normalization issue: %s', '[^a-z0-9]+', '\\([^)]*\\)', 'IND_', 'PAK_', 'SL_', 'BAN_', 'AFG_', 'UAE_', 'ENG_', 'IRE_', 'SCO_', 'NED_', 'AUS_', 'NZ_', 'SA_', 'ZIM_', 'WI_', 'USA_']


# Phase 12 Strike-1 Recovery: TypedDict key registration for FormGuidePayload, FormSequencePayload,
# and MatchStatus display labels. These are all service-layer semantic keys from team_types.py
# that must be declared here so the Zero-Literal rule in compliance_bouncer.py can authorize them.
SERVICE_LITERAL_REGISTRY += [
    # FormGuidePayload keys (core/interfaces/team_types.py: FormGuidePayload)
    'no_results',
    'raw_results',
    # MatrixReportRow / TeamFormRow form data payload key
    'form_data',
    # form_guide: semantic key used by format_form_guide() and builder-to-formatter handoff
    'form_guide',
    'analyze_squad_types',
    'analyze_dual_squad_matrix',
    # FormSequencePayload keys (core/interfaces/team_types.py: FormSequencePayload)
    'results',
    'missing_token',
    # Match status display label strings (used in ReportFormatter.MATCH_STATUS_LABELS)
    # The bouncer sees the bare label without the ☔ prefix — both forms must be registered.
    'Excluded',
    'Excluded (No Result)',
    'Excluded (Short 1st)',
    'Excluded (Short 2nd)',
    # Umbrella emoji used as the icon for non-OK match statuses in MATCH_STATUS_ICONS
    '☔',
    # Fallback emoji for unmapped form-guide result tokens in format_form_guide()
    '❓',
    # ReportMetricPayload key
    'is_low_sample',
]


# ── Quick Stats (for validators and introspection) ──────────────────────
# Calculator literal registry —
# internal column keys and computation
# strings used by core/calculators/
CALCULATOR_LITERAL_REGISTRY = [
    # phase_engine.py internal column keys
    "over_num",
    "phase_bucket",
    "phase_runs",
    "phase_wkts",
    "phase_balls",
    "extras",
    "_runs",
    "_wkts",
    "phase_bounds",
    "mean",
    "n",
    "start",
    "end",
    "both",
    "pp_rr",
    "mid_rr",
    "dth_rr",
    "avg_score",
    "pp_balls",
    "mid_balls",
    "dth_balls",
    "home_value",
    "away_value",
    "higher_better",
    "diff",
    "advantage",
    "diff_text",
    "diff_tone",
    # _scenario_row direction labels
    "UP",
    "DOWN",
    # _scenario_row tone values
    "success",
    # _scenario_row neutral diff
    "0.0",
    # summarize_phase_by_innings innings keys
    "1",
    # build_phase_scenario_rows UI labels
    "Avg PP Runs",
    "Avg PP Wkts",
    "Avg Mid Runs",
    "Avg Mid Wkts",
    "Avg Death Runs",
    "Avg Death Wkts",
    "Avg PP Score",
    # performance.py column keys
    # (already fixed but register for completeness)
    "is_defended",
    "is_chased",
    # phase_engine.py numeric literals
    6.0,
    0.05,
    # matchup_engine.py literals
    "style_key",
    "_join_key",
    "inner",
    "style",
    "Part-Timer",
    "balls_delivered",
    "outs",
    "sr",
    "::",
    100.0,
    # player_math.py literals
    "balls_faced",
    "fours",
    "sixes",
    "boundaries",
    "size",
    "player_name must be a non-empty string.",
    "balls_df is missing required column(s): ",
    # team/venue_calculator.py literals
    "defended",
    "chased",
    "bat1",
    "team_color",
    "team_tone",
    "low_sample_warnings",
    "summary",
    "home",
    "visitor",
    "venue_avg",
    "home_win_pct",
    # venue bias calculator (_bias.py) — key names used in output dicts
    "median", "std",
    "lowest_defended", "highest_chased",
    "direction", "recent_pct", "historical_pct",
    "chose_bat_win_pct", "chose_bowl_win_pct",
    "toss_match_count", "data_available",
    "forced_bat_win_pct", "forced_bowl_win_pct",
    "forced_bat_count", "forced_bowl_count",
    "pct", "inn1_bands",
    "bat1_wins", "chase_wins",
]

SERVICE_LITERAL_REGISTRY += [
    # enrichment.py — format rules key passed through service layer
    "format_rules",
    # serialization_service.py — JsonValue type name used as string literal
    "JsonValue",
]

SERVICE_LITERAL_REGISTRY += [
    # BOUNCER-FIX: Internal dict keys from core/services/builder/
    # _data_builder.py -- keys from _calculate_win_stats accessed by _build_report_data
    "home_stats", "visitor_stats", "valid_1st", "valid_2nd",
    "win_rate", "home_wins", "home_win_bat1", "home_win_bat2",
    "visitor_wins", "visitor_win_bat1", "visitor_win_bat2",
    # _matrix_generator.py -- keys from _compute_overall_stats accessed by _assemble_overall_row
    "total_wins", "total_losses", "total_tie_nr", "total_pct",
]
