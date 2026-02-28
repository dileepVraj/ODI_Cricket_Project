from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, JsonValue

JsonObject = Dict[str, JsonValue]

class ContextFieldDesc(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: str
    label: str
    required: bool = False
    source: Optional[str] = None
    min: Optional[int] = None
    max: Optional[int] = None
    default: Optional[JsonValue] = None
    options: Optional[List[str]] = None

class FunctionDesc(BaseModel):
    model_config = ConfigDict(extra="forbid")
    key: str
    label: str
    icon: str
    engine_class: str
    engine_method: str
    required_context: List[str]
    optional_context: Optional[List[str]] = None
    extra_inputs: Optional[JsonObject] = None
    output_type: str
    output_schema: Optional[JsonObject] = None

class CategoryDesc(BaseModel):
    model_config = ConfigDict(extra="forbid")
    key: str
    label: str
    icon: str
    group: Optional[str] = None
    description: Optional[str] = None
    functions: List[FunctionDesc]

class ManifestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    format_key: str
    format_label: str
    format_icon: str
    version: str
    context_fields: Dict[str, ContextFieldDesc]
    categories: List[CategoryDesc]
    output_types: List[str]
