from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, JsonValue

class BattingStatsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    innings: int
    runs: int
    average: float
    strike_rate: float
    centuries: int
    fifties: int
    highest_score: int
    form_last_10: List[str]
    last_10_runs: List[Optional[int]] = Field(default_factory=list)

class BowlingStatsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    innings: int
    wickets: int
    average: float
    economy: float
    best_figures: str
    form_last_10: List[str]

class ContextStatsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    batting: BattingStatsSchema
    bowling: Optional[BowlingStatsSchema] = None

class PlayerProfileSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    role: str
    batting: BattingStatsSchema
    bowling: Optional[BowlingStatsSchema] = None
    venue_stats: Optional[ContextStatsSchema] = None
    vs_opponent_stats: Optional[ContextStatsSchema] = None
    phase_runs: List[dict] = Field(default_factory=list)
    vs_bowling_style: List[dict] = Field(default_factory=list)
    phase_bowling: List[dict] = Field(default_factory=list)
    last_10_bowling: List[Optional[int]] = Field(default_factory=list)

class MatchupStatsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    batter: str
    bowler: str
    balls: int
    runs: int
    outs: int
    avg: float
    sr: float
    is_bunny: bool
    threat_rating: Optional[str] = None
    confidence: Optional[int] = None
    dismissal_structural: Optional[int] = None
    dismissal_caught: Optional[int] = None
    dismissal_other: Optional[int] = None
    pp_balls: Optional[int] = None
    pp_runs: Optional[int] = None
    pp_outs: Optional[int] = None
    pp_avg: Optional[float] = None
    pp_sr: Optional[float] = None
    pp_threat_rating: Optional[str] = None
    mid_balls: Optional[int] = None
    mid_runs: Optional[int] = None
    mid_outs: Optional[int] = None
    mid_avg: Optional[float] = None
    mid_sr: Optional[float] = None
    mid_threat_rating: Optional[str] = None
    death_balls: Optional[int] = None
    death_runs: Optional[int] = None
    death_outs: Optional[int] = None
    death_avg: Optional[float] = None
    death_sr: Optional[float] = None
    death_threat_rating: Optional[str] = None
    highlight_flags: Optional[Dict[str, bool]] = None
    derived_badges: Optional[List[str]] = None
    cell_tones: Optional[Dict[str, str]] = None

class SquadMetricsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    caps: int
    runs: int
    wickets: int
    centuries: int
    fifties: int
    five_wkt_hauls: int
    avg_caps: int

class TacticalMatrixRowSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    player: str
    role: str
    stats_per_style: Dict[str, Dict[str, JsonValue]]

class SquadComparisonDataSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    team_a_name: str
    team_b_name: str
    metrics_a: SquadMetricsSchema
    metrics_b: SquadMetricsSchema
    player_stats_a: List[Dict[str, JsonValue]]
    player_stats_b: List[Dict[str, JsonValue]]
    venue_id: str
    years: int


class TeamVenueStatsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    wins: int
    defended: int
    chased: int
    bat1: Dict[str, JsonValue]
    chase: Dict[str, JsonValue]
    team_color: Optional[str] = None
    team_tone: Optional[str] = None
    low_sample_warnings: Optional[List[str]] = None
    highlight_flags: Optional[Dict[str, bool]] = None
    derived_badges: Optional[List[str]] = None


class MatchIntelligenceSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: Dict[str, JsonValue]
    team_a: Dict[str, JsonValue]  # {name: str, stats: TeamVenueStatsSchema}
    team_b: Dict[str, JsonValue]  # {name: str, stats: TeamVenueStatsSchema}
    venue_avg: Dict[str, JsonValue]
    MATCH_IDS: Optional[str] = None
    low_sample_warnings: Optional[List[str]] = None
    highlight_flags: Optional[Dict[str, bool]] = None
    derived_badges: Optional[List[str]] = None
