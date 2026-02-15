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
            "source": "/api/odi/context/venues",
        },
        "team_a": {
            "type": "dropdown",
            "label": "🏠 Home Team",
            "required": True,
            "source": "/api/odi/context/teams",
        },
        "team_b": {
            "type": "dropdown",
            "label": "✈️ Away Team",
            "required": True,
            "source": "/api/odi/context/teams",
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
                    "engine_method": "analyze_venue_matchup",
                    "required_context": ["venue", "team_a", "team_b", "years"],
                    "output_type": "comparison_table",
                    "output_schema": {
                        "type": "comparison_table",
                        "columns": ["Metric", "team_a_value", "team_b_value"],
                    },
                },
                {
                    "key": "home_fortress",
                    "label": "Fortress Report",
                    "icon": "shield",
                    "engine_class": "TeamEngine",
                    "engine_method": "analyze_home_fortress",
                    "required_context": ["venue", "team_a", "team_b", "years"],
                    "output_type": "comparison_table",
                    "output_schema": {"type": "comparison_table"},
                },
                {
                    "key": "venue_phases",
                    "label": "Phase Breakdown",
                    "icon": "clock",
                    "engine_class": "TeamEngine",
                    "engine_method": "analyze_venue_phases",
                    "required_context": ["venue", "team_a", "years"],
                    "output_type": "table",
                    "output_schema": {
                        "type": "data_table",
                        "columns": [
                            "Phase", "Avg Runs", "Avg Wkts", "Run Rate", "Boundary%",
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
                    "required_context": ["team_a", "team_b", "region", "years"],
                    "output_type": "comparison_table",
                },
                {
                    "key": "continent_perf",
                    "label": "Continent Performance",
                    "icon": "compass",
                    "engine_class": "TeamEngine",
                    "engine_method": "analyze_continent_performance",
                    "required_context": ["team_a", "region", "years"],
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
                    "required_context": ["team_a", "years"],
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
                    "required_context": ["team_a", "years"],
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
                    "required_context": ["team_b"],
                    "extra_inputs": {
                        "player_name": {
                            "type": "combobox",
                            "label": "👤 Player",
                            "required": True,
                            "source": "/api/odi/context/players/{team}",
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
                    "output_type": "comparison_table",
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
                    "extra_inputs": {"squad_builder": True},
                    "output_type": "matchup_table",
                },
            ],
        },

        # ═══════════════════════════════════════════════════════════════
        # 🎯  SCORE PREDICTOR
        # ═══════════════════════════════════════════════════════════════
        {
            "key": "predictor",
            "label": "🎯 Score Predictor",
            "icon": "target",
            "group": "operations",
            "description": "Project 1st innings score based on squads and venue",
            "functions": [
                {
                    "key": "predict_score",
                    "label": "Predict Score",
                    "icon": "zap",
                    "engine_class": "PredictorEngine",
                    "engine_method": "predict_score",
                    "required_context": ["venue", "team_a", "team_b", "years"],
                    "extra_inputs": {"squad_builder": True},
                    "output_type": "prediction_card",
                },
            ],
        },

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


# ── Quick Stats (for validators and introspection) ──────────────────────
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
