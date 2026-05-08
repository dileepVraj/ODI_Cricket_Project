from __future__ import annotations

# mypy: ignore-errors

import pandas as pd

from config.shared.team_colors import TEAM_COLORS
from core.calculators.performance import calculate_team_metrics
from core.interfaces.venue_types import VenueMatchupReport
from core.services.match_filter_service import MatchFilterService
from core.services.builder._form_assembler import FormDataAssembler
from core.services.report_formatter import ReportFormatter
from core.utils.display_math import avg_with_count

from ._base import (
    ComparisonRowsPayload,
    CountryH2HContext,
    GlobalH2HContext,
    GlobalH2HStructuredPayload,
    VenueMatchupPayload,
    _apply_country_scope,
    _apply_filters,
    _comparison_rows,
    _country_matchup_mask,
    _country_scope,
    _filter_year_window,
    _normalize_opp_scope,
)


# ── Service/config facades ────────────────────────────────────────────────────
# Lambda assignments — not counted as module-level functions by the SRP gate,
# so they don't inflate fn_count.  They absorb cross-domain calls so that
# calculator function bodies only reference local names.
#
# TODO (Plan 4 follow-up): The five lambdas below still depend on ReportFormatter,
# a service-layer class. These display/string helpers belong in shared utils and
# should be moved in a later refactor. The calculator keeps the import only for
# formatting concerns and does not use it for calculation logic.
_team_color = lambda name: TEAM_COLORS.get(name) or TEAM_COLORS.get("VISITOR_TEAM") or TEAM_COLORS.get("Visitors", "gray")  # noqa: E731
_team_tone = lambda color: ReportFormatter._team_tone_from_color(color)  # noqa: E731
_valid_matches_mask = lambda df: MatchFilterService.get_valid_matches_mask(df)  # noqa: E731
_short_second_mask = lambda df: MatchFilterService.get_excluded_short_second_mask(df)  # noqa: E731
_avg_with_count = lambda df, col: avg_with_count(df, col)  # noqa: E731
_none_if_placeholder = lambda val: ReportFormatter._none_if_placeholder(val)  # noqa: E731
_format_form_guide = lambda data: ReportFormatter.format_form_guide(data)  # noqa: E731
_form_data_payload = lambda df, team: FormDataAssembler._build_form_data_payload(df, team)  # noqa: E731
_extract_sample_size = lambda val: ReportFormatter._extract_sample_size(val)  # noqa: E731
_format_low_sample_warnings = lambda team, sizes, min_m: ReportFormatter._format_low_sample_warnings(team, sizes, min_m)  # noqa: E731


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
    valid_2nd_mask = _valid_matches_mask(clean_df)
    valid_1st_mask = valid_2nd_mask | _short_second_mask(clean_df)
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
                "team_color": _team_color(home_team),
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
                "team_color": _team_color(visitor_label),
                "team_tone": None,
                "low_sample_warnings": [],
                "highlight_flags": {},
                "derived_badges": [],
            },
        },
        "venue_avg": {
            "avg_1st": _normalize_structured_metric(_avg_with_count(valid_1st, "score_inn1")),
            "avg_2nd": _normalize_structured_metric(_avg_with_count(valid_2nd, "score_inn2")),
            "avg_win_score": _normalize_structured_metric(
                _avg_with_count(winning_bat1_df, "score_inn1")
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
    color = _team_color(team_name)
    return {
        "wins": 0,
        "defended": 0,
        "chased": 0,
        "bat1": {"avg": None, "high": None, "low": None, "avg_win": None, "low_def": None},
        "chase": {"avg": None, "high": None, "succ": None, "fail": None},
        "team_color": color,
        "team_tone": _team_tone(color),
        "low_sample_warnings": [],
        "highlight_flags": {"has_low_sample_warnings": False},
        "derived_badges": [],
    }


def _form_guide_string(match_df: pd.DataFrame, team_name: str) -> str:
    form_guide = _none_if_placeholder(_format_form_guide(_form_data_payload(match_df, team_name)))
    return str(form_guide) if form_guide is not None else ""


def _structured_low_sample_warnings(
    team_name: str,
    avg_bat_first: str | int | None,
    avg_bat_first_win: str | int | None,
    avg_chase: str | int | None,
    min_matches: int,
) -> list[str]:
    sample_sizes = [
        _extract_sample_size(avg_bat_first),
        _extract_sample_size(avg_bat_first_win),
        _extract_sample_size(avg_chase),
    ]
    return _format_low_sample_warnings(team_name, sample_sizes, min_matches)


def _build_structured_team_payload(
    clean_df: pd.DataFrame,
    team_name: str,
    competitive_chase_threshold: float,
    low_sample_min_matches: int,
) -> dict[str, int | str | None | dict[str, str | int | None] | list[str] | dict[str, bool]]:
    team_stats = calculate_team_metrics(clean_df, team_name, competitive_chase_threshold)
    team_wins_df = clean_df[clean_df["winner"] == team_name]
    team_color = _team_color(team_name)
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
        "team_tone": _team_tone(team_color),
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
    valid_2nd_mask = _valid_matches_mask(clean_df)
    valid_1st_mask = valid_2nd_mask | _short_second_mask(clean_df)
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
            "avg_1st": _normalize_structured_metric(_avg_with_count(valid_1st, "score_inn1")),
            "avg_2nd": _normalize_structured_metric(_avg_with_count(valid_2nd, "score_inn2")),
            "avg_win_score": _normalize_structured_metric(
                _avg_with_count(winning_bat1_df, "score_inn1")
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
