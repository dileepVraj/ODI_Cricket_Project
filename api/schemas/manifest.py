from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, JsonValue

JsonObject = Dict[str, JsonValue]


# ── New manifest extension models (TASK-046) ────────────────────────────


class SourceRegistryEntry(BaseModel):
    """A single entry in the source registry.

    Maps a semantic source identifier (e.g. 'teams', 'venues') to an
    API path template.  The frontend resolves the template at runtime
    by substituting {format_key}, {team}, etc.
    """
    model_config = ConfigDict(extra="forbid")
    path: str
    preload: bool = False


class NavigationRoot(BaseModel):
    """Declaration of the default / home screen.

    Eliminates hardcoded 'dashboard' strings in page.tsx and Sidebar.tsx.
    """
    model_config = ConfigDict(extra="forbid")
    key: str
    label: str
    icon: str


class QuickLinkDesc(BaseModel):
    """A single quick-link entry attached to a category.

    Allows the manifest to declare contextual navigation links
    (e.g. 'From Venue Intel jump to Rivalry Lab') instead of
    hardcoding link arrays in the frontend.
    """
    model_config = ConfigDict(extra="forbid")
    label: str
    category_key: str


# ── Existing models (extended where noted) ──────────────────────────────


class ContextFieldDesc(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: str
    label: str
    required: bool = False
    source: Optional[str] = None
    source_params: Optional[JsonObject] = None  # TASK-046: template params for source path
    min: Optional[int] = None
    max: Optional[int] = None
    default: Optional[JsonValue] = None
    options: Optional[List[str]] = None
    placeholder: Optional[str] = None  # TASK-046: optional placeholder text

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
    quick_links: Optional[List[QuickLinkDesc]] = None  # TASK-046

class ManifestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    format_key: str
    format_label: str
    format_icon: str
    version: str
    context_fields: Dict[str, ContextFieldDesc]
    categories: List[CategoryDesc]
    output_types: List[str]
    source_registry: Optional[Dict[str, SourceRegistryEntry]] = None  # TASK-046
    navigation_root: Optional[NavigationRoot] = None  # TASK-046
