"""Match pack assembly helpers."""
from __future__ import annotations

import contextlib
import io
import sys
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, TypeAlias

import pandas as pd
from core.match_pack.interpreters import MatchInterpreter
from core.match_pack.transformers.h2h_transformer import transform_h2h_report, transform_h2h_slim
from core.match_pack.transformers.player_transformer import transform_player_stats, transform_squad_comparison
from core.match_pack.transformers.team_transformer import transform_dominance_matrix, transform_team_form
from core.match_pack.transformers.venue_transformer import transform_venue_bias
from formats.odi.config.players import BOWLER_STYLES, PLAYER_ROLES
from formats.odi.config.rankings import ODI_RANKINGS
from formats.odi.match_pack._formatter import MatchPackFormatter

JsonValue: TypeAlias = str | int | float | bool | None | dict[str, "JsonValue"] | list["JsonValue"]


class MatchPackAssembler:
    """Owns match-pack assembly and recursive cleanup of internal keys."""

    def __init__(self, bot: Any) -> None:
        self.bot = bot
        self.narrator = MatchPackFormatter()
        self.interpreter = MatchInterpreter(
            rankings=ODI_RANKINGS,
            bowler_styles=BOWLER_STYLES,
            player_roles=PLAYER_ROLES,
            format_key='odi',
        )

    def generate_pack(self, home, away, venue, home_xi, away_xi, context, persist=False):
        with contextlib.redirect_stdout(io.StringIO()):
            ch1 = self._build_chapter_1(home, away, venue)
            ch2 = self._build_chapter_2(home, away, venue, context)
            ch3 = self._build_chapter_3(home, away, venue, home_xi, away_xi, context, ch2)
            ch4 = self._build_chapter_4(home, away, venue, home_xi, away_xi, context)
            all_chapters = {'Chapter_1_Macro_Context': ch1, 'Chapter_2_Battlefield': ch2, 'Chapter_3_Tactical_Engine': ch3, 'Chapter_4_Player_Intelligence': ch4}
            executive = self.interpreter.generate_executive_summary(all_chapters, home, away, context)
        match_pack = {'meta': {'report_type': 'ODI_Match_Pack', 'version': '3.2', 'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'home_team': home, 'away_team': away, 'venue': venue, 'home_xi': home_xi, 'away_xi': away_xi, 'match_context': context}, 'Executive_Summary': executive, **all_chapters}
        return match_pack

    def _build_chapter_1(self, home: str, away: str, venue: str) -> Dict[str, Any]:
        """Builds Chapter 1: Macro Context."""
        chapter: Dict[str, Any] = {'chapter_description': 'High-level rivalry and momentum analysis. Covers head-to-head records, recent form for both teams, and home/away performance matrices.'}
        print('   1.1 Global H2H (4Y)...')
        raw_h2h_4y = self._silent_call(self.bot.analyze_global_h2h, home, away, 4)
        if raw_h2h_4y:
            data = transform_h2h_slim(raw_h2h_4y, home, away)
            chapter['global_h2h_4y'] = self.interpreter.interpret_h2h(data, home, away, 'Last 4 Years')
        print('   1.1b Global H2H (8Y Secondary)...')
        raw_h2h_8y = self._silent_call(self.bot.analyze_global_h2h, home, away, 8)
        if raw_h2h_8y:
            data = transform_h2h_slim(raw_h2h_8y, home, away)
            chapter['global_h2h_8y'] = self.interpreter.interpret_h2h(data, home, away, 'Last 8 Years')
        print('   1.2 Home Team Form...')
        home_form: Dict[str, Any] = {}
        raw_home_global = self._silent_call(self.bot.check_recent_form, home, 'All', 'All', 10)
        if raw_home_global:
            data = transform_team_form(raw_home_global, home)
            home_form['global'] = self.interpreter.interpret_form(data, 'Global')
        raw_home_vs = self._silent_call(self.bot.check_recent_form, home, away, 'All', 10)
        if raw_home_vs:
            data = transform_team_form(raw_home_vs, home)
            home_form['vs_opponent'] = self.interpreter.interpret_form(data, f'vs {away}')
        chapter['home_form'] = home_form
        print('   1.2b Away Team Form...')
        away_form: Dict[str, Any] = {}
        raw_away_global = self._silent_call(self.bot.check_recent_form, away, 'All', 'All', 10)
        if raw_away_global:
            data = transform_team_form(raw_away_global, away)
            away_form['global'] = self.interpreter.interpret_form(data, 'Global')
        raw_away_vs = self._silent_call(self.bot.check_recent_form, away, home, 'All', 10)
        if raw_away_vs:
            data = transform_team_form(raw_away_vs, away)
            away_form['vs_opponent'] = self.interpreter.interpret_form(data, f'vs {home}')
        chapter['away_form'] = away_form
        print('   1.3 Country H2H (8Y)...')
        from config.shared.venues import get_country_from_venue_id, resolve_venue_id

        host_country = get_country_from_venue_id(resolve_venue_id(venue) or venue)
        raw_country = None
        if host_country:
            raw_country = self._silent_call(self.bot.analyze_country_h2h, home, away, host_country, 8)
        if raw_country and isinstance(raw_country, dict):
            summary = raw_country.get('summary', {})
            home_stats = raw_country.get('team_a', {}).get('stats', {})
            away_stats = raw_country.get('team_b', {}).get('stats', {})
            data = {'matches_played': summary.get('matches', 0), 'home_wins': home_stats.get('wins', 0), 'away_wins': away_stats.get('wins', 0), 'no_result': summary.get('tie_nr', 0), 'home_win_pct': summary.get('win_pct', 0), 'home_won_batting_first': home_stats.get('defended', 0), 'home_won_chasing': home_stats.get('chased', 0), 'away_won_batting_first': away_stats.get('defended', 0), 'away_won_chasing': away_stats.get('chased', 0)}
            chapter['country_h2h'] = self.interpreter.interpret_h2h(data, home, away, f'In {host_country}, 8Y')
        print('   1.4 Home Dominance (4Y)...')
        raw_dom = self._silent_call(self.bot.analyze_home_dominance, home, 4)
        if raw_dom:
            data = transform_dominance_matrix(raw_dom, home)
            chapter['home_dominance'] = self.interpreter.interpret_dominance(data, home, 'HOME')
        print('   1.5 Away Performance (4Y)...')
        raw_away = self._silent_call(self.bot.analyze_away_performance, away, 4)
        if raw_away:
            data = transform_dominance_matrix(raw_away, away)
            chapter['away_performance'] = self.interpreter.interpret_dominance(data, away, 'AWAY')
        return chapter

    def _build_chapter_2(self, home: str, away: str, venue: str, context: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
        """Builds Chapter 2: Battlefield."""
        chapter: Dict[str, Any] = {'chapter_description': 'Venue-specific intelligence. Analyses whether the ground is a fortress for the home team, the head-to-head record at this specific venue, and historical toss impact.'}
        print('   2.1 Fortress Check (10Y)...')
        raw_fortress = self._silent_call(self.bot.analyze_home_fortress, venue, home, 'All', 10)
        if raw_fortress:
            data = transform_h2h_report(raw_fortress, home, 'All Opponents')
            chapter['fortress_check'] = self.interpreter.interpret_fortress(data, home)
        print('   2.2 Venue Matchup (15Y)...')
        raw_matchup = self._silent_call(self.bot.analyze_venue_matchup, venue, home, away, 15)
        if raw_matchup:
            data = transform_h2h_report(raw_matchup, home, away)
            chapter['venue_h2h'] = self.interpreter.interpret_h2h(data, home, away, 'At This Venue, 15Y')
        print('   2.3 Toss Bias (7Y)...')
        raw_bias = self._silent_call(self.bot.analyze_venue_bias, venue, 7)
        if raw_bias:
            data = transform_venue_bias(raw_bias)
            chapter['toss_bias'] = self.interpreter.interpret_toss_bias(data, match_context=context)
        print('   2.4 Battlefield Timeline...')
        raw_recent = self._silent_call(self.bot.analyze_venue_bias, venue, 3)
        if raw_recent and raw_bias:
            recent_data = transform_venue_bias(raw_recent)
            all_time_data = transform_venue_bias(raw_bias)
            trend_pct = recent_data.get('bat_first_win_pct', 0) - all_time_data.get('bat_first_win_pct', 0)
            chapter['battlefield_timeline'] = {'section_description': 'Historical scoring and win-percentage trends at this venue.', 'data': {'recent_3y_bat_first_win_pct': recent_data.get('bat_first_win_pct', 0), 'all_time_bat_first_win_pct': all_time_data.get('bat_first_win_pct', 0), 'trend': 'INCREASING_BAT_FIRST' if trend_pct > 10 else 'INCREASING_CHASE' if trend_pct < -10 else 'STABLE'}, 'narrative': f'Recent 3-year trend shows a {abs(trend_pct)}% {('increase' if trend_pct > 0 else 'decrease')} in Batting First success compared to the long-term average.'}
        return chapter

    def _build_chapter_3(self, home: str, away: str, venue: str, home_xi: List[str], away_xi: List[str], context: Dict[str, Any], ch2_data: Dict[str, Any]) -> Dict[str, Any]:
        """Builds Chapter 3: Tactical Engine."""
        chapter: Dict[str, Any] = {'chapter_description': 'Phase-by-phase scoring patterns at this venue and globally. Identifies powerplay, middle-overs, and death-overs tendencies for both teams, plus condition adjustments from pitch/time/toss inputs.'}
        print('   3.1 Phase Analysis (4Y)...')
        raw_phases = self._silent_call(self.bot.analyze_venue_phases, venue, home, away, 4)
        if raw_phases and isinstance(raw_phases, dict):
            clean_phases: Dict[str, Any] = {}
            caveat: str = ''
            for key, value in raw_phases.items():
                if key == 'MATCH_IDS':
                    continue
                elif key == 'caveat_2nd_innings_death':
                    caveat = value
                else:
                    clean_phases[key] = value
            section_desc = "Scoring and wicket-loss patterns across Powerplay (overs 1-10), Middle Overs (11-40), and Death Overs (41-50) for both teams. venue_baseline = all teams at this venue; home_at_venue/away_at_venue = team-specific at venue; global_habits = team's overall patterns across all venues."
            if caveat:
                section_desc += f' CAVEAT: {caveat}'
            chapter['phase_analysis'] = {'section_description': section_desc, 'data': clean_phases, 'context': {'alerts': clean_phases.get('alerts', [])}, 'narrative': self.narrator._build_phase_narrative(clean_phases, home, away)}
        print('   3.2 Condition Analysis...')
        bias_data = None
        if ch2_data and 'toss_bias' in ch2_data:
            bias_data = ch2_data['toss_bias'].get('data', {})
        conditions = self.interpreter.interpret_conditions(context.get('pitch', ''), context.get('time', ''), context.get('toss', ''), bias_data)
        chapter['condition_weights'] = conditions
        return chapter

    def _build_chapter_4(self, home: str, away: str, venue: str, home_xi: List[str], away_xi: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Builds Chapter 4: Player Intelligence."""
        chapter: Dict[str, Any] = {'chapter_description': 'Player-level analysis: squad aggregate comparison, tactical matrix (per-player stats), individual matchups, per-player batting/bowling form + venue metrics, and bowling roster composition vs pitch conditions.'}
        print('   4.1 Squad Comparison...')
        squad_context_df = pd.DataFrame()
        if hasattr(self.bot, 'dal') and self.bot.dal is not None:
            all_players = list(set(home_xi) | set(away_xi))
            squad_context_df = self.bot.dal.get_balls(players=all_players)
        raw_payload = self._silent_call(self.bot.player_engine._generate_comparison_payload, home, home_xi, away, away_xi, venue, 50, squad_context_df)
        transformed: Dict[str, Any] = {}
        if raw_payload:
            transformed = transform_squad_comparison(raw_payload)
            squad_data = transformed.get('squad_comparison', {})
            chapter['squad_comparison'] = {'section_description': f'Aggregate squad metrics comparing {home} and {away}. Shows combined experience (caps), run-scoring depth (total runs, centuries, fifties), and wicket-taking ability (total wickets, 5-wicket hauls).', 'data': squad_data, 'narrative': self.narrator._build_squad_narrative(squad_data, home, away)}
            matrix_data = transformed.get('tactical_matrix', {})
            chapter['tactical_matrix'] = {'section_description': "Per-player batting average vs each bowling type in the opposing squad. Format: 'Avg (StrikeRate)'. Low averages vs a bowling type indicate vulnerability. High averages with high strike rate indicate domination of that bowling type.", 'data': matrix_data, 'narrative': self.narrator._build_tactical_narrative(matrix_data, home, away)}
            matchup_data = transformed.get('matchups', {})
            chapter['matchups'] = {'section_description': 'Batter vs specific bowler head-to-head records. Shows runs scored, balls faced, dismissals, average, and strike rate. Bunny alerts flag batters dismissed 3+ times at avg <20 by a specific bowler.', 'data': matchup_data, 'narrative': self.narrator._build_matchup_narrative(matchup_data, home, away)}
            print('   4.2 Player Stats...')
            player_stats_raw = raw_payload.get('PlayerStats', {})
            if player_stats_raw:
                player_stats: Dict[str, Dict[str, Any]] = {}
                for team_name, team_stats in player_stats_raw.items():
                    player_stats[team_name] = {}
                    for player_name, stats_dict in team_stats.items():
                        player_stats[team_name][player_name] = transform_player_stats(stats_dict)
                chapter['player_stats'] = {'section_description': 'Per-player detailed statistics: batting form (last 10 match scores), career batting average, average vs this specific opponent, venue-specific batting record (innings, runs, avg, highest score), bowling form and economy, venue bowling economy and wickets. This is the most granular player-level data available for prediction.', 'data': player_stats, 'narrative': self.narrator._build_player_stats_narrative(player_stats, home, away)}
        print('   4.3 Bowling Roster...')
        player_stats_data = chapter.get('player_stats', {}).get('data', {})
        _ = chapter.get('matchups', {}).get('data', {})
        chapter['bowling_roster'] = self.interpreter.analyze_bowling_roster(home_xi, away_xi, context.get('pitch', ''), player_stats=player_stats_data)
        tactical_data = chapter.get('tactical_matrix', {}).get('data', {})
        if tactical_data:
            chapter['tactical_matrix']['narrative'] = self.narrator._build_role_based_tactical_narrative(tactical_data, home, away)
        return chapter

    def _silent_call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """
        Calls an engine function while suppressing its stdout/print output.
        The engine methods print HTML/tables for the UI  we only want the return value.

        This is the key to the "don't change the look and feel" constraint:
        engine methods still display normally when called from the UI buttons,
        but when called from the generator, their print output is captured and discarded.
        """
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f'   Engine call failed: {func.__name__}  {e}', file=sys.stderr)
                return None

    def _strip_internal_keys(self, payload: JsonValue) -> JsonValue:
        if isinstance(payload, dict):
            return {
                key: self._strip_internal_keys(value)
                for key, value in payload.items()
                if not key.startswith('_')
            }
        if isinstance(payload, list):
            return [self._strip_internal_keys(item) for item in payload]
        return payload
