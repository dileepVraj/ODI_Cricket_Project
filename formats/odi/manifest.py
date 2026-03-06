"""
formats/odi/manifest.py — ODI Format Capability Manifest (v1.0)

This manifest declares ALL capabilities of the ODI format.
The frontend reads this to dynamically build:
  - Sidebar navigation (categories)
  - Screen layouts (tabs = functions within each category)
  - Context bar inputs (what filters each function needs)
  - Output rendering (which React component to use)

RULES:
  - Every `engine_method` MUST exist on the declared `engine_class`
  - Every `output_type` MUST map to a known frontend renderer
  - Every `required_context` field MUST be in `context_fields`
  - This file is validated by `scripts/validate_manifest.py`
"""
from formats.odi.config.players import BOWLER_STYLES, PLAYER_ROLES

TACTICAL_THRESHOLDS = {
    "unmapped_min_balls": 6,
    "form_window_matches": 10,
    "structural_weakness_avg_max": 25,
    "dominant_matchup_avg_min": 50,
    "bunny_outs_hard": 3,
    "bunny_outs_soft": 2,
    "bunny_balls_per_out_max": 15,
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
    "min_innings_threshold": 2,
    "profile_sr_min_balls": 60,
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

MANIFEST = {
    # ── Format Identity ──────────────────────────────────────────────────
    "format_key": "odi",
    "format_label": "Men's ODI",
    "format_icon": "🏏",
    "version": "1.0",

    # ── Context Fields ───────────────────────────────────────────────────
    # These define the global filter bar at the top of the UI.
    # Each function declares which of these it requires.
    "context_fields": {
        "venue": {
            "type": "combobox",
            "label": "🏟️ Venue",
            "required": False,
            "source": "/api/v1/odi/context/venues",
        },
        "team_a": {
            "type": "dropdown",
            "label": "🏠 Home Team",
            "required": True,
            "source": "/api/v1/odi/context/teams",
        },
        "team_b": {
            "type": "dropdown",
            "label": "✈️ Away Team",
            "required": True,
            "source": "/api/v1/odi/context/teams",
        },
        "years": {
            "type": "slider",
            "label": "📅 Years",
            "min": 1,
            "max": 50,
            "default": 5,
            "required": False,
        },
        "region": {
            "type": "dropdown",
            "label": "🌏 Region",
            "required": False,
            "options": ["All", "Asia", "Europe", "Oceania", "Africa", "Americas"],
        },
    },

    # ── Approved Output Types ────────────────────────────────────────────
    # Frontend renderer map. Adding a new type = adding a new React component.
    "output_types": [
        "report",            # Key-value stat cards (ReportCard)
        "table",             # Sortable data table (DataTable)
        "comparison_table",  # Side-by-side team comparison (ComparisonTable)
        "matrix_table",      # Opponent-per-row dominance matrix (MatrixTable)
        "form_table",        # Recent form with emoji indicators (FormTable)
        "profile_card",      # Player stat sheet (PlayerProfileCard)
        "prediction_card",   # Score projection display (PredictionCard)
        "matchup_table",     # Batter vs bowler grid (MatchupTable)
        "download_json",     # File download + preview (DownloadPanel)
        "phase_analysis",    # Venue phase breakdown (PhaseAnalysisCard)
        "venue_matchup_report", # High-fidelity dual-card matchup
    ],

    # ── Categories ───────────────────────────────────────────────────────
    # Each category becomes a sidebar item. Functions become tabs.
    "categories": [

        # ═══════════════════════════════════════════════════════════════
        # 🏟️  VENUE INTELLIGENCE
        # ═══════════════════════════════════════════════════════════════
        {
            "key": "venue_intel",
            "label": "🏟️ Venue Intelligence",
            "icon": "stadium",
            "group": "intelligence",
            "description": "Stadium-centric analysis: bias, phases, matchups",
            "functions": [
                {
                    "key": "venue_bias",
                    "label": "Toss/Bias Analysis",
                    "icon": "coin",
                    "engine_class": "TeamEngine",
                    "engine_method": "analyze_venue_bias",
                    "required_context": ["venue", "years"],
                    "output_type": "report",
                    "output_schema": {
                        "type": "key_value_list",
                        "fields": [
                            "venue_id", "matches", "bat1_wins", "chase_wins",
                            "bat1_pct", "chase_pct", "bias_verdict",
                        ],
                    },
                },
                {
                    "key": "venue_matchup",
                    "label": "Venue Matchup",
                    "icon": "map-marker",
                    "engine_class": "TeamEngine",
                    "engine_method": "analyze_venue_matchup_structured",
                    "required_context": ["venue", "team_a", "team_b", "years"],
                    "output_type": "venue_matchup_report",
                    "output_schema": {
                        "type": "nested_dict",
                        "fields": ["summary", "team_a", "team_b", "venue_avg"]
                    },
                },
                {
                    "key": "home_fortress",
                    "label": "Fortress Report",
                    "icon": "shield",
                    "engine_class": "TeamEngine",
                    "engine_method": "analyze_home_fortress",
                    "required_context": ["venue", "team_a", "years"],
                    "output_type": "comparison_table",
                    "output_schema": {"type": "comparison_table"},
                },
                {
                    "key": "venue_phases",
                    "label": "Phase Breakdown",
                    "icon": "clock",
                    "engine_class": "TeamEngine",
                    "engine_method": "analyze_venue_phases",
                    "required_context": ["venue", "team_a", "team_b", "years"],
                    "output_type": "phase_analysis",
                    "output_schema": {
                        "type": "nested_dict",
                        "fields": [
                            "stadium_id", "match_count", "years",
                            "filter_criteria", "baseline", "home_at_venue", "away_at_venue", "global_habits",
                        ],
                    },
                },
            ],
        },

        # ═══════════════════════════════════════════════════════════════
        # 🤝  RIVALRY LAB
        # ═══════════════════════════════════════════════════════════════
        {
            "key": "rivalry",
            "label": "🤝 Rivalry Lab",
            "icon": "handshake",
            "group": "intelligence",
            "description": "Head-to-head analysis between two teams",
            "functions": [
                {
                    "key": "global_h2h",
                    "label": "Global H2H",
                    "icon": "globe",
                    "engine_class": "TeamEngine",
                    "engine_method": "analyze_global_h2h",
                    "required_context": ["team_a", "team_b", "years"],
                    "output_type": "comparison_table",
                },
                {
                    "key": "country_h2h",
                    "label": "Host Country H2H",
                    "icon": "flag",
                    "engine_class": "TeamEngine",
                    "engine_method": "analyze_country_h2h",
                    "required_context": ["team_a", "years"],
                    "optional_context": ["team_b"],
                    "extra_inputs": {
                        "country_name": {
                            "type": "dropdown",
                            "label": "Host Country",
                            "required": False,
                            "source": "/api/v1/odi/context/host_countries",
                        },
                    },
                    "output_type": "comparison_table",
                },
                {
                    "key": "continent_perf",
                    "label": "Continent Performance",
                    "icon": "compass",
                    "engine_class": "TeamEngine",
                    "engine_method": "analyze_continent_performance",
                    "required_context": ["team_a", "region", "years"],
                    "optional_context": ["team_b"],
                    "output_type": "matrix_table",
                },
            ],
        },

        # ═══════════════════════════════════════════════════════════════
        # 📊  TEAM COMMAND
        # ═══════════════════════════════════════════════════════════════
        {
            "key": "team_command",
            "label": "📊 Team Command",
            "icon": "bar-chart",
            "group": "intelligence",
            "description": "Team dominance matrices and form tracker",
            "functions": [
                {
                    "key": "home_dominance",
                    "label": "🏠 Home Dominance",
                    "icon": "home",
                    "engine_class": "TeamEngine",
                    "engine_method": "analyze_home_dominance",
                    "required_context": ["team_a", "years"],
                    "output_type": "matrix_table",
                },
                {
                    "key": "away_performance",
                    "label": "✈️ Away Performance",
                    "icon": "plane",
                    "engine_class": "TeamEngine",
                    "engine_method": "analyze_away_performance",
                    "required_context": ["team_b", "years"],
                    "output_type": "matrix_table",
                },
                {
                    "key": "global_performance",
                    "label": "🌍 Global Power",
                    "icon": "globe",
                    "engine_class": "TeamEngine",
                    "engine_method": "analyze_global_performance",
                    "required_context": ["team_a", "years"],
                    "output_type": "matrix_table",
                },
                {
                    "key": "team_form",
                    "label": "📉 Recent Form",
                    "icon": "trending-down",
                    "engine_class": "TeamEngine",
                    "engine_method": "analyze_team_form",
                    "required_context": ["team_a"],
                    "extra_inputs": {
                        "match_limit": {
                            "type": "text",
                            "label": "Recent Matches (count)",
                            "required": True,
                        },
                    },
                    "output_type": "form_table",
                },
            ],
        },

        # ═══════════════════════════════════════════════════════════════
        # 👤  PLAYER SCOUT
        # ═══════════════════════════════════════════════════════════════
        {
            "key": "player_scout",
            "label": "👤 Player Scout",
            "icon": "user",
            "group": "players",
            "description": "Individual player deep-dive profiles",
            "functions": [
                {
                    "key": "player_profile",
                    "label": "Player Profile",
                    "icon": "id-card",
                    "engine_class": "PlayerEngine",
                    "engine_method": "analyze_player_profile",
                    "required_context": [],
                    "extra_inputs": {
                        "player_name": {
                            "type": "combobox",
                            "label": "👤 Player",
                            "required": True,
                            "source": "/api/v1/odi/context/players/All",
                        },
                    },
                    "output_type": "profile_card",
                },
            ],
        },

        # ═══════════════════════════════════════════════════════════════
        # ⚔️  SQUAD BATTLE
        # ═══════════════════════════════════════════════════════════════
        {
            "key": "squad_battle",
            "label": "⚔️ Squad Battle",
            "icon": "users",
            "group": "players",
            "description": "11 vs 11 squad comparison with tactical matchups",
            "functions": [
                {
                    "key": "compare_squads",
                    "label": "Squad Comparison",
                    "icon": "columns",
                    "engine_class": "PlayerEngine",
                    "engine_method": "compare_squads",
                    "required_context": ["venue", "team_a", "team_b"],
                    "extra_inputs": {"squad_builder": True},
                    "output_type": "table",
                },
                {
                    "key": "tactical_matrix",
                    "label": "Tactical Matrix",
                    "icon": "grid",
                    "engine_class": "PlayerEngine",
                    "engine_method": "analyze_squad_types",
                    "required_context": ["team_a", "team_b"],
                    "extra_inputs": {"squad_builder": True},
                    "output_type": "table",
                },
                {
                    "key": "matchups",
                    "label": "Player Matchups",
                    "icon": "crosshair",
                    "engine_class": "PlayerEngine",
                    "engine_method": "get_matchups",
                    "required_context": ["team_a", "team_b"],
                    "extra_inputs": {
                        "squad_builder": True,
                        "player_name": {
                            "type": "combobox",
                            "label": "🏏 Batter",
                            "required": True,
                            "source": "/api/v1/odi/context/players/{team}",
                        },
                    },
                    "output_type": "matchup_table",
                },
            ],
        },

        # predict_score — removed, pending Phase 12 rebuild
        # (The "🎯 Score Predictor" category and its predict_score function entry
        #  have been removed. Re-add here when predict_score() is rebuilt per
        #  the requirements in formats/odi/predictor.py)


        # ═══════════════════════════════════════════════════════════════
        # 🚀  MATCH PACK
        # ═══════════════════════════════════════════════════════════════
        {
            "key": "match_pack",
            "label": "🚀 Match Pack",
            "icon": "rocket",
            "group": "operations",
            "description": "Full pre-match intelligence report generator",
            "functions": [
                {
                    "key": "generate_pack",
                    "label": "Generate Analyst Report",
                    "icon": "file-text",
                    "engine_class": "MatchPackGenerator",
                    "engine_method": "generate_pack",
                    "required_context": ["venue", "team_a", "team_b"],
                    "extra_inputs": {
                        "squad_builder": True,
                        "match_time": {
                            "type": "text",
                            "label": "🕒 Match Time",
                            "required": False,
                        },
                        "toss_result": {
                            "type": "dropdown",
                            "label": "🪙 Toss Result",
                            "required": False,
                            "options": ["Unknown", "Bat", "Bowl"],
                        },
                        "pitch_report": {
                            "type": "textarea",
                            "label": "🌱 Pitch Report",
                            "required": False,
                        },
                    },
                    "output_type": "download_json",
                },
            ],
        },
    ],
}


# Phase 11.2: Engine literal registry for compliance-bouncer
ENGINE_LITERAL_REGISTRY = ['CricketAnalyzer', 'match_id', 'player', 'date', 'team', "Missing required format rule '", "'. Define it in manifest FORMAT_RULES and pass it into PlayerEngine.", "Invalid tactical threshold '", "': ", '. Expected integer.', "Missing required format rule 'default_player_role'. Define it in manifest FORMAT_RULES and pass it into PlayerEngine.", "Missing required format rule 'default_years_window'. Define it in manifest FORMAT_RULES and pass it into PlayerEngine.", "Invalid format rule 'default_years_window': ", "Format rule 'default_years_window' must be > 0.", "Invalid engine default '", "Missing engine default '", "' in FORMAT_RULES['engine_defaults'].", 'reference_date', 'D', "Invalid reference_date rule '%s': %s", '_reference_date', 'Invalid years value: ', 'years must be > 0.', "Missing tactical threshold '", "' in FORMAT_RULES['tactical_thresholds'].", 'is_playing_xi', 'start_date', 11, 'batting_team', 'striker', 'non_striker', 'bowling_team', 'bowler', 'coerce', '_', '|', 'squad_metrics', 'player_stats', 'style_metrics', 'average_raw', 'STRUCTURAL_WEAKNESS', ' struggles vs ', ' (Avg ', ')', 'DOMINANT_MATCHUP', ' dominates ', 'runs_off_bat', 'sum', 'count', 'player_dismissed', 'Balls', 'Runs', 'Outs', 'Style', 'IsBunny', 'Avg', 'SR', 100, 'Bowler', 'records', 'context', 'vs_team', 'role', 'batting', 'runs', 'innings', 'dismissals', 'balls', 'bowling', 60, 'N/A', 'opponent', 'at_venue', "Missing required format rule 'min_balls_for_completed_innings'. Define it in manifest FORMAT_RULES and pass it into TeamEngine.", "Invalid format rule 'min_balls_for_completed_innings': ", "Format rule 'min_balls_for_completed_innings' must be > 0.", "Missing required format rule 'phases'. Define it in manifest FORMAT_RULES and pass it into TeamEngine.", "Missing required format rule 'tactical_thresholds'. Define it in manifest FORMAT_RULES and pass it into TeamEngine.", '_tactical_thresholds', 'status', 'string', 'included', 'excluded (no result)', 'excluded (short 2nd)', 'Visitors', 'vs ', 'team_bat_1', 'team_bat_2', 'FORTRESS REPORT (', 'win_pct', 'tie_nr', 'name', 'stats', 'avg_1st', '-', 'avg_2nd', 'avg_win_score', 'has_low_sample_warnings', 'has_form_guide', 'winner', 'tie', 'no result', 'nan', 'none', 'Batting 1st Avg', 'avg', 'Avg Winning Score', 'avg_win', 'Chasing Avg', ' ', ' (n=', 'gray', 'high', 'high_1st', 'low', 'low_1st', 'avg_1st_win', 'low_def', 'low_defended', 'high_chased', 'succ', 'avg_succ', 'fail', 'avg_fail', 'score_inn2', 'score_inn1', 'last_5_home', 'last_5_away', ',', 'phase_df', 'phase_overs', 'pp', 'mid', 'dth', 'balls_inn1', 'wickets_inn1', 'balls_inn2', 'wickets_inn2', '.', 'abandoned', 'min_first_innings_balls', 'min_first_innings_overs', 'keep_all_outs', 'keep_successful_chases', 'drop_short_no_result_only', 'MATCH_IDS', 'start_year', 'bat_first', 'home_team_pp_runs', 'pp_runs', 'away_team_pp_runs', 'home_team_pp_wkts', 'pp_wkts', 'away_team_pp_wkts', 'home_team_mid_runs', 'mid_runs', 'away_team_mid_runs', 'home_team_mid_wkts', 'mid_wkts', 'away_team_mid_wkts', 'home_team_dth_runs', 'dth_runs', 'away_team_dth_runs', 'home_team_dth_wkts', 'dth_wkts', 'away_team_dth_wkts', 'chasing', 'rr', 'away', 'scenario_rows', 'NEUTRAL', 'BAT FIRST', 'BOWL FIRST', 'period', 'total_matches', 'bat1_win_pct', 'chase_win_pct', 'avg_1st_inn', 'avg_2nd_inn', 'percent_breakdown', 'chase', 'highlight_flags', 'has_strong_bias', 'derived_badges', 'raw_matches', 'GLOBAL RIVALRY REPORT', 'HOME COUNTRY', 'HOST COUNTRY REPORT (', 'DOMINANCE MATRIX', 'AWAY PERFORMANCE MATRIX', 'GLOBAL PERFORMANCE MATRIX', 'Global', 'REGIONAL RIVALRY REPORT (', 'PERFORMANCE MATRIX: ']

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
    "min_innings_threshold",
    "profile_sr_min_balls",
    # PLAYER_CONTEXT_TYPES values absent from the original engine registry
    "all",
    "All",
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
]


def get_manifest_stats() -> dict:
    """Returns summary statistics about this manifest."""
    total_funcs = sum(len(cat["functions"]) for cat in MANIFEST["categories"])
    return {
        "format": MANIFEST["format_key"],
        "categories": len(MANIFEST["categories"]),
        "functions": total_funcs,
        "output_types_used": sorted(set(
            fn["output_type"]
            for cat in MANIFEST["categories"]
            for fn in cat["functions"]
        )),
        "engine_classes_used": sorted(set(
            fn["engine_class"]
            for cat in MANIFEST["categories"]
            for fn in cat["functions"]
        )),
    }
