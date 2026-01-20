import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML
from venues import get_venue_aliases
from config.teams import TEAM_COLORS, BOWLER_STYLES
from core.predictor import PredictorEngine
import re

class PlayerEngine:
    """
    ⚔️ The Dugout (v5.2 - Context-Aware Micro Profile).
    - PRESERVED: Exact formatting and indentation of your v5.0 code.
    - FIXED: 'KeyError: type' in analyze_player_profile (Changed to 'context').
    - FEATURE: Smart Player Profile (Auto-detects Opponent & Venue).
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
        mask = (self.raw_df['batting_team'] == team_name) | (self.raw_df['bowling_team'] == team_name)
        team_matches = self.raw_df[mask]
        
        if team_matches.empty: return []
        
        sorted_matches = team_matches.sort_values('start_date', ascending=False)['match_id'].unique()
        squad = set()
        
        for match_id in sorted_matches[:3]: 
            if len(squad) >= 11: break
            match_data = self.raw_df[self.raw_df['match_id'] == match_id]
            squad.update(match_data[match_data['batting_team'] == team_name]['striker'].unique())
            squad.update(match_data[match_data['batting_team'] == team_name]['non_striker'].unique())
            squad.update(match_data[match_data['bowling_team'] == team_name]['bowler'].unique())
            
        return sorted(list(squad))

    def compare_squads(self, team_a_name, team_a_players, team_b_name, team_b_players, venue_id, years=5):
        # 🎨 COLORS
        c1 = TEAM_COLORS.get(team_a_name, "#333")
        c2 = TEAM_COLORS.get(team_b_name, "#333")
        
        # -------------------------------------------------------------
        # 1. HEADER & SQUAD EXPERIENCE (Restored 50s & 5W)
        # -------------------------------------------------------------
        metrics_a = self._calculate_squad_metrics(team_a_name, team_a_players)
        metrics_b = self._calculate_squad_metrics(team_b_name, team_b_players)
        
        avg_caps_a = int(metrics_a['Caps (Combined)'] / max(len(team_a_players), 1))
        avg_caps_b = int(metrics_b['Caps (Combined)'] / max(len(team_b_players), 1))

        display(HTML(f"""
        <div style="font-family: 'Segoe UI', Roboto, sans-serif; margin-bottom:25px;">
            <div style="background: linear-gradient(135deg, {c1} 0%, {c2} 100%); padding:12px; border-radius:8px 8px 0 0; color:white; text-align:center;">
                <h3 style="margin:0; font-size:18px;">⚔️ SQUAD COMPARISON</h3>
                <div style="font-size:12px; opacity:0.9;">{team_a_name.upper()} vs {team_b_name.upper()}</div>
            </div>
            
            <div style="background:white; border:1px solid #ddd; border-top:none;">
                <table style="width:100%; text-align:center; border-collapse:separate; border-spacing:0; font-size:13px;">
                    <thead>
                        <tr style="background:#f8f9fa; color:#555; text-transform:uppercase; font-size:11px;">
                            <th style="padding:10px; border-bottom:2px solid #eee;">TEAM</th>
                            <th style="padding:10px; border-bottom:2px solid #eee;">CAPS</th>
                            <th style="padding:10px; border-bottom:2px solid #eee; background:#e9ecef;">AVG CAPS</th>
                            <th style="padding:10px; border-bottom:2px solid #eee;">RUNS</th>
                            <th style="padding:10px; border-bottom:2px solid #eee;">100s</th>
                            <th style="padding:10px; border-bottom:2px solid #eee;">50s</th>
                            <th style="padding:10px; border-bottom:2px solid #eee;">WKTS</th>
                            <th style="padding:10px; border-bottom:2px solid #eee;">5W</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom:1px solid #eee;">
                            <td style="padding:10px; font-weight:bold; color:{c1}; border-left: 4px solid {c1};">{team_a_name}</td>
                            <td style="font-weight:bold;">{metrics_a['Caps (Combined)']:,}</td>
                            <td style="background:#f8f9fa; color:#666;">{avg_caps_a}</td>
                            <td>{metrics_a['Total Runs']:,}</td>
                            <td>{metrics_a['100s']}</td>
                            <td>{metrics_a['50s']}</td>
                            <td>{metrics_a['Total Wickets']}</td>
                            <td>{metrics_a['5-Wkt Hauls']}</td>
                        </tr>
                        <tr>
                            <td style="padding:10px; font-weight:bold; color:{c2}; border-left: 4px solid {c2};">{team_b_name}</td>
                            <td style="font-weight:bold;">{metrics_b['Caps (Combined)']:,}</td>
                            <td style="background:#f8f9fa; color:#666;">{avg_caps_b}</td>
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
        # 2. PLAYER STATS (Smart Venue Logic)
        # -------------------------------------------------------------
        aliases = get_venue_aliases(venue_id)
        
        if "_" in venue_id:
            suffix_key = venue_id.split("_", 1)[1] # "MCG"
            suffix_aliases = get_venue_aliases(suffix_key)
            if suffix_aliases:
                aliases = list(set(aliases + suffix_aliases))
        
        if not aliases:
            aliases = [venue_id]
            if "_" in venue_id: aliases.append(venue_id.split("_", 1)[1])

        venue_pattern = '|'.join([re.escape(v) for v in aliases if v])
        venue_display = venue_id.replace("IND_", "").replace("AUS_", "").replace("_", " ").title()
        
        print("-" * 90)
        print(f"📍 Analysis Venue: {venue_id}  |  Display: {venue_display}")
        print(f"🔎 Final Regex: r'{venue_pattern}'")
        print("-" * 90)

        def render_pro_table(team_name, players, opponent, color):
            data = [self._get_stats(p, opponent, venue_pattern, years) for p in players]
            df = pd.DataFrame(data)
            if df.empty: return f"<div>No data for {team_name}</div>"

            rows = ""
            for i, row in df.iterrows():
                bg = "#ffffff" if i % 2 == 0 else "#f8f9fa"
                
                bat_f = str(row.get('Bat Form', '-'))
                bf_style = "color:#dc3545; font-weight:700;" if bat_f == '0' else "color:#495057;"
                
                bowl_f = str(row.get('Bowl Form', '-'))
                b_style = "color:#28a745; font-weight:700;" if 'w' in bowl_f and bowl_f != '0w' else "color:#6c757d;"
                
                v_avg = row.get('Ven Avg', '-')
                v_inns = row.get('Ven Inns', 0)
                v_avg_disp = f"<strong>{v_avg}</strong> ({v_inns})" if v_inns != '-' and v_inns > 0 else "-"
                
                v_runs = row.get('Ven Runs', '-')
                v_hs = row.get('Ven HS', '-')
                v_col_style = "color:#000;" if (v_runs != '-' and str(v_runs) != '0') else "color:#999;"

                v_wkts = row.get('Ven Wkts', '-')
                v_m = row.get('Ven Matches', 0)
                v_wkt_disp = f"<strong>{v_wkts}</strong> ({v_m})" if v_wkts != '-' and v_m > 0 else "-"
                
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
                    <td style="padding:6px; background:#fff3cd;">{v_wkt_disp}</td>
                </tr>"""

            return f"""
            <div style="margin-bottom:30px; font-family: 'Segoe UI', Roboto, sans-serif; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-radius:6px; overflow:hidden;">
                <div style="background:{color}; color:white; padding:8px 15px; font-weight:bold; letter-spacing:1px; font-size:13px; text-transform:uppercase;">
                    {team_name}
                </div>
                <table style="width:100%; border-collapse:collapse; font-size:12px; text-align:center; color:#333;">
                    <thead>
                        <tr style="background:#343a40; color:white; font-size:11px; text-transform:uppercase;">
                            <th style="padding:8px; text-align:right;">PLAYER</th>
                            <th>INNS</th>
                            <th>FORM</th>
                            <th style="background:#495057;">AVG</th>
                            <th>vs {opponent[:3].upper()}</th>
                            
                            <th style="background:#ffc107; color:#212529;">AVG ({venue_display})</th>
                            <th style="background:#ffc107; color:#212529;">RUNS</th>
                            <th style="background:#ffc107; color:#212529;">HS</th>
                            
                            <th>B.FORM</th>
                            <th>ECON</th>
                            <th style="background:#ffc107; color:#212529;">V.ECON</th>
                            <th style="background:#ffc107; color:#212529;">WKTS ({venue_display})</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>"""

        display(HTML(render_pro_table(team_a_name, team_a_players, team_b_name, c1)))
        display(HTML(render_pro_table(team_b_name, team_b_players, team_a_name, c2)))

        # -------------------------------------------------------------
        # 3. TACTICAL MATRIX (ARCHETYPES)
        # -------------------------------------------------------------
        print("\n")
        display(HTML(f"<div style='background:#444; color:white; padding:8px; border-radius:4px; font-weight:bold; margin-bottom:10px; font-family:sans-serif;'>📊 TACTICAL MATRIX: ARCHETYPES</div>"))
        
        self.analyze_squad_types(team_a_name, team_a_players, team_b_players)
        print("\n")
        self.analyze_squad_types(team_b_name, team_b_players, team_a_players)

        # -------------------------------------------------------------
        # 4. MATCHUPS (Live Data)
        # -------------------------------------------------------------
        display(HTML(f"""
        <div style="background:#343a40; color:white; padding:8px; border-radius:6px; font-weight:bold; margin-bottom:10px; font-family:'Segoe UI';">
            ⚔️ HEAD-TO-HEAD MATCHUPS
        </div>
        """))
        
        left = widgets.Output(); right = widgets.Output()
        
        with left:
            display(HTML(f"<div style='font-weight:bold; color:{c1}; margin-bottom:10px; border-bottom:3px solid {c1};'>🛡️ {team_a_name.upper()} BATTING</div>"))
            for p in team_a_players: self._display_batter_vs_bowlers(p, team_a_name, team_b_players)
        
        with right:
            display(HTML(f"<div style='font-weight:bold; color:{c2}; margin-bottom:10px; border-bottom:3px solid {c2};'>🛡️ {team_b_name.upper()} BATTING</div>"))
            for p in team_b_players: self._display_batter_vs_bowlers(p, team_b_name, team_a_players)
            
        display(widgets.HBox([left, right], layout=widgets.Layout(width='100%', gap='30px')))

    # --- NEW: ARCHETYPE ANALYSIS ---
    def analyze_squad_types(self, team_name, players, opposition_bowlers):
        """
        Generates a 'Tactical Breakdown' of how batters perform against
        the SPECIFIC bowling types present in the opposition's squad.
        """
        
        # 1. IDENTIFY OPPOSITION BOWLING TYPES
        active_styles_count = {}
        all_style_map = {}
        
        # Build Reverse Map to get ALL bowlers of a specific style from database
        for name, style in BOWLER_STYLES.items():
            if style not in all_style_map: all_style_map[style] = []
            all_style_map[style].append(name)
            
        # Count types in Opposition XI
        for b in opposition_bowlers:
            style = BOWLER_STYLES.get(b, 'Unknown')
            if style != 'Unknown':
                active_styles_count[style] = active_styles_count.get(style, 0) + 1
        
        if not active_styles_count:
            return

        # 2. DISPLAY ATTACK BREAKDOWN
        c1 = TEAM_COLORS.get(team_name, "#333")
        
        style_badges = ""
        for style, count in active_styles_count.items():
            icon = style.split(' ')[0]
            name = style.split(' ', 1)[1] if ' ' in style else style
            style_badges += f"""
            <div style="background:#fff; border:1px solid #ddd; padding:4px 8px; border-radius:12px; font-size:11px; font-weight:bold; color:#555; display:flex; align-items:center; gap:4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <span>{icon}</span>
                <span>{name}</span>
                <span style="background:{c1}; color:white; padding:1px 5px; border-radius:8px; font-size:10px;">{count}</span>
            </div>
            """

        display(HTML(f"""
        <div style="font-family:'Segoe UI', sans-serif; margin-bottom:10px; border:1px solid #eee; border-radius:6px; overflow:hidden;">
            <div style="background:#f8f9fa; padding:6px 10px; font-weight:bold; color:#333; border-bottom:1px solid #eee; font-size:12px;">
                🛡️ THREAT MATRIX: {team_name} Batters vs Opposition Types
            </div>
            <div style="padding:8px; display:flex; flex-wrap:wrap; gap:6px; background:white;">
                {style_badges}
            </div>
        </div>
        """))

        # 3. CALCULATE BATTER PERFORMANCE VS THESE TYPES
        target_styles = list(active_styles_count.keys())
        table_data = []
        
        for batter in players:
            row = {'Player': batter}
            for style in target_styles:
                # Use the proxy list (all bowlers of this type)
                proxy_bowlers = all_style_map.get(style, [])
                
                if not proxy_bowlers:
                    row[style] = "-"
                    continue
                
                try:
                    style_df = self.raw_df[
                        (self.raw_df['striker'] == batter) & 
                        (self.raw_df['bowler'].isin(proxy_bowlers))
                    ]
                    
                    if not style_df.empty:
                        runs = style_df['runs_off_bat'].sum()
                        balls = style_df['match_id'].count()
                        outs = style_df['wicket_type'].isin(['bowled','caught','lbw','stumped','caught and bowled','hit wicket']).sum()
                        
                        avg = round(runs/outs, 1) if outs > 0 else runs
                        sr = int((runs/balls)*100) if balls > 0 else 0
                        
                        color = "#2e7d32" if avg > 40 else "#c62828" if avg < 25 else "#333"
                        row[style] = f"<span style='color:{color}; font-weight:bold;'>{avg}</span> <span style='font-size:10px; color:#999;'>({sr})</span>"
                    else:
                        row[style] = "-"
                except:
                    row[style] = "-"
            table_data.append(row)

        # 4. RENDER MATRIX TABLE
        if table_data:
            df = pd.DataFrame(table_data)
            headers = "".join([f"<th style='padding:6px; background:#f4f4f4; color:#555; font-size:11px;'>{s.split(' ', 1)[1] if ' ' in s else s}</th>" for s in target_styles])
            
            rows_html = ""
            for _, r in df.iterrows():
                cells = "".join([f"<td style='padding:6px; border-bottom:1px solid #eee; font-size:12px;'>{r[col]}</td>" for col in target_styles])
                rows_html += f"<tr><td style='padding:6px; font-weight:bold; text-align:right; border-right:2px solid {c1}; color:{c1}; font-size:12px;'>{r['Player']}</td>{cells}</tr>"
            
            display(HTML(f"""
            <div style="border:1px solid #ddd; border-radius:6px; overflow-x:auto; margin-bottom:20px;">
                <table style="width:100%; border-collapse:collapse; text-align:center; font-family:sans-serif;">
                    <thead>
                        <tr>
                            <th style="padding:6px; text-align:right; background:{c1}; color:white; font-size:11px;">BATTER</th>
                            {headers}
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
                <div style="padding:4px; background:#fafafa; color:#777; font-size:9px; text-align:right;">
                    <i>Stats vs All bowlers of this type in database</i>
                </div>
            </div>
            """))

    # --- HELPERS ---

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

    def _get_stats(self, player, opp, venue_pattern, years=5):
        # 1. Base Stats
        bat = self.player_df[(self.player_df['player'] == player) & (self.player_df['role'] == 'batting')]
        raw_bat = self.raw_df[self.raw_df['striker'] == player].drop_duplicates('match_id').tail(5)
        form_bat = []
        for m in raw_bat['match_id']:
            d = self.raw_df[(self.raw_df['match_id']==m)&(self.raw_df['striker']==player)]
            r = d['runs_off_bat'].sum(); out = d['wicket_type'].notna().any()
            form_bat.append(f"{r}" if out else f"{r}*")

        car_inns = bat[bat['context']=='vs_team']['innings'].sum()
        avg = round(bat[bat['context']=='vs_team']['runs'].sum()/bat[bat['context']=='vs_team']['dismissals'].sum(), 1) if not bat.empty and bat['dismissals'].sum()>0 else bat['runs'].sum()
        opp_row = bat[(bat['context']=='vs_team')&(bat['opponent']==opp)]
        opp_avg = round(opp_row['runs'].sum()/opp_row['dismissals'].sum(),1) if not opp_row.empty and opp_row['dismissals'].sum()>0 else "-"

        # 2. VENUE BATTING
        v_inns = 0; v_runs = 0; v_avg = "-"; v_hs = "-"
        try:
            raw_ven_bat = self.raw_df[
                (self.raw_df['striker'] == player) & 
                (self.raw_df['venue'].str.contains(venue_pattern, case=False, na=False)) & 
                (self.raw_df['start_date'] >= pd.Timestamp.now() - pd.DateOffset(years=years)) 
            ]
            if not raw_ven_bat.empty:
                match_scores = raw_ven_bat.groupby('match_id').agg({'runs_off_bat': 'sum','wicket_type': lambda x: 1 if x.notna().any() else 0})
                v_inns = len(match_scores)
                v_runs = int(match_scores['runs_off_bat'].sum())
                v_outs = match_scores['wicket_type'].sum()
                v_avg = round(v_runs/v_outs, 1) if v_outs > 0 else v_runs
                v_hs = int(match_scores['runs_off_bat'].max()) 
        except: pass

        # 3. BOWLING
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

        # 4. VENUE BOWLING
        try:
            raw_ven_bowl = self.raw_df[
                (self.raw_df['bowler'] == player) & 
                (self.raw_df['venue'].str.contains(venue_pattern, case=False, na=False)) &
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
            'Ven Inns': v_inns if v_inns > 0 else "-", 'Ven Runs': v_runs if v_runs != 0 or v_inns > 0 else "-", 
            'Ven Avg': v_avg, 'Ven HS': v_hs,
            'Bowl Form': ", ".join(form_bowl[::-1]), 'Bowl Econ': econ, 'Ven Econ': v_econ,
            'Ven Wkts': v_wkts if v_wkts > 0 else "-", 'Ven Matches': v_matches
        }

    def _display_batter_vs_bowlers(self, batter, bat_team, bowlers):
        # LIVE RAW DATA CALCULATION
        batter_df = self.raw_df[
            (self.raw_df['striker'] == batter) & 
            (self.raw_df['bowler'].isin(bowlers))
        ].copy()

        if batter_df.empty: return

        matchup_stats = batter_df.groupby('bowler').agg({
            'runs_off_bat': 'sum',           
            'match_id': 'count',             
            'wicket_type': lambda x: x.isin(['bowled','caught','lbw','stumped','caught and bowled','hit wicket']).sum()
        }).reset_index()
        
        matchup_stats.rename(columns={'match_id': 'Balls', 'runs_off_bat': 'Runs', 'wicket_type': 'Outs'}, inplace=True)

        data = []
        for _, row in matchup_stats.iterrows():
            b = row['bowler']; r = row['Runs']; bl = row['Balls']; o = row['Outs']
            style_tag = BOWLER_STYLES.get(b, 'Unknown')
            bunny_tag = " (🐰 Bunny)" if o >= 3 else ""
            data.append({
                'Bowler': f"{b} ({style_tag}){bunny_tag}", 'Runs': r, 'Balls': bl, 'Outs': o, 
                'Avg': round(r/o, 1) if o > 0 else r, 'SR': round(r/bl*100, 1)
            })

        if data:
            hex = TEAM_COLORS.get(bat_team, '#000')
            display(HTML(f"<div style='font-weight:700; color:{hex}; font-size:12px; margin-top:8px;'>🏏 {batter}</div>"))
            df = pd.DataFrame(data).sort_values('Balls', ascending=False)
            
            def color_rows(row):
                val = row['Outs']
                color = '#333'; weight = 'normal'
                if val >= 3: color = '#d32f2f'; weight = 'bold'
                elif val == 2: color = '#e67e22'; weight = 'bold'
                elif val == 0: color = '#2e7d32'; weight = 'bold'
                return [f'color: {color}; font-weight: {weight}' if col == 'Bowler' else '' for col in row.index]

            styler = df.style.apply(color_rows, axis=1).format("{:.1f}", subset=['SR', 'Avg']).hide(axis='index')
            styler.set_table_styles([{'selector': 'th', 'props': [('background-color', '#f8f9fa'), ('color', '#495057'), ('font-size', '10px'), ('border-bottom', '2px solid #dee2e6')]}])
            display(styler)
    
    def analyze_player_profile(self, player_name, opposition=None, venue_id=None, active_bowlers=None, years=10):
        """
        Generates a Context-Aware Player Dashboard.
        FIXED:
        1. Aggregates 'vs Opposition' stats into one clean row.
        2. Filters 'H2H Nightmares' to ONLY show bowlers in the selected active squad.
        3. Accepts 'years' parameter for Venue Stats filtering.
        """
        import numpy as np
        
        # 1. FUZZY SEARCH
        if player_name not in self.player_df['player'].values:
            matches = [p for p in self.player_df['player'].unique() if player_name.lower() in str(p).lower()]
            if matches: player_name = matches[0]
            else: print(f"❌ No data found for '{player_name}'."); return

        print(f"\n👤 PLAYER PROFILE: {player_name.upper()}")
        
        # --- A. GLOBAL CAREER SUMMARY ---
        p_stats = self.player_df[self.player_df['player'] == player_name].copy()
        career_df = p_stats[p_stats['context'] == 'vs_team'].copy()
        
        if not career_df.empty:
            t_runs = career_df['runs'].sum()
            t_inns = career_df['innings'].sum()
            t_outs = career_df['dismissals'].sum()
            t_balls = career_df['balls'].sum()
            avg = round(t_runs / t_outs, 2) if t_outs > 0 else t_runs
            sr = round((t_runs / t_balls) * 100, 1) if t_balls > 0 else 0
            
            display(HTML(f"""
            <div style="background:#f9f9f9; border-left:4px solid #333; padding:10px 15px; margin-bottom:15px; font-family:'Segoe UI';">
                <div style="font-size:12px; color:#777; font-weight:bold; letter-spacing:1px;">CAREER SUMMARY</div>
                <div style="display:flex; gap:20px; margin-top:5px;">
                    <div><b>{t_inns}</b> Inns</div>
                    <div><b>{t_runs:,}</b> Runs</div>
                    <div><b>{avg}</b> Avg</div>
                    <div><b>{sr}</b> SR</div>
                </div>
            </div>
            """))

        # --- B. VS OPPOSITION (Aggregated Cleanly) ---
        if opposition and opposition != 'All':
            # Filter specifically for this opponent
            vs_opp = career_df[career_df['opponent'] == opposition].copy()
            
            if not vs_opp.empty:
                print(f"⚔️ vs {opposition.upper()}")
                
                # AGGREGATE to ensure single row (Fixes mashed text bug)
                agg_runs = vs_opp['runs'].sum()
                agg_inns = vs_opp['innings'].sum()
                agg_outs = vs_opp['dismissals'].sum()
                agg_balls = vs_opp['balls'].sum()
                
                agg_avg = round(agg_runs / agg_outs, 2) if agg_outs > 0 else agg_runs
                agg_sr = round((agg_runs / agg_balls) * 100, 1) if agg_balls > 0 else 0
                
                # Create clean single-row dataframe
                clean_df = pd.DataFrame([{
                    'Inns': agg_inns, 'Runs': agg_runs, 'Avg': agg_avg, 
                    'SR': agg_sr, 'Outs': agg_outs
                }])
                
                # Display cleanly using HTML to force formatting
                display(HTML(clean_df.to_html(index=False, border=0, justify="center", classes="table table-striped")))
            else:
                print(f"⚠️ No career stats found vs {opposition}.")

            # --- D. H2H NIGHTMARES (Filtered by ACTIVE SQUAD) ---
            if active_bowlers:
                try:
                    # Filter Raw Data: 
                    # 1. Striker is our player
                    # 2. Bowler is in the ACTIVE SQUAD list (The Fix)
                    # 3. Is a wicket
                    bunny_df = self.raw_df[
                        (self.raw_df['striker'] == player_name) &
                        (self.raw_df['bowler'].isin(active_bowlers)) & # <--- TARGETED FILTER
                        (self.raw_df['wicket_type'].isin(['bowled','caught','lbw','stumped','caught and bowled','hit wicket']))
                    ]
                    
                    if not bunny_df.empty:
                        print(f"\n🥊 H2H NIGHTMARES (Active {opposition} Bowlers)")
                        bunnies = bunny_df['bowler'].value_counts().reset_index()
                        bunnies.columns = ['Bowler', 'Outs']
                        bunnies['Style'] = bunnies['Bowler'].map(BOWLER_STYLES).fillna('-')
                        
                        def highlight(val):
                            color = '#d32f2f' if val >= 2 else '#333'
                            weight = 'bold' if val >= 2 else 'normal'
                            return f'color: {color}; font-weight: {weight}'
                            
                        display(bunnies.style.map(highlight, subset=['Outs']).hide(axis='index'))
                    else:
                        print(f"\n✅ No active {opposition} bowler has dismissed him yet.")
                except Exception as e:
                    print(e)

        # --- C. AT VENUE (Filtered by Years) ---
        if venue_id:
            aliases = get_venue_aliases(venue_id)
            if "_" in venue_id:
                 parts = venue_id.split("_")
                 if len(parts) > 1: aliases.append(parts[1])
            venue_pattern = '|'.join([re.escape(v) for v in aliases if v])
            v_display = venue_id.replace("IND_","").replace("AUS_","").replace("_", " ").title()
            
            try:
                # 🚨 DATE FILTER APPLIED HERE
                cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years)
                
                ven_df = self.raw_df[
                    (self.raw_df['striker'] == player_name) &
                    (self.raw_df['venue'].str.contains(venue_pattern, case=False, na=False)) &
                    (self.raw_df['start_date'] >= cutoff_date) # 👈 Uses the argument
                ]
                
                if not ven_df.empty:
                    print(f"\n🏟️ AT VENUE: {v_display} (Last {years} Years)")
                    runs = ven_df['runs_off_bat'].sum()
                    inns = len(ven_df['match_id'].unique())
                    outs = ven_df['wicket_type'].notna().sum()
                    avg = round(runs/outs, 1) if outs > 0 else runs
                    sr = int((runs/len(ven_df))*100)
                    hs = ven_df.groupby('match_id')['runs_off_bat'].sum().max()
                    
                    v_data = pd.DataFrame([{'Inns': inns, 'Runs': runs, 'Avg': avg, 'SR': sr, 'HS': hs}])
                    display(HTML(v_data.to_html(index=False, border=0)))
                else:
                    print(f"\n🏟️ AT VENUE: {v_display} (No Data in last {years} Years)")
            except: pass