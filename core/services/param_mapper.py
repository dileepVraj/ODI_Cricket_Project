from core.interfaces.team_types import ManifestFunctionDef, RawContextParams, MappedEngineParams

class ParamMapperService:
    """
    Industry Standard Parameter Mapping Service.
    Handles the translation of frontend context names to engine-specific argument names.
    This decouples the API contract from the underlying engine implementations.
    """

    # --- MAPPING CONFIGURATION ---
    # Defines how frontend context keys map to engine method arguments.
    # Pattern: method_name -> { context_key -> argument_name }
    # Use "*" for global defaults.
    MAPPING_REGISTRY = {
        "*": {
            "venue": "stadium_name",
            "team_a": "home_team",
            "team_b": "opp_team",
            "years": "years_back",
            "region": "continent",
        },
        # predict_score mapping removed — pending Phase 12 rebuild
        "compare_squads": {
            "venue": "venue_id",
            "team_a": "team_a_name",
            "team_b": "team_b_name",
            "home_xi": "team_a_players",
            "away_xi": "team_b_players",
            "years": "years",
        },
        "analyze_player_profile": {
            "venue": "venue_id",
            "team_b": "opposition",
            "years": "years", # Will be overridden to 50
        },
        "analyze_venue_phases": {
            "venue": "stadium_id",
            "team_b": "away_team",
            "years": "years",
        },
        "generate_pack": {
            "venue": "venue",
            "team_a": "home",
            "team_b": "away",
        },
        "analyze_squad_types": {
            "team_a": "team_name",
            "home_xi": "players",
            "away_xi": "opposition_bowlers",
            "years": "years",
        },
        "analyze_team_form": {
            "team_a": "team_name",
            "team_b": "opp_team",
            "region": "continent",
        },
        "analyze_away_performance": {
            "team_b": "team_name",
        },
        "analyze_global_performance": {
            "team_a": "team_name",
        },
        "analyze_continent_performance": {
            "team_a": "team_name",
        },
    }

    @classmethod
    def map_params(cls, fn_def: ManifestFunctionDef, raw_params: RawContextParams) -> MappedEngineParams:
        """
        Maps frontend context to engine arguments.
        Enforces strict filtering based on the format manifest to prevent param leakage.
        """
        method_name = fn_def.get("engine_method", "")
        function_key = fn_def.get("key", "")
        
        # 1. IDENTIFY ALLOWED KEYS FROM MANIFEST
        # The manifest is the "Filter of Truth". We only allow what the manifest declares.
        required = set(fn_def.get("required_context", []))
        optional = set(fn_def.get("optional_context", []))
        extra_input_defs = fn_def.get("extra_inputs", {})
        
        # extra_inputs can be a dict of field defs or a bool (like squad_builder: True)
        extra = set()
        if isinstance(extra_input_defs, dict):
            extra = set(extra_input_defs.keys())
        
        # Universal technical/system keys that handle cross-cutting concerns (e.g., squads)
        system_keys = {"home_xi", "away_xi", "context", "player_name", "batter", "bowlers"}
        
        allowed_keys = required | optional | extra | system_keys
        
        # 2. FILTER & INITIALIZE
        input_params = {k: v for k, v in raw_params.items() if k in allowed_keys}
        mapped_params = {}

        # 3. APPLY MAPPING REGISTRY
        # Method mappings inherit global defaults, then override as needed.
        # This prevents missing-key regressions (e.g., team_a leaking through
        # as an unexpected kwarg when a method-specific mapping omits it).
        mapping = {
            **cls.MAPPING_REGISTRY.get("*", {}),
            **cls.MAPPING_REGISTRY.get(method_name, {}),
        }
        
        for key, val in input_params.items():
            # Skip remapping for specific logic handled in overrides section
            if key in ("match_limit", "match_time", "toss_result", "pitch_report", "player_name"):
                continue
                
            arg_name = mapping.get(key)
            if arg_name:
                mapped_params[arg_name] = val
            else:
                # Direct passthrough only for system keys or manifest-declared extras.
                # Unknown context keys are ignored to avoid engine signature mismatches.
                if key in system_keys or key in extra:
                    mapped_params[key] = val

        # 4. OVERRIDES & SPECIAL LOGIC (The "Glue" Layer)
        
        # A. Player Profile 50-year default
        if method_name == "analyze_player_profile":
            mapped_params["years"] = 50
            
        # B. Matchup Name Mapping
        if method_name == "get_matchups" and "player_name" in input_params:
            mapped_params["batter"] = input_params["player_name"]

        # B2. Player profile explicit passthrough
        if method_name in {"analyze_player_profile", "get_player_profile"} and "player_name" in input_params:
            mapped_params["player_name"] = input_params["player_name"]

        # C. Match Limit (Team Form)
        if method_name == "analyze_team_form" and "match_limit" in input_params:
            raw_limit = input_params["match_limit"]
            try:
                mapped_params["limit"] = int(raw_limit) if raw_limit not in (None, "", "All") else 10
            except (TypeError, ValueError):
                mapped_params["limit"] = 10

        # D. Match Pack Context Bundle
        if method_name == "generate_pack":
            context = {
                "time": input_params.get("match_time"),
                "toss": input_params.get("toss_result"),
                "pitch": input_params.get("pitch_report"),
            }
            mapped_params["context"] = {k: v for k, v in context.items() if v is not None}
            # Keep API execute path CPU-bound by preventing report file writes.
            mapped_params["persist"] = False

        return mapped_params
