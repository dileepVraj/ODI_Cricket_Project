"""
api/models.py — Pydantic Models for Request/Response Validation (v1.0)

Defines typed contracts for the API layer.
All engine-agnostic — works with any format's manifest.
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


# ── Request Models ───────────────────────────────────────────────────────

class ExecuteRequest(BaseModel):
    """Generic request to execute any manifest-declared function."""
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters to pass to the engine method. Keys match the method's arguments.",
    )


class SquadExecuteRequest(BaseModel):
    """Extended request for functions requiring squad lists (compare_squads, predict_score, etc.)."""
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters for the engine method.",
    )
    home_xi: Optional[List[str]] = Field(
        default=None,
        description="Home team Playing XI player names.",
    )
    away_xi: Optional[List[str]] = Field(
        default=None,
        description="Away team Playing XI player names.",
    )


# ── Response Models ──────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    formats_loaded: List[str] = []
    total_matches: Dict[str, int] = {}


class ManifestResponse(BaseModel):
    """Full manifest for a format — drives the entire frontend UI."""
    format_key: str
    format_label: str
    format_icon: str
    context_fields: Dict[str, Any]
    categories: List[Dict[str, Any]]
    output_types: List[str] = []


class FormatInfo(BaseModel):
    """Metadata about a single format."""
    key: str
    label: str
    icon: str
    has_manifest: bool


class ContextTeamsResponse(BaseModel):
    """List of teams available in a format."""
    format_key: str
    teams: List[str]


class ContextVenuesResponse(BaseModel):
    """List of venues available in a format."""
    format_key: str
    venues: List[Dict[str, str]]  # [{id: "IND_MUMBAI_WANKHEDE", label: "Mumbai - Wankhede"}]


class ContextPlayersResponse(BaseModel):
    """List of players for a specific team."""
    format_key: str
    team: str
    players: List[str]


class ExecuteResponse(BaseModel):
    """Generic response wrapper for any engine function output."""
    function_key: str
    output_type: str
    data: Any
    metadata: Dict[str, Any] = {}


class ErrorResponse(BaseModel):
    """Structured error response."""
    error: str
    detail: str
    function_key: Optional[str] = None
