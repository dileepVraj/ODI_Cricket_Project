"""Context routes extracted from api.main."""

from __future__ import annotations

from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, Path, Query  # noqa: F401

from api.context_builder import _engine_default_int
from api.schemas.context import VenueInfo
from api.route_helpers import RequestValidator
from api.schemas import (
    HostCountriesResponse,
    PlayersResponse,
    RegionsResponse,
    TeamsResponse,
    VenuesResponse,
)
from config.format_registry import get_format_manifest
from config.settings import API_V1_PREFIX
from config.shared.venues import VENUE_MAP, list_host_countries_from_venue_ids


router = APIRouter(prefix=API_V1_PREFIX)


@router.get("/{format_type}/context/teams", response_model=TeamsResponse, tags=["Context"])
def get_teams(format_type: str = Path(..., description="Format key")) -> TeamsResponse:
    """Returns all teams available in this format's dataset."""
    analyzer = RequestValidator.get_analyzer_or_404(format_type)

    teams = set()
    if hasattr(analyzer, "match_df") and not analyzer.match_df.empty:
        df = analyzer.match_df
        if "team_bat_1" in df.columns:
            teams.update(df["team_bat_1"].dropna().unique())
        if "team_bat_2" in df.columns:
            teams.update(df["team_bat_2"].dropna().unique())

    return TeamsResponse(
        format_key=format_type,
        teams=sorted(teams),
    )


@router.get("/{format_type}/context/venues", response_model=VenuesResponse, tags=["Context"])
def get_venues(format_type: str = Path(..., description="Format key")) -> VenuesResponse:
    """Returns all venues available in this format, formatted for UI selectors."""
    analyzer = RequestValidator.get_analyzer_or_404(format_type)

    venues_list: list[VenueInfo] = []
    if hasattr(analyzer, "match_df") and not analyzer.match_df.empty:
        df = analyzer.match_df
        if "venue" in df.columns:
            unique_raw_names = df["venue"].dropna().unique()
            seen_codes: set[str] = set()
            for raw_name in unique_raw_names:
                venue_code = VENUE_MAP.get(raw_name, raw_name)
                if venue_code in seen_codes:
                    continue
                seen_codes.add(venue_code)
                display_label = str(raw_name)
                venues_list.append(VenueInfo(id=str(venue_code), label=display_label))

    return VenuesResponse(
        format_key=format_type,
        venues=sorted(venues_list, key=lambda x: x.label),
    )


@router.get("/{format_type}/context/players/{team}", response_model=PlayersResponse, tags=["Context"])
def get_players(
    team: str = Path(..., description="Team name (or 'All')"),
    format_type: str = Path(..., description="Format key"),
    opponent: Optional[str] = Query(
        None,
        description="Opponent team name for h2h squad lookup",
    ),
) -> PlayersResponse:
    """Returns unique players from the dataset, optionally filtered by team."""
    analyzer = RequestValidator.get_analyzer_or_404(format_type)
    team_norm = str(team).strip()
    opponent_norm = str(opponent).strip() if opponent else None
    players = []

    if team_norm.lower() == "all":
        if hasattr(analyzer, "player_df") and not analyzer.player_df.empty:
            players = sorted(analyzer.player_df["player"].dropna().astype(str).unique().tolist())
        else:
            if hasattr(analyzer, "meta_df") and not analyzer.meta_df.empty:
                players = sorted(analyzer.meta_df["player"].dropna().astype(str).unique().tolist())
    else:
        if hasattr(analyzer, "player_engine"):
            try:
                player_engine = analyzer.player_engine
                last_xi: list[str] = []
                active_squad: list[str] = []
                team_matches = pd.DataFrame()
                match_balls = pd.DataFrame()

                if hasattr(player_engine, "get_last_match_xi"):
                    dal = getattr(analyzer, "dal", None)
                    if dal is not None:
                        team_matches = dal.get_matches(
                            team_a=team_norm,
                            team_b=opponent_norm if opponent_norm else None,
                        )
                        if not team_matches.empty and "match_id" in team_matches.columns:
                            recent_match_ids = (
                                team_matches.sort_values("start_date", ascending=False)["match_id"]
                                .astype(str)
                                .dropna()
                                .unique()
                                .tolist()[:_engine_default_int(analyzer, "recent_match_ids_limit", 1)]
                            )
                            if recent_match_ids:
                                match_balls = dal.get_balls(match_ids=recent_match_ids)
                    last_xi = player_engine.get_last_match_xi(
                        team_norm,
                        team_matches=team_matches,
                        match_balls_df=match_balls,
                        opponent=opponent_norm if opponent_norm else None,
                    ) or []
                if hasattr(player_engine, "get_active_squad"):
                    active_squad = player_engine.get_active_squad(team_norm) or []

                if last_xi:
                    seen = set()
                    merged = []
                    for name in [*last_xi, *active_squad]:
                        key = str(name).strip()
                        if key and key not in seen:
                            seen.add(key)
                            merged.append(key)
                    players = merged
                else:
                    players = active_squad
            except (AttributeError, KeyError):
                if hasattr(analyzer, "meta_df") and not analyzer.meta_df.empty:
                    mask = analyzer.meta_df["team"] == team_norm
                    players = sorted(analyzer.meta_df[mask]["player"].unique().tolist())

    return PlayersResponse(
        format_key=format_type,
        team=team_norm,
        players=players,
    )


@router.get("/{format_type}/context/regions", response_model=RegionsResponse, tags=["Context"])
def get_regions(format_type: str = Path(..., description="Format key")) -> RegionsResponse:
    """Returns available regions/continents for filtering."""
    RequestValidator.validate_format(format_type)
    try:
        manifest = get_format_manifest(format_type)
        region_field = manifest.get("context_fields", {}).get("region", {})
        options = region_field.get("options", ["All", "Asia", "Europe", "Oceania", "Africa", "Americas"])
    except (ValueError, ImportError):
        options = ["All", "Asia", "Europe", "Oceania", "Africa", "Americas"]

    return RegionsResponse(format_key=format_type, regions=options)


@router.get("/{format_type}/context/host_countries", response_model=HostCountriesResponse, tags=["Context"])
def get_host_countries(format_type: str = Path(..., description="Format key")) -> HostCountriesResponse:
    """Returns available host countries inferred from venue_id prefixes."""
    analyzer = RequestValidator.get_analyzer_or_404(format_type)
    countries = []
    if hasattr(analyzer, "match_df") and not analyzer.match_df.empty:
        df = analyzer.match_df
        if "venue_id" in df.columns:
            venue_ids = df["venue_id"].dropna().astype(str).unique().tolist()
            countries = list_host_countries_from_venue_ids(venue_ids)
    return HostCountriesResponse(format_key=format_type, countries=countries)
