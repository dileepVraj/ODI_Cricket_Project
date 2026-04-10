"""Match pack narrative helpers."""
from typing import Any, Dict, List

from formats.odi.config.players import BOWLER_STYLES, PLAYER_ROLES


class MatchPackFormatter:
    def _build_squad_narrative(self, squad_data: Dict[str, Any], home: str, away: str) -> str:
        if not squad_data:
            return 'No squad data available.'
        h = squad_data.get(home, {}); a = squad_data.get(away, {}); parts = []
        h_caps = h.get('Caps (Combined)', 0); a_caps = a.get('Caps (Combined)', 0)
        if h_caps > 0 and a_caps > 0:
            if abs(h_caps - a_caps) > 50:
                more_exp = home if h_caps > a_caps else away
                parts.append(f'{more_exp} have significantly more experience ({max(h_caps, a_caps)} vs {min(h_caps, a_caps)} combined caps).')
            else:
                parts.append(f'Both squads are similarly experienced ({h_caps} vs {a_caps} caps).')
        h_100s = h.get('100s', 0); a_100s = a.get('100s', 0)
        if h_100s > 0 or a_100s > 0:
            parts.append(f'{away if a_100s > h_100s else home} have more centurions ({max(h_100s, a_100s)} vs {min(h_100s, a_100s)} centuries).')
        h_wkts = h.get('Total Wickets', 0); a_wkts = a.get('Total Wickets', 0)
        if h_wkts > 0 or a_wkts > 0 and abs(h_wkts - a_wkts) > 30: parts.append(f'{home if h_wkts > a_wkts else away} have superior bowling depth ({max(h_wkts, a_wkts)} vs {min(h_wkts, a_wkts)} wickets).')
        return ' '.join(parts) if parts else 'Squads are broadly comparable on aggregate metrics.'

    def _build_tactical_narrative(self, matrix_data: Dict[str, Any], home: str, away: str) -> str:
        if not matrix_data:
            return 'No tactical matrix data available.'
        parts = []
        for team, players in matrix_data.items():
            if not isinstance(players, list):
                continue
            vulnerabilities: Dict[str, List[str]] = {}
            for row in players:
                if not isinstance(row, dict):
                    continue
                player = row.get('Player', '')
                for col, val in row.items():
                    if col == 'Player' or col.endswith('_raw'):
                        continue
                    raw_val = row.get(f'{col}_raw')
                    if raw_val is None:
                        continue
                    try:
                        avg = float(raw_val)
                    except (ValueError, TypeError):
                        continue
                    if 0 < avg < 15:
                        bowl_type = col.replace('Right-Arm ', '').replace('Left-Arm ', '').replace('Slow ', '').strip()
                        vulnerabilities.setdefault(bowl_type, []).append(f'{player} (avg {avg})')
            for bowl_type, vuln_players in vulnerabilities.items():
                if len(vuln_players) >= 2: parts.append(f"{team} batters are vulnerable to {bowl_type}: {', '.join(vuln_players[:3])}.")
        return ' '.join(parts) if parts else 'No clear tactical vulnerabilities identified from the bowling-type matrix.'

    def _build_matchup_narrative(self, matchup_data: Dict[str, Any], home: str, away: str) -> str:
        if not matchup_data:
            return 'No matchup data available.'
        bunnies = []
        dominations = []
        for team, players in matchup_data.items():
            if not isinstance(players, dict):
                continue
            for batter, bowler_list in players.items():
                if not isinstance(bowler_list, list):
                    continue
                for m in bowler_list:
                    if not isinstance(m, dict):
                        continue
                    bowler = m.get('Bowler', m.get('RawName', '')); outs = m.get('Outs', 0); avg = m.get('Avg', 0); runs = m.get('Runs', 0); sr = m.get('SR', 0)
                    if isinstance(outs, (int, float)) and outs >= 3 and isinstance(avg, (int, float)) and 0 < avg < 20:
                        bunnies.append(f'{batter} is a bunny of {bowler} ({outs} dismissals, avg {avg}).')
                    if isinstance(runs, (int, float)) and runs >= 50 and isinstance(sr, (int, float)) and sr > 100 and outs == 0:
                        dominations.append(f'{batter} dominates {bowler} ({runs} runs at SR {sr}, never out).')
        parts = []
        if bunnies: parts.append('KEY BUNNY ALERTS: ' + ' '.join(bunnies[:5]));
        if dominations: parts.append('DOMINATION MATCHUPS: ' + ' '.join(dominations[:3]))
        return ' '.join(parts) if parts else 'No extreme bunny alerts or domination matchups detected.'

    def _build_player_stats_narrative(self, player_stats: Dict[str, Any], home: str, away: str) -> str:
        if not player_stats:
            return 'No player stats available.'
        bat_standouts = []
        bowl_standouts = []
        venue_kings = []
        strugglers = []
        for team, players in player_stats.items():
            if not isinstance(players, dict):
                continue
            for p_name, stats in players.items():
                if not isinstance(stats, dict) or 'error' in stats:
                    continue
                bat = stats.get('batting', {}); bowl = stats.get('bowling', {})
                bat_avg = bat.get('average', 0); inns = bat.get('innings', 0)
                if isinstance(bat_avg, (int, float)) and bat_avg > 45 and inns >= 5:
                    bat_standouts.append(f'{p_name} ({team})')
                elif isinstance(bat_avg, (int, float)) and 0 < bat_avg < 18 and inns >= 5:
                    strugglers.append(f'{p_name} ({team})')
                v_avg = bat.get('venue', {}).get('average', 0); v_inns = bat.get('venue', {}).get('innings', 0)
                if isinstance(v_avg, (int, float)) and v_avg > 40 and v_inns >= 3:
                    venue_kings.append(f'{p_name} ({v_avg} Avg)')
                b_wickets = bowl.get('career', {}).get('bowling', {}).get('wickets', 0); b_econ = bowl.get('career', {}).get('bowling', {}).get('economy', 10)
                if b_wickets > 20 and b_econ < 5.2:
                    bowl_standouts.append(f'{p_name} ({b_econ} Econ)')
        parts = []
        if bat_standouts: parts.append(f"IN-FORM BATTERS: {', '.join(bat_standouts[:3])} are in elite touch (Avg 45+).")
        if bowl_standouts: parts.append(f"BOWLING THREATS: {', '.join(bowl_standouts[:3])} maintain elite economy rates.")
        if venue_kings: parts.append(f"VENUE SPECIALISTS: {', '.join(venue_kings[:3])} have historically dominated these conditions.")
        if strugglers: parts.append(f"UNDER PRESSURE: {', '.join(strugglers[:3])} are searching for form (Avg < 18).")
        return ' '.join(parts) if parts else 'No significant player-level trends identified.'

    def _build_role_based_tactical_narrative(self, tactical_data: Dict[str, Any], home: str, away: str) -> str:
        narrative_parts = []
        for team_name in [home, away]:
            team_rows = tactical_data.get(team_name, [])
            if not team_rows:
                continue
            strugglers = []
            for row in team_rows:
                player = row.get('Player'); role = row.get('Role', '')
                raw_scores = {k.replace('_raw', ''): v for k, v in row.items() if k.endswith('_raw') and isinstance(v, (int, float))}
                if raw_scores:
                    worst_style = min(raw_scores, key=lambda style: raw_scores[style])
                    if raw_scores[worst_style] < 22:
                        strugglers.append(f'{player} ({role}) vs {worst_style}')
            if strugglers: narrative_parts.append(f"TACTICAL WEAKNESS ({team_name}): {', '.join(strugglers[:2])} represent key target areas for opposition bowlers.")
        return ' '.join(narrative_parts) if narrative_parts else 'Both lineups appear tactically balanced against opposition bowling styles.'

    def _build_smart_pitch_narrative(self, roster_data: Dict[str, Any], player_stats: Dict[str, Any], home: str, away: str, pitch_cond: str) -> str:
        pitch_lower = pitch_cond.lower()
        is_spin_pitch = any(kw in pitch_lower for kw in ['dry', 'turn', 'dust', 'spin', 'cracks'])
        is_pace_pitch = any(kw in pitch_lower for kw in ['green', 'seam', 'pace', 'moisture', 'grass'])
        if not is_spin_pitch and not is_pace_pitch:
            return ''
        parts = []; target_type = 'spin' if is_spin_pitch else 'pace'; home_venue_wkts = away_venue_wkts = 0.0
        home_bowlers_with_venue_data = []; away_bowlers_with_venue_data = []
        for team, players in player_stats.items():
            if not isinstance(players, dict):
                continue
            for player_name, stats in players.items():
                if not isinstance(stats, dict) or 'error' in stats:
                    continue
                style = BOWLER_STYLES.get(player_name, '')
                if not style or style == 'Part-Timer':
                    continue
                is_spin = any(kw in str(style).lower() for kw in ['spin', 'orth', 'unorth'])
                is_pace = any(kw in str(style).lower() for kw in ['fast', 'med'])
                if target_type == 'spin' and is_spin or (target_type == 'pace' and is_pace):
                    bowling = stats.get('bowling', {})
                    v_wkts = bowling.get('venue_wickets', 0); v_matches = bowling.get('venue_matches', 0); v_econ = bowling.get('venue_economy', 0)
                    if isinstance(v_wkts, (int, float)) and v_wkts > 0:
                        entry = f'{player_name} ({v_wkts} wkts in {v_matches} matches, econ {v_econ})'
                        if team == home:
                            home_venue_wkts += v_wkts
                            home_bowlers_with_venue_data.append(entry)
                        else:
                            away_venue_wkts += v_wkts
                            away_bowlers_with_venue_data.append(entry)
        parts.append(f'On this {"spin-friendly" if is_spin_pitch else "seam-friendly"} surface:')
        if home_bowlers_with_venue_data or away_bowlers_with_venue_data:
            if home_venue_wkts > away_venue_wkts:
                parts.append(f"{home} {target_type} bowlers have taken {home_venue_wkts} wickets at this venue vs {away}'s {away_venue_wkts}. ")
            elif away_venue_wkts > home_venue_wkts:
                parts.append(f"{away} {target_type} bowlers have taken {away_venue_wkts} wickets at this venue vs {home}'s {home_venue_wkts}. ")
            else:
                parts.append(f"Both teams' {target_type} bowlers have {home_venue_wkts} venue wickets each. ")
            if home_bowlers_with_venue_data: parts.append(f"{home} venue {target_type} bowlers: {'; '.join(home_bowlers_with_venue_data[:3])}.")
            if away_bowlers_with_venue_data: parts.append(f"{away} venue {target_type} bowlers: {'; '.join(away_bowlers_with_venue_data[:3])}.")
        else:
            suitability = roster_data.get('pitch_suitability', {})
            h_count = suitability.get(f'home_{target_type}_bowlers', 0) if target_type == 'spin' else suitability.get('home_pace_bowlers', 0)
            a_count = suitability.get(f'away_{target_type}_bowlers', 0) if target_type == 'spin' else suitability.get('away_pace_bowlers', 0)
            parts.append(f"No venue-specific wicket data available for {target_type} bowlers. By roster count: {home} has {h_count} vs {away}'s {a_count} {target_type} bowlers.")
        return ' '.join(parts)

    def _build_phase_narrative(self, phase_data: Dict[str, Any], home: str, away: str) -> str:
        baseline = phase_data.get('venue_baseline', {})
        home_venue = phase_data.get('home_at_venue', {})
        away_venue = phase_data.get('away_at_venue', {})
        global_hab = phase_data.get('global_habits', {})
        alerts = phase_data.get('alerts', [])
        parts = []
        pp_avg = baseline.get('pp_avg_1st', 0); dth_avg = baseline.get('dth_avg_1st', 0)
        if pp_avg and dth_avg:
            if dth_avg > pp_avg:
                parts.append(f'This venue rewards death-overs aggression (Death avg {dth_avg} vs PP avg {pp_avg} in 1st innings).')
            else:
                parts.append(f'Powerplay is key at this venue (PP avg {pp_avg} vs Death avg {dth_avg} in 1st innings).')
        if home_venue and away_venue:
            h_pp = home_venue.get('pp_avg_1st', 0); a_pp = away_venue.get('pp_avg_1st', 0)
            if h_pp > 0 and a_pp > 0 and abs(h_pp - a_pp) > 5: parts.append(f'{home if h_pp > a_pp else away} score more in the Powerplay at this venue ({max(h_pp, a_pp)} vs {min(h_pp, a_pp)}).')
        bat_first = global_hab.get('bat_first', {})
        if bat_first:
            h_dth = bat_first.get('home_team_dth_runs', 0); a_dth = bat_first.get('away_team_dth_runs', 0)
            if h_dth > 0 and a_dth > 0 and abs(h_dth - a_dth) > 5: parts.append(f'{home if h_dth > a_dth else away} score significantly more in death overs globally ({max(h_dth, a_dth)} vs {min(h_dth, a_dth)}).')
        if baseline.get('dth_avg_2nd', 0) > 0: parts.append('Note: 2nd innings death-over averages may be understated as many chases end before overs 41-50.')
        parts.extend(alerts)
        return ' '.join(parts) if parts else 'Phase analysis data available  see detailed breakdown.'
