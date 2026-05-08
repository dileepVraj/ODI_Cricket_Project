"""formats/odi/engines/player/_profile — PlayerEngineProfile: player profiles, phase stats, form sequences."""

from typing import List, Optional, Tuple, cast

import pandas as pd
import numpy as np
import re

from config.shared.venues import get_venue_aliases
from core.match_pack.transformers._form_parsers import (
    parse_last_10_bowling,
    parse_last_10_runs,
)
from core.interfaces.player_interface import (
    BattingStats, BowlingStats, ContextStats,
    PhaseBowlingRow, PhaseRunsRow, PlayerProfile, VsBowlingStyleRow,
)
from ._base import PlayerEngineBase, _PHASE_CANONICAL


def _get_batting_milestones(df: pd.DataFrame, rules: dict[str, object]) -> Tuple[int, int, int]:
    if df.empty:
        return 0, 0, 0
    match_sums = df.groupby('match_id')['runs_off_bat'].sum()
    player_rules = cast(dict[str, object], rules["player_rules"])
    centuries = (match_sums >= player_rules["milestone_century"]).sum()
    fifties = (
        (match_sums >= player_rules["milestone_half_century"])
        & (match_sums < player_rules["milestone_century"])
    ).sum()
    hs = match_sums.max() if not match_sums.empty else 0
    return centuries, fifties, hs


def _build_phase_conditions(
    over_num: pd.Series,
    rules: dict[str, object],
) -> tuple[List[pd.Series], List[str]]:
    phases_cfg = cast(dict[str, object], rules.get("phases", {}))
    conditions: List[pd.Series] = []
    labels: List[str] = []
    for phase_key, bounds in phases_cfg.items():
        if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
            continue
        start_over = pd.to_numeric(pd.Series([bounds[0]]), errors="coerce").iloc[0]
        end_over = pd.to_numeric(pd.Series([bounds[1]]), errors="coerce").iloc[0]
        if pd.isna(start_over) or pd.isna(end_over):
            continue
        canonical = _PHASE_CANONICAL.get(str(phase_key), str(phase_key))
        conditions.append(over_num.between(float(start_over), float(end_over)))
        labels.append(canonical)
    return conditions, labels


def _apply_ground_filter(df: pd.DataFrame, ground: Optional[str]) -> pd.DataFrame:
    if ground is None:
        return df
    if "venue" not in df.columns:
        return df
    aliases = get_venue_aliases(ground)
    if not aliases:
        return df
    return df[df["venue"].isin(aliases)].copy()


def _compute_phase_runs(raw_bat: pd.DataFrame, rules: dict[str, object]) -> List[PhaseRunsRow]:
    required_cols = {"over_num", "runs_off_bat", "player_dismissed"}
    if raw_bat.empty or not required_cols.issubset(raw_bat.columns):
        return []

    work = raw_bat.copy()
    over_num = pd.to_numeric(work["over_num"], errors="coerce")
    conditions, labels = _build_phase_conditions(over_num, rules)

    if not conditions:
        return []

    work["phase_bucket"] = np.select(conditions, labels, default="")
    work = work[work["phase_bucket"] != ""].copy()
    if work.empty:
        return []

    work["is_dismissal"] = work["player_dismissed"].notna().astype(int)
    agg = work.groupby("phase_bucket", sort=False).agg(
        total_runs=("runs_off_bat", "sum"),
        balls_faced=("runs_off_bat", "count"),
        dismissals=("is_dismissal", "sum"),
    ).reset_index()

    agg["avg_runs"] = np.where(
        agg["dismissals"] > 0,
        (agg["total_runs"] / agg["dismissals"]).round(2),
        agg["total_runs"].astype(float),
    )
    agg["strike_rate"] = np.where(
        agg["balls_faced"] > 0,
        (agg["total_runs"] / agg["balls_faced"] * 100).round(1),
        0.0,
    )

    return [
        PhaseRunsRow(
            phase=str(phase),
            total_runs=int(runs),
            balls_faced=int(balls),
            dismissals=int(dismissals),
            avg_runs=float(avg_runs),
            strike_rate=float(strike_rate),
        )
        for phase, runs, balls, dismissals, avg_runs, strike_rate in zip(
            agg["phase_bucket"],
            agg["total_runs"],
            agg["balls_faced"],
            agg["dismissals"],
            agg["avg_runs"],
            agg["strike_rate"],
        )
    ]


