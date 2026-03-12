"""Pure vectorized rivalry and team-performance calculators."""

from __future__ import annotations

from typing import Mapping, TypedDict, cast

import pandas as pd

from config.shared.team_colors import TEAM_COLORS
from config.shared.venues import VENUE_MAP, get_country_prefixes
from core.calculators.performance import calculate_team_metrics
from core.interfaces.team_types import ComparisonReportRows, MatrixReportRows, TeamFormRows, VenueMatchupReport
from core.services.match_filter_service import MatchFilterService, apply_smart_filters as apply_match_filters
from core.services.report_builder import ReportBuilder
from core.services.report_formatter import ReportFormatter
from core.services.serialization_service import SerializationService
from core.services.venue_service import VenueService


class GlobalH2HContext(TypedDict):
    home_team: str
    opp_team: str
    years_back: int
    reference_date: pd.Timestamp
    min_balls_for_completed_innings: int
    competitive_chase_threshold: int
    low_sample_min_matches: int
    percent_scale: int


class CountryH2HContext(TypedDict):
    home_team: str
    opp_team: str
    country_name: str | None
    years_back: int
    reference_date: pd.Timestamp
    min_balls_for_completed_innings: int
    competitive_chase_threshold: int


class HomeDominanceContext(TypedDict):
    home_team: str
    years_back: int
    reference_date: pd.Timestamp
    min_balls_for_completed_innings: int
    region: Mapping[str, str]


class AwayPerformanceContext(TypedDict):
    team_name: str
    years_back: int
    reference_date: pd.Timestamp
    min_balls_for_completed_innings: int
    region: Mapping[str, str]


class GlobalPerformanceContext(TypedDict):
    team_name: str
    years_back: int
    reference_date: pd.Timestamp
    min_balls_for_completed_innings: int


class ContinentPerformanceContext(TypedDict):
    team_name: str
    continent: str
    opp_team: str
    years_back: int
    reference_date: pd.Timestamp
    min_balls_for_completed_innings: int
    competitive_chase_threshold: int


class TeamFormContext(TypedDict):
    team_name: str
    opp_team: str
    continent: str
    limit: int
    min_balls_for_completed_innings: int


class ComparisonRowsPayload(TypedDict):
    rows: ComparisonReportRows


class VenueMatchupPayload(TypedDict):
    payload: VenueMatchupReport


class GlobalH2HStructuredPayload(TypedDict):
    payload: VenueMatchupReport


class MatrixRowsPayload(TypedDict):
    rows: MatrixReportRows


class TeamFormRowsPayload(TypedDict):
    rows: TeamFormRows


class ContinentRowsPayload(TypedDict):
    rows: MatrixReportRows | ComparisonReportRows


