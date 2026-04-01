from typing import List

from pydantic import BaseModel, ConfigDict

class TeamInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str

class TeamsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    format_key: str
    teams: List[str]

class VenueInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    label: str

class VenuesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    format_key: str
    venues: List[VenueInfo]

class PlayersResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    format_key: str
    team: str
    players: List[str]

class RegionsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    format_key: str
    regions: List[str]


class HostCountriesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    format_key: str
    countries: List[str]
