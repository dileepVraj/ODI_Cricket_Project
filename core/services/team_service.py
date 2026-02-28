import logging

import pandas as pd


logger = logging.getLogger("CricketAnalyzer")

class TeamService:
    """
    Industry Standard Team Service.
    Handles team-specific logic, data normalization, and specialized adapters.
    """

    @classmethod
    def ensure_phase_total_runs(cls, df: pd.DataFrame | None) -> pd.DataFrame | None:
        """
        Normalizes phase stats by ensuring 'total_runs' column exists.
        Some data sources provide partitioned runs but not the sum.
        """
        try:
            if df is None or getattr(df, "empty", False):
                return df
            cols = getattr(df, "columns", [])
            if "total_runs" not in cols and all(
                c in cols for c in ("pp_runs", "mid_runs", "dth_runs")
            ):
                df = df.copy()
                df["total_runs"] = (
                    df["pp_runs"].fillna(0)
                    + df["mid_runs"].fillna(0)
                    + df["dth_runs"].fillna(0)
                )
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            logger.warning("Non-fatal team phase normalization issue: %s", exc)
            return df
        return df
