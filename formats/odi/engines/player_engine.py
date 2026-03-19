from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from config.shared.venues import get_venue_aliases
import re
from core.calculators import MatchupEngine
from core.exceptions import ConfigurationError
from core.services.report_formatter import ReportFormatter
from core.services.squad_service import SquadService
from core.interfaces.player_interface import (
    BattingStats,
    BowlingStats,
    ContextStats,
    IPlayerEngine,
    PhaseBowlingRow,
    PhaseRunsRow,
    PlayerProfile,
    SquadComparisonData,
    VsBowlingStyleRow,
)
from core.interfaces.team_types import (
    DataAccessPort,
    DisplayRecord,
    FormatRulesMap,
    ManifestFunctionDef,
    SquadComparisonPayload,
    TacticalRecorderPort,
)


_PHASE_CANONICAL: Dict[str, str] = {
    "powerplay": "pp",
    "pp": "pp",
    "middle": "mid",
    "mid": "mid",
    "death": "dth",
    "dth": "dth",
}


_PURE_BOWLER_ROLE: str = "Bowler"


class PlayerEngine(IPlayerEngine):
    """
    The Dugout (v6.0 - Engineering Standards Aligned).
    - HEADLESS: Logic returning pure data.
    - TYPED: Full Type Hint signatures.
    - DECOUPLED: Renderers handle the UI.
    """
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
        self.squad_service = SquadService(format_rules=self.rules)
        self.matchup_engine = MatchupEngine(format_rules=self.rules)
        self.raw_df = None  # Deprecated in v5.0
        
        self.player_df = player_df
        self.meta_df = meta_df
        self.squads_df = self._normalise_squads_df(squads_df)

    def _normalise_squads_df(self, squads_df: Optional[pd.DataFrame]) -> pd.DataFrame:
        """Normalise squads_df: apply default columns and coerce match_id dtype."""
        df = squads_df if squads_df is not None else pd.DataFrame(
            columns=['match_id', 'player', 'date', 'team']
        )
        if not df.empty:
            df['match_id'] = df['match_id'].astype(str)
        return df

    def _require_nonempty_dict_rule(self, key: str) -> ManifestFunctionDef:
        raw_value = self.rules.get(key)
        if not isinstance(raw_value, dict) or not raw_value:
            raise ConfigurationError(
                f"Missing required format rule '{key}'. "
                "Define it in manifest FORMAT_RULES and pass it into PlayerEngine."
            )
        return raw_value

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
        thresholds = self._require_nonempty_dict_rule("tactical_thresholds")
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
        return self._coerce_positive_int_rule(raw_value, "default_years_window")

    def _require_engine_defaults(self) -> Dict[str, int]:
        defaults = self._require_nonempty_dict_rule("engine_defaults")
        return self._coerce_dict_values_to_int(defaults, "engine default")

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


    def get_active_squad(self, team_name: str) -> List[str]:
        """
        Retrieves the list of active players for a team from the metadata.
        """
        if self.meta_df.empty: return []
        team_players = self.meta_df[self.meta_df['team'].str.lower() == team_name.lower()]
        return sorted(team_players['player'].unique().tolist())
        
    def get_last_match_xi(
        self,
        team_name: str,
        team_matches: Optional[pd.DataFrame] = None,
        match_balls_df: Optional[pd.DataFrame] = None,
        opponent: Optional[str] = None,
    ) -> List[str]:
        """
        Retrieves players from the last match using Squads DB (preferred) or
        pre-fetched match/ball data.
        """
        opponent_norm = str(opponent).strip() if opponent else ""
        last_xi_match_limit = int(self.rules["player_rules"]["last_xi_match_limit"])

        # 1. Try Squads DB First
        if not self.squads_df.empty:
            team_rows = self.squads_df[self.squads_df['team'] == team_name]
            if opponent_norm:
                opponent_match_ids = self.squads_df.loc[
                    self.squads_df['team'] == opponent_norm, 'match_id'
                ].astype(str)
                team_rows = team_rows[team_rows['match_id'].isin(opponent_match_ids)]
            if not team_rows.empty:
                dates = team_rows.sort_values('date', ascending=False)
                last_match_id = str(dates.iloc[0]['match_id'])
                last_match_rows = team_rows[team_rows['match_id'] == last_match_id]
                player_sequence_columns = [
                    column_name
                    for column_name in last_match_rows.columns
                    if column_name != 'player'
                    and column_name.startswith('player')
                    and pd.api.types.is_numeric_dtype(last_match_rows[column_name])
                ]
                if 'is_playing_xi' in last_match_rows.columns:
                    confirmed_xi_rows = last_match_rows[last_match_rows['is_playing_xi'] == True]
                    if len(confirmed_xi_rows) < last_xi_match_limit:
                        supplemental_rows = last_match_rows[
                            ~last_match_rows['player'].isin(confirmed_xi_rows['player'])
                        ]
                        if player_sequence_columns:
                            supplemental_rows = supplemental_rows.sort_values(
                                player_sequence_columns[0]
                            )
                        supplement_count = last_xi_match_limit - len(confirmed_xi_rows)
                        last_match_rows = pd.concat(
                            [confirmed_xi_rows, supplemental_rows.head(supplement_count)]
                        )
                    else:
                        last_match_rows = confirmed_xi_rows
                if player_sequence_columns:
                    ordered_rows = last_match_rows.sort_values(player_sequence_columns[0])
                    return ordered_rows['player'].dropna().tolist()
                return last_match_rows['player'].dropna().tolist()

        # 2. Fallback to pre-fetched raw data (provided by API/Facade layer)
        if team_matches is None or team_matches.empty:
            return []

        balls_source = match_balls_df if match_balls_df is not None else pd.DataFrame()
        if not balls_source.empty and 'match_id' in balls_source.columns:
            balls_source = balls_source.assign(match_id=balls_source['match_id'].astype(str))

        filtered_matches = team_matches
        if opponent_norm:
            candidate_columns = [
                column_name
                for column_name in ['team_a', 'team_b', 'home_team', 'away_team']
                if column_name in team_matches.columns
            ]
            if candidate_columns:
                team_mask = pd.Series(False, index=team_matches.index)
                opponent_mask = pd.Series(False, index=team_matches.index)
                for column_name in candidate_columns:
                    column_values = team_matches[column_name].astype(str)
                    team_mask = team_mask | (column_values == team_name)
                    opponent_mask = opponent_mask | (column_values == opponent_norm)
                head_to_head_matches = team_matches[team_mask & opponent_mask]
                if not head_to_head_matches.empty:
                    filtered_matches = head_to_head_matches

        sorted_matches = filtered_matches.sort_values('start_date', ascending=False)['match_id'].astype(str).unique()
        backscan_limit = self._get_engine_default("squad_backscan_match_limit")

        for match_id in sorted_matches[:backscan_limit]:
            if balls_source.empty:
                continue
            match_data = balls_source[balls_source['match_id'] == match_id]
            if match_data.empty:
                continue
            order_columns = [
                column_name
                for column_name in ['over_num', 'ball']
                if column_name in match_data.columns
            ]
            ordered_match_data = (
                match_data.sort_values(order_columns)
                if order_columns
                else match_data
            )
            batting_rows = ordered_match_data[ordered_match_data['batting_team'] == team_name]
            bowling_rows = ordered_match_data[ordered_match_data['bowling_team'] == team_name]
            striker_order = batting_rows['striker'].dropna().drop_duplicates().tolist()
            non_striker_order = batting_rows['non_striker'].dropna().drop_duplicates().tolist()
            bowler_order = bowling_rows['bowler'].dropna().drop_duplicates().tolist()
            return list(dict.fromkeys([*striker_order, *non_striker_order, *bowler_order]))

        return []

    def _build_squad_context_df(
        self,
        context_df: Optional[pd.DataFrame],
        cutoff_date: pd.Timestamp,
    ) -> pd.DataFrame:
        squad_context_df = context_df.copy() if isinstance(context_df, pd.DataFrame) else pd.DataFrame()
        if not squad_context_df.empty and 'start_date' in squad_context_df.columns:
            squad_context_df['start_date'] = pd.to_datetime(
                squad_context_df['start_date'], errors='coerce'
            )
            squad_context_df = squad_context_df[squad_context_df['start_date'] >= cutoff_date]
        return squad_context_df

    def get_squad_comparison_data(
        self,
        team_a_name: str,
        team_a_players: List[str],
        team_b_name: str,
        team_b_players: List[str],
        venue_id: str,
        years: Optional[int] = None,
        *,
        context_df: pd.DataFrame,
    ) -> SquadComparisonData:
        """
        Headless API: Fetches all data required for a Squad Comparison.
        Returns: SquadComparisonData Dataclass.
        """
        # 1. OPTIMIZATION: Create Squad Context Subset
        years_back = self._get_years_back(years)
        cutoff_date = self._get_reference_date() - pd.DateOffset(years=years_back)
        squad_context_df = self._build_squad_context_df(context_df, cutoff_date)
        
        # 2. VENUE PATTERN
        aliases = get_venue_aliases(venue_id)
        if "_" in venue_id:
            suffix_key = venue_id.split("_", 1)[1] 
            suffix_aliases = get_venue_aliases(suffix_key)
            if suffix_aliases:
                aliases = list(set(aliases + suffix_aliases))
        venue_pattern = '|'.join([re.escape(v) for v in aliases if v])

        # 3. BULK TEAM METRICS + PLAYER TABLES (Vectorized Service)
        team_a_bundle = self.squad_service.get_bulk_metrics(
            base_df=squad_context_df,
            player_ids=team_a_players,
            opposition=team_b_name,
            venue_pattern=venue_pattern,
            player_roles=self.player_roles,
        )
        team_b_bundle = self.squad_service.get_bulk_metrics(
            base_df=squad_context_df,
            player_ids=team_b_players,
            opposition=team_a_name,
            venue_pattern=venue_pattern,
            player_roles=self.player_roles,
        )
        metrics_a = team_a_bundle["squad_metrics"]
        metrics_b = team_b_bundle["squad_metrics"]
        player_stats_a = ReportFormatter.format_squad_player_stats(team_a_bundle["player_stats"])
        player_stats_b = ReportFormatter.format_squad_player_stats(team_b_bundle["player_stats"])

        return SquadComparisonData(
            team_a_name=team_a_name,
            team_b_name=team_b_name,
            metrics_a=metrics_a,
            metrics_b=metrics_b,
            player_stats_a=player_stats_a,
            player_stats_b=player_stats_b,
            venue_id=venue_id,
            years=years_back
        )

    def compare_squads(
        self,
        team_a_name: str,
        team_a_players: List[str],
        team_b_name: str,
        team_b_players: List[str],
        venue_id: str,
        years: Optional[int] = None,
        recorder: Optional[TacticalRecorderPort] = None,
        *,
        context_df: pd.DataFrame,
    ) -> SquadComparisonData:
        """
        Headless API: Orchestrates squad comparison logic.
        (Note: UI rendering has been moved to PlayerHTMLRenderer)
        """
        return self.get_squad_comparison_data(
            team_a_name,
            team_a_players,
            team_b_name,
            team_b_players,
            venue_id,
            years,
            context_df=context_df,
        )

    # --- NEW: ARCHETYPE ANALYSIS ---
    def analyze_squad_types(
        self,
        team_name: str,
        players: List[str],
        opposition_bowlers: List[str],
        years: Optional[int] = None,
        recorder: Optional[TacticalRecorderPort] = None,
        *,
        context_df: pd.DataFrame,
    ) -> List[DisplayRecord]:
        """
        Headless logic for Tactical Breakdown.
        Returns: List of Dicts (Table Data).
        """
        years_back = self._get_years_back(years)
        cutoff_date = self._get_reference_date() - pd.DateOffset(years=years_back)
        base_df = context_df

        if base_df.empty:
            return []

        if 'start_date' in base_df.columns:
            if not pd.api.types.is_datetime64_any_dtype(base_df['start_date']):
                base_df = base_df.copy()
                base_df.loc[:, 'start_date'] = pd.to_datetime(base_df['start_date'], errors='coerce')
            window_df = base_df[base_df['start_date'] >= cutoff_date]
        else:
            window_df = base_df

        if window_df.empty:
            return []

        semantic_rows = self.matchup_engine.analyze_types(
            player_df=window_df,
            style_map=self.style_map,
            players=players,
            opposition_bowlers=opposition_bowlers,
            player_roles=self.player_roles,
        )
        table_data = ReportFormatter.format_tactical_matrix(semantic_rows)

        if recorder and semantic_rows:
            weakness_avg_max = self._get_tactical_threshold("structural_weakness_avg_max")
            dominance_avg_min = self._get_tactical_threshold("dominant_matchup_avg_min")
            for row in semantic_rows:
                player_name = str(row.get("player_name") or "")
                style_metrics = row.get("style_metrics", {})
                if not isinstance(style_metrics, dict):
                    continue
                for style, metric in style_metrics.items():
                    if not isinstance(metric, dict):
                        continue
                    avg_value = metric.get("average_raw")
                    if avg_value is None:
                        continue
                    try:
                        avg_float = float(avg_value)
                    except (TypeError, ValueError):
                        continue
                    if avg_float < weakness_avg_max:
                        recorder.log_tactical_alert(
                            "STRUCTURAL_WEAKNESS",
                            f"{player_name} struggles vs {style} (Avg {avg_float})",
                        )
                    if avg_float > dominance_avg_min:
                        recorder.log_tactical_alert(
                            "DOMINANT_MATCHUP",
                            f"{player_name} dominates {style} (Avg {avg_float})",
                        )

        return table_data

    def analyze_dual_squad_matrix(
        self,
        team_a_name: str,
        team_a_players: List[str],
        team_b_name: str,
        team_b_players: List[str],
        years: Optional[int] = None,
        *,
        context_df: pd.DataFrame,
    ) -> List[DisplayRecord]:
        rows_a = self.analyze_squad_types(
            team_name=team_a_name,
            players=team_a_players,
            opposition_bowlers=team_b_players,
            years=years,
            context_df=context_df,
        )
        rows_b = self.analyze_squad_types(
            team_name=team_b_name,
            players=team_b_players,
            opposition_bowlers=team_a_players,
            years=years,
            context_df=context_df,
        )
        team_a_rows: List[DisplayRecord] = [{"Team": team_a_name, **row} for row in rows_a]
        team_b_rows: List[DisplayRecord] = [{"Team": team_b_name, **row} for row in rows_b]
        return team_a_rows + team_b_rows


    # --- HELPERS ---

    def get_matchups(
        self,
        batter: Optional[str] = None,
        bowlers: Optional[List[str]] = None,
        *,
        home_team: Optional[str] = None,
        opp_team: Optional[str] = None,
        home_xi: Optional[List[str]] = None,
        away_xi: Optional[List[str]] = None,
        context_df: pd.DataFrame,
    ) -> List[DisplayRecord]:
        """
        Public dispatcher for Player Matchups.
        Single-player mode: batter is provided - delegates to _matchup_single_batter.
        Bulk mode: batter is None - iterates all non-Bowler players in home_xi against away_xi,
        returning combined rows with a leading 'Batter' key per row.
        """
        if batter:
            return self._matchup_single_batter(
                batter,
                bowlers,
                home_team=home_team,
                opp_team=opp_team,
                home_xi=home_xi,
                away_xi=away_xi,
                context_df=context_df,
            )

        home_players: List[str] = list(home_xi or [])
        away_players: List[str] = list(away_xi or [])
        if not home_players or not away_players:
            return []

        eligible_home: List[str] = [
            player_name
            for player_name in home_players
            if self._get_player_role(player_name) != _PURE_BOWLER_ROLE
        ]
        eligible_away: List[str] = [
            player_name
            for player_name in away_players
            if self._get_player_role(player_name) != _PURE_BOWLER_ROLE
        ]
        if not eligible_home and not eligible_away:
            return []

        combined: List[DisplayRecord] = []
        for player_name in eligible_home:
            rows = self._matchup_single_batter(
                player_name,
                away_players,
                home_team=home_team,
                opp_team=opp_team,
                home_xi=home_xi,
                away_xi=away_xi,
                context_df=context_df,
            )
            for row in rows:
                combined.append({"Batter": player_name, **row})
        for player_name in eligible_away:
            rows = self._matchup_single_batter(
                player_name,
                home_players,
                home_team=home_team,
                opp_team=opp_team,
                home_xi=home_xi,
                away_xi=away_xi,
                context_df=context_df,
            )
            for row in rows:
                combined.append({"Batter": player_name, **row})
        return combined

    def _compute_threat_rating(
        self,
        raw_balls: pd.Series,
        raw_outs: pd.Series,
        w_avg: pd.Series,
        w_sr: pd.Series,
        threat_min_balls: int | float,
        threat_dominant_balls: int | float,
        threat_dominant_sr: int | float,
        threat_threat_sr_outs0: int | float,
        threat_threat_avg_outs1: int | float,
        threat_threat_sr_outs1: int | float,
        threat_advantage_sr: int | float,
        threat_advantage_avg: int | float,
        threat_watchful_avg: int | float,
        threat_watchful_sr: int | float,
        threat_dominated_outs: int | float,
        threat_dominated_avg: int | float,
        threat_bunny_outs: int | float,
        threat_bunny_avg: int | float,
    ) -> pd.Series:
        conditions = [
            raw_balls == 0,
            raw_balls < float(threat_min_balls),
            (raw_outs >= float(threat_bunny_outs)) & (w_avg < float(threat_bunny_avg)),
            (raw_outs >= float(threat_dominated_outs)) & (w_avg < float(threat_dominated_avg)),
            (raw_outs >= 1) & (w_avg < float(threat_watchful_avg)) & (w_sr < float(threat_watchful_sr)),
            (raw_balls >= float(threat_dominant_balls))
            & (raw_outs == 0)
            & (w_sr > float(threat_dominant_sr)),
            (
                ((raw_outs == 0) & (w_sr > float(threat_threat_sr_outs0)))
                | (
                    (raw_outs == 1)
                    & (w_avg > float(threat_threat_avg_outs1))
                    & (w_sr > float(threat_threat_sr_outs1))
                )
            ),
            (raw_outs <= 1)
            & (w_sr > float(threat_advantage_sr))
            & ((raw_outs == 0) | (w_avg > float(threat_advantage_avg))),
        ]
        choices = [
            "NEW MATCHUP",
            "LOW DATA",
            "BUNNY",
            "DOMINATED",
            "WATCHFUL",
            "DOMINANT",
            "THREAT",
            "ADVANTAGE",
        ]
        return pd.Series(
            np.select(conditions, choices, default="CONTESTED"),
            index=raw_balls.index,
        )

    def _matchup_single_batter(
        self,
        batter: str,
        bowlers: Optional[List[str]] = None,
        *,
        home_team: Optional[str] = None,
        opp_team: Optional[str] = None,
        home_xi: Optional[List[str]] = None,
        away_xi: Optional[List[str]] = None,
        context_df: pd.DataFrame,
    ) -> List[DisplayRecord]:
        """
        Headless logic for Batter vs Bowlers.
        """
        threat_min_balls = self._get_tactical_threshold("threat_min_balls")
        threat_dominant_balls = self._get_tactical_threshold("threat_dominant_balls")
        threat_dominant_sr = self._get_tactical_threshold("threat_dominant_sr")
        threat_threat_sr_outs0 = self._get_tactical_threshold("threat_threat_sr_outs0")
        threat_threat_avg_outs1 = self._get_tactical_threshold("threat_threat_avg_outs1")
        threat_threat_sr_outs1 = self._get_tactical_threshold("threat_threat_sr_outs1")
        threat_advantage_sr = self._get_tactical_threshold("threat_advantage_sr")
        threat_advantage_avg = self._get_tactical_threshold("threat_advantage_avg")
        threat_watchful_avg = self._get_tactical_threshold("threat_watchful_avg")
        threat_watchful_sr = self._get_tactical_threshold("threat_watchful_sr")
        threat_dominated_outs = self._get_tactical_threshold("threat_dominated_outs")
        threat_dominated_avg = self._get_tactical_threshold("threat_dominated_avg")
        threat_bunny_outs = self._get_tactical_threshold("threat_bunny_outs")
        threat_bunny_avg = self._get_tactical_threshold("threat_bunny_avg")
        recency_w_0_12 = self._get_tactical_threshold("recency_w_0_12")
        recency_w_12_24 = self._get_tactical_threshold("recency_w_12_24")
        recency_w_24_36 = self._get_tactical_threshold("recency_w_24_36")
        recency_w_36_plus = self._get_tactical_threshold("recency_w_36_plus")
        confidence_2_min = self._get_tactical_threshold("confidence_2_min")
        confidence_3_min = self._get_tactical_threshold("confidence_3_min")
        confidence_4_min = self._get_tactical_threshold("confidence_4_min")
        confidence_5_min = self._get_tactical_threshold("confidence_5_min")
        percent_scale = float(self.rules["SPORT_CONSTANTS"]["percent_scale"])

        inferred_bowlers: List[str] = list(bowlers or [])
        home_xi = home_xi or []
        away_xi = away_xi or []

        if not inferred_bowlers:
            if home_xi and away_xi:
                if batter in home_xi:
                    inferred_bowlers = away_xi
                elif batter in away_xi:
                    inferred_bowlers = home_xi
                else:
                    inferred_bowlers = away_xi
            elif away_xi:
                inferred_bowlers = away_xi
            elif home_xi:
                inferred_bowlers = home_xi

        inferred_bowlers = sorted({
            str(name).strip()
            for name in inferred_bowlers
            if str(name).strip() and str(name).strip() != batter
        })
        if not inferred_bowlers:
            return []

        base_df = context_df
        required_cols = {"striker", "bowler", "runs_off_bat", "player_dismissed"}
        if not required_cols.issubset(set(base_df.columns)):
            return []

        batter_df = base_df[
            (base_df["striker"] == batter)
            & (base_df["bowler"].isin(inferred_bowlers))
        ].copy()
        if batter_df.empty:
            return []

        batter_df["_runs_off_bat_num"] = pd.to_numeric(
            batter_df["runs_off_bat"], errors="coerce"
        ).fillna(0.0)
        batter_df["_is_out"] = (batter_df["player_dismissed"] == batter).astype(int)

        if "start_date" not in batter_df.columns:
            batter_df["_weight"] = 1.0
        else:
            reference_date = self._get_reference_date()
            days_ago = (
                reference_date - pd.to_datetime(batter_df["start_date"], errors="coerce")
            ).dt.days
            batter_df["_weight"] = np.select(
                [
                    days_ago <= 365,
                    days_ago <= 730,
                    days_ago <= 1095,
                ],
                [
                    float(recency_w_0_12),
                    float(recency_w_12_24),
                    float(recency_w_24_36),
                ],
                default=float(recency_w_36_plus),
            ).astype(float)

        batter_df["_weighted_runs"] = batter_df["_runs_off_bat_num"] * batter_df["_weight"]
        batter_df["_weighted_outs"] = batter_df["_is_out"].astype(float) * batter_df["_weight"]

        def _aggregate_matchup_window(window_df: pd.DataFrame) -> pd.DataFrame:
            if window_df.empty:
                return pd.DataFrame(
                    columns=[
                        "Bowler",
                        "Balls",
                        "Runs",
                        "Outs",
                        "Avg",
                        "SR",
                        "ThreatRating",
                    ]
                )

            grouped = window_df.groupby("bowler", sort=True, dropna=False)
            matchup_stats = grouped.agg(
                Runs=("_runs_off_bat_num", "sum"),
                Outs=("_is_out", "sum"),
                WeightedBalls=("_weight", "sum"),
                WeightedRuns=("_weighted_runs", "sum"),
                WeightedOuts=("_weighted_outs", "sum"),
            )
            matchup_stats["Balls"] = grouped.size()
            matchup_stats["Avg"] = np.where(
                matchup_stats["Outs"] > 0,
                matchup_stats["WeightedRuns"] / matchup_stats["WeightedOuts"],
                matchup_stats["WeightedRuns"],
            )
            matchup_stats["SR"] = np.where(
                matchup_stats["WeightedBalls"] > 0,
                (matchup_stats["WeightedRuns"] / matchup_stats["WeightedBalls"]) * percent_scale,
                0.0,
            )
            matchup_stats["ThreatRating"] = self._compute_threat_rating(
                raw_balls=matchup_stats["Balls"].astype(float),
                raw_outs=matchup_stats["Outs"].astype(float),
                w_avg=matchup_stats["Avg"].astype(float),
                w_sr=matchup_stats["SR"].astype(float),
                threat_min_balls=threat_min_balls,
                threat_dominant_balls=threat_dominant_balls,
                threat_dominant_sr=threat_dominant_sr,
                threat_threat_sr_outs0=threat_threat_sr_outs0,
                threat_threat_avg_outs1=threat_threat_avg_outs1,
                threat_threat_sr_outs1=threat_threat_sr_outs1,
                threat_advantage_sr=threat_advantage_sr,
                threat_advantage_avg=threat_advantage_avg,
                threat_watchful_avg=threat_watchful_avg,
                threat_watchful_sr=threat_watchful_sr,
                threat_dominated_outs=threat_dominated_outs,
                threat_dominated_avg=threat_dominated_avg,
                threat_bunny_outs=threat_bunny_outs,
                threat_bunny_avg=threat_bunny_avg,
            )
            matchup_stats["Runs"] = matchup_stats["Runs"].round(0)
            matchup_stats["Avg"] = matchup_stats["Avg"].round(1)
            matchup_stats["SR"] = matchup_stats["SR"].round(1)
            return matchup_stats.reset_index().rename(columns={"bowler": "Bowler"})[
                ["Bowler", "Balls", "Runs", "Outs", "Avg", "SR", "ThreatRating"]
            ]

        def _build_phase_stats(phase_key: str, prefix: str, overall_df: pd.DataFrame) -> pd.DataFrame:
            phase_output = overall_df[["Bowler"]].copy()
            phase_output[f"{prefix}Balls"] = 0
            phase_output[f"{prefix}Runs"] = 0
            phase_output[f"{prefix}Outs"] = 0
            phase_output[f"{prefix}Avg"] = None
            phase_output[f"{prefix}SR"] = None
            phase_output[f"{prefix}ThreatRating"] = "NEW MATCHUP"

            phase_bounds = self.rules["phases"].get(phase_key)
            if "over_num" not in batter_df.columns or phase_bounds is None:
                return phase_output

            over_num = pd.to_numeric(batter_df["over_num"], errors="coerce")
            phase_df = batter_df[over_num.between(int(phase_bounds[0]), int(phase_bounds[1]))]
            if phase_df.empty:
                return phase_output

            aggregated = _aggregate_matchup_window(phase_df).rename(
                columns={
                    "Balls": f"{prefix}Balls",
                    "Runs": f"{prefix}Runs",
                    "Outs": f"{prefix}Outs",
                    "Avg": f"{prefix}Avg",
                    "SR": f"{prefix}SR",
                    "ThreatRating": f"{prefix}ThreatRating",
                }
            )
            phase_output = phase_output.drop(
                columns=[
                    f"{prefix}Balls",
                    f"{prefix}Runs",
                    f"{prefix}Outs",
                    f"{prefix}Avg",
                    f"{prefix}SR",
                    f"{prefix}ThreatRating",
                ]
            ).merge(aggregated, how="left", on="Bowler")
            phase_output[f"{prefix}Balls"] = phase_output[f"{prefix}Balls"].fillna(0).astype(int)
            phase_output[f"{prefix}Runs"] = phase_output[f"{prefix}Runs"].fillna(0).astype(int)
            phase_output[f"{prefix}Outs"] = phase_output[f"{prefix}Outs"].fillna(0).astype(int)
            phase_output[f"{prefix}ThreatRating"] = (
                phase_output[f"{prefix}ThreatRating"].fillna("NEW MATCHUP").astype(str)
            )
            phase_avg = pd.to_numeric(phase_output[f"{prefix}Avg"], errors="coerce").round(1)
            phase_sr = pd.to_numeric(phase_output[f"{prefix}SR"], errors="coerce").round(1)
            phase_output[f"{prefix}Avg"] = phase_avg.where(phase_output[f"{prefix}Balls"] > 0, np.nan)
            phase_output[f"{prefix}SR"] = phase_sr.where(phase_output[f"{prefix}Balls"] > 0, np.nan)
            phase_output.loc[phase_output[f"{prefix}Balls"] == 0, f"{prefix}Avg"] = None
            phase_output.loc[phase_output[f"{prefix}Balls"] == 0, f"{prefix}SR"] = None
            return phase_output

        overall = _aggregate_matchup_window(batter_df)
        overall["Style"] = overall["Bowler"].map(self.style_map).fillna("Other")
        overall["Confidence"] = np.select(
            [
                overall["Balls"] >= float(confidence_5_min),
                overall["Balls"] >= float(confidence_4_min),
                overall["Balls"] >= float(confidence_3_min),
                overall["Balls"] >= float(confidence_2_min),
            ],
            [5, 4, 3, 2],
            default=1,
        ).astype(int)

        dismissal_stats = pd.DataFrame(
            {
                "Bowler": overall["Bowler"],
                "DismissalStructural": 0,
                "DismissalCaught": 0,
                "DismissalOther": 0,
            }
        )
        if "wicket_type" in batter_df.columns:
            dismissal_df = batter_df[batter_df["_is_out"] == 1].copy()
            if not dismissal_df.empty:
                structural_mask = dismissal_df["wicket_type"].isin(["bowled", "lbw"])
                caught_mask = dismissal_df["wicket_type"].isin(["caught", "caught and bowled"])
                dismissal_df["_dismissal_structural"] = structural_mask.astype(int)
                dismissal_df["_dismissal_caught"] = caught_mask.astype(int)
                dismissal_df["_dismissal_other"] = (~(structural_mask | caught_mask)).astype(int)
                dismissal_stats = dismissal_df.groupby("bowler", sort=True, dropna=False).agg(
                    DismissalStructural=("_dismissal_structural", "sum"),
                    DismissalCaught=("_dismissal_caught", "sum"),
                    DismissalOther=("_dismissal_other", "sum"),
                ).reset_index().rename(columns={"bowler": "Bowler"})

        result = overall[
            ["Bowler", "Style", "Balls", "Runs", "Outs", "Avg", "SR", "ThreatRating", "Confidence"]
        ].copy()
        result = result.merge(dismissal_stats, how="left", on="Bowler")

        for phase_key, prefix in (
            ("powerplay", "PP_"),
            ("middle", "Mid_"),
            ("death", "Death_"),
        ):
            result = result.merge(_build_phase_stats(phase_key, prefix, overall), how="left", on="Bowler")

        result["Runs"] = result["Runs"].astype(int)
        result["Balls"] = result["Balls"].astype(int)
        result["Outs"] = result["Outs"].astype(int)
        result["Avg"] = pd.to_numeric(result["Avg"], errors="coerce").round(1).astype(float)
        result["SR"] = pd.to_numeric(result["SR"], errors="coerce").round(1).astype(float)
        result["ThreatRating"] = result["ThreatRating"].astype(str)
        result["Confidence"] = result["Confidence"].astype(int)
        result["DismissalStructural"] = result["DismissalStructural"].fillna(0).astype(int)
        result["DismissalCaught"] = result["DismissalCaught"].fillna(0).astype(int)
        result["DismissalOther"] = result["DismissalOther"].fillna(0).astype(int)
        result["IsBunny"] = result["ThreatRating"].eq("BUNNY")

        return result[
            [
                "Bowler",
                "Style",
                "Balls",
                "Runs",
                "Outs",
                "Avg",
                "SR",
                "ThreatRating",
                "Confidence",
                "DismissalStructural",
                "DismissalCaught",
                "DismissalOther",
                "PP_Balls",
                "PP_Runs",
                "PP_Outs",
                "PP_Avg",
                "PP_SR",
                "PP_ThreatRating",
                "Mid_Balls",
                "Mid_Runs",
                "Mid_Outs",
                "Mid_Avg",
                "Mid_SR",
                "Mid_ThreatRating",
                "Death_Balls",
                "Death_Runs",
                "Death_Outs",
                "Death_Avg",
                "Death_SR",
                "Death_ThreatRating",
                "IsBunny",
            ]
        ].to_dict("records")

    def _generate_comparison_payload(
        self,
        team_a_name: str,
        team_a_players: List[str],
        team_b_name: str,
        team_b_players: List[str],
        venue_id: str,
        years: Optional[int] = None,
        context_df: Optional[pd.DataFrame] = None,
    ) -> SquadComparisonPayload:
        """
        REGRESSION HELPER: Payload for validation.
        """
        years_back = self._get_years_back(years)
        aliases = get_venue_aliases(venue_id)
        venue_pattern = '|'.join([re.escape(v) for v in aliases if v])
        cutoff_date = self._get_reference_date() - pd.DateOffset(years=years_back)
        squad_context_df = self._build_squad_context_df(context_df, cutoff_date)
        team_a_bundle = self.squad_service.get_bulk_metrics(
            base_df=squad_context_df,
            player_ids=team_a_players,
            opposition=team_b_name,
            venue_pattern=venue_pattern,
            player_roles=self.player_roles,
        )
        team_b_bundle = self.squad_service.get_bulk_metrics(
            base_df=squad_context_df,
            player_ids=team_b_players,
            opposition=team_a_name,
            venue_pattern=venue_pattern,
            player_roles=self.player_roles,
        )
        squad_a = team_a_bundle["squad_metrics"]
        squad_b = team_b_bundle["squad_metrics"]
        matrix_a = self.analyze_squad_types(
            team_a_name, team_a_players, team_b_players, years_back, context_df=squad_context_df
        )
        matrix_b = self.analyze_squad_types(
            team_b_name, team_b_players, team_a_players, years_back, context_df=squad_context_df
        )

        matchups_a = {}
        for p in team_a_players:
            m_data = self._matchup_single_batter(p, team_b_players, context_df=squad_context_df)
            if m_data: matchups_a[p] = m_data
            
        matchups_b = {}
        for p in team_b_players:
            m_data = self._matchup_single_batter(p, team_a_players, context_df=squad_context_df)
            if m_data: matchups_b[p] = m_data

        return {
            "SquadComparison": {
                team_a_name: squad_a,
                team_b_name: squad_b,
            },
            "TacticalMatrix": {
                team_a_name: matrix_a,
                team_b_name: matrix_b,
            },
            "Matchups": {
                team_a_name: matchups_a,
                team_b_name: matchups_b,
            },
            "PlayerStats": {
                team_a_name: {
                    str(row.get("Player", "")).strip(): row
                    for row in ReportFormatter.format_squad_player_stats(team_a_bundle["player_stats"])
                    if isinstance(row, dict) and str(row.get("Player", "")).strip()
                },
                team_b_name: {
                    str(row.get("Player", "")).strip(): row
                    for row in ReportFormatter.format_squad_player_stats(team_b_bundle["player_stats"])
                    if isinstance(row, dict) and str(row.get("Player", "")).strip()
                },
            },
        }
    
    def _get_batting_milestones(self, df: pd.DataFrame) -> Tuple[int, int, int]:
        if df.empty: return 0, 0, 0
        match_sums = df.groupby('match_id')['runs_off_bat'].sum()
        centuries = (match_sums >= self.rules["player_rules"]["milestone_century"]).sum()
        fifties = (
            (match_sums >= self.rules["player_rules"]["milestone_half_century"])
            & (match_sums < self.rules["player_rules"]["milestone_century"])
        ).sum()
        hs = match_sums.max() if not match_sums.empty else 0
        return centuries, fifties, hs

    def _player_exists(self, player_name: str) -> bool:
        return player_name in self.player_df['player'].values

    def _parse_last_10_runs(self, form_last_10: List[str]) -> List[Optional[int]]:
        parsed_runs: List[Optional[int]] = []
        for token in form_last_10:
            value = str(token).strip()
            if value in {"DNB", "-"}:
                parsed_runs.append(None)
                continue
            try:
                parsed_runs.append(int(value.rstrip("*")))
            except ValueError:
                parsed_runs.append(None)
        return parsed_runs

    def _parse_last_10_bowling(self, form_last_10: List[str]) -> List[Optional[int]]:
        parsed_wickets: List[Optional[int]] = []
        for token in form_last_10:
            value = str(token).strip()
            if value == "" or value == "-" or value.upper() == "DNB":
                parsed_wickets.append(None)
                continue
            if "/" in value:
                try:
                    parsed_wickets.append(int(value.split("/", maxsplit=1)[0]))
                except ValueError:
                    parsed_wickets.append(None)
                continue
            try:
                parsed_wickets.append(int(value))
            except ValueError:
                parsed_wickets.append(None)
        return parsed_wickets

    def _compute_phase_runs(self, raw_bat: pd.DataFrame) -> List[PhaseRunsRow]:
        required_cols = {"over_num", "runs_off_bat", "player_dismissed"}
        if raw_bat.empty or not required_cols.issubset(raw_bat.columns):
            return []

        phases_cfg = self.rules.get("phases", {})
        if not isinstance(phases_cfg, dict) or not phases_cfg:
            return []

        work = raw_bat.copy()
        over_num = pd.to_numeric(work["over_num"], errors="coerce")
        conditions: List[pd.Series] = []
        labels: List[str] = []

        for phase_key, bounds in phases_cfg.items():
            if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
                continue
            start_over = pd.to_numeric(pd.Series([bounds[0]]), errors="coerce").iloc[0]
            end_over = pd.to_numeric(pd.Series([bounds[1]]), errors="coerce").iloc[0]
            if pd.isna(start_over) or pd.isna(end_over):
                continue
            canonical = _PHASE_CANONICAL.get(str(phase_key), str(phase_key))
            conditions.append(over_num.between(float(start_over), float(end_over)))
            labels.append(canonical)

        if not conditions:
            return []

        work["phase_bucket"] = np.select(conditions, labels, default="")
        work = work[work["phase_bucket"] != ""].copy()
        if work.empty:
            return []

        work["is_dismissal"] = work["player_dismissed"].notna().astype(int)
        agg = work.groupby("phase_bucket", sort=False).agg(
            total_runs=("runs_off_bat", "sum"),
            balls_faced=("runs_off_bat", "count"),
            dismissals=("is_dismissal", "sum"),
        ).reset_index()

        agg["avg_runs"] = np.where(
            agg["dismissals"] > 0,
            (agg["total_runs"] / agg["dismissals"]).round(2),
            agg["total_runs"].astype(float),
        )
        agg["strike_rate"] = np.where(
            agg["balls_faced"] > 0,
            (agg["total_runs"] / agg["balls_faced"] * 100).round(1),
            0.0,
        )

        return [
            PhaseRunsRow(
                phase=str(phase),
                total_runs=int(runs),
                balls_faced=int(balls),
                dismissals=int(dismissals),
                avg_runs=float(avg_runs),
                strike_rate=float(strike_rate),
            )
            for phase, runs, balls, dismissals, avg_runs, strike_rate in zip(
                agg["phase_bucket"],
                agg["total_runs"],
                agg["balls_faced"],
                agg["dismissals"],
                agg["avg_runs"],
                agg["strike_rate"],
            )
        ]

    def _compute_phase_bowling(self, raw_bowl: pd.DataFrame) -> List[PhaseBowlingRow]:
        required_cols = {"over_num", "runs_off_bat", "player_dismissed"}
        if raw_bowl.empty or not required_cols.issubset(raw_bowl.columns):
            return []

        phases_cfg = self.rules.get("phases", {})
        if not isinstance(phases_cfg, dict) or not phases_cfg:
            return []

        work = raw_bowl.copy()
        over_num = pd.to_numeric(work["over_num"], errors="coerce")
        conditions: List[pd.Series] = []
        labels: List[str] = []

        for phase_key, bounds in phases_cfg.items():
            if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
                continue
            start_over = pd.to_numeric(pd.Series([bounds[0]]), errors="coerce").iloc[0]
            end_over = pd.to_numeric(pd.Series([bounds[1]]), errors="coerce").iloc[0]
            if pd.isna(start_over) or pd.isna(end_over):
                continue
            canonical = _PHASE_CANONICAL.get(str(phase_key), str(phase_key))
            conditions.append(over_num.between(float(start_over), float(end_over)))
            labels.append(canonical)

        if not conditions:
            return []

        phase_order = list(dict.fromkeys(_PHASE_CANONICAL.values()))
        work["phase_bucket"] = np.select(conditions, labels, default="")
        work = work[work["phase_bucket"] != ""].copy()
        if work.empty:
            return []

        work["phase_bucket"] = pd.Categorical(
            work["phase_bucket"],
            categories=phase_order,
            ordered=True,
        )
        phase_bucket = work["phase_bucket"]
        runs_off_bat = pd.to_numeric(work["runs_off_bat"], errors="coerce").fillna(0)
        wickets = work["player_dismissed"].replace("", pd.NA).notna().astype(int)
        dot_balls = (runs_off_bat == 0).astype(int)
        boundary_balls = (runs_off_bat >= 4).astype(int)
        phase_runs = runs_off_bat.groupby(phase_bucket, observed=True, sort=True).sum()
        phase_balls = runs_off_bat.groupby(phase_bucket, observed=True, sort=True).count()
        phase_wickets = wickets.groupby(phase_bucket, observed=True, sort=True).sum()
        phase_dots = dot_balls.groupby(phase_bucket, observed=True, sort=True).sum()
        phase_boundaries = boundary_balls.groupby(phase_bucket, observed=True, sort=True).sum()
        balls_per_over = float(self.rules["SPORT_CONSTANTS"]["balls_per_over"])
        percent_scale = float(self.rules["SPORT_CONSTANTS"]["percent_scale"])
        phase_rows: List[PhaseBowlingRow] = []
        for phase in phase_order:
            total_balls = int(phase_balls.get(phase, 0))
            if total_balls <= 0:
                continue
            total_runs = int(phase_runs.get(phase, 0))
            total_wickets = int(phase_wickets.get(phase, 0))
            total_dots = int(phase_dots.get(phase, 0))
            total_boundaries = int(phase_boundaries.get(phase, 0))
            phase_rows.append(
                PhaseBowlingRow(
                    phase=phase,
                    wickets=total_wickets,
                    economy=round((total_runs / total_balls) * balls_per_over, 1) if total_balls > 0 else 0.0,
                    average=round(total_runs / total_wickets, 1) if total_wickets > 0 else 0.0,
                    strike_rate=round(total_balls / total_wickets, 1) if total_wickets > 0 else 0.0,
                    dot_pct=round(total_dots / total_balls * percent_scale, 1) if total_balls > 0 else 0.0,
                    boundary_pct=round(total_boundaries / total_balls * percent_scale, 1) if total_balls > 0 else 0.0,
                )
            )
        return phase_rows

    def _compute_vs_bowling_style(self, raw_bat: pd.DataFrame) -> List[VsBowlingStyleRow]:
        required_cols = {"bowler", "runs_off_bat", "player_dismissed"}
        if raw_bat.empty or not required_cols.issubset(raw_bat.columns):
            return []

        work = raw_bat.copy()
        work["style"] = work["bowler"].map(self.style_map).fillna("Other")
        work["is_dismissal"] = work["player_dismissed"].notna().astype(int)
        agg = work.groupby("style", sort=False).agg(
            total_runs=("runs_off_bat", "sum"),
            balls_faced=("runs_off_bat", "count"),
            dismissals=("is_dismissal", "sum"),
        ).reset_index()

        agg["avg_runs"] = np.where(
            agg["dismissals"] > 0,
            (agg["total_runs"] / agg["dismissals"]).round(2),
            agg["total_runs"].astype(float),
        )
        agg["strike_rate"] = np.where(
            agg["balls_faced"] > 0,
            (agg["total_runs"] / agg["balls_faced"] * 100).round(1),
            0.0,
        )
        agg = agg.sort_values("style").reset_index(drop=True)

        return [
            VsBowlingStyleRow(
                style=str(style),
                total_runs=int(runs),
                balls_faced=int(balls),
                dismissals=int(dismissals),
                avg_runs=float(avg_runs),
                strike_rate=float(strike_rate),
            )
            for style, runs, balls, dismissals, avg_runs, strike_rate in zip(
                agg["style"],
                agg["total_runs"],
                agg["balls_faced"],
                agg["dismissals"],
                agg["avg_runs"],
                agg["strike_rate"],
            )
        ]

    def _apply_ground_filter(self, df: pd.DataFrame, ground: Optional[str]) -> pd.DataFrame:
        if ground is None:
            return df
        if "venue" not in df.columns:
            return df
        aliases = get_venue_aliases(ground)
        if not aliases:
            return df
        return df[df["venue"].isin(aliases)].copy()

    def get_player_profile(
        self,
        player_name: str,
        opposition: Optional[str] = None,
        venue_id: Optional[str] = None,
        years: Optional[int] = None,
        raw_balls_df: Optional[pd.DataFrame] = None,
    ) -> Optional[PlayerProfile]:
        """
        Headless API: Fetches player profile data.
        """
        if not self._player_exists(player_name):
            return None
        
        years_back = self._get_years_back(years)
        cutoff_date = self._get_reference_date() - pd.DateOffset(years=years_back)
        p_stats = self.player_df[self.player_df['player'] == player_name].copy()
        
        # BATTING
        career_bat = p_stats[
            (p_stats['context'] == self.rules["player_context_types"]["vs_team"])
            & (p_stats['role'] == self.rules["player_context_types"]["batting"])
        ].copy()
        bat_stats = BattingStats(0, 0, 0.0, 0.0, 0, 0, 0, [])
        if not career_bat.empty:
            runs = int(career_bat['runs'].sum())
            inns = int(career_bat['innings'].sum())
            outs = int(career_bat['dismissals'].sum())
            balls = int(career_bat['balls'].sum())
            avg = round(runs / outs, self.rules["player_rules"]["stat_precision_avg"]) if outs > 0 else runs
            sr = round((runs / balls) * self.rules["SPORT_CONSTANTS"]["percent_scale"], 1) if balls > 0 else 0.0
            
            raw_bat = pd.DataFrame()
            if isinstance(raw_balls_df, pd.DataFrame) and not raw_balls_df.empty:
                raw_bat = raw_balls_df[raw_balls_df['striker'] == player_name].copy()
            
            if not raw_bat.empty:
                 if 'start_date' in raw_bat.columns:
                     raw_bat['start_date'] = pd.to_datetime(raw_bat['start_date'], errors='coerce')
                 raw_bat = raw_bat[raw_bat['start_date'] >= cutoff_date]
                 c100, c50, hs = self._get_batting_milestones(raw_bat)
                 bat_stats = BattingStats(inns, runs, avg, sr, c100, c50, hs, [])

        # BOWLING
        career_bowl = p_stats[
            (p_stats['context'] == self.rules["player_context_types"]["vs_team"])
            & (p_stats['role'] == self.rules["player_context_types"]["bowling"])
        ].copy()
        bowl_stats = None
        if not career_bowl.empty:
            b_runs = int(career_bowl['runs'].sum())
            b_balls = int(career_bowl['balls'].sum())
            b_wkts = int(career_bowl['dismissals'].sum())
            if b_balls > self.rules["player_rules"]["profile_sr_min_balls"]:
                b_avg = round(b_runs / b_wkts, self.rules["player_rules"]["stat_precision_avg"]) if b_wkts > 0 else 0.0
                b_econ = round((b_runs / b_balls) * self.rules["SPORT_CONSTANTS"]["balls_per_over"], self.rules["player_rules"]["stat_precision_rate"]) if b_balls > 0 else 0.0
                bowl_stats = BowlingStats(0, b_wkts, b_avg, b_econ, None, [])

        # CONTEXT
        vs_opponent_context = None
        if opposition and opposition != self.rules["player_context_types"]["all"]:
            opp_bat_stats = None
            opp_bat = p_stats[
                (p_stats['context'] == self.rules["player_context_types"]["vs_team"])
                & (p_stats['role'] == self.rules["player_context_types"]["batting"])
                & (p_stats['opponent'] == opposition)
            ]
            if not opp_bat.empty:
                r = int(opp_bat['runs'].sum()); i = int(opp_bat['innings'].sum()); o = int(opp_bat['dismissals'].sum()); b = int(opp_bat['balls'].sum())
                av = round(r / o, self.rules["player_rules"]["stat_precision_avg"]) if o > 0 else r; sr = round((r / b) * self.rules["SPORT_CONSTANTS"]["percent_scale"], 1) if b > 0 else 0.0
                vs_opponent_context = ContextStats(batting=BattingStats(i, r, av, sr, 0, 0, 0, []), bowling=None)

        venue_context = None
        if venue_id:
            aliases = get_venue_aliases(venue_id)
            ven_pattern = '|'.join([re.escape(v) for v in aliases])
            ven_bat = p_stats[
                (p_stats['context'] == self.rules["player_context_types"]["at_venue"])
                & (p_stats['role'] == self.rules["player_context_types"]["batting"])
                & (p_stats['opponent'].str.contains(ven_pattern, case=False, regex=True))
            ]
            if not ven_bat.empty:
                r = int(ven_bat['runs'].sum()); i = int(ven_bat['innings'].sum()); o = int(ven_bat['dismissals'].sum()); b = int(ven_bat['balls'].sum())
                av = round(r / o, self.rules["player_rules"]["stat_precision_avg"]) if o > 0 else r; sr = round((r / b) * self.rules["SPORT_CONSTANTS"]["percent_scale"], 1) if b > 0 else 0.0
                venue_context = ContextStats(batting=BattingStats(i, r, av, sr, 0, 0, 0, []), bowling=None)

        return PlayerProfile(
            name=player_name,
            role=self._get_player_role(player_name),
            batting=bat_stats,
            bowling=bowl_stats,
            venue_stats=venue_context,
            vs_opponent_stats=vs_opponent_context
        )

    def analyze_player_profile(
        self,
        player_name: str,
        opposition: Optional[str] = None,
        venue_id: Optional[str] = None,
        active_bowlers: Optional[List[str]] = None,
        years: Optional[int] = None,
        raw_balls_df: Optional[pd.DataFrame] = None,
        country: Optional[str] = None,
        ground: Optional[str] = None,
    ) -> Optional[PlayerProfile]:
        """
        Headless API: Context-Aware Player Profile retrieval.
        """
        _ = (active_bowlers, country)
        if not self._player_exists(player_name):
            return None

        profile = self.get_player_profile(
            player_name,
            opposition,
            venue_id,
            years,
            raw_balls_df=raw_balls_df,
        )
        if profile is None:
            return None

        profile.batting.last_10_runs = self._parse_last_10_runs(profile.batting.form_last_10)

        raw_bat = pd.DataFrame()
        if (
            isinstance(raw_balls_df, pd.DataFrame)
            and not raw_balls_df.empty
            and "striker" in raw_balls_df.columns
        ):
            raw_bat = raw_balls_df[raw_balls_df["striker"] == player_name].copy()
            if years is not None and "start_date" in raw_bat.columns:
                cutoff_date = self._get_reference_date() - pd.DateOffset(
                    years=self._get_years_back(years)
                )
                start_dates = pd.to_datetime(raw_bat["start_date"], errors="coerce")
                raw_bat = raw_bat[start_dates >= cutoff_date].copy()

        raw_bat_ground = self._apply_ground_filter(raw_bat, ground) if not raw_bat.empty else raw_bat
        profile.phase_runs = self._compute_phase_runs(raw_bat_ground)
        profile.vs_bowling_style = self._compute_vs_bowling_style(raw_bat_ground)
        raw_bowl: pd.DataFrame = pd.DataFrame()
        if (
            isinstance(raw_balls_df, pd.DataFrame)
            and not raw_balls_df.empty
            and "bowler" in raw_balls_df.columns
        ):
            raw_bowl = raw_balls_df[raw_balls_df["bowler"] == player_name].copy()
            if years is not None and "start_date" in raw_bowl.columns:
                cutoff_bowl = self._get_reference_date() - pd.DateOffset(
                    years=self._get_years_back(years)
                )
                bowl_dates = pd.to_datetime(raw_bowl["start_date"], errors="coerce")
                raw_bowl = raw_bowl[bowl_dates >= cutoff_bowl].copy()

        raw_bowl_ground = (
            self._apply_ground_filter(raw_bowl, ground)
            if not raw_bowl.empty
            else raw_bowl
        )
        profile.phase_bowling = self._compute_phase_bowling(raw_bowl_ground)
        profile.last_10_bowling = (
            self._parse_last_10_bowling(profile.bowling.form_last_10)
            if profile.bowling is not None
            else []
        )
        return profile
