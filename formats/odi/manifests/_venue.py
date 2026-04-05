VENUE_CATEGORIES = [
{
            "key": "venue_intel",
            "label": "🏟️ Venue Intelligence",
            "icon": "stadium",
            "group": "intelligence",
            "description": "Stadium-centric analysis: bias, phases, matchups",
            "quick_links": [
                {"label": "Compare Rivals", "category_key": "rivalry"},
                {"label": "Check Form", "category_key": "team_command"},
            ],
            "functions": [
                {
                    "key": "venue_bias",
                    "label": "Toss/Bias Analysis",
                    "icon": "coin",
                    "engine_class": "TeamEngine",
                    "engine_method": "analyze_venue_bias",
                    "required_context": ["venue", "years"],
                    "output_type": "venue_bias_card",
                    "output_schema": {
                        "type": "key_value_list",
                        "fields": [
                            "venue_id", "matches", "total_matches", "bat1_win_pct", "chase_win_pct",
                            "bias_verdict", "sample_reliability", "confidence_interval",
                            "score_distribution", "score_extremes", "bias_trend", "toss_intelligence",
                        ],
                    },
                    "discover_bullets": [
                        "Bat-first vs chase win split with a 95% confidence interval — know how reliable the number is",
                        "Score extremes: the lowest total ever defended and highest ever chased at this ground",
                        "Bias trend: whether the venue's toss advantage is strengthening or weakening over time",
                        "Toss intelligence: win rate when the toss winner chose to bat vs chose to bowl",
                    ],
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
                    "discover_bullets": [
                        "Head-to-head record between both teams at this specific ground",
                        "Each team's batting and chasing win rates, averages, and venue scoring benchmarks",
                        "Last 5 match form guide and average winning score at this venue",
                    ],
                },
                {
                    "key": "home_fortress",
                    "label": "Fortress Report",
                    "icon": "shield",
                    "engine_class": "TeamEngine",
                    "engine_method": "analyze_home_fortress_structured",
                    "required_context": ["venue", "team_a", "years"],
                    "output_type": "home_fortress",
                    "discover_bullets": [
                        "How dominant a team is at this ground across all opponents",
                        "Bat-first vs chasing win rates and average scores for the selected team",
                        "Sample size warnings when data is too thin to draw reliable conclusions",
                    ],
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
                    "discover_bullets": [
                        "Run rates and wicket patterns across powerplay, middle, and death overs at this ground",
                        "How each team performs in every phase at this specific venue",
                        "Side-by-side phase habit comparison to identify tactical mismatches",
                    ],
                },
            ],
        },
]
