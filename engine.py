import pandas as pd
import numpy as np
from IPython.display import display

class CricketAnalyzer:
    # --- STADIUM TRANSLATOR ---
    VENUE_MAP = {
        'centurion': 'SuperSport Park',
        'joburg': 'Wanderers Stadium',
        'wanderers': 'Wanderers Stadium',
        'port elizabeth': 'St George\'s Park',
        'paarl': 'Boland Park',
        'mcg': 'Melbourne Cricket Ground',
        'scg': 'Sydney Cricket Ground',
        'gabba': 'Brisbane Cricket Ground',
        'hobart': 'Bellerive Oval',
        'perth': 'Perth Stadium',
        'waca': 'W.A.C.A. Ground',
        'wankhede': 'Wankhede',
        'eden gardens': 'Eden Gardens',
        'chinnaswamy': 'Chinnaswamy',
        'bangalore': 'Chinnaswamy',
        'chepauk': 'MA Chidambaram',    
        'chennai': 'MA Chidambaram',
        'hyderabad': 'Rajiv Gandhi',
        'ahmedabad': 'Narendra Modi',
        'motera': 'Narendra Modi',
        'dharamshala': 'Himachal',
        'lords': 'Lord\'s',
        'oval': 'The Oval',
        'old trafford': 'Old Trafford',
        'edgbaston': 'Edgbaston',
        'headingley': 'Headingley',
        'trent bridge': 'Trent Bridge',
    }

    def __init__(self, filepath):
        print(f"⚙️ Initializing Engine...")
        print(f"📂 Loading Database: {filepath}")
        
        self.raw_df = pd.read_csv(filepath, low_memory=False)
        self.raw_df['start_date'] = pd.to_datetime(self.raw_df['start_date'], errors='coerce')
        self.raw_df['year'] = self.raw_df['start_date'].dt.year
        
        print(f"   Raw Data: {len(self.raw_df)} balls loaded.")
        self._create_match_summary()
        print(f"✅ Engine Ready! Condensed into {len(self.match_df)} unique matches.")
        print(f"   Date Range: {self.match_df['year'].min()} to {self.match_df['year'].max()}")

    def _create_match_summary(self):
        print("   🔨 Building Match Summary (Filtering Super Overs)...")
        
        # 1. Detect Wicket Column
        wicket_col = 'is_wicket' if 'is_wicket' in self.raw_df.columns else 'player_dismissed'
        agg_func = 'sum' if wicket_col == 'is_wicket' else 'count'

        # 2. Aggregation
        innings_stats = self.raw_df.groupby(['match_id', 'innings']).agg({
            'runs_off_bat': 'sum', 
            'extras': 'sum',
            'ball': 'count',
            wicket_col: agg_func 
        }).reset_index()
        
        # --- FIX: REMOVE GHOST INNINGS (3, 4, etc) ---
        innings_stats = innings_stats[innings_stats['innings'].isin([1, 2])]
        
        innings_stats.rename(columns={wicket_col: 'wickets'}, inplace=True)
        innings_stats['total_score'] = innings_stats['runs_off_bat'] + innings_stats['extras']
        
        # 3. Formatted Score String
        def format_score(row):
            overs = row['ball'] // 6
            balls = row['ball'] % 6
            return f"{int(row['total_score'])}/{int(row['wickets'])} ({overs}.{balls})"

        innings_stats['score_display'] = innings_stats.apply(format_score, axis=1)

        # 4. Pivots
        scores_pivot = innings_stats.pivot(index='match_id', columns='innings', values='total_score').reset_index()
        scores_pivot.rename(columns={1: 'score_inn1', 2: 'score_inn2'}, inplace=True)
        if 'score_inn1' not in scores_pivot.columns: scores_pivot['score_inn1'] = 0
        if 'score_inn2' not in scores_pivot.columns: scores_pivot['score_inn2'] = 0
        scores_pivot.fillna(0, inplace=True)
        
        balls_pivot = innings_stats.pivot(index='match_id', columns='innings', values='ball').reset_index()
        balls_pivot.rename(columns={1: 'balls_inn1', 2: 'balls_inn2'}, inplace=True)
        if 'balls_inn1' not in balls_pivot.columns: balls_pivot['balls_inn1'] = 0
        if 'balls_inn2' not in balls_pivot.columns: balls_pivot['balls_inn2'] = 0
        balls_pivot.fillna(0, inplace=True)
        
        wickets_pivot = innings_stats.pivot(index='match_id', columns='innings', values='wickets').reset_index()
        wickets_pivot.rename(columns={1: 'wickets_inn1', 2: 'wickets_inn2'}, inplace=True)
        if 'wickets_inn1' not in wickets_pivot.columns: wickets_pivot['wickets_inn1'] = 0
        if 'wickets_inn2' not in wickets_pivot.columns: wickets_pivot['wickets_inn2'] = 0
        wickets_pivot.fillna(0, inplace=True)

        display_pivot = innings_stats.pivot(index='match_id', columns='innings', values='score_display').reset_index()
        display_pivot.rename(columns={1: 'display_inn1', 2: 'display_inn2'}, inplace=True)
        if 'display_inn1' not in display_pivot.columns: display_pivot['display_inn1'] = "DNB"
        if 'display_inn2' not in display_pivot.columns: display_pivot['display_inn2'] = "DNB"
        display_pivot.fillna("DNB", inplace=True)
        
        # 5. Merge ALL Data
        cols_to_keep = ['match_id', 'season', 'year', 'start_date', 'venue', 'batting_team', 'bowling_team', 'winner']
        if 'method' in self.raw_df.columns: cols_to_keep.append('method')

        meta_data = self.raw_df.drop_duplicates(subset='match_id')[cols_to_keep].copy()
        if 'method' not in meta_data.columns: meta_data['method'] = np.nan
            
        meta_data.rename(columns={'batting_team': 'team_bat_1', 'bowling_team': 'team_bat_2'}, inplace=True)
        
        self.match_df = pd.merge(meta_data, scores_pivot, on='match_id', how='left')
        self.match_df = pd.merge(self.match_df, balls_pivot, on='match_id', how='left')
        self.match_df = pd.merge(self.match_df, wickets_pivot, on='match_id', how='left')
        self.match_df = pd.merge(self.match_df, display_pivot, on='match_id', how='left')
        
        self.match_df['is_defended'] = self.match_df['winner'] == self.match_df['team_bat_1']
        self.match_df['is_chased'] = self.match_df['winner'] == self.match_df['team_bat_2']

    def _resolve_stadium(self, input_name):
        clean_input = input_name.lower().strip()
        if clean_input in self.VENUE_MAP: return self.VENUE_MAP[clean_input]
        return input_name
    
    # --- SMART FILTER LOGIC ---
    def _apply_smart_filters(self, df):
        df['status'] = '✅ Included'
        if 'method' in df.columns: df.loc[df['method'].notna(), 'status'] = '❌ Excluded (Rain/DL)'
        df.loc[df['winner'].isin(['No Result', np.nan]), 'status'] = '❌ Excluded (No Result)'
        
        # Short Game Check ( < 48 overs played AND < 10 wickets lost)
        mask_short_game = (df['balls_inn1'] < 288) & (df['wickets_inn1'] < 10)
        df.loc[mask_short_game, 'status'] = '❌ Excluded (Shortened)'
        
        return df

    # --- ADVANCED STATS HELPER (Upgraded to handle Chasing Split) ---
    def _calculate_team_stats(self, df, team_name, is_home_analysis=False):
        if is_home_analysis and team_name == 'Visitors':
            bat1 = df[df['team_bat_1'] != df['home_team_ref']]
        else:
            bat1 = df[df['team_bat_1'] == team_name]
            
        avg_1st = int(bat1['score_inn1'].mean()) if not bat1.empty else 0
        high_1st = int(bat1['score_inn1'].max()) if not bat1.empty else 0
        low_1st = int(bat1['score_inn1'].min()) if not bat1.empty else 0
        
        bat1_win = bat1[bat1['is_defended'] == True]
        avg_1st_win = int(bat1_win['score_inn1'].mean()) if not bat1_win.empty else 0
        low_defended = int(bat1_win['score_inn1'].min()) if not bat1_win.empty else 0
        
        # CHASING LOGIC
        if is_home_analysis and team_name == 'Visitors':
            chase = df[df['team_bat_2'] != df['home_team_ref']]
        else:
            chase = df[df['team_bat_2'] == team_name]
            
        avg_2nd = int(chase['score_inn2'].mean()) if not chase.empty else 0
        
        # Successful Chase
        chase_win = chase[chase['is_chased'] == True]
        high_chased = int(chase_win['score_inn2'].max()) if not chase_win.empty else 0
        avg_succ_chase = int(chase_win['score_inn2'].mean()) if not chase_win.empty else 0
        
        # Failed Chase
        chase_loss = chase[chase['is_chased'] == False]
        avg_fail_chase = int(chase_loss['score_inn2'].mean()) if not chase_loss.empty else 0
        
        return {
            'avg_1st': avg_1st, 'avg_1st_win': avg_1st_win, 
            'high_1st': high_1st, 'low_1st': low_1st, 'low_defended': low_defended,
            'avg_2nd': avg_2nd, 
            'high_chased': high_chased, 'avg_succ': avg_succ_chase, 'avg_fail': avg_fail_chase
        }

    # -------------------------------------------------------------------------------------
    # FUNCTION 1: VENUE ANALYSIS (Handles "Fortress" & "Matchup")
    # -------------------------------------------------------------------------------------
    def analyze_home_fortress(self, stadium_name, home_team, opp_team='All', years_back=10):
        stadium_name = self._resolve_stadium(stadium_name)
        self.match_df['start_date'] = pd.to_datetime(self.match_df['start_date'])
        
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        
        # Labels
        visitor_label = opp_team if opp_team != 'All' else "Visitors"
        vs_text = f"vs {visitor_label}"
        print(f"\n🏰 FORTRESS CHECK: {home_team} {vs_text} at {stadium_name}")
        print(f"📅 Analyzing data from the last {years_back} years...")
        
        # Filter 1: Venue & Date
        venue_matches = self.match_df[
            (self.match_df['venue'].str.contains(stadium_name, case=False, na=False)) &
            (self.match_df['start_date'] >= cutoff_date)
        ].copy()
        
        # Filter 2: Home Team
        df = venue_matches[(venue_matches['team_bat_1'] == home_team) | (venue_matches['team_bat_2'] == home_team)].copy()
        
        # Filter 3: Opponent (If Specific)
        if opp_team != 'All':
            df = df[(df['team_bat_1'] == opp_team) | (df['team_bat_2'] == opp_team)].copy()
        
        if df.empty:
            print(f"❌ No matches found for {home_team} {vs_text} at this venue.")
            return

        # --- GENERATE REPORT ---
        # We reuse a shared logic function to avoid code duplication
        self._build_and_display_report(df, home_team, visitor_label, f"FORTRESS REPORT ({vs_text})", is_venue_mode=True)


    # -------------------------------------------------------------------------------------
    # FUNCTION 2: GLOBAL H2H ANALYSIS (Handles "Global Stats")
    # -------------------------------------------------------------------------------------
    def analyze_global_h2h(self, home_team, opp_team, years_back=5):
        self.match_df['start_date'] = pd.to_datetime(self.match_df['start_date'])
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        
        print(f"\n🌍 GLOBAL H2H CHECK: {home_team} vs {opp_team}")
        print(f"📅 Analyzing data from the last {years_back} years (All Venues)...")
        
        # Filter: Date & Matchup
        mask = (
            ((self.match_df['team_bat_1'] == home_team) & (self.match_df['team_bat_2'] == opp_team)) |
            ((self.match_df['team_bat_1'] == opp_team) & (self.match_df['team_bat_2'] == home_team))
        ) & (self.match_df['start_date'] >= cutoff_date)
        
        df = self.match_df[mask].copy()
        
        if df.empty:
            print(f"❌ No global matches found between {home_team} and {opp_team}.")
            return

        # --- GENERATE REPORT ---
        self._build_and_display_report(df, home_team, opp_team, f"GLOBAL RIVALRY REPORT", is_venue_mode=False)


    # -------------------------------------------------------------------------------------
    # SHARED REPORT GENERATOR (Internal Logic)
    # -------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------
    # SHARED REPORT GENERATOR (Internal Logic)
    # -------------------------------------------------------------------------------------
    def _build_and_display_report(self, df, home_team, visitor_label, title, is_venue_mode):
        # Win/Loss Counts
        matches_played = len(df)
        home_wins_df = df[df['winner'] == home_team]
        won_home = len(home_wins_df)
        won_home_bat1 = len(home_wins_df[home_wins_df['team_bat_1'] == home_team])
        won_home_bat2 = len(home_wins_df[home_wins_df['team_bat_2'] == home_team])

        if visitor_label == 'Visitors':
            vis_wins_df = df[(df['winner'] != home_team) & (df['winner'] != 'Tie') & (df['winner'].notna())]
        else:
            vis_wins_df = df[df['winner'] == visitor_label]
            
        won_visitor = len(vis_wins_df)
        won_vis_bat1 = len(vis_wins_df[vis_wins_df['team_bat_2'] == home_team]) 
        won_vis_bat2 = len(vis_wins_df[vis_wins_df['team_bat_1'] == home_team]) 
        
        invalid_results = matches_played - won_home - won_visitor
        win_rate = int((won_home / matches_played) * 100) if matches_played > 0 else 0
        
        # Stats Calculation
        df = self._apply_smart_filters(df)
        stats_df = df[df['status'] == '✅ Included'].copy()
        
        # Set Home Ref for the helper
        stats_df['home_team_ref'] = home_team 
        
        # Overall Averages
        overall_avg_1 = int(stats_df['score_inn1'].mean()) if not stats_df.empty else 0
        overall_avg_2 = int(stats_df['score_inn2'].mean()) if not stats_df.empty else 0
        bat1_winners = stats_df[stats_df['winner'] == stats_df['team_bat_1']]
        overall_avg_win = int(bat1_winners['score_inn1'].mean()) if not bat1_winners.empty else 0
        
        # Detailed Stats
        h_stats = self._calculate_team_stats(stats_df, home_team)
        v_stats = self._calculate_team_stats(stats_df, visitor_label, is_home_analysis=True)

        report_data = [
            {"Metric": "Matches Played", "Value": matches_played},
            {"Metric": "Tied / No Result", "Value": invalid_results},
            {"Metric": f"{home_team} Win %", "Value": f"{win_rate}%"},

            {"Metric": f"--- {home_team.upper()} WINS ---", "Value": "---"},
            {"Metric": "Total Wins", "Value": won_home},
            {"Metric": "Won Batting 1st (Defended)", "Value": won_home_bat1},
            {"Metric": "Won Batting 2nd (Chased)", "Value": won_home_bat2},
            
            {"Metric": f"--- {visitor_label.upper()} WINS ---", "Value": "---"},
            {"Metric": "Total Wins", "Value": won_visitor},
            {"Metric": "Won Batting 1st (Defended)", "Value": won_vis_bat1},
            {"Metric": "Won Batting 2nd (Chased)", "Value": won_vis_bat2},
            
            {"Metric": "--- OVERALL SCORING STATS ---", "Value": "---"},
            {"Metric": "Overall Avg 1st Innings", "Value": overall_avg_1},
            {"Metric": "Overall Avg 2nd Innings", "Value": overall_avg_2},
            {"Metric": "Avg 1st Innings Winning Score", "Value": overall_avg_win},
            
            {"Metric": f"--- BATTING 1ST: {home_team} ---", "Value": "---"},
            {"Metric": "Average 1st Innings", "Value": h_stats['avg_1st']},
            {"Metric": "Highest 1st Innings", "Value": h_stats['high_1st']},
            {"Metric": "Lowest 1st Innings", "Value": h_stats['low_1st']},
            {"Metric": "Avg Winning Score", "Value": h_stats['avg_1st_win']},
            {"Metric": "Lowest Defended Score", "Value": h_stats['low_defended']},
            
            {"Metric": f"--- BATTING 1ST: {visitor_label} ---", "Value": "---"},
            {"Metric": "Average 1st Innings", "Value": v_stats['avg_1st']},
            {"Metric": "Highest 1st Innings", "Value": v_stats['high_1st']},
            {"Metric": "Lowest 1st Innings", "Value": v_stats['low_1st']},
            {"Metric": "Avg Winning Score", "Value": v_stats['avg_1st_win']},
            {"Metric": "Lowest Defended Score", "Value": v_stats['low_defended']},
            
            {"Metric": f"--- CHASING: {home_team} ---", "Value": "---"},
            {"Metric": "Average 2nd Innings", "Value": h_stats['avg_2nd']},
            {"Metric": "Highest Chased", "Value": h_stats['high_chased']},
            {"Metric": "Avg Successful Chase", "Value": h_stats['avg_succ']}, 
            {"Metric": "Avg Failed Chase", "Value": h_stats['avg_fail']},
            
            {"Metric": f"--- CHASING: {visitor_label} ---", "Value": "---"},
            {"Metric": "Average 2nd Innings", "Value": v_stats['avg_2nd']},
            {"Metric": "Highest Chased", "Value": v_stats['high_chased']},
            {"Metric": "Avg Successful Chase", "Value": v_stats['avg_succ']},
            {"Metric": "Avg Failed Chase", "Value": v_stats['avg_fail']},
        ]
        
        self._display_report(report_data, home_team, visitor_label, title)
        
        # --- FIX: ALWAYS SHOW AUDIT (Removed the is_venue_mode check) ---
        self._display_audit(df, home_team)

    # --- UI HELPERS ---
    def _display_report(self, data, team_a, team_b, title):
        report_df = pd.DataFrame(data)
        team_colors = {
            'India': '#1F8AC0', 'England': '#D60C0C', 'Australia': '#CBA135',
            'Pakistan': '#006400', 'South Africa': '#004d00', 'New Zealand': '#404040',
            'West Indies': '#7D000B', 'Sri Lanka': '#4d88ff', 'Bangladesh': '#006a4e',
            'Visitors': '#808080'
        }
        def get_color(val):
            for t, c in team_colors.items():
                if t in str(val): return f'color: {c}; font-weight: bold;'
            return ''
        print(f"\n📊 {title}")
        styled = report_df.style.map(lambda x: get_color(team_a) if team_a in str(x) else '', subset=['Metric'])\
                                .map(lambda x: get_color(team_b) if team_b in str(x) else '', subset=['Metric'])\
                                .hide(axis='index')
        with pd.option_context('display.max_rows', None): display(styled)

    def _display_audit(self, df, highlight_team):
        print("\n🕵️‍♂️ MATCH AUDIT (Most Recent First)")
        cols = ['start_date', 'venue', 'winner', 'team_bat_1', 'display_inn1', 'team_bat_2', 'display_inn2', 'status']
        audit_df = df[cols].sort_values('start_date', ascending=False).rename(
            columns={'display_inn1': 'score_inn1', 'display_inn2': 'score_inn2'}
        )
        display(audit_df)

if __name__ == "__main__":
    print("Engine code loaded.")