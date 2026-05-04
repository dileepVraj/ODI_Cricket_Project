"""
core/match_pack/interpreters._summary_interpreter -- executive summary synthesis domain.
"""
from __future__ import annotations

from typing import Any, Dict, List

from core.match_pack.interpreters._base import InterpreterBase


class SummaryInterpreter(InterpreterBase):
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
        key_factors: List[str] = []
        risk_alerts: List[str] = []

        ch1 = chapters.get("Chapter_1_Macro_Context", {})

        h2h_4y = ch1.get("global_h2h_4y", {})
        h2h_ctx = h2h_4y.get("context", {})
        if h2h_ctx.get("dominance") in ("HOME_DOMINANT", "AWAY_DOMINANT"):
            dom_team = home_team if "HOME" in h2h_ctx.get("dominance", "") else away_team
            h2h_data = h2h_4y.get("data", {})
            home_win_pct = h2h_data.get("home_win_pct", 0)
            dom_win_pct = home_win_pct if "HOME" in h2h_ctx.get("dominance", "") else 100 - home_win_pct
            key_factors.append(
                f"{dom_team} dominate the H2H with "
                f"{dom_win_pct}% "
                f"win rate ({h2h_data.get('matches_played', 0)} matches, 4Y)."
            )

        for team_key in ["home_form", "away_form"]:
            form_data = ch1.get(team_key, {}).get("global", {})
            form_ctx = form_data.get("context", {})
            team_label = home_team if "home" in team_key else away_team
            if form_ctx.get("momentum") == "COLD":
                risk_alerts.append(
                    f"{team_label} recent form is COLD "
                    f"({form_data.get('data', {}).get('wins', 0)}/"
                    f"{form_data.get('data', {}).get('total', 0)} wins)."
                )
            elif form_ctx.get("momentum") == "HOT":
                key_factors.append(
                    f"{team_label} are in HOT form "
                    f"({form_data.get('data', {}).get('wins', 0)}/"
                    f"{form_data.get('data', {}).get('total', 0)} wins)."
                )

        ch2 = chapters.get("Chapter_2_Battlefield", {})

        fortress = ch2.get("fortress_check", {})
        fortress_ctx = fortress.get("context", {})
        if fortress_ctx.get("fortress_status") == "FORTRESS_CONFIRMED":
            f_data = fortress.get("data", {})
            key_factors.append(
                f"Fortress venue: {home_team} win {f_data.get('home_win_pct', 0)}% here "
                f"({f_data.get('home_wins', 0)}/{f_data.get('matches_played', 0)} matches)."
            )

        toss = ch2.get("toss_bias", {})
        toss_ctx = toss.get("context", {})
        if toss_ctx.get("toss_alignment") == "TOSS_ALIGNED":
            key_factors.append(
                "Toss decision aligns with venue bias - tactical advantage gained."
            )
        elif toss_ctx.get("toss_alignment") == "COUNTER_TOSS":
            risk_alerts.append(
                "Away team won the toss and chose the statistically favoured option - "
                "counter-toss alert."
            )

        ch3 = chapters.get("Chapter_3_Tactical_Engine", {})
        cond = ch3.get("condition_weights", {})
        adjustments = cond.get("adjustments", [])

        ch4 = chapters.get("Chapter_4_Player_Intelligence", {})
        roster = ch4.get("bowling_roster", {})
        roster_verdict = roster.get("pitch_suitability", {}).get("verdict", "")
        if "HOME_SPIN_ADVANTAGE" in roster_verdict:
            key_factors.append(
                f"Pitch favours spin - {home_team} has more specialist spinners."
            )
        elif "AWAY_SPIN_ADVANTAGE" in roster_verdict:
            risk_alerts.append(
                f"Pitch favours spin - {away_team} has more specialist spinners than {home_team}."
            )

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
            prediction = "Too close to call - both teams have matching strengths and weaknesses."

        condition_str = " | ".join(adjustments) if adjustments else "No significant condition modifiers."

        return {
            "prediction": prediction,
            "key_factors": key_factors[:5],
            "risk_alerts": risk_alerts[:5],
            "condition_adjustments": condition_str,
        }
