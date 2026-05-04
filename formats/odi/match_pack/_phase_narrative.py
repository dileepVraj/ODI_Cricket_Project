"""Phase and conditions narrative builder."""

from typing import Any, Dict, List


class PhaseNarrativeBuilder:
    def _build_phase_narrative(self, phase_data: Dict[str, Any], home: str, away: str) -> str:
        baseline = phase_data.get("venue_baseline", {})
        home_venue = phase_data.get("home_at_venue", {})
        away_venue = phase_data.get("away_at_venue", {})
        global_hab = phase_data.get("global_habits", {})
        alerts = phase_data.get("alerts", [])
        parts: List[str] = []

        pp_avg = baseline.get("pp_avg_1st", 0)
        dth_avg = baseline.get("dth_avg_1st", 0)
        if pp_avg and dth_avg:
            if dth_avg > pp_avg:
                parts.append(f"This venue rewards death-overs aggression (Death avg {dth_avg} vs PP avg {pp_avg} in 1st innings).")
            else:
                parts.append(f"Powerplay is key at this venue (PP avg {pp_avg} vs Death avg {dth_avg} in 1st innings).")

        if home_venue and away_venue:
            home_pp = home_venue.get("pp_avg_1st", 0)
            away_pp = away_venue.get("pp_avg_1st", 0)
            if home_pp > 0 and away_pp > 0 and abs(home_pp - away_pp) > 5:
                parts.append(f"{home if home_pp > away_pp else away} score more in the Powerplay at this venue ({max(home_pp, away_pp)} vs {min(home_pp, away_pp)}).")

        bat_first = global_hab.get("bat_first", {})
        if bat_first:
            home_dth = bat_first.get("home_team_dth_runs", 0)
            away_dth = bat_first.get("away_team_dth_runs", 0)
            if home_dth > 0 and away_dth > 0 and abs(home_dth - away_dth) > 5:
                parts.append(f"{home if home_dth > away_dth else away} score significantly more in death overs globally ({max(home_dth, away_dth)} vs {min(home_dth, away_dth)}).")

        if baseline.get("dth_avg_2nd", 0) > 0:
            parts.append("Note: 2nd innings death-over averages may be understated as many chases end before overs 41-50.")

        parts.extend(alerts)
        return " ".join(parts) if parts else "Phase analysis data available  see detailed breakdown."
