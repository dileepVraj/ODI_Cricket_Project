"""
core/match_pack/interpreters.summary_composer — summary composition domain.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.match_pack.interpreters._base import InterpreterBase


class MatchSummaryComposer(InterpreterBase):
    def interpret_conditions(
        self,
        pitch: str,
        time: str,
        toss: str,
        bias_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generates condition adjustments from pitch/time/toss context inputs.

        Keywords detected:
            Pitch: dry/cracks/turn/dust → SPIN_BOOST
            Pitch: green/grass/seam/moisture → SEAM_BOOST
            Time: night/14:30+/sunset → DEW_FACTOR
            Toss alignment with venue bias
        """
        adjustments = []
        weights = {}

        # Pitch analysis
        pitch_lower = str(pitch).lower() if pitch else ""
        if any(kw in pitch_lower for kw in ["dry", "cracks", "turn", "dust", "spin"]):
            adjustments.append("SPIN_BOOST")
            weights["spin_weight"] = 1.2  # +20%
        if any(kw in pitch_lower for kw in ["green", "grass", "seam", "moisture", "pace"]):
            adjustments.append("SEAM_BOOST")
            weights["pace_weight"] = 1.15  # +15%

        # Time analysis
        time_lower = str(time).lower() if time else ""
        if any(kw in time_lower for kw in ["night", "evening", "sunset", "dew"]):
            adjustments.append("DEW_FACTOR")
            weights["chase_boost"] = 1.1  # +10%
        # Check for late afternoon (14:30+)
        if any(t in time_lower for t in ["14:30", "15:00", "15:30", "16:00", "14:", "15:", "16:"]):
            adjustments.append("DEW_FACTOR")
            weights["chase_boost"] = 1.1

        # Toss alignment
        toss_lower = str(toss).lower() if toss else ""
        if bias_data and isinstance(bias_data, dict):
            verdict = bias_data.get("verdict", "NEUTRAL").upper()
            is_bat_first_venue = "BAT" in verdict

            if "home" in toss_lower and "batting" in toss_lower and is_bat_first_venue:
                adjustments.append("TOSS_ALIGNED")
            elif "away" in toss_lower and "batting" in toss_lower and is_bat_first_venue:
                adjustments.append("COUNTER_TOSS")
            elif "home" in toss_lower and "bowling" in toss_lower and not is_bat_first_venue:
                adjustments.append("TOSS_ALIGNED")
            elif "away" in toss_lower and "bowling" in toss_lower and not is_bat_first_venue:
                adjustments.append("COUNTER_TOSS")

        return {
            "adjustments": adjustments,
            "weights": weights,
            "pitch_report": str(pitch) if pitch else "",
            "match_time": str(time) if time else "",
            "toss_decision": str(toss) if toss else "",
        }

    def analyze_bowling_roster(
        self,
        home_xi: List[str],
        away_xi: List[str],
        pitch_conditions: str = "",
        player_stats: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Builds the bowling roster for both teams and determines pitch suitability.
        v3.3: Added awareness of bowler experience and career venue metrics.
        """
        def build_roster(players: List[str], team_stats: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
            roster = []
            for p in players:
                style = self.bowler_styles.get(p)
                if style and style != '🚫 Part-Timer':
                    role_raw = self.player_roles.get(p, "All-Rounder")
                    # Determine experience from player_stats if available
                    exp_rank = "INTERMEDIATE"
                    if team_stats and p in team_stats:
                        stats = team_stats[p]
                        wickets = stats.get('career', {}).get('bowling', {}).get('wickets', 0)
                        if wickets > 100:
                            exp_rank = "VETERAN"
                        elif wickets < 20:
                            exp_rank = "PROSPECT"

                    clean_style = style.replace('⚡ ', '').replace('🌀 ', '')
                    roster.append({
                        "bowler": p,
                        "type": clean_style,
                        "role": role_raw,
                        "experience": exp_rank
                    })
            return roster

        home_stats = player_stats.get("home", {}) if player_stats else {}
        away_stats = player_stats.get("away", {}) if player_stats else {}

        home_roster = build_roster(home_xi, home_stats)
        away_roster = build_roster(away_xi, away_stats)

        # Count spin vs pace
        home_spin = sum(1 for b in home_roster if "Spin" in b["type"] or "Orth" in b["type"] or "Unorth" in b["type"])
        away_spin = sum(1 for b in away_roster if "Spin" in b["type"] or "Orth" in b["type"] or "Unorth" in b["type"])
        home_pace = sum(1 for b in home_roster if "Fast" in b["type"] or "Med" in b["type"])
        away_pace = sum(1 for b in away_roster if "Fast" in b["type"] or "Med" in b["type"])

        # Pitch suitability
        pitch_lower = str(pitch_conditions).lower()
        is_spin_pitch = any(kw in pitch_lower for kw in ["dry", "turn", "dust", "spin", "cracks"])
        is_pace_pitch = any(kw in pitch_lower for kw in ["green", "seam", "pace", "moisture", "grass"])

        if is_spin_pitch:
            verdict = "HOME_SPIN_ADVANTAGE" if home_spin > away_spin else ("AWAY_SPIN_ADVANTAGE" if away_spin > home_spin else "EVEN_SPIN")
        elif is_pace_pitch:
            verdict = "HOME_PACE_ADVANTAGE" if home_pace > away_pace else ("AWAY_PACE_ADVANTAGE" if away_pace > home_pace else "EVEN_PACE")
        else:
            verdict = "BALANCED"

        narrative = ""
        if is_spin_pitch:
            more_spin_team = "Home" if home_spin > away_spin else "Away"
            narrative = (
                f"{more_spin_team} team has {max(home_spin, away_spin)} spinner(s) vs "
                f"{min(home_spin, away_spin)}. On this spin-friendly surface, "
                f"the {'home' if home_spin > away_spin else 'away'} bowling attack is better suited."
            )
        elif is_pace_pitch:
            more_pace_team = "Home" if home_pace > away_pace else "Away"
            narrative = (
                f"{more_pace_team} team has {max(home_pace, away_pace)} pacer(s) vs "
                f"{min(home_pace, away_pace)}. On this seam-friendly surface, "
                f"the {'home' if home_pace > away_pace else 'away'} bowling attack is better suited."
            )
        else:
            narrative = f"Balanced conditions — Home has {home_spin}S/{home_pace}P, Away has {away_spin}S/{away_pace}P."

        return {
            "home": home_roster,
            "away": away_roster,
            "pitch_suitability": {
                "home_spin_bowlers": home_spin,
                "away_spin_bowlers": away_spin,
                "home_pace_bowlers": home_pace,
                "away_pace_bowlers": away_pace,
                "verdict": verdict,
                "narrative": narrative,
            },
        }

    def generate_executive_summary(
        self,
        chapters: Dict[str, Any],
        home_team: str,
        away_team: str,
        conditions: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Synthesizes all chapter data into a TL;DR executive summary.

        Returns:
            dict: {prediction, key_factors, risk_alerts, condition_adjustments}
        """
        key_factors = []
        risk_alerts = []

        # --- From Chapter 1: Macro Context ---
        ch1 = chapters.get("Chapter_1_Macro_Context", {})

        # H2H dominance
        h2h_4y = ch1.get("global_h2h_4y", {})
        h2h_ctx = h2h_4y.get("context", {})
        if h2h_ctx.get("dominance") in ("HOME_DOMINANT", "AWAY_DOMINANT"):
            dom_team = home_team if "HOME" in h2h_ctx.get("dominance", "") else away_team
            h2h_data = h2h_4y.get("data", {})
            key_factors.append(
                f"{dom_team} dominate the H2H with {h2h_data.get('home_win_pct', 0) if 'HOME' in h2h_ctx.get('dominance', '') else 100 - h2h_data.get('home_win_pct', 0)}% "
                f"win rate ({h2h_data.get('matches_played', 0)} matches, 4Y)."
            )

        # Form alerts
        for team_key in ["home_form", "away_form"]:
            form_data = ch1.get(team_key, {}).get("global", {})
            form_ctx = form_data.get("context", {})
            team_label = home_team if "home" in team_key else away_team
            if form_ctx.get("momentum") == "COLD":
                risk_alerts.append(f"{team_label} recent form is COLD ({form_data.get('data', {}).get('wins', 0)}/{form_data.get('data', {}).get('total', 0)} wins).")
            elif form_ctx.get("momentum") == "HOT":
                key_factors.append(f"{team_label} are in HOT form ({form_data.get('data', {}).get('wins', 0)}/{form_data.get('data', {}).get('total', 0)} wins).")

        # --- From Chapter 2: Battlefield ---
        ch2 = chapters.get("Chapter_2_Battlefield", {})

        # Fortress
        fortress = ch2.get("fortress_check", {})
        fortress_ctx = fortress.get("context", {})
        if fortress_ctx.get("fortress_status") == "FORTRESS_CONFIRMED":
            f_data = fortress.get("data", {})
            key_factors.append(
                f"Fortress venue: {home_team} win {f_data.get('home_win_pct', 0)}% here "
                f"({f_data.get('home_wins', 0)}/{f_data.get('matches_played', 0)} matches)."
            )

        # Toss bias
        toss = ch2.get("toss_bias", {})
        toss_ctx = toss.get("context", {})
        if toss_ctx.get("toss_alignment") == "TOSS_ALIGNED":
            key_factors.append("Toss decision aligns with venue bias — tactical advantage gained.")
        elif toss_ctx.get("toss_alignment") == "COUNTER_TOSS":
            risk_alerts.append("Away team won the toss and chose the statistically favoured option — counter-toss alert.")

        # --- From Chapter 3: Conditions ---
        ch3 = chapters.get("Chapter_3_Tactical_Engine", {})
        cond = ch3.get("condition_weights", {})
        adjustments = cond.get("adjustments", [])

        # --- From Chapter 4: Player Intelligence ---
        ch4 = chapters.get("Chapter_4_Player_Intelligence", {})
        roster = ch4.get("bowling_roster", {})
        roster_verdict = roster.get("pitch_suitability", {}).get("verdict", "")
        if "HOME_SPIN_ADVANTAGE" in roster_verdict:
            key_factors.append(
                f"Pitch favours spin — {home_team} has more specialist spinners."
            )
        elif "AWAY_SPIN_ADVANTAGE" in roster_verdict:
            risk_alerts.append(
                f"Pitch favours spin — {away_team} has more specialist spinners than {home_team}."
            )

        # --- Build Prediction ---
        home_factors = sum(1 for f in key_factors if home_team in f)
        away_factors = sum(1 for f in key_factors if away_team in f)
        home_risks = sum(1 for r in risk_alerts if home_team in r)
        away_risks = sum(1 for r in risk_alerts if away_team in r)

        net_home = (home_factors - home_risks) - (away_factors - away_risks)

        if net_home > 2:
            prediction = f"{home_team} strong favourites with multiple advantages."
        elif net_home > 0:
            prediction = f"{home_team} slight favourites despite some risk factors."
        elif net_home < -2:
            prediction = f"{away_team} strong favourites with multiple advantages."
        elif net_home < 0:
            prediction = f"{away_team} slight favourites despite some risk factors."
        else:
            prediction = "Too close to call — both teams have matching strengths and weaknesses."

        condition_str = " | ".join(adjustments) if adjustments else "No significant condition modifiers."

        return {
            "prediction": prediction,
            "key_factors": key_factors[:5],  # Cap at 5 most important
            "risk_alerts": risk_alerts[:5],
            "condition_adjustments": condition_str,
        }
