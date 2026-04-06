from __future__ import annotations

from types import MappingProxyType
from typing import Optional, Union, cast

import pandas as pd

from core.exceptions import ConfigurationError
from core.interfaces.team_interface import ITeamEngine
from core.interfaces.team_types import DataAccessPort, FormatConfig, SportConstants, TacticalThresholds, TeamMatchContext


class TeamEngineBase(ITeamEngine):
    def __init__(
        # INTENTIONAL: match_df, phase_df, dal
        # discarded — engine is stateless.
        # Data arrives via match_context per request.
        # Do not assign or store these parameters.
        # Do not remove this discard pattern.
        self,
        match_df: Optional[pd.DataFrame] = None,
        phase_df: Optional[pd.DataFrame] = None,
        dal: Optional[DataAccessPort] = None,
        format_rules: Optional[FormatConfig] = None,
    ) -> None:
        _ = (match_df, phase_df, dal)
        self._format_config = MappingProxyType(dict(format_rules or {}))

    @staticmethod
    def _compute_reference_date(match_frame: pd.DataFrame) -> pd.Timestamp:
        if match_frame is not None and not match_frame.empty and "start_date" in match_frame.columns:
            max_date = match_frame["start_date"].max()
            if pd.notna(max_date):
                return pd.Timestamp(max_date).floor("D")
        return pd.Timestamp.now().floor("D")

    def _require_match_context(self, match_context: Optional[TeamMatchContext]) -> TeamMatchContext:
        if isinstance(match_context, dict):
            return match_context
        raise ConfigurationError("Missing required 'match_context'. Inject match_df/phase_df/reference_date/tactical_thresholds per request.")

    @staticmethod
    def _context_df(match_context: TeamMatchContext, key: str) -> pd.DataFrame:
        frame = match_context.get(key)
        if isinstance(frame, pd.DataFrame):
            return frame.copy()
        return pd.DataFrame()

    def _context_reference_date(self, match_context: TeamMatchContext) -> pd.Timestamp:
        raw_value = match_context.get("reference_date")
        if raw_value is None:
            return self._compute_reference_date(self._context_df(match_context, "match_df"))
        try:
            return pd.Timestamp(raw_value).floor("D")
        except (TypeError, ValueError) as exc:
            raise ConfigurationError(f"Invalid match_context reference_date: {raw_value!r}") from exc

    def _require_format_config(self) -> FormatConfig:
        return cast(FormatConfig, dict(self._format_config))

    def _require_positive_int(self, raw_value: Union[int, str, float, None], config_key: str) -> int:
        try:
            normalized = int(raw_value)
        except (TypeError, ValueError) as exc:
            _ = (config_key, raw_value)
            raise ConfigurationError from exc
        if normalized <= 0:
            raise ConfigurationError
        return normalized

    def _min_balls_for_completed_innings(self) -> int:
        format_config = self._require_format_config()
        if "min_balls_for_completed_innings" not in format_config:
            raise ConfigurationError
        return self._require_positive_int(format_config.get("min_balls_for_completed_innings"), "min_balls_for_completed_innings")

    def _default_years_window(self) -> int:
        format_config = self._require_format_config()
        if "default_years_window" not in format_config:
            raise ConfigurationError
        return self._require_positive_int(format_config.get("default_years_window"), "default_years_window")

    def _resolved_years(self, years_value: int) -> int:
        return years_value if years_value > 0 else self._default_years_window()

    def _phase_rules(self) -> dict[str, list[int]]:
        raw_rules = self._require_format_config().get("phases")
        if not isinstance(raw_rules, dict) or not raw_rules:
            raise ConfigurationError
        normalized: dict[str, list[int]] = {}
        for key, value in raw_rules.items():
            if isinstance(value, (list, tuple)) and len(value) >= 2:
                normalized[str(key)] = [int(value[0]), int(value[1])]
        if not normalized:
            raise ConfigurationError
        return normalized

    def _require_tactical_thresholds(self, match_context: TeamMatchContext) -> TacticalThresholds:
        format_config = self._require_format_config()
        base_thresholds = format_config.get("tactical_thresholds")
        context_thresholds = match_context.get("tactical_thresholds")
        if not isinstance(base_thresholds, dict) or not base_thresholds:
            raise ConfigurationError
        raw_thresholds = dict(base_thresholds)
        if isinstance(context_thresholds, dict) and context_thresholds:
            raw_thresholds.update(context_thresholds)
        if not isinstance(raw_thresholds, dict) or not raw_thresholds:
            raise ConfigurationError
        thresholds: TacticalThresholds = {}
        for key in ("competitive_chase_threshold", "low_sample_min_matches", "bias_win_pct_min", "strong_bias_gap_min", "phase_start_year_default", "form_window_matches"):
            if key in raw_thresholds:
                thresholds[key] = int(raw_thresholds[key])
        return thresholds

    def _threshold(self, match_context: TeamMatchContext, key: str) -> int:
        thresholds = self._require_tactical_thresholds(match_context)
        if key not in thresholds:
            raise ConfigurationError(f"Missing tactical threshold '{key}' in FORMAT_RULES['tactical_thresholds'].")
        return int(thresholds[key])

    def _require_sport_constants(self) -> SportConstants:
        raw_constants = self._require_format_config().get("SPORT_CONSTANTS")
        if not isinstance(raw_constants, dict) or not raw_constants:
            raise ConfigurationError
        constants: SportConstants = {}
        for key in ("percent_scale", "all_out_wickets", "balls_per_over"):
            if key in raw_constants:
                constants[key] = int(raw_constants[key])
        return constants

    def _sport_constant(self, key: str) -> int:
        constants = self._require_sport_constants()
        if key not in constants:
            raise ConfigurationError(f"Missing SPORT_CONSTANTS key '{key}' in FORMAT_RULES['SPORT_CONSTANTS'].")
        return int(constants[key])

    def _resolved_team_form_limit(self, match_context: TeamMatchContext, limit_value: int) -> int:
        return limit_value if limit_value > 0 else self._threshold(match_context, "form_window_matches")
