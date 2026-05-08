"""
formats/odi/manifest.py — thin shim.
All definitions live in formats/odi/manifests/.
"""
from formats.odi.manifests import (
    MANIFEST,
    get_manifest_stats,
    FORMAT_RULES,
    TACTICAL_THRESHOLDS,
    SPORT_CONSTANTS,
    ENGINE_DEFAULTS,
    PLAYER_RULES,
    PLAYER_CONTEXT_TYPES,
)
from formats.odi.manifests._config import (
    ENGINE_LITERAL_REGISTRY,
    SERVICE_LITERAL_REGISTRY,
    CALCULATOR_LITERAL_REGISTRY,
)

__all__ = [
    "MANIFEST",
    "get_manifest_stats",
    "FORMAT_RULES",
    "TACTICAL_THRESHOLDS",
    "SPORT_CONSTANTS",
    "ENGINE_DEFAULTS",
    "PLAYER_RULES",
    "PLAYER_CONTEXT_TYPES",
    "ENGINE_LITERAL_REGISTRY",
    "SERVICE_LITERAL_REGISTRY",
    "CALCULATOR_LITERAL_REGISTRY",
]
