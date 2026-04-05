TEAM_CATEGORIES = [
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
]
