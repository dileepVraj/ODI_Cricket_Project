"""formats/odi/engines/player/_squad — PlayerEngineSquad: squad analysis, comparison, tactical matrix."""

from typing import List, Optional

import pandas as pd
import re

from config.shared.venues import get_venue_aliases
from core.services.report_formatter import ReportFormatter
from core.interfaces.player_interface import SquadComparisonData
from core.interfaces.player_types import TacticalRecorderPort, SquadComparisonPayload
from core.interfaces.serialization_types import DisplayRecord
from ._base import PlayerEngineBase


class PlayerEngineSquad(PlayerEngineBase):
    def get_active_squad(self, team_name: str) -> List[str]:
        """
        Retrieves the list of active players for a team from the metadata.
        """
        if self.meta_df.empty:
            return []
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
                    confirmed_xi_rows = last_match_rows[last_match_rows['is_playing_xi']]
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
            if m_data:
                matchups_a[p] = m_data
            
        matchups_b = {}
        for p in team_b_players:
            m_data = self._matchup_single_batter(p, team_a_players, context_df=squad_context_df)
            if m_data:
                matchups_b[p] = m_data

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
    
