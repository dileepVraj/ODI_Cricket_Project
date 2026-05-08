"""
core/player_engine.py
Strict Player Engine strategy loader.
"""
import importlib
from typing import Type

from core.interfaces.player_interface import IPlayerEngine


def get_player_engine(format_key: str) -> Type[IPlayerEngine]:
    """
    Returns the concrete PlayerEngine class for a required format key.
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

    module_path = f"{entry['module']}.engines.player"
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise NotImplementedError(
            f"No player engine module for format '{normalized_key}' at '{module_path}'."
        ) from exc

    engine_cls = getattr(module, "PlayerEngine", None)
    if engine_cls is None:
        raise NotImplementedError(
            f"Module '{module_path}' does not define PlayerEngine."
        )

    if not issubclass(engine_cls, IPlayerEngine):
        raise TypeError(
            f"{module_path}.PlayerEngine must inherit from core.interfaces.player_interface.IPlayerEngine."
        )

    return engine_cls


__all__ = ["get_player_engine"]
