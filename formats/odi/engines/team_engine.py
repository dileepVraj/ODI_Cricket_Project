from typing import List, Dict, Optional, Any, Union
import pandas as pd
import numpy as np
import os
from config.shared.venues import VENUE_MAP
from config.shared.team_colors import TEAM_COLORS
from formats.odi.renderers.team_renderer import TeamHTMLRenderer
from core.data_loader import load_csv_or_pickle

class TeamEngine:
    """
    🦁 The War Room (v6.0 - Engineering Standards Aligned).
    Handles Team-Level Analysis: Fortress Checks, H2H, Dominance, and Form.
    - HEADLESS: Logic returning pure data.
    - TYPED: Full Type Hint signatures.
    """
    def __init__(self, match_df: Optional[pd.DataFrame] = None, dal: Any = None):
        self.dal = dal
        if match_df is None and dal is not None:
            match_df = dal.get_matches()
        self.match_df = match_df if match_df is not None else pd.DataFrame()

    # =================================================================================
    # 🔧 CORE HELPERS
    # =================================================================================

    def _compute_reference_date(self) -> pd.Timestamp:
        """Use latest available match date to stabilize lookbacks."""
        df = self.match_df
        if df is not None and not df.empty and 'start_date' in df.columns:
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


    def _apply_smart_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filters match data based on meaningful competition criteria.

        Smart Filter Logic (v2.1):
        1. **No Result**: Excludes matches with no winner (NaN, None, Tied).
        2. **Short Innings**: Excludes innings shorter than 45 overs (270 balls) UNLESS the team was bowled out.
        3. **Both Short**: Flags matches where both innings were curtailed.
        """
        # --- ROBUST COLUMN MAPPING (v2.3) ---
        cols = df.columns.tolist()
        b1_col = next((c for c in cols if 'ball' in c and 'inn1' in c), None)
        w1_col = next((c for c in cols if 'wicket' in c and 'inn1' in c), None)
        b2_col = next((c for c in cols if 'ball' in c and 'inn2' in c), None)
        w2_col = next((c for c in cols if 'wicket' in c and 'inn2' in c), None)
        
        # Robust Team Name Detection
        t1_col = next((c for c in cols if 'team' in c and 'bat' in c and '1' in c), 'team_bat_1')
        t2_col = next((c for c in cols if 'team' in c and 'bat' in c and '2' in c), 'team_bat_2')

        # 1. Default Status
        df['status'] = '✅ Included'
        
        # 2. Check for explicit No Result / Abandoned
        if 'winner' in df.columns:
            pass
        
        # --- DEFINE CONDITIONS ---
        # Condition A: Short 1st Innings (< 45 ov & not all out)
        if b1_col and w1_col:
            is_short_1 = (df[b1_col] < 270) & (df[w1_col] < 10)
        else:
            is_short_1 = pd.Series([False]*len(df), index=df.index)
        
        # Condition B: Short 2nd Innings (< 45 ov & not all out & not natural win)
        if b2_col and w2_col and 'winner' in cols and 'score_inn2' in cols and 'score_inn1' in cols:
            nat_win = (df['winner'] == df[t2_col]) & (df['score_inn2'] > df['score_inn1'])
            is_short_2 = (df[b2_col] < 270) & (df[w2_col] < 10) & (~nat_win)
        else:
            is_short_2 = pd.Series([False]*len(df), index=df.index)
        
        # --- APPLY STATUS ---
        
        # 3. Apply individual flags first
        df.loc[is_short_1, 'status'] = '☔ Excluded (Short 1st)'
        df.loc[is_short_2, 'status'] = '☔ Excluded (Short 2nd)'
        
        # 4. Apply "Both Short" flag (Overwrites the specific ones)
        df.loc[is_short_1 & is_short_2, 'status'] = '☔ Excluded'
        
        return df

    def _get_avg_with_count(self, df: pd.DataFrame, col: str) -> str:
        """
        Calculates the mean of a column and formats it as "Avg (Count)".
        """
        if df.empty or col not in df.columns: return "-"
        
        # 🚨 CRITICAL: We must average the MATCH-LEVEL scores, not the row-level (duplicated) scores
        match_scores = df.groupby('match_id')[col].first()
        
        val = match_scores.mean()
        if pd.isna(val) or val == 0: return "-"
        
        return f"{int(val)} ({len(match_scores)})"

    def _get_form_guide(self, df: pd.DataFrame, team: str) -> str:
        """
        Generates a visual form guide (Last 5 matches) for a team.
        VECTORIZED: No iterrows loops.
        """
        if df.empty: return "-"
        
        # Take head(5) early to keep vector ops light. 
        # Sort by date descending (Newest first)
        recent = df.sort_values('start_date', ascending=False).head(5).copy()
        
        w = recent['winner'].astype(str).str.lower()
        t = team.lower()
        is_level = (recent['score_inn1'] == recent['score_inn2'])
        
        conditions = [
            (w == t),
            (w == 'tie') | (w.isin(['nan', 'no result']) & is_level),
            (w.isin(['nan', 'no result']))
        ]
        choices = ["✅", "🤝", "🌧️"]
        
        # Vectorized mapping
        results = np.select(conditions, choices, default="❌")
        return " ".join(results)

    def _calculate_team_stats(self, df: pd.DataFrame, team: str, is_home_analysis: bool = False) -> Dict[str, Union[int, str]]:
        """
        Computes detailed batting/chasing statistics for a specific team.
        """
        def get_val(s, func): return int(func(s)) if not s.empty and not pd.isna(func(s)) else "-"
        
        # 1. Define Valid Subsets (PRESERVED)
        valid_1st_mask = df['status'].isin(['✅ Included', '☔ Excluded (Short 2nd)'])
        valid_2nd_mask = df['status'] == '✅ Included'

        # 2. Filter for Team (PRESERVED)
        if is_home_analysis and team == 'Visitors':
            bat1 = df[(df['team_bat_1'] != df['home_team_ref']) & valid_1st_mask]
            bat2 = df[(df['team_bat_2'] != df['home_team_ref']) & valid_2nd_mask]
        else:
            bat1 = df[(df['team_bat_1'] == team) & valid_1st_mask]
            bat2 = df[(df['team_bat_2'] == team) & valid_2nd_mask]
            
        # 3. Winning Stats (PRESERVED)
        if 'is_defended' in df.columns:
            w1 = bat1[bat1['is_defended'] == True]
            w2 = bat2[bat2['is_chased'] == True]
        else:
            w1 = bat1[bat1['winner'] == bat1['team_bat_1']]
            w2 = bat2[bat2['winner'] == bat2['team_bat_2']]
            
        if 'is_chased' in df.columns: l2 = bat2[bat2['is_chased'] == False]
        else: l2 = bat2[bat2['winner'] != bat2['team_bat_2']]

        # 🚀 4. SMART FILTER: Competitive 2nd Innings (DELIBERATE DESIGN CHOICE)
        # ---------------------------------------------------------------------------------
        # NOTE FOR DEVELOPERS: We EXCLUDE 'Easy Chases' (Winning Score < 200) from the 
        # general 'Avg Score' metric. 
        # 
        # RATIONALE: If a team bowls out an opponent for 140 and chases it down easily, 
        # including that score would artificially drag down their "Batting Power" average.
        # We only want 'Competitive' chases (>= 200) or ANY loss to reflect in the BAT2 Avg.
        # 
        # IF USER ASKS: "Why is the count smaller than the total wins in the Avg Score?" 
        # ANSWER: We are protecting the team's chasing average from small Targets.
        # ---------------------------------------------------------------------------------
        is_win = bat2.index.isin(w2.index)
        mask_competitive = (~is_win) | (bat2['score_inn2'] >= 200)
        smart_bat2 = bat2[mask_competitive]

        return {
            'avg_1st': self._get_avg_with_count(bat1, 'score_inn1'),
            'high_1st': get_val(bat1['score_inn1'], np.max),
            'low_1st': get_val(bat1['score_inn1'], np.min),
            'avg_1st_win': self._get_avg_with_count(w1, 'score_inn1'),
            'low_defended': get_val(w1['score_inn1'], np.min),
            
            # Use 'smart_bat2' for the general average to protect the metric
            'avg_2nd': self._get_avg_with_count(smart_bat2, 'score_inn2'), 
            
            # Use raw 'w2' for success average (Win is a win regardless of score)
            'high_chased': get_val(w2['score_inn2'], np.max),
            'avg_succ': self._get_avg_with_count(w2, 'score_inn2'),
            'avg_fail': self._get_avg_with_count(l2, 'score_inn2')
        }

    # =================================================================================
    # 🎨 NEW GRID-BASED DISPLAY ENGINE (UPDATED WITH ALL METRICS)
    # =================================================================================

    # =================================================================================
    # 🎨 NEW GRID-BASED DISPLAY ENGINE (FULL METRICS RESTORED)
    # =================================================================================

    # REFACTORED: Removed legacy _display_report and _display_audit (NOW HEADLESS)

    def _build_report_data(self, df: pd.DataFrame, home_team: str, visitor_label: str, title: str, is_venue_mode: bool) -> List[Dict[str, Any]]:
        """
        Headless logic for computing report data.
        """
        matches = len(df)
        w = df['winner'].astype(str).str.lower().str.strip()
        h_clean = home_team.lower().strip()
        h_wins = len(df[w == h_clean])
        tie_nr = len(df[w.isin(['tie','no result','nan','none'])])
        
        if visitor_label == 'Visitors':
            v_wins = matches - h_wins - tie_nr
            vis_wins_df = df[(w != h_clean) & (~w.isin(['tie','no result','nan','none']))]
        else:
            v_clean = visitor_label.lower().strip()
            v_wins = len(df[w == v_clean])
            vis_wins_df = df[w == v_clean]
        
        home_wins_df = df[w == h_clean]
        h_win_bat1 = len(home_wins_df[home_wins_df['team_bat_1'] == home_team])
        h_win_bat2 = len(home_wins_df[home_wins_df['team_bat_2'] == home_team])
        
        if visitor_label == 'Visitors':
            v_win_bat1 = len(vis_wins_df[vis_wins_df['team_bat_2'] == home_team]) 
            v_win_bat2 = len(vis_wins_df[vis_wins_df['team_bat_1'] == home_team])
        else:
            v_win_bat1 = len(vis_wins_df[vis_wins_df['team_bat_1'] == visitor_label])
            v_win_bat2 = len(vis_wins_df[vis_wins_df['team_bat_2'] == visitor_label])

        dec = matches - tie_nr
        rate = int((h_wins/dec)*100) if dec > 0 else 0
        
        df_for_stats = df.copy()
        if is_venue_mode: df_for_stats['home_team_ref'] = home_team
        
        h_stats = self._calculate_team_stats(df_for_stats, home_team)
        v_stats = self._calculate_team_stats(df_for_stats, visitor_label, is_home_analysis=is_venue_mode)
        
        valid_1st = df[df['status'].isin(['✅ Included', '☔ Excluded (Short 2nd)'])]
        valid_2nd = df[df['status'] == '✅ Included']
        
        data = [
            {"Metric": "Matches Played", "Value": matches},
            {"Metric": "Tied / No Result", "Value": tie_nr},
            {"Metric": f"{home_team} Win %", "Value": f"{rate}%"},
            {"Metric": "--- HOME PERFORMANCE ---", "Value": ""},
            {"Metric": "Total Wins", "Value": h_wins},
            {"Metric": "Won Batting 1st (Defended)", "Value": h_win_bat1},
            {"Metric": "Won Batting 2nd (Chased)", "Value": h_win_bat2},
            {"Metric": "--- VISITOR PERFORMANCE ---", "Value": ""},
            {"Metric": "Total Wins", "Value": v_wins},
            {"Metric": "Won Batting 1st (Defended)", "Value": v_win_bat1},
            {"Metric": "Won Batting 2nd (Chased)", "Value": v_win_bat2},
            {"Metric": "--- VENUE AVERAGES ---", "Value": ""},
            {"Metric": "Overall Avg 1st Innings", "Value": self._get_avg_with_count(valid_1st, 'score_inn1')},
            {"Metric": "Overall Avg 2nd Innings", "Value": self._get_avg_with_count(valid_2nd, 'score_inn2')},
            {"Metric": "Avg 1st Innings Winning Score", "Value": self._get_avg_with_count(valid_1st[valid_1st['winner']==valid_1st['team_bat_1']], 'score_inn1')},
            {"Metric": f"--- BATTING 1ST ({home_team.upper()}) ---", "Value": ""},
            {"Metric": "Average 1st Innings", "Value": h_stats['avg_1st']},
            {"Metric": "Highest 1st Innings", "Value": h_stats['high_1st']},
            {"Metric": "Lowest 1st Innings", "Value": h_stats['low_1st']},
            {"Metric": "Avg Winning Score", "Value": h_stats['avg_1st_win']},
            {"Metric": "Lowest Defended Score", "Value": h_stats['low_defended']},
            {"Metric": f"--- BATTING 1ST ({visitor_label.upper()}) ---", "Value": ""},
            {"Metric": "Average 1st Innings", "Value": v_stats['avg_1st']},
            {"Metric": "Highest 1st Innings", "Value": v_stats['high_1st']},
            {"Metric": "Lowest 1st Innings", "Value": v_stats['low_1st']},
            {"Metric": "Avg Winning Score", "Value": v_stats['avg_1st_win']},
            {"Metric": "Lowest Defended Score", "Value": v_stats['low_defended']},
            {"Metric": f"--- CHASING ({home_team.upper()}) ---", "Value": ""},
            {"Metric": "Average 2nd Innings", "Value": h_stats['avg_2nd']},
            {"Metric": "Highest Chased", "Value": h_stats['high_chased']},
            {"Metric": "Avg Successful Chase", "Value": h_stats['avg_succ']},
            {"Metric": "Avg Failed Chase", "Value": h_stats['avg_fail']},
            {"Metric": f"--- CHASING ({visitor_label.upper()}) ---", "Value": ""},
            {"Metric": "Average 2nd Innings", "Value": v_stats['avg_2nd']},
            {"Metric": "Highest Chased", "Value": v_stats['high_chased']},
            {"Metric": "Avg Successful Chase", "Value": v_stats['avg_succ']},
            {"Metric": "Avg Failed Chase", "Value": v_stats['avg_fail']},
            {"Metric": "MATCH_IDS", "Value": ",".join(df['match_id'].astype(str).unique().tolist())}, 
        ]
        return data

    def _generate_matrix_report(self, matches: pd.DataFrame, team_name: str, title: str, is_away: bool = False) -> List[Dict[str, Any]]:
        """
        Generates a Multi-Opponent Matrix Report (Row-per-Opponent).

        Used for:
        - Home Dominance (how Team X performs at home vs everyone).
        - Away Performance (how Team X performs away vs everyone).
        - Global Performance (how Team X performs everywhere vs everyone).

        Args:
            matches (pd.DataFrame): Filtered DataFrame of matches to analyze.
            team_name (str): Focus Team Name.
            title (str): Title of the report.
            is_away (bool): If True, slightly adjusts the 'Opponent' column logic if needed.

        Returns:
            list: List of dictionaries (the raw data rows) for testing.
        """
        clean = self._apply_smart_filters(matches)
        valid = clean[clean['status'] == '✅ Included'].copy()
        
        # VECTORIZED OPPONENT DETECTION (Eliminated apply(axis=1) loop)
        clean['opponent'] = np.where(clean['team_bat_1'] == team_name, clean['team_bat_2'], clean['team_bat_1'])
        valid['opponent'] = np.where(valid['team_bat_1'] == team_name, valid['team_bat_2'], valid['team_bat_1'])
        
        top_teams = ['India', 'Australia', 'England', 'South Africa', 'New Zealand', 'Pakistan', 'Sri Lanka', 'West Indies', 'Bangladesh', 'Afghanistan']
        opponents = [t for t in top_teams if t != team_name]
        
        stats = []
        for opp in opponents:
            full = clean[clean['opponent'] == opp]; val = valid[valid['opponent'] == opp]
            if full.empty: continue
            
            wins = len(full[full['winner'] == team_name])
            loss = len(full[full['winner'] == opp])
            tie_nr = len(full) - wins - loss
            dec = len(full) - tie_nr
            pct = int((wins/dec)*100) if dec > 0 else 0
            
            stats.append({
                'Opponent': opp, 'Mat': len(full), 'Won': wins, 'Lost': loss, 'Tie/NR': tie_nr, 'Win %': f"{pct}%",
                'Last 5': self._get_form_guide(full, team_name),
                f'{team_name} Avg (1st)': self._get_avg_with_count(val[val['team_bat_1'] == team_name], 'score_inn1'),
                'Opp Avg (1st)': self._get_avg_with_count(val[val['team_bat_1'] != team_name], 'score_inn1'),
                'MATCH_IDS': ",".join(map(str, full['match_id'].unique().tolist()))
            })
            
        df = pd.DataFrame(stats).sort_values('Mat', ascending=False)
        
        top_full = clean[clean['opponent'].isin(top_teams)]
        top_val = valid[valid['opponent'].isin(top_teams)]
        t_w = len(top_full[top_full['winner'] == team_name])
        
        w_low = top_full['winner'].astype(str).str.lower().str.strip()
        t_low = team_name.lower().strip()
        is_loss = (w_low != t_low) & (~w_low.isin(['tie','no result','nan','none']))
        t_l = len(top_full[is_loss])
        
        t_nr = len(top_full) - t_w - t_l
        t_dec = len(top_full) - t_nr
        t_pct = int((t_w/t_dec)*100) if t_dec > 0 else 0
        
        ov = pd.DataFrame([{
            'Opponent': '⚡ OVERALL', 'Mat': len(top_full), 'Won': t_w, 'Lost': t_l, 'Tie/NR': t_nr, 'Win %': f"{t_pct}%",
            'Last 5': self._get_form_guide(top_full, team_name),
            f'{team_name} Avg (1st)': self._get_avg_with_count(top_val[top_val['team_bat_1'] == team_name], 'score_inn1'),
            'Opp Avg (1st)': self._get_avg_with_count(top_val[top_val['team_bat_1'] != team_name], 'score_inn1'),
            'MATCH_IDS': ",".join(map(str, top_full['match_id'].unique().tolist()))
        }])
        
        final_df = pd.concat([ov, df], ignore_index=True)
        # REFACTORED: Removed display() calls. Caller should use renderer.
        return final_df.to_dict(orient='records')

    # =================================================================================
    # 🔍 ANALYSIS FUNCTIONS (Public API)
    # =================================================================================

    def analyze_home_fortress(self, stadium_name: str, home_team: str, opp_team: str = 'All', years_back: int = 10, recorder: Any = None) -> List[Dict[str, Any]]:
        """
        Headless API: Analyzes a team's performance at a specific stadium.
        """
        stadium_id = stadium_name
        if stadium_name not in VENUE_MAP.values():
            for k, v in VENUE_MAP.items():
                if k.lower() in stadium_name.lower(): stadium_id = v; break
        
        cutoff = self._get_reference_date() - pd.DateOffset(years=years_back)
        vis_label = opp_team if opp_team != 'All' else "Visitors"
        vs_txt = f"vs {vis_label}"
        
        if self.dal is not None:
            v_matches = self.dal.get_matches(venue_id=stadium_id)
        else:
            v_matches = self.match_df[self.match_df['venue'] == stadium_id].copy()

        if not v_matches.empty and 'start_date' in v_matches.columns:
            v_matches['start_date'] = pd.to_datetime(v_matches['start_date'], errors='coerce')
            v_matches = v_matches[v_matches['start_date'] >= cutoff].copy()

        df = v_matches[(v_matches['team_bat_1'] == home_team) | (v_matches['team_bat_2'] == home_team)].copy()
        if opp_team != 'All': df = df[(df['team_bat_1'] == opp_team) | (df['team_bat_2'] == opp_team)].copy()
        
        if df.empty: return []
        
        df = self._apply_smart_filters(df)
        return self._build_report_data(df, home_team, vis_label, f"FORTRESS REPORT ({vs_txt})", is_venue_mode=True)

    def analyze_venue_matchup(self, stadium_name: str, home_team: str, opp_team: str, years_back: int = 5, recorder: Any = None) -> List[Dict[str, Any]]:
        """
        Headless API: Wrapper for venue-specific matchup analysis.
        """
        return self.analyze_home_fortress(stadium_name, home_team, opp_team, years_back, recorder)

    def analyze_venue_phases(self, stadium_id: str, home_team: Optional[str] = None, away_team: Optional[str] = None, years: int = 5, recorder: Any = None) -> Dict[str, Any]:
        """
        Headless API: Deep-dive Phase Analysis (Powerplay, Middle, Death) for a Venue.
        """
        match_source = self.match_df
        phase_df = None
        if self.dal is not None and hasattr(self.dal, "get_phase_stats"):
            phase_df = self.dal.get_phase_stats()

        if phase_df is None or phase_df.empty:
            file_path = 'formats/odi/data/processed_phase_stats.csv'
            if not os.path.exists(file_path): return {}
            phase_df = load_csv_or_pickle(file_path)

        # ID Normalization
        if 'match_id' in phase_df.columns:
            phase_df['match_id'] = phase_df['match_id'].astype(str).str.split('.').str[0].str.strip()

        # Smart Date Merge
        if 'start_date' not in phase_df.columns and 'match_id' in phase_df.columns:
            temp_map_df = match_source.copy()
            temp_map_df['match_id'] = temp_map_df['match_id'].astype(str).str.split('.').str[0].str.strip()
            date_map = temp_map_df.set_index('match_id')['start_date'].to_dict()
            phase_df['start_date'] = phase_df['match_id'].map(date_map)
            phase_df['start_date'] = pd.to_datetime(phase_df['start_date'])
        elif 'start_date' in phase_df.columns:
            phase_df['start_date'] = pd.to_datetime(phase_df['start_date'])

        # Filter by Venue
        from config.shared.venues import get_venue_aliases
        valid_aliases = get_venue_aliases(stadium_id)
        search_terms = [x.lower() for x in valid_aliases]
        venue_stats = phase_df[phase_df['venue'].str.lower().isin(search_terms)].copy()
        
        if venue_stats.empty:
            location_part = stadium_id.split('_')[-1].lower()
            if len(location_part) > 3: 
                venue_stats = phase_df[phase_df['venue'].str.lower().str.contains(location_part)]

        if venue_stats.empty: return {}

        # Apply Date Filter
        if 'start_date' in venue_stats.columns:
            cutoff = self._get_reference_date() - pd.DateOffset(years=years)
            venue_stats = venue_stats[venue_stats['start_date'] >= cutoff].copy()
            if venue_stats.empty: return {}
            start_year = cutoff.year
        else:
            start_year = "2015"

        if 'total_runs' not in venue_stats.columns:
            venue_stats['total_runs'] = venue_stats['pp_runs'].fillna(0) + venue_stats['mid_runs'].fillna(0) + venue_stats['dth_runs'].fillna(0)

        def get_summary(stats_df):
            agg_rules = {
                'pp_runs': ['mean', 'count'], 'pp_wkts': 'mean',
                'mid_runs': ['mean', 'count'], 'mid_wkts': 'mean',
                'dth_runs': ['mean', 'count'], 'dth_wkts': 'mean',
                'total_runs': ['mean', 'count']
            }
            summary = stats_df.groupby('innings').agg(agg_rules).round(1)
            res = {}
            for inn in [1, 2]:
                res[str(inn)] = {}
                for p in ['pp', 'mid', 'dth', 'total']:
                    col = f'{p}_runs' if p != 'total' else 'total_runs'
                    try:
                        res[str(inn)][p] = {
                            'avg': float(summary.loc[inn, (col, 'mean')]),
                            'n': int(summary.loc[inn, (col, 'count')]),
                            'wkts': float(summary.loc[inn, (f'{p}_wkts' if p != 'total' else 'pp_wkts', 'mean')]) if p != 'total' else 0.0
                        }
                    except (KeyError, TypeError, ValueError):
                        res[str(inn)][p] = {'avg': 0.0, 'n': 0, 'wkts': 0.0}
            return res

        report = {
            'stadium_id': stadium_id,
            'match_count': len(venue_stats),
            'years': years,
            'baseline': get_summary(venue_stats),
            'home_at_venue': None,
            'away_at_venue': None,
            'global_habits': None,
            "MATCH_IDS": ",".join(venue_stats['match_id'].unique().astype(str)) if 'match_id' in venue_stats.columns else ""
        }

        if home_team and home_team != 'All':
            h_venue = venue_stats[venue_stats['team'] == home_team]
            if not h_venue.empty: report['home_at_venue'] = {'team': home_team, 'stats': get_summary(h_venue)}
        
        if away_team and away_team != 'All':
            a_venue = venue_stats[venue_stats['team'] == away_team]
            if not a_venue.empty: report['away_at_venue'] = {'team': away_team, 'stats': get_summary(a_venue)}

        if home_team and away_team and away_team != 'All':
             h_stats = phase_df[phase_df['team'] == home_team]
             a_stats = phase_df[phase_df['team'] == away_team]
             if not h_stats.empty and not a_stats.empty:
                 def get_global(df):
                     return {
                         'pp_rr': round(df['pp_runs'].mean() / 10, 2),
                         'mid_rr': round(df['mid_runs'].mean() / 30, 2),
                         'dth_rr': round(df['dth_runs'].mean() / 10, 2),
                         'avg_score': round(df['total_runs'].mean(), 1)
                     }
                 report['global_habits'] = {
                     'home': get_global(h_stats),
                     'away': get_global(a_stats),
                     'start_year': start_year
                 }

        return report
    def analyze_venue_bias(self, stadium_name: str, years_back: int = 10, recorder: Any = None) -> Optional[Dict[str, Any]]:
        """
        Headless API: Determines if a venue has a significant "Bat First" or "Bowl First" advantage.
        """
        venue_id = stadium_name
        from config.shared.venues import get_venue_aliases
        valid_aliases = get_venue_aliases(stadium_name)
        search_terms = [x.lower() for x in valid_aliases]
        
        base_df = self.dal.get_matches() if self.dal is not None else self.match_df
        if base_df is None or base_df.empty: return None

        base_df = base_df.copy()
        if 'start_date' in base_df.columns:
            base_df['start_date'] = pd.to_datetime(base_df['start_date'], errors='coerce')
        
        available_venues = [v for v in base_df['venue'].unique() if str(v).lower() in search_terms]
        if available_venues:
            venue_id = available_venues[0]
        else:
            matches = [v for v in base_df['venue'].unique() if stadium_name.lower() in str(v).lower()]
            if matches: venue_id = matches[0]
            else: return None

        cutoff = self._get_reference_date() - pd.DateOffset(years=years_back)
        venue_matches = base_df[(base_df['venue'] == venue_id) & (base_df['start_date'] >= cutoff)].copy()
        clean_df = self._apply_smart_filters(venue_matches)
        
        valid_results = clean_df[clean_df['status'] != '☔ Excluded (No Result)']
        valid_stats = clean_df[clean_df['status'] == '✅ Included']
        
        if valid_results.empty: return None

        total = valid_results['match_id'].nunique()
        matches_won = valid_results.groupby('match_id').first()
        
        bat1_wins = len(matches_won[matches_won['winner'] == matches_won['team_bat_1']])
        chase_wins = len(matches_won[matches_won['winner'] == matches_won['team_bat_2']])
        
        bat1_pct = int((bat1_wins / total) * 100) if total > 0 else 0
        chase_pct = int((chase_wins / total) * 100) if total > 0 else 0
        
        bias = "NEUTRAL"
        if bat1_pct >= 55: bias = "BAT FIRST"
        elif chase_pct >= 55: bias = "BOWL FIRST"
        
        return {
            "venue_id": venue_id,
            "period": years_back,
            "total_matches": total,
            "bat1_wins": bat1_wins,
            "chase_wins": chase_wins,
            "bat1_win_pct": bat1_pct,
            "chase_win_pct": chase_pct,
            "bias_verdict": bias,
            "avg_1st_inn": self._get_avg_with_count(valid_stats, 'score_inn1'),
            "avg_2nd_inn": self._get_avg_with_count(valid_stats, 'score_inn2'),
            "MATCH_IDS": ",".join(valid_results['match_id'].unique().astype(str)),
            "raw_matches": valid_results.to_dict('records')
        }

        
    def analyze_global_h2h(self, home_team: str, opp_team: str, years_back: int = 5) -> Dict[str, Any]:
        """
        Headless API: Analyzes Head-to-Head performance between two teams globally.
        """
        cutoff = self._get_reference_date() - pd.DateOffset(years=years_back)

        if self.dal is not None:
            base_df = self.dal.get_matches(team_a=home_team, team_b=opp_team)
        else:
            base_df = self.match_df

        if base_df is None or base_df.empty: return {}

        if 'start_date' in base_df.columns:
            base_df['start_date'] = pd.to_datetime(base_df['start_date'], errors='coerce')

        mask = (((base_df['team_bat_1'] == home_team) & (base_df['team_bat_2'] == opp_team)) | 
                ((base_df['team_bat_1'] == opp_team) & (base_df['team_bat_2'] == home_team)))
        if 'start_date' in base_df.columns:
            mask = mask & (base_df['start_date'] >= cutoff)

        df = base_df[mask].copy()
        if df.empty: return {}
        
        df = self._apply_smart_filters(df)
        return self._build_report_data(df, home_team, opp_team, f"GLOBAL RIVALRY REPORT", False)

    def analyze_country_h2h(self, home_team: str, opp_team: str, country_name: str, years_back: int = 10, recorder: Optional[Any] = None) -> Dict[str, Any]:
        """
        Headless API: Analyzes H2H performance within a specific Host Country.
        """
        cutoff = self._get_reference_date() - pd.DateOffset(years=years_back)
        
        country_map = {
            'India': ['India', 'IND_'], 'Australia': ['Australia', 'AUS_'], 'England': ['England', 'ENG_'], 
            'South Africa': ['South Africa', 'SA_'], 'New Zealand': ['New Zealand', 'NZ_'], 
            'Sri Lanka': ['Sri Lanka', 'SL_'], 'West Indies': ['West Indies', 'WI_'], 
            'Pakistan': ['Pakistan', 'PAK_'], 'Bangladesh': ['Bangladesh', 'BAN_'], 
            'UAE': ['UAE', 'Dubai', 'Sharjah']
        }
        keys = country_map.get(country_name, [country_name])
        pat = '|'.join(keys)

        if self.dal is not None:
            base_df = self.dal.get_matches(team_a=home_team, team_b=opp_team)
        else:
            base_df = self.match_df

        if base_df is None or base_df.empty: return {}

        if 'start_date' in base_df.columns:
            base_df['start_date'] = pd.to_datetime(base_df['start_date'], errors='coerce')

        venue_col = 'venue_id' if 'venue_id' in base_df.columns else 'venue'
        v_mask = base_df[venue_col].astype(str).str.contains(pat, case=False, na=False)
        m_mask = (((base_df['team_bat_1'] == home_team) & (base_df['team_bat_2'] == opp_team)) | 
                  ((base_df['team_bat_1'] == opp_team) & (base_df['team_bat_2'] == home_team)))
        if 'start_date' in base_df.columns:
            m_mask = m_mask & (base_df['start_date'] >= cutoff)
            
        df = base_df[v_mask & m_mask].copy()
        if df.empty: return {}
        
        df = self._apply_smart_filters(df)
        return self._build_report_data(df, home_team, opp_team, f"HOST COUNTRY REPORT ({country_name})", False)

    def analyze_home_dominance(self, home_team: str, years_back: int = 10, recorder: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Headless API: Generates a Matrix Report of a team's performance at HOME.
        """
        cutoff = self._get_reference_date() - pd.DateOffset(years=years_back)
        c_codes = {'India':'IND_','England':'ENG_','Australia':'AUS_','South Africa':'SA_','New Zealand':'NZ_','Sri Lanka':'SL_','West Indies':'WI_','Pakistan':'PAK_','Bangladesh':'BAN_'}
        if home_team not in c_codes: return []

        if self.dal is not None:
            base_df = self.dal.get_matches(team_a=home_team)
        else:
            base_df = self.match_df

        if base_df is None or base_df.empty: return []

        if 'start_date' in base_df.columns:
            base_df['start_date'] = pd.to_datetime(base_df['start_date'], errors='coerce')

        venue_col = 'venue_id' if 'venue_id' in base_df.columns else 'venue'
        matches = base_df[(base_df[venue_col].astype(str).str.startswith(c_codes[home_team])) & 
                         ((base_df['team_bat_1'] == home_team) | (base_df['team_bat_2'] == home_team))].copy()
        
        if 'start_date' in matches.columns:
            matches = matches[matches['start_date'] >= cutoff].copy()
            
        if matches.empty: return []
        return self._generate_matrix_report(matches, home_team, "DOMINANCE MATRIX")

    def analyze_away_performance(self, team_name: str, years_back: int = 5, recorder: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Headless API: Generates a Matrix Report of a team's performance AWAY from home.
        """
        cutoff = self._get_reference_date() - pd.DateOffset(years=years_back)
        c_codes = {'India':'IND_','England':'ENG_','Australia':'AUS_','South Africa':'SA_','New Zealand':'NZ_','Sri Lanka':'SL_','West Indies':'WI_','Pakistan':'PAK_','Bangladesh':'BAN_'}
        if team_name not in c_codes: return []

        if self.dal is not None:
            base_df = self.dal.get_matches(team_a=team_name)
        else:
            base_df = self.match_df

        if base_df is None or base_df.empty: return []

        if 'start_date' in base_df.columns:
            base_df['start_date'] = pd.to_datetime(base_df['start_date'], errors='coerce')

        venue_col = 'venue_id' if 'venue_id' in base_df.columns else 'venue'
        matches = base_df[((base_df['team_bat_1'] == team_name) | (base_df['team_bat_2'] == team_name)) & 
                         (~base_df[venue_col].astype(str).str.startswith(c_codes[team_name]))].copy()
        
        if 'start_date' in matches.columns:
            matches = matches[matches['start_date'] >= cutoff].copy()
            
        if matches.empty: return []
        return self._generate_matrix_report(matches, team_name, "AWAY PERFORMANCE MATRIX", is_away=True)

    def analyze_global_performance(self, team_name: str, years_back: int = 5) -> List[Dict[str, Any]]:
        """
        Headless API: Generates a Matrix Report of a team's performance GLOBALLY.
        """
        cutoff = self._get_reference_date() - pd.DateOffset(years=years_back)

        if self.dal is not None:
            base_df = self.dal.get_matches(team_a=team_name)
        else:
            base_df = self.match_df

        if base_df is None or base_df.empty: return []

        if 'start_date' in base_df.columns:
            base_df['start_date'] = pd.to_datetime(base_df['start_date'], errors='coerce')

        matches = base_df[((base_df['team_bat_1'] == team_name) | (base_df['team_bat_2'] == team_name))].copy()
        if 'start_date' in matches.columns:
            matches = matches[matches['start_date'] >= cutoff].copy()
            
        if matches.empty: return []
        return self._generate_matrix_report(matches, team_name, "GLOBAL PERFORMANCE MATRIX")

    def analyze_continent_performance(self, team_name: str, continent: str, opp_team: str = 'All', years_back: int = 5) -> List[Dict[str, Any]]:
        """
        Headless API: Analyzes performance within a specific Continent/Region.
        """
        cutoff = self._get_reference_date() - pd.DateOffset(years=years_back)

        if self.dal is not None:
            base_df = self.dal.get_matches(team_a=team_name)
        else:
            base_df = self.match_df

        if base_df is None or base_df.empty: return []

        if 'start_date' in base_df.columns:
            base_df['start_date'] = pd.to_datetime(base_df['start_date'], errors='coerce')

        mask = ((base_df['team_bat_1'] == team_name) | (base_df['team_bat_2'] == team_name))
        if 'start_date' in base_df.columns:
            mask = mask & (base_df['start_date'] >= cutoff)

        if continent != 'All':
            c_map = {
                'Asia': ['IND_', 'PAK_', 'SL_', 'BAN_', 'AFG_', 'UAE_'], 
                'Europe': ['ENG_', 'IRE_', 'SCO_', 'NED_'], 
                'Oceania': ['AUS_', 'NZ_'], 
                'Africa': ['SA_', 'ZIM_'], 
                'Americas': ['WI_', 'USA_']
            }
            venue_col = 'venue_id' if 'venue_id' in base_df.columns else 'venue'
            if continent in c_map:
                mask = mask & (base_df[venue_col].astype(str).str.startswith(tuple(c_map[continent])))
            else: return []
            
        if opp_team != 'All':
            mask = mask & ((base_df['team_bat_1'] == opp_team) | (base_df['team_bat_2'] == opp_team))
            
        matches = base_df[mask].copy()
        if matches.empty: return []
        
        reg_label = "Global" if continent == 'All' else continent
        return self._generate_matrix_report(matches, team_name, f"PERFORMANCE MATRIX: {reg_label.upper()}")

    def analyze_team_form(self, team_name: str, opp_team: str = 'All', continent: str = 'All', limit: int = 5, recorder: Any = None) -> List[Dict[str, Any]]:
        """
        Headless logic for retrieving recent team form.
        """
        if self.dal is not None:
            base_df = self.dal.get_matches(team_a=team_name)
        else:
            base_df = self.match_df

        if 'start_date' in base_df.columns:
            base_df['start_date'] = pd.to_datetime(base_df['start_date'], errors='coerce')

        mask = (base_df['team_bat_1'] == team_name) | (base_df['team_bat_2'] == team_name)
        if opp_team != 'All': mask = mask & ((base_df['team_bat_1'] == opp_team) | (base_df['team_bat_2'] == opp_team))
        if continent != 'All':
            c_map = {'Asia':['IND_','PAK_','SL_','BAN_','AFG_','UAE_'], 'Europe':['ENG_','IRE_','SCO_','NED_'], 'Oceania':['AUS_','NZ_'], 'Africa':['SA_','ZIM_'], 'Americas':['WI_','USA_']}
            venue_col = 'venue_id' if 'venue_id' in base_df.columns else 'venue'
            if continent in c_map: mask = mask & (base_df[venue_col].astype(str).str.startswith(tuple(c_map[continent])))
            
        df = base_df[mask].copy()
        if df.empty: return []
        
        df = self._apply_smart_filters(df)
        recent = df.sort_values('start_date', ascending=False).head(limit)
        
        data = []
        for _, row in recent.iterrows():
            bat1 = (row['team_bat_1'] == team_name)
            opp = row['team_bat_2'] if bat1 else row['team_bat_1']
            w = str(row['winner'])
            
            # Determine Result
            is_level = (pd.notna(row['score_inn1']) and pd.notna(row['score_inn2']) and row['score_inn1'] == row['score_inn2'])

            if w == team_name: 
                res = "WIN"
            elif w.lower() == 'tie' or (w.lower() in ['nan','no result','none'] and is_level): 
                res = "TIE"
            elif w.lower() in ['nan','no result','none']: 
                res = "NR"
            else: 
                res = "LOSS"
            
            s_my = row['score_inn1'] if bat1 else row['score_inn2']
            s_opp = row['score_inn2'] if bat1 else row['score_inn1']
            l_my = "(1st)" if bat1 else "(2nd)"
            l_opp = "(2nd)" if bat1 else "(1st)"
            
            venue_val = row['venue_id'] if 'venue_id' in row and pd.notna(row['venue_id']) else row['venue']
            data.append({
                "Date": row['start_date'].strftime('%Y-%m-%d'),
                "Opponent": opp,
                "Venue": str(venue_val).split('_')[-1].title(),
                "Result": res,
                "TeamScore": f"{int(s_my) if pd.notna(s_my) else '-'} {l_my}",
                "OppScore": f"{int(s_opp) if pd.notna(s_opp) else '-'} {l_opp}",
                "RawResult": res[0] if res != "NR" else "NR"
            })
            
        return data
