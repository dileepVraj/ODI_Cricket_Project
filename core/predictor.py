"""
core/predictor.py
Strict Predictor Engine strategy loader.
"""
import importlib
from typing import Type

from core.interfaces.predictor_interface import IPredictorEngine


def get_predictor_engine(format_key: str) -> Type[IPredictorEngine]:
    """
    Returns the concrete PredictorEngine class for a required format key.
    """
    if format_key is None or not str(format_key).strip():
        raise ValueError("format_key is required (must be a registered format key).")

    from config.format_registry import FORMATS

    normalized_key = str(format_key).strip().lower()
    entry = FORMATS.get(normalized_key)
    if not entry:
        raise ValueError(
            f"Unknown format_key '{normalized_key}'. Available: {list(FORMATS.keys())}"
        )

    module_path = f"{entry['module']}.predictor"
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise NotImplementedError(
            f"No predictor engine module for format '{normalized_key}' at '{module_path}'."
        ) from exc

    engine_cls = getattr(module, "PredictorEngine", None)
    if engine_cls is None:
        raise NotImplementedError(
            f"Module '{module_path}' does not define PredictorEngine."
        )

    if not issubclass(engine_cls, IPredictorEngine):
        raise TypeError(
            f"{module_path}.PredictorEngine must inherit from core.interfaces.predictor_interface.IPredictorEngine."
        )

    return engine_cls


__all__ = ["get_predictor_engine"]