def _compute_phase_bowling(raw_bowl: pd.DataFrame, rules: dict[str, object]) -> List[PhaseBowlingRow]:
    required_cols = {"over_num", "runs_off_bat", "player_dismissed"}
    if raw_bowl.empty or not required_cols.issubset(raw_bowl.columns):
        return []

    work = raw_bowl.copy()
    over_num = pd.to_numeric(work["over_num"], errors="coerce")
    conditions, labels = _build_phase_conditions(over_num, rules)

    if not conditions:
        return []

    phase_order = list(dict.fromkeys(_PHASE_CANONICAL.values()))
    work["phase_bucket"] = np.select(conditions, labels, default="")
    work = work[work["phase_bucket"] != ""].copy()
    if work.empty:
        return []

    work["phase_bucket"] = pd.Categorical(
        work["phase_bucket"],
        categories=phase_order,
        ordered=True,
    )
    phase_bucket = work["phase_bucket"]
    runs_off_bat = pd.to_numeric(work["runs_off_bat"], errors="coerce").fillna(0)
    wickets = work["player_dismissed"].replace("", pd.NA).notna().astype(int)
    dot_balls = (runs_off_bat == 0).astype(int)
    boundary_balls = (runs_off_bat >= 4).astype(int)
    phase_runs = runs_off_bat.groupby(phase_bucket, observed=True, sort=True).sum()
    phase_balls = runs_off_bat.groupby(phase_bucket, observed=True, sort=True).count()
    phase_wickets = wickets.groupby(phase_bucket, observed=True, sort=True).sum()
    phase_dots = dot_balls.groupby(phase_bucket, observed=True, sort=True).sum()
    phase_boundaries = boundary_balls.groupby(phase_bucket, observed=True, sort=True).sum()
    sport_constants = cast(dict[str, object], rules["SPORT_CONSTANTS"])
    balls_per_over = float(sport_constants["balls_per_over"])
    percent_scale = float(sport_constants["percent_scale"])
    phase_rows: List[PhaseBowlingRow] = []
    for phase in phase_order:
        total_balls = int(phase_balls.get(phase, 0))
        if total_balls <= 0:
            continue
        total_runs = int(phase_runs.get(phase, 0))
        total_wickets = int(phase_wickets.get(phase, 0))
        total_dots = int(phase_dots.get(phase, 0))
        total_boundaries = int(phase_boundaries.get(phase, 0))
        phase_rows.append(
            PhaseBowlingRow(
                phase=phase,
                wickets=total_wickets,
                economy=round((total_runs / total_balls) * balls_per_over, 1) if total_balls > 0 else 0.0,
                average=round(total_runs / total_wickets, 1) if total_wickets > 0 else 0.0,
                strike_rate=round(total_balls / total_wickets, 1) if total_wickets > 0 else 0.0,
                dot_pct=round(total_dots / total_balls * percent_scale, 1) if total_balls > 0 else 0.0,
                boundary_pct=round(total_boundaries / total_balls * percent_scale, 1) if total_balls > 0 else 0.0,
            )
        )
    return phase_rows


