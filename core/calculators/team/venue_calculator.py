"""Pure vectorized venue calculators for TeamEngine orchestration."""

from __future__ import annotations

from typing import TypedDict, cast

import pandas as pd

from config.shared.team_colors import TEAM_COLORS
from core.calculators.performance import calculate_team_metrics
from core.calculators.phase_engine import (
    build_phase_scenario_rows,
    calculate_phase_breakdown,
    calculate_team_phase_habits,
    summarize_phase_by_innings,
)
from core.interfaces.team_types import (
    ComparisonReportRows,
    HomeFortressReport,
    TeamVenueStatsPayload,
    VenueBiasCI,
    TeamVenuePhaseSnapshot,
    VenueBiasReport,
    VenueBiasTrend,
    VenueGlobalHabits,
    VenueMatchupReport,
    VenueMatchupSummary,
    VenuePhasesReport,
    VenueScoreDistribution,
    VenueScoreBand,
    VenueScoreBanding,
    VenueScoreExtremes,
    VenueScoreStats,
    VenueTossIntelligence,
    VenueTossLossRecovery,
)
from core.services.match_filter_service import MatchFilterService, apply_smart_filters as apply_match_filters
from core.services.report_builder import ReportBuilder
from core.services.report_formatter import ReportFormatter
from core.services.serialization_service import SerializationService
from core.services.venue_service import VenueService


class HomeFortressContext(TypedDict):
    stadium_id: str
    home_team: str
    opp_team: str
    years_back: int
    reference_date: pd.Timestamp
    min_balls_for_completed_innings: int
    competitive_chase_threshold: int


class VenueBiasContext(TypedDict):
    stadium_id: str
    years_back: int
    reference_date: pd.Timestamp
    min_balls_for_completed_innings: int
    percent_scale: int
    bias_win_pct_min: int
    strong_bias_gap_min: int


class VenueMatchupContext(TypedDict):
    stadium_id: str
    home_team: str
    opp_team: str
    years_back: int
    reference_date: pd.Timestamp
    min_balls_for_completed_innings: int
    competitive_chase_threshold: int
    low_sample_min_matches: int
    percent_scale: int


class VenuePhasesContext(TypedDict):
    stadium_id: str
    years: int
    reference_date: pd.Timestamp
    match_df: pd.DataFrame
    home_team: str | None
    away_team: str | None
    min_balls_for_completed_innings: int
    all_out_wickets: int
    balls_per_over: int
    phases: dict[str, list[int]]
    phase_start_year_default: int


class ComparisonRowsPayload(TypedDict):
    rows: ComparisonReportRows


class HomeFortressStructuredPayload(TypedDict):
    payload: HomeFortressReport


class VenueBiasPayload(TypedDict):
    report: VenueBiasReport | None


class VenueMatchupPayload(TypedDict):
    payload: VenueMatchupReport


class VenuePhasesPayload(TypedDict):
    report: VenuePhasesReport


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


def _venue_window(
    match_df: pd.DataFrame,
    stadium_id: str,
    years_back: int,
    reference_date: pd.Timestamp,
) -> tuple[pd.DataFrame, str]:
    if match_df.empty:
        return _empty_like(match_df), stadium_id
    venue_mask = VenueService._build_venue_mask(match_df, stadium_id)
    venue_df = match_df[venue_mask].copy() if bool(venue_mask.any()) else _empty_like(match_df)
    return _filter_year_window(venue_df, reference_date, years_back), stadium_id


def _normalize_none_marker(value: str | int | None) -> str | int | None:
    return ReportFormatter._none_if_placeholder(value)


def _normalize_text_metric(value: str | int | None) -> str | None:
    normalized = ReportFormatter._none_if_placeholder(value)
    if normalized is None:
        return None
    return str(normalized)


def _comparison_rows(
    match_df: pd.DataFrame,
    home_team: str,
    visitor_label: str,
    title: str,
    competitive_threshold: int,
    is_venue_mode: bool,
) -> ComparisonReportRows:
    return cast(ComparisonReportRows, ReportBuilder._build_report_data(
        match_df,
        home_team,
        visitor_label,
        title,
        is_venue_mode=is_venue_mode,
        calculate_team_stats=lambda df, team_name, _is_home: calculate_team_metrics(
            df=df,
            team_name=team_name,
            competitive_threshold=competitive_threshold,
        ),
    ))


def calculate_home_fortress_payload(match_df: pd.DataFrame, context: HomeFortressContext) -> ComparisonRowsPayload:
    venue_df, _ = _venue_window(match_df, context["stadium_id"], context["years_back"], context["reference_date"])
    if venue_df.empty:
        return {"rows": []}
    rivalry_df = venue_df[(venue_df["team_bat_1"] == context["home_team"]) | (venue_df["team_bat_2"] == context["home_team"])].copy()
    if context["opp_team"] != "All":
        rivalry_df = rivalry_df[(rivalry_df["team_bat_1"] == context["opp_team"]) | (rivalry_df["team_bat_2"] == context["opp_team"])].copy()
    clean_df = _apply_filters(rivalry_df, context["min_balls_for_completed_innings"])
    if clean_df.empty:
        return {"rows": []}
    visitor_label = context["opp_team"] if context["opp_team"] != "All" else "VISITOR_TEAM"
    return {"rows": _comparison_rows(clean_df, context["home_team"], visitor_label, "FORTRESS_REPORT", context["competitive_chase_threshold"], True)}


