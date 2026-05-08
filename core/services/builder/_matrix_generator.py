from typing import Callable

import numpy as np
import pandas as pd

from config.shared.team_colors import TEAM_COLORS
from core.interfaces.team_types import (
    ComparisonReportRow,
    MATRIX_ROW_HOME_TEAM_COLOR,
    MATRIX_ROW_HOME_TEAM_NAME,
    MATRIX_ROW_OVERALL_LABEL,
    MatrixReportRow,
)
from core.services.builder._form_assembler import FormDataAssembler
from core.services.match_filter_service import MatchFilterService
from core.services.formatter._tone_assigner import ToneAssigner
from core.utils.display_math import avg_with_count


class MatrixReportGenerator:
    @staticmethod
    def _team_color(team: str) -> str:
        """Config facade -- resolves team colour without exposing config domain to the main method."""
        return TEAM_COLORS.get(team) or TEAM_COLORS.get("Visitors", "gray")

    @staticmethod
    def _compute_opponent_stats(
        full: pd.DataFrame,
        team_name: str,
        opp: str,
    ) -> dict:
        """Return raw numeric win/loss/pct stats for one opponent.

        No formatting. All values are plain ints.
        """
        wins = len(full[full["winner"] == team_name])
        losses = len(full[full["winner"] == opp])
        decisions = wins + losses
        tie_nr = len(full) - decisions
        pct = int((wins / decisions) * 100) if decisions > 0 else 0
        return dict(wins=wins, losses=losses, decisions=decisions, tie_nr=tie_nr, pct=pct)

    @staticmethod
    def _compute_overall_stats(
        overall_full: pd.DataFrame,
        team_name: str,
    ) -> dict:
        """Return raw numeric win/loss/pct stats for the overall row.

        No formatting. All values are plain ints.
        """
        total_wins = len(overall_full[overall_full["winner"] == team_name])

        winner_lower = overall_full["winner"].astype(str).str.lower().str.strip()
        team_lower = team_name.lower().strip()
        is_loss = (winner_lower != team_lower) & (
            ~winner_lower.isin(["tie", "no result", "nan", "none"])
        )
        total_losses = len(overall_full[is_loss])

        total_decisions = total_wins + total_losses
        total_tie_nr = len(overall_full) - total_decisions
        total_pct = int((total_wins / total_decisions) * 100) if total_decisions > 0 else 0
        return dict(
            total_wins=total_wins,
            total_losses=total_losses,
            total_decisions=total_decisions,
            total_tie_nr=total_tie_nr,
            total_pct=total_pct,
        )

    @staticmethod
    def _assemble_opponent_row(
        opp: str,
        numeric: dict,
        val: pd.DataFrame,
        full: pd.DataFrame,
        team_name: str,
    ) -> dict:
        """Map numeric stats for one opponent into the display row schema."""
        return {
            "Opponent": opp,
            "Mat": len(full),
            "Won": numeric["wins"],
            "Lost": numeric["losses"],
            "Tie/NR": numeric["tie_nr"],
            "Win %": f"{numeric['pct']}%",
            "team_color": MatrixReportGenerator._team_color(opp),
            "form_data": FormDataAssembler._build_form_data_payload(full, team_name),
            f"{team_name} Avg (1st)": avg_with_count(
                val[val["team_bat_1"] == team_name], "score_inn1"
            ),
            "Opp Avg (1st)": avg_with_count(
                val[val["team_bat_1"] != team_name], "score_inn1"
            ),
            "MATCH_IDS": ",".join(map(str, full["match_id"].unique().tolist())),
            "cell_tones": {"Win %": ToneAssigner._tone_from_win_pct(numeric["pct"])},
            "highlight_flags": {"is_overall": False},
            "derived_badges": [f"{numeric['pct']}% win rate"],
        }

    @staticmethod
    def _assemble_overall_row(
        team_name: str,
        numeric: dict,
        overall_val: pd.DataFrame,
        overall_full: pd.DataFrame,
    ) -> dict:
        """Map overall numeric stats into the display row schema."""
        return {
            "Opponent": MATRIX_ROW_OVERALL_LABEL,
            "Mat": len(overall_full),
            "Won": numeric["total_wins"],
            "Lost": numeric["total_losses"],
            "Tie/NR": numeric["total_tie_nr"],
            "Win %": f"{numeric['total_pct']}%",
            "team_color": None,
            MATRIX_ROW_HOME_TEAM_COLOR: MatrixReportGenerator._team_color(team_name),
            MATRIX_ROW_HOME_TEAM_NAME: team_name,
            "form_data": FormDataAssembler._build_form_data_payload(overall_full, team_name),
            f"{team_name} Avg (1st)": avg_with_count(
                overall_val[overall_val["team_bat_1"] == team_name], "score_inn1"
            ),
            "Opp Avg (1st)": avg_with_count(
                overall_val[overall_val["team_bat_1"] != team_name], "score_inn1"
            ),
            "MATCH_IDS": ",".join(map(str, overall_full["match_id"].unique().tolist())),
            "cell_tones": {"Win %": ToneAssigner._tone_from_win_pct(numeric["total_pct"])},
            "highlight_flags": {"is_overall": True},
            "derived_badges": [f"{numeric['total_pct']}% win rate", "Overall benchmark"],
        }

    @staticmethod
    def _generate_matrix_report(
        matches: pd.DataFrame,
        team_name: str,
        title: str,
        is_away: bool,
        apply_smart_filters: Callable[[pd.DataFrame], pd.DataFrame],
        serialize_ui_records: Callable[[pd.DataFrame], list[MatrixReportRow] | list[ComparisonReportRow]],
    ) -> list[MatrixReportRow] | list[ComparisonReportRow]:
        """
        Generate a multi-opponent matrix report (row per opponent + overall row).
        """
        clean = apply_smart_filters(matches)

        # Vectorized opponent detection.
        clean["opponent"] = np.where(clean["team_bat_1"] == team_name, clean["team_bat_2"], clean["team_bat_1"])

        count_mask = ~MatchFilterService.get_excluded_no_result_mask(clean)
        valid_2nd_mask = MatchFilterService.get_valid_matches_mask(clean)
        valid_1st_mask = valid_2nd_mask | MatchFilterService.get_excluded_short_second_mask(clean)
        valid = clean[valid_1st_mask]

        # Sort opponents alphabetically for stable matrix row ordering across callers.
        opponents = sorted([opp for opp in clean["opponent"].unique() if pd.notna(opp) and opp != team_name])

        rows = []
        for opp in opponents:
            full = clean[(clean["opponent"] == opp) & count_mask]
            if full.empty:
                continue

            val = valid[valid["opponent"] == opp]
            numeric = MatrixReportGenerator._compute_opponent_stats(full, team_name, opp)
            rows.append(
                MatrixReportGenerator._assemble_opponent_row(opp, numeric, val, full, team_name)
            )

        if not rows:
            # Fallback for empty results.
            return []

        overall_full = clean[clean["opponent"].isin(opponents) & count_mask]
        overall_val = valid[valid["opponent"].isin(opponents)]
        overall_numeric = MatrixReportGenerator._compute_overall_stats(overall_full, team_name)
        overall_row = MatrixReportGenerator._assemble_overall_row(
            team_name, overall_numeric, overall_val, overall_full
        )

        final_df = pd.concat([pd.DataFrame([overall_row]), pd.DataFrame(rows)], ignore_index=True)
        return serialize_ui_records(final_df)
