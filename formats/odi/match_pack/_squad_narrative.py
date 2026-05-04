"""Squad and player-level narrative builders."""

from typing import Any, Dict, List


class SquadNarrativeBuilder:
    def _build_squad_narrative(self, squad_data: Dict[str, Any], home: str, away: str) -> str:
        if not squad_data:
            return "No squad data available."

        home_rows = squad_data.get(home, {})
        away_rows = squad_data.get(away, {})
        parts: List[str] = []

        home_caps = home_rows.get("Caps (Combined)", 0)
        away_caps = away_rows.get("Caps (Combined)", 0)
        if home_caps > 0 and away_caps > 0:
            if abs(home_caps - away_caps) > 50:
                more_exp = home if home_caps > away_caps else away
                parts.append(
                    f"{more_exp} have significantly more experience "
                    f"({max(home_caps, away_caps)} vs {min(home_caps, away_caps)} combined caps)."
                )
            else:
                parts.append(f"Both squads are similarly experienced ({home_caps} vs {away_caps} caps).")

        home_centuries = home_rows.get("100s", 0)
        away_centuries = away_rows.get("100s", 0)
        if home_centuries > 0 or away_centuries > 0:
            more_centuries = away if away_centuries > home_centuries else home
            parts.append(
                f"{more_centuries} have more centurions "
                f"({max(home_centuries, away_centuries)} vs {min(home_centuries, away_centuries)} centuries)."
            )

        home_wickets = home_rows.get("Total Wickets", 0)
        away_wickets = away_rows.get("Total Wickets", 0)
        if (home_wickets > 0 or away_wickets > 0) and abs(home_wickets - away_wickets) > 30:
            stronger_bowling = home if home_wickets > away_wickets else away
            parts.append(
                f"{stronger_bowling} have superior bowling depth "
                f"({max(home_wickets, away_wickets)} vs {min(home_wickets, away_wickets)} wickets)."
            )

        return " ".join(parts) if parts else "Squads are broadly comparable on aggregate metrics."

    def _build_player_stats_narrative(self, player_stats: Dict[str, Any], home: str, away: str) -> str:
        if not player_stats:
            return "No player stats available."

        bat_standouts: List[str] = []
        bowl_standouts: List[str] = []
        venue_kings: List[str] = []
        strugglers: List[str] = []

        for team, players in player_stats.items():
            if not isinstance(players, dict):
                continue

            for player_name, stats in players.items():
                if not isinstance(stats, dict) or "error" in stats:
                    continue

                batting = stats.get("batting", {})
                bowling = stats.get("bowling", {})

                bat_avg = batting.get("average", 0)
                innings = batting.get("innings", 0)
                if isinstance(bat_avg, (int, float)) and bat_avg > 45 and innings >= 5:
                    bat_standouts.append(f"{player_name} ({team})")
                elif isinstance(bat_avg, (int, float)) and 0 < bat_avg < 18 and innings >= 5:
                    strugglers.append(f"{player_name} ({team})")

                venue_avg = batting.get("venue", {}).get("average", 0)
                venue_innings = batting.get("venue", {}).get("innings", 0)
                if isinstance(venue_avg, (int, float)) and venue_avg > 40 and venue_innings >= 3:
                    venue_kings.append(f"{player_name} ({venue_avg} Avg)")

                bowl_wickets = bowling.get("career", {}).get("bowling", {}).get("wickets", 0)
                bowl_econ = bowling.get("career", {}).get("bowling", {}).get("economy", 10)
                if bowl_wickets > 20 and bowl_econ < 5.2:
                    bowl_standouts.append(f"{player_name} ({bowl_econ} Econ)")

        parts: List[str] = []
        if bat_standouts:
            parts.append(f"IN-FORM BATTERS: {', '.join(bat_standouts[:3])} are in elite touch (Avg 45+).")
        if bowl_standouts:
            parts.append(f"BOWLING THREATS: {', '.join(bowl_standouts[:3])} maintain elite economy rates.")
        if venue_kings:
            parts.append(f"VENUE SPECIALISTS: {', '.join(venue_kings[:3])} have historically dominated these conditions.")
        if strugglers:
            parts.append(f"UNDER PRESSURE: {', '.join(strugglers[:3])} are searching for form (Avg < 18).")

        return " ".join(parts) if parts else "No significant player-level trends identified."