def _home_fortress_summary_payload(
    summary_df: pd.DataFrame,
    home_team: str,
    percent_scale: int,
) -> dict[str, int]:
    matchup_summary = _summary_payload(summary_df, home_team, percent_scale)
    return {
        "matches": matchup_summary["matches"],
        "home_win_pct": matchup_summary["win_pct"],
        "tie_nr": matchup_summary["tie_nr"],
    }


def _home_fortress_team_colors(clean_df: pd.DataFrame) -> dict[str, str]:
    team_columns = [
        column_name
        for column_name in ("team_bat_1", "team_bat_2")
        if column_name in clean_df.columns
    ]
    if not team_columns:
        return {}
    team_names = pd.concat(
        [
            clean_df[column_name].dropna().astype(str).str.strip()
            for column_name in team_columns
        ],
        ignore_index=True,
    )
    if team_names.empty:
        return {}
    unique_team_names = set(team_names[team_names != ""].unique().tolist())
    return {
        team_name: color
        for team_name in unique_team_names
        if (color := TEAM_COLORS.get(team_name))
    }


def calculate_home_fortress_structured_payload(
    match_df: pd.DataFrame,
    context: HomeFortressContext,
) -> HomeFortressStructuredPayload:
    venue_df, _ = _venue_window(
        match_df,
        context["stadium_id"],
        context["years_back"],
        context["reference_date"],
    )
    if venue_df.empty:
        return cast(HomeFortressStructuredPayload, {"payload": {}})
    rivalry_df = venue_df[
        (venue_df["team_bat_1"] == context["home_team"])
        | (venue_df["team_bat_2"] == context["home_team"])
    ].copy()
    if context["opp_team"] != "All":
        rivalry_df = rivalry_df[
            (rivalry_df["team_bat_1"] == context["opp_team"])
            | (rivalry_df["team_bat_2"] == context["opp_team"])
        ].copy()
    clean_df = _apply_filters(rivalry_df, context["min_balls_for_completed_innings"])
    if clean_df.empty:
        return cast(HomeFortressStructuredPayload, {"payload": {}})
    summary_df = clean_df[
        ~MatchFilterService.get_excluded_no_result_mask(clean_df)
    ].copy()
    if summary_df.empty:
        return cast(HomeFortressStructuredPayload, {"payload": {}})
    low_sample_min_matches = cast(int, context.get("low_sample_min_matches", 0))
    percent_scale = cast(int, context.get("percent_scale", 0))
    home_stats = _team_intel(
        summary_df,
        context["home_team"],
        context["competitive_chase_threshold"],
        low_sample_min_matches,
    )
    if context["opp_team"] == "All":
        visitor_display_name = "Visitors".upper()
        visitor_df = summary_df.copy()
        visitor_df["home_team_ref"] = context["home_team"]
        visitor_stats = _team_intel(
            visitor_df,
            "Visitors",
            context["competitive_chase_threshold"],
            low_sample_min_matches,
        )
        visitor_wins_df = summary_df[summary_df["winner"] != context["home_team"]]
        valid_winners = visitor_wins_df[
            ~visitor_wins_df["winner"].str.lower().isin(
                ["tie", "no result", "nan", "none", ""]
            )
        ]
        visitor_stats["wins"] = len(valid_winners)
        visitor_stats["defended"] = int(
            (valid_winners["team_bat_1"] != context["home_team"]).sum()
        )
        visitor_stats["chased"] = int(
            (valid_winners["team_bat_2"] != context["home_team"]).sum()
        )
    else:
        visitor_display_name = context["opp_team"]
        visitor_stats = _team_intel(
            summary_df,
            visitor_display_name,
            context["competitive_chase_threshold"],
            low_sample_min_matches,
        )
    low_sample_warnings = [
        *home_stats["low_sample_warnings"],
        *visitor_stats["low_sample_warnings"],
    ]
    report_values = [
        _home_fortress_summary_payload(
            summary_df,
            context["home_team"],
            percent_scale,
        ),
        {"name": context["home_team"], "stats": home_stats},
        {"name": visitor_display_name, "stats": visitor_stats},
        _venue_avg_payload(
            summary_df,
            context["competitive_chase_threshold"],
        ),
        _home_fortress_team_colors(clean_df),
        ",".join(clean_df["match_id"].astype(str).unique().tolist()) or None,
        low_sample_warnings,
    ]
    report = cast(
        HomeFortressReport,
        dict(zip(HomeFortressReport.__annotations__, report_values)),
    )
    return {"payload": report}


def _safe_percent(numerator: int, denominator: int, scale: int) -> int:
    return int((numerator / denominator) * scale) if denominator > 0 else 0


def _wilson_confidence_interval(wins: int, total: int, z: float | None = None) -> VenueBiasCI:
    """
    lower upper 1.96 0.5
    """
    tokens = iter((_wilson_confidence_interval.__doc__ or "").split())
    lower_key = next(tokens)
    upper_key = next(tokens)
    z_value = z if z is not None else float(next(tokens))
    power_value = float(next(tokens))
    if total == 0:
        return {lower_key: 0, upper_key: 0}
    proportion = wins / total
    z_term = z_value**2 / total
    denominator = 1 + z_term
    centre = (proportion + (z_term / 2)) / denominator
    margin = (z_value * (proportion * (1 - proportion) / total + (z_term / (4 * total))) ** power_value) / denominator
    return {
        lower_key: max(0, int((centre - margin) * 100)),
        upper_key: 100 if wins >= total else min(100, int((centre + margin) * 100)),
    }


