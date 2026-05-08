"""
DataAccess - all public data retrieval methods for cricket engines.
Inherits connection and schema verification from DALConnection.
Each method returns a pandas DataFrame.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd

from core.data_access._connection import DALConnection
from core.data_access._filters import (
    append_balls_venue_filter,
    append_matches_team_filter,
    append_matches_venue_filter,
)
from core.data_access._normalizers import (
    hydrate_missing_match_teams,
    normalize_match_innings_fields,
)


class DataAccess(DALConnection):
    """
    Provides high-level data retrieval methods for cricket engines.
    Each method returns a pandas DataFrame.
    """

    def get_player_stats(self) -> pd.DataFrame:
        if not self.has_table("player_stats"):
            return pd.DataFrame()
        return self.con.execute("SELECT * FROM player_stats").df()

    def get_player_batting_stats(self) -> pd.DataFrame:
        if not self.has_table("player_batting_stats"):
            return pd.DataFrame()
        return self.con.execute("SELECT * FROM player_batting_stats").df()

    def get_player_bowling_stats(self) -> pd.DataFrame:
        if not self.has_table("player_bowling_stats"):
            return pd.DataFrame()
        return self.con.execute("SELECT * FROM player_bowling_stats").df()

    def get_phase_stats(self) -> pd.DataFrame:
        if not self.has_table("phase_stats"):
            return pd.DataFrame()
        return self.con.execute("SELECT * FROM phase_stats").df()

    def get_player_metadata(self) -> pd.DataFrame:
        if not self.has_table("player_metadata"):
            return pd.DataFrame()
        return self.con.execute("SELECT * FROM player_metadata").df()

    def get_squads(self) -> pd.DataFrame:
        if not self.has_table("squads"):
            return pd.DataFrame()
        return self.con.execute("SELECT * FROM squads").df()

    def get_matches(
        self,
        team_a: Optional[str] = None,
        team_b: Optional[str] = None,
        venue: Optional[str] = None,
        venue_id: Optional[str] = None,
        years_back: Optional[int] = None,
        country: Optional[str] = None,
        match_ids: Optional[List[Any]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        conditions: list[str] = []
        params: list[Any] = []

        if team_a:
            append_matches_team_filter(conditions, params, team_a)

        if team_b:
            append_matches_team_filter(conditions, params, team_b)

        target_v = venue if venue else venue_id
        if target_v:
            append_matches_venue_filter(conditions, params, target_v, self.match_cols)

        if match_ids:
            placeholders = ",".join(["?"] * len(match_ids))
            conditions.append(f"match_id IN ({placeholders})")
            params.extend(match_ids)

        if years_back:
            cutoff = datetime.now() - timedelta(days=years_back * 365)
            conditions.append("start_date >= ?")
            params.append(cutoff.strftime("%Y-%m-%d"))

        if country:
            conditions.append("country = ?")
            params.append(country)

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        limit_clause = f" LIMIT {limit}" if limit is not None else ""
        query = f"SELECT * FROM matches {where_clause} ORDER BY start_date DESC{limit_clause}"
        result_df = self.con.execute(query, params).df()
        result_df = hydrate_missing_match_teams(result_df, self.con)
        return normalize_match_innings_fields(result_df)

    def get_balls(
        self,
        match_ids: Optional[List[Any]] = None,
        venue: Optional[str] = None,
        venue_id: Optional[str] = None,
        batting_team: Optional[str] = None,
        bowling_team: Optional[str] = None,
        striker: Optional[str] = None,
        bowler: Optional[str] = None,
        players: Optional[List[str]] = None,
        innings: Optional[int] = None,
        phase: Optional[str] = None,
        years_back: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        conditions: list[str] = []
        params: list[Any] = []

        if match_ids:
            placeholders = ",".join(["?"] * len(match_ids))
            conditions.append(f"match_id IN ({placeholders})")
            params.extend(match_ids)

        target_v = venue if venue else venue_id
        if target_v:
            append_balls_venue_filter(conditions, params, target_v, self.ball_cols)

        if batting_team:
            conditions.append("batting_team = ?")
            params.append(batting_team)

        if bowling_team:
            conditions.append("bowling_team = ?")
            params.append(bowling_team)

        if striker:
            conditions.append("striker = ?")
            params.append(striker)

        if bowler:
            conditions.append("bowler = ?")
            params.append(bowler)

        if players:
            placeholders = ",".join(["?"] * len(players))
            conditions.append(f"(striker IN ({placeholders}) OR bowler IN ({placeholders}))")
            params.extend(players + players)

        if innings:
            conditions.append("innings = ?")
            params.append(innings)

        if phase:
            conditions.append("phase = ?")
            params.append(phase)

        if years_back:
            cutoff = datetime.now() - timedelta(days=years_back * 365)
            conditions.append("start_date >= ?")
            params.append(cutoff.strftime("%Y-%m-%d"))

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        limit_clause = f" LIMIT {limit}" if limit is not None else ""
        query = f"SELECT * FROM balls {where_clause}{limit_clause}"
        return self.con.execute(query, params).df()

    def get_venue_summary(self, venue_id: str, years_back: Optional[int] = None) -> pd.DataFrame:
        conditions: list[str] = []
        params: list[Any] = []

        append_matches_venue_filter(conditions, params, venue_id, self.match_cols)

        if years_back:
            cutoff = datetime.now() - timedelta(days=years_back * 365)
            conditions.append("start_date >= ?")
            params.append(cutoff.strftime("%Y-%m-%d"))

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        return self.con.execute(
            f"""
            SELECT
                COUNT(*) as matches,
                ROUND(AVG(TRY_CAST(score_inn1 AS DOUBLE)), 1) as avg_score_1,
                ROUND(AVG(TRY_CAST(score_inn2 AS DOUBLE)), 1) as avg_score_2
            FROM matches
            {where_clause}
            """,
            params,
        ).df()

    def get_h2h_summary(
        self,
        team_a: str,
        team_b: str,
        venue_id: Optional[str] = None,
        years_back: Optional[int] = None,
    ) -> pd.DataFrame:
        conditions: list[str] = []
        params: list[Any] = []
        append_matches_team_filter(conditions, params, team_a)
        append_matches_team_filter(conditions, params, team_b)

        if venue_id:
            append_matches_venue_filter(conditions, params, venue_id, self.match_cols)

        if years_back:
            cutoff = datetime.now() - timedelta(days=years_back * 365)
            conditions.append("start_date >= ?")
            params.append(cutoff.strftime("%Y-%m-%d"))

        where_clause = "WHERE " + " AND ".join(conditions)

        return self.con.execute(
            f"""
            SELECT
                winner,
                COUNT(*) as wins,
                ROUND(AVG(TRY_CAST(score_inn1 AS DOUBLE)), 1) as avg_score_1,
                ROUND(AVG(TRY_CAST(score_inn2 AS DOUBLE)), 1) as avg_score_2
            FROM matches
            {where_clause}
            GROUP BY winner
            """,
            params,
        ).df()

    def get_player_career_summary(self, player_name: str) -> pd.DataFrame:
        batting = self.con.execute(
            """
            SELECT
                'batting' as role,
                COUNT(DISTINCT match_id) as innings,
                SUM(runs_off_bat) as runs,
                COUNT(*) as balls,
                SUM(CASE WHEN wicket_type IS NOT NULL AND player_dismissed = ? THEN 1 ELSE 0 END) as outs
            FROM balls
            WHERE striker = ?
            """,
            [player_name, player_name],
        ).df()

        bowling = self.con.execute(
            """
            SELECT
                'bowling' as role,
                COUNT(DISTINCT match_id) as innings,
                SUM(runs_off_bat + extras - (CASE WHEN wides > 0 OR noballs > 0 THEN extras ELSE 0 END)) as runs,
                COUNT(CASE WHEN wides = 0 AND noballs = 0 THEN 1 END) as balls,
                SUM(CASE WHEN wicket_type IS NOT NULL AND wicket_type NOT IN ('run out', 'retired hurt') THEN 1 ELSE 0 END) as wickets
            FROM balls
            WHERE bowler = ?
            """,
            [player_name],
        ).df()

        return pd.concat([batting, bowling], ignore_index=True)

    def get_venue_phase_stats(self, venue: str, innings: Optional[int] = None) -> pd.DataFrame:
        conditions: list[str] = []
        params: list[Any] = []
        append_balls_venue_filter(conditions, params, venue, self.ball_cols)
        if innings:
            conditions.append("innings = ?")
            params.append(innings)
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        return self.con.execute(
            f"""
            SELECT
                phase,
                innings,
                ROUND(AVG(phase_runs), 1) AS avg_runs,
                ROUND(AVG(phase_wkts), 1) AS avg_wkts,
                COUNT(DISTINCT match_id) AS matches
            FROM (
                SELECT
                    match_id, innings, phase,
                    SUM(runs_off_bat + extras) AS phase_runs,
                    SUM(CASE WHEN wicket_type IS NOT NULL THEN 1 ELSE 0 END) AS phase_wkts
                FROM balls
                {where_clause}
                GROUP BY match_id, innings, phase
            ) sub
            GROUP BY phase, innings
            ORDER BY phase, innings
            """,
            params,
        ).df()

    def get_player_vs_style(self, striker: str, bowling_style_players: Dict[str, List[str]]) -> pd.DataFrame:
        results = []
        for style, bowlers in bowling_style_players.items():
            placeholders = ",".join(["?"] * len(bowlers))
            row = self.con.execute(
                f"""
                SELECT
                    ? AS style,
                    SUM(runs_off_bat) AS runs,
                    COUNT(*) AS balls,
                    SUM(CASE WHEN wicket_type IS NOT NULL
                             AND player_dismissed = ? THEN 1 ELSE 0 END) AS outs
                FROM balls
                WHERE striker = ? AND bowler IN ({placeholders})
                """,
                [style, striker, striker] + bowlers,
            ).df()
            results.append(row)

        return pd.concat(results, ignore_index=True) if results else pd.DataFrame()

    def get_team_form(self, team_name: str, limit: int = 10, opponent: Optional[str] = None) -> pd.DataFrame:
        conditions: list[str] = []
        params: list[Any] = []
        append_matches_team_filter(conditions, params, team_name)

        if opponent:
            append_matches_team_filter(conditions, params, opponent)

        where_clause = "WHERE " + " AND ".join(conditions)
        params.append(limit)

        return self.con.execute(
            f"""
            SELECT *,
                CASE WHEN winner = ? THEN 'W'
                     WHEN winner IN ('Tie', 'No Result') THEN 'NR'
                     ELSE 'L' END AS result
            FROM matches
            {where_clause}
            ORDER BY start_date DESC
            LIMIT ?
            """,
            [team_name] + params,
        ).df()

    def get_all_teams(self) -> List[str]:
        return self.con.execute(
            """
            SELECT DISTINCT team FROM (
                SELECT team_bat_1 AS team FROM matches
                UNION
                SELECT team_bat_2 AS team FROM matches
            ) ORDER BY team
            """
        ).df()["team"].tolist()

    def get_all_venues(self) -> List[str]:
        return self.con.execute("SELECT DISTINCT venue FROM matches ORDER BY venue").df()["venue"].tolist()

    def get_player_stats_batch(
        self,
        player_list: List[str],
        opponent: Optional[str] = None,
        venue: Optional[str] = None,
        years_back: Optional[int] = None,
    ) -> pd.DataFrame:
        placeholders = ",".join(["?"] * len(player_list))
        conditions = [f"striker IN ({placeholders})"]
        params = list(player_list)

        if opponent:
            conditions.append("bowling_team = ?")
            params.append(opponent)
        if venue:
            append_balls_venue_filter(conditions, params, venue, self.ball_cols)
        if years_back:
            cutoff = datetime.now() - timedelta(days=years_back * 365)
            conditions.append("start_date >= ?")
            params.append(cutoff.strftime("%Y-%m-%d"))

        where_clause = "WHERE " + " AND ".join(conditions)

        return self.con.execute(
            f"""
            WITH per_match_stats AS (
                SELECT
                    striker,
                    match_id,
                    SUM(runs_off_bat) as runs,
                    COUNT(*) as balls,
                    SUM(CASE WHEN runs_off_bat = 4 THEN 1 ELSE 0 END) as fours,
                    SUM(CASE WHEN runs_off_bat = 6 THEN 1 ELSE 0 END) as sixes,
                    SUM(CASE WHEN wicket_type IS NOT NULL AND player_dismissed = striker THEN 1 ELSE 0 END) as outs
                FROM balls
                {where_clause}
                GROUP BY striker, match_id
            )
            SELECT
                striker as player,
                COUNT(match_id) as innings,
                SUM(runs) as runs,
                SUM(balls) as balls,
                SUM(fours) as fours,
                SUM(sixes) as sixes,
                SUM(outs) as outs,
                MAX(runs) as highest_score
            FROM per_match_stats
            GROUP BY striker
            """,
            params,
        ).df()

    def get_db_stats(self) -> Dict[str, int]:
        balls_row = self.con.execute("SELECT COUNT(*) FROM balls").fetchone()
        matches_row = self.con.execute("SELECT COUNT(*) FROM matches").fetchone()

        assert balls_row is not None
        assert matches_row is not None

        balls = int(balls_row[0])
        matches = int(matches_row[0])
        return {"balls": balls, "matches": matches}

    def get_latest_match_date(self) -> Optional[pd.Timestamp]:
        row = self.con.execute(
            """
            SELECT COALESCE(
                (SELECT MAX(start_date) FROM balls),
                (SELECT MAX(start_date) FROM matches)
            ) AS latest_date
            """
        ).fetchone()

        if row is None:
            return None

        if row[0] is None:
            return None

        try:
            return pd.Timestamp(row[0]).floor("D")
        except (TypeError, ValueError):
            return None
