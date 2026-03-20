"""
Context builders for engine call parameters.

Extracted from api/main.py to keep request orchestration separate
from context construction logic.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Protocol, TypedDict, cast

import pandas as pd

from core.interfaces.team_interface import MatchContext


class DataAccessProtocol(Protocol):
    def get_balls(
        self,
        players: Optional[List[str]] = None,
        match_ids: Optional[List[str]] = None,
        venue_id: Optional[str] = None,
    ) -> pd.DataFrame:
        ...

    def get_matches(
        self,
        country: Optional[str] = None,
    ) -> pd.DataFrame:
        ...


class AnalyzerProtocol(Protocol):
    match_df: pd.DataFrame
    phase_df: pd.DataFrame
    dal: Optional[DataAccessProtocol]
    format_rules: Dict[str, object]
    team_engine: object
    player_engine: object
    predictor_engine: object


class EngineCallParams(TypedDict, total=False):
    stadium_name: str
    stadium_id: str
    venue_id: str
    home_team: str
    away_team: str
    opp_team: str
    team_name: str
    batting_team: str
    bowling_team: str
    years: int
    years_back: int
    limit: int
    continent: str
    country: Optional[str]
    country_name: str
    ground: Optional[str]
    player_name: str
    name: str
    batter: str
    opposition: str
    team_a_name: str
    team_b_name: str
    team_a_players: List[str]
    team_b_players: List[str]
    players: List[str]
    opposition_bowlers: List[str]
    bowlers: List[str]
    home_xi: List[str]
    away_xi: List[str]
    context_df: pd.DataFrame
    raw_balls_df: pd.DataFrame
    match_context: MatchContext


class EngineDefaults(TypedDict, total=False):
    recent_match_ids_limit: int
    recent_context_fallback_years: int
    venue_stats_fallback_years: int


def _safe_int(value: object, default: int) -> int:
    try:
        parsed = int(value)
        return parsed if parsed > 0 else default
    except (TypeError, ValueError):
        return default


def _engine_defaults(analyzer: AnalyzerProtocol) -> EngineDefaults:
    raw_rules = analyzer.format_rules if isinstance(analyzer.format_rules, dict) else {}
    defaults = raw_rules.get("engine_defaults", {})
    if isinstance(defaults, dict):
        return cast(EngineDefaults, defaults)
    return {}


def _engine_default_int(analyzer: AnalyzerProtocol, key: str, minimum: int) -> int:
    raw_value = _engine_defaults(analyzer).get(key)
    parsed = _safe_int(raw_value, minimum)
    return parsed if parsed >= minimum else minimum


def _build_recent_player_context(
    analyzer: AnalyzerProtocol,
    players: List[str],
    years: Optional[object],
    venue_id: Optional[str] = None,
) -> pd.DataFrame:
    dal = analyzer.dal
    if dal is None:
        return pd.DataFrame()

    clean_players = sorted({
        str(player).strip()
        for player in players
        if str(player).strip()
    })
    if not clean_players:
        return pd.DataFrame()

    context_df = dal.get_balls(players=clean_players, venue_id=venue_id or None)
    if context_df is None or context_df.empty:
        return pd.DataFrame()

    years_back = _safe_int(
        years,
        _engine_default_int(analyzer, "recent_context_fallback_years", 1),
    )
    if "start_date" in context_df.columns:
        context_df = context_df.copy()
        context_df["start_date"] = pd.to_datetime(context_df["start_date"], errors="coerce")
        max_date = context_df["start_date"].max()
        if pd.notna(max_date):
            cutoff_date = pd.Timestamp(max_date).floor("D") - pd.DateOffset(years=years_back)
        else:
            cutoff_date = pd.Timestamp.now().floor("D") - pd.DateOffset(years=years_back)
        context_df = context_df[context_df["start_date"] >= cutoff_date]
    return context_df


def _inject_team_engine_context(
    analyzer: AnalyzerProtocol,
    engine_class_name: str,
    engine_method_name: str,
    call_params: EngineCallParams,
) -> EngineCallParams:
    if engine_class_name != "TeamEngine":
        return call_params

    params = cast(EngineCallParams, dict(call_params))
    _ = engine_method_name
    match_df = getattr(analyzer, "match_df", pd.DataFrame())
    phase_df = getattr(analyzer, "phase_df", pd.DataFrame())
    raw_rules = analyzer.format_rules if isinstance(analyzer.format_rules, dict) else {}
    tactical = raw_rules.get("tactical_thresholds", {})
    context: MatchContext = {}
    if isinstance(match_df, pd.DataFrame):
        context["match_df"] = match_df
        if "start_date" in match_df.columns and not match_df.empty:
            dates = pd.to_datetime(match_df["start_date"], errors="coerce")
            max_date = dates.max()
            if pd.notna(max_date):
                context["reference_date"] = pd.Timestamp(max_date).floor("D")
    if isinstance(phase_df, pd.DataFrame):
        context["phase_df"] = phase_df
    if isinstance(tactical, dict):
        normalized: Dict[str, int] = {}
        for key, value in tactical.items():
            try:
                normalized[str(key)] = int(value)
            except (TypeError, ValueError):
                continue
        context["tactical_thresholds"] = normalized
    params["match_context"] = context
    return params


def _inject_player_engine_context(
    analyzer: AnalyzerProtocol,
    engine_class_name: str,
    engine_method_name: str,
    call_params: EngineCallParams,
) -> EngineCallParams:
    if engine_class_name != "PlayerEngine":
        return call_params

    params = cast(EngineCallParams, dict(call_params))
    method = engine_method_name

    if method in {"compare_squads", "get_squad_comparison_data"}:
        players = list(params.get("team_a_players") or []) + list(params.get("team_b_players") or [])
        params["context_df"] = _build_recent_player_context(analyzer, players, params.get("years"))
        return params

    if method in {"analyze_squad_types"}:
        players = list(params.get("players") or []) + list(params.get("opposition_bowlers") or [])
        params["context_df"] = _build_recent_player_context(analyzer, players, params.get("years"))
        return params

    if method in {"analyze_dual_squad_matrix"}:
        players = (
            list(params.get("team_a_players") or [])
            + list(params.get("team_b_players") or [])
        )
        params["context_df"] = _build_recent_player_context(analyzer, players, params.get("years"))
        return params

    if method in {"get_matchups"}:
        players = []
        batter = params.get("batter")
        if batter:
            players.append(str(batter))
        players.extend([str(p) for p in (params.get("bowlers") or [])])
        players.extend([str(p) for p in (params.get("home_xi") or [])])
        players.extend([str(p) for p in (params.get("away_xi") or [])])
        venue_id = str(params.get("venue_id") or "").strip() or None
        context_df = _build_recent_player_context(
            analyzer, players, params.get("years"), venue_id=venue_id
        )
        home_xi = list(params.get("home_xi") or [])
        away_xi = list(params.get("away_xi") or [])
        if (
            home_xi
            and away_xi
            and not context_df.empty
            and "striker" in context_df.columns
            and "bowler" in context_df.columns
        ):
            home_set = set(home_xi)
            away_set = set(away_xi)
            dir_mask = (
                (context_df["striker"].isin(home_set) & context_df["bowler"].isin(away_set))
                | (context_df["striker"].isin(away_set) & context_df["bowler"].isin(home_set))
            )
            context_df = context_df[dir_mask].copy()
        params["context_df"] = context_df
        return params

    if method == "analyze_player_profile":
        player_name = str(params.get("player_name") or params.get("name") or "").strip()
        raw_balls_df = _build_recent_player_context(analyzer, [player_name], params.get("years"))
        country = params.get("country")
        if country is None:
            raw_country = params.get("country_name")
            country = str(raw_country).strip() if raw_country else None
        if (
            country
            and not raw_balls_df.empty
            and "match_id" in raw_balls_df.columns
        ):
            dal = getattr(analyzer, "dal", None)
            if dal is not None:
                try:
                    country_matches = dal.get_matches(country=country)
                    if not country_matches.empty and "match_id" in country_matches.columns:
                        valid_ids: set[str] = set(country_matches["match_id"].astype(str))
                        raw_balls_df = raw_balls_df[
                            raw_balls_df["match_id"].astype(str).isin(valid_ids)
                        ].copy()
                except Exception:
                    pass  # country column absent from matches table — skip filter
        params["country"] = country
        params["ground"] = params.get("ground") or params.get("venue_id")
        params["raw_balls_df"] = raw_balls_df
        params.pop("country_name", None)
        return params

    if method == "get_player_profile":
        player_name = str(params.get("player_name") or params.get("name") or "").strip()
        params["raw_balls_df"] = _build_recent_player_context(analyzer, [player_name], params.get("years"))
        return params

    return params