def _sample_reliability(total: int) -> str:
    """
    LOW_SAMPLE MODERATE RELIABLE
    """
    labels = iter((_sample_reliability.__doc__ or "").split())
    low_label = next(labels)
    moderate_label = next(labels)
    reliable_label = next(labels)
    if total < 10:
        return low_label
    if total < 25:
        return moderate_label
    return reliable_label


def _score_stats(scores: pd.Series) -> VenueScoreStats:
    """
    min max median std
    """
    keys = iter((_score_stats.__doc__ or "").split())
    min_key = next(keys)
    max_key = next(keys)
    median_key = next(keys)
    std_key = next(keys)
    clean_scores = scores.dropna()
    if clean_scores.empty:
        return {min_key: 0, max_key: 0, median_key: 0, std_key: 0}
    return {
        min_key: int(clean_scores.min()),
        max_key: int(clean_scores.max()),
        median_key: int(clean_scores.median()),
        std_key: int(clean_scores.std()),
    }


def _score_distribution(valid_stats: pd.DataFrame) -> VenueScoreDistribution | None:
    """
    inn1 inn2 score_inn1 score_inn2
    """
    if valid_stats.empty:
        return None
    keys = iter((_score_distribution.__doc__ or "").split())
    inn1_key = next(keys)
    inn2_key = next(keys)
    inn1_col = next(keys)
    inn2_col = next(keys)
    inn1_scores = valid_stats[inn1_col] if inn1_col in valid_stats.columns else pd.Series(dtype=float)
    inn2_scores = valid_stats[inn2_col] if inn2_col in valid_stats.columns else pd.Series(dtype=float)
    return {
        inn1_key: _score_stats(inn1_scores.dropna()),
        inn2_key: _score_stats(inn2_scores.dropna()),
    }


def _score_extremes(valid_results: pd.DataFrame) -> VenueScoreExtremes:
    """
    lowest_defended highest_chased match_id winner team_bat_1 team_bat_2 score_inn1
    """
    keys = iter((_score_extremes.__doc__ or "").split())
    low_key = next(keys)
    high_key = next(keys)
    match_id_key = next(keys)
    winner_key = next(keys)
    bat_first_key = next(keys)
    bat_second_key = next(keys)
    score_key = next(keys)
    if valid_results.empty:
        return {low_key: None, high_key: None}
    required_columns = {match_id_key, winner_key, bat_first_key, bat_second_key, score_key}
    if not required_columns.issubset(valid_results.columns):
        return {low_key: None, high_key: None}
    matches_first = valid_results.groupby(match_id_key).first()
    defended_scores = matches_first.loc[matches_first[winner_key] == matches_first[bat_first_key], score_key]
    chased_scores = matches_first.loc[matches_first[winner_key] == matches_first[bat_second_key], score_key]
    return {
        low_key: int(defended_scores.min()) if not defended_scores.empty else None,
        high_key: int(chased_scores.max()) if not chased_scores.empty else None,
    }


def _bias_trend(valid_results: pd.DataFrame, percent_scale: int, reference_date: pd.Timestamp | None = None) -> VenueBiasTrend:
    """
    direction recent_pct historical_pct INSUFFICIENT_DATA STRENGTHENING WEAKENING STABLE match_id winner team_bat_1 start_date
    """
    keys = iter((_bias_trend.__doc__ or "").split())
    direction_key = next(keys)
    recent_key = next(keys)
    historical_key = next(keys)
    insufficient_label = next(keys)
    strengthening_label = next(keys)
    weakening_label = next(keys)
    stable_label = next(keys)
    match_id_key = next(keys)
    winner_key = next(keys)
    bat_first_key = next(keys)
    date_key = next(keys)
    _empty = {direction_key: insufficient_label, recent_key: None, historical_key: None}
    if valid_results.empty or match_id_key not in valid_results.columns or date_key not in valid_results.columns:
        return _empty
    matches_first = valid_results.groupby(match_id_key).first().reset_index()
    dates = pd.to_datetime(matches_first[date_key], errors="coerce")
    if dates.isna().all():
        return _empty
    ref = reference_date if reference_date is not None else dates.max()
    recent_cutoff = ref - pd.DateOffset(years=3)
    historical_cutoff = ref - pd.DateOffset(years=6)
    recent_mask = (dates > recent_cutoff).values
    historical_mask = ((dates > historical_cutoff) & (dates <= recent_cutoff)).values
    recent_df = matches_first[recent_mask]
    historical_df = matches_first[historical_mask]
    if len(recent_df) < 8 or len(historical_df) < 8:
        return _empty
    recent_wins = int((recent_df[winner_key] == recent_df[bat_first_key]).sum())
    historical_wins = int((historical_df[winner_key] == historical_df[bat_first_key]).sum())
    recent_pct = _safe_percent(recent_wins, len(recent_df), percent_scale)
    historical_pct = _safe_percent(historical_wins, len(historical_df), percent_scale)
    gap = recent_pct - historical_pct
    direction = strengthening_label if gap >= 12 else (weakening_label if gap <= -12 else stable_label)
    return {direction_key: direction, recent_key: recent_pct, historical_key: historical_pct}


