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
        # Ensure columns exist even if data is missing
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
        
        if is_home_analysis and team_name == 'Visitors':
            chase_win = df[(df['team_bat_2'] != df['home_team_ref']) & (df['is_chased'] == True)]
        else:
            chase_win = df[(df['team_bat_2'] == team_name) & (df['is_chased'] == True)]
            
        avg_chase = int(chase_win['score_inn2'].mean()) if not chase_win.empty else 0
        high_chase = int(chase_win['score_inn2'].max()) if not chase_win.empty else 0
        
        return {
            'avg_1st': avg_1st, 'avg_1st_win': avg_1st_win, 
            'high_1st': high_1st, 'low_1st': low_1st, 'low_defended': low_defended,
            'avg_chase': avg_chase, 'high_chase': high_chase
        }

    # --- TABLE 2: SPECIFIC MATCHUP (Updated with Win %) ---
    def analyze_venue_matchup(self, stadium_name, home_team, touring_team, years_back=10):
        stadium_name = self._resolve_stadium(stadium_name)
        
        # 1. Date Filter
        self.match_df['start_date'] = pd.to_datetime(self.match_df['start_date'])
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        
        print(f"\n🏟️ DEEP DIVE: {home_team} vs {touring_team} at {stadium_name}")
        print(f"   (📅 Data from last {years_back} years: Since {cutoff_date.date()})")
        
        # 2. Filter Venue & Date
        venue_matches = self.match_df[
            (self.match_df['venue'].str.contains(stadium_name, case=False, na=False)) &
            (self.match_df['start_date'] >= cutoff_date)
        ].copy()
        
        # 3. Filter Teams
        df = venue_matches[
            ((venue_matches['team_bat_1'] == home_team) & (venue_matches['team_bat_2'] == touring_team)) |
            ((venue_matches['team_bat_1'] == touring_team) & (venue_matches['team_bat_2'] == home_team))
        ].copy()
        
        if df.empty:
            print(f"❌ No matches found in the last {years_back} years.")
            return

        # --- PART A: THE RECORD ---
        matches_played = len(df)
        won_home = len(df[df['winner'] == home_team])
        won_touring = len(df[df['winner'] == touring_team])
        tied_nr = matches_played - (won_home + won_touring)
        
        # NEW: Calculate Win %
        home_win_rate = int((won_home / matches_played) * 100) if matches_played > 0 else 0

        # --- PART B: THE STATS ---
        df = self._apply_smart_filters(df)
        stats_df = df[df['status'] == '✅ Included'].copy()
        
        # Overall Stats
        overall_avg_1st = int(stats_df['score_inn1'].mean()) if not stats_df.empty else 0
        overall_defended = stats_df[stats_df['is_defended'] == True]
        overall_avg_1st_win = int(overall_defended['score_inn1'].mean()) if not overall_defended.empty else 0

        # Team Stats
        h_stats = self._calculate_team_stats(stats_df, home_team)
        t_stats = self._calculate_team_stats(stats_df, touring_team)
        
        # Chasing Stats
        h_chase_win = stats_df[(stats_df['team_bat_2'] == home_team) & (stats_df['is_chased'] == True)]
        h_avg_chase_win = int(h_chase_win['score_inn2'].mean()) if not h_chase_win.empty else 0
        h_chase_loss = stats_df[(stats_df['team_bat_2'] == home_team) & (stats_df['is_chased'] == False)]
        h_avg_chase_loss = int(h_chase_loss['score_inn2'].mean()) if not h_chase_loss.empty else 0

        t_chase_win = stats_df[(stats_df['team_bat_2'] == touring_team) & (stats_df['is_chased'] == True)]
        t_avg_chase_win = int(t_chase_win['score_inn2'].mean()) if not t_chase_win.empty else 0
        t_chase_loss = stats_df[(stats_df['team_bat_2'] == touring_team) & (stats_df['is_chased'] == False)]
        t_avg_chase_loss = int(t_chase_loss['score_inn2'].mean()) if not t_chase_loss.empty else 0

        # --- BUILD REPORT ---
        report_data = [
            {"Metric": "Matches Played", "Value": matches_played},
            {"Metric": f"Wins: {home_team}", "Value": won_home},
            {"Metric": f"Win %: {home_team}", "Value": f"{home_win_rate}%"}, # <--- ADDED HERE
            {"Metric": f"Wins: {touring_team}", "Value": won_touring},
            {"Metric": "Tied / No Result", "Value": tied_nr},
            
            {"Metric": "--- OVERALL VENUE STATS ---", "Value": "---"},
            {"Metric": "Overall Avg 1st Innings Score", "Value": overall_avg_1st},
            {"Metric": "Overall Avg 1st Innings Winning Score", "Value": overall_avg_1st_win},
            
            {"Metric": f"--- BATTING 1ST: {home_team} ---", "Value": "---"},
            {"Metric": f"{home_team} Average 1st Innings", "Value": h_stats['avg_1st']},
            {"Metric": f"{home_team} Highest 1st Innings", "Value": h_stats['high_1st']},
            {"Metric": f"{home_team} Lowest 1st Innings", "Value": h_stats['low_1st']},
            {"Metric": f"{home_team} Avg Winning Score", "Value": h_stats['avg_1st_win']},
            {"Metric": f"{home_team} Lowest Defended Score", "Value": h_stats['low_defended']},
            
            {"Metric": f"--- BATTING 1ST: {touring_team} ---", "Value": "---"},
            {"Metric": f"{touring_team} Average 1st Innings", "Value": t_stats['avg_1st']},
            {"Metric": f"{touring_team} Highest 1st Innings", "Value": t_stats['high_1st']},
            {"Metric": f"{touring_team} Lowest 1st Innings", "Value": t_stats['low_1st']},
            {"Metric": f"{touring_team} Avg Winning Score", "Value": t_stats['avg_1st_win']},
            {"Metric": f"{touring_team} Lowest Defended Score", "Value": t_stats['low_defended']},
            
            {"Metric": f"--- CHASING: {home_team} ---", "Value": "---"},
            {"Metric": f"{home_team} Highest Chased", "Value": h_stats['high_chase']},
            {"Metric": f"{home_team} Avg Successful Chase", "Value": h_avg_chase_win},
            {"Metric": f"{home_team} Avg Failed Chase", "Value": h_avg_chase_loss},
            
            {"Metric": f"--- CHASING: {touring_team} ---", "Value": "---"},
            {"Metric": f"{touring_team} Highest Chased", "Value": t_stats['high_chase']},
            {"Metric": f"{touring_team} Avg Successful Chase", "Value": t_avg_chase_win},
            {"Metric": f"{touring_team} Avg Failed Chase", "Value": t_avg_chase_loss},
        ]
        
        self._display_report(report_data, home_team, touring_team, f"MATCHUP: {home_team} vs {touring_team}")
        self._display_audit(df, home_team)

    # --- TABLE 3: FORTRESS REPORT ---
    def analyze_home_fortress(self, stadium_name, home_team, years_back=10):
        stadium_name = self._resolve_stadium(stadium_name)
        self.match_df['start_date'] = pd.to_datetime(self.match_df['start_date'])
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        
        print(f"\n🏰 FORTRESS CHECK: {home_team} at {stadium_name}")
        
        venue_matches = self.match_df[
            (self.match_df['venue'].str.contains(stadium_name, case=False, na=False)) &
            (self.match_df['start_date'] >= cutoff_date)
        ].copy()
        
        df = venue_matches[(venue_matches['team_bat_1'] == home_team) | (venue_matches['team_bat_2'] == home_team)].copy()
        
        if df.empty:
            print("❌ No matches found.")
            return

        matches_played = len(df)
        won_home = len(df[df['winner'] == home_team])
        won_visitor = matches_played - won_home
        win_rate = int((won_home / matches_played) * 100) if matches_played > 0 else 0
        
        df = self._apply_smart_filters(df)
        stats_df = df[df['status'] == '✅ Included'].copy()
        stats_df['home_team_ref'] = home_team
        
        home_stats = self._calculate_team_stats(stats_df, home_team)
        visit_stats = self._calculate_team_stats(stats_df, 'Visitors', is_home_analysis=True)
        
        report_data = [
            {"Metric": "Matches Played", "Value": matches_played},
            {"Metric": f"Wins: {home_team}", "Value": won_home},
            {"Metric": "Wins: Visitors", "Value": won_visitor},
            {"Metric": "Overall Win %", "Value": f"{win_rate}%"},
            
            {"Metric": f"--- BATTING 1ST: {home_team} ---", "Value": "---"},
            {"Metric": "Average Score", "Value": home_stats['avg_1st']},
            {"Metric": "Highest Score", "Value": home_stats['high_1st']},
            {"Metric": "Lowest Score", "Value": home_stats['low_1st']},
            {"Metric": "Avg Winning Score", "Value": home_stats['avg_1st_win']},
            {"Metric": "Lowest Defended Score", "Value": home_stats['low_defended']},
            
            {"Metric": "--- BATTING 1ST: VISITORS ---", "Value": "---"},
            {"Metric": "Average Score", "Value": visit_stats['avg_1st']},
            {"Metric": "Highest Score", "Value": visit_stats['high_1st']},
            {"Metric": "Lowest Score", "Value": visit_stats['low_1st']},
            {"Metric": "Avg Winning Score", "Value": visit_stats['avg_1st_win']},
            {"Metric": "Lowest Defended Score", "Value": visit_stats['low_defended']},
            
            {"Metric": "--- CHASING RECORDS ---", "Value": "---"},
            {"Metric": f"{home_team} Highest Chased", "Value": home_stats['high_chase']},
            {"Metric": "Visitors Highest Chased", "Value": visit_stats['high_chase']},
        ]
        
        self._display_report(report_data, home_team, 'Visitors', f"FORTRESS REPORT")
        self._display_audit(df, home_team)

    # --- TABLE 4 & 5: GLOBAL/COUNTRY RIVALRY ---
    def analyze_global_h2h(self, team_a, team_b, years_back=5):
        self._generic_h2h_analysis(team_a, team_b, years_back=years_back, filter_country=None)

    def analyze_h2h_in_country(self, team_a, team_b, host_country, years_back=10):
        self._generic_h2h_analysis(team_a, team_b, years_back=years_back, filter_country=host_country)

    def _generic_h2h_analysis(self, team_a, team_b, years_back, filter_country=None):
        self.match_df['start_date'] = pd.to_datetime(self.match_df['start_date'])
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years_back)
        
        title_extra = f"IN {filter_country.upper()}" if filter_country else "GLOBAL"
        print(f"\n⚔️ RIVALRY CHECK ({title_extra}): {team_a} vs {team_b}")
        
        matches = self.match_df[self.match_df['start_date'] >= cutoff_date].copy()
        
        if filter_country:
            venue_keywords = []
            c = filter_country.lower()
            if c == 'australia': venue_keywords = ['Australia', 'Melbourne', 'Sydney', 'Brisbane', 'Adelaide', 'Perth', 'Hobart', 'Canberra', 'W.A.C.A']
            elif c == 'england': venue_keywords = ['England', 'Lord', 'Oval', 'Manchester', 'Birmingham', 'Leeds', 'Nottingham', 'Southampton', 'Cardiff', 'Bristol', 'Chester-le-Street']
            elif c == 'india': venue_keywords = ['India', 'Mumbai', 'Kolkata', 'Delhi', 'Chennai', 'Bangalore', 'Hyderabad', 'Ahmedabad', 'Mohali', 'Indore', 'Pune', 'Jaipur', 'Cuttack', 'Visakhapatnam', 'Raipur', 'Ranchi', 'Dharamsala', 'Lucknow', 'Guwahati', 'Thiruvananthapuram', 'Rajkot']
            elif c == 'south africa': venue_keywords = ['South Africa', 'Cape Town', 'Johannesburg', 'Centurion', 'Durban', 'Port Elizabeth', 'Paarl', 'Bloemfontein', 'East London', 'Kimberley', 'Gqeberha', 'St George']
            elif c == 'new zealand': venue_keywords = ['New Zealand', 'Auckland', 'Wellington', 'Christchurch', 'Hamilton', 'Napier', 'Dunedin', 'Mount Maunganui', 'Nelson']
            elif c == 'sri lanka': venue_keywords = ['Sri Lanka', 'Colombo', 'Kandy', 'Galle', 'Hambantota', 'Dambulla', 'Pallekele']
            elif c == 'west indies': venue_keywords = ['West Indies', 'Barbados', 'Trinidad', 'Guyana', 'Antigua', 'Jamaica', 'Saint Lucia', 'Grenada', 'St Kitts']
            elif c == 'pakistan': venue_keywords = ['Pakistan', 'Lahore', 'Karachi', 'Rawalpindi', 'Multan']
            else: venue_keywords = [filter_country]
            
            matches = matches[matches['venue'].str.contains('|'.join(venue_keywords), case=False, na=False)]

        df = matches[
            ((matches['team_bat_1'] == team_a) & (matches['team_bat_2'] == team_b)) |
            ((matches['team_bat_1'] == team_b) & (matches['team_bat_2'] == team_a))
        ].copy()
        
        if df.empty:
            print(f"❌ No matches found.")
            return

        matches_played = len(df)
        won_a = len(df[df['winner'] == team_a])
        won_b = len(df[df['winner'] == team_b])
        tied_nr = matches_played - (won_a + won_b)
        win_rate_a = int((won_a / matches_played) * 100) if matches_played > 0 else 0
        
        df = self._apply_smart_filters(df)
        stats_df = df[df['status'] == '✅ Included'].copy()
        
        a_stats = self._calculate_team_stats(stats_df, team_a)
        b_stats = self._calculate_team_stats(stats_df, team_b)

        report_data = [
            {"Metric": "Matches Played", "Value": matches_played},
            {"Metric": f"Wins: {team_a}", "Value": won_a},
            {"Metric": f"Wins: {team_b}", "Value": won_b},
            {"Metric": "Tied / No Result", "Value": tied_nr},
            {"Metric": f"{team_a} Win %", "Value": f"{win_rate_a}%"},
            
            {"Metric": f"--- BATTING 1ST: {team_a} ---", "Value": "---"},
            {"Metric": "Average Score", "Value": a_stats['avg_1st']},
            {"Metric": "Highest Score", "Value": a_stats['high_1st']},
            {"Metric": "Lowest Score", "Value": a_stats['low_1st']},
            {"Metric": "Avg Winning Score", "Value": a_stats['avg_1st_win']},
            {"Metric": "Lowest Defended Score", "Value": a_stats['low_defended']},
            
            {"Metric": f"--- BATTING 1ST: {team_b} ---", "Value": "---"},
            {"Metric": "Average Score", "Value": b_stats['avg_1st']},
            {"Metric": "Highest Score", "Value": b_stats['high_1st']},
            {"Metric": "Lowest Score", "Value": b_stats['low_1st']},
            {"Metric": "Avg Winning Score", "Value": b_stats['avg_1st_win']},
            {"Metric": "Lowest Defended Score", "Value": b_stats['low_defended']},
            
            {"Metric": "--- CHASING RECORDS ---", "Value": "---"},
            {"Metric": f"{team_a} Highest Chased", "Value": a_stats['high_chase']},
            {"Metric": f"{team_b} Highest Chased", "Value": b_stats['high_chase']},
        ]
        
        self._display_report(report_data, team_a, team_b, f"RIVALRY: {team_a} vs {team_b}")
        self._display_audit(df, team_a)

    # --- UTILITY & UI ---
    def export_reference_lists(self, filename='reference_data.txt'):
        # Code remains the same as before...
        pass

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
        styled = report_df.style.applymap(lambda x: get_color(team_a) if team_a in str(x) else '', subset=['Metric'])\
                                .applymap(lambda x: get_color(team_b) if team_b in str(x) else '', subset=['Metric'])\
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