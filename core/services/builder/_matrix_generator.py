from typing import Callable

import numpy as np
import pandas as pd

from config.shared.team_colors import TEAM_COLORS
from core.interfaces.team_types import ComparisonReportRow, MATRIX_ROW_HOME_TEAM_COLOR, MATRIX_ROW_HOME_TEAM_NAME, MatrixReportRow
from core.services.match_filter_service import MatchFilterService
from core.services.report_builder import ReportBuilder
from core.services.report_formatter import ReportFormatter


class MatrixReportGenerator:
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
            tie_nr - known_non_decisions
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
        total_tie_nr - total_known_non_decisions
        total_pct = int((total_wins / total_decisions) * 100) if total_decisions > 0 else 0

        overall = pd.DataFrame(
            [
                {
                    "Opponent": "\U0001F539 OVERALL",
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
