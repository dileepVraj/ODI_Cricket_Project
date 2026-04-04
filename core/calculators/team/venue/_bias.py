"""Venue bias calculator domain."""

from __future__ import annotations

from typing import cast

import pandas as pd

from core.calculators.team.venue._base import (
    VenueBiasContext,
    VenueBiasPayload,
    VenueBiasReport,
    _apply_filters,
    _normalize_none_marker,
    _safe_percent,
    _venue_window,
)
from core.interfaces.venue_types import (
    VenueBiasCI,
    VenueBiasTrend,
    VenueScoreBand,
    VenueScoreBanding,
    VenueScoreDistribution,
    VenueScoreExtremes,
    VenueScoreStats,
    VenueTossIntelligence,
    VenueTossLossRecovery,
)
from core.services.match_filter_service import MatchFilterService
from core.services.report_builder import ReportBuilder
from core.services.serialization_service import SerializationService
from core.services.venue_service import VenueService


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
    int(valid_results["match_id"].nunique())
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
