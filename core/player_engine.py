"""
core/player_engine.py
Format-agnostic Player Engine factory.

Usage:
    from core.player_engine import get_player_engine
    PlayerEngine = get_player_engine("odi")

For backward compatibility, a direct import of PlayerEngine still works
and defaults to the ODI format.
"""
import importlib
import logging

logger = logging.getLogger("CricketAnalyzer")


def get_player_engine(format_type: str = "odi"):
    """
    Factory: Dynamically loads the PlayerEngine class for the given format.
    Returns the CLASS (not an instance).
    """
    from config.format_registry import FORMATS
    entry = FORMATS.get(format_type)
    if not entry:
        raise KeyError(f"Unknown format: '{format_type}'. Available: {list(FORMATS.keys())}")

    module_path = f"{entry['module']}.engines.player_engine"
    try:
        module = importlib.import_module(module_path)
        return module.PlayerEngine
    except (ImportError, AttributeError) as e:
        raise ImportError(
            f"PlayerEngine not found for format '{format_type}' at '{module_path}'. Error: {e}"
        )


# --- BACKWARD COMPATIBILITY ---
# Direct `from core.player_engine import PlayerEngine` defaults to ODI.
try:
    from formats.odi.engines.player_engine import PlayerEngine
except ImportError:
    logger.warning("ODI PlayerEngine not available. Use get_player_engine() factory for other formats.")

    class PlayerEngine:
        """Placeholder — ODI format module not found."""
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "ODI Format not found. Use get_player_engine(format_type) to load a specific format."
            )
