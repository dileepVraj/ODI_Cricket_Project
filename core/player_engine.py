import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML
from venues import get_venue_aliases
from config.teams import TEAM_COLORS, BOWLER_STYLES, PLAYER_ROLES
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

    def compare_squads(self, team_a_name, team_a_players, team_b_name, team_b_players, venue_id, years=None, recorder=None):
        # 🎨 COLORS
        c1 = TEAM_COLORS.get(team_a_name, "#333")
        c2 = TEAM_COLORS.get(team_b_name, "#333")
        
        # 1. HEADER & SQUAD EXPERIENCE
        metrics_a = self._calculate_squad_metrics(team_a_name, team_a_players, years) 
        metrics_b = self._calculate_squad_metrics(team_b_name, team_b_players, years)
        
        avg_caps_a = int(metrics_a['Caps (Combined)'] / max(len(team_a_players), 1))
        avg_caps_b = int(metrics_b['Caps (Combined)'] / max(len(team_b_players), 1))

        display(HTML(f"""
        <div style="font-family: 'Segoe UI', Roboto, sans-serif; margin-bottom:25px;">
            <div style="background: linear-gradient(135deg, {c1} 0%, {c2} 100%); padding:12px; border-radius:8px 8px 0 0; color:white; text-align:center;">
                <h3 style="margin:0; font-size:18px;">⚔️ SQUAD COMPARISON (Last {years} Years)</h3>
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
        # 2. PLAYER STATS SETUP
        # -------------------------------------------------------------
        aliases = get_venue_aliases(venue_id)
        if "_" in venue_id:
            suffix_key = venue_id.split("_", 1)[1] 
            suffix_aliases = get_venue_aliases(suffix_key)
            if suffix_aliases:
                aliases = list(set(aliases + suffix_aliases))
        if not aliases:
            aliases = [venue_id]
            if "_" in venue_id: aliases.append(venue_id.split("_", 1)[1])

        venue_pattern = '|'.join([re.escape(v) for v in aliases if v])
        
        display(HTML(f"""
        <div style="background:#334155; color:#e2e8f0; padding:10px 15px; border-radius:6px; margin:20px 0 10px 0; border-left:5px solid #34d399; font-family:'Segoe UI', sans-serif;">
            <div style="font-weight:bold; font-size:14px;">📊 DETAILED PLAYER STATISTICS & VENUE METRICS</div>
            <div style="font-size:11px; opacity:0.8; margin-top:2px;">
                INCLUDES: Form, (vs Opponent), and Venue History ({venue_id})
            </div>
        </div>
        """))

        # --- NESTED FUNCTION: RENDER PRO TABLE ---
        def render_pro_table(team_name, players, opponent, color):
            
            # Use Global Role Map
            role_map = PLAYER_ROLES
            
            # --- 1. FETCH DATA ---
            if not players: return f"<div>No players selected for {team_name}</div>"
            
            data = [self._get_stats(p, opponent, venue_pattern, years) for p in players]
            df = pd.DataFrame(data)
            
            if df.empty: return f"<div>No data available for {team_name}</div>"

            # --- 2. THRESHOLDS (Full Spectrum 4-Tier) ---
            BAT_GREAT = 45; BAT_GOOD = 30; BAT_AVG = 20
            BOWL_GREAT = 8; BOWL_GOOD = 4; BOWL_AVG = 2
            MIN_VENUE_INNS = 3 

            rows = ""
            for i, row in df.iterrows():
                bg = "#ffffff" if i % 2 == 0 else "#f8f9fa"
                player_name = row['Player']
                
                # --- 3. DETERMINE ROLE ---
                role = role_map.get(player_name, 'Auto') 
                
                # --- 4. PARSE STATS ---
                try:
                    raw_bat = str(row.get('Bat Form',''))
                    bat_scores = [int(x.replace('*','').strip()) for x in raw_bat.split(',') if x.replace('*','').strip().isdigit()]
                    rec_bat_avg = sum(bat_scores) / len(bat_scores) if bat_scores else 0
                except: rec_bat_avg = 0

                try:
                    bowl_form_str = str(row.get('Bowl Form',''))
                    rec_wkts = 0
                    if '/' in bowl_form_str:
                        for m in bowl_form_str.split(','):
                            if '/' in m:
                                p = m.split('/')
                                if p[0].strip().isdigit(): rec_wkts += int(p[0].strip())
                except: rec_wkts = 0

                try: ven_avg = float(str(row.get('Ven Avg', 0)).replace('-','0').replace('DNB','0'))
                except: ven_avg = 0
                try: ven_wkts = int(str(row.get('Ven Wkts', 0)).replace('-','0'))
                except: ven_wkts = 0
                try: ven_inns = int(str(row.get('Ven Inns', 0)).replace('-','0'))
                except: ven_inns = 0
                try: ven_runs_int = int(str(row.get('Ven Runs', 0)).replace('-','0').replace('DNB','0'))
                except: ven_runs_int = 0

                # Auto-Role Fallback
                if role == 'Auto':
                    if rec_wkts >= 5 or ven_wkts >= 5: role = 'Bowler'
                    else: role = 'Batter'

                # --- 5. ICONS & BADGES ---
                acronyms = []
                
                # 🟢 ROLE ICONS (The Final Touch)
                role_icon = ""
                if role == 'Batter': role_icon = "🏏"
                elif role == 'Bowler': role_icon = "⚾"
                elif role == 'Batting All-Rounder': role_icon = "🏏⚾"
                elif role == 'Bowling All-Rounder': role_icon = "⚾🏏"
                
                # Badge Helper
                def get_badge(text, tier):
                    if tier == 'GE': return f"<span style='color:#155724; background:#d4edda; border:1px solid #c3e6cb; font-weight:bold; font-size:9px; padding:1px 3px; border-radius:3px; margin-right:2px;'>{text}</span>" 
                    if tier == 'GD': return f"<span style='color:#0f5132; background:#e2e3e5; border:1px solid #d6d8db; font-weight:bold; font-size:9px; padding:1px 3px; border-radius:3px; margin-right:2px;'>{text}</span>" 
                    if tier == 'AV': return f"<span style='color:#856404; background:#fff3cd; border:1px solid #ffeeba; font-weight:bold; font-size:9px; padding:1px 3px; border-radius:3px; margin-right:2px;'>{text}</span>" 
                    if tier == 'DP': return f"<span style='color:#721c24; background:#f8d7da; border:1px solid #f5c6cb; font-weight:bold; font-size:9px; padding:1px 3px; border-radius:3px; margin-right:2px;'>{text}</span>" 
                    return ""

                # === BATTING EVALUATION ===
                if role in ['Batter', 'Batting All-Rounder', 'Bowling All-Rounder']:
                    if rec_bat_avg >= BAT_GREAT: acronyms.append(get_badge("RBF-GE", "GE"))
                    elif rec_bat_avg >= BAT_GOOD: acronyms.append(get_badge("RBF-GD", "GD"))
                    elif rec_bat_avg >= BAT_AVG: acronyms.append(get_badge("RBF-AVG", "AV"))
                    else: acronyms.append(get_badge("RBF-DIP", "DP"))
                    
                    if ven_inns >= MIN_VENUE_INNS:
                        if ven_avg >= BAT_GREAT: acronyms.append(get_badge("VBF-GE", "GE"))
                        elif ven_avg >= BAT_GOOD: acronyms.append(get_badge("VBF-GD", "GD"))
                        elif ven_avg >= BAT_AVG: acronyms.append(get_badge("VBF-AVG", "AV"))
                        else: acronyms.append(get_badge("VBF-DIP", "DP"))

                # === BOWLING EVALUATION ===
                if role in ['Bowler', 'Bowling All-Rounder', 'Batting All-Rounder']:
                    if rec_wkts >= BOWL_GREAT: acronyms.append(get_badge("RBWF-GE", "GE"))
                    elif rec_wkts >= BOWL_GOOD: acronyms.append(get_badge("RBWF-GD", "GD"))
                    elif rec_wkts >= BOWL_AVG: acronyms.append(get_badge("RBWF-AVG", "AV"))
                    else: acronyms.append(get_badge("RBWF-DIP", "DP"))

                    if ven_inns >= MIN_VENUE_INNS:
                        if ven_wkts >= 8: acronyms.append(get_badge("VWF-GE", "GE"))
                        elif ven_wkts >= 5: acronyms.append(get_badge("VWF-GD", "GD"))
                        elif ven_wkts >= 3: acronyms.append(get_badge("VWF-AVG", "AV"))
                        else: acronyms.append(get_badge("VWF-DIP", "DP"))

                # --- 6. RENDER ROWS ---
                badges = " ".join(acronyms)
                
                # Name with Role Icon
                p_name = f"<div style='font-weight:700; color:{color}; font-size:13px;'>{role_icon} {player_name}</div><div style='margin-top:3px;'>{badges}</div>"

                bat_f = str(row.get('Bat Form', '-'))
                v_runs_val = str(row.get('Ven Runs', '-'))
                v_inns_val = str(row.get('Ven Inns', '-'))
                v_runs_display = f"{v_runs_val} <span style='font-size:10px; color:#666;'>({v_inns_val})</span>" if v_runs_val not in ['-','0'] else v_runs_val
                bowl_f = str(row.get('Bowl Form', '-'))

                rows += f"""
                <tr style="background:{bg}; border-bottom:1px solid #dee2e6; font-family:'Segoe UI', sans-serif; font-size:12px; height:45px;">
                    <td style="padding:4px 8px; text-align:left; border-right:3px solid {color}; vertical-align:middle;">{p_name}</td>
                    <td style="padding:6px; vertical-align:middle;">{row['Inns']}</td>
                    <td style="padding:6px; font-size:11px; color:#555; vertical-align:middle;">{bat_f}</td>
                    <td style="padding:6px; font-weight:600; background:#f1f3f5; vertical-align:middle;">{row['Bat Avg']}</td>
                    <td style="padding:6px; vertical-align:middle;">{row['vs Opp']}</td>
                    <td style="padding:6px; background:#fff3cd; font-weight:bold; border-left:2px solid #ffeeba; vertical-align:middle;">{row['Ven Avg']}</td>
                    <td style="padding:6px; background:#fff3cd; vertical-align:middle;">{v_runs_display}</td>
                    <td style="padding:6px; background:#fff3cd; border-right:2px solid #ffeeba; vertical-align:middle;">{row['Ven HS']}</td>
                    <td style="padding:6px; font-size:11px; color:#0d6efd; text-align:left; vertical-align:middle;">{bowl_f}</td>
                    <td style="padding:6px; vertical-align:middle;">{row['Bowl Econ']}</td>
                    <td style="padding:6px; background:#e8f4f8; font-weight:bold; color:#0c5460; vertical-align:middle;">{row['Ven Econ']}</td>
                    <td style="padding:6px; background:#e8f4f8; font-weight:bold; color:#0c5460; vertical-align:middle;">{row['Ven Wkts']}</td>
                </tr>"""

            # --- 7. LEGEND ---
            legend_html = f"""
            <div style="margin-top:5px; padding:10px 15px; background:#e2e8f0; border-radius:0 0 8px 8px; font-size:10px; color:#475569;">
                <div style="font-weight:bold; margin-bottom:5px;">LEGEND (Last 5 Inns):</div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                    <div>
                        <div style="font-weight:bold; margin-bottom:2px;">🏏 Batting (Avg)</div>
                        <span style="background:#d4edda; color:#155724; padding:1px 4px; border-radius:3px;">GE &gt; 45</span>
                        <span style="background:#e2e3e5; color:#0f5132; padding:1px 4px; border-radius:3px;">GD 30-45</span>
                        <span style="background:#fff3cd; color:#856404; padding:1px 4px; border-radius:3px;">AVG 20-30</span>
                        <span style="background:#f8d7da; color:#721c24; padding:1px 4px; border-radius:3px;">DIP &lt; 20</span>
                    </div>
                    <div>
                        <div style="font-weight:bold; margin-bottom:2px;">⚾ Bowling (Wkts)</div>
                        <span style="background:#cfe2ff; color:#084298; padding:1px 4px; border-radius:3px;">GE &gt; 8</span>
                        <span style="background:#e2e3e5; color:#052c65; padding:1px 4px; border-radius:3px;">GD 4-7</span>
                        <span style="background:#fff3cd; color:#664d03; padding:1px 4px; border-radius:3px;">AVG 2-3</span>
                        <span style="background:#f8d7da; color:#721c24; padding:1px 4px; border-radius:3px;">DIP 0-1</span>
                    </div>
                </div>
            </div>
            """

            return f"""
            <div style="margin-bottom:30px; border-radius:8px; overflow:hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border:1px solid #e0e0e0;">
                <div style="background:{color}; color:white; padding:10px 15px; font-weight:bold; font-size:14px; letter-spacing:1px; text-transform:uppercase;">
                    {team_name} <span style="font-size:11px; opacity:0.8; float:right;">(Last {years} Years)</span>
                </div>
                <div style="overflow-x:auto;">
                    <table style="width:100%; min-width:1100px; border-collapse:collapse; text-align:center; color:#333;">
                        <colgroup>
                            <col style="width:200px;"> <col style="width:50px;">  <col style="width:160px;"> <col style="width:50px;">  <col style="width:50px;">  <col style="width:50px;">  <col style="width:50px;">  <col style="width:50px;">  <col style="width:220px;"> <col style="width:50px;">  <col style="width:50px;">  <col style="width:50px;">  
                        </colgroup>
                        <thead>
                            <tr style="background:#343a40; color:white; font-size:11px; text-transform:uppercase; height:40px;">
                                <th style="text-align:left; padding-left:10px;">Player & Signals</th>
                                <th>Inns</th>
                                <th>Form (Bat)</th>
                                <th style="background:#495057;">Avg</th>
                                <th>vs {opponent[:3].upper()}</th>
                                <th style="background:#ffc107; color:#212529;">V.Avg</th>
                                <th style="background:#ffc107; color:#212529;">V.Runs</th>
                                <th style="background:#ffc107; color:#212529;">V.HS</th>
                                <th style="text-align:left; padding-left:10px;">Form (Bowl)</th>
                                <th>Econ</th>
                                <th style="background:#17a2b8;">V.Econ</th>
                                <th style="background:#17a2b8;">V.Wkts</th>
                            </tr>
                        </thead>
                        <tbody>{rows}</tbody>
                    </table>
                </div>
                {legend_html}
            </div>"""

        # --- IMPORTANT: EXECUTE TABLE RENDER ---
        display(HTML(render_pro_table(team_a_name, team_a_players, team_b_name, c1)))
        display(HTML(render_pro_table(team_b_name, team_b_players, team_a_name, c2)))

        # -------------------------------------------------------------
        # 3. TACTICAL MATRIX
        # -------------------------------------------------------------
        print("\n")
        display(HTML(f"<div style='background:#444; color:white; padding:8px; border-radius:4px; font-weight:bold; margin-bottom:10px; font-family:sans-serif;'>📊 TACTICAL MATRIX: ARCHETYPES (Last {years} Years)</div>"))
        
        self.analyze_squad_types(team_a_name, team_a_players, team_b_players, years, recorder=recorder)
        print("\n")
        self.analyze_squad_types(team_b_name, team_b_players, team_a_players, years, recorder=recorder)

        # -------------------------------------------------------------
        # 4. MATCHUPS
        # -------------------------------------------------------------
        display(HTML(f"""<div style="background:#343a40; color:white; padding:8px; border-radius:6px; font-weight:bold; margin-bottom:10px; font-family:'Segoe UI';">⚔️ HEAD-TO-HEAD MATCHUPS</div>"""))
        
        left = widgets.Output(); right = widgets.Output()
        
        with left:
            display(HTML(f"<div style='font-weight:bold; color:{c1}; margin-bottom:10px; border-bottom:3px solid {c1};'>🛡️ {team_a_name.upper()} BATTING</div>"))
            for p in team_a_players: self._display_batter_vs_bowlers(p, team_a_name, team_b_players, recorder=recorder)
        
        with right:
            display(HTML(f"<div style='font-weight:bold; color:{c2}; margin-bottom:10px; border-bottom:3px solid {c2};'>🛡️ {team_b_name.upper()} BATTING</div>"))
            for p in team_b_players: self._display_batter_vs_bowlers(p, team_b_name, team_a_players, recorder=recorder)
            
        display(widgets.HBox([left, right], layout=widgets.Layout(width='100%', gap='30px')))

    # --- NEW: ARCHETYPE ANALYSIS ---
    def analyze_squad_types(self, team_name, players, opposition_bowlers, years=None, recorder=None):
        """
        Generates a 'Tactical Breakdown' of how batters perform against
        the SPECIFIC bowling types present in the opposition's squad.
        UPDATED: Smartly ignores pure batters to prevent false warnings.
        """
        
        # 📅 DYNAMIC DATE FILTER
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years)
        window_df = self.raw_df[self.raw_df['start_date'] >= cutoff_date]
        
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
            
            # A. Explicit Ignore (if you used the Part-Timer tag)
            if style == '🚫 Part-Timer':
                continue

            # B. Known Bowler -> Add to Matrix
            if style != 'Unknown':
                if style not in active_styles_data: 
                    active_styles_data[style] = []
                active_styles_data[style].append(b)
            
            # C. Unknown Player -> SMART CHECK
            else:
                # Check if they have actually bowled in the selected window
                # We count the number of balls they delivered in the database
                bowler_stats = window_df[window_df['bowler'] == b]
                balls_delivered = len(bowler_stats)
                
                # 🚨 THRESHOLD: Only warn if they bowled more than 1 over (6 balls)
                # This ignores pure batters (0 balls) and accidental 1-ball events.
                if balls_delivered > 6:
                    missing_bowlers.append(f"{b} ({balls_delivered} balls)")

        # 🚨 DISPLAY WARNING ONLY FOR ACTIVE BOWLERS
        if missing_bowlers:
            print(f"⚠️ WARNING: The following ACTIVE BOWLERS in {team_name}'s opposition are missing from teams.py:")
            print(f"   {', '.join(missing_bowlers)}")
            print("   Please add them to config/teams.py to see them in the Matrix.")

        if not active_styles_data: 
            # If no styles found, it might be a data issue, but we don't spam print here anymore
            return

        # 2. DISPLAY ATTACK BREAKDOWN (Enhanced Badges)
        c1 = TEAM_COLORS.get(team_name, "#333")
        
        style_badges = ""
        for style, bowlers_list in active_styles_data.items():
            count = len(bowlers_list)
            names_str = ", ".join(bowlers_list)
            
            icon = style.split(' ')[0]
            name = style.split(' ', 1)[1] if ' ' in style else style
            
            style_badges += f"""
            <div style="background:#fff; border:1px solid #ddd; padding:6px 10px; border-radius:8px; font-size:11px; font-weight:bold; color:#555; display:flex; flex-direction:column; align-items:center; gap:2px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); min-width: 100px;">
                <div style="display:flex; align-items:center; gap:5px; margin-bottom:2px;">
                    <span style="font-size:14px;">{icon}</span>
                    <span>{name}</span>
                    <span style="background:{c1}; color:white; padding:1px 6px; border-radius:10px; font-size:10px;">{count}</span>
                </div>
                <div style="font-size:9px; color:#777; font-weight:normal; text-align:center; max-width:140px; line-height:1.1;">
                    {names_str}
                </div>
            </div>
            """

        display(HTML(f"""
        <div style="font-family:'Segoe UI', sans-serif; margin-bottom:10px; border:1px solid #eee; border-radius:6px; overflow:hidden;">
            <div style="background:#f8f9fa; padding:6px 10px; font-weight:bold; color:#333; border-bottom:1px solid #eee; font-size:12px;">
                🛡️ THREAT MATRIX: {team_name} Batters vs Opposition Team Bowler Types
            </div>
            <div style="padding:10px; display:flex; flex-wrap:wrap; gap:8px; background:white;">
                {style_badges}
            </div>
        </div>
        """))

        # 3. CALCULATE BATTER PERFORMANCE VS THESE TYPES
        target_styles = list(active_styles_data.keys())
        table_data = []
        
        for batter in players:
            row = {'Player': batter}
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
                        runs = style_df['runs_off_bat'].sum()
                        balls = style_df['match_id'].count()
                        outs = style_df['wicket_type'].isin(['bowled','caught','lbw','stumped','caught and bowled','hit wicket']).sum()
                        
                        avg = round(runs/outs, 1) if outs > 0 else runs
                        sr = int((runs/balls)*100) if balls > 0 else 0
                        
                        color = "#2e7d32" if avg > 40 else "#c62828" if avg < 25 else "#333"
                        row[style] = f"<span style='color:{color}; font-weight:bold;'>{avg}</span> <span style='font-size:10px; color:#999;'>({sr})</span>"
                        row[f"{style}_raw"] = avg
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
                display_cols = [c for c in target_styles if c in r]
                cells = "".join([f"<td style='padding:6px; border-bottom:1px solid #eee; font-size:12px;'>{r[col]}</td>" for col in display_cols])
                rows_html += f"<tr><td style='padding:6px; font-weight:bold; text-align:right; border-right:2px solid {c1}; color:{c1}; font-size:12px;'>{r['Player']}</td>{cells}</tr>"
            
            display(HTML(f"""
            <div style="border:1px solid #ddd; border-radius:6px; overflow-x:auto; margin-bottom:20px;">
                <table style="width:100%; border-collapse:collapse; text-align:center; font-family:sans-serif;">
                    <thead><tr><th style="padding:6px; text-align:right; background:{c1}; color:white; font-size:11px;">BATTER</th>{headers}</tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
                <div style="padding:4px; background:#fafafa; color:#777; font-size:9px; text-align:right;">
                    <i>Stats vs All bowlers of this type in database</i>
                </div>
            </div>
            """))

            if recorder:
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


    # --- HELPERS ---

    def _calculate_squad_metrics(self, team, players, years=None):
        # 📅 DYNAMIC DATE FILTER
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years)
        
        # Filter the Raw DB first
        window_df = self.raw_df[self.raw_df['start_date'] >= cutoff_date]

        mask = (window_df['striker'].isin(players)) | (window_df['bowler'].isin(players))
        df = window_df[mask]
        
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

    def _get_stats(self, player, opp, venue_pattern, years=None):
        # 1. SETUP & DATE FILTER
        cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years)
        
        # Get ALL activity for this player (Batting OR Bowling)
        # This ensures we know they played the match even if they did nothing in one discipline
        all_activity = self.raw_df[
            ((self.raw_df['striker'] == player) | (self.raw_df['bowler'] == player)) &
            (self.raw_df['start_date'] >= cutoff_date)
        ]
        
        if all_activity.empty:
            return {
                'Player': player, 'Inns': 0, 'Bat Form': "-", 'Bat Avg': "-", 'vs Opp': "-", 
                'Ven Inns': "-", 'Ven Runs': "-", 'Ven Avg': "-", 'Ven HS': "-",
                'Bowl Form': "-", 'Bowl Econ': "-", 'Ven Econ': "-", 'Ven Wkts': "-", 'Ven Matches': "-"
            }

        # Get Unique Match IDs sorted by Date (Newest First)
        # 🚨 CRITICAL FIX: Explicit Sort to prevent random match selection
        matches_played = all_activity.drop_duplicates('match_id').sort_values('start_date', ascending=False)
        last_5_ids = matches_played['match_id'].head(5).tolist()

        # ---------------------------------------------------------
        # 2. BATTING FORM (Smart DNB)
        # ---------------------------------------------------------
        form_bat = []
        for m_id in last_5_ids:
            # Check if they appeared as a striker
            m_bat = self.raw_df[(self.raw_df['match_id'] == m_id) & (self.raw_df['striker'] == player)]
            
            if m_bat.empty:
                # They played (we know from all_activity) but didn't bat -> DNB
                form_bat.append("DNB")
            else:
                r = m_bat['runs_off_bat'].sum()
                is_out = m_bat['wicket_type'].notna().any()
                score = f"{int(r)}" if is_out else f"{int(r)}*"
                form_bat.append(score)

        # Career Batting Stats (Windowed)
        bat_window = self.raw_df[(self.raw_df['striker'] == player) & (self.raw_df['start_date'] >= cutoff_date)]
        car_inns = bat_window['match_id'].nunique()
        total_runs = bat_window['runs_off_bat'].sum()
        total_outs = bat_window['wicket_type'].count()
        avg = round(total_runs / total_outs, 1) if total_outs > 0 else total_runs

        # vs Opponent
        opp_df = bat_window[bat_window['bowling_team'] == opp]
        opp_runs = opp_df['runs_off_bat'].sum()
        opp_outs = opp_df['wicket_type'].count()
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
            # Check if they played at venue but DNB
            ven_activity = all_activity[all_activity['venue'].str.contains(venue_pattern, case=False, na=False)]
            if not ven_activity.empty:
                v_runs_disp = "DNB"

        # ---------------------------------------------------------
        # 4. BOWLING FORM (Strict Legal Balls)
        # ---------------------------------------------------------
        form_bowl = []
        for m_id in last_5_ids:
            # Check if they bowled
            m_bowl = self.raw_df[(self.raw_df['match_id'] == m_id) & (self.raw_df['bowler'] == player)]
            
            if m_bowl.empty:
                # Played but didn't bowl
                form_bowl.append("-") 
            else:
                # Wickets (Standard 6)
                wkts = m_bowl['wicket_type'].isin(['bowled','caught','lbw','stumped','caught and bowled','hit wicket']).sum()
                
                # Runs (Bat + Wide + NB)
                wides = m_bowl['wides'].sum() if 'wides' in m_bowl.columns else 0
                nbs = m_bowl['noballs'].sum() if 'noballs' in m_bowl.columns else 0
                runs = m_bowl['runs_off_bat'].sum() + wides + nbs
                
                # Legal Balls (Exclude Wides/NBs for over count)
                # Note: 'wides' column > 0 means it's an illegal ball. Same for 'noballs'.
                legal_mask = (m_bowl['wides'].fillna(0) == 0) & (m_bowl['noballs'].fillna(0) == 0)
                legal_balls = m_bowl[legal_mask].shape[0]
                
                overs = legal_balls // 6
                balls = legal_balls % 6
                overs_disp = f"{overs}.{balls}" if balls > 0 else f"{overs}"
                
                form_bowl.append(f"{wkts}/{int(runs)} ({overs_disp})")

        # Bowling Career
        bowl_window = self.raw_df[(self.raw_df['bowler'] == player) & (self.raw_df['start_date'] >= cutoff_date)]
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
            'Bat Form': ", ".join(form_bat), # Removed reversal, matches are already sorted Newest->Oldest
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

    def _display_batter_vs_bowlers(self, batter, bat_team, bowlers, recorder=None):
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
            
            # Calculate Avg/SR here for both display and AI
            avg = round(r/o, 1) if o > 0 else r
            sr = round(r/bl*100, 1) if bl > 0 else 0
            
            data.append({
                'Bowler': f"{b} ({style_tag}){bunny_tag}", 
                'Runs': r, 'Balls': bl, 'Outs': o, 
                'Avg': avg, 'SR': sr,
                'RawName': b, 'RawStyle': style_tag # Store raw names for AI logging
            })

        if data:
            hex = TEAM_COLORS.get(bat_team, '#000')
            display(HTML(f"<div style='font-weight:700; color:{hex}; font-size:12px; margin-top:8px;'>🏏 {batter}</div>"))
            df = pd.DataFrame(data).sort_values('Balls', ascending=False)
            
            # Display Logic (Preserved)
            def color_rows(row):
                val = row['Outs']
                color = '#333'; weight = 'normal'
                if val >= 3: color = '#d32f2f'; weight = 'bold'
                elif val == 2: color = '#e67e22'; weight = 'bold'
                elif val == 0: color = '#2e7d32'; weight = 'bold'
                return [f'color: {color}; font-weight: {weight}' if col == 'Bowler' else '' for col in row.index]

            # Filter columns for display (Hide RawName/RawStyle)
            display_cols = ['Bowler', 'Runs', 'Balls', 'Outs', 'Avg', 'SR']
            styler = df[display_cols].style.apply(color_rows, axis=1).format("{:.1f}", subset=['SR', 'Avg']).hide(axis='index')
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