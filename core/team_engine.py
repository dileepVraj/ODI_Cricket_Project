"""
core/team_engine.py
Format-agnostic Team Engine factory.

Usage:
    from core.team_engine import get_team_engine
    TeamEngine = get_team_engine("odi")

For backward compatibility, a direct import of TeamEngine still works
and defaults to the ODI format.
"""
import importlib
import logging

logger = logging.getLogger("CricketAnalyzer")


def get_team_engine(format_type: str = "odi"):
    """
    Factory: Dynamically loads the TeamEngine class for the given format.
    Returns the CLASS (not an instance).
    """
    from config.format_registry import FORMATS
    entry = FORMATS.get(format_type)
    if not entry:
        raise KeyError(f"Unknown format: '{format_type}'. Available: {list(FORMATS.keys())}")

    module_path = f"{entry['module']}.engines.team_engine"
    try:
        module = importlib.import_module(module_path)
        return module.TeamEngine
    except (ImportError, AttributeError) as e:
        raise ImportError(
            f"TeamEngine not found for format '{format_type}' at '{module_path}'. Error: {e}"
        )


# --- BACKWARD COMPATIBILITY ---
# Direct `from core.team_engine import TeamEngine` defaults to ODI.
try:
    from formats.odi.engines.team_engine import TeamEngine
except ImportError:
    logger.warning("ODI TeamEngine not available. Use get_team_engine() factory for other formats.")

    class TeamEngine:
        """Placeholder — ODI format module not found."""
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "ODI Format not found. Use get_team_engine(format_type) to load a specific format."
            )
