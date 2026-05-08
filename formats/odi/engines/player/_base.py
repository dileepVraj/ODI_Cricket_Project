"""formats/odi/engines/player/_base — PlayerEngineBase: config loading and runtime accessors."""

from typing import Dict, Optional, cast

import logging

import pandas as pd

from core.calculators import MatchupEngine
from core.exceptions import ConfigurationError
from core.interfaces.player_interface import IPlayerEngine
from core.interfaces.player_types import FormatRulesMap
from core.interfaces.serialization_types import ManifestFunctionDef
from core.interfaces.team_types import DataAccessPort
from core.services.squad import SquadService


_PHASE_CANONICAL: Dict[str, str] = {
    "powerplay": "pp",
    "pp": "pp",
    "middle": "mid",
    "mid": "mid",
    "death": "dth",
    "dth": "dth",
}


_PURE_BOWLER_ROLE: str = "Bowler"

_logger = logging.getLogger(__name__)


class _PlayerConfigMixin:
    """Config loading and validation helpers used by PlayerEngineBase."""

    rules: dict[str, object]

    def _require_nonempty_dict_rule(self, key: str) -> ManifestFunctionDef:
        raw_value = self.rules.get(key)
        if not isinstance(raw_value, dict) or not raw_value:
            raise ConfigurationError(
                f"Missing required format rule '{key}'. "
                "Define it in manifest FORMAT_RULES and pass it into PlayerEngine."
            )
        return cast(ManifestFunctionDef, raw_value)

    def _coerce_dict_values_to_int(
        self,
        raw: Dict[str, int | float | str],
        context_key: str,
    ) -> Dict[str, int | float]:
        """Coerce all values in a string-keyed dict to numeric scalars."""
        normalized: Dict[str, int | float] = {}
        for key, value in raw.items():
            try:
                numeric_value = float(value)
            except (TypeError, ValueError) as exc:
                raise ConfigurationError(
                    f"Invalid {context_key} '{key}': {value!r}. Expected integer."
                ) from exc
            normalized[str(key)] = int(numeric_value) if numeric_value.is_integer() else numeric_value
        return normalized

    def _require_tactical_thresholds(self) -> Dict[str, int | float]:
        thresholds = cast(
            Dict[str, int | float | str],
            self._require_nonempty_dict_rule("tactical_thresholds"),
        )
        return self._coerce_dict_values_to_int(thresholds, "tactical threshold")

    def _require_style_map(self) -> Dict[str, str]:
        style_map = self._require_nonempty_dict_rule("style_map")
        return {str(k): str(v) for k, v in style_map.items()}

    def _require_player_roles(self) -> Dict[str, str]:
        role_map = self._require_nonempty_dict_rule("player_roles")
        return {str(k): str(v) for k, v in role_map.items()}

    def _require_default_player_role(self) -> str:
        raw_value = self.rules.get("default_player_role")
        if not isinstance(raw_value, str) or not raw_value.strip():
            raise ConfigurationError(
                "Missing required format rule 'default_player_role'. "
                "Define it in manifest FORMAT_RULES and pass it into PlayerEngine."
            )
        return raw_value.strip()

    def _coerce_positive_int_rule(self, raw_value: int | str, rule_name: str) -> int:
        """Coerce a raw rule value to a positive integer."""
        try:
            coerced = int(raw_value)
        except (TypeError, ValueError) as exc:
            raise ConfigurationError(
                f"Invalid format rule '{rule_name}': {raw_value!r}"
            ) from exc
        if coerced <= 0:
            raise ConfigurationError(f"Format rule '{rule_name}' must be > 0.")
        return coerced

    def _require_default_years_window(self) -> int:
        raw_value = self.rules.get("default_years_window")
        if raw_value is None:
            raise ConfigurationError(
                "Missing required format rule 'default_years_window'. "
                "Define it in manifest FORMAT_RULES and pass it into PlayerEngine."
            )
        return self._coerce_positive_int_rule(
            cast(int | str, raw_value),
            "default_years_window",
        )

    def _require_engine_defaults(self) -> Dict[str, int | float]:
        defaults = cast(
            Dict[str, int | float | str],
            self._require_nonempty_dict_rule("engine_defaults"),
        )
        return self._coerce_dict_values_to_int(defaults, "engine default")


