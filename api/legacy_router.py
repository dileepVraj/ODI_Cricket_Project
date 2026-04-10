"""Legacy v0 compatibility routes."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter

from api.context_router import (
    get_host_countries,
    get_players,
    get_regions,
    get_teams,
    get_venues,
)
from api.schemas import (
    ExecuteRequest,
    ExecuteResponse,
    FormatMetadata,
    HostCountriesResponse,
    ManifestResponse,
    PlayersResponse,
    RegionsResponse,
    TeamsResponse,
    VenuesResponse,
)


router = APIRouter(prefix="/api/v0", include_in_schema=False)


@router.get("/formats", response_model=List[FormatMetadata], tags=["Legacy"])
def legacy_formats() -> List[FormatMetadata]:
    from api.main import list_formats as current_list_formats

    return current_list_formats()


@router.get("/{format_type}/manifest", response_model=ManifestResponse, tags=["Legacy"])
def legacy_manifest(format_type: str) -> ManifestResponse:
    from api.main import get_manifest as current_get_manifest

    return current_get_manifest(format_type)


@router.get("/{format_type}/context/teams", response_model=TeamsResponse, tags=["Legacy"])
def legacy_teams(format_type: str) -> TeamsResponse:
    return get_teams(format_type)


@router.get("/{format_type}/context/venues", response_model=VenuesResponse, tags=["Legacy"])
def legacy_venues(format_type: str) -> VenuesResponse:
    return get_venues(format_type)


@router.get("/{format_type}/context/players/{team}", response_model=PlayersResponse, tags=["Legacy"])
def legacy_players(format_type: str, team: str) -> PlayersResponse:
    return get_players(team=team, format_type=format_type)


@router.get("/{format_type}/context/regions", response_model=RegionsResponse, tags=["Legacy"])
def legacy_regions(format_type: str) -> RegionsResponse:
    return get_regions(format_type)


@router.get("/{format_type}/context/host_countries", response_model=HostCountriesResponse, tags=["Legacy"])
def legacy_host_countries(format_type: str) -> HostCountriesResponse:
    return get_host_countries(format_type)


@router.post("/{format_type}/execute/{function_key}", response_model=ExecuteResponse, tags=["Legacy"])
def legacy_execute(
    request: ExecuteRequest,
    format_type: str,
    function_key: str,
) -> ExecuteResponse:
    from api.main import execute_function as current_execute_function

    return current_execute_function(
        request=request,
        format_type=format_type,
        function_key=function_key,
    )
