import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML
from venues import get_venue_aliases
from config.teams import TEAM_COLORS, BOWLER_STYLES
from core.predictor import PredictorEngine

class PlayerEngine:
    """
    ⚔️ The Dugout (Pro-UI Fixed).
    - Fixed: Venue Name parsing (removes country prefix generically).
    - Fixed: Removed 3-char limit on venue headers.
    """
    def __init__(self, raw_df, player_df, meta_df):
        self.raw_df = raw_df
        self.player_df = player_df
        self.meta_df = meta_df
        self.predictor = PredictorEngine(raw_df, player_df)

    def get_active_squad(self, team_name):
        if self.meta_df.empty: return []
        team_players = self.meta_df[self.meta_df['team'].str.lower() == team_name.lower()]
        return sorted(team_players['player'].unique().tolist())
        
    def get_last_match_xi(self, team_name):
        """Smart Fetch: Retrieves players from the last match (with backfill)."""
        team_matches = self.raw_df[(self.raw_df['batting_team'] == team_name) | (self.raw_df['bowling_team'] == team_name)]
        if team_matches.empty: return []
        sorted_matches = team_matches.sort_values('start_date', ascending=False)['match_id'].unique()
        squad = set()
        for match_id in sorted_matches[:3]: 
            if len(squad) >= 11: break
            match_data = self.raw_df[self.raw_df['match_id'] == match_id]
            squad.update(match_data[match_data['batting_team'] == team_name]['striker'].unique().tolist())
            squad.update(match_data[match_data['batting_team'] == team_name]['non_striker'].unique().tolist())
            squad.update(match_data[match_data['bowling_team'] == team_name]['bowler'].unique().tolist())
        return sorted(list(squad))

    def compare_squads(self, team_a_name, team_a_players, team_b_name, team_b_players, venue_id, years=5):
        # 🎨 COLORS
        c1 = TEAM_COLORS.get(team_a_name, "#333")
        c2 = TEAM_COLORS.get(team_b_name, "#333")
        
        # -------------------------------------------------------------
        # 1. HEADER & SQUAD EXPERIENCE (Styled Horizontal Table)
        # -------------------------------------------------------------
        metrics_a = self._calculate_squad_metrics(team_a_name, team_a_players)
        metrics_b = self._calculate_squad_metrics(team_b_name, team_b_players)
        
        display(HTML(f"""
        <div style="font-family: 'Segoe UI', Roboto, sans-serif; margin-bottom:25px;">
            <div style="background: linear-gradient(135deg, {c1} 0%, {c2} 100%); padding:12px; border-radius:8px 8px 0 0; color:white; text-align:center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h3 style="margin:0; font-size:18px; letter-spacing:1px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">⚔️ SQUAD COMPARISON</h3>
                <div style="font-size:12px; opacity:0.9;">{team_a_name.upper()} vs {team_b_name.upper()}</div>
            </div>
            
            <div style="background:white; border:1px solid #ddd; border-top:none; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                <table style="width:100%; text-align:center; border-collapse:collapse; font-size:13px;">
                    <thead>
                        <tr style="background:#f8f9fa; color:#555; border-bottom:2px solid #eee; text-transform:uppercase; font-size:11px;">
                            <th style="padding:10px; text-align:left;">TEAM</th>
                            <th style="padding:10px;">CAPS</th>
                            <th style="padding:10px;">RUNS</th>
                            <th style="padding:10px;">100s</th>
                            <th style="padding:10px;">50s</th>
                            <th style="padding:10px;">WKTS</th>
                            <th style="padding:10px;">5W</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:12px 10px; text-align:left; font-weight:bold; color:{c1}; border-left: 4px solid {c1};">{team_a_name}</td>
                            <td style="font-weight:bold;">{metrics_a['Caps (Combined)']:,}</td>
                            <td>{metrics_a['Total Runs']:,}</td>
                            <td>{metrics_a['100s']}</td>
                            <td>{metrics_a['50s']}</td>
                            <td>{metrics_a['Total Wickets']}</td>
                            <td>{metrics_a['5-Wkt Hauls']}</td>
                        </tr>
                        <tr>
                            <td style="padding:12px 10px; text-align:left; font-weight:bold; color:{c2}; border-left: 4px solid {c2};">{team_b_name}</td>
                            <td style="font-weight:bold;">{metrics_b['Caps (Combined)']:,}</td>
                            <td>{metrics_b['Total Runs']:,}</td>
                            <td>{metrics_b['100s']}</td>
                            <td>{metrics_b['50s']}</td>
                            <td>{metrics_b['Total Wickets']}</td>
                            <td>{metrics_b['5-Wkt Hauls']}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        """))

        # -------------------------------------------------------------
        # 2. PLAYER STATS TABLE (Pro Styled) 📊
        # -------------------------------------------------------------
        target_venues = get_venue_aliases(venue_id)
        
        # 🔧 FIX: Smarter Venue Name Logic
        # If ID is "AUS_MELBOURNE", split gives ['AUS', 'MELBOURNE'], we take index [1] -> "MELBOURNE"
        # If ID is "INDORE" (no underscore), we take it as is.
        if "_" in venue_id:
            venue_short = venue_id.split("_", 1)[1].replace("_", " ").title()
        else:
            venue_short = venue_id.replace("_", " ").title()
        
        print("-" * 90)
        print(f"📍 Analysis Venue: {venue_id}  |  Short Name: {venue_short}  |  📅 Range: Last {years} Years")
        print(f"🔎 Aggregating stats from: {target_venues}")
        print("-" * 90)

        def render_pro_table(team_name, players, opponent, color):
            data = [self._get_stats(p, opponent, target_venues, years) for p in players]
            df = pd.DataFrame(data)
            if df.empty: return f"<div>No data for {team_name}</div>"

            rows = ""
            for i, row in df.iterrows():
                bg = "#ffffff" if i % 2 == 0 else "#f8f9fa" # Zebra Striping
                
                # Bat Form Styling
                bat_f = str(row.get('Bat Form', '-'))
                bf_style = "color:#dc3545; font-weight:700;" if bat_f == '0' else "color:#495057;"
                
                # Bowl Form Styling
                bowl_f = str(row.get('Bowl Form', '-'))
                b_style = "color:#28a745; font-weight:700;" if 'w' in bowl_f and bowl_f != '0w' else "color:#6c757d;"
                
                # Venue Data (Gold Highlight)
                v_avg = row.get('Ven Avg', '-')
                v_inns = row.get('Ven Inns', 0)
                v_avg_disp = f"<strong>{v_avg}</strong> <span style='font-size:9px; color:#666;'>({v_inns})</span>" if v_inns != '-' and v_inns > 0 else "-"
                
                v_runs = row.get('Ven Runs', '-')
                v_hs = row.get('Ven HS', '-')
                v_col_style = "color:#000;" if (v_runs != '-' and str(v_runs) != '0') else "color:#999;"

                # Wickets (Gold Highlight)
                v_wkts = row.get('Ven Wkts', '-')
                v_m = row.get('Ven Matches', 0)
                v_wkt_disp = f"<strong>{v_wkts}</strong> <span style='font-size:9px; color:#666;'>({v_m})</span>" if v_wkts != '-' and v_m > 0 else "-"
                
                # Dynamic Player Name (Clickable look)
                p_name = f"<span style='color:{color};'>{row['Player']}</span>"

                rows += f"""
                <tr style="background:{bg}; border-bottom:1px solid #e9ecef; height:32px;">
                    <td style="padding:6px 10px; text-align:right; font-weight:bold; font-size:12px; border-right:2px solid {color};">{p_name}</td>
                    <td style="padding:6px;">{row['Inns']}</td>
                    <td style="padding:6px; font-size:11px; {bf_style} white-space:nowrap;">{bat_f}</td>
                    <td style="padding:6px; font-weight:600; background:#f1f3f5;">{row['Bat Avg']}</td>
                    <td style="padding:6px;">{row['vs Opp']}</td>
                    
                    <td style="padding:6px; {v_col_style} background:#fff3cd; border-left:1px solid #ffeeba;">{v_avg_disp}</td>
                    <td style="padding:6px; {v_col_style} background:#fff3cd;">{v_runs}</td>
                    <td style="padding:6px; font-size:11px; color:#666; background:#fff3cd; border-right:1px solid #ffeeba;">{v_hs}</td>
                    
                    <td style="padding:6px; font-size:11px; {b_style} white-space:nowrap;">{bowl_f}</td>
                    <td style="padding:6px;">{row.get('Bowl Econ', '-')}</td>
                    <td style="padding:6px; background:#fff3cd;">{row.get('Ven Econ', '-')}</td>
                    <td style="padding:6px; {v_col_style} background:#fff3cd;">{v_wkt_disp}</td>
                </tr>"""

            # 🔧 FIX: Removed [:3] slice from venue headers
            return f"""
            <div style="margin-bottom:30px; font-family: 'Segoe UI', Roboto, sans-serif; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-radius:6px; overflow:hidden;">
                <div style="background:{color}; color:white; padding:10px 15px; font-weight:bold; letter-spacing:1px; font-size:14px; text-transform:uppercase;">
                    {team_name} <span style="font-size:11px; opacity:0.8; float:right;">Recent Form & Venue Stats</span>
                </div>
                
                <table style="width:100%; border-collapse:collapse; font-size:12px; text-align:center; color:#333;">
                    <thead>
                        <tr style="background:#343a40; color:white; font-size:11px; text-transform:uppercase;">
                            <th style="padding:10px; text-align:right;">PLAYER</th>
                            <th>INNS</th>
                            <th>FORM (L5)</th>
                            <th style="background:#495057;">AVG</th>
                            <th>vs {opponent[:3].upper()}</th>
                            
                            <th style="background:#ffc107; color:#212529;">AVG ({venue_short})</th>
                            <th style="background:#ffc107; color:#212529;">RUNS</th>
                            <th style="background:#ffc107; color:#212529;">HS</th>
                            
                            <th>B.FORM</th>
                            <th>ECON</th>
                            <th style="background:#ffc107; color:#212529;">V.ECON</th>
                            <th style="background:#ffc107; color:#212529;">WKTS ({venue_short})</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>"""

        # RENDER TABLES
        display(HTML(render_pro_table(team_a_name, team_a_players, team_b_name, c1)))
        display(HTML(render_pro_table(team_b_name, team_b_players, team_a_name, c2)))

        # -------------------------------------------------------------
        # 3. MATCHUPS (Modern Card Layout)
        # -------------------------------------------------------------
        display(HTML(f"""
        <div style="background:#343a40; color:white; padding:10px; border-radius:6px; font-weight:bold; margin-bottom:15px; font-family:'Segoe UI'; display:flex; justify-content:space-between; align-items:center;">
            <span>⚔️ HEAD-TO-HEAD MATCHUPS</span>
            <span style="font-size:11px; background:#495057; padding:2px 8px; border-radius:10px;">Who owns whom?</span>
        </div>
        """))
        
        left = widgets.Output(); right = widgets.Output()
        
        with left:
            display(HTML(f"<div style='font-family:sans-serif; font-weight:bold; color:{c1}; margin-bottom:10px; border-bottom:3px solid {c1}; padding-bottom:5px;'>🛡️ {team_a_name.upper()} BATTING</div>"))
            for p in team_a_players: self._display_batter_vs_bowlers(p, team_a_name, team_b_players)
        
        with right:
            display(HTML(f"<div style='font-family:sans-serif; font-weight:bold; color:{c2}; margin-bottom:10px; border-bottom:3px solid {c2}; padding-bottom:5px;'>🛡️ {team_b_name.upper()} BATTING</div>"))
            for p in team_b_players: self._display_batter_vs_bowlers(p, team_b_name, team_a_players)
            
        display(widgets.HBox([left, right], layout=widgets.Layout(width='100%', gap='30px')))

    # --- HELPERS (Logic Unchanged) ---
    def analyze_player_profile(self, player_name):
        import numpy as np
        print(f"\n👤 PLAYER PROFILE: {player_name.upper()}")
        if self.player_df.empty: print("❌ Player data is missing."); return
        p_stats = self.player_df[self.player_df['player'].str.lower() == player_name.lower()].copy()
        if p_stats.empty: print(f"❌ No data found for '{player_name}'."); return
        if 'type' in p_stats.columns:
            print("\n⚔️ PERFORMANCE vs TEAMS")
            vs_teams = p_stats[p_stats['type'] == 'vs_team'].sort_values('runs', ascending=False)
            if not vs_teams.empty: display(vs_teams[['opponent', 'innings', 'runs', 'average', 'strike_rate']].style.format("{:.1f}", subset=['average', 'strike_rate']).hide(axis='index'))
            print("\n🏟️ TOP 10 VENUES")
            at_venues = p_stats[p_stats['type'] == 'at_venue'].sort_values('runs', ascending=False).head(10)
            if not at_venues.empty: display(at_venues[['opponent', 'innings', 'runs', 'average', 'strike_rate']].rename(columns={'opponent': 'Venue'}).style.format("{:.1f}", subset=['average', 'strike_rate']).hide(axis='index'))

    def _calculate_squad_metrics(self, team, players):
        mask = (self.raw_df['striker'].isin(players)) | (self.raw_df['bowler'].isin(players))
        df = self.raw_df[mask]
        tr, c, f, tw, fw, caps = 0,0,0,0,0,0
        for p in players:
            pb = df[df['striker'] == p]; pw = df[df['bowler'] == p]
            caps += len(set(pb['match_id'].unique()) | set(pw['match_id'].unique()))
            if not pb.empty:
                s = pb.groupby('match_id')['runs_off_bat'].sum()
                tr += s.sum(); c += (s>=100).sum(); f += ((s>=50)&(s<100)).sum()
            if not pw.empty:
                valid = pw[pw['wicket_type'].isin(['bowled','caught','lbw','stumped','caught and bowled','hit wicket'])]
                tw += len(valid)
                if not valid.empty: fw += (valid.groupby('match_id').count()['wicket_type']>=5).sum()
        return {'Caps (Combined)': caps, 'Total Runs': tr, '100s': c, '50s': f, 'Total Wickets': tw, '5-Wkt Hauls': fw}

    def _get_stats(self, player, opp, venues, years=5):
        bat = self.player_df[(self.player_df['player'] == player) & (self.player_df['role'] == 'batting')]
        # Form
        raw_bat = self.raw_df[self.raw_df['striker'] == player].drop_duplicates('match_id').tail(5)
        form_bat = []
        for m in raw_bat['match_id']:
            d = self.raw_df[(self.raw_df['match_id']==m)&(self.raw_df['striker']==player)]
            r = d['runs_off_bat'].sum(); out = d['wicket_type'].notna().any()
            form_bat.append(f"{r}" if out else f"{r}*")
        # Career
        car_inns = bat[bat['context']=='vs_team']['innings'].sum()
        car_runs = bat[bat['context']=='vs_team']['runs'].sum()
        car_outs = bat[bat['context']=='vs_team']['dismissals'].sum()
        avg = round(car_runs/car_outs, 1) if car_outs > 0 else car_runs
        opp_row = bat[(bat['context']=='vs_team')&(bat['opponent']==opp)]
        opp_avg = round(opp_row['runs'].sum()/opp_row['dismissals'].sum(),1) if not opp_row.empty and opp_row['dismissals'].sum()>0 else "-"
        # VENUE (Batting) - Uses 'years' param
        v_inns = 0; v_runs = 0; v_avg = "-"; v_hs = "-"
        try:
            raw_ven_bat = self.raw_df[
                (self.raw_df['striker'] == player) & (self.raw_df['venue'].isin(venues)) &
                (self.raw_df['start_date'] >= pd.Timestamp.now() - pd.DateOffset(years=years)) 
            ]
            if not raw_ven_bat.empty:
                match_scores = raw_ven_bat.groupby('match_id').agg({'runs_off_bat': 'sum','wicket_type': lambda x: 1 if x.notna().any() else 0})
                v_inns = len(match_scores)
                v_runs = int(match_scores['runs_off_bat'].sum())
                v_outs = match_scores['wicket_type'].sum()
                v_avg = round(v_runs/v_outs, 1) if v_outs > 0 else v_runs
                v_hs = int(match_scores['runs_off_bat'].max()) 
            else:
                if years == 5:
                    ven_row = bat[(bat['context']=='at_venue')&(bat['opponent'].isin(venues))]
                    if not ven_row.empty:
                        v_runs = int(ven_row['runs'].sum())
                        v_avg = round(ven_row['runs'].sum()/ven_row['dismissals'].sum(),1) if ven_row['dismissals'].sum()>0 else ven_row['runs'].sum()
        except: pass
        # Bowling
        bowl = self.player_df[(self.player_df['player'] == player) & (self.player_df['role'] == 'bowling')]
        v_wkts = 0; v_matches = 0; v_econ = "-"; econ = "-"
        raw_bowl = self.raw_df[self.raw_df['bowler'] == player].drop_duplicates('match_id').tail(5)
        form_bowl = []
        for m in raw_bowl['match_id']:
            d = self.raw_df[(self.raw_df['match_id']==m)&(self.raw_df['bowler']==player)]
            w = d['wicket_type'].isin(['bowled','caught','lbw','stumped','caught and bowled','hit wicket']).sum()
            form_bowl.append(f"{w}w")
        c_r = bowl[bowl['context']=='vs_team']['runs'].sum(); c_b = bowl[bowl['context']=='vs_team']['balls'].sum()
        econ = round(c_r/c_b*6, 1) if c_b>0 else "-"
        try:
            raw_ven_bowl = self.raw_df[
                (self.raw_df['bowler'] == player) & (self.raw_df['venue'].isin(venues)) &
                (self.raw_df['start_date'] >= pd.Timestamp.now() - pd.DateOffset(years=years))
            ]
            if not raw_ven_bowl.empty:
                v_matches = len(raw_ven_bowl['match_id'].unique()) 
                v_wkts = raw_ven_bowl['wicket_type'].isin(['bowled','caught','lbw','stumped','caught and bowled','hit wicket']).sum()
                runs_conceded = raw_ven_bowl['runs_off_bat'].sum() + raw_ven_bowl['extras'].sum()
                total_balls = len(raw_ven_bowl) 
                if total_balls > 0: v_econ = round((runs_conceded / total_balls) * 6, 1)
        except: pass
        return {
            'Player': player, 'Inns': car_inns, 'Bat Form': ", ".join(form_bat[::-1]), 
            'Bat Avg': avg, 'vs Opp': opp_avg, 
            'Ven Inns': v_inns if v_inns > 0 else "-", 'Ven Runs': v_runs if v_runs > 0 else "-", 
            'Ven Avg': v_avg, 'Ven HS': v_hs,
            'Bowl Form': ", ".join(form_bowl[::-1]), 'Bowl Econ': econ, 'Ven Econ': v_econ,
            'Ven Wkts': v_wkts if v_wkts > 0 else "-", 'Ven Matches': v_matches
        }

    def _display_batter_vs_bowlers(self, batter, bat_team, bowlers):
        data = []
        for b in bowlers:
            h2h = self.player_df[(self.player_df['player']==batter)&(self.player_df['opponent']==b)&(self.player_df['role']=='h2h')]
            if not h2h.empty:
                r = h2h['runs'].sum(); bl = h2h['balls'].sum(); o = h2h['dismissals'].sum()
                if bl > 0:
                    style_tag = BOWLER_STYLES.get(b, 'Unknown')
                    bunny_tag = " (🐰 Bunny)" if o >= 3 else ""
                    data.append({'Bowler': f"{b} ({style_tag}){bunny_tag}", 'Runs': r, 'Balls': bl, 'Outs': o, 'Avg': round(r/o,1) if o>0 else r, 'SR': round(r/bl*100,1)})
        
        if data:
            hex = TEAM_COLORS.get(bat_team, '#000')
            display(HTML(f"<div style='font-weight:700; color:{hex}; font-size:12px; margin-top:8px;'>🏏 {batter}</div>"))
            df = pd.DataFrame(data).sort_values('Balls', ascending=False)
            
            def color_rows(row):
                val = row['Outs']
                color = '#333'; weight = 'normal'
                if val >= 3: color = '#d32f2f'; weight = 'bold'
                elif val == 2: color = '#e67e22'; weight = 'bold'
                elif val == 0: color = '#27ae60'; weight = 'bold'
                return [f'color: {color}; font-weight: {weight}' if col == 'Bowler' else '' for col in row.index]

            styler = df.style.apply(color_rows, axis=1).format("{:.1f}", subset=['SR', 'Avg']).hide(axis='index')
            styler.set_table_styles([{'selector': 'th', 'props': [('background-color', '#f8f9fa'), ('color', '#495057'), ('font-size', '10px'), ('border-bottom', '2px solid #dee2e6')]}])
            display(styler)