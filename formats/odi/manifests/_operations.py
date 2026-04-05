OPERATIONS_CATEGORIES = [
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
]