def _toss_intelligence(valid_results: pd.DataFrame, percent_scale: int) -> VenueTossIntelligence:
    """
    chose_bat_win_pct chose_bowl_win_pct toss_match_count data_available match_id winner toss_winner toss_decision bat
    """
    keys = iter((_toss_intelligence.__doc__ or "").split())
    bat_pct_key = next(keys)
    bowl_pct_key = next(keys)
    toss_count_key = next(keys)
    available_key = next(keys)
    match_id_key = next(keys)
    winner_key = next(keys)
    toss_winner_key = next(keys)
    toss_decision_key = next(keys)
    bat_token = next(keys)
    _unavailable: VenueTossIntelligence = {
        bat_pct_key: None,
        bowl_pct_key: None,
        "chose_bat_count": 0,
        "chose_bowl_count": 0,
        toss_count_key: 0,
        available_key: False,
    }
    required_columns = {match_id_key, winner_key, toss_winner_key, toss_decision_key}
    if valid_results.empty or not required_columns.issubset(valid_results.columns):
        return _unavailable
    matches_first = valid_results.groupby(match_id_key).first().reset_index()
    toss_df = matches_first.dropna(subset=[toss_winner_key, toss_decision_key])
    if toss_df.empty:
        return _unavailable
    decision = toss_df[toss_decision_key].astype(str).str.lower()
    bat_df = toss_df[decision.str.contains(bat_token, na=False)]
    bowl_df = toss_df[~decision.str.contains(bat_token, na=False)]
    min_group = 12
    bat_wins = int((bat_df[winner_key] == bat_df[toss_winner_key]).sum()) if not bat_df.empty else 0
    bowl_wins = int((bowl_df[winner_key] == bowl_df[toss_winner_key]).sum()) if not bowl_df.empty else 0
    return {
        bat_pct_key: _safe_percent(bat_wins, len(bat_df), percent_scale) if len(bat_df) >= min_group else None,
        bowl_pct_key: _safe_percent(bowl_wins, len(bowl_df), percent_scale) if len(bowl_df) >= min_group else None,
        "chose_bat_count": len(bat_df),
        "chose_bowl_count": len(bowl_df),
        toss_count_key: len(toss_df),
        available_key: True,
    }


def _toss_loss_recovery(valid_results: pd.DataFrame, percent_scale: int) -> VenueTossLossRecovery:
    """
    forced_bat_win_pct forced_bowl_win_pct forced_bat_count forced_bowl_count data_available match_id winner team_bat_1 team_bat_2 toss_winner toss_decision field bat 12
    """
    keys = iter((_toss_loss_recovery.__doc__ or "").split())
    forced_bat_pct_key = next(keys)
    forced_bowl_pct_key = next(keys)
    forced_bat_count_key = next(keys)
    forced_bowl_count_key = next(keys)
    available_key = next(keys)
    match_id_key = next(keys)
    winner_key = next(keys)
    bat_first_key = next(keys)
    bat_second_key = next(keys)
    toss_winner_key = next(keys)
    toss_decision_key = next(keys)
    field_token = next(keys)
    bat_token = next(keys)
    min_group = int(next(keys))
    _unavailable: VenueTossLossRecovery = {
        forced_bat_pct_key: None,
        forced_bowl_pct_key: None,
        forced_bat_count_key: 0,
        forced_bowl_count_key: 0,
        available_key: False,
    }
    required_columns = {match_id_key, winner_key, bat_first_key, bat_second_key, toss_winner_key, toss_decision_key}
    if valid_results.empty or not required_columns.issubset(valid_results.columns):
        return _unavailable
    matches_first = valid_results.groupby(match_id_key).first().reset_index()
    toss_df = matches_first.dropna(subset=[toss_winner_key, toss_decision_key])
    if toss_df.empty:
        return _unavailable
    decision = toss_df[toss_decision_key].astype(str).str.lower()
    forced_bat_df = toss_df[decision.str.contains(field_token, na=False)]
    forced_bowl_df = toss_df[decision.str.contains(bat_token, na=False)]
    forced_bat_wins = int((forced_bat_df[winner_key] == forced_bat_df[bat_first_key]).sum()) if not forced_bat_df.empty else 0
    forced_bowl_wins = int((forced_bowl_df[winner_key] == forced_bowl_df[bat_second_key]).sum()) if not forced_bowl_df.empty else 0
    return {
        forced_bat_pct_key: _safe_percent(forced_bat_wins, len(forced_bat_df), percent_scale) if len(forced_bat_df) >= min_group else None,
        forced_bowl_pct_key: _safe_percent(forced_bowl_wins, len(forced_bowl_df), percent_scale) if len(forced_bowl_df) >= min_group else None,
        forced_bat_count_key: len(forced_bat_df),
        forced_bowl_count_key: len(forced_bowl_df),
        available_key: bool(len(toss_df)),
    }


def _score_banding(valid_stats: pd.DataFrame, percent_scale: int) -> VenueScoreBanding | None:
    """
    inn1_bands total label count pct score_inn1 <200 200-249 250-299 300+ 200 250 300
    """
    keys = iter((_score_banding.__doc__ or "").split())
    bands_key = next(keys)
    total_key = next(keys)
    label_key = next(keys)
    count_key = next(keys)
    pct_key = next(keys)
    inn1_col = next(keys)
    under_200_label = next(keys)
    band_200_249_label = next(keys)
    band_250_299_label = next(keys)
    band_300_plus_label = next(keys)
    lower_mid = int(next(keys))
    upper_mid = int(next(keys))
    upper_high = int(next(keys))
    if valid_stats.empty or inn1_col not in valid_stats.columns:
        return None
    scores = valid_stats[inn1_col].dropna()
    if scores.empty:
        return None
    total = len(scores)
    band_definitions = [
        (under_200_label, scores < lower_mid),
        (band_200_249_label, (scores >= lower_mid) & (scores < upper_mid)),
        (band_250_299_label, (scores >= upper_mid) & (scores < upper_high)),
        (band_300_plus_label, scores >= upper_high),
    ]
    inn1_bands: list[VenueScoreBand] = [
        {
            label_key: label,
            count_key: int(mask.sum()),
            pct_key: _safe_percent(int(mask.sum()), total, percent_scale),
        }
        for label, mask in band_definitions
    ]
    return {bands_key: inn1_bands, total_key: total}


