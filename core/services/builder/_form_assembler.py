import numpy as np
import pandas as pd

from core.interfaces.team_types import FormGuidePayload


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
