RIVALRY_CATEGORIES = [
{
            "key": "rivalry",
            "label": "🤝 Rivalry Lab",
            "icon": "handshake",
            "group": "intelligence",
            "description": "Head-to-head analysis between two teams",
            "quick_links": [
                {"label": "Venue Deep-Dive", "category_key": "venue_intel"},
                {"label": "Scout Players", "category_key": "player_scout"},
            ],
            "functions": [
                {
                    "key": "global_h2h",
                    "label": "Global H2H",
                    "icon": "swords",
                    "engine_class": "TeamEngine",
                    "engine_method": "analyze_global_h2h_structured",
                    "required_context": ["team_a", "team_b", "years"],
                    "output_type": "global_h2h_report",
                },
                {
                    "key": "country_h2h",
                    "label": "Host Country H2H",
                    "icon": "flag",
                    "engine_class": "TeamEngine",
                    "engine_method": "analyze_country_h2h",
                    "required_context": ["team_a", "team_b", "years"],
                    "extra_inputs": {
                        "country_name": {
                            "type": "dropdown",
                            "label": "Host Country",
                            "required": False,
                            "source": "host_countries",
                        },
                    },
                    "output_type": "country_h2h_report",
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
]
