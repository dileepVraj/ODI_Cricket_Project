from core.services.param_mapper import ParamMapperService


def test_map_params_continent_performance_uses_team_name():
    fn_def = {
        "engine_method": "analyze_continent_performance",
        "required_context": ["team_a", "region", "years"],
    }
    raw_params = {"team_a": "Sri Lanka", "region": "Asia", "years": 10}

    mapped = ParamMapperService.map_params(fn_def, raw_params)

    assert mapped == {
        "team_name": "Sri Lanka",
        "continent": "Asia",
        "years_back": 10,
    }
    assert "home_team" not in mapped


def test_map_params_continent_performance_maps_optional_away_team():
    fn_def = {
        "engine_method": "analyze_continent_performance",
        "required_context": ["team_a", "region", "years"],
        "optional_context": ["team_b"],
    }
    raw_params = {
        "team_a": "Sri Lanka",
        "team_b": "England",
        "region": "Asia",
        "years": 10,
    }

    mapped = ParamMapperService.map_params(fn_def, raw_params)

    assert mapped == {
        "team_name": "Sri Lanka",
        "opp_team": "England",
        "continent": "Asia",
        "years_back": 10,
    }
    assert "home_team" not in mapped


def test_map_params_global_performance_uses_team_name():
    fn_def = {
        "engine_method": "analyze_global_performance",
        "required_context": ["team_a", "years"],
    }
    raw_params = {"team_a": "India", "years": 5}

    mapped = ParamMapperService.map_params(fn_def, raw_params)

    assert mapped == {"team_name": "India", "years_back": 5}
    assert "home_team" not in mapped


def test_map_params_away_performance_uses_team_name():
    fn_def = {
        "engine_method": "analyze_away_performance",
        "required_context": ["team_b", "years"],
    }
    raw_params = {"team_b": "England", "years": 7}

    mapped = ParamMapperService.map_params(fn_def, raw_params)

    assert mapped == {"team_name": "England", "years_back": 7}
    assert "opp_team" not in mapped


def test_map_params_home_dominance_still_uses_home_team():
    fn_def = {
        "engine_method": "analyze_home_dominance",
        "required_context": ["team_a", "years"],
    }
    raw_params = {"team_a": "India", "years": 6}

    mapped = ParamMapperService.map_params(fn_def, raw_params)

    assert mapped == {"home_team": "India", "years_back": 6}
