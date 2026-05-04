"""Bowling matchup and tactical narrative builders."""

from typing import Any, Dict, List

from formats.odi.config.players import BOWLER_STYLES


class MatchupNarrativeBuilder:
    def _build_tactical_narrative(self, matrix_data: Dict[str, Any], home: str, away: str) -> str:
        if not matrix_data:
            return "No tactical matrix data available."

        parts: List[str] = []
        for team, players in matrix_data.items():
            if not isinstance(players, list):
                continue

            vulnerabilities: Dict[str, List[str]] = {}
            for row in players:
                if not isinstance(row, dict):
                    continue

                player = row.get("Player", "")
                for col, _value in row.items():
                    if col == "Player" or col.endswith("_raw"):
                        continue

                    raw_val = row.get(f"{col}_raw")
                    if raw_val is None:
                        continue

                    try:
                        avg = float(raw_val)
                    except (ValueError, TypeError):
                        continue

                    if 0 < avg < 15:
                        bowl_type = (
                            col.replace("Right-Arm ", "")
                            .replace("Left-Arm ", "")
                            .replace("Slow ", "")
                            .strip()
                        )
                        vulnerabilities.setdefault(bowl_type, []).append(f"{player} (avg {avg})")

            for bowl_type, vuln_players in vulnerabilities.items():
                if len(vuln_players) >= 2:
                    parts.append(f"{team} batters are vulnerable to {bowl_type}: {', '.join(vuln_players[:3])}.")

        return " ".join(parts) if parts else "No clear tactical vulnerabilities identified from the bowling-type matrix."

    def _build_matchup_narrative(self, matchup_data: Dict[str, Any], home: str, away: str) -> str:
        if not matchup_data:
            return "No matchup data available."

        bunnies: List[str] = []
        dominations: List[str] = []

        for _team, players in matchup_data.items():
            if not isinstance(players, dict):
                continue

            for batter, bowler_list in players.items():
                if not isinstance(bowler_list, list):
                    continue

                for matchup in bowler_list:
                    if not isinstance(matchup, dict):
                        continue

                    bowler = matchup.get("Bowler", matchup.get("RawName", ""))
                    outs = matchup.get("Outs", 0)
                    avg = matchup.get("Avg", 0)
                    runs = matchup.get("Runs", 0)
                    sr = matchup.get("SR", 0)

                    if isinstance(outs, (int, float)) and outs >= 3 and isinstance(avg, (int, float)) and 0 < avg < 20:
                        bunnies.append(f"{batter} is a bunny of {bowler} ({outs} dismissals, avg {avg}).")

                    if isinstance(runs, (int, float)) and runs >= 50 and isinstance(sr, (int, float)) and sr > 100 and outs == 0:
                        dominations.append(f"{batter} dominates {bowler} ({runs} runs at SR {sr}, never out).")

        parts: List[str] = []
        if bunnies:
            parts.append("KEY BUNNY ALERTS: " + " ".join(bunnies[:5]))
        if dominations:
            parts.append("DOMINATION MATCHUPS: " + " ".join(dominations[:3]))

        return " ".join(parts) if parts else "No extreme bunny alerts or domination matchups detected."

    def _build_role_based_tactical_narrative(self, tactical_data: Dict[str, Any], home: str, away: str) -> str:
        narrative_parts: List[str] = []

        for team_name in [home, away]:
            team_rows = tactical_data.get(team_name, [])
            if not team_rows:
                continue

            strugglers: List[str] = []
            for row in team_rows:
                player = row.get("Player")
                role = row.get("Role", "")
                raw_scores = {
                    key.replace("_raw", ""): value
                    for key, value in row.items()
                    if key.endswith("_raw") and isinstance(value, (int, float))
                }
                if raw_scores:
                    worst_style = min(raw_scores, key=lambda style: raw_scores[style])
                    if raw_scores[worst_style] < 22:
                        strugglers.append(f"{player} ({role}) vs {worst_style}")

            if strugglers:
                narrative_parts.append(
                    f"TACTICAL WEAKNESS ({team_name}): {', '.join(strugglers[:2])} "
                    f"represent key target areas for opposition bowlers."
                )

        return (
            " ".join(narrative_parts)
            if narrative_parts
            else "Both lineups appear tactically balanced against opposition bowling styles."
        )

    def _build_smart_pitch_narrative(
        self,
        roster_data: Dict[str, Any],
        player_stats: Dict[str, Any],
        home: str,
        away: str,
        pitch_cond: str,
    ) -> str:
        pitch_lower = pitch_cond.lower()
        is_spin_pitch = any(keyword in pitch_lower for keyword in ["dry", "turn", "dust", "spin", "cracks"])
        is_pace_pitch = any(keyword in pitch_lower for keyword in ["green", "seam", "pace", "moisture", "grass"])

        if not is_spin_pitch and not is_pace_pitch:
            return ""

        parts: List[str] = []
        target_type = "spin" if is_spin_pitch else "pace"
        home_venue_wkts = 0.0
        away_venue_wkts = 0.0
        home_bowlers_with_venue_data: List[str] = []
        away_bowlers_with_venue_data: List[str] = []

        for team, players in player_stats.items():
            if not isinstance(players, dict):
                continue

            for player_name, stats in players.items():
                if not isinstance(stats, dict) or "error" in stats:
                    continue

                style = BOWLER_STYLES.get(player_name, "")
                if not style or style == "Part-Timer":
                    continue

                is_spin = any(keyword in str(style).lower() for keyword in ["spin", "orth", "unorth"])
                is_pace = any(keyword in str(style).lower() for keyword in ["fast", "med"])
                if (target_type == "spin" and is_spin) or (target_type == "pace" and is_pace):
                    bowling = stats.get("bowling", {})
                    venue_wkts = bowling.get("venue_wickets", 0)
                    venue_matches = bowling.get("venue_matches", 0)
                    venue_econ = bowling.get("venue_economy", 0)
                    if isinstance(venue_wkts, (int, float)) and venue_wkts > 0:
                        entry = f"{player_name} ({venue_wkts} wkts in {venue_matches} matches, econ {venue_econ})"
                        if team == home:
                            home_venue_wkts += venue_wkts
                            home_bowlers_with_venue_data.append(entry)
                        else:
                            away_venue_wkts += venue_wkts
                            away_bowlers_with_venue_data.append(entry)

        parts.append(f'On this {"spin-friendly" if is_spin_pitch else "seam-friendly"} surface:')
        if home_bowlers_with_venue_data or away_bowlers_with_venue_data:
            if home_venue_wkts > away_venue_wkts:
                parts.append(
                    f"{home} {target_type} bowlers have taken {home_venue_wkts} wickets at this venue "
                    f"vs {away}'s {away_venue_wkts}. "
                )
            elif away_venue_wkts > home_venue_wkts:
                parts.append(
                    f"{away} {target_type} bowlers have taken {away_venue_wkts} wickets at this venue "
                    f"vs {home}'s {home_venue_wkts}. "
                )
            else:
                parts.append(f"Both teams' {target_type} bowlers have {home_venue_wkts} venue wickets each. ")

            if home_bowlers_with_venue_data:
                parts.append(f"{home} venue {target_type} bowlers: {'; '.join(home_bowlers_with_venue_data[:3])}.")
            if away_bowlers_with_venue_data:
                parts.append(f"{away} venue {target_type} bowlers: {'; '.join(away_bowlers_with_venue_data[:3])}.")
        else:
            suitability = roster_data.get("pitch_suitability", {})
            h_count = (
                suitability.get(f"home_{target_type}_bowlers", 0)
                if target_type == "spin"
                else suitability.get("home_pace_bowlers", 0)
            )
            a_count = (
                suitability.get(f"away_{target_type}_bowlers", 0)
                if target_type == "spin"
                else suitability.get("away_pace_bowlers", 0)
            )
            parts.append(
                f"No venue-specific wicket data available for {target_type} bowlers. "
                f"By roster count: {home} has {h_count} vs {away}'s {a_count} {target_type} bowlers."
            )

        return " ".join(parts)