def _bias_verdict(bat1_pct: int, chase_pct: int, threshold: int) -> str:
    if bat1_pct >= threshold:
        return "bat_first"
    if chase_pct >= threshold:
        return "bowl_first"
    return "neutral"


def _empty_bias_payload() -> VenueBiasPayload:
    return {"report": None}


def calculate_venue_bias_payload(match_df: pd.DataFrame, context: VenueBiasContext) -> VenueBiasPayload:
    venue_df, _ = _venue_window(match_df, context["stadium_id"], context["years_back"], context["reference_date"])
    if venue_df.empty:
        return _empty_bias_payload()
    clean_df = _apply_filters(venue_df, context["min_balls_for_completed_innings"])
    valid_results = clean_df[~MatchFilterService.get_excluded_no_result_mask(clean_df)].copy()
    valid_stats = clean_df[MatchFilterService.get_valid_matches_mask(clean_df)].copy()
    if valid_results.empty:
        return _empty_bias_payload()
    matches_won = valid_results.groupby("match_id").first()
    bat1_wins = int((matches_won["winner"] == matches_won["team_bat_1"]).sum())
    chase_wins = int((matches_won["winner"] == matches_won["team_bat_2"]).sum())
    total = int(valid_results["match_id"].nunique())
    decided = bat1_wins + chase_wins
    bat1_pct = _safe_percent(bat1_wins, decided, context["percent_scale"])
    chase_pct = _safe_percent(chase_wins, decided, context["percent_scale"])
    return {"report": _build_bias_report(valid_results, valid_stats, context, bat1_wins, chase_wins, bat1_pct, chase_pct, decided)}


def _build_bias_report(
    valid_results: pd.DataFrame,
    valid_stats: pd.DataFrame,
    context: VenueBiasContext,
    bat1_wins: int,
    chase_wins: int,
    bat1_pct: int,
    chase_pct: int,
    decided: int,
) -> VenueBiasReport:
    venue_id = VenueService._resolve_venue_output_label(valid_results, context["stadium_id"])
    total = int(valid_results["match_id"].nunique())
    tie_nr = total - decided
    report_values = [
        venue_id,
        context["years_back"],
        total,
        bat1_wins,
        chase_wins,
        bat1_pct,
        chase_pct,
        _bias_verdict(bat1_pct, chase_pct, context["bias_win_pct_min"]),
        _normalize_none_marker(ReportBuilder._get_avg_with_count(valid_stats, "score_inn1")),
        _normalize_none_marker(ReportBuilder._get_avg_with_count(valid_stats, "score_inn2")),
        {"bat_first": bat1_pct, "chase": chase_pct, "tie_nr": tie_nr},
        {"has_strong_bias": abs(bat1_pct - chase_pct) >= context["strong_bias_gap_min"]},
        [],
        _wilson_confidence_interval(bat1_wins, decided),
        _sample_reliability(total),
        _score_distribution(valid_stats),
        _score_extremes(valid_results),
        _bias_trend(valid_results, context["percent_scale"], context["reference_date"]),
        _toss_intelligence(valid_results, context["percent_scale"]),
        _toss_loss_recovery(valid_results, context["percent_scale"]),
        _score_banding(valid_stats, context["percent_scale"]),
        ",".join(valid_results["match_id"].astype(str).unique().tolist()) or None,
        SerializationService.serialize_raw_matches(valid_results),
    ]
    report = cast(VenueBiasReport, dict(zip(VenueBiasReport.__annotations__, report_values)))
    return report


def _empty_team_stats(team_name: str) -> TeamVenueStatsPayload:
    team_color = TEAM_COLORS.get(team_name) or TEAM_COLORS.get("VISITOR_TEAM") or TEAM_COLORS.get("Visitors", "gray")
    return {
        "wins": 0,
        "defended": 0,
        "chased": 0,
        "bat1": {"avg": None, "high": None, "low": None, "avg_win": None, "low_def": None},
        "chase": {"avg": None, "high": None, "succ": None, "fail": None},
        "team_color": team_color,
        "team_tone": None,
        "low_sample_warnings": [],
        "highlight_flags": {"has_low_sample_warnings": False},
        "derived_badges": [],
    }


def _empty_match_intel(home_team: str, opp_team: str) -> VenueMatchupReport:
    return {
        "summary": {"matches": 0, "win_pct": 0, "tie_nr": 0},
        "team_a": {"name": home_team, "stats": _empty_team_stats(home_team)},
        "team_b": {"name": opp_team, "stats": _empty_team_stats(opp_team)},
        "venue_avg": {"avg_1st": None, "avg_2nd": None, "avg_win_score": None},
        "MATCH_IDS": None,
        "low_sample_warnings": [],
        "highlight_flags": {"has_low_sample_warnings": False, "has_form_guide": False},
        "derived_badges": [],
    }


def _summary_payload(summary_df: pd.DataFrame, home_team: str, percent_scale: int) -> VenueMatchupSummary:
    unique_df = summary_df.groupby("match_id").first() if "match_id" in summary_df.columns else summary_df
    matches = len(unique_df)
    winner_series = unique_df["winner"].astype(str).str.lower().str.strip()
    home_wins = int((winner_series == home_team.lower().strip()).sum())
    tie_nr = int(winner_series.isin(["tie", "no result", "nan", "none"]).sum())
    decisions = matches - tie_nr
    return {"matches": matches, "win_pct": _safe_percent(home_wins, decisions, percent_scale), "tie_nr": tie_nr}


