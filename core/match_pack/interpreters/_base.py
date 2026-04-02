"""
core/match_pack/interpreters._base — shared base class for all interpreter domains.
"""
from __future__ import annotations

import importlib
from typing import Any, Dict, Optional


class InterpreterBase:
    def __init__(
        self,
        rankings: Optional[Dict[str, Any]] = None,
        bowler_styles: Optional[Dict[str, str]] = None,
        player_roles: Optional[Dict[str, str]] = None,
        format_key: str = "",
    ) -> None:
        if not str(format_key).strip():
            raise ValueError("format_key is required for MatchInterpreter initialization.")

        default_rankings: Dict[str, Any] = {}
        default_bowler_styles: Dict[str, str] = {}
        default_player_roles: Dict[str, str] = {}

        if rankings is None or bowler_styles is None or player_roles is None:
            try:
                players_module = importlib.import_module(f"formats.{format_key}.config.players")  # nosemgrep: python.lang.security.audit.non-literal-import.non-literal-import
                rankings_module = importlib.import_module(f"formats.{format_key}.config.rankings")  # nosemgrep: python.lang.security.audit.non-literal-import.non-literal-import
                ranking_candidates = [
                    "RANKINGS",
                    f"{str(format_key).upper()}_RANKINGS",
                ]
                for attr_name in ranking_candidates:
                    candidate = getattr(rankings_module, attr_name, None)
                    if isinstance(candidate, dict):
                        default_rankings = candidate
                        break
                if not default_rankings:
                    for attr_name in dir(rankings_module):
                        if attr_name.endswith("_RANKINGS"):
                            candidate = getattr(rankings_module, attr_name, None)
                            if isinstance(candidate, dict):
                                default_rankings = candidate
                                break
                default_bowler_styles = getattr(players_module, "BOWLER_STYLES", {})
                default_player_roles = getattr(players_module, "PLAYER_ROLES", {})
            except (ImportError, AttributeError):
                pass

        self.rankings = rankings if rankings is not None else default_rankings
        self.bowler_styles = bowler_styles if bowler_styles is not None else default_bowler_styles
        self.player_roles = player_roles if player_roles is not None else default_player_roles