def _empty_like(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.iloc[0:0].copy() if isinstance(frame, pd.DataFrame) else pd.DataFrame()


def _filter_year_window(match_df: pd.DataFrame, reference_date: pd.Timestamp, years_back: int) -> pd.DataFrame:
    if match_df.empty:
        return _empty_like(match_df)
    if "start_date" not in match_df.columns:
        return match_df.copy()
    cutoff = reference_date - pd.DateOffset(years=years_back)
    return match_df[match_df["start_date"] >= cutoff].copy()


def _apply_filters(match_df: pd.DataFrame, min_balls: int) -> pd.DataFrame:
    if match_df.empty:
        return _empty_like(match_df)
    return apply_match_filters(match_df, min_balls=min_balls)


def _comparison_rows(
    match_df: pd.DataFrame,
    home_team: str,
    visitor_label: str,
    title: str,
    competitive_threshold: int,
) -> ComparisonReportRows:
    return cast(ComparisonReportRows, ReportBuilder._build_report_data(
        match_df,
        home_team,
        visitor_label,
        title,
        is_venue_mode=False,
        calculate_team_stats=lambda df, team_name, _is_home: calculate_team_metrics(
            df=df,
            team_name=team_name,
            competitive_threshold=competitive_threshold,
        ),
    ))


def _matrix_rows(
    match_df: pd.DataFrame,
    team_name: str,
    title: str,
    is_away: bool,
    min_balls: int,
) -> MatrixReportRows:
    return cast(MatrixReportRows, ReportBuilder._generate_matrix_report(
        matches=match_df,
        team_name=team_name,
        title=title,
        is_away=is_away,
        apply_smart_filters=lambda frame: _apply_filters(frame, min_balls),
        serialize_ui_records=SerializationService.serialize_ui_records,
    ))


def _normalize_opp_scope(opp_team: str) -> str:
    return opp_team if opp_team and str(opp_team).strip() and opp_team != "All" else "All"


def _country_scope(home_team: str, country_name: str | None) -> tuple[str, bool]:
    raw_country = str(country_name).strip() if country_name is not None else ""
    default_home_country = raw_country in ("", "All")
    return (home_team if default_home_country else raw_country, default_home_country)


def _country_matchup_mask(match_df: pd.DataFrame, home_team: str, opp_scope: str) -> pd.Series:
    if opp_scope == "All":
        return (match_df["team_bat_1"] == home_team) | (match_df["team_bat_2"] == home_team)
    return (
        ((match_df["team_bat_1"] == home_team) & (match_df["team_bat_2"] == opp_scope))
        | ((match_df["team_bat_1"] == opp_scope) & (match_df["team_bat_2"] == home_team))
    )


def _country_prefix_mask(match_df: pd.DataFrame, prefixes: list[str]) -> pd.Series:
    prefix_tuple = tuple(prefixes)
    mask = pd.Series(False, index=match_df.index)
    if "venue_id" in match_df.columns:
        mask = mask | match_df["venue_id"].fillna("").astype(str).str.upper().str.startswith(prefix_tuple)
    if "venue" in match_df.columns:
        venue_series = match_df["venue"].fillna("").astype(str).str.strip()
        mapped_ids = venue_series.map(VENUE_MAP)
        canonical_ids = venue_series.where(venue_series.isin(set(VENUE_MAP.values())), "")
        resolved_ids = mapped_ids.where(mapped_ids.notna(), canonical_ids).fillna("").astype(str).str.upper()
        mask = mask | resolved_ids.str.startswith(prefix_tuple)
    return mask


def _explicit_country_mask(match_df: pd.DataFrame, country_scope: str) -> pd.Series:
    venue_text = match_df["venue"].astype(str) if "venue" in match_df.columns else pd.Series("", index=match_df.index)
    venue_id_text = (
        match_df["venue_id"].astype(str) if "venue_id" in match_df.columns else pd.Series("", index=match_df.index)
    )
    return venue_text.str.contains(country_scope, case=False, na=False) | venue_id_text.str.contains(
        country_scope, case=False, na=False
    )


def _apply_country_scope(match_df: pd.DataFrame, country_scope: str, default_home_country: bool) -> pd.DataFrame:
    if not country_scope:
        return match_df.copy()
    prefixes = get_country_prefixes(country_scope)
    if prefixes:
        return match_df[_country_prefix_mask(match_df, prefixes)].copy()
    if default_home_country:
        return match_df.copy()
    return match_df[_explicit_country_mask(match_df, country_scope)].copy()


def calculate_global_h2h_payload(match_df: pd.DataFrame, context: GlobalH2HContext) -> ComparisonRowsPayload:
    window_df = _filter_year_window(match_df, context["reference_date"], context["years_back"])
    if window_df.empty:
        return {"rows": []}
    rivalry_mask = (
        ((window_df["team_bat_1"] == context["home_team"]) & (window_df["team_bat_2"] == context["opp_team"]))
        | ((window_df["team_bat_1"] == context["opp_team"]) & (window_df["team_bat_2"] == context["home_team"]))
    )
    rivalry_df = _apply_filters(window_df[rivalry_mask].copy(), context["min_balls_for_completed_innings"])
    if rivalry_df.empty:
        return {"rows": []}
    return {
        "rows": _comparison_rows(
            rivalry_df, context["home_team"], context["opp_team"], "GLOBAL_RIVALRY_REPORT",
            context["competitive_chase_threshold"],
        )
    }


def _normalize_structured_metric(value: str | int) -> str | int | None:
    return None if value == "-" else value


def _build_country_h2h_structured(
    clean_df: pd.DataFrame,
    home_team: str,
    visitor_label: str,
    context: CountryH2HContext,
) -> VenueMatchupReport:
    winners = clean_df["winner"].astype(str).str.lower().str.strip()
    home_clean = home_team.lower().strip()
    visitor_clean = visitor_label.lower().strip()
    home_wins_df = clean_df[winners == home_clean]
    visitor_wins_df = clean_df[winners == visitor_clean]
    tie_nr = int(winners.isin(["tie", "no result", "nan", "none"]).sum())
    matches = int(len(clean_df))
    decisions = matches - tie_nr
    win_pct = int(format(len(home_wins_df) / decisions, "%").split(".")[0]) if decisions > 0 else 0
    home_stats = calculate_team_metrics(clean_df, home_team, context["competitive_chase_threshold"])
    visitor_stats = calculate_team_metrics(clean_df, visitor_label, context["competitive_chase_threshold"])
    valid_2nd_mask = MatchFilterService.get_valid_matches_mask(clean_df)
    valid_1st_mask = valid_2nd_mask | MatchFilterService.get_excluded_short_second_mask(clean_df)
    valid_1st = clean_df[valid_1st_mask]
    valid_2nd = clean_df[valid_2nd_mask]
    winning_bat1_df = valid_1st[valid_1st["winner"] == valid_1st["team_bat_1"]]
    match_ids = ",".join(clean_df["match_id"].astype(str).unique().tolist()) if "match_id" in clean_df.columns else ""
    return {
        "summary": {
            "matches": matches,
            "win_pct": win_pct,
            "tie_nr": tie_nr,
            "last_5_home": "",
            "last_5_away": "",
        },
        "team_a": {
            "name": home_team,
            "stats": {
                "wins": int(len(home_wins_df)),
                "defended": int((home_wins_df["team_bat_1"] == home_team).sum()),
                "chased": int((home_wins_df["team_bat_2"] == home_team).sum()),
                "bat1": {
                    "avg": _normalize_structured_metric(home_stats["avg_1st"]),
                    "high": _normalize_structured_metric(home_stats["high_1st"]),
                    "low": _normalize_structured_metric(home_stats["low_1st"]),
                    "avg_win": _normalize_structured_metric(home_stats["avg_1st_win"]),
                    "low_def": _normalize_structured_metric(home_stats["low_defended"]),
                },
                "chase": {
                    "avg": _normalize_structured_metric(home_stats["avg_2nd"]),
                    "high": _normalize_structured_metric(home_stats["high_chased"]),
                    "succ": _normalize_structured_metric(home_stats["avg_succ"]),
                    "fail": _normalize_structured_metric(home_stats["avg_fail"]),
                },
                "team_color": TEAM_COLORS.get(home_team) or TEAM_COLORS.get("VISITOR_TEAM") or TEAM_COLORS.get("Visitors", "gray"),
                "team_tone": None,
                "low_sample_warnings": [],
                "highlight_flags": {},
                "derived_badges": [],
            },
        },
        "team_b": {
            "name": visitor_label,
            "stats": {
                "wins": int(len(visitor_wins_df)),
                "defended": int((visitor_wins_df["team_bat_1"] == visitor_label).sum()),
                "chased": int((visitor_wins_df["team_bat_2"] == visitor_label).sum()),
                "bat1": {
                    "avg": _normalize_structured_metric(visitor_stats["avg_1st"]),
                    "high": _normalize_structured_metric(visitor_stats["high_1st"]),
                    "low": _normalize_structured_metric(visitor_stats["low_1st"]),
                    "avg_win": _normalize_structured_metric(visitor_stats["avg_1st_win"]),
                    "low_def": _normalize_structured_metric(visitor_stats["low_defended"]),
                },
                "chase": {
                    "avg": _normalize_structured_metric(visitor_stats["avg_2nd"]),
                    "high": _normalize_structured_metric(visitor_stats["high_chased"]),
                    "succ": _normalize_structured_metric(visitor_stats["avg_succ"]),
                    "fail": _normalize_structured_metric(visitor_stats["avg_fail"]),
                },
                "team_color": TEAM_COLORS.get(visitor_label) or TEAM_COLORS.get("VISITOR_TEAM") or TEAM_COLORS.get("Visitors", "gray"),
                "team_tone": None,
                "low_sample_warnings": [],
                "highlight_flags": {},
                "derived_badges": [],
            },
        },
        "venue_avg": {
            "avg_1st": _normalize_structured_metric(ReportBuilder._get_avg_with_count(valid_1st, "score_inn1")),
            "avg_2nd": _normalize_structured_metric(ReportBuilder._get_avg_with_count(valid_2nd, "score_inn2")),
            "avg_win_score": _normalize_structured_metric(
                ReportBuilder._get_avg_with_count(winning_bat1_df, "score_inn1")
            ),
        },
        "MATCH_IDS": match_ids or None,
        "low_sample_warnings": [],
        "highlight_flags": {
            "has_low_sample_warnings": False,
            "has_form_guide": False,
        },
        "derived_badges": [],
    }


def _empty_structured_team_stats(team_name: str) -> dict[str, int | str | None | dict[str, str | int | None] | list[str] | dict[str, bool]]:
    team_color = TEAM_COLORS.get(team_name) or TEAM_COLORS.get("VISITOR_TEAM") or TEAM_COLORS.get("Visitors", "gray")
    return {
        "wins": 0,
        "defended": 0,
        "chased": 0,
        "bat1": {"avg": None, "high": None, "low": None, "avg_win": None, "low_def": None},
        "chase": {"avg": None, "high": None, "succ": None, "fail": None},
        "team_color": team_color,
        "team_tone": ReportFormatter._team_tone_from_color(team_color),
        "low_sample_warnings": [],
        "highlight_flags": {"has_low_sample_warnings": False},
        "derived_badges": [],
    }


def _form_guide_string(match_df: pd.DataFrame, team_name: str) -> str:
    form_guide = ReportFormatter._none_if_placeholder(
        ReportFormatter.format_form_guide(ReportBuilder._build_form_data_payload(match_df, team_name))
    )
    return str(form_guide) if form_guide is not None else ""


def _structured_low_sample_warnings(
    team_name: str,
    avg_bat_first: str | int | None,
    avg_bat_first_win: str | int | None,
    avg_chase: str | int | None,
    min_matches: int,
) -> list[str]:
    sample_sizes = [
        ReportFormatter._extract_sample_size(avg_bat_first),
        ReportFormatter._extract_sample_size(avg_bat_first_win),
        ReportFormatter._extract_sample_size(avg_chase),
    ]
    return ReportFormatter._format_low_sample_warnings(team_name, sample_sizes, min_matches)


def _build_structured_team_payload(
    clean_df: pd.DataFrame,
    team_name: str,
    competitive_chase_threshold: float,
    low_sample_min_matches: int,
) -> dict[str, int | str | None | dict[str, str | int | None] | list[str] | dict[str, bool]]:
    team_stats = calculate_team_metrics(clean_df, team_name, competitive_chase_threshold)
    team_wins_df = clean_df[clean_df["winner"] == team_name]
    team_color = TEAM_COLORS.get(team_name) or TEAM_COLORS.get("VISITOR_TEAM") or TEAM_COLORS.get("Visitors", "gray")
    payload = {
        "wins": int(len(team_wins_df)),
        "defended": int((team_wins_df["team_bat_1"] == team_name).sum()),
        "chased": int((team_wins_df["team_bat_2"] == team_name).sum()),
        "bat1": {
            "avg": _normalize_structured_metric(team_stats["avg_1st"]),
            "high": _normalize_structured_metric(team_stats["high_1st"]),
            "low": _normalize_structured_metric(team_stats["low_1st"]),
            "avg_win": _normalize_structured_metric(team_stats["avg_1st_win"]),
            "low_def": _normalize_structured_metric(team_stats["low_defended"]),
        },
        "chase": {
            "avg": _normalize_structured_metric(team_stats["avg_2nd"]),
            "high": _normalize_structured_metric(team_stats["high_chased"]),
            "succ": _normalize_structured_metric(team_stats["avg_succ"]),
            "fail": _normalize_structured_metric(team_stats["avg_fail"]),
        },
        "team_color": team_color,
        "team_tone": ReportFormatter._team_tone_from_color(team_color),
        "low_sample_warnings": [],
        "highlight_flags": {},
        "derived_badges": [],
    }
    low_sample_warnings = _structured_low_sample_warnings(
        team_name,
        payload["bat1"]["avg"],
        payload["bat1"]["avg_win"],
        payload["chase"]["avg"],
        low_sample_min_matches,
    )
    payload["low_sample_warnings"] = low_sample_warnings
    payload["highlight_flags"] = {"has_low_sample_warnings": bool(low_sample_warnings)}
    return payload


def _build_global_h2h_structured(
    clean_df: pd.DataFrame,
    home_team: str,
    opp_team: str,
    competitive_chase_threshold: float,
    low_sample_min_matches: int,
    percent_scale: float,
) -> VenueMatchupReport:
    if clean_df.empty:
        return {
            "summary": {
                "matches": 0,
                "win_pct": 0,
                "tie_nr": 0,
                "last_5_home": "",
                "last_5_away": "",
            },
            "team_a": {"name": home_team, "stats": _empty_structured_team_stats(home_team)},
            "team_b": {"name": opp_team, "stats": _empty_structured_team_stats(opp_team)},
            "venue_avg": {"avg_1st": None, "avg_2nd": None, "avg_win_score": None},
            "MATCH_IDS": None,
            "low_sample_warnings": [],
            "highlight_flags": {"has_low_sample_warnings": False, "has_form_guide": False},
            "derived_badges": [],
        }
    winners = clean_df["winner"].astype(str).str.lower().str.strip()
    home_clean = home_team.lower().strip()
    tie_nr = int(winners.isin(["tie", "no result", "nan", "none"]).sum())
    matches = int(len(clean_df))
    decisions = matches - tie_nr
    home_wins_df = clean_df[winners == home_clean]
    valid_2nd_mask = MatchFilterService.get_valid_matches_mask(clean_df)
    valid_1st_mask = valid_2nd_mask | MatchFilterService.get_excluded_short_second_mask(clean_df)
    valid_1st = clean_df[valid_1st_mask]
    valid_2nd = clean_df[valid_2nd_mask]
    winning_bat1_df = valid_1st[valid_1st["winner"] == valid_1st["team_bat_1"]]
    team_a_stats = _build_structured_team_payload(
        clean_df,
        home_team,
        competitive_chase_threshold,
        low_sample_min_matches,
    )
    team_b_stats = _build_structured_team_payload(
        clean_df,
        opp_team,
        competitive_chase_threshold,
        low_sample_min_matches,
    )
    last_5_home = _form_guide_string(clean_df, home_team)
    last_5_away = _form_guide_string(clean_df, opp_team)
    low_sample_warnings = [*team_a_stats["low_sample_warnings"], *team_b_stats["low_sample_warnings"]]
    win_pct = int(round((len(home_wins_df) * percent_scale) / decisions)) if decisions > 0 else 0
    match_ids = ",".join(clean_df["match_id"].astype(str).unique().tolist()) if "match_id" in clean_df.columns else ""
    return {
        "summary": {
            "matches": matches,
            "win_pct": win_pct,
            "tie_nr": tie_nr,
            "last_5_home": last_5_home,
            "last_5_away": last_5_away,
        },
        "team_a": {"name": home_team, "stats": team_a_stats},
        "team_b": {"name": opp_team, "stats": team_b_stats},
        "venue_avg": {
            "avg_1st": _normalize_structured_metric(ReportBuilder._get_avg_with_count(valid_1st, "score_inn1")),
            "avg_2nd": _normalize_structured_metric(ReportBuilder._get_avg_with_count(valid_2nd, "score_inn2")),
            "avg_win_score": _normalize_structured_metric(
                ReportBuilder._get_avg_with_count(winning_bat1_df, "score_inn1")
            ),
        },
        "MATCH_IDS": match_ids or None,
        "low_sample_warnings": low_sample_warnings,
        "highlight_flags": {
            "has_low_sample_warnings": bool(low_sample_warnings),
            "has_form_guide": bool(last_5_home or last_5_away),
        },
        "derived_badges": [],
    }


def calculate_country_h2h_payload(match_df: pd.DataFrame, context: CountryH2HContext) -> VenueMatchupPayload:
    window_df = _filter_year_window(match_df, context["reference_date"], context["years_back"])
    if window_df.empty:
        return {"payload": {}}
    opp_scope = _normalize_opp_scope(context["opp_team"])
    if opp_scope == "All":
        return {"payload": {}}
    country_scope, default_home_country = _country_scope(context["home_team"], context["country_name"])
    masked_df = window_df[_country_matchup_mask(window_df, context["home_team"], opp_scope)].copy()
    if masked_df.empty:
        return {"payload": {}}
    country_df = _apply_country_scope(masked_df, country_scope, default_home_country)
    clean_df = _apply_filters(country_df, context["min_balls_for_completed_innings"])
    if clean_df.empty:
        return {"payload": {}}
    visitor_label = opp_scope
    return {
        "payload": _build_country_h2h_structured(
            clean_df,
            context["home_team"],
            visitor_label,
            context,
        )
    }


def calculate_global_h2h_structured_payload(
    match_df: pd.DataFrame,
    context: GlobalH2HContext,
) -> GlobalH2HStructuredPayload:
    window_df = _filter_year_window(match_df, context["reference_date"], context["years_back"])
    if window_df.empty:
        return {"payload": {}}
    rivalry_mask = (
        ((window_df["team_bat_1"] == context["home_team"]) & (window_df["team_bat_2"] == context["opp_team"]))
        | ((window_df["team_bat_1"] == context["opp_team"]) & (window_df["team_bat_2"] == context["home_team"]))
    )
    rivalry_df = window_df[rivalry_mask].copy()
    if rivalry_df.empty:
        return {"payload": {}}
    clean_df = _apply_filters(rivalry_df, context["min_balls_for_completed_innings"])
    if clean_df.empty:
        return {"payload": {}}
    return {
        "payload": _build_global_h2h_structured(
            clean_df,
            context["home_team"],
            context["opp_team"],
            context["competitive_chase_threshold"],
            context["low_sample_min_matches"],
            context["percent_scale"],
        )
    }


def calculate_home_dominance_payload(match_df: pd.DataFrame, context: HomeDominanceContext) -> MatrixRowsPayload:
    prefix = context["region"].get(context["home_team"])
    if not prefix:
        return {"rows": []}
    window_df = _filter_year_window(match_df, context["reference_date"], context["years_back"])
    if window_df.empty:
        return {"rows": []}
    venue_col = "venue_id" if "venue_id" in window_df.columns else "venue"
    team_mask = (window_df["team_bat_1"] == context["home_team"]) | (window_df["team_bat_2"] == context["home_team"])
    match_df_home = window_df[team_mask & window_df[venue_col].astype(str).str.startswith(prefix)].copy()
    return {"rows": _matrix_rows(match_df_home, context["home_team"], "DOMINANCE_MATRIX", False, context["min_balls_for_completed_innings"])} if not match_df_home.empty else {"rows": []}


def calculate_away_performance_payload(match_df: pd.DataFrame, context: AwayPerformanceContext) -> MatrixRowsPayload:
    prefix = context["region"].get(context["team_name"])
    if not prefix:
        return {"rows": []}
    window_df = _filter_year_window(match_df, context["reference_date"], context["years_back"])
    if window_df.empty:
        return {"rows": []}
    venue_col = "venue_id" if "venue_id" in window_df.columns else "venue"
    team_mask = (window_df["team_bat_1"] == context["team_name"]) | (window_df["team_bat_2"] == context["team_name"])
    away_df = window_df[team_mask & (~window_df[venue_col].astype(str).str.startswith(prefix))].copy()
    return {"rows": _matrix_rows(away_df, context["team_name"], "AWAY_PERFORMANCE_MATRIX", True, context["min_balls_for_completed_innings"])} if not away_df.empty else {"rows": []}


def calculate_global_performance_payload(match_df: pd.DataFrame, context: GlobalPerformanceContext) -> MatrixRowsPayload:
    window_df = _filter_year_window(match_df, context["reference_date"], context["years_back"])
    if window_df.empty:
        return {"rows": []}
    team_mask = (window_df["team_bat_1"] == context["team_name"]) | (window_df["team_bat_2"] == context["team_name"])
    global_df = window_df[team_mask].copy()
    return {"rows": _matrix_rows(global_df, context["team_name"], "GLOBAL_PERFORMANCE_MATRIX", False, context["min_balls_for_completed_innings"])} if not global_df.empty else {"rows": []}


def calculate_continent_performance_payload(
    match_df: pd.DataFrame,
    context: ContinentPerformanceContext,
) -> ContinentRowsPayload:
    window_df = _filter_year_window(match_df, context["reference_date"], context["years_back"])
    if window_df.empty:
        return {"rows": []}
    opp_scope = _normalize_opp_scope(context["opp_team"])
    mask = (window_df["team_bat_1"] == context["team_name"]) | (window_df["team_bat_2"] == context["team_name"])
    if context["continent"] != "All":
        mask = mask & VenueService._build_continent_mask(window_df, context["continent"])
    if opp_scope != "All":
        mask = mask & ((window_df["team_bat_1"] == opp_scope) | (window_df["team_bat_2"] == opp_scope))
    scoped_df = window_df[mask].copy()
    if scoped_df.empty:
        return {"rows": []}
    if opp_scope != "All":
        clean_df = _apply_filters(scoped_df, context["min_balls_for_completed_innings"])
        if clean_df.empty:
            return {"rows": []}
        rows = _comparison_rows(clean_df, context["team_name"], opp_scope, "REGIONAL_RIVALRY_REPORT", context["competitive_chase_threshold"])
        return {"rows": rows}
    return {"rows": _matrix_rows(scoped_df, context["team_name"], "REGIONAL_PERFORMANCE_MATRIX", False, context["min_balls_for_completed_innings"])}


def calculate_team_form_payload(match_df: pd.DataFrame, context: TeamFormContext) -> TeamFormRowsPayload:
    if match_df.empty:
        return {"rows": []}
    mask = (match_df["team_bat_1"] == context["team_name"]) | (match_df["team_bat_2"] == context["team_name"])
    if context["opp_team"] != "All":
        mask = mask & ((match_df["team_bat_1"] == context["opp_team"]) | (match_df["team_bat_2"] == context["opp_team"]))
    if context["continent"] != "All":
        mask = mask & VenueService._build_continent_mask(match_df, context["continent"])
    scoped_df = match_df[mask].copy()
    clean_df = _apply_filters(scoped_df, context["min_balls_for_completed_innings"])
    if clean_df.empty:
        return {"rows": []}
    recent_df = clean_df.sort_values("start_date", ascending=False).head(context["limit"])
    return {"rows": cast(TeamFormRows, ReportBuilder._build_team_form_records(recent_df, context["team_name"]))}
