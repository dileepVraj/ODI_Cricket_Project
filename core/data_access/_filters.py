"""
DAL Filters - SQL WHERE clause builder helpers.
All functions are pure (no class state). Callers pass match_cols/ball_cols explicitly.
"""
from typing import Sequence

import pandas as pd

from config.shared.venues import get_venue_aliases


def is_blank_team(value: str | float | None) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and pd.isna(value):
        return True
    return str(value).strip() == ""


def is_no_result_winner(value: str | float | None) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and pd.isna(value):
        return True
    return str(value).strip().lower() in {"", "none", "nan", "no result", "abandoned"}


def is_regex_venue_filter(venue_identifier: str | None) -> bool:
    return isinstance(venue_identifier, str) and "|" in venue_identifier


def build_in_clause(column_name: str, values: Sequence[str]) -> str:
    placeholders = ",".join(["?"] * len(values))
    return f"{column_name} IN ({placeholders})"


def resolve_venue_terms(venue_identifier: str | None) -> list[str]:
    """
    Expands a venue identifier into canonical and raw aliases for robust filtering.
    """
    if not venue_identifier:
        return []
    try:
        aliases = get_venue_aliases(venue_identifier)
    except (AttributeError, KeyError, TypeError, ValueError):
        aliases = [venue_identifier]

    seen = set()
    terms = []
    for alias in aliases + [venue_identifier]:
        if alias is None:
            continue
        alias_str = str(alias).strip()
        if not alias_str or alias_str in seen:
            continue
        seen.add(alias_str)
        terms.append(alias_str)
    return terms


def append_matches_venue_filter(
    conditions: list[str],
    params: list,
    venue_identifier: str | None,
    match_cols: set[str],
) -> None:
    """
    Appends a venue WHERE clause for the matches table.
    match_cols: the set of column names in the matches table.
    """
    if is_regex_venue_filter(venue_identifier):
        parts = []
        if "venue_id" in match_cols:
            parts.append("regexp_matches(venue_id, ?)")
            params.append(venue_identifier)
        if "venue" in match_cols:
            parts.append("regexp_matches(venue, ?)")
            params.append(venue_identifier)
        if parts:
            conditions.append("(" + " OR ".join(parts) + ")")
        return

    terms = resolve_venue_terms(venue_identifier)
    if not terms:
        return

    parts = []
    if "venue_id" in match_cols:
        parts.append(build_in_clause("venue_id", terms))
        params.extend(terms)
    if "venue" in match_cols:
        parts.append(build_in_clause("venue", terms))
        params.extend(terms)

    if parts:
        conditions.append("(" + " OR ".join(parts) + ")")


def append_balls_venue_filter(
    conditions: list[str],
    params: list,
    venue_identifier: str | None,
    ball_cols: set[str],
) -> None:
    """
    Appends a venue WHERE clause for the balls table.
    ball_cols: the set of column names in the balls table.
    """
    if is_regex_venue_filter(venue_identifier):
        parts = []
        if "venue_id" in ball_cols:
            parts.append("regexp_matches(venue_id, ?)")
            params.append(venue_identifier)
        if "venue" in ball_cols:
            parts.append("regexp_matches(venue, ?)")
            params.append(venue_identifier)
        if parts:
            conditions.append("(" + " OR ".join(parts) + ")")
        return

    terms = resolve_venue_terms(venue_identifier)
    if not terms:
        return

    parts = []
    if "venue_id" in ball_cols:
        parts.append(build_in_clause("venue_id", terms))
        params.extend(terms)
    if "venue" in ball_cols:
        parts.append(build_in_clause("venue", terms))
        params.extend(terms)

    if parts:
        conditions.append("(" + " OR ".join(parts) + ")")


def append_matches_team_filter(
    conditions: list[str],
    params: list,
    team_name: str | None,
) -> None:
    """
    Robust match-team filter:
    1) Primary: matches.team_bat_1 / matches.team_bat_2
    2) Fallback: correlated lookup against balls.batting_team / balls.bowling_team
    """
    if not team_name:
        return

    conditions.append(
        "("
        "team_bat_1 = ? OR team_bat_2 = ? "
        "OR EXISTS ("
        "SELECT 1 FROM balls b "
        "WHERE b.match_id = matches.match_id "
        "AND (b.batting_team = ? OR b.bowling_team = ?)"
        ")"
        ")"
    )
    params.extend([team_name, team_name, team_name, team_name])