class PlayerEngineBase(_PlayerConfigMixin, IPlayerEngine):
    def __init__(
        self,
        player_df: pd.DataFrame,
        meta_df: pd.DataFrame,
        squads_df: Optional[pd.DataFrame] = None,
        dal: Optional[DataAccessPort] = None,
        format_rules: Optional[FormatRulesMap] = None,
    ) -> None:
        _ = dal  # Backward-compatible parameter; DAL access is forbidden in PlayerEngine.
        self.rules = format_rules or {}
        self.tactical_thresholds = self._require_tactical_thresholds()
        self.style_map = self._require_style_map()
        self.player_roles = self._require_player_roles()
        self.default_player_role = self._require_default_player_role()
        self.default_years_window = self._require_default_years_window()
        self.engine_defaults = self._require_engine_defaults()
        self.squad_service = self._create_squad_service()
        self.matchup_engine = self._create_matchup_engine()
        self.raw_df = None  # Deprecated in v5.0
        self._reference_date = None
        
        self.player_df = player_df
        self.meta_df = meta_df
        self.squads_df = self._normalise_squads_df(squads_df)

    def _create_squad_service(self) -> SquadService:
        """Factory: create the SquadService for this engine instance."""
        return SquadService(format_rules=self.rules)

    def _create_matchup_engine(self) -> MatchupEngine:
        """Factory: create the MatchupEngine for this engine instance."""
        return MatchupEngine(format_rules=self.rules)

    def _normalise_squads_df(self, squads_df: Optional[pd.DataFrame]) -> pd.DataFrame:
        """Normalise squads_df: apply default columns and coerce match_id dtype."""
        df = squads_df if squads_df is not None else pd.DataFrame(
            columns=['match_id', 'player', 'date', 'team']
        )
        if not df.empty:
            df['match_id'] = df['match_id'].astype(str)
        return df

    def _get_player_role(self, player_name: str) -> str:
        """Returns the role of a player from config or default."""
        return self.player_roles.get(player_name, self.default_player_role)

    def _compute_reference_date(self) -> pd.Timestamp:
        """Use latest available ball date to stabilize lookbacks."""
        rule_date = self.rules.get("reference_date")
        if rule_date is not None:
            try:
                parsed = pd.Timestamp(rule_date)
                if pd.notna(parsed):
                    return parsed.floor('D')
            except (TypeError, ValueError):
                pass
        return pd.Timestamp.now().floor('D')

    def _get_reference_date(self) -> pd.Timestamp:
        if not self._is_reference_date_cached():
            self._reference_date = self._compute_reference_date()
        return self._reference_date

    def _is_reference_date_cached(self) -> bool:
        return getattr(self, '_reference_date', None) is not None

    def _get_years_back(self, years: Optional[int]) -> int:
        if years is None:
            return self.default_years_window
        try:
            years_back = int(years)
        except (TypeError, ValueError) as exc:
            raise ConfigurationError(f"Invalid years value: {years!r}") from exc
        if years_back <= 0:
            raise ConfigurationError("years must be > 0.")
        return years_back

    def _get_tactical_threshold(self, key: str) -> int | float:
        if key not in self.tactical_thresholds:
            raise ConfigurationError(
                f"Missing tactical threshold '{key}' in FORMAT_RULES['tactical_thresholds']."
            )
        raw_value = self.tactical_thresholds[key]
        try:
            numeric_value = float(raw_value)
        except (TypeError, ValueError) as exc:
            raise ConfigurationError(
                f"Invalid tactical threshold '{key}': {raw_value!r}"
            ) from exc
        return int(numeric_value) if numeric_value.is_integer() else numeric_value

    def _get_engine_default(self, key: str) -> int:
        if key not in self.engine_defaults:
            raise ConfigurationError(
                f"Missing engine default '{key}' in FORMAT_RULES['engine_defaults']."
            )
        raw_value = self.engine_defaults[key]
        try:
            return int(raw_value)
        except (TypeError, ValueError) as exc:
            raise ConfigurationError(
                f"Invalid engine default '{key}': {raw_value!r}"
            ) from exc


