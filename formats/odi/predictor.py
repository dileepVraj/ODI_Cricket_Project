"""ODI PredictorEngine — stateless prediction orchestration layer."""

from __future__ import annotations

import logging
from types import MappingProxyType
from typing import Dict, Optional, Tuple, cast

import pandas as pd

from core.exceptions import ConfigurationError
from core.interfaces.predictor_interface import IPredictorEngine
from core.interfaces.team_types import DataAccessPort, FormatConfig

logger = logging.getLogger("CricketAnalyzer")


class PredictorEngine(IPredictorEngine):
    """Stateless prediction engine (calculator-driven).

    Constructor accepts player_df and dal for backward-compatible
    instantiation but discards them — data arrives per-request
    via method parameters.
    """

    def __init__(
        # INTENTIONAL: player_df, dal discarded — engine is stateless.
        # Data arrives via method parameters per request.
        # Do not assign or store these parameters.
        # Do not remove this discard pattern.
        self,
        player_df: Optional[pd.DataFrame] = None,
        dal: Optional[DataAccessPort] = None,
        format_config: Optional[FormatConfig] = None,
        format_rules: Optional[FormatConfig] = None,
    ) -> None:
        _ = (player_df, dal)
        merged: Dict[str, object] = {}
        if isinstance(format_config, dict):
            merged.update(format_config)
        if isinstance(format_rules, dict):
            merged.update(format_rules)
        self._format_config = MappingProxyType(merged)

    def _require_format_config(self) -> FormatConfig:
        return cast(FormatConfig, dict(self._format_config))

    def _require_positive_number(
        self,
        raw_value: object,
        config_key: str,
    ) -> float:
        try:
            normalized = float(raw_value)  # type: ignore[arg-type]
        except (TypeError, ValueError) as exc:
            raise ConfigurationError(
                f"Invalid predictor config '{config_key}': {raw_value!r}"
            ) from exc
        if normalized <= 0:
            raise ConfigurationError(
                f"Predictor config '{config_key}' must be > 0."
            )
        return normalized

    def _config_float(self, key: str) -> float:
        config = self._require_format_config()
        config_map = cast(dict[str, object], config)
        if key not in config_map:
            raise ConfigurationError(
                f"Missing predictor config '{key}' in format_config."
            )
        return self._require_positive_number(config_map[key], key)

    def calculate_smart_projection(
        self,
        player: str,
        role: str,
        venue_pattern: str,
        *,
        player_df: Optional[pd.DataFrame] = None,
        venue_balls_df: Optional[pd.DataFrame] = None,
    ) -> Tuple[float, str]:
        """Calculate a player's projected performance.

        All data arrives as parameters — no DAL or stored state is used.

        Parameters
        ----------
        player : str
            Player name.
        role : str
            One of 'batting' or 'bowling'.
        venue_pattern : str
            Regex-safe venue pattern for filtering venue balls.
        player_df : pd.DataFrame, optional
            Pre-loaded player stats DataFrame.
        venue_balls_df : pd.DataFrame, optional
            Pre-loaded venue ball-by-ball data (filtered by caller).

        Returns
        -------
        Tuple[float, str]
            (projected_value, status_token)
        """
        if player_df is None or player_df.empty:
            return 0.0, ""

        # 1. Career Baseline (Static Context)
        bat = player_df[
            (player_df["player"] == player) & (player_df["role"] == role)
        ]

        if bat.empty:
            return 0.0, ""

        car_val = self._career_value(bat, role)

        # 2. Venue Specifics (from pre-loaded data)
        ven_val = self._venue_value(venue_balls_df, player, role, car_val)

        # 3. Weighted projection
        venue_weight = 0.3
        career_weight = 0.7
        proj = (venue_weight * ven_val) + (career_weight * car_val)
        return round(proj, 1), "OK"

    @staticmethod
    def _career_value(bat: pd.DataFrame, role: str) -> float:
        """Extract career value from filtered player stats."""
        context_mask = bat["context"] == "vs_team"
        context_df = bat[context_mask]
        if context_df.empty:
            return 0.0

        if role == "batting":
            runs = context_df["runs"].sum()
            outs = context_df["dismissals"].sum()
            return float(runs / outs) if outs > 0 else float(runs)

        # bowling
        wkts = context_df["dismissals"].sum()
        inns = context_df["innings"].sum()
        return float(wkts / inns) if inns > 0 else 0.0

    @staticmethod
    def _venue_value(
        venue_balls_df: Optional[pd.DataFrame],
        player: str,
        role: str,
        fallback: float,
    ) -> float:
        """Extract venue-specific value from pre-loaded ball data."""
        if venue_balls_df is None or venue_balls_df.empty:
            return fallback

        try:
            if role == "batting":
                if "runs_off_bat" not in venue_balls_df.columns:
                    return fallback
                v_runs = venue_balls_df["runs_off_bat"].sum()
                if "wicket_type" in venue_balls_df.columns:
                    v_outs = venue_balls_df["wicket_type"].notna().sum()
                else:
                    v_outs = 0
                return float(v_runs / v_outs) if v_outs > 0 else float(v_runs)

            # bowling
            wkt_types = [
                "bowled", "caught", "lbw", "stumped",
                "caught and bowled", "hit wicket",
            ]
            if "wicket_type" not in venue_balls_df.columns:
                return fallback
            v_wkts = venue_balls_df["wicket_type"].isin(wkt_types).sum()
            if "match_id" not in venue_balls_df.columns:
                return fallback
            v_matches = len(venue_balls_df["match_id"].unique())
            return float(v_wkts / v_matches) if v_matches > 0 else 0.0
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            logger.warning(
                "Non-fatal smart projection venue context issue for player '%s': %s",
                player,
                exc,
            )
            return fallback

    # -------------------------------------------------------------------------
    # predict_score() — REMOVED (Phase 12 Rebuild Pending)
    #
    # Reason: The previous implementation loaded the entire balls table
    # (~181MB on disk, 300-600MB in RAM) with no player or team filter.
    # This was identified as a critical memory risk for Phase 12's
    # 10-second scrape cycle which would have caused repeated RAM spikes
    # eventually exceeding the 4GB hardware ceiling.
    #
    # Rebuild Requirements (for when this is reimplemented):
    # - MUST filter by players=all_players before loading any ball data
    # - MUST filter by team and venue at the SQL level, not in Pandas
    # - MUST comply with the Memory Ceiling Law in engineering_standards.md
    # - MUST comply with the I/O Air-Gap Law — no DAL calls inside the
    #   execute path. Data must be pre-loaded and injected.
    # - MUST use pre-allocated NumPy arrays for simulation results
    # - MUST be registered in manifest.py before any API or UI work begins
    # -------------------------------------------------------------------------
