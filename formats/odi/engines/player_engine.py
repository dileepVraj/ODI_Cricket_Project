from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from config.shared.venues import get_venue_aliases
import re
from core.calculators import MatchupEngine
from core.exceptions import ConfigurationError
from core.services.report_builder import ReportBuilder
from core.services.report_formatter import ReportFormatter
from core.services.squad_service import SquadService
from core.interfaces.player_interface import (
    BattingStats,
    BowlingStats,
    ContextStats,
    IPlayerEngine,
    PlayerProfile,
    SquadComparisonData,
)
from core.interfaces.team_types import (
    DataAccessPort,
    DisplayRecord,
    FormatRulesMap,
    ManifestFunctionDef,
    SquadComparisonPayload,
    TacticalRecorderPort,
)

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
        self.squads_df = squads_df if squads_df is not None else pd.DataFrame(columns=['match_id', 'player', 'date', 'team'])
        
        if not self.squads_df.empty:
            self.squads_df['match_id'] = self.squads_df['match_id'].astype(str)

    def _require_nonempty_dict_rule(self, key: str) -> ManifestFunctionDef:
        raw_value = self.rules.get(key)
        if not isinstance(raw_value, dict) or not raw_value:
            raise ConfigurationError(
                f"Missing required format rule '{key}'. "
                "Define it in manifest FORMAT_RULES and pass it into PlayerEngine."
            )
        return raw_value

    def _require_tactical_thresholds(self) -> Dict[str, int]:
        thresholds = self._require_nonempty_dict_rule("tactical_thresholds")
        normalized: Dict[str, int] = {}
        for key, value in thresholds.items():
            try:
                normalized[str(key)] = int(value)
            except (TypeError, ValueError) as exc:
                raise ConfigurationError(
                    f"Invalid tactical threshold '{key}': {value!r}. Expected integer."
                ) from exc
        return normalized

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

    def _require_default_years_window(self) -> int:
        raw_value = self.rules.get("default_years_window")
        if raw_value is None:
            raise ConfigurationError(
                "Missing required format rule 'default_years_window'. "
                "Define it in manifest FORMAT_RULES and pass it into PlayerEngine."
            )
        try:
            years_window = int(raw_value)
        except (TypeError, ValueError) as exc:
            raise ConfigurationError(
                f"Invalid format rule 'default_years_window': {raw_value!r}"
            ) from exc
        if years_window <= 0:
            raise ConfigurationError("Format rule 'default_years_window' must be > 0.")
        return years_window

    def _require_engine_defaults(self) -> Dict[str, int]:
        defaults = self._require_nonempty_dict_rule("engine_defaults")
        normalized: Dict[str, int] = {}
        for key, value in defaults.items():
            try:
                normalized[str(key)] = int(value)
            except (TypeError, ValueError) as exc:
                raise ConfigurationError(
                    f"Invalid engine default '{key}': {value!r}. Expected integer."
                ) from exc
        return normalized

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
        if getattr(self, '_reference_date', None) is None:
            self._reference_date = self._compute_reference_date()
        return self._reference_date

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

    def _get_tactical_threshold(self, key: str) -> int:
        if key not in self.tactical_thresholds:
            raise ConfigurationError(
                f"Missing tactical threshold '{key}' in FORMAT_RULES['tactical_thresholds']."
            )
        raw_value = self.tactical_thresholds[key]
        try:
            return int(raw_value)
        except (TypeError, ValueError) as exc:
            raise ConfigurationError(
                f"Invalid tactical threshold '{key}': {raw_value!r}"
            ) from exc

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
    ) -> List[str]:
        """
        Retrieves players from the last match using Squads DB (preferred) or
        pre-fetched match/ball data.
        """
        
        # 1. Try Squads DB First
        if not self.squads_df.empty:
            team_squads = self.squads_df[self.squads_df['team'] == team_name]
            if not team_squads.empty:
                dates = team_squads.sort_values('date', ascending=False)
                last_match_id = dates.iloc[0]['match_id']
                last_match_rows = team_squads[team_squads['match_id'] == str(last_match_id)].copy()
                if 'is_playing_xi' in last_match_rows.columns:
                    last_match_rows = last_match_rows[last_match_rows['is_playing_xi'] == True]
                return sorted(last_match_rows['player'].unique().tolist())

        # 2. Fallback to pre-fetched raw data (provided by API/Facade layer)
        if team_matches is None or team_matches.empty:
            return []

        balls_source = match_balls_df if match_balls_df is not None else pd.DataFrame()
        if not balls_source.empty and 'match_id' in balls_source.columns:
            balls_source = balls_source.copy()
            balls_source['match_id'] = balls_source['match_id'].astype(str)

        sorted_matches = team_matches.sort_values('start_date', ascending=False)['match_id'].unique()
        squad = set()
        backscan_limit = self._get_engine_default("squad_backscan_match_limit")
        
        for match_id in sorted_matches[:backscan_limit]: 
            if len(squad) >= self.rules["player_rules"]["last_xi_match_limit"]:
                break
            if balls_source.empty:
                continue
            match_data = balls_source[balls_source['match_id'] == str(match_id)]
            if match_data.empty:
                continue
            squad.update(match_data[match_data['batting_team'] == team_name]['striker'].unique())
            squad.update(match_data[match_data['batting_team'] == team_name]['non_striker'].unique())
            squad.update(match_data[match_data['bowling_team'] == team_name]['bowler'].unique())
            
        return sorted(list(squad))

    def get_squad_comparison_data(
        self,
        team_a_name: str,
        team_a_players: List[str],
        team_b_name: str,
        team_b_players: List[str],
        venue_id: str,
        years: Optional[int] = None,
        context_df: Optional[pd.DataFrame] = None,
    ) -> SquadComparisonData:
        """
        Headless API: Fetches all data required for a Squad Comparison.
        Returns: SquadComparisonData Dataclass.
        """
        # 1. OPTIMIZATION: Create Squad Context Subset
        years_back = self._get_years_back(years)
        cutoff_date = self._get_reference_date() - pd.DateOffset(years=years_back)
        squad_context_df = context_df.copy() if isinstance(context_df, pd.DataFrame) else pd.DataFrame()
        if not squad_context_df.empty and 'start_date' in squad_context_df.columns:
            squad_context_df['start_date'] = pd.to_datetime(squad_context_df['start_date'], errors='coerce')
            squad_context_df = squad_context_df[squad_context_df['start_date'] >= cutoff_date]
        
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

        # 4. TACTICAL MATRIX
        matrix_a = self.analyze_squad_types(
            team_a_name,
            team_a_players,
            team_b_players,
            years_back,
            context_df=squad_context_df,
        )
        matrix_b = self.analyze_squad_types(
            team_b_name,
            team_b_players,
            team_a_players,
            years_back,
            context_df=squad_context_df,
        )

        # 5. MATCHUPS
        matchups_a = {p: self.get_matchups(p, team_b_players, context_df=squad_context_df) for p in team_a_players}
        matchups_b = {p: self.get_matchups(p, team_a_players, context_df=squad_context_df) for p in team_b_players}

        return SquadComparisonData(
            team_a_name=team_a_name,
            team_b_name=team_b_name,
            metrics_a=metrics_a,
            metrics_b=metrics_b,
            player_stats_a=player_stats_a,
            player_stats_b=player_stats_b,
            tactical_matrix_a=matrix_a,
            tactical_matrix_b=matrix_b,
            matchups_a=matchups_a,
            matchups_b=matchups_b,
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
        context_df: Optional[pd.DataFrame] = None,
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
        context_df: Optional[pd.DataFrame] = None,
    ) -> List[DisplayRecord]:
        """
        Headless logic for Tactical Breakdown.
        Returns: List of Dicts (Table Data).
        """
        years_back = self._get_years_back(years)
        cutoff_date = self._get_reference_date() - pd.DateOffset(years=years_back)
        if context_df is not None:
            base_df = context_df
        else:
            return []

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


    # --- HELPERS ---

    def get_matchups(
        self,
        batter: str,
        bowlers: Optional[List[str]] = None,
        *,
        home_team: Optional[str] = None,
        opp_team: Optional[str] = None,
        home_xi: Optional[List[str]] = None,
        away_xi: Optional[List[str]] = None,
        context_df: Optional[pd.DataFrame] = None,
    ) -> List[DisplayRecord]:
        """
        Headless logic for Batter vs Bowlers.
        """
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

        if context_df is not None:
            base_df = context_df
        else:
            return []

        required_cols = {"striker", "bowler", "runs_off_bat", "match_id", "player_dismissed"}
        if not required_cols.issubset(set(base_df.columns)):
            return []

        bunny_outs_hard = self._get_tactical_threshold("bunny_outs_hard")
        bunny_outs_soft = self._get_tactical_threshold("bunny_outs_soft")
        bunny_balls_per_out_max = self._get_tactical_threshold("bunny_balls_per_out_max")

        # Filter for relevant balls
        batter_df = base_df[
            (base_df['striker'] == batter) & 
            (base_df['bowler'].isin(inferred_bowlers))
        ].copy()

        if batter_df.empty: return []

        matchup_stats = batter_df.groupby('bowler').agg({
            'runs_off_bat': 'sum',           
            'match_id': 'count',             
            'player_dismissed': lambda x: (x == batter).sum()
        }).reset_index()
        
        matchup_stats.rename(columns={'match_id': 'Balls', 'runs_off_bat': 'Runs', 'player_dismissed': 'Outs'}, inplace=True)
        matchup_stats['Style'] = matchup_stats['bowler'].map(self.style_map).fillna('Unknown')
        outs = matchup_stats['Outs'].astype(float)
        balls = matchup_stats['Balls'].astype(float)
        matchup_stats['IsBunny'] = (
            (outs >= bunny_outs_hard)
            | (
                (outs >= bunny_outs_soft)
                & (balls > 0)
                & ((balls / outs) <= bunny_balls_per_out_max)
            )
        )
        matchup_stats['Avg'] = np.where(
            matchup_stats['Outs'] > 0,
            (matchup_stats['Runs'] / matchup_stats['Outs']).round(1),
            matchup_stats['Runs'].astype(float),
        )
        matchup_stats['SR'] = np.where(
            matchup_stats['Balls'] > 0,
            ((matchup_stats['Runs'] / matchup_stats['Balls']) * self.rules["SPORT_CONSTANTS"]["percent_scale"]).round(1),
            0.0,
        )

        result = matchup_stats.rename(columns={'bowler': 'Bowler'})
        result['Runs'] = result['Runs'].astype(int)
        result['Balls'] = result['Balls'].astype(int)
        result['Outs'] = result['Outs'].astype(int)
        return result[['Bowler', 'Style', 'IsBunny', 'Runs', 'Balls', 'Outs', 'Avg', 'SR']].to_dict('records')

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
        squad_context_df = context_df.copy() if isinstance(context_df, pd.DataFrame) else pd.DataFrame()
        if not squad_context_df.empty and 'start_date' in squad_context_df.columns:
            squad_context_df['start_date'] = pd.to_datetime(squad_context_df['start_date'], errors='coerce')
            squad_context_df = squad_context_df[squad_context_df['start_date'] >= cutoff_date]
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
            m_data = self.get_matchups(p, team_b_players, context_df=squad_context_df)
            if m_data: matchups_a[p] = m_data
            
        matchups_b = {}
        for p in team_b_players:
            m_data = self.get_matchups(p, team_a_players, context_df=squad_context_df)
            if m_data: matchups_b[p] = m_data

        return ReportBuilder._build_squad_comparison_payload(
            team_a_name=team_a_name,
            team_b_name=team_b_name,
            squad_a=squad_a,
            squad_b=squad_b,
            matrix_a=matrix_a,
            matrix_b=matrix_b,
            matchups_a=matchups_a,
            matchups_b=matchups_b,
            player_stats_a=ReportFormatter.format_squad_player_stats(team_a_bundle["player_stats"]),
            player_stats_b=ReportFormatter.format_squad_player_stats(team_b_bundle["player_stats"]),
        )
    
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
        if player_name not in self.player_df['player'].values:
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
            avg = round(runs / outs, 2) if outs > 0 else runs
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
                b_avg = round(b_runs / b_wkts, 2) if b_wkts > 0 else 0.0
                b_econ = round((b_runs / b_balls) * self.rules["SPORT_CONSTANTS"]["balls_per_over"], 2) if b_balls > 0 else 0.0
                bowl_stats = BowlingStats(0, b_wkts, b_avg, b_econ, "N/A", [])

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
                av = round(r / o, 2) if o > 0 else r; sr = round((r / b) * self.rules["SPORT_CONSTANTS"]["percent_scale"], 1) if b > 0 else 0.0
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
                av = round(r / o, 2) if o > 0 else r; sr = round((r / b) * self.rules["SPORT_CONSTANTS"]["percent_scale"], 1) if b > 0 else 0.0
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
    ) -> Optional[PlayerProfile]:
        """
        Headless API: Context-Aware Player Profile retrieval.
        """
        if player_name not in self.player_df['player'].values:
            return None

        _ = active_bowlers
        return self.get_player_profile(
            player_name,
            opposition,
            venue_id,
            years,
            raw_balls_df=raw_balls_df,
        )
