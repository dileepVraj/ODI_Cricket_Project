import pandas as pd
import numpy as np
import os
from IPython.display import display, HTML
from venues import VENUE_MAP
from config.teams import TEAM_COLORS

class TeamEngine:
    """
    🦁 The War Room.
    Handles Team-Level Analysis: Fortress Checks, H2H, Dominance, and Form.
    """
    def __init__(self, match_df):
        self.match_df = match_df

    # =================================================================================
    # 🔧 CORE HELPERS
    # =================================================================================

    def _apply_smart_filters(self, df):
        """
        Filters match data based on meaningful competition criteria.

        Smart Filter Logic (v2.1):
        1. **No Result**: Excludes matches with no winner (NaN, None, Tied).
        2. **Short Innings**: Excludes innings shorter than 45 overs (270 balls) UNLESS the team was bowled out.
           - This prevents rain-curtailed matches from skewing averages (e.g., scoring 150/2 in 20 overs).
        3. **Both Short**: Flags matches where both innings were curtailed.

        Args:
            df (pd.DataFrame): The raw match dataframe.

        Returns:
            pd.DataFrame: DataFrame with a 'status' column indicating inclusion/exclusion reason.
        """
        # 1. Default Status
        df['status'] = '✅ Included'
        
        # 2. Check for explicit No Result / Abandoned
        # 🚨 UPDATED LOGIC (v2.2):
        # We NO LONGER blanket exclude 'No Result' or 'nan'.
        # Why? Some 'No Result' matches are actually Ties or ran full 50 overs (e.g. 213/7 vs 213/9).
        # We rely strictly on the "Short Innings" logic below to filter out rain-ruined games.
        if 'winner' in df.columns:
            # Only exclude purely empty result strings if needed, but let length check decide validity.
            pass
        
        # --- DEFINE CONDITIONS ---
        # Condition A: Short 1st Innings (< 45 ov & not all out)
        is_short_1 = (df['balls_inn1'] < 270) & (df['wickets_inn1'] < 10)
        
        # Condition B: Short 2nd Innings (< 45 ov & not all out & not natural win)
        nat_win = (df['winner'] == df['team_bat_2']) & (df['score_inn2'] > df['score_inn1'])
        is_short_2 = (df['balls_inn2'] < 270) & (df['wickets_inn2'] < 10) & (~nat_win)
        
        # --- APPLY STATUS ---
        
        # 3. Apply individual flags first
        df.loc[is_short_1, 'status'] = '☔ Excluded (Short 1st)'
        df.loc[is_short_2, 'status'] = '☔ Excluded (Short 2nd)'
        
        # 4. Apply "Both Short" flag (Overwrites the specific ones)
        df.loc[is_short_1 & is_short_2, 'status'] = '☔ Excluded'
        
        return df

    def _get_avg_with_count(self, df, col):
        """
        Calculates the mean of a column and formats it as "Avg (Count)".

        Args:
            df (pd.DataFrame): Dataframe containing the column.
            col (str): Column name to average (e.g., 'score_inn1').

        Returns:
            str: Formatted string "123 (45)" or "-" if empty.
        """
        if df.empty or col not in df.columns: return "-"
        val = df[col].mean()
        if pd.isna(val): return "-"
        return f"{int(val)} ({len(df)})"

    def _get_form_guide(self, df, team):
        """
        Generates a visual form guide (Last 5 matches) for a team.

        Args:
            df (pd.DataFrame): Match dataframe filtered for the specific context.
            team (str): The name of the team to check form for.

        Returns:
            str: A string of emojis/text representing results (e.g., "✅ ❌ ✅ 🤝 🌧️").
                 Newest match is first (leftmost).
        """
        if df.empty: return "-"
        res = []
        for _, r in df.sort_values('start_date', ascending=False).head(5).iterrows():
            w = str(r['winner']).lower(); t = team.lower()
            
            # Logic: Tie = Explicit Tie OR (No Result & Level Scores)
            is_level = (r['score_inn1'] == r['score_inn2'])
            
            if w == t: res.append("✅")
            elif w == 'tie' or (w in ['nan','no result'] and is_level): res.append("🤝")
            elif w in ['nan', 'no result']: res.append("🌧️")
            else: res.append("❌")
        return " ".join(res)

    def _calculate_team_stats(self, df, team, is_home_analysis=False):
        """
        Computes detailed batting/chasing statistics for a specific team.
        
        Implements 'Partial Validity Logic':
        - **1st Innings Stats**: computed using Included matches + Short 2nd Innings (valid 1st inn).
        - **2nd Innings Stats**: computed using only fully Included matches.
        - **Smart Chase Filter**: Excludes 'Easy Chases' (winning score < 200) from Average to avoid penalty for bowling well.

        Args:
            df (pd.DataFrame): The match dataframe (must have 'status' column).
            team (str): The team name to calculate stats for.
            is_home_analysis (bool): If True, handles 'Visitors' label dynamically.

        Returns:
            dict: Dictionary containing Avg/High/Low for Batting 1st and Chasing.
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

        # 🚀 4. SMART FILTER: Competitive 2nd Innings (NEW ADDITION)
        # We assume if the row is in 'w2', it was a win.
        # Logic: Keep if (Team Lost) OR (Team Won AND Score >= 200).
        # This removes "Easy Chases" (e.g. 150/2) from dragging down the average.
        
        is_win = bat2.index.isin(w2.index)
        # Keep if NOT a win OR Score is substantial
        mask_competitive = (~is_win) | (bat2['score_inn2'] >= 200)
        smart_bat2 = bat2[mask_competitive]

        return {
            'avg_1st': self._get_avg_with_count(bat1, 'score_inn1'),
            'high_1st': get_val(bat1['score_inn1'], np.max),
            'low_1st': get_val(bat1['score_inn1'], np.min),
            'avg_1st_win': self._get_avg_with_count(w1, 'score_inn1'),
            'low_defended': get_val(w1['score_inn1'], np.min),
            
            # 👇 UPDATED: Uses smart_bat2 instead of bat2
            'avg_2nd': self._get_avg_with_count(smart_bat2, 'score_inn2'), 
            
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

    def _display_report(self, data, t1, t2, title):
        """
        Renders a modern HTML Grid Dashboard for team statistics.

        Visual Components:
        - **Header**: Matches played, Win %, Tie/NR count.
        - **Team Cards**: Color-coded sections for Team 1 and Team 2 containing:
            - Win Breakdown (Wins, Defended, Chased).
            - Batting 1st Stats (Avg, High/Low, Win Score).
            - Chasing Stats (Avg, High Chased, Succ/Fail Chase Avgs).
        - **Venue Averages**: Overall venue stats for context.

        Args:
            data (list): List of dictionaries containing metrics and values.
            t1 (str): Home Team Name.
            t2 (str): Away Team Name (or 'Visitors').
            title (str): Title of the report.
        """
        # Parse Data into a List of Values for direct indexing
        d = [x['Value'] for x in data] 
        
        # Get Colors
        c1 = TEAM_COLORS.get(t1, "#333")
        c2 = TEAM_COLORS.get(t2, "#333")

        html_fixed = f"""
        <style>
            .dashboard-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-family: sans-serif; margin-bottom: 20px; }}
            .card {{ background: #f8f9fa; border: 1px solid #ddd; border-radius: 8px; padding: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
            .stat-row {{ display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 5px; border-bottom: 1px dashed #eee; }}
            .stat-val {{ font-weight: bold; color: #333; }}
            .section-title {{ font-size: 11px; font-weight: bold; color: #666; margin-top: 10px; margin-bottom: 5px; text-transform: uppercase; border-bottom: 1px solid #ccc; }}
            .win-stats {{ display: flex; justify-content: space-between; background: #e9ecef; padding: 5px; border-radius: 4px; font-size: 12px; margin-bottom: 10px; }}
        </style>

        <h3 style="margin:0 0 10px 0;">📊 {title}</h3>

        <div class="dashboard-grid">
            <div class="card" style="grid-column: span 2; display:flex; justify-content:space-around; text-align:center;">
                <div><div style="font-size:20px; font-weight:bold;">{d[0]}</div><div style="font-size:10px; color:#666;">MATCHES</div></div>
                <div><div style="font-size:20px; font-weight:bold; color:{c1}">{d[2]}</div><div style="font-size:10px; color:#666;">{t1} WIN %</div></div>
                <div><div style="font-size:20px; font-weight:bold;">{d[1]}</div><div style="font-size:10px; color:#666;">TIE/NR</div></div>
            </div>

            <div class="card" style="border-top: 3px solid {c1}">
                <div style="font-weight:bold; color:{c1}; font-size:16px; margin-bottom:5px;">{t1.upper()}</div>
                
                <div class="win-stats">
                    <span>🏆 <b>{d[4]}</b> Wins</span>
                    <span>🛡️ <b>{d[5]}</b> Def</span>
                    <span>🎯 <b>{d[6]}</b> Chs</span>
                </div>

                <div class="section-title">Batting 1st</div>
                <div class="stat-row"><span>Avg Score:</span> <span class="stat-val">{d[16]}</span></div>
                <div class="stat-row"><span>High / Low:</span> <span class="stat-val">{d[17]} / {d[18]}</span></div>
                <div class="stat-row"><span>Avg Win Score:</span> <span class="stat-val">{d[19]}</span></div>
                <div class="stat-row"><span>Lowest Defended:</span> <span class="stat-val">{d[20]}</span></div>

                <div class="section-title">Chasing</div>
                <div class="stat-row"><span>Avg Score:</span> <span class="stat-val">{d[28]}</span></div>
                <div class="stat-row"><span>Highest Chased:</span> <span class="stat-val">{d[29]}</span></div>
                <div class="stat-row"><span>Avg Succ. Chase:</span> <span class="stat-val">{d[30]}</span></div>
                <div class="stat-row"><span>Avg Fail Chase:</span> <span class="stat-val">{d[31]}</span></div>
            </div>

            <div class="card" style="border-top: 3px solid {c2}">
                <div style="font-weight:bold; color:{c2}; font-size:16px; margin-bottom:5px;">{t2.upper()}</div>
                
                <div class="win-stats">
                    <span>🏆 <b>{d[8]}</b> Wins</span>
                    <span>🛡️ <b>{d[9]}</b> Def</span>
                    <span>🎯 <b>{d[10]}</b> Chs</span>
                </div>

                <div class="section-title">Batting 1st</div>
                <div class="stat-row"><span>Avg Score:</span> <span class="stat-val">{d[22]}</span></div>
                <div class="stat-row"><span>High / Low:</span> <span class="stat-val">{d[23]} / {d[24]}</span></div>
                <div class="stat-row"><span>Avg Win Score:</span> <span class="stat-val">{d[25]}</span></div>
                <div class="stat-row"><span>Lowest Defended:</span> <span class="stat-val">{d[26]}</span></div>

                <div class="section-title">Chasing</div>
                <div class="stat-row"><span>Avg Score:</span> <span class="stat-val">{d[33]}</span></div>
                <div class="stat-row"><span>Highest Chased:</span> <span class="stat-val">{d[34]}</span></div>
                <div class="stat-row"><span>Avg Succ. Chase:</span> <span class="stat-val">{d[35]}</span></div>
                <div class="stat-row"><span>Avg Fail Chase:</span> <span class="stat-val">{d[36]}</span></div>
            </div>
            
            <div class="card" style="grid-column: span 2; background:#eef2f5;">
                <div style="font-weight:bold; color:#444; margin-bottom:8px; text-align:center;">🏟️ VENUE AVERAGES</div>
                <div style="display:flex; justify-content:space-around;">
                     <div><span>1st Inn Avg:</span> <b>{d[12]}</b></div>
                     <div><span>2nd Inn Avg:</span> <b>{d[13]}</b></div>
                     <div><span>Avg Winning Score:</span> <b>{d[14]}</b></div>
                </div>
            </div>
        </div>
        """
        display(HTML(html_fixed))

    def _display_audit(self, df, team):
        """
        Prints a raw data table of the matches included in the analysis for verification.
        """
        if df.empty: return
        print("\n🕵️‍♂️ MATCH AUDIT (Recent First)")
        # Robust column check
        c1 = 'display_inn1' if 'display_inn1' in df.columns else 'score_inn1'
        c2 = 'display_inn2' if 'display_inn2' in df.columns else 'score_inn2'
        cols = [c for c in ['start_date', 'venue', 'winner', 'team_bat_1', c1, 'team_bat_2', c2, 'status'] if c in df.columns]
        
        audit_df = df[cols].sort_values('start_date', ascending=False).rename(columns={c1: '1st Inn', c2: '2nd Inn'})
        
        # 🎨 WRAP IN SCROLLABLE CONTAINER (Responsive)
        # Removed 'white-space: nowrap' to allow wrapping (Fit Screen)
        html = f"""
        <div style="overflow-x: auto; width: 100%; font-size: 12px; margin-bottom: 20px;">
            {audit_df.to_html(index=False, classes='table table-striped table-hover table-sm', border=0)}
        </div>
        """
        display(HTML(html))

    def _build_and_display_report(self, df, home_team, visitor_label, title, is_venue_mode):
        """
        Orchestrates the calculation and display of standard match reports.

        Steps:
        1. Calculates Win Counts (Bat 1st vs Bat 2nd).
        2. Computes detailed Batting/Bowling stats via `_calculate_team_stats`.
        3. Packages all metrics into a standardized dictionary list.
        4. Calls `_display_report` to render the UI.

        Args:
            df (pd.DataFrame): Filtered match dataframe.
            home_team (str): The primary team (Home).
            visitor_label (str): The opponent or 'Visitors'.
            title (str): Dashboard title.
            is_venue_mode (bool): Flag to trigger venue-specific logic (e.g., generic 'Visitors').
        
        Returns:
            list: The data dictionary passed to the display engine (useful for testing).
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
        
        # 🚨 KEY CHANGE: Pass FULL dataframe with statuses to `_calculate_team_stats`
        # Also need `home_team_ref` for visitor logic
        df_for_stats = df.copy()
        if is_venue_mode: df_for_stats['home_team_ref'] = home_team
        
        h_stats = self._calculate_team_stats(df_for_stats, home_team)
        v_stats = self._calculate_team_stats(df_for_stats, visitor_label, is_home_analysis=is_venue_mode)
        
        # For Overall Venue Stats:
        # Valid 1st: Included + Short 2nd
        # Valid 2nd: Included only
        valid_1st = df[df['status'].isin(['✅ Included', '☔ Excluded (Short 2nd)'])]
        valid_2nd = df[df['status'] == '✅ Included']
        
        data = [
            {"Metric": "Matches Played", "Value": matches}, # 0
            {"Metric": "Tied / No Result", "Value": tie_nr}, # 1
            {"Metric": f"{home_team} Win %", "Value": f"{rate}%"}, # 2
            
            {"Metric": "--- HOME PERFORMANCE ---", "Value": ""}, # 3
            {"Metric": "Total Wins", "Value": h_wins}, # 4
            {"Metric": "Won Batting 1st (Defended)", "Value": h_win_bat1}, # 5
            {"Metric": "Won Batting 2nd (Chased)", "Value": h_win_bat2}, # 6
            
            {"Metric": "--- VISITOR PERFORMANCE ---", "Value": ""}, # 7
            {"Metric": "Total Wins", "Value": v_wins}, # 8
            {"Metric": "Won Batting 1st (Defended)", "Value": v_win_bat1}, # 9
            {"Metric": "Won Batting 2nd (Chased)", "Value": v_win_bat2}, # 10

            {"Metric": "--- VENUE AVERAGES ---", "Value": ""}, # 11
            {"Metric": "Overall Avg 1st Innings", "Value": self._get_avg_with_count(valid_1st, 'score_inn1')}, # 12
            {"Metric": "Overall Avg 2nd Innings", "Value": self._get_avg_with_count(valid_2nd, 'score_inn2')}, # 13
            {"Metric": "Avg 1st Innings Winning Score", "Value": self._get_avg_with_count(valid_1st[valid_1st['winner']==valid_1st['team_bat_1']], 'score_inn1')}, # 14

            {"Metric": f"--- BATTING 1ST ({home_team.upper()}) ---", "Value": ""}, # 15
            {"Metric": "Average 1st Innings", "Value": h_stats['avg_1st']}, # 16
            {"Metric": "Highest 1st Innings", "Value": h_stats['high_1st']}, # 17
            {"Metric": "Lowest 1st Innings", "Value": h_stats['low_1st']}, # 18
            {"Metric": "Avg Winning Score", "Value": h_stats['avg_1st_win']}, # 19
            {"Metric": "Lowest Defended Score", "Value": h_stats['low_defended']}, # 20
            
            {"Metric": f"--- BATTING 1ST ({visitor_label.upper()}) ---", "Value": ""}, # 21
            {"Metric": "Average 1st Innings", "Value": v_stats['avg_1st']}, # 22
            {"Metric": "Highest 1st Innings", "Value": v_stats['high_1st']}, # 23
            {"Metric": "Lowest 1st Innings", "Value": v_stats['low_1st']}, # 24
            {"Metric": "Avg Winning Score", "Value": v_stats['avg_1st_win']}, # 25
            {"Metric": "Lowest Defended Score", "Value": v_stats['low_defended']}, # 26
            
            {"Metric": f"--- CHASING ({home_team.upper()}) ---", "Value": ""}, # 27
            {"Metric": "Average 2nd Innings", "Value": h_stats['avg_2nd']}, # 28
            {"Metric": "Highest Chased", "Value": h_stats['high_chased']}, # 29
            {"Metric": "Avg Successful Chase", "Value": h_stats['avg_succ']}, # 30
            {"Metric": "Avg Failed Chase", "Value": h_stats['avg_fail']}, # 31
            
            {"Metric": f"--- CHASING ({visitor_label.upper()}) ---", "Value": ""}, # 32
            {"Metric": "Average 2nd Innings", "Value": v_stats['avg_2nd']}, # 33
            {"Metric": "Highest Chased", "Value": v_stats['high_chased']}, # 34
            {"Metric": "Avg Successful Chase", "Value": v_stats['avg_succ']}, # 35
            {"Metric": "Avg Failed Chase", "Value": v_stats['avg_fail']}, # 36
        ]
        self._display_report(data, home_team, visitor_label, title)
        self._display_audit(df, home_team)
        return data  # <--- RETURN DATA FOR TESTING

    def _generate_matrix_report(self, matches, team_name, title, is_away=False):
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
        
        def get_opp(row): return row['team_bat_2'] if row['team_bat_1'] == team_name else row['team_bat_1']
        clean['opponent'] = clean.apply(get_opp, axis=1)
        valid['opponent'] = valid.apply(get_opp, axis=1)
        
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
                'Opp Avg (1st)': self._get_avg_with_count(val[val['team_bat_1'] != team_name], 'score_inn1')
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
            'Opp Avg (1st)': self._get_avg_with_count(top_val[top_val['team_bat_1'] != team_name], 'score_inn1')
        }])
        
        final_df = pd.concat([ov, df], ignore_index=True)
        print(f"\n📊 {title}")
        display(final_df.style.hide(axis='index'))
        self._display_audit(matches, team_name)
        return final_df.to_dict(orient='records')

    # =================================================================================
    # 🔍 ANALYSIS FUNCTIONS (Public API)
    # =================================================================================

    def analyze_home_fortress(self, stadium_name, home_team, opp_team='All', years_back=10, recorder=None):
        """
        Analyzes a team's performance at a specific stadium (Fortress Check).
        
        Features:
        - Fuzzy Matches stadium name if ID not found.
        - Filters by Home Team (Bat 1 or Bat 2).
        - Optional: Filter by specific Opposition.

        Args:
            stadium_name (str): Venue ID or Name (e.g., 'Wankhede Stadium').
            home_team (str): The team claiming this venue as home.
            opp_team (str, optional): Specific opponent to check against. Defaults to 'All'.
            years_back (int): Lookback period in years.
            recorder (SnapshotRecorder, optional): For AI logging.

        Returns:
            list: Report data dictionary.
        """
        stadium_id = stadium_name
        if stadium_name not in VENUE_MAP.values():
            for k, v in VENUE_MAP.items():
                if k.lower() in stadium_name.lower(): stadium_id = v; break
        
        cutoff = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        vis_label = opp_team if opp_team != 'All' else "Visitors"
        vs_txt = f"vs {vis_label}"
        
        print(f"\n🏰 FORTRESS CHECK: {home_team} {vs_txt} at {stadium_id}")
        
        v_matches = self.match_df[(self.match_df['venue'] == stadium_id) & (self.match_df['start_date'] >= cutoff)].copy()
        df = v_matches[(v_matches['team_bat_1'] == home_team) | (v_matches['team_bat_2'] == home_team)].copy()
        if opp_team != 'All': df = df[(df['team_bat_1'] == opp_team) | (df['team_bat_2'] == opp_team)].copy()
        
        if df.empty: print(f"❌ No matches found."); return
        
        df = self._apply_smart_filters(df)
        df = self._apply_smart_filters(df)
        return self._build_and_display_report(df, home_team, vis_label, f"FORTRESS REPORT ({vs_txt})", is_venue_mode=True)

    # 🔗 BRIDGE FUNCTION (Connects Interface Button to Fortress Logic)
    def analyze_venue_matchup(self, stadium_name, home_team, opp_team, years_back=5, recorder=None):
        """
        Redirects the 'Venue Matchup' button to the Fortress function, 
        but ensures it runs in 'Matchup Mode' (specific opponent).
        """
        return self.analyze_home_fortress(stadium_name, home_team, opp_team, years_back, recorder)

    def analyze_venue_phases(self, stadium_id, home_team=None, away_team=None, years=5, recorder=None):
        """
        Deep-dive Phase Analysis (Powerplay, Middle, Death) for a Venue.
        
        Uses pre-processed data from `processed_phase_stats.csv`.
        Comparing:
        1. **Venue Baseline**: Avg Score/Wickets per phase for ALL teams.
        2. **Team History**: How Home/Away teams perform specifically at this venue.
        3. **Global Habits**: How the two teams perform generally (for strategy comparison).

        Args:
            stadium_id (str): Venue ID.
            home_team (str, optional): Home Team name for context.
            away_team (str, optional): Opponent name for matchup comparison.
            years (int): Lookback period.
        """
        import os
        from IPython.display import display, HTML
        from config.teams import TEAM_COLORS 
        # ... rest of function ... (No changes needed inside, just header)

        file_path = 'data/processed_phase_stats.csv'
        if not os.path.exists(file_path): print("❌ Error: 'processed_phase_stats.csv' not found."); return
        
        phase_df = pd.read_csv(file_path)
        
        # ---------------------------------------------------------
        # 🚨 NUCLEAR FIX: ID NORMALIZATION (Handles "518" vs "518.0")
        # ---------------------------------------------------------
        if 'match_id' in phase_df.columns:
            # remove decimals (.0), spaces, and force to string
            phase_df['match_id'] = phase_df['match_id'].astype(str).str.split('.').str[0].str.strip()

        # 2. Smart Date Merge
        if 'start_date' not in phase_df.columns and 'match_id' in phase_df.columns:
            # Prepare Master Map (Apply same normalization)
            temp_map_df = self.match_df.copy()
            temp_map_df['match_id'] = temp_map_df['match_id'].astype(str).str.split('.').str[0].str.strip()
            
            date_map = temp_map_df.set_index('match_id')['start_date'].to_dict()
            phase_df['start_date'] = phase_df['match_id'].map(date_map)
            phase_df['start_date'] = pd.to_datetime(phase_df['start_date'])

        elif 'start_date' in phase_df.columns:
            phase_df['start_date'] = pd.to_datetime(phase_df['start_date'])

        # 3. Filter by Venue (BEFORE Date Filter to debug availability)
        # Check standard alias OR fuzzy match location
        valid_aliases = [k for k, v in VENUE_MAP.items() if v == stadium_id]
        valid_aliases.append(stadium_id)
        search_terms = [x.lower() for x in valid_aliases]
        
        venue_stats = phase_df[phase_df['venue'].str.lower().isin(search_terms)].copy()
        
        # Fallback: Search by city name if ID match fails
        if venue_stats.empty:
            location_part = stadium_id.split('_')[-1].lower()
            if len(location_part) > 3: 
                venue_stats = phase_df[phase_df['venue'].str.lower().str.contains(location_part)]

        if venue_stats.empty: 
            print(f"❌ No phase data found for venue ID: '{stadium_id}' (Check 'processed_phase_stats.csv')")
            return

        # 4. Apply Date Filter & DEBUGGER
        if 'start_date' in venue_stats.columns:
            cutoff = pd.Timestamp.now() - pd.DateOffset(years=years)
            filtered_stats = venue_stats[venue_stats['start_date'] >= cutoff].copy()
            
            # 🔍 DEBUG: If filter kills all data, explain why
            if filtered_stats.empty and not venue_stats.empty:
                latest = venue_stats['start_date'].max()
                print(f"⚠️ Venue found, but NO matches in last {years} years.")
                print(f"   📅 Latest data available: {latest.date()} (Cutoff: {cutoff.date()})")
                return
            
            venue_stats = filtered_stats
            start_year = cutoff.year
        else:
            print("⚠️ Warning: Could not map dates. Using all data.")
            start_year = "2015"

        # Helper for Total Runs
        if 'total_runs' not in venue_stats.columns:
            venue_stats['total_runs'] = venue_stats['pp_runs'].fillna(0) + venue_stats['mid_runs'].fillna(0) + venue_stats['dth_runs'].fillna(0)

        # -----------------------------------------------------------
        # SECTION 1: OVERALL VENUE BASELINE (HTML STYLED)
        # -----------------------------------------------------------
        target_venue = venue_stats['venue'].iloc[0].upper()
        
        display(HTML(f"""
        <div style="background:#f4f4f4; padding:10px; border-radius:5px; margin-bottom:10px; border-left: 5px solid #666;">
            <h3 style="margin:0; color:#333;">🕒 PHASE ANALYSIS: {target_venue}</h3>
            <div style="font-size:12px; color:#666;">📅 Sample Size: {len(venue_stats)} Innings (Last {years} Years)</div>
        </div>
        """))
        
        agg_rules = {
            'pp_runs': ['mean', 'count'], 'pp_wkts': 'mean',
            'mid_runs': ['mean', 'count'], 'mid_wkts': 'mean',
            'dth_runs': ['mean', 'count'], 'dth_wkts': 'mean',
            'total_runs': ['mean', 'count']
        }
        
        def display_phase_html(stats_df, title, header_color="#333", bg_color="#fff"):
            summary = stats_df.groupby('innings').agg(agg_rules).round(1)
            def get_stat(inn, col, stat):
                try: return summary.loc[inn, (col, stat)]
                except: return 0

            rows = ""
            phases = [("POWERPLAY (1-10)", 'pp'), ("MIDDLE (11-40)", 'mid'), ("DEATH (41-50)", 'dth')]
            for name, p in phases:
                r1 = get_stat(1, f'{p}_runs', 'mean'); c1 = int(get_stat(1, f'{p}_runs', 'count')); w1 = get_stat(1, f'{p}_wkts', 'mean')
                str1 = f"<b>{r1}</b> ({c1}) / <span style='color:#d9534f'>{w1} w</span>"
                r2 = get_stat(2, f'{p}_runs', 'mean'); c2 = int(get_stat(2, f'{p}_runs', 'count')); w2 = get_stat(2, f'{p}_wkts', 'mean')
                str2 = f"<b>{r2}</b> ({c2}) / <span style='color:#d9534f'>{w2} w</span>"
                rows += f"<tr><td style='padding:5px;'>{name}</td><td style='padding:5px;'>{str1}</td><td style='padding:5px;'>{str2}</td></tr>"

            display(HTML(f"""
            <div style="margin-bottom:15px; border:1px solid #ddd; border-radius:5px; background:{bg_color};">
                <div style="background:{header_color}; color:#fff; padding:5px 10px; font-weight:bold; font-size:13px;">{title}</div>
                <table style="width:100%; font-size:13px; border-collapse:collapse;">
                    <tr style="background:#eee; text-align:left;">
                        <th style="padding:5px;">PHASE</th>
                        <th style="padding:5px;">1st INNINGS (Avg / N / Wkts)</th>
                        <th style="padding:5px;">2nd INNINGS (Avg / N / Wkts)</th>
                    </tr>
                    {rows}
                </table>
            </div>
            """))

        display_phase_html(venue_stats, f"🏟️ OVERALL VENUE BASELINE (All Teams)", header_color="#555")

        # -----------------------------------------------------------
        # SECTION 2: SPECIFIC TEAM HISTORY AT THIS VENUE (PRESERVED)
        # -----------------------------------------------------------
        if home_team and home_team != 'All':
            h_venue = venue_stats[venue_stats['team'] == home_team]
            if not h_venue.empty:
                c1 = TEAM_COLORS.get(home_team, "#004085")
                display_phase_html(h_venue, f"🏠 {home_team.upper()} AT THIS VENUE", header_color=c1, bg_color="#f8f9fa")
        
        if away_team and away_team != 'All':
            a_venue = venue_stats[venue_stats['team'] == away_team]
            if not a_venue.empty:
                c2 = TEAM_COLORS.get(away_team, "#856404")
                display_phase_html(a_venue, f"✈️ {away_team.upper()} AT THIS VENUE", header_color=c2, bg_color="#fff3cd")

        # -----------------------------------------------------------
        # SECTION 3: GLOBAL HABITS COMPARISON (HTML STYLED)
        # -----------------------------------------------------------
        if home_team and away_team and away_team != 'All':
            h_stats = phase_df[phase_df['team'] == home_team]
            a_stats = phase_df[phase_df['team'] == away_team]
            
            if not h_stats.empty and not a_stats.empty:
                c1 = TEAM_COLORS.get(home_team, "#333")
                c2 = TEAM_COLORS.get(away_team, "#333")
                
                display(HTML(f"<h4 style='border-bottom:2px solid #ccc; padding-bottom:5px; margin-top:20px;'>⚔️ GLOBAL HABITS (Any Venue, Since {start_year})</h4>"))

                def get_row_html(label, val_h, val_a, is_high_good):
                    diff = round(val_h - val_a, 1)
                    is_green = (diff > 0) if is_high_good else (diff < 0)
                    color = "#28a745" if is_green else "#dc3545"
                    arrow = "▲" if is_green else "▼"
                    return f"<tr style='border-bottom:1px dashed #eee;'><td style='padding:5px; color:#555;'>{label}</td><td style='padding:5px; font-weight:bold; color:{c1}'>{val_h:.1f}</td><td style='padding:5px; font-weight:bold; color:{c2}'>{val_a:.1f}</td><td style='padding:5px; color:{color}; font-weight:bold;'>{arrow} {abs(diff)}</td></tr>"

                # Scenario 1: Bat First
                h_avg_1 = h_stats[h_stats['innings'] == 1].mean(numeric_only=True)
                a_avg_1 = a_stats[a_stats['innings'] == 1].mean(numeric_only=True)
                
                metrics = [('pp_runs', 'Avg PP Runs', True), ('pp_wkts', 'Avg PP Wkts', False),
                           ('mid_runs', 'Avg Mid Runs', True), ('mid_wkts', 'Avg Mid Wkts', False),
                           ('dth_runs', 'Avg Death Runs', True), ('dth_wkts', 'Avg Death Wkts', False)]
                
                rows_1 = ""
                for col, lbl, flg in metrics:
                    rows_1 += get_row_html(lbl, h_avg_1.get(col,0), a_avg_1.get(col,0), flg)

                # Scenario 2: Chasing
                h_avg_2 = h_stats[h_stats['innings'] == 2].mean(numeric_only=True)
                a_avg_2 = a_stats[a_stats['innings'] == 2].mean(numeric_only=True)
                
                rows_2 = get_row_html("Avg PP Score", h_avg_2.get('pp_runs',0), a_avg_2.get('pp_runs',0), True)
                rows_2 += get_row_html("Avg Mid Wkts", h_avg_2.get('mid_wkts',0), a_avg_2.get('mid_wkts',0), False)
                rows_2 += get_row_html("Avg Death Wkts", h_avg_2.get('dth_wkts',0), a_avg_2.get('dth_wkts',0), False)

                display(HTML(f"""
                <div style="display:flex; gap:20px;">
                    <div style="flex:1;">
                        <div style="background:#e9ecef; padding:5px; font-weight:bold; text-align:center; color:#495057;">📉 SCENARIO 1: BAT FIRST</div>
                        <table style="width:100%; border-collapse:collapse; font-size:12px;">
                            <tr style="background:#f8f9fa;"><th>METRIC</th><th>{home_team}</th><th>{away_team}</th><th>DIFF</th></tr>
                            {rows_1}
                        </table>
                    </div>
                    <div style="flex:1;">
                        <div style="background:#e9ecef; padding:5px; font-weight:bold; text-align:center; color:#495057;">📉 SCENARIO 2: CHASING</div>
                        <table style="width:100%; border-collapse:collapse; font-size:12px;">
                            <tr style="background:#f8f9fa;"><th>METRIC</th><th>{home_team}</th><th>{away_team}</th><th>DIFF</th></tr>
                            {rows_2}
                        </table>
                    </div>
                </div>
                """))
                
                # Strategic Alerts (PRESERVED)
                venue_pp_1 = venue_stats[venue_stats['innings']==1]['pp_runs'].mean() if not venue_stats.empty else 0
                h_pp_1 = h_avg_1.get('pp_runs', 0)
                if h_pp_1 > venue_pp_1 + 5: 
                    display(HTML(f"<div style='margin-top:10px; padding:8px; background:#d4edda; color:#155724; border-left:4px solid #28a745;'><b>🚀 EDGE:</b> {home_team} (1st Inn) outscores this venue avg ({venue_pp_1:.1f}). BACK Powerplay.</div>"))
                
                h_wkts_chase = h_avg_2.get('mid_wkts', 0)
                if h_wkts_chase > 3.0: 
                    display(HTML(f"<div style='margin-top:5px; padding:8px; background:#f8d7da; color:#721c24; border-left:4px solid #dc3545;'><b>⚠️ RISK:</b> {home_team} collapses chasing (Avg {h_wkts_chase:.1f} wkts lost in Middle Overs). LAY Stability.</div>"))

        # 5. Audit (PRESERVED)
        if 'match_id' in venue_stats.columns:
            used_match_ids = venue_stats['match_id'].unique()
            # 🚨 FIX: Ensure main df IDs are normalized for audit lookup
            audit_mask = self.match_df['match_id'].astype(str).str.split('.').str[0].str.strip().isin(used_match_ids)
            audit_df = self.match_df[audit_mask]
            self._display_audit(audit_df, stadium_id)
            
        # 🚨 AI LOGGING: PHASE ANALYSIS (PRESERVED)
        if recorder:
            try:
                # 1. Overall Venue Stats
                venue_meta = {
                    "pp_avg_1st": float(round(venue_stats[venue_stats['innings']==1]['pp_runs'].mean(), 1)),
                    "pp_avg_2nd": float(round(venue_stats[venue_stats['innings']==2]['pp_runs'].mean(), 1)),
                    "dth_avg_1st": float(round(venue_stats[venue_stats['innings']==1]['dth_runs'].mean(), 1)),
                    "dth_avg_2nd": float(round(venue_stats[venue_stats['innings']==2]['dth_runs'].mean(), 1))
                }
                
                recorder.log_venue_intel("phase_analysis", {
                    "description_context": f"Phase Scoring Patterns at {stadium_id}",
                    "strategic_insight": "Compare Powerplay & Death scoring rates against global averages.",
                    "metrics": venue_meta
                }, years, len(venue_stats))
            except: pass

    def analyze_venue_bias(self, stadium_name, years_back=10, recorder=None):
        """
        Determines if a venue has a significant "Bat First" or "Bowl First" advantage.
        
        Logic:
        - Calculates Win % for Batting 1st vs Chasing.
        - Verdict is "BAT FIRST" if Win % >= 55%.
        - Verdict is "BOWL FIRST" if Chase Win % >= 55%.
        - Otherwise "NEUTRAL".

        Args:
            stadium_name (str): Venue Name.
            years_back (int): Lookback period.

        Outputs:
            Bias Verdict and detailed averages for 1st/2nd innings.
        """
        print(f"\n🪙 TOSS BIAS REPORT: {stadium_name}")
        venue_id = stadium_name
        
        # 1. Resolve Venue Name
        if stadium_name not in self.match_df['venue'].values:
            matches = [v for v in self.match_df['venue'].unique() if stadium_name.lower() in str(v).lower()]
            if matches: 
                venue_id = matches[0]
                print(f"🔎 Mapped '{stadium_name}' to -> '{venue_id}'")
            else: 
                print("❌ Venue not found."); return

        # 2. Filter by Date & Venue
        cutoff = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        venue_matches = self.match_df[
            (self.match_df['venue'] == venue_id) & 
            (self.match_df['start_date'] >= cutoff)
        ].copy()
        
        # 3. Apply Filters
        clean_df = self._apply_smart_filters(venue_matches)
        
        # 🚨 SPLIT LOGIC HERE 🚨
        # Dataset A: For Win Calculation (Include Rain/DL Results)
        valid_results = clean_df[clean_df['status'] != '☔ Excluded (No Result)']
        
        # Dataset B: For Score Calculation (Keep Strict to protect Averages)
        valid_stats = clean_df[clean_df['status'] == '✅ Included']
        
        if valid_results.empty: 
            print("❌ Not enough valid matches to analyze toss bias.")
            return

        # 4. Calculate Stats (Using Result Dataset)
        total = len(valid_results)
        bat1_wins = len(valid_results[valid_results['winner'] == valid_results['team_bat_1']])
        chase_wins = len(valid_results[valid_results['winner'] == valid_results['team_bat_2']])
        
        bat1_pct = int((bat1_wins / total) * 100)
        chase_pct = int((chase_wins / total) * 100)
        
        bias = "NEUTRAL ⚖️"
        if bat1_pct >= 55: bias = "BAT FIRST 🏏"
        elif chase_pct >= 55: bias = "BOWL FIRST 🥎"
        
        # 5. Display Summary
        print(f"📅 Period: Last {years_back} Years")
        print(f"🏟️ Matches Analyzed: {total} | 📊 Bias Verdict: {bias}")
        print("-" * 40)
        
        data = [
            {"Metric": "Win % Batting 1st", "Value": f"{bat1_pct}% ({bat1_wins})"},
            {"Metric": "Win % Chasing", "Value": f"{chase_pct}% ({chase_wins})"},
            # Use 'valid_stats' (Strict) for Averages
            {"Metric": "Avg 1st Innings Score", "Value": self._get_avg_with_count(valid_stats, 'score_inn1')},
            {"Metric": "Avg 2nd Innings Score", "Value": self._get_avg_with_count(valid_stats, 'score_inn2')},
        ]
        display(pd.DataFrame(data).style.hide(axis='index'))
        
        # 6. Show Match Audit
        self._display_audit(valid_results, venue_id)
        
    def analyze_global_h2h(self, home_team, opp_team, years_back=5):
        """
        Analyzes Head-to-Head performance between two teams globally (any venue).

        Args:
            home_team (str): Primary Team.
            opp_team (str): Opposition Team.
            years_back (int): Lookback period.

        Returns:
            list: Report data dictionary.
        """
        cutoff = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        print(f"\n🌍 GLOBAL H2H CHECK: {home_team} vs {opp_team}")
        mask = (((self.match_df['team_bat_1'] == home_team) & (self.match_df['team_bat_2'] == opp_team)) | ((self.match_df['team_bat_1'] == opp_team) & (self.match_df['team_bat_2'] == home_team))) & (self.match_df['start_date'] >= cutoff)
        df = self.match_df[mask].copy()
        if df.empty: print("❌ No global matches found."); return
        df = self._apply_smart_filters(df)
        return self._build_and_display_report(df, home_team, opp_team, f"GLOBAL RIVALRY REPORT", False)

    def analyze_country_h2h(self, home_team, opp_team, country_name, years_back=10, recorder=None):
        """
        Analyzes H2H performance within a specific Host Country.
        Useful for neutral venues (e.g., India vs Pak in UAE) or away tours.

        Args:
            home_team (str): Focus Team.
            opp_team (str): Opposition.
            country_name (str): Country Name (e.g., 'Australia', 'UAE').
            years_back (int): Lookback period.
        """
        cutoff = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        print(f"\n🗺️ COUNTRY CHECK: {home_team} vs {opp_team} in {country_name.upper()}")
        country_map = {
            'India': ['India', 'IND_'], 'Australia': ['Australia', 'AUS_'], 'England': ['England', 'ENG_'], 'South Africa': ['South Africa', 'SA_'], 'New Zealand': ['New Zealand', 'NZ_'], 'Sri Lanka': ['Sri Lanka', 'SL_'], 'West Indies': ['West Indies', 'WI_'], 'Pakistan': ['Pakistan', 'PAK_'], 'Bangladesh': ['Bangladesh', 'BAN_'], 'UAE': ['UAE', 'Dubai', 'Sharjah']
        }
        keys = country_map.get(country_name, [country_name])
        pat = '|'.join(keys)
        v_mask = self.match_df['venue'].str.contains(pat, case=False, na=False)
        m_mask = (((self.match_df['team_bat_1'] == home_team) & (self.match_df['team_bat_2'] == opp_team)) | ((self.match_df['team_bat_1'] == opp_team) & (self.match_df['team_bat_2'] == home_team))) & (self.match_df['start_date'] >= cutoff)
        df = self.match_df[v_mask & m_mask].copy()
        if df.empty: print(f"❌ No matches found."); return
        df = self._apply_smart_filters(df)
        return self._build_and_display_report(df, home_team, opp_team, f"HOST COUNTRY REPORT ({country_name})", False)

    def analyze_home_dominance(self, home_team, years_back=10, recorder=None):
        """
        Generates a Matrix Report of a team's performance at HOME against all major opponents.

        Args:
            home_team (str): The home team to analyze.
            years_back (int): Lookback period.
        
        Returns:
            list: Matrix data rows for testing.
        """
        print(f"\n🦁 HOME DOMINANCE: {home_team}"); cutoff = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        c_codes = {'India':'IND_','England':'ENG_','Australia':'AUS_','South Africa':'SA_','New Zealand':'NZ_','Sri Lanka':'SL_','West Indies':'WI_','Pakistan':'PAK_','Bangladesh':'BAN_'}
        if home_team not in c_codes: print("❌ Unknown code."); return
        matches = self.match_df[(self.match_df['venue'].str.startswith(c_codes[home_team])) & ((self.match_df['team_bat_1'] == home_team) | (self.match_df['team_bat_2'] == home_team)) & (self.match_df['start_date'] >= cutoff)].copy()
        if matches.empty: print("❌ No matches found."); return
        return self._generate_matrix_report(matches, home_team, "DOMINANCE MATRIX")

    def analyze_away_performance(self, team_name, years_back=5, recorder=None):
        """
        Generates a Matrix Report of a team's performance AWAY from home.
        
        - Filters OUT matches played in the home country.
        - Includes Neutral venues and Opposition Home venues.

        Args:
            team_name (str): Team to analyze.
            years_back (int): Lookback period.
        """
        print(f"\n✈️ AWAY PERFORMANCE: {team_name}"); cutoff = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        c_codes = {'India':'IND_','England':'ENG_','Australia':'AUS_','South Africa':'SA_','New Zealand':'NZ_','Sri Lanka':'SL_','West Indies':'WI_','Pakistan':'PAK_','Bangladesh':'BAN_'}
        if team_name not in c_codes: print("❌ Unknown code."); return
        matches = self.match_df[((self.match_df['team_bat_1'] == team_name) | (self.match_df['team_bat_2'] == team_name)) & (~self.match_df['venue'].astype(str).str.startswith(c_codes[team_name])) & (self.match_df['start_date'] >= cutoff)].copy()
        if matches.empty: print("❌ No matches found."); return
        return self._generate_matrix_report(matches, team_name, "AWAY PERFORMANCE MATRIX", is_away=True)

    def analyze_global_performance(self, team_name, years_back=5):
        """
        Generates a Matrix Report of a team's performance GLOBALLY (Home + Away + Neutral).
        """
        print(f"\n🌍 GLOBAL PERFORMANCE: {team_name} vs Top 10"); cutoff = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        matches = self.match_df[((self.match_df['team_bat_1'] == team_name) | (self.match_df['team_bat_2'] == team_name)) & (self.match_df['start_date'] >= cutoff)].copy()
        if matches.empty: print("❌ No matches found."); return
        return self._generate_matrix_report(matches, team_name, "GLOBAL PERFORMANCE MATRIX")

    def analyze_continent_performance(self, team_name, continent, opp_team='All', years_back=5):
        """
        Analyzes performance within a specific Continent/Region.
        
        Regions Supported: Asia, Europe, Oceania, Africa, Americas.

        Args:
            team_name (str): Focus Team.
            continent (str): Region Name.
            opp_team (str, optional): Specific Opponent or 'All'.
            years_back (int): Lookback.
        """
        reg = "Global" if continent == 'All' else continent
        print(f"\n🌏 REGION REPORT: {team_name} in {reg}"); cutoff = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        mask = ((self.match_df['team_bat_1'] == team_name) | (self.match_df['team_bat_2'] == team_name)) & (self.match_df['start_date'] >= cutoff)
        if continent != 'All':
            c_map = {'Asia':['IND_','PAK_','SL_','BAN_','AFG_','UAE_'], 'Europe':['ENG_','IRE_','SCO_','NED_'], 'Oceania':['AUS_','NZ_'], 'Africa':['SA_','ZIM_'], 'Americas':['WI_','USA_']}
            if continent in c_map: mask = mask & (self.match_df['venue'].astype(str).str.startswith(tuple(c_map[continent])))
            else: print("❌ Unknown Continent"); return
        if opp_team != 'All': mask = mask & ((self.match_df['team_bat_1'] == opp_team) | (self.match_df['team_bat_2'] == opp_team))
        matches = self.match_df[mask].copy()
        if matches.empty: print("❌ No matches found."); return
        if opp_team != 'All': self._build_and_display_report(self._apply_smart_filters(matches), team_name, opp_team, f"REGION REPORT ({reg})", False)
        else: return self._generate_matrix_report(matches, team_name, f"PERFORMANCE MATRIX: {reg.upper()}")

    def analyze_team_form(self, team_name, opp_team='All', continent='All', limit=5, recorder=None):
        """
        Displays recent form as a row of visual cards (Win/Loss/Tie).
        
        Args:
            team_name (str): Team.
            opp_team (str): Filter by opponent.
            continent (str): Filter by region.
            limit (int): Number of matches to show (default 5).
        """
        title = f"📉 FORM: {team_name}"
        if opp_team != 'All': title += f" vs {opp_team}"
        if continent != 'All': title += f" in {continent}"
        print(title)
        
        mask = (self.match_df['team_bat_1'] == team_name) | (self.match_df['team_bat_2'] == team_name)
        if opp_team != 'All': mask = mask & ((self.match_df['team_bat_1'] == opp_team) | (self.match_df['team_bat_2'] == opp_team))
        if continent != 'All':
            c_map = {'Asia':['IND_','PAK_','SL_','BAN_','AFG_','UAE_'], 'Europe':['ENG_','IRE_','SCO_','NED_'], 'Oceania':['AUS_','NZ_'], 'Africa':['SA_','ZIM_'], 'Americas':['WI_','USA_']}
            if continent in c_map: mask = mask & (self.match_df['venue'].astype(str).str.startswith(tuple(c_map[continent])))
            
        df = self.match_df[mask].copy()
        if df.empty: print("❌ No matches found."); return
        
        df = self._apply_smart_filters(df)
        recent = df.sort_values('start_date', ascending=False).head(limit)
        
        data = []
        form_str = [] # To store W/L/T string for AI
        
        for _, row in recent.iterrows():
            bat1 = (row['team_bat_1'] == team_name)
            opp = row['team_bat_2'] if bat1 else row['team_bat_1']
            w = str(row['winner'])
            
            # Determine Result for UI and AI
            is_level = (pd.notna(row['score_inn1']) and pd.notna(row['score_inn2']) and row['score_inn1'] == row['score_inn2'])

            if w == team_name: 
                res = "✅ WIN"
                form_str.append("W")
            elif w.lower() == 'tie' or (w.lower() in ['nan','no result','none'] and is_level): 
                res = "🤝 TIE"
                form_str.append("T")
            elif w.lower() in ['nan','no result','none']: 
                res = "🌧️ NR"
                form_str.append("NR")
            else: 
                res = "❌ LOSS"
                form_str.append("L")
            
            s_my = row['score_inn1'] if bat1 else row['score_inn2']
            s_opp = row['score_inn2'] if bat1 else row['score_inn1']
            l_my = "(1st)" if bat1 else "(2nd)"
            l_opp = "(2nd)" if bat1 else "(1st)"
            
            data.append({
                "Date": row['start_date'].strftime('%Y-%m-%d'), "Opponent": opp, "Venue": str(row['venue']).split('_')[-1].title(),
                "Result": res, f"{team_name}": f"{int(s_my) if pd.notna(s_my) else '-'} {l_my}", "Opp Score": f"{int(s_opp) if pd.notna(s_opp) else '-'} {l_opp}"
            })
            
        def col(v):
            c = 'black'
            if 'WIN' in v: c = 'green'
            elif 'LOSS' in v: c = 'red'
            elif 'TIE' in v: c = 'orange'
            elif 'NR' in v: c = 'gray'
            return f'color: {c}; font-weight: bold'
        
        display(pd.DataFrame(data).style.map(col, subset=['Result']).hide(axis='index'))
        self._display_audit(recent, team_name)

        