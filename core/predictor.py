"""
core/predictor.py
Format-agnostic Predictor Engine factory + base class.

Usage:
    from core.predictor import get_predictor_engine
    PredictorEngine = get_predictor_engine("odi")

For backward compatibility, a direct import of PredictorEngine still works
and defaults to the ODI format.
"""
import importlib
import logging

logger = logging.getLogger("CricketAnalyzer")


def get_predictor_engine(format_type: str = "odi"):
    """
    Factory: Dynamically loads the PredictorEngine class for the given format.
    Returns the CLASS (not an instance).
    """
    from config.format_registry import FORMATS
    entry = FORMATS.get(format_type)
    if not entry:
        raise KeyError(f"Unknown format: '{format_type}'. Available: {list(FORMATS.keys())}")

    module_path = f"{entry['module']}.predictor"
    try:
        module = importlib.import_module(module_path)
        return module.PredictorEngine
    except (ImportError, AttributeError) as e:
        raise ImportError(
            f"PredictorEngine not found for format '{format_type}' at '{module_path}'. Error: {e}"
        )


# --- BACKWARD COMPATIBILITY ---
# Direct `from core.predictor import PredictorEngine` defaults to ODI.
try:
    from formats.odi.predictor import PredictorEngine
except ImportError:
    logger.warning("ODI PredictorEngine not available. Use get_predictor_engine() factory.")

    class PredictorEngine:
        """Placeholder — ODI format module not found."""
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "ODI Format not found. Use get_predictor_engine(format_type) to load a specific format."
            )