def _team_intel(
    summary_df: pd.DataFrame,
    team_name: str,
    competitive_threshold: int,
    low_sample_min_matches: int,
) -> TeamVenueStatsPayload:
    stats = calculate_team_metrics(df=summary_df, team_name=team_name, competitive_threshold=competitive_threshold)
    team_wins = summary_df[summary_df["winner"] == team_name]
    team_wins_first = (
        team_wins.groupby("match_id").first()
        if "match_id" in team_wins.columns and not team_wins.empty
        else team_wins
    )
    payload: TeamVenueStatsPayload = {
        "wins": len(team_wins_first),
        "defended": int((team_wins_first["team_bat_1"] == team_name).sum()),
        "chased": int((team_wins_first["team_bat_2"] == team_name).sum()),
        "bat1": {
            "avg": stats["avg_1st"],
            "high": stats["high_1st"],
            "low": stats["low_1st"],
            "avg_win": stats["avg_1st_win"],
            "low_def": _normalize_text_metric(stats["low_defended"]),
        },
        "chase": {
            "avg": stats["avg_2nd"],
            "high": stats["high_chased"],
            "succ": stats["avg_succ"],
            "fail": stats["avg_fail"],
        },
        "team_color": TEAM_COLORS.get(team_name) or TEAM_COLORS.get("VISITOR_TEAM") or TEAM_COLORS.get("Visitors", "gray"),
        "team_tone": None,
        "low_sample_warnings": [],
        "highlight_flags": {},
        "derived_badges": [],
    }
    payload["low_sample_warnings"] = _low_sample_warnings(team_name, payload, low_sample_min_matches)
    payload["highlight_flags"] = {"has_low_sample_warnings": bool(payload["low_sample_warnings"])}
    return payload


def _low_sample_warnings(team_name: str, payload: TeamVenueStatsPayload, min_matches: int) -> list[str]:
    sample_sizes = [
        ReportFormatter._extract_sample_size(payload["bat1"].get("avg")),
        ReportFormatter._extract_sample_size(payload["bat1"].get("avg_win")),
        ReportFormatter._extract_sample_size(payload["chase"].get("avg")),
    ]
    return ReportFormatter._format_low_sample_warnings(team_name, sample_sizes, min_matches)


def _venue_avg_payload(summary_df: pd.DataFrame, competitive_threshold: int) -> dict[str, str | int | None]:
    included_mask = MatchFilterService.get_valid_matches_mask(summary_df)
    short_second_mask = MatchFilterService.get_excluded_short_second_mask(summary_df)
    valid_1st = summary_df[included_mask | short_second_mask]
    valid_2nd = summary_df[included_mask]
    is_chase_win = valid_2nd["winner"] == valid_2nd["team_bat_2"]
    comp_mask = (~is_chase_win) | (valid_2nd["score_inn2"] >= competitive_threshold)
    comp_2nd = valid_2nd[comp_mask]
    return {
        "avg_1st": _normalize_none_marker(ReportBuilder._get_avg_with_count(valid_1st, "score_inn1")),
        "avg_2nd": _normalize_none_marker(ReportBuilder._get_avg_with_count(comp_2nd, "score_inn2")),
        "avg_win_score": _normalize_none_marker(ReportBuilder._get_avg_with_count(valid_1st[valid_1st["winner"] == valid_1st["team_bat_1"]], "score_inn1")),
    }


def calculate_venue_matchup_payload(match_df: pd.DataFrame, context: VenueMatchupContext) -> VenueMatchupPayload:
    venue_df, _ = _venue_window(match_df, context["stadium_id"], context["years_back"], context["reference_date"])
    if venue_df.empty:
        return {"payload": _empty_match_intel(context["home_team"], context["opp_team"])}
    clean_df = _apply_filters(venue_df, context["min_balls_for_completed_innings"])
    matchup_mask = ((clean_df["team_bat_1"] == context["home_team"]) & (clean_df["team_bat_2"] == context["opp_team"])) | ((clean_df["team_bat_1"] == context["opp_team"]) & (clean_df["team_bat_2"] == context["home_team"]))
    matchup_df = clean_df[matchup_mask].copy()
    summary_df = matchup_df[~MatchFilterService.get_excluded_no_result_mask(matchup_df)].copy()
    if summary_df.empty:
        return {"payload": _empty_match_intel(context["home_team"], context["opp_team"])}
    return {"payload": _build_match_intel(summary_df, context)}


def _build_match_intel(summary_df: pd.DataFrame, context: VenueMatchupContext) -> VenueMatchupReport:
    summary = _summary_payload(summary_df, context["home_team"], context["percent_scale"])
    team_a_stats = _team_intel(summary_df, context["home_team"], context["competitive_chase_threshold"], context["low_sample_min_matches"])
    team_b_stats = _team_intel(summary_df, context["opp_team"], context["competitive_chase_threshold"], context["low_sample_min_matches"])
    last_5_home = ReportFormatter._none_if_placeholder(ReportFormatter.format_form_guide(ReportBuilder._build_form_data_payload(summary_df, context["home_team"])))
    last_5_away = ReportFormatter._none_if_placeholder(ReportFormatter.format_form_guide(ReportBuilder._build_form_data_payload(summary_df, context["opp_team"])))
    low_sample_warnings = [*team_a_stats["low_sample_warnings"], *team_b_stats["low_sample_warnings"]]
    summary["last_5_home"] = last_5_home
    summary["last_5_away"] = last_5_away
    return {
        "summary": summary,
        "team_a": {"name": context["home_team"], "stats": team_a_stats},
        "team_b": {"name": context["opp_team"], "stats": team_b_stats},
        "venue_avg": _venue_avg_payload(summary_df, context["competitive_chase_threshold"]),
        "MATCH_IDS": ",".join(summary_df["match_id"].astype(str).unique().tolist()) or None,
        "low_sample_warnings": low_sample_warnings,
        "highlight_flags": {"has_low_sample_warnings": bool(low_sample_warnings), "has_form_guide": bool(last_5_home or last_5_away)},
        "derived_badges": [],
    }


