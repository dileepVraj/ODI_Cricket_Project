from typing import Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, JsonValue

JsonObject = Dict[str, JsonValue]

class EngineParams(BaseModel):
    """
    Unified parameters for all engine functions.
    This model represents the union of all possible context fields and extra inputs.
    """
    # Context Fields
    venue: Optional[str] = Field(None, description="Venue ID (e.g., IND_MUMBAI_WANKHEDE)")
    team_a: Optional[str] = Field(None, description="Home/Primary team name")
    team_b: Optional[str] = Field(None, description="Away/Secondary team name")
    country_name: Optional[str] = Field(None, description="Host country for country-specific H2H")
    years: Optional[int] = Field(5, ge=1, le=50, description="Years of historical data to consider")
    region: Optional[str] = Field("All", description="Geographical region filter")

    # Squad Fields (SquadBuilder)
    home_xi: Optional[List[str]] = Field(None, description="Home team playing XI")
    away_xi: Optional[List[str]] = Field(None, description="Away team playing XI")

    # Extra Inputs
    player_name: Optional[str] = Field(None, description="Specific player for deep-dive/matchups")
    match_limit: Optional[Union[int, str]] = Field(None, description="Match limit for form analysis (int or 'All')")
    match_time: Optional[str] = Field(None, description="Time of match (Day/Night)")
    toss_result: Optional[str] = Field(None, description="Toss outcome for prediction")
    pitch_report: Optional[str] = Field(None, description="Qualitative pitch assessment")

    model_config = ConfigDict(extra="forbid")

class ExecuteRequest(BaseModel):
    """Generic request to execute any manifest-declared function."""
    model_config = ConfigDict(extra="forbid")
    params: EngineParams = Field(
        default_factory=EngineParams,
        description="Parameters to pass to the engine method. Keys match the manifest context fields.",
    )

class ExecuteResponse(BaseModel):
    """Generic response wrapper for any engine function output."""
    model_config = ConfigDict(extra="forbid")
    function_key: str
    output_type: str
    data: JsonValue = Field(..., description="The actual engine results (table, profile, etc.)")
    metadata: JsonObject = Field(
        default_factory=dict,
        description="Processing metadata (timing, engine used, etc.)"
    )

class ErrorResponse(BaseModel):
    """Structured error response following industry standards."""
    model_config = ConfigDict(extra="forbid")
    error: str = Field(..., description="Short error code/type")
    detail: str = Field(..., description="Human-readable explanation")
    function_key: Optional[str] = None
    status_code: int = 500
