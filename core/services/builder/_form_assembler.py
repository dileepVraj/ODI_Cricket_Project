import numpy as np
import pandas as pd

from core.interfaces.team_types import FormGuidePayload, TeamFormRow
from core.services.report_builder import ReportBuilder


class FormDataAssembler:
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
        is_level = (recent["score_inn1"].fillna(-1) == recent["score_inn2"].fillna(-2)).to_numpy(dtype=bool)

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
        ).to_numpy(dtype=bool, na_value=False)
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

        s1 = recent["score_inn1"].to_numpy(dtype="float64", na_value=float("nan"))
        s2 = recent["score_inn2"].to_numpy(dtype="float64", na_value=float("nan"))
        team_scores = pd.Series(np.where(bat1, s1, s2), index=recent.index, dtype="float64")
        opp_scores = pd.Series(np.where(bat1, s2, s1), index=recent.index, dtype="float64")

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
            row["form_summary"] = form_payload
            row["highlight_flags"] = {"is_win": row.get("Result") == "WIN"}
            row["derived_badges"] = [f"Result: {row.get('Result', '-')}"]

        return records
