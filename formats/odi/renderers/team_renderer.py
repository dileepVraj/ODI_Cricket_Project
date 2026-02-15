from typing import List, Dict, Optional
import pandas as pd
from config.shared.team_colors import TEAM_COLORS

class TeamHTMLRenderer:
    """
    Handles all HTML generation for Team Analytics.
    Decoupled from Engine logic (Headless Architecture).
    """

    @staticmethod
    def render_dashboard(data: List[Dict], t1: str, t2: str, title: str) -> str:
        """Renders the modern HTML Grid Dashboard for team statistics."""
        # Parse Data into a List of Values
        d = [x['Value'] for x in data] 
        
        c1 = TEAM_COLORS.get(t1, TEAM_COLORS.get('Visitors', '#333'))
        c2 = TEAM_COLORS.get(t2, TEAM_COLORS.get('Visitors', '#333'))

        # UI Colors from Source of Truth
        white = TEAM_COLORS.get('white')
        light_grey = TEAM_COLORS.get('light_grey')
        bg_grey = TEAM_COLORS.get('grey_bg')
        border_grey = TEAM_COLORS.get('border_light')

        html = f"""
        <style>
            .team-dashboard-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-family: 'Segoe UI', sans-serif; margin-bottom: 20px; }}
            .team-card {{ background: {light_grey}; border: 1px solid {border_grey}; border-radius: 8px; padding: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
            .team-stat-row {{ display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 5px; border-bottom: 1px dashed #eee; }}
            .team-stat-val {{ font-weight: bold; color: #333; }}
            .team-section-title {{ font-size: 11px; font-weight: bold; color: #666; margin-top: 10px; margin-bottom: 5px; text-transform: uppercase; border-bottom: 1px solid #ccc; }}
            .team-win-stats {{ display: flex; justify-content: space-between; background: {bg_grey}; padding: 5px; border-radius: 4px; font-size: 12px; margin-bottom: 10px; }}
        </style>

        <h3 style="margin:0 0 10px 0; font-family: sans-serif;">📊 {title}</h3>

        <div class="team-dashboard-grid">
            <div class="team-card" style="grid-column: span 2; display:flex; justify-content:space-around; text-align:center;">
                <div><div style="font-size:20px; font-weight:bold;">{d[0]}</div><div style="font-size:10px; color:#666;">MATCHES</div></div>
                <div><div style="font-size:20px; font-weight:bold; color:{c1}">{d[2]}</div><div style="font-size:10px; color:#666;">{t1} WIN %</div></div>
                <div><div style="font-size:20px; font-weight:bold;">{d[1]}</div><div style="font-size:10px; color:#666;">TIE/NR</div></div>
            </div>

            <div class="team-card" style="border-top: 3px solid {c1}">
                <div style="font-weight:bold; color:{c1}; font-size:16px; margin-bottom:5px;">{t1.upper()}</div>
                
                <div class="team-win-stats">
                    <span>🏆 <b>{d[4]}</b> Wins</span>
                    <span>🛡️ <b>{d[5]}</b> Def</span>
                    <span>🎯 <b>{d[6]}</b> Chs</span>
                </div>

                <div class="team-section-title">Batting 1st</div>
                <div class="team-stat-row"><span>Avg Score:</span> <span class="team-stat-val">{d[16]}</span></div>
                <div class="team-stat-row"><span>High / Low:</span> <span class="team-stat-val">{d[17]} / {d[18]}</span></div>
                <div class="team-stat-row"><span>Avg Win Score:</span> <span class="team-stat-val">{d[19]}</span></div>
                <div class="team-stat-row"><span>Lowest Defended:</span> <span class="team-stat-val">{d[20]}</span></div>

                <div class="team-section-title">Chasing</div>
                <div class="team-stat-row"><span>Avg Score:</span> <span class="team-stat-val">{d[28]}</span></div>
                <div class="team-stat-row"><span>Highest Chased:</span> <span class="team-stat-val">{d[29]}</span></div>
                <div class="team-stat-row"><span>Avg Succ. Chase:</span> <span class="team-stat-val">{d[30]}</span></div>
                <div class="team-stat-row"><span>Avg Fail Chase:</span> <span class="team-stat-val">{d[31]}</span></div>
            </div>

            <div class="team-card" style="border-top: 3px solid {c2}">
                <div style="font-weight:bold; color:{c2}; font-size:16px; margin-bottom:5px;">{t2.upper()}</div>
                
                <div class="team-win-stats">
                    <span>🏆 <b>{d[8]}</b> Wins</span>
                    <span>🛡️ <b>{d[9]}</b> Def</span>
                    <span>🎯 <b>{d[10]}</b> Chs</span>
                </div>

                <div class="team-section-title">Batting 1st</div>
                <div class="team-stat-row"><span>Avg Score:</span> <span class="team-stat-val">{d[22]}</span></div>
                <div class="team-stat-row"><span>High / Low:</span> <span class="team-stat-val">{d[23]} / {d[24]}</span></div>
                <div class="team-stat-row"><span>Avg Win Score:</span> <span class="team-stat-val">{d[25]}</span></div>
                <div class="team-stat-row"><span>Lowest Defended:</span> <span class="team-stat-val">{d[26]}</span></div>

                <div class="team-section-title">Chasing</div>
                <div class="team-stat-row"><span>Avg Score:</span> <span class="team-stat-val">{d[33]}</span></div>
                <div class="team-stat-row"><span>Highest Chased:</span> <span class="team-stat-val">{d[34]}</span></div>
                <div class="team-stat-row"><span>Avg Succ. Chase:</span> <span class="team-stat-val">{d[35]}</span></div>
                <div class="team-stat-row"><span>Avg Fail Chase:</span> <span class="team-stat-val">{d[36]}</span></div>
            </div>
            
            <div class="team-card" style="grid-column: span 2; background:#eef2f5;">
                <div style="font-weight:bold; color:#444; margin-bottom:8px; text-align:center;">🏟️ VENUE AVERAGES</div>
                <div style="display:flex; justify-content:space-around;">
                     <div><span>1st Inn Avg:</span> <b>{d[12]}</b></div>
                     <div><span>2nd Inn Avg:</span> <b>{d[13]}</b></div>
                     <div><span>Avg Winning Score:</span> <b>{d[14]}</b></div>
                </div>
            </div>
        </div>
        """
        return html

    @staticmethod
    def render_audit(df: pd.DataFrame, title: str = "MATCH AUDIT") -> str:
        """Renders the match audit table."""
        if df.empty: return ""
        
        # Robust column check
        c1 = 'display_inn1' if 'display_inn1' in df.columns else 'score_inn1'
        c2 = 'display_inn2' if 'display_inn2' in df.columns else 'score_inn2'
        cols = [c for c in ['start_date', 'venue', 'winner', 'team_bat_1', c1, 'team_bat_2', c2, 'status'] if c in df.columns]
        
        audit_df = df[cols].sort_values('start_date', ascending=False).rename(columns={c1: '1st Inn', c2: '2nd Inn'})
        
        html_table = audit_df.to_html(index=False, classes='table table-striped table-hover table-sm', border=0)
        
        return f"""
        <div style="margin-top:20px;">
            <div style="font-weight:bold; font-size:14px; color:#444; margin-bottom:8px; font-family:sans-serif;">🕵️‍♂️ {title} (Recent First)</div>
            <div style="overflow-x: auto; width: 100%; font-size: 12px; border: 1px solid #eee; border-radius:4px;">
                {html_table}
            </div>
        </div>
        """

    @staticmethod
    def render_bias(data: List[Dict], verdict: str, venue: str, years: int, total: int) -> str:
        """Renders the toss bias report."""
        df = pd.DataFrame(data)
        table_html = df.to_html(index=False, header=False, classes='table', border=0)
        
        return f"""
        <div style="background:#fff; border:1px solid #ddd; border-radius:8px; padding:15px; margin-bottom:20px; font-family:'Segoe UI', sans-serif; box-shadow:0 2px 5px rgba(0,0,0,0.05);">
            <div style="font-size:14px; font-weight:bold; color:#222; margin-bottom:10px;">🪙 TOSS BIAS REPORT: {venue.upper()}</div>
            <div style="display:flex; justify-content:space-between; margin-bottom:15px; font-size:12px; color:#666;">
                <span>📅 Period: Last {years} Years</span>
                <span>🏟️ Matches: {total}</span>
                <span style="font-weight:bold; color:#000;">📊 Verdict: <span style="background:#ffc107; padding:2px 6px; border-radius:4px;">{verdict}</span></span>
            </div>
            <div style="font-size:13px;">
                {table_html}
            </div>
        </div>
        """

    @staticmethod
    def render_matrix(df: pd.DataFrame, title: str) -> str:
        """Renders matrix-style reports (Dominance/Away)."""
        table_html = df.to_html(index=False, classes='table', border=0)
        return f"""
        <div style="margin-bottom:25px; font-family:'Segoe UI', sans-serif;">
            <div style="background:#343a40; color:white; padding:10px; font-weight:bold; font-size:14px; border-radius:4px 4px 0 0;">📊 {title}</div>
            <div style="overflow-x:auto; border:1px solid #ddd; border-top:none;">
                {table_html}
            </div>
        </div>
        """

    @staticmethod
    def render_form(data: List[Dict], team_name: str, title: str) -> str:
        """Renders the recent form cards/table."""
        def get_res_color(val):
            if 'WIN' in val: return 'green'
            if 'LOSS' in val: return 'red'
            if 'TIE' in val: return 'orange'
            return 'gray'

        rows = ""
        for row in data:
            c = get_res_color(row['Result'])
            rows += f"""
            <tr style="border-bottom:1px solid #eee;">
                <td style="padding:8px;">{row['Date']}</td>
                <td style="padding:8px; font-weight:bold;">{row['Opponent']}</td>
                <td style="padding:8px;">{row['Venue']}</td>
                <td style="padding:8px; color:{c}; font-weight:bold;">{row['Result']}</td>
                <td style="padding:8px;">{row[team_name]}</td>
                <td style="padding:8px;">{row['Opp Score']}</td>
            </tr>
            """

        return f"""
        <div style="margin-bottom:20px; font-family:'Segoe UI', sans-serif;">
            <div style="font-weight:bold; font-size:15px; margin-bottom:10px; color:#333;">{title}</div>
            <table style="width:100%; border-collapse:collapse; font-size:13px; text-align:left; border:1px solid #ddd;">
                <thead style="background:#f8f9fa;">
                    <tr>
                        <th style="padding:8px;">Date</th><th style="padding:8px;">Opponent</th><th style="padding:8px;">Venue</th>
                        <th style="padding:8px;">Result</th><th style="padding:8px;">{team_name}</th><th style="padding:8px;">Opp Score</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """

    @staticmethod
    def render_phase_header(venue: str, count: int, years: int) -> str:
        """Renders a styled header for phase analysis."""
        return f"""
        <div style="background:#f4f4f4; padding:15px; border-radius:8px; margin-bottom:15px; border-left: 5px solid #666; font-family:'Segoe UI', sans-serif;">
            <h3 style="margin:0; color:#333;">🕒 PHASE ANALYSIS: {venue.upper()}</h3>
            <div style="font-size:12px; color:#666; margin-top:4px;">📅 Sample Size: {count} Innings (Last {years} Years)</div>
        </div>
        """

    @staticmethod
    def render_phase_table(summary_html: str, title: str, header_color: str, bg_color: str = "#fff") -> str:
        """Wraps phase aggregation into a styled container."""
        return f"""
        <div style="margin-bottom:20px; border:1px solid #ddd; border-radius:6px; background:{bg_color}; font-family:'Segoe UI', sans-serif; overflow:hidden;">
            <div style="background:{header_color}; color:#fff; padding:8px 12px; font-weight:bold; font-size:13px;">{title}</div>
            <div style="overflow-x:auto;">
                {summary_html}
            </div>
        </div>
        """

    @staticmethod
    def render_phase_analysis(data: Dict) -> str:
        """Renders the headless phase analysis report."""
        if not data: return "<div style='color:red;'>⚠️ No Phase Data Available.</div>"
        
        venue = data.get('stadium_id', 'Unknown Venue')
        count = data.get('match_count', 0)
        years = data.get('years', 5)
        
        html = TeamHTMLRenderer.render_phase_header(venue, count, years)
        
        # 1. Baseline
        baseline = data.get('baseline')
        if baseline:
            def build_table(stats):
                rows = ""
                for phase, label in [('pp', 'POWERPLAY (1-10)'), ('mid', 'MIDDLE (11-40)'), ('dth', 'DEATH (41-50)')]:
                    row_inn1 = f"<b>{stats[1][phase]['avg']:.1f}</b> / <span style='color:#d9534f'>{stats[1][phase]['wkts']:.1f} w</span>"
                    row_inn2 = f"<b>{stats[2][phase]['avg']:.1f}</b> / <span style='color:#d9534f'>{stats[2][phase]['wkts']:.1f} w</span>"
                    rows += f"<tr style='border-bottom:1px solid #eee;'><td style='padding:8px;'>{label}</td><td style='padding:8px;'>{row_inn1}</td><td style='padding:8px;'>{row_inn2}</td></tr>"
                
                return f"""
                <table style="width:100%; border-collapse:collapse; font-size:13px;">
                    <tr style="background:#f8f9fa; text-align:left;">
                        <th style="padding:8px;">PHASE</th>
                        <th style="padding:8px;">1st INNINGS (Avg/Wkts)</th>
                        <th style="padding:8px;">2nd INNINGS (Avg/Wkts)</th>
                    </tr>
                    {rows}
                </table>
                """
            
            html += TeamHTMLRenderer.render_phase_table(build_table(baseline), "🏟️ OVERALL VENUE BASELINE", TEAM_COLORS['grey_text'], TEAM_COLORS['light_grey'])
            
        # 2. Home/Away Context
        for ctx_key, label, color in [('home_at_venue', 'HOME TEAM AT VENUE', TEAM_COLORS['Visitors']), ('away_at_venue', 'AWAY TEAM AT VENUE', TEAM_COLORS['dark_orange'])]:
            ctx = data.get(ctx_key)
            if ctx and ctx.get('stats'):
                title = f"{label}: {ctx['team'].upper()}"
                html += TeamHTMLRenderer.render_phase_table(build_table(ctx['stats']), title, color, "#fff")
        
        # 3. Global Habits
        habits = data.get('global_habits')
        if habits:
            html += f"<h4 style='margin-top:20px; border-bottom:2px solid #ddd; padding-bottom:5px;'>🧪 GLOBAL HABITS (Since {habits.get('start_year')})</h4>"
            # Simpler representation for global RR
            h = habits['home']
            a = habits['away']
            html += f"""
            <div style="display:flex; gap:10px; font-size:12px; font-family:sans-serif;">
                <div style="flex:1; background:#e9ecef; padding:10px; border-radius:4px;">
                    <b>Home Team:</b> RR {h['pp_rr']} (PP) | {h['mid_rr']} (Mid) | {h['dth_rr']} (Dth)
                </div>
                <div style="flex:1; background:#fff3cd; padding:10px; border-radius:4px;">
                    <b>Away Team:</b> RR {a['pp_rr']} (PP) | {a['mid_rr']} (Mid) | {a['dth_rr']} (Dth)
                </div>
            </div>
            """
            
        return html

    @staticmethod
    def render_alert(text: str, type: str = "edge") -> str:
        """Renders strategic alerts (Edge/Risk)."""
        if type == "edge":
            style = f"background:{TEAM_COLORS.get('green_bg')}; color:{TEAM_COLORS.get('dark_green')}; border-left:4px solid {TEAM_COLORS.get('green')};"
        else:
            style = f"background:{TEAM_COLORS.get('red_bg')}; color:{TEAM_COLORS.get('dark_red')}; border-left:4px solid {TEAM_COLORS.get('red')};"
        label = "🚀 EDGE:" if type == "edge" else "⚠️ RISK:"
        return f"""
        <div style="margin-top:8px; padding:10px; border-radius:4px; font-size:13px; font-family:sans-serif; {style}">
            <b>{label}</b> {text}
        </div>
        """
    @staticmethod
    def render_prediction(data: Dict) -> str:
        """
        Renders the Project Score Prediction card.
        Decoupled from PredictorEngine logic.
        """
        t1 = data['batting_team']
        t2 = data['bowling_team']
        c1 = TEAM_COLORS.get(t1, "#333")
        
        venue_avg = data['venue_avg']
        bat_factor = data['bat_factor']
        bowl_factor = data['bowl_factor']
        bf_text = data['bf_text']
        
        # 🎨 DERIVE COLORS (Interface logic)
        if bf_text == "STRONG ATTACK": bf_color = 'green'
        elif bf_text == "WEAK ATTACK": bf_color = 'red'
        else: bf_color = TEAM_COLORS.get(t2, 'grey')

        lower = data['lower']
        upper = data['upper']
        venue_msg = data['venue_msg']
        adjustment_msg = data['adjustment_msg']

        html = f"""
        <div style="background:#fff; border:1px solid #ddd; border-top: 4px solid {c1}; border-radius:6px; margin-bottom:20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); font-family: 'Segoe UI', sans-serif;">
            <div style="padding:10px; background:#f8f9fa; border-bottom:1px solid #eee; display:flex; justify-content:space-between; align-items:center;">
                <div style="font-weight:bold; color:#333;">🔮 PROJECTED SCORE: {t1.upper()}</div>
                <div style="font-size:11px; color:#777;">{venue_msg}</div>
            </div>
            
            <div style="padding:15px; display:flex; justify-content:space-between; align-items:center;">
                <div style="text-align:center;">
                    <div style="font-size:12px; color:#555;">VENUE PAR</div>
                    <div style="font-size:20px; font-weight:bold; color:#333;">{venue_avg}</div>
                </div>
                <div style="text-align:center; color:#ccc;">✖️</div>
                <div style="text-align:center;">
                    <div style="font-size:12px; color:#555;">BAT STRENGTH</div>
                    <div style="font-size:18px; font-weight:bold; color:{'green' if bat_factor>=1 else 'red'}">{bat_factor:.2f}x</div>
                </div>
                <div style="text-align:center; color:#ccc;">✖️</div>
                <div style="text-align:center;">
                    <div style="font-size:12px; color:#555;">BOWL IMPACT</div>
                    <div style="font-size:18px; font-weight:bold; color:{bf_color}">{bowl_factor:.2f}x</div>
                    <div style="font-size:9px; color:{bf_color}">{bf_text}</div>
                </div>
                <div style="text-align:center; color:#ccc;">=</div>
                <div style="text-align:center; background:{c1}; color:white; padding:10px 20px; border-radius:6px;">
                    <div style="font-size:12px; opacity:0.9;">PREDICTED RANGE</div>
                    <div style="font-size:24px; font-weight:bold;">{lower} - {upper}</div>
                </div>
            </div>
            
            <div style="padding:10px; background:#fffbe6; font-size:11px; color:#856404; border-top:1px solid #ffeeba;">
                <b>🤖 Model Notes:</b> {', '.join(adjustment_msg) if adjustment_msg else 'Standard conditions detected.'}
            </div>
        </div>
        """
        return html
