from typing import Callable, Dict, List, Union

from config.shared.team_colors import TEAM_COLORS
from core.interfaces.team_types import (
    ComparisonReportRow,
    FormGuidePayload,
    MATRIX_ROW_HOME_TEAM_COLOR,
    MATRIX_ROW_HOME_TEAM_NAME,
    TeamMetricsPayload,
    MatrixReportRow,
    PlayerStatRow,
    SquadComparisonPayload,
    TeamFormRow,
)

import numpy as np
import pandas as pd

from core.services.match_filter_service import MatchFilterService
from core.services.report_formatter import ReportFormatter


class ReportBuilder:
    """Stateless report payload builder for team comparison outputs."""

    @staticmethod
    def _get_avg_with_count(df: pd.DataFrame, col: str) -> str:
        """
        Calculates the mean of a column and formats it as "Avg [Count]".
        """
        if df.empty or col not in df.columns:
            return "-"

        # Average match-level scores (row-level rows can be duplicated).
        match_scores = df.groupby("match_id")[col].first()

        val = match_scores.mean()
        if pd.isna(val) or val == 0:
            return "-"

        return f"{int(val)} [{len(match_scores)}]"

    @staticmethod
    def _build_report_data(
        df: pd.DataFrame,
        home_team: str,
        visitor_label: str,
        title: str,
        is_venue_mode: bool,
        calculate_team_stats: Callable[[pd.DataFrame, str, bool], TeamMetricsPayload],
    ) -> list[ComparisonReportRow]:
        """
        Build the flat H2H/Fortress report rows consumed by the frontend.
        """
        _ = title
        matches = len(df)
        winners = df["winner"].astype(str).str.lower().str.strip()
        home_clean = home_team.lower().strip()
        home_wins = len(df[winners == home_clean])
        tie_nr = len(df[winners.isin(["tie", "no result", "nan", "none"])])

        if visitor_label == "Visitors":
            visitor_wins = matches - home_wins - tie_nr
            visitor_wins_df = df[(winners != home_clean) & (~winners.isin(["tie", "no result", "nan", "none"]))]
        else:
            visitor_clean = visitor_label.lower().strip()
            visitor_wins = len(df[winners == visitor_clean])
            visitor_wins_df = df[winners == visitor_clean]

        home_wins_df = df[winners == home_clean]
        home_win_bat1 = len(home_wins_df[home_wins_df["team_bat_1"] == home_team])
        home_win_bat2 = len(home_wins_df[home_wins_df["team_bat_2"] == home_team])

        if visitor_label == "Visitors":
            visitor_win_bat1 = len(visitor_wins_df[visitor_wins_df["team_bat_2"] == home_team])
            visitor_win_bat2 = len(visitor_wins_df[visitor_wins_df["team_bat_1"] == home_team])
        else:
            visitor_win_bat1 = len(visitor_wins_df[visitor_wins_df["team_bat_1"] == visitor_label])
            visitor_win_bat2 = len(visitor_wins_df[visitor_wins_df["team_bat_2"] == visitor_label])

        decisions = matches - tie_nr
        win_rate = int((home_wins / decisions) * 100) if decisions > 0 else 0

        df_for_stats = df.copy()
        if is_venue_mode:
            df_for_stats["home_team_ref"] = home_team

        home_stats = calculate_team_stats(df_for_stats, home_team, False)
        visitor_stats = calculate_team_stats(df_for_stats, visitor_label, is_venue_mode)

        valid_2nd_mask = MatchFilterService.get_valid_matches_mask(df)
        valid_1st_mask = valid_2nd_mask | MatchFilterService.get_excluded_short_second_mask(df)
        valid_1st = df[valid_1st_mask]
        valid_2nd = df[valid_2nd_mask]

        data = [
            {"Metric": "Matches Played", "Value": matches},
            {"Metric": "Tied / No Result", "Value": tie_nr},
            {"Metric": f"{home_team} Win %", "Value": f"{win_rate}%"},
            {"Metric": "--- HOME PERFORMANCE ---", "Value": ""},
            {"Metric": "Total Wins", "Value": home_wins},
            {"Metric": "Won Batting 1st (Defended)", "Value": home_win_bat1},
            {"Metric": "Won Batting 2nd (Chased)", "Value": home_win_bat2},
            {"Metric": "--- VISITOR PERFORMANCE ---", "Value": ""},
            {"Metric": "Total Wins", "Value": visitor_wins},
            {"Metric": "Won Batting 1st (Defended)", "Value": visitor_win_bat1},
            {"Metric": "Won Batting 2nd (Chased)", "Value": visitor_win_bat2},
            {"Metric": "--- VENUE AVERAGES ---", "Value": ""},
            {"Metric": "Overall Avg 1st Innings", "Value": ReportBuilder._get_avg_with_count(valid_1st, "score_inn1")},
            {"Metric": "Overall Avg 2nd Innings", "Value": ReportBuilder._get_avg_with_count(valid_2nd, "score_inn2")},
            {
                "Metric": "Avg 1st Innings Winning Score",
                "Value": ReportBuilder._get_avg_with_count(valid_1st[valid_1st["winner"] == valid_1st["team_bat_1"]], "score_inn1"),
            },
            {"Metric": f"--- BATTING 1ST ({home_team.upper()}) ---", "Value": ""},
            {"Metric": "Average 1st Innings", "Value": home_stats["avg_1st"]},
            {"Metric": "Highest 1st Innings", "Value": home_stats["high_1st"]},
            {"Metric": "Lowest 1st Innings", "Value": home_stats["low_1st"]},
            {"Metric": "Avg Winning Score", "Value": home_stats["avg_1st_win"]},
            {"Metric": "Lowest Defended Score", "Value": home_stats["low_defended"]},
            {"Metric": f"--- BATTING 1ST ({visitor_label.upper()}) ---", "Value": ""},
            {"Metric": "Average 1st Innings", "Value": visitor_stats["avg_1st"]},
            {"Metric": "Highest 1st Innings", "Value": visitor_stats["high_1st"]},
            {"Metric": "Lowest 1st Innings", "Value": visitor_stats["low_1st"]},
            {"Metric": "Avg Winning Score", "Value": visitor_stats["avg_1st_win"]},
            {"Metric": "Lowest Defended Score", "Value": visitor_stats["low_defended"]},
            {"Metric": f"--- CHASING ({home_team.upper()}) ---", "Value": ""},
            {"Metric": "Average 2nd Innings", "Value": home_stats["avg_2nd"]},
            {"Metric": "Highest Chased", "Value": home_stats["high_chased"]},
            {"Metric": "Avg Successful Chase", "Value": home_stats["avg_succ"]},
            {"Metric": "Avg Failed Chase", "Value": home_stats["avg_fail"]},
            {"Metric": f"--- CHASING ({visitor_label.upper()}) ---", "Value": ""},
            {"Metric": "Average 2nd Innings", "Value": visitor_stats["avg_2nd"]},
            {"Metric": "Highest Chased", "Value": visitor_stats["high_chased"]},
            {"Metric": "Avg Successful Chase", "Value": visitor_stats["avg_succ"]},
            {"Metric": "Avg Failed Chase", "Value": visitor_stats["avg_fail"]},
            {"Metric": "MATCH_IDS", "Value": ",".join(df["match_id"].astype(str).unique().tolist())},
        ]

        current_section = "Overview"
        current_section_tone = ReportFormatter._comparison_section_tone(current_section)
        for row in data:
            metric = str(row.get("Metric", ""))
            if metric.startswith("---") and metric.endswith("---"):
                section_label = metric.strip("- ").strip()
                current_section = section_label or current_section
                current_section_tone = ReportFormatter._comparison_section_tone(current_section)
                row["row_kind"] = "section"
                row["display_metric"] = section_label
                row["section_label"] = current_section
                row["section_tone"] = current_section_tone
                row["value_tone"] = "muted"
                row["is_zero_or_empty"] = False
                continue

            row_kind = "meta" if metric == "MATCH_IDS" else "metric"
            row["row_kind"] = row_kind
            row["display_metric"] = metric
            row["section_label"] = current_section
            row["section_tone"] = current_section_tone

            value = row.get("Value")
            is_zero_or_empty = value in ("", 0, "0")
            row["is_zero_or_empty"] = bool(is_zero_or_empty)
            if "win %" in metric.lower():
                row["value_tone"] = ReportFormatter._tone_from_win_pct(value)
            elif is_zero_or_empty:
                row["value_tone"] = "muted"
            else:
                row["value_tone"] = "default"

        return data

    @staticmethod
    def _build_form_data_payload(df: pd.DataFrame, team: str) -> FormGuidePayload:
        """
        Build semantic form data without UI/emoji sequences.
        """
        if df.empty:
            return {"wins": 0, "losses": 0, "no_results": 0, "total": 0, "raw_results": []}

        recent = df.sort_values("start_date", ascending=False).head(5)
        winners = recent["winner"].astype(str).str.lower()
        team_lower = team.lower()
        is_level = recent["score_inn1"] == recent["score_inn2"]

        conditions = [
            winners == team_lower,
            (winners == "tie") | (winners.isin(["nan", "no result"]) & is_level),
            winners.isin(["nan", "no result"]),
        ]
        choices = ["W", "T", "NR"]
        raw_results = np.select(conditions, choices, default="L").tolist()

        wins = int((np.array(raw_results) == "W").sum())
        losses = int((np.array(raw_results) == "L").sum())
        nrs = int(((np.array(raw_results) != "W") & (np.array(raw_results) != "L")).sum())

        return {
            "wins": wins,
            "losses": losses,
            "no_results": int(nrs),
            "total": int(len(recent)),
            "raw_results": raw_results,
        }

    @staticmethod
    def _generate_matrix_report(
        matches: pd.DataFrame,
        team_name: str,
        title: str,
        is_away: bool,
        apply_smart_filters: Callable[[pd.DataFrame], pd.DataFrame],
        serialize_ui_records: Callable[[pd.DataFrame], list[MatrixReportRow] | list[ComparisonReportRow]],
    ) -> list[MatrixReportRow]:
        """
        Generate a multi-opponent matrix report (row per opponent + overall row).
        """
        _ = title
        _ = is_away
        clean = apply_smart_filters(matches)

        # Vectorized opponent detection.
        clean["opponent"] = np.where(clean["team_bat_1"] == team_name, clean["team_bat_2"], clean["team_bat_1"])

        count_mask = ~MatchFilterService.get_excluded_no_result_mask(clean)
        valid_2nd_mask = MatchFilterService.get_valid_matches_mask(clean)
        valid_1st_mask = valid_2nd_mask | MatchFilterService.get_excluded_short_second_mask(clean)
        valid = clean[valid_1st_mask]

        # Sort opponents alphabetically for stable matrix row ordering across callers.
        opponents = sorted([opp for opp in clean["opponent"].unique() if pd.notna(opp) and opp != team_name])

        stats = []
        for opp in opponents:
            full = clean[(clean["opponent"] == opp) & count_mask]
            if full.empty:
                continue

            val = valid[valid["opponent"] == opp]

            wins = len(full[full["winner"] == team_name])
            losses = len(full[full["winner"] == opp])
            decisions = wins + losses
            tie_nr = len(full) - decisions
            known_non_decisions = int(
                full["winner"].astype(str).str.lower().str.strip().isin(["tie", "no result", "nan", "none"]).sum()
            )
            data_gaps = tie_nr - known_non_decisions
            pct = int((wins / decisions) * 100) if decisions > 0 else 0

            stats.append(
                {
                    "Opponent": opp,
                    "Mat": len(full),
                    "Won": wins,
                    "Lost": losses,
                    "Tie/NR": tie_nr,
                    "Win %": f"{pct}%",
                    "team_color": TEAM_COLORS.get(opp) or TEAM_COLORS.get("Visitors", "gray"),
                    "form_data": ReportBuilder._build_form_data_payload(full, team_name),
                    f"{team_name} Avg (1st)": ReportBuilder._get_avg_with_count(val[val["team_bat_1"] == team_name], "score_inn1"),
                    "Opp Avg (1st)": ReportBuilder._get_avg_with_count(val[val["team_bat_1"] != team_name], "score_inn1"),
                    "MATCH_IDS": ",".join(map(str, full["match_id"].unique().tolist())),
                    "cell_tones": {"Win %": ReportFormatter._tone_from_win_pct(pct)},
                    "highlight_flags": {"is_overall": False},
                    "derived_badges": [f"{pct}% win rate"],
                }
            )

        if not stats:
            # Fallback for empty results.
            return []

        df = pd.DataFrame(stats)

        overall_full = clean[clean["opponent"].isin(opponents) & count_mask]
        overall_val = valid[valid["opponent"].isin(opponents)]
        total_wins = len(overall_full[overall_full["winner"] == team_name])

        winner_lower = overall_full["winner"].astype(str).str.lower().str.strip()
        team_lower = team_name.lower().strip()
        is_loss = (winner_lower != team_lower) & (~winner_lower.isin(["tie", "no result", "nan", "none"]))
        total_losses = len(overall_full[is_loss])

        total_decisions = total_wins + total_losses
        total_tie_nr = len(overall_full) - total_decisions
        total_known_non_decisions = int(
            overall_full["winner"].astype(str).str.lower().str.strip().isin(["tie", "no result", "nan", "none"]).sum()
        )
        total_data_gaps = total_tie_nr - total_known_non_decisions
        total_pct = int((total_wins / total_decisions) * 100) if total_decisions > 0 else 0

        overall = pd.DataFrame(
            [
                {
                    "Opponent": "🔹 OVERALL",
                    "Mat": len(overall_full),
                    "Won": total_wins,
                    "Lost": total_losses,
                    "Tie/NR": total_tie_nr,
                    "Win %": f"{total_pct}%",
                    "team_color": None,
                    MATRIX_ROW_HOME_TEAM_COLOR: TEAM_COLORS.get(team_name) or TEAM_COLORS.get("Visitors", "gray"),
                    MATRIX_ROW_HOME_TEAM_NAME: team_name,
                    "form_data": ReportBuilder._build_form_data_payload(overall_full, team_name),
                    f"{team_name} Avg (1st)": ReportBuilder._get_avg_with_count(
                        overall_val[overall_val["team_bat_1"] == team_name], "score_inn1"
                    ),
                    "Opp Avg (1st)": ReportBuilder._get_avg_with_count(
                        overall_val[overall_val["team_bat_1"] != team_name], "score_inn1"
                    ),
                    "MATCH_IDS": ",".join(map(str, overall_full["match_id"].unique().tolist())),
                    "cell_tones": {"Win %": ReportFormatter._tone_from_win_pct(total_pct)},
                    "highlight_flags": {"is_overall": True},
                    "derived_badges": [f"{total_pct}% win rate", "Overall benchmark"],
                }
            ]
        )

        final_df = pd.concat([overall, df], ignore_index=True)
        return serialize_ui_records(final_df)

    @staticmethod
    def _index_player_stats(player_rows: list[PlayerStatRow]) -> dict[str, PlayerStatRow]:
        """
        Build a player-name keyed dictionary from flat player rows.
        """
        indexed: dict[str, PlayerStatRow] = {}
        for row in player_rows:
            if not isinstance(row, dict):
                continue
            player_name = str(row.get("Player", "")).strip()
            if not player_name:
                continue
            indexed[player_name] = row
        return indexed

    @staticmethod
    def _build_squad_comparison_payload(
        team_a_name: str,
        team_b_name: str,
        squad_a: list[str],
        squad_b: list[str],
        matrix_a: list[MatrixReportRow],
        matrix_b: list[MatrixReportRow],
        matchups_a: dict[str, list[ComparisonReportRow]],
        matchups_b: dict[str, list[ComparisonReportRow]],
        player_stats_a: list[PlayerStatRow],
        player_stats_b: list[PlayerStatRow],
    ) -> SquadComparisonPayload:
        """
        Build the regression payload contract used by compare_squads.
        """
        return {
            "SquadComparison": {
                team_a_name: squad_a,
                team_b_name: squad_b,
            },
            "TacticalMatrix": {
                team_a_name: matrix_a,
                team_b_name: matrix_b,
            },
            "Matchups": {
                team_a_name: matchups_a,
                team_b_name: matchups_b,
            },
            "PlayerStats": {
                team_a_name: ReportBuilder._index_player_stats(player_stats_a),
                team_b_name: ReportBuilder._index_player_stats(player_stats_b),
            },
        }

    @staticmethod
    def _build_team_form_records(recent: pd.DataFrame, team_name: str) -> list[TeamFormRow]:
        """
        Build team-form rows from a filtered recent matches DataFrame.
        """
        if recent is None or recent.empty:
            return []

        recent = recent.copy()
        bat1 = recent["team_bat_1"].eq(team_name)

        recent["Opponent"] = np.where(bat1, recent["team_bat_2"], recent["team_bat_1"])

        winner_text = recent["winner"].astype(str)
        winner_lower = winner_text.str.lower()
        is_level = (
            recent["score_inn1"].notna()
            & recent["score_inn2"].notna()
            & recent["score_inn1"].eq(recent["score_inn2"])
        )
        no_result_tokens = ["nan", "no result", "none"]

        recent["Result"] = np.select(
            [
                winner_text.eq(team_name),
                winner_lower.eq("tie") | (winner_lower.isin(no_result_tokens) & is_level),
                winner_lower.isin(no_result_tokens),
            ],
            ["WIN", "TIE", "NR"],
            default="LOSS",
        )

        team_scores = pd.to_numeric(np.where(bat1, recent["score_inn1"], recent["score_inn2"]), errors="coerce")
        opp_scores = pd.to_numeric(np.where(bat1, recent["score_inn2"], recent["score_inn1"]), errors="coerce")

        team_score_text = team_scores.astype("Int64").astype(str).replace("<NA>", "-")
        opp_score_text = opp_scores.astype("Int64").astype(str).replace("<NA>", "-")

        my_label = np.where(bat1, "(1st)", "(2nd)")
        opp_label = np.where(bat1, "(2nd)", "(1st)")

        recent["TeamScore"] = team_score_text + " " + my_label
        recent["OppScore"] = opp_score_text + " " + opp_label

        if "venue_id" in recent.columns:
            venue_val = recent["venue_id"].where(recent["venue_id"].notna(), recent.get("venue", ""))
        else:
            venue_val = recent.get("venue", "")
        recent["Venue"] = venue_val.astype(str).str.split("_").str[-1].str.title()

        recent["Date"] = pd.to_datetime(recent["start_date"], errors="coerce").dt.strftime("%Y-%m-%d").fillna("-")
        recent["RawResult"] = np.where(recent["Result"].ne("NR"), recent["Result"].str[0], "NR")
        recent["ResultTone"] = recent["Result"].map(
            {
                "WIN": "elite",
                "LOSS": "danger",
                "TIE": "caution",
                "NR": "caution",
            }
        ).fillna("muted")
        recent["ResultSymbol"] = recent["Result"].map(
            {
                "WIN": "W",
                "LOSS": "L",
                "TIE": "T",
                "NR": "-",
            }
        ).fillna("-")

        form_payload = ReportBuilder._build_form_data_payload(recent, team_name)

        records = recent[
            [
                "Date",
                "Opponent",
                "Venue",
                "Result",
                "TeamScore",
                "OppScore",
                "RawResult",
                "ResultTone",
                "ResultSymbol",
            ]
        ].to_dict("records")
        for row in records:
            row["form_data"] = form_payload
            row["highlight_flags"] = {"is_win": row.get("Result") == "WIN"}
            row["derived_badges"] = [f"Result: {row.get('Result', '-')}"]

        return records