class PlayerEngineProfile(PlayerEngineBase):
    def _get_batting_milestones(self, df: pd.DataFrame) -> Tuple[int, int, int]:
        return _get_batting_milestones(df, self.rules)

    def _player_exists(self, player_name: str) -> bool:
        _ = self.rules
        return player_name in self.player_df['player'].values

    def _build_phase_conditions(self, over_num: pd.Series) -> tuple[List[pd.Series], List[str]]:
        return _build_phase_conditions(over_num, self.rules)

    def _compute_phase_runs(self, raw_bat: pd.DataFrame) -> List[PhaseRunsRow]:
        return _compute_phase_runs(raw_bat, self.rules)

    def _compute_phase_bowling(self, raw_bowl: pd.DataFrame) -> List[PhaseBowlingRow]:
        return _compute_phase_bowling(raw_bowl, self.rules)

    def _compute_vs_bowling_style(self, raw_bat: pd.DataFrame) -> List[VsBowlingStyleRow]:
        _ = self.rules
        required_cols = {"bowler", "runs_off_bat", "player_dismissed"}
        if raw_bat.empty or not required_cols.issubset(raw_bat.columns):
            return []

        work = raw_bat.copy()
        work["style"] = work["bowler"].map(self.style_map).fillna("Other")
        work["is_dismissal"] = work["player_dismissed"].notna().astype(int)
        agg = work.groupby("style", sort=False).agg(
            total_runs=("runs_off_bat", "sum"),
            balls_faced=("runs_off_bat", "count"),
            dismissals=("is_dismissal", "sum"),
        ).reset_index()

        agg["avg_runs"] = np.where(
            agg["dismissals"] > 0,
            (agg["total_runs"] / agg["dismissals"]).round(2),
            agg["total_runs"].astype(float),
        )
        agg["strike_rate"] = np.where(
            agg["balls_faced"] > 0,
            (agg["total_runs"] / agg["balls_faced"] * 100).round(1),
            0.0,
        )
        agg = agg.sort_values("style").reset_index(drop=True)

        return [
            VsBowlingStyleRow(
                style=str(style),
                total_runs=int(runs),
                balls_faced=int(balls),
                dismissals=int(dismissals),
                avg_runs=float(avg_runs),
                strike_rate=float(strike_rate),
            )
            for style, runs, balls, dismissals, avg_runs, strike_rate in zip(
                agg["style"],
                agg["total_runs"],
                agg["balls_faced"],
                agg["dismissals"],
                agg["avg_runs"],
                agg["strike_rate"],
            )
        ]

    def _apply_ground_filter(self, df: pd.DataFrame, ground: Optional[str]) -> pd.DataFrame:
        return _apply_ground_filter(df, ground)

    def _collect_profile_sections(
        self,
        player_name: str,
        raw_balls_df: Optional[pd.DataFrame],
        years: Optional[int],
        ground: Optional[str],
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        _ = self.rules
        raw_bat = pd.DataFrame()
        if (
            isinstance(raw_balls_df, pd.DataFrame)
            and not raw_balls_df.empty
            and "striker" in raw_balls_df.columns
        ):
            raw_bat = raw_balls_df[raw_balls_df["striker"] == player_name].copy()
            if years is not None and "start_date" in raw_bat.columns:
                cutoff_date = self._get_reference_date() - pd.DateOffset(
                    years=self._get_years_back(years)
                )
                start_dates = pd.to_datetime(raw_bat["start_date"], errors="coerce")
                raw_bat = raw_bat[start_dates >= cutoff_date].copy()

        raw_bat_ground = self._apply_ground_filter(raw_bat, ground) if not raw_bat.empty else raw_bat

        raw_bowl = pd.DataFrame()
        if (
            isinstance(raw_balls_df, pd.DataFrame)
            and not raw_balls_df.empty
            and "bowler" in raw_balls_df.columns
        ):
            raw_bowl = raw_balls_df[raw_balls_df["bowler"] == player_name].copy()
            if years is not None and "start_date" in raw_bowl.columns:
                cutoff_bowl = self._get_reference_date() - pd.DateOffset(
                    years=self._get_years_back(years)
                )
                bowl_dates = pd.to_datetime(raw_bowl["start_date"], errors="coerce")
                raw_bowl = raw_bowl[bowl_dates >= cutoff_bowl].copy()

        raw_bowl_ground = (
            self._apply_ground_filter(raw_bowl, ground)
            if not raw_bowl.empty
            else raw_bowl
        )
        return raw_bat_ground, raw_bowl_ground

    def get_player_profile(
        self,
        player_name: str,
        opposition: Optional[str] = None,
        venue_id: Optional[str] = None,
        years: Optional[int] = None,
        raw_balls_df: Optional[pd.DataFrame] = None,
    ) -> Optional[PlayerProfile]:
        """
        Headless API: Fetches player profile data.
        """
        if not self._player_exists(player_name):
            return None
        
        years_back = self._get_years_back(years)
        cutoff_date = self._get_reference_date() - pd.DateOffset(years=years_back)
        p_stats = self.player_df[self.player_df['player'] == player_name].copy()
        player_context_types = cast(dict[str, object], self.rules["player_context_types"])
        player_rules = cast(dict[str, object], self.rules["player_rules"])
        sport_constants = cast(dict[str, object], self.rules["SPORT_CONSTANTS"])
        
        # BATTING
        career_bat = p_stats[
            (p_stats['context'] == player_context_types["vs_team"])
            & (p_stats['role'] == player_context_types["batting"])
        ].copy()
        bat_stats = BattingStats(0, 0, 0.0, 0.0, 0, 0, 0, [])
        if not career_bat.empty:
            runs = int(career_bat['runs'].sum())
            inns = int(career_bat['innings'].sum())
            outs = int(career_bat['dismissals'].sum())
            balls = int(career_bat['balls'].sum())
            avg = round(runs / outs, player_rules["stat_precision_avg"]) if outs > 0 else runs
            sr = round((runs / balls) * sport_constants["percent_scale"], 1) if balls > 0 else 0.0
            
            raw_bat = pd.DataFrame()
            if isinstance(raw_balls_df, pd.DataFrame) and not raw_balls_df.empty:
                raw_bat = raw_balls_df[raw_balls_df['striker'] == player_name].copy()
            
            if not raw_bat.empty:
                 if 'start_date' in raw_bat.columns:
                     raw_bat['start_date'] = pd.to_datetime(raw_bat['start_date'], errors='coerce')
                 raw_bat = raw_bat[raw_bat['start_date'] >= cutoff_date]
                 c100, c50, hs = self._get_batting_milestones(raw_bat)
                 bat_stats = BattingStats(inns, runs, avg, sr, c100, c50, hs, [])

        # BOWLING
        career_bowl = p_stats[
            (p_stats['context'] == player_context_types["vs_team"])
            & (p_stats['role'] == player_context_types["bowling"])
        ].copy()
        bowl_stats = None
        if not career_bowl.empty:
            b_runs = int(career_bowl['runs'].sum())
            b_balls = int(career_bowl['balls'].sum())
            b_wkts = int(career_bowl['dismissals'].sum())
            if b_balls > player_rules["profile_sr_min_balls"]:
                b_avg = round(b_runs / b_wkts, player_rules["stat_precision_avg"]) if b_wkts > 0 else 0.0
                b_econ = round((b_runs / b_balls) * sport_constants["balls_per_over"], player_rules["stat_precision_rate"]) if b_balls > 0 else 0.0
                bowl_stats = BowlingStats(0, b_wkts, b_avg, b_econ, None, [])

        # CONTEXT
        vs_opponent_context = None
        if opposition and opposition != player_context_types["all"]:
            opp_bat = p_stats[
                (p_stats['context'] == player_context_types["vs_team"])
                & (p_stats['role'] == player_context_types["batting"])
                & (p_stats['opponent'] == opposition)
            ]
            if not opp_bat.empty:
                r = int(opp_bat['runs'].sum())
                i = int(opp_bat['innings'].sum())
                o = int(opp_bat['dismissals'].sum())
                b = int(opp_bat['balls'].sum())
                av = round(r / o, player_rules["stat_precision_avg"]) if o > 0 else r
                sr = round((r / b) * sport_constants["percent_scale"], 1) if b > 0 else 0.0
                vs_opponent_context = ContextStats(batting=BattingStats(i, r, av, sr, 0, 0, 0, []), bowling=None)

        venue_context = None
        if venue_id:
            aliases = get_venue_aliases(venue_id)
            ven_pattern = '|'.join([re.escape(v) for v in aliases])
            ven_bat = p_stats[
                (p_stats['context'] == player_context_types["at_venue"])
                & (p_stats['role'] == player_context_types["batting"])
                & (p_stats['opponent'].str.contains(ven_pattern, case=False, regex=True))
            ]
            if not ven_bat.empty:
                r = int(ven_bat['runs'].sum())
                i = int(ven_bat['innings'].sum())
                o = int(ven_bat['dismissals'].sum())
                b = int(ven_bat['balls'].sum())
                av = round(r / o, player_rules["stat_precision_avg"]) if o > 0 else r
                sr = round((r / b) * sport_constants["percent_scale"], 1) if b > 0 else 0.0
                venue_context = ContextStats(batting=BattingStats(i, r, av, sr, 0, 0, 0, []), bowling=None)

        return PlayerProfile(
            name=player_name,
            role=self._get_player_role(player_name),
            batting=bat_stats,
            bowling=bowl_stats,
            venue_stats=venue_context,
            vs_opponent_stats=vs_opponent_context
        )

    def analyze_player_profile(
        self,
        player_name: str,
        opposition: Optional[str] = None,
        venue_id: Optional[str] = None,
        active_bowlers: Optional[List[str]] = None,
        years: Optional[int] = None,
        raw_balls_df: Optional[pd.DataFrame] = None,
        country: Optional[str] = None,
        ground: Optional[str] = None,
    ) -> Optional[PlayerProfile]:
        """
        Headless API: Context-Aware Player Profile retrieval.
        """
        _ = self.rules
        _ = (active_bowlers, country)
        if not self._player_exists(player_name):
            return None

        profile = self.get_player_profile(
            player_name,
            opposition,
            venue_id,
            years,
            raw_balls_df=raw_balls_df,
        )
        if profile is None:
            return None

        profile.batting.last_10_runs = parse_last_10_runs(profile.batting.form_last_10)
        raw_bat_ground, raw_bowl_ground = self._collect_profile_sections(
            player_name,
            raw_balls_df,
            years,
            ground,
        )
        profile.phase_runs = self._compute_phase_runs(raw_bat_ground)
        profile.vs_bowling_style = self._compute_vs_bowling_style(raw_bat_ground)
        profile.phase_bowling = self._compute_phase_bowling(raw_bowl_ground)
        profile.last_10_bowling = (
            parse_last_10_bowling(profile.bowling.form_last_10)
            if profile.bowling is not None
            else []
        )
        return profile
