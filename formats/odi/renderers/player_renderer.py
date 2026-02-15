from typing import List, Dict, Optional, Any
from core.interfaces.player_interface import PlayerProfile, BattingStats, BowlingStats, SquadComparisonData

class PlayerHTMLRenderer:
    """
    Handles all HTML generation for Player Analytics.
    Input: Strictly typed Dataclasses from PlayerEngine.
    Output: HTML Strings (for Display).
    """

    @staticmethod
    def render_profile_card(stats: PlayerProfile, years: int) -> str:
        """
        Renders the main Player Profile card (Career Summary).
        """
        # Extract Data
        name = stats.name
        role = stats.role
        bat = stats.batting
        bowl = stats.bowling
        
        # Color Logic
        bg_color = "#fff"
        border_color = "#222"

        # HTML Construction
        html = f"""
        <div style="background:{bg_color}; border-left:4px solid {border_color}; padding:15px; margin-bottom:20px; font-family:'Segoe UI', sans-serif; box-shadow:0 2px 5px rgba(0,0,0,0.05);">
            <div style="font-size:14px; color:#222; font-weight:bold; letter-spacing:1px; margin-bottom:10px;">👤 {name.upper()} <span style="font-weight:normal; color:#777; font-size:11px;">(Last {years} Years)</span></div>
            <div style="display:flex; gap:30px; align-items:flex-start;">
                <!-- BATTING -->
                <div style="flex:1;">
                     <div style="font-size:11px; color:#555; font-weight:bold; letter-spacing:1px; margin-bottom:5px;">BATTING</div>
                     <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; font-size:13px; margin-bottom:8px;">
                        <div><b>{bat.innings if bat else 0}</b> Inns</div>
                        <div><b>{bat.runs if bat else 0:,}</b> Runs</div>
                        <div><b>{bat.average if bat else "-"}</b> Avg</div>
                        <div><b>{bat.strike_rate if bat else "-"}</b> SR</div>
                     </div>
                     <div style="display:flex; gap:15px; font-size:12px; color:#444; background:#f4f4f4; padding:5px 8px; border-radius:4px;">
                        <span><b>{bat.centuries if bat else 0}</b> 100s</span>
                        <span><b>{bat.fifties if bat else 0}</b> 50s</span>
                        <span><b>{bat.highest_score if bat else 0}</b> HS</span>
                     </div>
                </div>
        """
        
        if bowl:
            html += f"""
                <div style="width:1px; background:#eee;"></div>
                <div style="flex:1;">
                    <div style="font-size:11px; color:#555; font-weight:bold; letter-spacing:1px; margin-bottom:5px;">BOWLING</div>
                     <div style="display:flex; gap:15px; font-size:13px;">
                        <div><b>{bowl.wickets}</b> Wkts</div>
                        <div><b>{bowl.average}</b> Avg</div>
                        <div><b>{bowl.economy}</b> Econ</div>
                        <div><b>{bowl.best_figures}</b> Best</div>
                    </div>
                </div>
            """
            
        html += """
            </div>
        </div>
        """
        return html

    @staticmethod
    def get_role_icon(role: str, player_name: str = "") -> str:
        """Returns the high-aesthetic emoji for a player role."""
        role_lower = role.lower()
        if "batter" == role_lower: return "🏏"
        if "bowler" == role_lower: return "⚾"
        if "batting all-rounder" in role_lower: return "🏏⚾"
        if "bowling all-rounder" in role_lower: return "⚾🏏"
        if "all-rounder" in role_lower: return "⚡"
        if "wicketkeeper" in role_lower or "wk" in role_lower: return "🧤"
        return "👤"

    @staticmethod
    def render_squad_table(team_name: str, players_data: List[Dict], opponent_name: str, team_color: str, years: int) -> str:
        """
        Renders the Pro Table for Squad Comparison.
        Restores iconic emojis and high-density formatting.
        """
        from config.shared.team_colors import TEAM_COLORS
        
        # Thresholds
        BAT_GREAT = 45; BAT_GOOD = 30; BAT_AVG = 20
        BOWL_GREAT = 8; BOWL_GOOD = 4; BOWL_AVG = 2
        MIN_VENUE_INNS = 3

        rows = ""
        for i, row in enumerate(players_data):
            bg = TEAM_COLORS['white'] if i % 2 == 0 else TEAM_COLORS['light_grey']
            player_name = row['Player']
            role = row.get('Role', 'Batter')
            icon = PlayerHTMLRenderer.get_role_icon(role, player_name)

            # Signal Logic (Badges)
            acronyms = []
            
            # 1. Batting Form
            try:
                raw_bat = str(row.get('Bat Form',''))
                bat_scores = [int(x.replace('*','').strip()) for x in raw_bat.split(',') if x.replace('*','').strip().isdigit()]
                rec_bat_avg = sum(bat_scores) / len(bat_scores) if bat_scores else 0
            except (ValueError, TypeError): rec_bat_avg = 0

            # 2. Bowling Form
            try:
                bowl_form_str = str(row.get('Bowl Form',''))
                rec_wkts = 0
                if '/' in bowl_form_str:
                    for m in bowl_form_str.split(','):
                        if '/' in m:
                            p = m.split('/')
                            if p[0].strip().isdigit(): rec_wkts += int(p[0].strip())
            except (ValueError, TypeError): rec_wkts = 0

            # 3. Venue
            try: ven_avg = float(str(row.get('Ven Avg', 0)).replace('-','0').replace('DNB','0'))
            except (ValueError, TypeError): ven_avg = 0
            try: ven_wkts = int(str(row.get('Ven Wkts', 0)).replace('-','0'))
            except (ValueError, TypeError): ven_wkts = 0
            try: ven_inns = int(str(row.get('Ven Inns', 0)).replace('-','0'))
            except (ValueError, TypeError): ven_inns = 0

            # Badge Helper
            def get_badge(text, tier):
                from config.shared.team_colors import TEAM_COLORS
                colors = {
                    'GE': (TEAM_COLORS['dark_green'], TEAM_COLORS['green_bg'], TEAM_COLORS['green_border']),
                    'GD': (TEAM_COLORS['dark_grey_text'], TEAM_COLORS['grey_bg'], TEAM_COLORS['grey_border']),
                    'AV': (TEAM_COLORS['dark_orange'], TEAM_COLORS['orange_bg'], TEAM_COLORS['orange_border']),
                    'DP': (TEAM_COLORS['dark_red'], TEAM_COLORS['red_bg'], TEAM_COLORS['red_border'])
                }
                c, b, bo = colors.get(tier, (TEAM_COLORS['white'], TEAM_COLORS['white'], TEAM_COLORS['white']))
                return f"<span style='color:{c}; background:{b}; border:1px solid {bo}; font-weight:bold; font-size:9px; padding:1px 3px; border-radius:3px; margin-right:2px;'>{text}</span>"

            # Eval Bat
            if "Batter" in role or "All-Rounder" in role:
                if rec_bat_avg >= BAT_GREAT: acronyms.append(get_badge("RBF-GE", "GE"))
                elif rec_bat_avg >= BAT_GOOD: acronyms.append(get_badge("RBF-GD", "GD"))
                elif rec_bat_avg >= BAT_AVG: acronyms.append(get_badge("RBF-AVG", "AV"))
                else: acronyms.append(get_badge("RBF-DIP", "DP"))
                
                if ven_inns >= MIN_VENUE_INNS:
                    if ven_avg >= BAT_GREAT: acronyms.append(get_badge("VBF-GE", "GE"))
                    elif ven_avg >= BAT_GOOD: acronyms.append(get_badge("VBF-GD", "GD"))
                    elif ven_avg >= BAT_AVG: acronyms.append(get_badge("VBF-AVG", "AV"))
                    else: acronyms.append(get_badge("VBF-DIP", "DP"))

            # Eval Bowl
            if "Bowler" in role or "All-Rounder" in role:
                if rec_wkts >= BOWL_GREAT: acronyms.append(get_badge("RBWF-GE", "GE"))
                elif rec_wkts >= BOWL_GOOD: acronyms.append(get_badge("RBWF-GD", "GD"))
                elif rec_wkts >= BOWL_AVG: acronyms.append(get_badge("RBWF-AVG", "AV"))
                else: acronyms.append(get_badge("RBWF-DIP", "DP"))

                if ven_inns >= MIN_VENUE_INNS:
                    if ven_wkts >= 8: acronyms.append(get_badge("VWF-GE", "GE"))
                    elif ven_wkts >= 5: acronyms.append(get_badge("VWF-GD", "GD"))
                    elif ven_wkts >= 3: acronyms.append(get_badge("VWF-AVG", "AV"))
                    else: acronyms.append(get_badge("VWF-DIP", "DP"))

            badges = " ".join(acronyms)
            p_name = f"<div style='font-weight:700; color:{team_color}; font-size:13px;'>{icon} {player_name}</div><div style='margin-top:3px;'>{badges}</div>"
            
            bat_f = str(row.get('Bat Form', '-'))
            bowl_f = str(row.get('Bowl Form', '-'))
            v_runs = f"{row.get('Ven Runs', '-')} <span style='font-size:10px; color:#666;'>({row.get('Ven Inns', '-')})</span>"

            rows += f"""
            <tr style="background:{bg}; border-bottom:1px solid #dee2e6; font-size:12px; height:45px;">
                <td style="padding:4px 8px; text-align:left; border-right:3px solid {team_color}; vertical-align:middle;">{p_name}</td>
                <td>{row.get('Inns','-')}</td>
                <td style="font-size:10px; color:#555; white-space:nowrap;">{bat_f}</td>
                <td style="font-weight:600; background:#f1f3f5;">{row.get('Bat Avg','-')}</td>
                <td>{row.get('vs Opp','-')}</td>
                <td style="background:#fff3cd; font-weight:bold; border-left:2px solid #ffeeba;">{row.get('Ven Avg','-')}</td>
                <td style="background:#fff3cd;">{v_runs}</td>
                <td style="background:#fff3cd; border-right:2px solid #ffeeba;">{row.get('Ven HS','-')}</td>
                <td style="font-size:10px; color:#0d6efd; text-align:left; white-space:nowrap;">{bowl_f}</td>
                <td>{row.get('Bowl Econ','-')}</td>
                <td style="background:#e8f4f8; font-weight:bold; color:#0c5460;">{row.get('Ven Econ','-')}</td>
                <td style="background:#e8f4f8; font-weight:bold; color:#0c5460;">{row.get('Ven Wkts','-')}</td>
            </tr>"""

        # Legend & Table Wrap (Simplified for brevity but maintaining high density)
        return f"""
        <div style="margin-bottom:30px; border-radius:8px; overflow:hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border:1px solid #e0e0e0; font-family:'Segoe UI', sans-serif;">
            <div style="background:{team_color}; color:white; padding:10px 15px; font-weight:bold; font-size:14px; text-transform:uppercase;">
                {team_name} <span style="font-size:11px; opacity:0.8; float:right;">(Last {years} Years)</span>
            </div>
            <div style="overflow-x:auto;">
                <table style="width:100%; min-width:1100px; border-collapse:collapse; text-align:center; color:#333;">
                    <thead>
                        <tr style="background:#343a40; color:white; font-size:11px; text-transform:uppercase; height:40px;">
                            <th style="text-align:left; padding-left:10px;">Player & Signals</th>
                            <th>Inns</th><th>Form (Bat)</th><th style="background:#495057;">Avg</th><th>vs {opponent_name[:3].upper()}</th>
                            <th style="background:#ffc107; color:#212529;">V.Avg</th><th style="background:#ffc107; color:#212529;">V.Runs</th><th style="background:#ffc107; color:#212529;">V.HS</th>
                            <th style="text-align:left; padding-left:10px;">Form (Bowl)</th><th>Econ</th><th style="background:#17a2b8;">V.Econ</th><th style="background:#17a2b8;">V.Wkts</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
        </div>"""

    @staticmethod
    def render_squad_header(data: SquadComparisonData) -> str:
        """
        Renders the Comparison Header with team metrics.
        """
        from config.shared.team_colors import TEAM_COLORS
        c1 = TEAM_COLORS.get(data.team_a, "#333")
        c2 = TEAM_COLORS.get(data.team_b, "#333")
        ma = data.metrics_a
        mb = data.metrics_b
        
        html = f"""
        <div style="font-family: 'Segoe UI', Roboto, sans-serif; margin-bottom:25px; border:1px solid #ddd; border-radius:8px; overflow:hidden; box-shadow:0 4px 6px rgba(0,0,0,0.05);">
            <div style="background: linear-gradient(135deg, {c1} 0%, {c2} 100%); padding:12px; color:white; text-align:center;">
                <h3 style="margin:0; font-size:18px;">⚔️ SQUAD COMPARISON</h3>
                <div style="font-size:12px; opacity:0.9;">{data.team_a.upper()} vs {data.team_b.upper()}</div>
            </div>
            <table style="width:100%; text-align:center; border-collapse:collapse; font-size:13px; background:white;">
                <tr style="background:#f8f9fa; color:#555; text-transform:uppercase; font-size:11px; border-bottom:1px solid #eee;">
                    <th style="padding:10px; text-align:left;">TEAM</th><th>CAPS</th><th style="background:#e9ecef;">AVG CAPS</th><th>RUNS</th><th>100s/50s</th><th>WKTS</th><th>5W</th>
                </tr>
                <tr style="border-bottom:1px solid #eee;">
                    <td style="padding:10px; text-align:left; font-weight:bold; color:{c1}; border-left: 4px solid {c1};">{data.team_a}</td>
                    <td style="font-weight:bold;">{ma.caps:,}</td>
                    <td style="background:#f8f9fa; color:#666;">{ma.avg_caps}</td>
                    <td>{ma.runs:,}</td><td>{ma.centuries}/{ma.fifties}</td><td>{ma.wickets}</td><td>{ma.five_wkt_hauls}</td>
                </tr>
                <tr>
                    <td style="padding:10px; text-align:left; font-weight:bold; color:{c2}; border-left: 4px solid {c2};">{data.team_b}</td>
                    <td style="font-weight:bold;">{mb.caps:,}</td>
                    <td style="background:#f8f9fa; color:#666;">{mb.avg_caps}</td>
                    <td>{mb.runs:,}</td><td>{mb.centuries}/{mb.fifties}</td><td>{mb.wickets}</td><td>{mb.five_wkt_hauls}</td>
                </tr>
            </table>
        </div>
        """
        return html

    @staticmethod
    def render_section_divider(title: str) -> str:
        return f"""<div style="background:#334155; color:#e2e8f0; padding:10px 15px; border-radius:6px; margin:20px 0 10px 0; border-left:5px solid #34d399; font-family:'Segoe UI', sans-serif;"><div style="font-weight:bold; font-size:14px;">{title}</div></div>"""

    @staticmethod
    def render_tactical_matrix(team_name: str, matrix_data: List[Dict], target_styles: List[str], team_color: str) -> str:
        """Renders the Tactical Matrix (Batter vs Bowling Style)."""
        if not matrix_data: return ""
        
        headers = "".join([f"<th style='padding:6px; background:#f4f4f4; color:#555; font-size:11px;'>{s.split(' ', 1)[1] if ' ' in s else s}</th>" for s in target_styles])
        
        rows_html = ""
        for r in matrix_data:
            cells = ""
            for style in target_styles:
                val = r.get(style, "-")
                cells += f"<td style='padding:6px; border-bottom:1px solid #eee; font-size:12px;'>{val}</td>"
            
            rows_html += f"<tr><td style='padding:6px; font-weight:bold; text-align:right; border-right:2px solid {team_color}; color:{team_color}; font-size:12px;'>{r['Player']}</td>{cells}</tr>"
        
        return f"""
        <div style="border:1px solid #ddd; border-radius:6px; overflow-x:auto; margin-bottom:20px; font-family:'Segoe UI', sans-serif;">
            <table style="width:100%; border-collapse:collapse; text-align:center;">
                <thead><tr><th style="padding:6px; text-align:right; background:{team_color}; color:white; font-size:11px;">{team_name.upper()} BATTER</th>{headers}</tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
            <div style="padding:4px; background:#fafafa; color:#777; font-size:9px; text-align:right;">
                <i>Stats vs All bowlers of this category in database</i>
            </div>
        </div>
        """

    @staticmethod
    def render_matchup_header(batter_name: str, team_color: str) -> str:
        """Small header for individual player matchups."""
        return f"<div style='font-weight:700; color:{team_color}; font-size:12px; margin-top:8px; font-family:sans-serif;'>{batter_name}</div>"

    @staticmethod
    def render_matchup_table(data: List[Dict]) -> str:
        """Renders a clean, high-aesthetic matchup table (Batter vs Bowlers)."""
        if not data: return ""
        
        rows = ""
        for row in data:
            name = row['Bowler']
            outs = row['Outs']
            
            # Color coding for threat
            color = "#555"; weight = "normal"
            if outs >= 3: color = "red"; weight = "bold"
            elif outs == 2: color = "orange"; weight = "bold"
            elif outs == 0: color = "green"; weight = "bold"
            
            rows += f"""
            <tr style="border-bottom:1px solid #eee; font-size:11px;">
                <td style="text-align:left; padding:4px; color:{color}; font-weight:{weight};">{name}</td>
                <td style="padding:4px;">{row['Runs']}</td>
                <td style="padding:4px;">{row['Balls']}</td>
                <td style="padding:4px; font-weight:bold;">{row['Outs']}</td>
                <td style="padding:4px;">{row['Avg']}</td>
                <td style="padding:4px;">{row['SR']}</td>
            </tr>
            """
            
        return f"""
        <table style="width:100%; border-collapse:collapse; text-align:center; font-family:sans-serif; margin-bottom:10px;">
            <thead>
                <tr style="border-bottom:2px solid #ddd; font-size:10px; color:#777; text-transform:uppercase;">
                    <th style="text-align:left; padding:4px;">Bowler</th>
                    <th>R</th><th>B</th><th>O</th><th>Avg</th><th>SR</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        """
    @staticmethod
    def render_mini_card(title: str, bat: Optional[BattingStats], bowl: Optional[BowlingStats], label: str) -> str:
        """Renders a high-density mini-card for context-specific stats (Venue/Opponent)."""
        html = f"""
        <div style="background:#f8f9fa; border:1px solid #ddd; padding:10px; border-radius:6px; min-width:200px; font-family:'Segoe UI', sans-serif;">
            <div style="font-size:11px; font-weight:bold; color:#555; margin-bottom:5px; text-transform:uppercase;">{title}</div>
            <div style="font-size:12px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                    <span>Avg / SR</span>
                    <span style="font-weight:bold;">{bat.average if bat else '-'} / {bat.strike_rate if bat else '-'}</span>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <span>Inns / Runs</span>
                    <span>{bat.innings if bat else 0} / {bat.runs if bat else 0}</span>
                </div>
            </div>
        </div>
        """
        return html
