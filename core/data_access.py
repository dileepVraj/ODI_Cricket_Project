"""
Data Access Layer (DAL)
The only module that interacts with DuckDB directly.
Engines call DAL methods and receive pandas DataFrames.
"""
from datetime import datetime, timedelta

import duckdb
import pandas as pd
from typing import Any, Dict, List, Optional, Sequence

from config.shared.venues import get_venue_aliases
from core.exceptions import DataIntegrityError


def _open_duckdb_connection(db_path: str) -> duckdb.DuckDBPyConnection:
    """Create a read-only DuckDB connection outside class scope for boundary linting."""
    return duckdb.connect(db_path, read_only=True)

class DataAccess:
    """
    Provides high-level data retrieval methods for cricket engines.
    Each method returns a pandas DataFrame.
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        try:
            self.con = _open_duckdb_connection(db_path)
        except (duckdb.Error, OSError, RuntimeError, ValueError, TypeError) as e:
            raise DataIntegrityError(f"🔥 FATAL: Could not connect to DuckDB at {db_path}. Error: {e}")

        # 🛡️ MANDATORY SCHEMA VERIFICATION (Crash Early, Crash Loud)
        self.tables = set(r[0] for r in self.con.execute("SHOW TABLES").fetchall())
        mandatory_tables = ["matches", "balls"]
        for table in mandatory_tables:
            if table not in self.tables:
                raise DataIntegrityError(f"🔥 FATAL: Database at {db_path} is missing mandatory table '{table}'.")

        self.match_cols = set(r[1] for r in self.con.execute("PRAGMA table_info('matches')").fetchall())
        mandatory_cols = ["match_id", "start_date", "venue", "team_bat_1", "team_bat_2", "winner"]
        for col in mandatory_cols:
            if col not in self.match_cols:
                raise DataIntegrityError(f"🔥 FATAL: Table 'matches' is missing mandatory column '{col}'. Schema drift detected.")

        self.ball_cols = set(r[1] for r in self.con.execute("PRAGMA table_info('balls')").fetchall())
        mandatory_ball_cols = ["match_id", "innings", "striker", "bowler", "runs_off_bat", "extras"]
        for col in mandatory_ball_cols:
            if col not in self.ball_cols:
                raise DataIntegrityError(f"🔥 FATAL: Table 'balls' is missing mandatory column '{col}'. Schema drift detected.")

        self._validate_match_integrity()

    def close(self) -> None:
        self.con.close()

    def has_table(self, name: str) -> bool:
        return name in self.tables

    def _validate_match_integrity(self) -> None:
        """
        Fast integrity checks for match summary completeness.
        Allows innings-2 missingness only for no-result/abandoned outcomes.
        """
        suspicious_missing_inn2 = self.con.execute(
            """
            SELECT COUNT(*) FROM matches
            WHERE (balls_inn2 IS NULL OR wickets_inn2 IS NULL)
              AND lower(trim(coalesce(winner, ''))) NOT IN ('', 'none', 'nan', 'no result', 'abandoned')
            """
        ).fetchone()[0]

        if suspicious_missing_inn2:
            raise DataIntegrityError(
                f"FATAL: Found {suspicious_missing_inn2} matches with missing innings-2 fields "
                "despite having a declared result. Pipeline/data integrity issue detected."
            )

    def _resolve_venue_terms(self, venue_identifier: Any) -> List[str]:
        """
        Expands a venue identifier into canonical/raw aliases for robust filtering.
        """
        if not venue_identifier:
            return []
        try:
            aliases = get_venue_aliases(venue_identifier)
        except (AttributeError, KeyError, TypeError, ValueError):
            aliases = [venue_identifier]

        seen = set()
        terms = []
        for alias in aliases + [venue_identifier]:
            if alias is None:
                continue
            alias_str = str(alias).strip()
            if not alias_str or alias_str in seen:
                continue
            seen.add(alias_str)
            terms.append(alias_str)
        return terms

    @staticmethod
    def _is_regex_venue_filter(venue_identifier: Any) -> bool:
        return isinstance(venue_identifier, str) and "|" in venue_identifier

    @staticmethod
    def _build_in_clause(column_name: str, values: Sequence[Any]) -> str:
        placeholders = ",".join(["?"] * len(values))
        return f"{column_name} IN ({placeholders})"

    def _append_matches_venue_filter(
        self,
        conditions: List[str],
        params: List[Any],
        venue_identifier: Any,
    ) -> None:
        if self._is_regex_venue_filter(venue_identifier):
            parts = []
            if "venue_id" in self.match_cols:
                parts.append("regexp_matches(venue_id, ?)")
                params.append(venue_identifier)
            if "venue" in self.match_cols:
                parts.append("regexp_matches(venue, ?)")
                params.append(venue_identifier)
            if parts:
                conditions.append("(" + " OR ".join(parts) + ")")
            return

        terms = self._resolve_venue_terms(venue_identifier)
        if not terms:
            return

        parts = []
        if "venue_id" in self.match_cols:
            parts.append(self._build_in_clause("venue_id", terms))
            params.extend(terms)
        if "venue" in self.match_cols:
            parts.append(self._build_in_clause("venue", terms))
            params.extend(terms)

        if parts:
            conditions.append("(" + " OR ".join(parts) + ")")

    def _append_balls_venue_filter(
        self,
        conditions: List[str],
        params: List[Any],
        venue_identifier: Any,
    ) -> None:
        if self._is_regex_venue_filter(venue_identifier):
            parts = []
            if "venue_id" in self.ball_cols:
                parts.append("regexp_matches(venue_id, ?)")
                params.append(venue_identifier)
            if "venue" in self.ball_cols:
                parts.append("regexp_matches(venue, ?)")
                params.append(venue_identifier)
            if parts:
                conditions.append("(" + " OR ".join(parts) + ")")
            return

        terms = self._resolve_venue_terms(venue_identifier)
        if not terms:
            return

        parts = []
        if "venue_id" in self.ball_cols:
            parts.append(self._build_in_clause("venue_id", terms))
            params.extend(terms)
        if "venue" in self.ball_cols:
            parts.append(self._build_in_clause("venue", terms))
            params.extend(terms)

        if parts:
            conditions.append("(" + " OR ".join(parts) + ")")

    @staticmethod
    def _append_matches_team_filter(
        conditions: List[str],
        params: List[Any],
        team_name: Optional[str],
    ) -> None:
        """
        Robust match-team filter:
        1) Primary: matches.team_bat_1 / matches.team_bat_2
        2) Fallback: correlated lookup against balls.batting_team / balls.bowling_team

        This prevents dropped rain/abandoned/no-result matches where one innings-side
        can be null in `matches` while team participation is still present in `balls`.
        """
        if not team_name:
            return

        conditions.append(
            "("
            "team_bat_1 = ? OR team_bat_2 = ? "
            "OR EXISTS ("
            "SELECT 1 FROM balls b "
            "WHERE b.match_id = matches.match_id "
            "AND (b.batting_team = ? OR b.bowling_team = ?)"
            ")"
            ")"
        )
        params.extend([team_name, team_name, team_name, team_name])

    @staticmethod
    def _is_blank_team(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, float) and pd.isna(value):
            return True
        return str(value).strip() == ""

    @staticmethod
    def _is_no_result_winner(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, float) and pd.isna(value):
            return True
        return str(value).strip().lower() in {"", "none", "nan", "no result", "abandoned"}

    def _normalize_match_innings_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalizes innings columns to make downstream filters deterministic.

        Rule:
        - For no-result/abandoned matches where innings-2 did not start,
          set balls_inn2/wickets_inn2 = 0 (structural completeness).
        - Keep score_inn2 as NULL to avoid fabricating scoring data.
        """
        if df is None or df.empty:
            return df

        out = df.copy()
        numeric_cols = [
            "score_inn1", "score_inn2",
            "balls_inn1", "balls_inn2",
            "wickets_inn1", "wickets_inn2",
        ]
        for col in numeric_cols:
            if col in out.columns:
                out[col] = pd.to_numeric(out[col], errors="coerce")

        if all(col in out.columns for col in ["winner", "balls_inn2", "wickets_inn2"]):
            no_result_mask = out["winner"].apply(self._is_no_result_winner)
            missing_inn2_mask = out["balls_inn2"].isna() & out["wickets_inn2"].isna()
            fill_mask = no_result_mask & missing_inn2_mask
            if bool(fill_mask.any()):
                out.loc[fill_mask, "balls_inn2"] = 0
                out.loc[fill_mask, "wickets_inn2"] = 0

        return out

    def _hydrate_missing_match_teams(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Backfills missing team_bat_1/team_bat_2 using team evidence from balls.
        This makes downstream team masks resilient for interrupted/no-result games.
        """
        if df is None or df.empty:
            return df
        if "match_id" not in df.columns or "team_bat_1" not in df.columns or "team_bat_2" not in df.columns:
            return df

        missing_mask = (
            df["team_bat_1"].apply(self._is_blank_team)
            | df["team_bat_2"].apply(self._is_blank_team)
        )
        if not bool(missing_mask.any()):
            return df

        target_ids = df.loc[missing_mask, "match_id"].dropna().unique().tolist()
        if not target_ids:
            return df

        placeholders = ",".join(["?"] * len(target_ids))
        team_rows = self.con.execute(
            f"""
            SELECT match_id, LIST(DISTINCT team) AS teams
            FROM (
                SELECT match_id, batting_team AS team
                FROM balls
                WHERE match_id IN ({placeholders})
                UNION ALL
                SELECT match_id, bowling_team AS team
                FROM balls
                WHERE match_id IN ({placeholders})
            ) t
            WHERE team IS NOT NULL AND TRIM(CAST(team AS VARCHAR)) <> ''
            GROUP BY match_id
            """,
            target_ids + target_ids,
        ).df()

        def _normalize_team_list(teams_val: Any) -> List[str]:
            if hasattr(teams_val, "tolist") and not isinstance(teams_val, (str, bytes)):
                teams_iter = teams_val.tolist()
            elif isinstance(teams_val, (list, tuple, set)):
                teams_iter = list(teams_val)
            else:
                teams_iter = [teams_val]
            teams = [str(t).strip() for t in teams_iter if not self._is_blank_team(t)]
            return sorted(set(teams))

        if team_rows.empty:
            return df

        team_rows = team_rows.copy()
        team_rows["teams_normalized"] = team_rows["teams"].apply(_normalize_team_list)
        team_lookup = team_rows.set_index("match_id")["teams_normalized"]

        out = df.copy()
        missing_out = out.loc[missing_mask].copy()
        missing_out["candidates"] = missing_out["match_id"].map(team_lookup)

        missing_out["team_1_current"] = missing_out["team_bat_1"].apply(
            lambda v: None if self._is_blank_team(v) else str(v).strip()
        )
        missing_out["team_2_current"] = missing_out["team_bat_2"].apply(
            lambda v: None if self._is_blank_team(v) else str(v).strip()
        )

        missing_out["team_1_filled"] = missing_out.apply(
            lambda row: row["team_1_current"]
            if row["team_1_current"] is not None
            else (row["candidates"][0] if isinstance(row["candidates"], list) and row["candidates"] else None),
            axis=1,
        )

        missing_out["team_2_filled"] = missing_out.apply(
            lambda row: row["team_2_current"]
            if row["team_2_current"] is not None
            else next(
                (
                    cand
                    for cand in (row["candidates"] if isinstance(row["candidates"], list) else [])
                    if cand != row["team_1_filled"]
                ),
                None,
            ),
            axis=1,
        )

        filled_team_1 = missing_out["team_1_filled"].dropna()
        filled_team_2 = missing_out["team_2_filled"].dropna()
        if not filled_team_1.empty:
            out.loc[filled_team_1.index, "team_bat_1"] = filled_team_1
        if not filled_team_2.empty:
            out.loc[filled_team_2.index, "team_bat_2"] = filled_team_2

        return out

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

    # --- MATCH QUERIES ---
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
        conditions = []
        params = []

        if team_a:
            self._append_matches_team_filter(conditions, params, team_a)

        if team_b:
            self._append_matches_team_filter(conditions, params, team_b)

        # Prioritize 'venue' if provided, otherwise use 'venue_id'
        target_v = venue if venue else venue_id
        if target_v:
            self._append_matches_venue_filter(conditions, params, target_v)

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
        result_df = self._hydrate_missing_match_teams(result_df)
        return self._normalize_match_innings_fields(result_df)

    # --- BALL-BY-BALL QUERIES ---
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
        conditions = []
        params = []

        if match_ids:
            placeholders = ",".join(["?"] * len(match_ids))
            conditions.append(f"match_id IN ({placeholders})")
            params.extend(match_ids)

        target_v = venue if venue else venue_id
        if target_v:
            self._append_balls_venue_filter(conditions, params, target_v)

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

    # --- AGGREGATION QUERIES (Vectorized) ---
    def get_venue_summary(self, venue_id: str, years_back: Optional[int] = None) -> pd.DataFrame:
        """
        Returns a summary of matches at a venue, including avg scores.
        """
        conditions = []
        params = []
        
        self._append_matches_venue_filter(conditions, params, venue_id)

        if years_back:
            cutoff = datetime.now() - timedelta(days=years_back * 365)
            conditions.append("start_date >= ?")
            params.append(cutoff.strftime("%Y-%m-%d"))

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        return self.con.execute(f"""
            SELECT 
                COUNT(*) as matches,
                ROUND(AVG(TRY_CAST(score_inn1 AS DOUBLE)), 1) as avg_score_1,
                ROUND(AVG(TRY_CAST(score_inn2 AS DOUBLE)), 1) as avg_score_2
            FROM matches 
            {where_clause}
        """, params).df()

    def get_h2h_summary(
        self,
        team_a: str,
        team_b: str,
        venue_id: Optional[str] = None,
        years_back: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Returns head-to-head summary stats.
        """
        conditions = []
        params = []
        self._append_matches_team_filter(conditions, params, team_a)
        self._append_matches_team_filter(conditions, params, team_b)

        if venue_id:
            self._append_matches_venue_filter(conditions, params, venue_id)

        if years_back:
            cutoff = datetime.now() - timedelta(days=years_back * 365)
            conditions.append("start_date >= ?")
            params.append(cutoff.strftime("%Y-%m-%d"))

        where_clause = "WHERE " + " AND ".join(conditions)
        
        return self.con.execute(f"""
            SELECT 
                winner,
                COUNT(*) as wins,
                ROUND(AVG(TRY_CAST(score_inn1 AS DOUBLE)), 1) as avg_score_1,
                ROUND(AVG(TRY_CAST(score_inn2 AS DOUBLE)), 1) as avg_score_2
            FROM matches 
            {where_clause}
            GROUP BY winner
        """, params).df()

    def get_player_career_summary(self, player_name: str) -> pd.DataFrame:
        """
        Returns batting and bowling career summaries for a player.
        Leverages DuckDB's vectorized engine for fast aggregation over million-ball datasets.
        """
        batting = self.con.execute("""
            SELECT 
                'batting' as role,
                COUNT(DISTINCT match_id) as innings,
                SUM(runs_off_bat) as runs,
                COUNT(*) as balls,
                SUM(CASE WHEN wicket_type IS NOT NULL AND player_dismissed = ? THEN 1 ELSE 0 END) as outs
            FROM balls 
            WHERE striker = ?
        """, [player_name, player_name]).df()

        bowling = self.con.execute("""
            SELECT 
                'bowling' as role,
                COUNT(DISTINCT match_id) as innings,
                SUM(runs_off_bat + extras - (CASE WHEN wides > 0 OR noballs > 0 THEN extras ELSE 0 END)) as runs,
                COUNT(CASE WHEN wides = 0 AND noballs = 0 THEN 1 END) as balls,
                SUM(CASE WHEN wicket_type IS NOT NULL AND wicket_type NOT IN ('run out', 'retired hurt') THEN 1 ELSE 0 END) as wickets
            FROM balls 
            WHERE bowler = ?
        """, [player_name]).df()

        return pd.concat([batting, bowling], ignore_index=True)

    def get_venue_phase_stats(self, venue: str, innings: Optional[int] = None) -> pd.DataFrame:
        conditions = []
        params = []
        self._append_balls_venue_filter(conditions, params, venue)
        if innings:
            conditions.append("innings = ?")
            params.append(innings)
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        return self.con.execute(f"""
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
        """, params).df()

    def get_player_vs_style(self, striker: str, bowling_style_players: Dict[str, List[str]]) -> pd.DataFrame:
        results = []
        for style, bowlers in bowling_style_players.items():
            placeholders = ",".join(["?"] * len(bowlers))
            row = self.con.execute(f"""
                SELECT
                    ? AS style,
                    SUM(runs_off_bat) AS runs,
                    COUNT(*) AS balls,
                    SUM(CASE WHEN wicket_type IS NOT NULL
                             AND player_dismissed = ? THEN 1 ELSE 0 END) AS outs
                FROM balls
                WHERE striker = ? AND bowler IN ({placeholders})
            """, [style, striker, striker] + bowlers).df()
            results.append(row)

        return pd.concat(results, ignore_index=True) if results else pd.DataFrame()

    def get_team_form(self, team_name: str, limit: int = 10, opponent: Optional[str] = None) -> pd.DataFrame:
        conditions = []
        params = []
        self._append_matches_team_filter(conditions, params, team_name)

        if opponent:
            self._append_matches_team_filter(conditions, params, opponent)

        where_clause = "WHERE " + " AND ".join(conditions)
        params.append(limit)

        return self.con.execute(f"""
            SELECT *,
                CASE WHEN winner = ? THEN 'W'
                     WHEN winner IN ('Tie', 'No Result') THEN 'NR'
                     ELSE 'L' END AS result
            FROM matches
            {where_clause}
            ORDER BY start_date DESC
            LIMIT ?
        """, [team_name] + params).df()

    # --- METADATA QUERIES ---
    def get_all_teams(self) -> List[str]:
        return self.con.execute("""
            SELECT DISTINCT team FROM (
                SELECT team_bat_1 AS team FROM matches
                UNION
                SELECT team_bat_2 AS team FROM matches
            ) ORDER BY team
        """).df()["team"].tolist()

    def get_all_venues(self) -> List[str]:
        return self.con.execute(
            "SELECT DISTINCT venue FROM matches ORDER BY venue"
        ).df()["venue"].tolist()

    def get_player_stats_batch(
        self,
        player_list: List[str],
        opponent: Optional[str] = None,
        venue: Optional[str] = None,
        years_back: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Returns a DataFrame of stats for multiple players in one shot.
        Vectorized replacement for the 'linear scan' loop in PlayerEngine.
        """
        placeholders = ",".join(["?"] * len(player_list))
        conditions = [f"striker IN ({placeholders})"]
        params = list(player_list)

        if opponent:
            conditions.append("bowling_team = ?")
            params.append(opponent)
        if venue:
            self._append_balls_venue_filter(conditions, params, venue)
        if years_back:
            cutoff = datetime.now() - timedelta(days=years_back * 365)
            conditions.append("start_date >= ?")
            params.append(cutoff.strftime("%Y-%m-%d"))

        where_clause = "WHERE " + " AND ".join(conditions)
        
        return self.con.execute(f"""
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
        """, params).df()

    def get_db_stats(self) -> Dict[str, int]:
        balls = self.con.execute("SELECT COUNT(*) FROM balls").fetchone()[0]
        matches = self.con.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
        return {"balls": balls, "matches": matches}

    def get_latest_match_date(self) -> Optional[pd.Timestamp]:
        """
        Returns the latest available start_date from the DB.
        Prefers ball-level dates and falls back to match-level dates.
        """
        row = self.con.execute(
            """
            SELECT COALESCE(
                (SELECT MAX(start_date) FROM balls),
                (SELECT MAX(start_date) FROM matches)
            ) AS latest_date
            """
        ).fetchone()

        if not row or row[0] is None:
            return None

        try:
            return pd.Timestamp(row[0]).floor("D")
        except (TypeError, ValueError):
            return None
