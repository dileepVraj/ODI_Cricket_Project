from typing import Dict, List

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str
    formats_loaded: List[str]
    total_matches: Dict[str, int]


class FormatMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    key: str
    label: str
    icon: str
    has_manifest: bool
