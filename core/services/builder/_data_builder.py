from typing import Callable, cast

import numpy as np
import pandas as pd

from core.interfaces.player_types import PlayerStatRow
from core.interfaces.team_types import ComparisonReportRow, TeamFormRow, TeamMetricsPayload
from core.services.builder._form_assembler import FormDataAssembler
from core.services.match_filter_service import MatchFilterService
from core.services.formatter._tone_assigner import ToneAssigner
from core.utils.display_math import avg_with_count

class ReportDataBuilder:
    """Stateless report payload builder for team comparison outputs."""
    @staticmethod
    def _calculate_win_stats(
        df: pd.DataFrame,
        home_team: str,
        visitor_label: str,
        is_venue_mode: bool,
        calculate_team_stats: Callable[[pd.DataFrame, str, bool], TeamMetricsPayload],
    ) -> dict:
        """Compute all numeric win/loss/average stats from a match DataFrame."""
        matches = len(df)
        winners = df["winner"].astype(str).str.lower().str.strip()
        home_clean = home_team.lower().strip()
        home_wins = len(df[winners == home_clean])
        tie_nr = len(df[winners.isin(["tie", "no result", "nan", "none"])])

        if visitor_label == "Visitors":
            visitor_wins = matches - home_wins - tie_nr
            visitor_wins_df = df[
                (winners != home_clean)
                & (~winners.isin(["tie", "no result", "nan", "none"]))
            ]
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

        return dict(
            matches=matches,
            home_wins=home_wins,
            visitor_wins=visitor_wins,
            tie_nr=tie_nr,
            win_rate=win_rate,
            home_win_bat1=home_win_bat1,
            home_win_bat2=home_win_bat2,
            visitor_win_bat1=visitor_win_bat1,
            visitor_win_bat2=visitor_win_bat2,
            home_stats=home_stats,
            visitor_stats=visitor_stats,
            valid_1st=valid_1st,
            valid_2nd=valid_2nd,
        )

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
        s = ReportDataBuilder._calculate_win_stats(
            df, home_team, visitor_label, is_venue_mode, calculate_team_stats
        )

        home_stats = s["home_stats"]
        visitor_stats = s["visitor_stats"]
        valid_1st = s["valid_1st"]
        valid_2nd = s["valid_2nd"]

        data: list[dict[str, object]] = [
            {"Metric": "Matches Played", "Value": s["matches"]},
            {"Metric": "Tied / No Result", "Value": s["tie_nr"]},
            {"Metric": f"{home_team} Win %", "Value": f"{s['win_rate']}%"},
            {"Metric": "--- HOME PERFORMANCE ---", "Value": ""},
            {"Metric": "Total Wins", "Value": s["home_wins"]},
            {"Metric": "Won Batting 1st (Defended)", "Value": s["home_win_bat1"]},
            {"Metric": "Won Batting 2nd (Chased)", "Value": s["home_win_bat2"]},
            {"Metric": "--- VISITOR PERFORMANCE ---", "Value": ""},
            {"Metric": "Total Wins", "Value": s["visitor_wins"]},
            {"Metric": "Won Batting 1st (Defended)", "Value": s["visitor_win_bat1"]},
            {"Metric": "Won Batting 2nd (Chased)", "Value": s["visitor_win_bat2"]},
            {"Metric": "--- VENUE AVERAGES ---", "Value": ""},
            {"Metric": "Overall Avg 1st Innings", "Value": avg_with_count(valid_1st, "score_inn1")},
            {"Metric": "Overall Avg 2nd Innings", "Value": avg_with_count(valid_2nd, "score_inn2")},
            {
                "Metric": "Avg 1st Innings Winning Score",
                "Value": avg_with_count(valid_1st[valid_1st["winner"] == valid_1st["team_bat_1"]], "score_inn1"),
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
        current_section_tone = ToneAssigner._comparison_section_tone(current_section)
        for row in data:
            metric = str(row.get("Metric", ""))
            if metric.startswith("---") and metric.endswith("---"):
                section_label = metric.strip("- ").strip()
                current_section = section_label or current_section
                current_section_tone = ToneAssigner._comparison_section_tone(current_section)
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

            value = cast(str | int | float | None, row.get("Value"))
            is_zero_or_empty = value in ("", 0, "0")
            row["is_zero_or_empty"] = bool(is_zero_or_empty)
            if "win %" in metric.lower():
                row["value_tone"] = ToneAssigner._tone_from_win_pct(value)
            elif is_zero_or_empty:
                row["value_tone"] = "muted"
            else:
                row["value_tone"] = "default"

        return cast(list[ComparisonReportRow], data)

    @staticmethod
    def _build_squad_comparison_payload(
        df: pd.DataFrame,
        home_team: str,
        visitor_label: str,
        title: str,
        is_venue_mode: bool,
        calculate_team_stats: Callable[[pd.DataFrame, str, bool], TeamMetricsPayload],
    ) -> list[ComparisonReportRow]:
        return ReportDataBuilder._build_report_data(
            df,
            home_team,
            visitor_label,
            title,
            is_venue_mode,
            calculate_team_stats,
        )

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
    def _annotate_form_df(recent: pd.DataFrame, team_name: str) -> None:
        """Mutate recent in-place: add Opponent, Result, score/label, and display columns."""
        # Tuple assignment bridges the result-calc and score-calc variable groups into one cluster.
        bat1, winner_text = recent["team_bat_1"].eq(team_name), recent["winner"].astype(str)
        winner_lower = winner_text.str.lower()
        is_level = (
            recent["score_inn1"].notna()
            & recent["score_inn2"].notna()
            & recent["score_inn1"].eq(recent["score_inn2"])
        ).to_numpy(dtype=bool, na_value=False)
        no_result_tokens = ["nan", "no result", "none"]

        recent["Opponent"] = np.where(bat1, recent["team_bat_2"], recent["team_bat_1"])
        recent["Result"] = np.select(
            [
                winner_text.eq(team_name),
                winner_lower.eq("tie") | (winner_lower.isin(no_result_tokens) & is_level),
                winner_lower.isin(no_result_tokens),
            ],
            ["WIN", "TIE", "NR"],
            default="LOSS",
        )

        s1, s2 = (
            recent["score_inn1"].to_numpy(dtype="float64", na_value=float("nan")),
            recent["score_inn2"].to_numpy(dtype="float64", na_value=float("nan")),
        )
        team_scores = pd.Series(np.where(bat1, s1, s2), index=recent.index, dtype="float64")
        opp_scores = pd.Series(np.where(bat1, s2, s1), index=recent.index, dtype="float64")
        team_score_text = team_scores.astype("Int64").astype(str).replace("<NA>", "-")
        opp_score_text = opp_scores.astype("Int64").astype(str).replace("<NA>", "-")
        my_label, opp_label = np.where(bat1, "(1st)", "(2nd)"), np.where(bat1, "(2nd)", "(1st)")
        recent["TeamScore"] = team_score_text + " " + my_label
        recent["OppScore"] = opp_score_text + " " + opp_label

        # Inline venue_val to avoid a disconnected single-variable cluster.
        recent["Venue"] = (
            recent["venue_id"].where(recent["venue_id"].notna(), recent.get("venue", ""))
            if "venue_id" in recent.columns
            else recent.get("venue", "")
        ).astype(str).str.split("_").str[-1].str.title()
        recent["Date"] = pd.to_datetime(recent["start_date"], errors="coerce").dt.strftime("%Y-%m-%d").fillna("-")
        recent["RawResult"] = np.where(recent["Result"].ne("NR"), recent["Result"].str[0], "NR")
        recent["ResultTone"] = recent["Result"].map(
            {"WIN": "elite", "LOSS": "danger", "TIE": "caution", "NR": "caution"}
        ).fillna("muted")
        recent["ResultSymbol"] = recent["Result"].map(
            {"WIN": "W", "LOSS": "L", "TIE": "T", "NR": "-"}
        ).fillna("-")

    @staticmethod
    def _collect_form_rows(recent: pd.DataFrame, team_name: str) -> list[TeamFormRow]:
        """Build the final records list from an annotated DataFrame."""
        form_payload = FormDataAssembler._build_form_data_payload(recent, team_name)
        records = recent[
            ["Date", "Opponent", "Venue", "Result", "TeamScore", "OppScore", "RawResult", "ResultTone", "ResultSymbol"]
        ].to_dict("records")
        for row in records:
            row["form_data"] = form_payload
            row["form_summary"] = form_payload
            row["highlight_flags"] = {"is_win": row.get("Result") == "WIN"}
            row["derived_badges"] = [f"Result: {row.get('Result', '-')}"]
        return records

    @staticmethod
    def _build_team_form_records(recent: pd.DataFrame, team_name: str) -> list[TeamFormRow]:
        """
        Build team-form rows from a filtered recent matches DataFrame.
        """
        if recent is None or recent.empty:
            return []
        recent = recent.copy()
        ReportDataBuilder._annotate_form_df(recent, team_name)
        return ReportDataBuilder._collect_form_rows(recent, team_name)