def _coerce_match_meta(match_df: pd.DataFrame) -> pd.DataFrame:
    required = ["match_id", "balls_inn1", "wickets_inn1", "balls_inn2", "wickets_inn2", "winner", "team_bat_2"]
    if match_df.empty or not all(col in match_df.columns for col in required):
        return _empty_like(match_df)
    meta_df = match_df.copy()
    meta_df["match_id"] = meta_df["match_id"].astype(str).str.split(".").str[0].str.strip()
    meta_df = meta_df.drop_duplicates(subset=["match_id"])
    for col in ["balls_inn1", "balls_inn2", "wickets_inn1", "wickets_inn2"]:
        meta_df[col] = pd.to_numeric(meta_df[col], errors="coerce")
    return meta_df


def _valid_phase_match_ids(meta_df: pd.DataFrame, min_balls: int, all_out_wickets: int) -> tuple[set[str], set[str]]:
    if meta_df.empty:
        return set(), set()
    winner_norm = meta_df["winner"].astype(str).str.lower().str.strip()
    team2_norm = meta_df["team_bat_2"].astype(str).str.lower().str.strip()
    is_no_result = winner_norm.isin(["nan", "none", "no result", "abandoned", ""])
    is_chase_win = (~is_no_result) & (winner_norm == team2_norm)
    valid_1 = (meta_df["balls_inn1"] >= min_balls) | (meta_df["wickets_inn1"] >= all_out_wickets)
    valid_2 = (meta_df["balls_inn2"] >= min_balls) | (meta_df["wickets_inn2"] >= all_out_wickets) | is_chase_win
    short_1 = (meta_df["balls_inn1"] < min_balls) & (meta_df["wickets_inn1"] < all_out_wickets)
    short_2 = (meta_df["balls_inn2"] < min_balls) & (meta_df["wickets_inn2"] < all_out_wickets) & (~is_chase_win)
    eligible = (~(is_no_result & (short_1 | short_2))) & valid_1
    ids_1 = set(meta_df.loc[eligible & valid_1, "match_id"].astype(str))
    ids_2 = set(meta_df.loc[eligible & valid_2, "match_id"].astype(str))
    return ids_1, ids_2


def _filter_phase_rows(phase_df: pd.DataFrame, ids_1: set[str], ids_2: set[str]) -> pd.DataFrame:
    valid_ids = ids_1 | ids_2
    filtered_df = phase_df[phase_df["match_id"].isin(valid_ids)].copy()
    if "innings" not in filtered_df.columns:
        return filtered_df
    inn1 = (filtered_df["innings"] == 1) & filtered_df["match_id"].isin(ids_1)
    inn2 = (filtered_df["innings"] == 2) & filtered_df["match_id"].isin(ids_2)
    return filtered_df[inn1 | inn2].copy()


def _ensure_phase_dates(phase_df: pd.DataFrame, match_df: pd.DataFrame) -> pd.DataFrame:
    if phase_df.empty or "start_date" in phase_df.columns or "match_id" not in phase_df.columns:
        return phase_df.copy()
    if match_df.empty or "match_id" not in match_df.columns or "start_date" not in match_df.columns:
        return phase_df.copy()
    date_lookup_df = match_df.copy()
    date_lookup_df["match_id"] = date_lookup_df["match_id"].astype(str).str.split(".").str[0].str.strip()
    date_map = date_lookup_df.set_index("match_id")["start_date"].to_dict()
    merged_df = phase_df.copy()
    merged_df["start_date"] = merged_df["match_id"].map(date_map)
    return merged_df


def _phase_report_base(
    venue_stats: pd.DataFrame,
    stadium_id: str,
    years: int,
    min_balls: int,
    balls_per_over: int,
) -> VenuePhasesReport:
    match_count = int(venue_stats["match_id"].nunique()) if "match_id" in venue_stats.columns else int(len(venue_stats))
    return {
        "stadium_id": stadium_id, "match_count": match_count, "years": years,
        "filter_criteria": {
            "min_first_innings_balls": min_balls, "min_first_innings_overs": round(min_balls / balls_per_over, 1),
            "keep_all_outs": True, "keep_successful_chases": True, "drop_short_no_result_only": True,
        },
        "baseline": summarize_phase_by_innings(venue_stats), "home_at_venue": None, "away_at_venue": None, "global_habits": None,
        "MATCH_IDS": ",".join(venue_stats["match_id"].astype(str).unique().tolist()) if "match_id" in venue_stats.columns else None,
    }


