from typing import List, Dict, Optional, Any, Union
import pandas as pd
import numpy as np
import datetime
import logging
from config.shared.venues import get_venue_aliases
from config.shared.team_colors import TEAM_COLORS
from formats.odi.config.players import BOWLER_STYLES, PLAYER_ROLES
from core.predictor import PredictorEngine
import re
from core.interfaces.player_interface import (
    PlayerProfile, BattingStats, BowlingStats, MatchupStats, 
    ContextStats, SquadMetrics, SquadComparisonData
)
from formats.odi.renderers.player_renderer import PlayerHTMLRenderer

logger = logging.getLogger("CricketAnalyzer")

class PlayerEngine:
    """
    ⚔️ The Dugout (v6.0 - Engineering Standards Aligned).
    - HEADLESS: Logic returning pure data.
    - TYPED: Full Type Hint signatures.
    - DECOUPLED: Renderers handle the UI.
    """
    def __init__(self, raw_df: pd.DataFrame, player_df: pd.DataFrame, meta_df: pd.DataFrame, squads_df: Optional[pd.DataFrame] = None, dal: Any = None):
        self.dal = dal
        # 🔗 PURE DB MODE: If dal is provided, we don't load the global raw_df
        if raw_df is None and dal is not None:
             self.raw_df = pd.DataFrame() 
        else:
             self.raw_df = raw_df if raw_df is not None else pd.DataFrame()
        
        self.player_df = player_df
        self.meta_df = meta_df
        self.squads_df = squads_df if squads_df is not None else pd.DataFrame(columns=['match_id','player'])
        
        # Ensure ID type match
        if not self.squads_df.empty:
            self.squads_df['match_id'] = self.squads_df['match_id'].astype(str)
            if not self.raw_df.empty:
                self.raw_df['match_id'] = self.raw_df['match_id'].astype(str)
            
        self.predictor = PredictorEngine(self.raw_df, player_df, dal=dal)

    def _get_player_role(self, player_name: str) -> str:
        """Returns the role of a player from config or default."""
        from formats.odi.config.players import PLAYER_ROLES
        return PLAYER_ROLES.get(player_name, "All-Rounder")

    def _compute_reference_date(self) -> pd.Timestamp:
        """Use latest available ball date to stabilize lookbacks."""
        # 🚀 PURE DB MODE: Fetch max date from DAL if raw_df is empty
        if self.raw_df.empty and self.dal is not None:
             try:
                  max_date_str = self.dal.con.execute("SELECT MAX(start_date) FROM balls").fetchone()[0]
                  if max_date_str:
                      return pd.Timestamp(max_date_str).floor('D')
             except (Exception) as e:
                 logger.debug(f"DAL date query failed: {e}")

        df = self.raw_df
        if not df.empty and 'start_date' in df.columns:
            try:
                dates = pd.to_datetime(df['start_date'], errors='coerce')
                max_date = dates.max()
            except Exception:
                max_date = None
            if pd.notna(max_date):
                return pd.Timestamp(max_date).floor('D')
        return pd.Timestamp.now().floor('D')

    def _get_reference_date(self) -> pd.Timestamp:
        if getattr(self, '_reference_date', None) is None:
            self._reference_date = self._compute_reference_date()
        return self._reference_date


    def get_active_squad(self, team_name: str) -> List[str]:
        """
        Retrieves the list of active players for a team from the metadata.
        """
        if self.meta_df.empty: return []
        team_players = self.meta_df[self.meta_df['team'].str.lower() == team_name.lower()]
        return sorted(team_players['player'].unique().tolist())
        
    def get_last_match_xi(self, team_name: str) -> List[str]:
        """
        Smart Fetch: Retrieves players from the last match using Squads DB (Preferred) or Backfill.
        """
        
        # 1. Try Squads DB First
        if not self.squads_df.empty:
            team_squads = self.squads_df[self.squads_df['team'] == team_name]
            if not team_squads.empty:
                dates = team_squads.sort_values('date', ascending=False)
                last_match_id = dates.iloc[0]['match_id']
                return sorted(team_squads[team_squads['match_id'] == str(last_match_id)]['player'].unique().tolist())

        # 2. Fallback to Raw Data Backfill (Legacy / DAL)
        if self.dal is not None:
            team_matches = self.dal.get_matches(team_a=team_name)
        else:
            base_df = self.raw_df
            mask = (base_df['batting_team'] == team_name) | (base_df['bowling_team'] == team_name)
            team_matches = base_df[mask]
        
        if team_matches.empty: return []
        
        sorted_matches = team_matches.sort_values('start_date', ascending=False)['match_id'].unique()
        squad = set()
        
        for match_id in sorted_matches[:3]: 
            if len(squad) >= 11: break
            if self.dal is not None:
                match_data = self.dal.get_balls(match_ids=[match_id])
            else:
                match_data = self.raw_df[self.raw_df['match_id'] == match_id]
            squad.update(match_data[match_data['batting_team'] == team_name]['striker'].unique())
            squad.update(match_data[match_data['batting_team'] == team_name]['non_striker'].unique())
            squad.update(match_data[match_data['bowling_team'] == team_name]['bowler'].unique())
            
        return sorted(list(squad))

    def get_squad_comparison_data(self, team_a_name: str, team_a_players: List[str], team_b_name: str, team_b_players: List[str], venue_id: str, years: int = None) -> SquadComparisonData:
        """
        Headless API: Fetches all data required for a Squad Comparison.
        Returns: SquadComparisonData Dataclass.
        """
        # 1. OPTIMIZATION: Create Squad Context Subset
        all_matchup_players = list(set(team_a_players) | set(team_b_players))
        cutoff_date = self._get_reference_date() - pd.DateOffset(years=years)
        
        if self.dal is not None:
            squad_context_df = self.dal.get_balls(players=all_matchup_players)
            if 'start_date' in squad_context_df.columns:
                squad_context_df['start_date'] = pd.to_datetime(squad_context_df['start_date'], errors='coerce')
            squad_context_df = squad_context_df[squad_context_df['start_date'] >= cutoff_date]
        else:
            squad_context_df = self.raw_df[
                ((self.raw_df['striker'].isin(all_matchup_players)) | 
                 (self.raw_df['non_striker'].isin(all_matchup_players)) | 
                 (self.raw_df['bowler'].isin(all_matchup_players))) &
                (self.raw_df['start_date'] >= cutoff_date)
            ]

        # 2. CALCULATE METRICS
        metrics_a = self._calculate_squad_metrics(team_a_name, team_a_players, years, context_df=squad_context_df) 
        metrics_b = self._calculate_squad_metrics(team_b_name, team_b_players, years, context_df=squad_context_df)
        
        # 3. VENUE PATTERN
        aliases = get_venue_aliases(venue_id)
        if "_" in venue_id:
            suffix_key = venue_id.split("_", 1)[1] 
            suffix_aliases = get_venue_aliases(suffix_key)
            if suffix_aliases:
                aliases = list(set(aliases + suffix_aliases))
        venue_pattern = '|'.join([re.escape(v) for v in aliases if v])

        # 4. PLAYER TABLES
        def get_team_stats(players, opponent):
             data = []
             for p in players:
                  stats = self._get_stats(p, opponent, venue_pattern, years, context_df=squad_context_df)
                  stats['Role'] = PLAYER_ROLES.get(p, 'Batter')
                  data.append(stats)
             return data

        player_stats_a = get_team_stats(team_a_players, team_b_name)
        player_stats_b = get_team_stats(team_b_players, team_a_name)

        # 5. TACTICAL MATRIX
        matrix_a = self.analyze_squad_types(team_a_name, team_a_players, team_b_players, years, context_df=squad_context_df)
        matrix_b = self.analyze_squad_types(team_b_name, team_b_players, team_a_players, years, context_df=squad_context_df)

        # 6. MATCHUPS
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
            years=years
        )

    def compare_squads(self, team_a_name: str, team_a_players: List[str], team_b_name: str, team_b_players: List[str], venue_id: str, years: int = None, recorder: Any = None) -> SquadComparisonData:
        """
        Headless API: Orchestrates squad comparison logic.
        (Note: UI rendering has been moved to PlayerHTMLRenderer)
        """
        return self.get_squad_comparison_data(team_a_name, team_a_players, team_b_name, team_b_players, venue_id, years)

    # --- NEW: ARCHETYPE ANALYSIS ---
    def analyze_squad_types(self, team_name: str, players: List[str], opposition_bowlers: List[str], years: int = None, recorder: Any = None, context_df: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
        """
        Headless logic for Tactical Breakdown.
        Returns: List of Dicts (Table Data).
        """
        # DYNAMIC DATE FILTER
        cutoff_date = self._get_reference_date() - pd.DateOffset(years=years)
        if context_df is not None:
            base_df = context_df.copy()
        elif self.dal is not None:
            merged_players = list(set(players + opposition_bowlers))
            base_df = self.dal.get_balls(players=merged_players)
        else:
            base_df = self.raw_df

        if 'start_date' in base_df.columns:
            base_df.loc[:, 'start_date'] = pd.to_datetime(base_df['start_date'], errors='coerce')
        window_df = base_df[base_df['start_date'] >= cutoff_date]
        
        # 1. IDENTIFY OPPOSITION BOWLING TYPES & NAMES
        active_styles_data = {} 
        all_style_map = {}
        missing_bowlers = [] 
        
        # Build Reverse Map
        for name, style in BOWLER_STYLES.items():
            if style not in all_style_map: all_style_map[style] = []
            all_style_map[style].append(name)
            
        # Group bowlers by style
        for b in opposition_bowlers:
            style = BOWLER_STYLES.get(b, 'Unknown')
            if style == 'Part-Timer': continue

            if style != 'Unknown':
                if style not in active_styles_data: 
                    active_styles_data[style] = []
                active_styles_data[style].append(b)
            else:
                bowler_stats = window_df[window_df['bowler'] == b]
                balls_delivered = len(bowler_stats)
                if balls_delivered > 6:
                    missing_bowlers.append(f"{b} ({balls_delivered} balls)")

        if not active_styles_data: 
            return []

        # 2. CALCULATE BATTER PERFORMANCE VS THESE TYPES
        target_styles = list(active_styles_data.keys())
        table_data = []
        
        for batter in players:
            row = {'Player': batter, 'Role': self._get_player_role(batter)}
            for style in target_styles:
                proxy_bowlers = all_style_map.get(style, [])
                
                if not proxy_bowlers:
                    row[style] = "-"
                    continue
                
                try:
                    style_df = window_df[
                        (window_df['striker'] == batter) & 
                        (window_df['bowler'].isin(proxy_bowlers))
                    ]
                    
                    if not style_df.empty:
                        runs = int(style_df['runs_off_bat'].sum())
                        balls = int(style_df['match_id'].count())
                        outs = int(style_df['wicket_type'].isin(['bowled','caught','lbw','stumped','caught and bowled','hit wicket']).sum())
                        
                        avg = round(runs/outs, 1) if outs > 0 else runs
                        sr = int((runs/balls)*100) if balls > 0 else 0
                        
                        # We store raw data; the renderer handles colors
                        row[style] = [avg, sr] 
                        row[f"{style}_raw"] = avg
                    else:
                        row[style] = "-"
                except (KeyError, TypeError, ZeroDivisionError):
                    row[style] = "-"
            table_data.append(row)

        if recorder and table_data:
            for row in table_data:
                batter = row['Player']
                for style in target_styles:
                    raw_key = f"{style}_raw"
                    if raw_key in row:
                        avg = row[raw_key]
                        if avg < 25:
                            recorder.log_tactical_alert("STRUCTURAL_WEAKNESS", f"{batter} struggles vs {style} (Avg {avg})")
                        elif avg > 50:
                            recorder.log_tactical_alert("DOMINANT_MATCHUP", f"{batter} dominates {style} (Avg {avg})")

        return table_data


    # --- HELPERS ---

    def _calculate_squad_metrics(self, team: str, players: List[str], years: int = None, context_df: Optional[pd.DataFrame] = None) -> SquadMetrics:
        """
        Internal Helper: Computes aggregated stats for a list of players.
        VECTORIZED: Eliminates per-player loops and nested grouping.
        """
        cutoff_date = self._get_reference_date() - pd.DateOffset(years=years)
        
        if context_df is not None:
            base_df = context_df.copy()
        elif self.dal is not None:
            base_df = self.dal.get_balls(players=players)
        else:
            base_df = self.raw_df

        if 'start_date' in base_df.columns:
            base_df.loc[:, 'start_date'] = pd.to_datetime(base_df['start_date'], errors='coerce')
        if 'match_id' in base_df.columns:
            base_df.loc[:, 'match_id'] = base_df['match_id'].astype(str)

        window_df = base_df[base_df['start_date'] >= cutoff_date]
        if window_df.empty:
            return SquadMetrics(0,0,0,0,0,0,0)

        # 1. BATTING METRICS (Vectorized)
        bat_df = window_df[window_df['striker'].isin(players)]
        if not bat_df.empty:
            bat_scores = bat_df.groupby(['striker', 'match_id'])['runs_off_bat'].sum()
            tr = bat_scores.sum()
            c = (bat_scores >= 100).sum()
            f = ((bat_scores >= 50) & (bat_scores < 100)).sum()
        else:
            tr, c, f = 0, 0, 0
        
        # 2. BOWLING METRICS (Vectorized)
        bowl_df = window_df[window_df['bowler'].isin(players)]
        if not bowl_df.empty:
            valid_wkts = bowl_df[bowl_df['wicket_type'].isin(['bowled','caught','lbw','stumped','caught and bowled','hit wicket'])]
            tw = len(valid_wkts)
            if not valid_wkts.empty:
                fws = valid_wkts.groupby(['bowler', 'match_id']).size()
                fw = (fws >= 5).sum()
            else:
                fw = 0
        else:
            tw, fw = 0, 0
        
        # 3. CAPS (Experience - Vectorized Set Logic)
        strikers_matches = bat_df[['match_id', 'striker']].rename(columns={'striker': 'player'})
        bowlers_matches = bowl_df[['match_id', 'bowler']].rename(columns={'bowler': 'player'})
        unique_appearances = pd.concat([strikers_matches, bowlers_matches]).drop_duplicates()
        caps = len(unique_appearances)
        
        avg_caps = int(caps / len(players)) if players else 0
        
        return SquadMetrics(
            caps=caps, 
            runs=int(tr), 
            centuries=int(c), 
            fifties=int(f), 
            wickets=int(tw), 
            five_wkt_hauls=int(fw),
            avg_caps=avg_caps
        )

    def _get_stats(self, player: str, opp: str, venue_pattern: str, years: int = None, context_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Internal Helper: Fetches comprehensive stats for a single player.
        """
        # 1. SETUP & DATE FILTER
        cutoff_date = self._get_reference_date() - pd.DateOffset(years=years)
        
        # Get ALL activity for this player (Batting OR Bowling)
        if context_df is not None:
            base_df = context_df.copy()
        elif self.dal is not None:
            base_df = self.dal.get_balls(players=[player])
        else:
            base_df = self.raw_df

        if 'start_date' in base_df.columns:
            base_df.loc[:, 'start_date'] = pd.to_datetime(base_df['start_date'], errors='coerce')
        if 'match_id' in base_df.columns:
            base_df.loc[:, 'match_id'] = base_df['match_id'].astype(str)
        
        all_activity = base_df[
            ((base_df['striker'] == player) | (base_df['bowler'] == player)) &
            (base_df['start_date'] >= cutoff_date)
        ]
        
        # OPTIMIZED MATCH IDENTIFICATION
        matches_played = pd.DataFrame()
        
        if not self.squads_df.empty:
            matches_selected = self.squads_df[self.squads_df['player'] == player].copy()
            if matches_selected['date'].dtype == 'object':
                 matches_selected['date'] = pd.to_datetime(matches_selected['date'])
                 
            matches_played = matches_selected[matches_selected['date'] >= cutoff_date].sort_values(
                ['date', 'match_id'], ascending=[False, False]
            )
        else:
            if all_activity.empty:
                matches_played = pd.DataFrame()
            else:
                matches_played = all_activity.drop_duplicates('match_id').sort_values(['start_date', 'match_id'], ascending=[False, False])

        if matches_played.empty:
            return {
                'Player': player, 'Inns': 0, 'Bat Form': "-", 'Bat Avg': "-", 'vs Opp': "-", 
                'Ven Inns': "-", 'Ven Runs': "-", 'Ven Avg': "-", 'Ven HS': "-",
                'Bowl Form': "-", 'Bowl Econ': "-", 'Ven Econ': "-", 'Ven Wkts': "-", 'Ven Matches': "-"
            }

        last_10_ids = matches_played['match_id'].head(10).tolist()

        # ---------------------------------------------------------
        # 2. BATTING FORM (Smart DNB)
        # ---------------------------------------------------------
        form_bat = []
        for m_id in last_10_ids:
            m_id = str(m_id)
            m_bat = base_df[(base_df['match_id'] == m_id) & (base_df['striker'] == player)]
            
            if m_bat.empty:
                form_bat.append("DNB")
            else:
                r = m_bat['runs_off_bat'].sum()
                is_out = m_bat['wicket_type'].notna().any()
                score = f"{int(r)}" if is_out else f"{int(r)}*"
                form_bat.append(score)

        # Career Batting Stats (Windowed)
        bat_window = base_df[(base_df['striker'] == player) & (base_df['start_date'] >= cutoff_date)]
        car_inns = bat_window['match_id'].nunique()
        total_runs = bat_window['runs_off_bat'].sum()
        total_outs = base_df[(base_df['player_dismissed'] == player) & (base_df['start_date'] >= cutoff_date)].shape[0]
        avg = round(total_runs / total_outs, 1) if total_outs > 0 else total_runs

        # vs Opponent
        opp_df = bat_window[bat_window['bowling_team'] == opp]
        opp_runs = opp_df['runs_off_bat'].sum()
        opp_outs = base_df[(base_df['player_dismissed'] == player) & (base_df['bowling_team'] == opp) & (base_df['start_date'] >= cutoff_date)].shape[0]
        opp_avg = round(opp_runs / opp_outs, 1) if opp_outs > 0 else (opp_runs if not opp_df.empty else "-")

        # ---------------------------------------------------------
        # 3. VENUE BATTING
        # ---------------------------------------------------------
        v_inns = "-"; v_runs_disp = "-"; v_avg = "-"; v_hs = "-"
        ven_df = bat_window[bat_window['venue'].str.contains(venue_pattern, case=False, na=False)]
        
        if not ven_df.empty:
            match_scores = ven_df.groupby('match_id')['runs_off_bat'].sum()
            v_inns = len(match_scores)
            v_runs_total = match_scores.sum()
            v_outs_total = ven_df['wicket_type'].count()
            v_hs_val = match_scores.max()
            
            v_runs_disp = int(v_runs_total)
            v_avg = round(v_runs_total / v_outs_total, 1) if v_outs_total > 0 else v_runs_total
            v_hs = int(v_hs_val)
        else:
            ven_activity = all_activity[all_activity['venue'].str.contains(venue_pattern, case=False, na=False)]
            if not ven_activity.empty:
                v_runs_disp = "DNB"

        # ---------------------------------------------------------
        # 4. BOWLING FORM (Strict Legal Balls)
        # ---------------------------------------------------------
        form_bowl = []
        for m_id in last_10_ids:
            m_bowl = all_activity[(all_activity['match_id'] == m_id) & (all_activity['bowler'] == player)]
            
            if m_bowl.empty:
                form_bowl.append("-") 
            else:
                wkts = m_bowl['wicket_type'].isin(['bowled','caught','lbw','stumped','caught and bowled','hit wicket']).sum()
                wides = m_bowl['wides'].sum() if 'wides' in m_bowl.columns else 0
                nbs = m_bowl['noballs'].sum() if 'noballs' in m_bowl.columns else 0
                runs = m_bowl['runs_off_bat'].sum() + wides + nbs
                
                legal_mask = (m_bowl['wides'].fillna(0) == 0) & (m_bowl['noballs'].fillna(0) == 0)
                legal_balls = m_bowl[legal_mask].shape[0]
                
                overs = legal_balls // 6
                balls = legal_balls % 6
                overs_disp = f"{overs}.{balls}" if balls > 0 else f"{overs}"
                
                form_bowl.append(f"{wkts}/{int(runs)} ({overs_disp})")

        # Bowling Career
        bowl_window = base_df[(base_df['bowler'] == player) & (base_df['start_date'] >= cutoff_date)]
        econ = "-"
        if not bowl_window.empty:
            legal_mask = (bowl_window['wides'].fillna(0) == 0) & (bowl_window['noballs'].fillna(0) == 0)
            legal_b = bowl_window[legal_mask].shape[0]
            total_rc = bowl_window['runs_off_bat'].sum() + bowl_window['wides'].sum() + bowl_window['noballs'].sum()
            if legal_b > 0:
                econ = round((total_rc / legal_b) * 6, 2)

        # Venue Bowling
        v_wkts = "-"; v_econ = "-"; v_matches = "-"
        ven_bowl = bowl_window[bowl_window['venue'].str.contains(venue_pattern, case=False, na=False)]
        if not ven_bowl.empty:
            v_matches = ven_bowl['match_id'].nunique()
            v_wkts = ven_bowl['wicket_type'].isin(['bowled','caught','lbw','stumped','caught and bowled','hit wicket']).sum()
            
            legal_mask = (ven_bowl['wides'].fillna(0) == 0) & (ven_bowl['noballs'].fillna(0) == 0)
            v_legal = ven_bowl[legal_mask].shape[0]
            v_rc = ven_bowl['runs_off_bat'].sum() + ven_bowl['wides'].sum() + ven_bowl['noballs'].sum()
            if v_legal > 0:
                v_econ = round((v_rc / v_legal) * 6, 2)

        return {
            'Player': player, 
            'Inns': car_inns, 
            'Bat Form': ", ".join(form_bat), 
            'Bat Avg': avg, 
            'vs Opp': opp_avg, 
            'Ven Inns': v_inns, 
            'Ven Runs': v_runs_disp, 
            'Ven Avg': v_avg, 
            'Ven HS': v_hs,
            'Bowl Form': ", ".join(form_bowl), 
            'Bowl Econ': econ, 
            'Ven Econ': v_econ,
            'Ven Wkts': v_wkts, 
            'Ven Matches': v_matches
        }

    def get_matchups(self, batter: str, bowlers: List[str], context_df: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
        """
        Headless logic for Batter vs Bowlers.
        """
        if context_df is not None:
            base_df = context_df
        elif self.dal is not None:
            base_df = self.dal.get_balls(striker=batter)
        else:
            base_df = self.raw_df
        
        # Filter for relevant balls
        batter_df = base_df[
            (base_df['striker'] == batter) & 
            (base_df['bowler'].isin(bowlers))
        ].copy()

        if batter_df.empty: return []

        matchup_stats = batter_df.groupby('bowler').agg({
            'runs_off_bat': 'sum',           
            'match_id': 'count',             
            'player_dismissed': lambda x: (x == batter).sum()
        }).reset_index()
        
        matchup_stats.rename(columns={'match_id': 'Balls', 'runs_off_bat': 'Runs', 'player_dismissed': 'Outs'}, inplace=True)

        data = []
        for _, row in matchup_stats.iterrows():
            b = row['bowler']; r = row['Runs']; bl = row['Balls']; o = row['Outs']
            style_tag = BOWLER_STYLES.get(b, 'Unknown')
            bunny_tag = " (Bunny)" if o >= 3 else ""
            avg = round(r/o, 1) if o > 0 else r
            sr = round(r/bl*100, 1) if bl > 0 else 0
            
            data.append({
                'Bowler': b,
                'Style': style_tag,
                'IsBunny': o >= 3,
                'Runs': int(r), 
                'Balls': int(bl), 
                'Outs': int(o), 
                'Avg': avg, 
                'SR': sr
            })
            
        return data

    def _generate_comparison_payload(self, team_a_name, team_a_players, team_b_name, team_b_players, venue_id, years=None):
        """
        REGRESSION HELPER: Payload for validation.
        """
        aliases = get_venue_aliases(venue_id)
        venue_pattern = '|'.join([re.escape(v) for v in aliases if v])
        all_matchup_players = list(set(team_a_players) | set(team_b_players))
        cutoff_date = self._get_reference_date() - pd.DateOffset(years=years)
        
        if self.dal is not None:
            squad_context_df = self.dal.get_balls(players=all_matchup_players)
            if 'start_date' in squad_context_df.columns:
                squad_context_df['start_date'] = pd.to_datetime(squad_context_df['start_date'], errors='coerce')
            squad_context_df = squad_context_df[squad_context_df['start_date'] >= cutoff_date]
        else:
            squad_context_df = self.raw_df[
                ((self.raw_df['striker'].isin(all_matchup_players)) | 
                 (self.raw_df['non_striker'].isin(all_matchup_players)) | 
                 (self.raw_df['bowler'].isin(all_matchup_players))) &
                (self.raw_df['start_date'] >= cutoff_date)
            ]

        squad_a = self._calculate_squad_metrics(team_a_name, team_a_players, years, context_df=squad_context_df)
        squad_b = self._calculate_squad_metrics(team_b_name, team_b_players, years, context_df=squad_context_df)
        matrix_a = self.analyze_squad_types(team_a_name, team_a_players, team_b_players, years, context_df=squad_context_df)
        matrix_b = self.analyze_squad_types(team_b_name, team_b_players, team_a_players, years, context_df=squad_context_df)

        matchups_a = {}
        for p in team_a_players:
            m_data = self.get_matchups(p, team_b_players, context_df=squad_context_df)
            if m_data: matchups_a[p] = m_data
            
        matchups_b = {}
        for p in team_b_players:
            m_data = self.get_matchups(p, team_a_players, context_df=squad_context_df)
            if m_data: matchups_b[p] = m_data

        player_stats_a = {}
        for p in team_a_players:
            player_stats_a[p] = self._get_stats(p, team_b_name, venue_pattern, years, context_df=squad_context_df)

        player_stats_b = {}
        for p in team_b_players:
            player_stats_b[p] = self._get_stats(p, team_a_name, venue_pattern, years, context_df=squad_context_df)

        return {
            'SquadComparison': {team_a_name: squad_a, team_b_name: squad_b},
            'TacticalMatrix': {team_a_name: matrix_a, team_b_name: matrix_b},
            'Matchups': {team_a_name: matchups_a, team_b_name: matchups_b},
            'PlayerStats': {team_a_name: player_stats_a, team_b_name: player_stats_b}
        }
    
    def _get_batting_milestones(self, df):
        if df.empty: return 0, 0, 0
        match_sums = df.groupby('match_id')['runs_off_bat'].sum()
        centuries = (match_sums >= 100).sum()
        fifties = ((match_sums >= 50) & (match_sums < 100)).sum()
        hs = match_sums.max() if not match_sums.empty else 0
        return centuries, fifties, hs

    def get_player_profile(self, player_name: str, opposition: Optional[str] = None, venue_id: Optional[str] = None, years: int = 10) -> Optional[PlayerProfile]:
        """
        Headless API: Fetches player profile data.
        """
        if player_name not in self.player_df['player'].values:
            matches = [p for p in self.player_df['player'].unique() if player_name.lower() in str(p).lower()]
            if matches: player_name = matches[0]
            else: return None
        
        cutoff_date = self._get_reference_date() - pd.DateOffset(years=years)
        p_stats = self.player_df[self.player_df['player'] == player_name].copy()
        
        # BATTING
        career_bat = p_stats[(p_stats['context'] == 'vs_team') & (p_stats['role'] == 'batting')].copy()
        bat_stats = BattingStats(0, 0, 0.0, 0.0, 0, 0, 0, [])
        if not career_bat.empty:
            runs = int(career_bat['runs'].sum())
            inns = int(career_bat['innings'].sum())
            outs = int(career_bat['dismissals'].sum())
            balls = int(career_bat['balls'].sum())
            avg = round(runs / outs, 2) if outs > 0 else runs
            sr = round((runs / balls) * 100, 1) if balls > 0 else 0.0
            
            if self.dal is not None:
                raw_bat = self.dal.get_balls(striker=player_name)
            else:
                raw_bat = self.raw_df[self.raw_df['striker'] == player_name]
            
            if not raw_bat.empty:
                 if 'start_date' in raw_bat.columns:
                     raw_bat['start_date'] = pd.to_datetime(raw_bat['start_date'], errors='coerce')
                 raw_bat = raw_bat[raw_bat['start_date'] >= cutoff_date]
                 c100, c50, hs = self._get_batting_milestones(raw_bat)
                 bat_stats = BattingStats(inns, runs, avg, sr, c100, c50, hs, [])

        # BOWLING
        career_bowl = p_stats[(p_stats['context'] == 'vs_team') & (p_stats['role'] == 'bowling')].copy()
        bowl_stats = None
        if not career_bowl.empty:
            b_runs = int(career_bowl['runs'].sum())
            b_balls = int(career_bowl['balls'].sum())
            b_wkts = int(career_bowl['dismissals'].sum())
            if b_balls > 60:
                b_avg = round(b_runs / b_wkts, 2) if b_wkts > 0 else 0.0
                b_econ = round((b_runs / b_balls) * 6, 2) if b_balls > 0 else 0.0
                bowl_stats = BowlingStats(0, b_wkts, b_avg, b_econ, "N/A", [])

        # CONTEXT
        vs_opponent_context = None
        if opposition and opposition != 'All':
            opp_bat_stats = None
            opp_bat = p_stats[(p_stats['context'] == 'vs_team') & (p_stats['role'] == 'batting') & (p_stats['opponent'] == opposition)]
            if not opp_bat.empty:
                r = int(opp_bat['runs'].sum()); i = int(opp_bat['innings'].sum()); o = int(opp_bat['dismissals'].sum()); b = int(opp_bat['balls'].sum())
                av = round(r / o, 2) if o > 0 else r; sr = round((r / b) * 100, 1) if b > 0 else 0.0
                vs_opponent_context = ContextStats(batting=BattingStats(i, r, av, sr, 0, 0, 0, []), bowling=None)

        venue_context = None
        if venue_id:
            aliases = get_venue_aliases(venue_id)
            ven_pattern = '|'.join([re.escape(v) for v in aliases])
            ven_bat = p_stats[(p_stats['context'] == 'at_venue') & (p_stats['role'] == 'batting') & (p_stats['opponent'].str.contains(ven_pattern, case=False, regex=True))]
            if not ven_bat.empty:
                r = int(ven_bat['runs'].sum()); i = int(ven_bat['innings'].sum()); o = int(ven_bat['dismissals'].sum()); b = int(ven_bat['balls'].sum())
                av = round(r / o, 2) if o > 0 else r; sr = round((r / b) * 100, 1) if b > 0 else 0.0
                venue_context = ContextStats(batting=BattingStats(i, r, av, sr, 0, 0, 0, []), bowling=None)

        return PlayerProfile(
            name=player_name,
            role=self._get_player_role(player_name),
            batting=bat_stats,
            bowling=bowl_stats,
            venue_stats=venue_context,
            vs_opponent_stats=vs_opponent_context
        )

    def analyze_player_profile(self, player_name: str, opposition: Optional[str] = None, venue_id: Optional[str] = None, active_bowlers: Optional[List[str]] = None, years: int = 10) -> Optional[PlayerProfile]:
        """
        Headless API: Context-Aware Player Profile retrieval.
        """
        if player_name not in self.player_df['player'].values:
            matches = [p for p in self.player_df['player'].unique() if player_name.lower() in str(p).lower()]
            if matches: player_name = matches[0]
            else: return None

        return self.get_player_profile(player_name, opposition, venue_id, years)
