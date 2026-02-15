"""
FORMAT REGISTRY (v2.1)
Maps format keys to module paths and provides factory functions for:
  - Format modules
  - Engine classes (TeamEngine, PlayerEngine, PredictorEngine, MatchPackGenerator)
  - Manifests (for frontend-driven UI)
  - Format-specific config
  - Format metadata (for frontend format selector)
"""
import importlib
import logging

logger = logging.getLogger("CricketAnalyzer")

FORMATS = {
    "odi":   {"module": "formats.odi",   "label": "Men's ODI",     "icon": "🏏"},
    "t20i":  {"module": "formats.t20i",  "label": "Men's T20I",    "icon": "⚡"},
    "wodi":  {"module": "formats.wodi",  "label": "Women's ODI",   "icon": "🏏"},
    "wt20i": {"module": "formats.wt20i", "label": "Women's T20I",  "icon": "⚡"},
    "ipl":   {"module": "formats.ipl",   "label": "IPL",           "icon": "🏆"},
}


def get_format_module(format_type: str):
    """Dynamically imports and returns the format module."""
    entry = FORMATS.get(format_type)
    if not entry:
        raise KeyError(f"Unknown format: '{format_type}'. Available: {list(FORMATS.keys())}")
    return importlib.import_module(entry["module"])


def get_available_formats() -> list:
    """Returns list of (label, key) tuples for UI dropdowns."""
    return [(v["label"], k) for k, v in FORMATS.items()]


def get_format_metadata() -> list:
    """
    Returns format metadata for the frontend format selector.
    Each entry includes key, label, icon, and whether a manifest exists.
    """
    metadata = []
    for key, entry in FORMATS.items():
        has_manifest = False
        try:
            mod = importlib.import_module(f"{entry['module']}.manifest")
            has_manifest = hasattr(mod, "MANIFEST")
        except ImportError:
            pass

        metadata.append({
            "key": key,
            "label": entry["label"],
            "icon": entry["icon"],
            "has_manifest": has_manifest,
        })
    return metadata


def get_format_config(format_type: str) -> dict:
    """Returns the format-specific config dictionary (paths, phases, etc.)."""
    module = get_format_module(format_type)
    if hasattr(module, "FORMAT_CONFIG"):
        return module.FORMAT_CONFIG
    raise AttributeError(f"Format '{format_type}' module has no FORMAT_CONFIG.")


def get_format_manifest(format_type: str) -> dict:
    """Returns the format's manifest for frontend UI generation."""
    entry = FORMATS.get(format_type)
    if not entry:
        raise KeyError(f"Unknown format: '{format_type}'. Available: {list(FORMATS.keys())}")

    module_path = f"{entry['module']}.manifest"
    try:
        module = importlib.import_module(module_path)
        return module.MANIFEST
    except ImportError:
        raise ValueError(f"No manifest found for format '{format_type}' at '{module_path}'.")
    except AttributeError:
        raise ValueError(f"Manifest module for '{format_type}' has no MANIFEST dict.")


def get_format_engines(format_type: str) -> dict:
    """
    Returns a dict of engine CLASSES for the given format.
    Example: {"TeamEngine": <class>, "PlayerEngine": <class>, "PredictorEngine": <class>, "MatchPackGenerator": <class>}
    """
    entry = FORMATS.get(format_type)
    if not entry:
        raise KeyError(f"Unknown format: '{format_type}'. Available: {list(FORMATS.keys())}")

    base = entry["module"]
    engines = {}

    # TeamEngine
    try:
        mod = importlib.import_module(f"{base}.engines.team_engine")
        engines["TeamEngine"] = mod.TeamEngine
    except (ImportError, AttributeError) as e:
        logger.debug(f"TeamEngine not found for {format_type}: {e}")

    # PlayerEngine
    try:
        mod = importlib.import_module(f"{base}.engines.player_engine")
        engines["PlayerEngine"] = mod.PlayerEngine
    except (ImportError, AttributeError) as e:
        logger.debug(f"PlayerEngine not found for {format_type}: {e}")

    # PredictorEngine
    try:
        mod = importlib.import_module(f"{base}.predictor")
        engines["PredictorEngine"] = mod.PredictorEngine
    except (ImportError, AttributeError) as e:
        logger.debug(f"PredictorEngine not found for {format_type}: {e}")

    # MatchPackGenerator
    try:
        mod = importlib.import_module(f"{base}.match_pack")
        engines["MatchPackGenerator"] = mod.MatchPackGenerator
    except (ImportError, AttributeError) as e:
        logger.debug(f"MatchPackGenerator not found for {format_type}: {e}")

    return engines