def _attach_phase_team_snapshots(
    report: VenuePhasesReport,
    venue_stats: pd.DataFrame,
    home_team: str | None,
    away_team: str | None,
) -> None:
    if home_team and home_team != "All" and "team" in venue_stats.columns:
        home_df = venue_stats[venue_stats["team"] == home_team]
        if not home_df.empty:
            report["home_at_venue"] = cast(TeamVenuePhaseSnapshot, {"team": home_team, "stats": summarize_phase_by_innings(home_df)})
    if away_team and away_team != "All" and "team" in venue_stats.columns:
        away_df = venue_stats[venue_stats["team"] == away_team]
        if not away_df.empty:
            report["away_at_venue"] = cast(TeamVenuePhaseSnapshot, {"team": away_team, "stats": summarize_phase_by_innings(away_df)})


def _global_habits(phase_df: pd.DataFrame, home_team: str | None, away_team: str | None, cutoff: pd.Timestamp | None, start_year: int | str, phase_overs: dict[str, float]) -> VenueGlobalHabits | None:
    if not home_team or not away_team or away_team == "All" or "team" not in phase_df.columns:
        return None
    phase_window = phase_df[phase_df["start_date"] >= cutoff].copy() if cutoff is not None and "start_date" in phase_df.columns else phase_df.copy()
    home_df = phase_window[phase_window["team"] == home_team]
    away_df = phase_window[phase_window["team"] == away_team]
    if home_df.empty or away_df.empty:
        return None
    home_habits = calculate_team_phase_habits(home_df, phase_overs)
    away_habits = calculate_team_phase_habits(away_df, phase_overs)
    return cast(VenueGlobalHabits, {
        "start_year": start_year, "bat_first": {
            "home_team_pp_runs": home_habits["bat_first"]["pp_runs"], "away_team_pp_runs": away_habits["bat_first"]["pp_runs"],
            "home_team_pp_wkts": home_habits["bat_first"]["pp_wkts"], "away_team_pp_wkts": away_habits["bat_first"]["pp_wkts"],
            "home_team_mid_runs": home_habits["bat_first"]["mid_runs"], "away_team_mid_runs": away_habits["bat_first"]["mid_runs"],
            "home_team_mid_wkts": home_habits["bat_first"]["mid_wkts"], "away_team_mid_wkts": away_habits["bat_first"]["mid_wkts"],
            "home_team_dth_runs": home_habits["bat_first"]["dth_runs"], "away_team_dth_runs": away_habits["bat_first"]["dth_runs"],
            "home_team_dth_wkts": home_habits["bat_first"]["dth_wkts"], "away_team_dth_wkts": away_habits["bat_first"]["dth_wkts"]},
        "chasing": {
            "home_team_pp_runs": home_habits["chasing"]["pp_runs"], "away_team_pp_runs": away_habits["chasing"]["pp_runs"],
            "home_team_mid_wkts": home_habits["chasing"]["mid_wkts"], "away_team_mid_wkts": away_habits["chasing"]["mid_wkts"],
            "home_team_dth_wkts": home_habits["chasing"]["dth_wkts"], "away_team_dth_wkts": away_habits["chasing"]["dth_wkts"]},
        "home": home_habits["rr"], "away": away_habits["rr"], "scenario_rows": ReportFormatter.format_scenario_rows(build_phase_scenario_rows(home_habits, away_habits))
    })


def calculate_venue_phases_payload(phase_df: pd.DataFrame, context: VenuePhasesContext) -> VenuePhasesPayload:
    if phase_df.empty:
        return {"report": {}}
    phase_payload = calculate_phase_breakdown(phase_df, context["phases"])
    scoped_phase_df = phase_payload.get("phase_df", pd.DataFrame())
    phase_overs = cast(dict[str, float], phase_payload.get("phase_overs", {"pp": 0.0, "mid": 0.0, "dth": 0.0}))
    if scoped_phase_df.empty:
        return {"report": {}}
    meta_df = _coerce_match_meta(context["match_df"])
    ids_1, ids_2 = _valid_phase_match_ids(meta_df, context["min_balls_for_completed_innings"], context["all_out_wickets"])
    phase_window = _filter_phase_rows(scoped_phase_df, ids_1, ids_2) if ids_1 or ids_2 else scoped_phase_df.copy()
    phase_window = _ensure_phase_dates(phase_window, context["match_df"])
    venue_stats = phase_window[VenueService._build_venue_mask(phase_window, context["stadium_id"])].copy()
    report, cutoff, start_year = _phase_report_with_window(venue_stats, context)
    if not report:
        return {"report": {}}
    _attach_phase_team_snapshots(report, venue_stats, context["home_team"], context["away_team"])
    report["global_habits"] = _global_habits(phase_window, context["home_team"], context["away_team"], cutoff, start_year, phase_overs)
    return {"report": report}


def _phase_report_with_window(
    venue_stats: pd.DataFrame,
    context: VenuePhasesContext,
) -> tuple[VenuePhasesReport, pd.Timestamp | None, int | str]:
    if venue_stats.empty:
        return {}, None, context["phase_start_year_default"]
    if "start_date" not in venue_stats.columns:
        report = _phase_report_base(venue_stats, context["stadium_id"], context["years"], context["min_balls_for_completed_innings"], context["balls_per_over"])
        return report, None, context["phase_start_year_default"]
    cutoff = context["reference_date"] - pd.DateOffset(years=context["years"])
    scoped_stats = venue_stats[venue_stats["start_date"] >= cutoff].copy()
    if scoped_stats.empty:
        return {}, cutoff, cutoff.year
    report = _phase_report_base(scoped_stats, context["stadium_id"], context["years"], context["min_balls_for_completed_innings"], context["balls_per_over"])
    return report, cutoff, cutoff.year
