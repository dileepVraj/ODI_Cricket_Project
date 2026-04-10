"""ODI format module.
Exports the standard interface expected by the format router.
"""
from __future__ import annotations

from typing import Any

from formats.odi.config.settings import ODI_FORMAT_CONFIG as FORMAT_CONFIG

__all__ = [
    "PlayerEngine",
    "TeamEngine",
    "PredictorEngine",
    "FORMAT_CONFIG",
]


def __getattr__(name: str) -> Any:
    if name == "PlayerEngine":
        from formats.odi.engines.player import PlayerEngine

        return PlayerEngine
    if name == "TeamEngine":
        from formats.odi.engines.team import TeamEngine

        return TeamEngine
    if name == "PredictorEngine":
        from formats.odi.predictor import PredictorEngine

        return PredictorEngine
    if name == "FORMAT_CONFIG":
        return FORMAT_CONFIG
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
