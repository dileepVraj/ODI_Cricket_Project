"""
reports/match_pack_generator.py
The Orchestrator — chains engine calls through transformer and interpreter
to produce the final Match Pack JSON report.

Pipeline:
    Engine Call → Transformer (clean data) → Interpreter (add context + narrative) → JSON

Rules:
    - ZERO changes to engine display output (existing UI untouched)
    - Engine methods are called silently; they print to stdout but we only use their return values
    - Final JSON has NO HTML, NO emojis, NO [{Metric, Value}] flat lists
    - NO _match_ids in final output (internal diagnostic only)
"""
import json
import os
import io
import sys
from datetime import datetime

from core.transformer import (
    transform_h2h_report,
    transform_h2h_slim,
    transform_venue_bias,
    transform_team_form,
    transform_dominance_matrix,
    transform_squad_comparison,
    transform_player_stats,
)
from core.interpreter import MatchInterpreter
from config.teams import PLAYER_ROLES, BOWLER_STYLES


class MatchPackGenerator:
    """
    Orchestrates the Match Pack generation pipeline.

    Usage:
        generator = MatchPackGenerator(bot)
        filepath = generator.generate_pack("India", "England", "IND_MUMBAI_WANKHEDE",
                                           india_xi, england_xi, context)
    """

    def __init__(self, bot):
        """
        Args:
            bot: CricketAnalyzer instance (the Facade).
        """
        self.bot = bot
        self.interpreter = MatchInterpreter()

    def generate_pack(self, home, away, venue, home_xi, away_xi, context):
        """
        Generates the complete Match Pack JSON report.

        Args:
            home (str): Home team name.
            away (str): Away team name.
            venue (str): Venue ID or name.
            home_xi (list): Home team Playing XI.
            away_xi (list): Away team Playing XI.
            context (dict): Match context with keys: time, toss, pitch.

        Returns:
            str: Filepath to the generated JSON report.
        """
        print(f"📦 Match Pack Engine: {home} vs {away} at {venue}")
        print("=" * 60)

        # --- Build each chapter ---
        print("\n📘 Chapter 1: Macro Context...")
        ch1 = self._build_chapter_1(home, away, venue)

        print("\n📗 Chapter 2: Battlefield...")
        ch2 = self._build_chapter_2(home, away, venue, context)

        print("\n📙 Chapter 3: Tactical Engine...")
        ch3 = self._build_chapter_3(home, away, venue, home_xi, away_xi, context, ch2)

        print("\n📕 Chapter 4: Player Intelligence...")
        ch4 = self._build_chapter_4(home, away, venue, home_xi, away_xi, context)

        # --- Assemble Full Report ---
        all_chapters = {
            "Chapter_1_Macro_Context": ch1,
            "Chapter_2_Battlefield": ch2,
            "Chapter_3_Tactical_Engine": ch3,
            "Chapter_4_Player_Intelligence": ch4,
        }

        # --- Executive Summary ---
        print("\n🧠 Executive Summary...")
        executive = self.interpreter.generate_executive_summary(
            all_chapters, home, away, context
        )

        # --- Final Assembly ---
        match_pack = {
            "meta": {
                "report_type": "ODI_Match_Pack",
                "version": "3.2",
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "home_team": home,
                "away_team": away,
                "venue": venue,
                "home_xi": home_xi,
                "away_xi": away_xi,
                "match_context": context,
            },
            "Executive_Summary": executive,
            **all_chapters,
        }

        # --- Strip ALL internal _match_ids from final output ---
        match_pack = self._strip_internal_keys(match_pack)

        # --- Write to file ---
        filepath = self._save_report(match_pack, home, away)
        print(f"\n✅ Match Pack generated: {filepath}")
        return filepath

    # =========================================================================
    # CHAPTER 1: MACRO CONTEXT (H2H, Form, Dominance)
    # =========================================================================

    def _build_chapter_1(self, home, away, venue):
        """Builds Chapter 1: Macro Context."""
        chapter = {
            "chapter_description": (
                "High-level rivalry and momentum analysis. Covers head-to-head records, "
                "recent form for both teams, and home/away performance matrices."
            ),
        }

        # --- 1.1 Global H2H (4Y primary, 8Y secondary) — SLIM (no averages) ---
        print("  ├── 1.1 Global H2H (4Y)...")
        raw_h2h_4y = self._silent_call(self.bot.analyze_global_h2h, home, away, 4)
        if raw_h2h_4y:
            data = transform_h2h_slim(raw_h2h_4y, home, away)
            chapter["global_h2h_4y"] = self.interpreter.interpret_h2h(data, home, away, "Last 4 Years")

        print("  ├── 1.1b Global H2H (8Y Secondary)...")
        raw_h2h_8y = self._silent_call(self.bot.analyze_global_h2h, home, away, 8)
        if raw_h2h_8y:
            data = transform_h2h_slim(raw_h2h_8y, home, away)
            chapter["global_h2h_8y"] = self.interpreter.interpret_h2h(data, home, away, "Last 8 Years")

        # --- 1.2 Recent Form ---
        print("  ├── 1.2 Home Team Form...")
        home_form = {}

        raw_home_global = self._silent_call(self.bot.check_recent_form, home, 'All', 'All', 10)
        if raw_home_global:
            data = transform_team_form(raw_home_global, home)
            home_form["global"] = self.interpreter.interpret_form(data, "Global")

        raw_home_vs = self._silent_call(self.bot.check_recent_form, home, away, 'All', 10)
        if raw_home_vs:
            data = transform_team_form(raw_home_vs, home)
            home_form["vs_opponent"] = self.interpreter.interpret_form(data, f"vs {away}")

        chapter["home_form"] = home_form

        print("  ├── 1.2b Away Team Form...")
        away_form = {}

        raw_away_global = self._silent_call(self.bot.check_recent_form, away, 'All', 'All', 10)
        if raw_away_global:
            data = transform_team_form(raw_away_global, away)
            away_form["global"] = self.interpreter.interpret_form(data, "Global")

        raw_away_vs = self._silent_call(self.bot.check_recent_form, away, home, 'All', 10)
        if raw_away_vs:
            data = transform_team_form(raw_away_vs, away)
            away_form["vs_opponent"] = self.interpreter.interpret_form(data, f"vs {home}")

        chapter["away_form"] = away_form

        # --- 1.3 Country H2H — SLIM ---
        print("  ├── 1.3 Country H2H (8Y)...")
        raw_country = self._silent_call(self.bot.analyze_country_h2h, home, away, home, 8)
        if raw_country:
            data = transform_h2h_slim(raw_country, home, away)
            chapter["country_h2h"] = self.interpreter.interpret_h2h(data, home, away, "In-Country, 8Y")

        # --- 1.4 Home Dominance ---
        print("  ├── 1.4 Home Dominance (4Y)...")
        raw_dom = self._silent_call(self.bot.analyze_home_dominance, home, 4)
        if raw_dom:
            data = transform_dominance_matrix(raw_dom, home)
            chapter["home_dominance"] = self.interpreter.interpret_dominance(data, home, "HOME")

        # --- 1.5 Away Performance ---
        print("  └── 1.5 Away Performance (4Y)...")
        raw_away = self._silent_call(self.bot.analyze_away_performance, away, 4)
        if raw_away:
            data = transform_dominance_matrix(raw_away, away)
            chapter["away_performance"] = self.interpreter.interpret_dominance(data, away, "AWAY")

        return chapter

    # =========================================================================
    # CHAPTER 2: BATTLEFIELD (Fortress, Venue Matchup, Toss Bias)
    # =========================================================================

    def _build_chapter_2(self, home, away, venue, context=None):
        """Builds Chapter 2: Battlefield."""
        chapter = {
            "chapter_description": (
                "Venue-specific intelligence. Analyses whether the ground is a fortress for the home team, "
                "the head-to-head record at this specific venue, and historical toss impact."
            ),
        }

        # --- 2.1 Fortress Check (10Y, home only) — FULL (with averages) ---
        print("  ├── 2.1 Fortress Check (10Y)...")
        raw_fortress = self._silent_call(self.bot.analyze_home_fortress, venue, home, 'All', 10)
        if raw_fortress:
            data = transform_h2h_report(raw_fortress, home, "All Opponents")
            chapter["fortress_check"] = self.interpreter.interpret_fortress(data, home)

        # --- 2.2 Venue Matchup (home vs away at venue, 15Y) — FULL (with averages) ---
        print("  ├── 2.2 Venue Matchup (15Y)...")
        raw_matchup = self._silent_call(self.bot.analyze_venue_matchup, venue, home, away, 15)
        if raw_matchup:
            data = transform_h2h_report(raw_matchup, home, away)
            chapter["venue_h2h"] = self.interpreter.interpret_h2h(data, home, away, "At This Venue, 15Y")

        # --- 2.3 Toss Bias (7Y) — with match context for alignment ---
        print("  └── 2.3 Toss Bias (7Y)...")
        raw_bias = self._silent_call(self.bot.analyze_venue_bias, venue, 7)
        if raw_bias:
            data = transform_venue_bias(raw_bias)
            chapter["toss_bias"] = self.interpreter.interpret_toss_bias(data, match_context=context)

        return chapter

    # =========================================================================
    # CHAPTER 3: TACTICAL ENGINE (Phases, Conditions)
    # =========================================================================

    def _build_chapter_3(self, home, away, venue, home_xi, away_xi, context, ch2_data):
        """Builds Chapter 3: Tactical Engine."""
        chapter = {
            "chapter_description": (
                "Phase-by-phase scoring patterns at this venue and globally. "
                "Identifies powerplay, middle-overs, and death-overs tendencies for both teams, "
                "plus condition adjustments from pitch/time/toss inputs."
            ),
        }

        # --- 3.1 Phase Analysis (4Y) ---
        print("  ├── 3.1 Phase Analysis (4Y)...")
        raw_phases = self._silent_call(self.bot.analyze_venue_phases, venue, home, away, 4)
        if raw_phases and isinstance(raw_phases, dict):
            # Phase data is already structured from the engine — clean it
            clean_phases = {}
            caveat = ""
            for key, value in raw_phases.items():
                # Skip internal keys
                if key == "MATCH_IDS":
                    continue
                elif key == "caveat_2nd_innings_death":
                    caveat = value
                else:
                    clean_phases[key] = value

            section_desc = (
                "Scoring and wicket-loss patterns across Powerplay (overs 1-10), "
                "Middle Overs (11-40), and Death Overs (41-50) for both teams. "
                "venue_baseline = all teams at this venue; home_at_venue/away_at_venue = team-specific at venue; "
                "global_habits = team's overall patterns across all venues."
            )
            if caveat:
                section_desc += f" CAVEAT: {caveat}"

            chapter["phase_analysis"] = {
                "section_description": section_desc,
                "data": clean_phases,
                "context": {
                    "alerts": clean_phases.get("alerts", []),
                },
                "narrative": self._build_phase_narrative(clean_phases, home, away),
            }

        # --- 3.2 Condition Weights ---
        print("  └── 3.2 Condition Analysis...")
        bias_data = None
        if ch2_data and "toss_bias" in ch2_data:
            bias_data = ch2_data["toss_bias"].get("data", {})

        conditions = self.interpreter.interpret_conditions(
            context.get("pitch", ""),
            context.get("time", ""),
            context.get("toss", ""),
            bias_data,
        )
        chapter["condition_weights"] = conditions

        return chapter

    # =========================================================================
    # CHAPTER 4: PLAYER INTELLIGENCE (Squads, Matrix, Matchups, Stats)
    # =========================================================================

    def _build_chapter_4(self, home, away, venue, home_xi, away_xi, context):
        """Builds Chapter 4: Player Intelligence."""
        chapter = {
            "chapter_description": (
                "Player-level analysis: squad aggregate comparison, tactical matrix (per-player stats), "
                "individual matchups, per-player batting/bowling form + venue metrics, "
                "and bowling roster composition vs pitch conditions."
            ),
        }

        # --- 4.1 Squad Comparison (50Y — wide window for player career data) ---
        print("  ├── 4.1 Squad Comparison...")
        raw_payload = self._silent_call(
            self.bot.player_engine._generate_comparison_payload,
            home, home_xi, away, away_xi, venue, 50
        )

        transformed = {}
        if raw_payload:
            transformed = transform_squad_comparison(raw_payload)

            # Squad Comparison — with narrative (FIX 3)
            squad_data = transformed.get("squad_comparison", {})
            chapter["squad_comparison"] = {
                "section_description": (
                    f"Aggregate squad metrics comparing {home} and {away}. "
                    "Shows combined experience (caps), run-scoring depth (total runs, centuries, fifties), "
                    "and wicket-taking ability (total wickets, 5-wicket hauls)."
                ),
                "data": squad_data,
                "narrative": self._build_squad_narrative(squad_data, home, away),
            }

            # Tactical Matrix — with narrative (FIX 3)
            matrix_data = transformed.get("tactical_matrix", {})
            chapter["tactical_matrix"] = {
                "section_description": (
                    "Per-player batting average vs each bowling type in the opposing squad. "
                    "Format: 'Avg (StrikeRate)'. Low averages vs a bowling type indicate vulnerability. "
                    "High averages with high strike rate indicate domination of that bowling type."
                ),
                "data": matrix_data,
                "narrative": self._build_tactical_narrative(matrix_data, home, away),
            }

            # Matchups — with narrative (FIX 3)
            matchup_data = transformed.get("matchups", {})
            chapter["matchups"] = {
                "section_description": (
                    "Batter vs specific bowler head-to-head records. "
                    "Shows runs scored, balls faced, dismissals, average, and strike rate. "
                    "Bunny alerts flag batters dismissed 3+ times at avg <20 by a specific bowler."
                ),
                "data": matchup_data,
                "narrative": self._build_matchup_narrative(matchup_data, home, away),
            }

            # --- 4.2 Player Stats (Batting/Bowling Form + Venue) (FIX 5) ---
            print("  ├── 4.2 Player Stats...")
            player_stats_raw = raw_payload.get("PlayerStats", {})
            if player_stats_raw:
                player_stats = {}
                for team_name, team_stats in player_stats_raw.items():
                    player_stats[team_name] = {}
                    for player_name, stats_dict in team_stats.items():
                        player_stats[team_name][player_name] = transform_player_stats(stats_dict)

                chapter["player_stats"] = {
                    "section_description": (
                        "Per-player detailed statistics: batting form (last 10 match scores), "
                        "career batting average, average vs this specific opponent, "
                        "venue-specific batting record (innings, runs, avg, highest score), "
                        "bowling form and economy, venue bowling economy and wickets. "
                        "This is the most granular player-level data available for prediction."
                    ),
                    "data": player_stats,
                    "narrative": self._build_player_stats_narrative(player_stats, home, away),
                }

        # --- 4.3 Bowling Roster Analysis (FIX 4 — smart narrative) ---
        print("  ├── 4.3 Bowling Roster...")
        player_stats_data = chapter.get("player_stats", {}).get("data", {})
        matchup_data_for_roster = chapter.get("matchups", {}).get("data", {})

        chapter["bowling_roster"] = self.interpreter.analyze_bowling_roster(
            home_xi, away_xi, context.get("pitch", "")
        )

        # FIX 4: Override the shallow narrative with a data-driven one
        pitch_cond = context.get("pitch", "")
        if player_stats_data and pitch_cond:
            smart_narrative = self._build_smart_pitch_narrative(
                chapter["bowling_roster"], player_stats_data, home, away, pitch_cond
            )
            if smart_narrative:
                chapter["bowling_roster"]["pitch_suitability"]["narrative"] = smart_narrative

        return chapter

    # =========================================================================
    # NARRATIVE BUILDERS (FIX 3 & FIX 4)
    # =========================================================================

    def _build_squad_narrative(self, squad_data, home, away):
        """Builds a concise narrative from squad comparison data."""
        if not squad_data:
            return "No squad data available."

        h = squad_data.get(home, {})
        a = squad_data.get(away, {})
        parts = []

        # Experience
        h_caps = h.get("Caps (Combined)", 0)
        a_caps = a.get("Caps (Combined)", 0)
        if h_caps > 0 and a_caps > 0:
            if abs(h_caps - a_caps) > 50:
                more_exp = home if h_caps > a_caps else away
                parts.append(f"{more_exp} have significantly more experience ({max(h_caps, a_caps)} vs {min(h_caps, a_caps)} combined caps).")
            else:
                parts.append(f"Both squads are similarly experienced ({h_caps} vs {a_caps} caps).")

        # Run-scoring depth
        h_runs = h.get("Total Runs", 0)
        a_runs = a.get("Total Runs", 0)
        h_100s = h.get("100s", 0)
        a_100s = a.get("100s", 0)
        if h_100s > 0 or a_100s > 0:
            parts.append(
                f"{away if a_100s > h_100s else home} have more centurions ({max(h_100s, a_100s)} vs {min(h_100s, a_100s)} centuries)."
            )

        # Wicket-taking
        h_wkts = h.get("Total Wickets", 0)
        a_wkts = a.get("Total Wickets", 0)
        if h_wkts > 0 or a_wkts > 0:
            if abs(h_wkts - a_wkts) > 30:
                more_wkts = home if h_wkts > a_wkts else away
                parts.append(f"{more_wkts} have superior bowling depth ({max(h_wkts, a_wkts)} vs {min(h_wkts, a_wkts)} wickets).")

        return " ".join(parts) if parts else "Squads are broadly comparable on aggregate metrics."

    def _build_tactical_narrative(self, matrix_data, home, away):
        """Identifies vulnerability patterns from the tactical matrix."""
        if not matrix_data:
            return "No tactical matrix data available."

        parts = []
        for team, players in matrix_data.items():
            if not isinstance(players, list):
                continue
            # Find bowling types where batters average below 15 (vulnerability)
            vulnerabilities = {}
            for row in players:
                if not isinstance(row, dict):
                    continue
                player = row.get("Player", "")
                for col, val in row.items():
                    if col == "Player" or col.endswith("_raw"):
                        continue
                    # Check the _raw value for actual average
                    raw_key = f"{col}_raw"
                    raw_val = row.get(raw_key)
                    if raw_val is not None:
                        try:
                            avg = float(raw_val)
                            if 0 < avg < 15:
                                bowl_type = col.replace("Right-Arm ", "").replace("Left-Arm ", "").replace("Slow ", "").strip()
                                if bowl_type not in vulnerabilities:
                                    vulnerabilities[bowl_type] = []
                                vulnerabilities[bowl_type].append(f"{player} (avg {avg})")
                        except (ValueError, TypeError):
                            pass

            if vulnerabilities:
                for bowl_type, vuln_players in vulnerabilities.items():
                    if len(vuln_players) >= 2:
                        parts.append(
                            f"{team} batters are vulnerable to {bowl_type}: {', '.join(vuln_players[:3])}."
                        )

        return " ".join(parts) if parts else "No clear tactical vulnerabilities identified from the bowling-type matrix."

    def _build_matchup_narrative(self, matchup_data, home, away):
        """Identifies key bunny alerts and domination matchups."""
        if not matchup_data:
            return "No matchup data available."

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
                    bowler = m.get("Bowler", m.get("RawName", ""))
                    outs = m.get("Outs", 0)
                    avg = m.get("Avg", 0)
                    runs = m.get("Runs", 0)
                    balls = m.get("Balls", 0)
                    sr = m.get("SR", 0)

                    # Bunny: dismissed 3+ times with avg < 20
                    if isinstance(outs, (int, float)) and outs >= 3 and isinstance(avg, (int, float)) and 0 < avg < 20:
                        bunnies.append(f"{batter} is a bunny of {bowler} ({outs} dismissals, avg {avg}).")

                    # Domination: 50+ runs at SR > 100 with 0 dismissals
                    if isinstance(runs, (int, float)) and runs >= 50 and isinstance(sr, (int, float)) and sr > 100 and outs == 0:
                        dominations.append(f"{batter} dominates {bowler} ({runs} runs at SR {sr}, never out).")

        parts = []
        if bunnies:
            parts.append("KEY BUNNY ALERTS: " + " ".join(bunnies[:5]))
        if dominations:
            parts.append("DOMINATION MATCHUPS: " + " ".join(dominations[:3]))

        return " ".join(parts) if parts else "No extreme bunny alerts or domination matchups detected."

    def _build_player_stats_narrative(self, player_stats, home, away):
        """Summarizes key player stats: form standouts, venue specialists, strugglers."""
        if not player_stats:
            return "No player stats available."

        standouts = []
        venue_specialists = []
        strugglers = []

        for team, players in player_stats.items():
            if not isinstance(players, dict):
                continue
            for player_name, stats in players.items():
                if not isinstance(stats, dict) or "error" in stats:
                    continue
                batting = stats.get("batting", {})
                bowling = stats.get("bowling", {})

                # Batting form standout: avg > 40
                bat_avg = batting.get("average", 0)
                innings = batting.get("innings", 0)
                if isinstance(bat_avg, (int, float)) and bat_avg > 40 and innings >= 5:
                    standouts.append(f"{player_name} ({team}) avg {bat_avg} in {innings} innings.")

                # Venue specialist: venue avg > 35 with 3+ innings
                venue = batting.get("venue", {})
                v_avg = venue.get("average", 0)
                v_inns = venue.get("innings", 0)
                if isinstance(v_avg, (int, float)) and v_avg > 35 and isinstance(v_inns, int) and v_inns >= 3:
                    venue_specialists.append(f"{player_name} ({team}) venue avg {v_avg} in {v_inns} innings.")

                # Struggler: avg < 18 with 5+ innings
                if isinstance(bat_avg, (int, float)) and 0 < bat_avg < 18 and innings >= 5:
                    strugglers.append(f"{player_name} ({team}) avg only {bat_avg}.")

        parts = []
        if standouts:
            parts.append("IN-FORM BATTERS: " + " ".join(standouts[:4]))
        if venue_specialists:
            parts.append("VENUE SPECIALISTS: " + " ".join(venue_specialists[:3]))
        if strugglers:
            parts.append("STRUGGLING: " + " ".join(strugglers[:3]))

        return " ".join(parts) if parts else "No extreme standout or struggling players identified."

    def _build_smart_pitch_narrative(self, roster_data, player_stats, home, away, pitch_cond):
        """
        FIX 4: Builds a data-driven pitch suitability narrative using actual player stats
        instead of just bowler count.
        """
        pitch_lower = pitch_cond.lower()
        is_spin_pitch = any(kw in pitch_lower for kw in ["dry", "turn", "dust", "spin", "cracks"])
        is_pace_pitch = any(kw in pitch_lower for kw in ["green", "seam", "pace", "moisture", "grass"])

        if not is_spin_pitch and not is_pace_pitch:
            return ""

        parts = []
        target_type = "spin" if is_spin_pitch else "pace"

        # Collect venue wickets for spin/pace bowlers from player_stats
        home_venue_wkts = 0
        away_venue_wkts = 0
        home_bowlers_with_venue_data = []
        away_bowlers_with_venue_data = []

        for team, players in player_stats.items():
            if not isinstance(players, dict):
                continue
            for player_name, stats in players.items():
                if not isinstance(stats, dict) or "error" in stats:
                    continue
                style = BOWLER_STYLES.get(player_name, "")
                if not style or style == "Part-Timer":
                    continue

                is_spin = any(kw in str(style).lower() for kw in ["spin", "orth", "unorth"])
                is_pace = any(kw in str(style).lower() for kw in ["fast", "med"])

                if (target_type == "spin" and is_spin) or (target_type == "pace" and is_pace):
                    bowling = stats.get("bowling", {})
                    v_wkts = bowling.get("venue_wickets", 0)
                    v_matches = bowling.get("venue_matches", 0)
                    v_econ = bowling.get("venue_economy", 0)

                    if isinstance(v_wkts, (int, float)) and v_wkts > 0:
                        entry = f"{player_name} ({v_wkts} wkts in {v_matches} matches, econ {v_econ})"
                        if team == home:
                            home_venue_wkts += v_wkts
                            home_bowlers_with_venue_data.append(entry)
                        else:
                            away_venue_wkts += v_wkts
                            away_bowlers_with_venue_data.append(entry)

        surface = "spin-friendly" if is_spin_pitch else "seam-friendly"
        parts.append(f"On this {surface} surface:")

        if home_bowlers_with_venue_data or away_bowlers_with_venue_data:
            if home_venue_wkts > away_venue_wkts:
                parts.append(
                    f"{home} {target_type} bowlers have taken {home_venue_wkts} wickets at this venue vs "
                    f"{away}'s {away_venue_wkts}. "
                )
            elif away_venue_wkts > home_venue_wkts:
                parts.append(
                    f"{away} {target_type} bowlers have taken {away_venue_wkts} wickets at this venue vs "
                    f"{home}'s {home_venue_wkts}. "
                )
            else:
                parts.append(f"Both teams' {target_type} bowlers have {home_venue_wkts} venue wickets each. ")

            if home_bowlers_with_venue_data:
                parts.append(f"{home} venue {target_type} bowlers: {'; '.join(home_bowlers_with_venue_data[:3])}.")
            if away_bowlers_with_venue_data:
                parts.append(f"{away} venue {target_type} bowlers: {'; '.join(away_bowlers_with_venue_data[:3])}.")
        else:
            suitability = roster_data.get("pitch_suitability", {})
            h_count = suitability.get(f"home_{target_type}_bowlers", 0) if target_type == "spin" else suitability.get("home_pace_bowlers", 0)
            a_count = suitability.get(f"away_{target_type}_bowlers", 0) if target_type == "spin" else suitability.get("away_pace_bowlers", 0)
            parts.append(
                f"No venue-specific wicket data available for {target_type} bowlers. "
                f"By roster count: {home} has {h_count} vs {away}'s {a_count} {target_type} bowlers."
            )

        return " ".join(parts)

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _silent_call(self, func, *args, **kwargs):
        """
        Calls an engine function while suppressing its stdout/print output.
        The engine methods print HTML/tables for the UI — we only want the return value.

        This is the key to the "don't change the look and feel" constraint:
        engine methods still display normally when called from the UI buttons,
        but when called from the generator, their print output is captured and discarded.
        """
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            sys.stdout = old_stdout
            print(f"  ⚠️ Engine call failed: {func.__name__} — {str(e)}")
            return None
        finally:
            sys.stdout = old_stdout
        return result

    def _build_phase_narrative(self, phase_data, home, away):
        """Generates a narrative summary from phase analysis data."""
        baseline = phase_data.get("venue_baseline", {})
        home_venue = phase_data.get("home_at_venue", {})
        away_venue = phase_data.get("away_at_venue", {})
        global_hab = phase_data.get("global_habits", {})
        alerts = phase_data.get("alerts", [])

        parts = []

        # Baseline insight
        pp_avg = baseline.get("pp_avg_1st", 0)
        mid_avg = baseline.get("mid_avg_1st", 0)
        dth_avg = baseline.get("dth_avg_1st", 0)
        if pp_avg and dth_avg:
            if dth_avg > pp_avg:
                parts.append(f"This venue rewards death-overs aggression (Death avg {dth_avg} vs PP avg {pp_avg} in 1st innings).")
            else:
                parts.append(f"Powerplay is key at this venue (PP avg {pp_avg} vs Death avg {dth_avg} in 1st innings).")

        # Home vs Away at venue comparison
        if home_venue and away_venue:
            h_pp = home_venue.get("pp_avg_1st", 0)
            a_pp = away_venue.get("pp_avg_1st", 0)
            if h_pp > 0 and a_pp > 0:
                if abs(h_pp - a_pp) > 5:
                    better = home if h_pp > a_pp else away
                    parts.append(f"{better} score more in the Powerplay at this venue ({max(h_pp, a_pp)} vs {min(h_pp, a_pp)}).")

        # Global habits insight — uses RENAMED keys (home_team_/away_team_)
        bat_first = global_hab.get("bat_first", {})
        if bat_first:
            h_dth = bat_first.get("home_team_dth_runs", 0)
            a_dth = bat_first.get("away_team_dth_runs", 0)
            if h_dth > 0 and a_dth > 0 and abs(h_dth - a_dth) > 5:
                better = home if h_dth > a_dth else away
                parts.append(f"{better} score significantly more in death overs globally ({max(h_dth, a_dth)} vs {min(h_dth, a_dth)}).")

        # 2nd innings death overs caveat
        dth_2nd = baseline.get("dth_avg_2nd", 0)
        if dth_2nd > 0:
            parts.append(
                "Note: 2nd innings death-over averages may be understated as many chases end before overs 41-50."
            )

        # Alerts
        for alert in alerts:
            parts.append(alert)

        return " ".join(parts) if parts else "Phase analysis data available — see detailed breakdown."

    def _strip_internal_keys(self, obj):
        """
        Recursively strips all keys starting with '_' (internal diagnostics)
        from the final JSON output. This removes _match_ids, _squad_match_ids, etc.
        """
        if isinstance(obj, dict):
            return {k: self._strip_internal_keys(v) for k, v in obj.items() if not k.startswith('_')}
        elif isinstance(obj, list):
            return [self._strip_internal_keys(item) for item in obj]
        else:
            return obj

    def _save_report(self, match_pack, home, away):
        """Saves the match pack JSON to the reports directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"MatchPack_{home}_vs_{away}_{timestamp}.json"

        # Ensure reports directory exists
        reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        os.makedirs(reports_dir, exist_ok=True)

        filepath = os.path.join(reports_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(match_pack, f, indent=2, ensure_ascii=False, default=str)

        return filepath
