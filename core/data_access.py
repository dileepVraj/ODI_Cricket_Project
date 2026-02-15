"""
Data Access Layer (DAL)
The only module that interacts with DuckDB directly.
Engines call DAL methods and receive pandas DataFrames.
"""
from datetime import datetime, timedelta

import duckdb
import pandas as pd

from core.exceptions import DataIntegrityError

class DataAccess:
    """
    Provides high-level data retrieval methods for cricket engines.
    Each method returns a pandas DataFrame.
    """

    def __init__(self, db_path):
        self.db_path = db_path
        try:
            self.con = duckdb.connect(db_path, read_only=True)
        except Exception as e:
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

        print(f"Connected to: {db_path} (Schema Verified ✅)")

    def close(self):
        self.con.close()

    def has_table(self, name):
        return name in self.tables

    def get_player_stats(self):
        if not self.has_table("player_stats"):
            return pd.DataFrame()
        return self.con.execute("SELECT * FROM player_stats").df()

    def get_phase_stats(self):
        if not self.has_table("phase_stats"):
            return pd.DataFrame()
        return self.con.execute("SELECT * FROM phase_stats").df()

    def get_player_metadata(self):
        if not self.has_table("player_metadata"):
            return pd.DataFrame()
        return self.con.execute("SELECT * FROM player_metadata").df()

    def get_squads(self):
        if not self.has_table("squads"):
            return pd.DataFrame()
        return self.con.execute("SELECT * FROM squads").df()

    # --- MATCH QUERIES ---
    def get_matches(self, team_a=None, team_b=None, venue=None, venue_id=None, 
                    years_back=None, country=None, match_ids=None, limit=None):
        conditions = []
        params = []

        if team_a:
            conditions.append("(team_bat_1 = ? OR team_bat_2 = ?)")
            params.extend([team_a, team_a])

        if team_b:
            conditions.append("(team_bat_1 = ? OR team_bat_2 = ?)")
            params.extend([team_b, team_b])

        # Prioritize 'venue' if provided, otherwise use 'venue_id'
        target_v = venue if venue else venue_id
        if target_v:
            if "venue_id" in self.match_cols:
                conditions.append("venue_id = ?")
            else:
                conditions.append("venue = ?")
            params.append(target_v)

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
        return self.con.execute(query, params).df()

    # --- BALL-BY-BALL QUERIES ---
    def get_balls(self, match_ids=None, venue=None, venue_id=None, batting_team=None, 
                  bowling_team=None, striker=None, bowler=None, players=None,
                  innings=None, phase=None, years_back=None, limit=None):
        conditions = []
        params = []

        if match_ids:
            placeholders = ",".join(["?"] * len(match_ids))
            conditions.append(f"match_id IN ({placeholders})")
            params.extend(match_ids)

        target_v = venue if venue else venue_id
        if target_v:
            conditions.append("venue = ?")
            params.append(target_v)

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
    def get_venue_summary(self, venue_id, years_back=None):
        """
        Returns a summary of matches at a venue, including avg scores.
        """
        conditions = []
        params = []
        
        if "venue_id" in self.match_cols:
            conditions.append("venue_id = ?")
            params.append(venue_id)
        else:
            conditions.append("venue = ?")
            params.append(venue_id)

        if years_back:
            cutoff = datetime.now() - timedelta(days=years_back * 365)
            conditions.append("start_date >= ?")
            params.append(cutoff.strftime("%Y-%m-%d"))

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        return self.con.execute(f"""
            SELECT 
                COUNT(*) as matches,
                ROUND(AVG(CAST(regexp_extract(score_1, '(\d+)') AS INT)), 1) as avg_score_1,
                ROUND(AVG(CAST(regexp_extract(score_2, '(\d+)') AS INT)), 1) as avg_score_2
            FROM matches 
            {where_clause}
        """, params).df()

    def get_h2h_summary(self, team_a, team_b, venue_id=None, years_back=None):
        """
        Returns head-to-head summary stats.
        """
        conditions = [
            "((team_bat_1 = ? AND team_bat_2 = ?) OR (team_bat_1 = ? AND team_bat_2 = ?))"
        ]
        params = [team_a, team_b, team_b, team_a]

        if venue_id:
            if "venue_id" in self.match_cols:
                conditions.append("venue_id = ?")
                params.append(venue_id)
            else:
                conditions.append("venue = ?")
                params.append(venue_id)

        if years_back:
            cutoff = datetime.now() - timedelta(days=years_back * 365)
            conditions.append("start_date >= ?")
            params.append(cutoff.strftime("%Y-%m-%d"))

        where_clause = "WHERE " + " AND ".join(conditions)
        
        return self.con.execute(f"""
            SELECT 
                winner,
                COUNT(*) as wins,
                ROUND(AVG(CAST(regexp_extract(score_1, '(\d+)') AS INT)), 1) as avg_score_1,
                ROUND(AVG(CAST(regexp_extract(score_2, '(\d+)') AS INT)), 1) as avg_score_2
            FROM matches 
            {where_clause}
            GROUP BY winner
        """, params).df()

    def get_player_career_summary(self, player_name):
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

    def get_venue_phase_stats(self, venue, innings=None):
        inn_filter = "AND innings = ?" if innings else ""
        params = [venue] + ([innings] if innings else [])

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
                WHERE venue = ? {inn_filter}
                GROUP BY match_id, innings, phase
            ) sub
            GROUP BY phase, innings
            ORDER BY phase, innings
        """, params).df()

    def get_player_vs_style(self, striker, bowling_style_players):
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

    def get_team_form(self, team_name, limit=10, opponent=None):
        conditions = ["(team_bat_1 = ? OR team_bat_2 = ?)"]
        params = [team_name, team_name]

        if opponent:
            conditions.append("(team_bat_1 = ? OR team_bat_2 = ?)")
            params.extend([opponent, opponent])

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
    def get_all_teams(self):
        return self.con.execute("""
            SELECT DISTINCT team FROM (
                SELECT team_bat_1 AS team FROM matches
                UNION
                SELECT team_bat_2 AS team FROM matches
            ) ORDER BY team
        """).df()["team"].tolist()

    def get_all_venues(self):
        return self.con.execute(
            "SELECT DISTINCT venue FROM matches ORDER BY venue"
        ).df()["venue"].tolist()

    def get_player_stats_batch(self, player_list, opponent=None, venue=None, years_back=None):
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
            conditions.append("venue = ?")
            params.append(venue)
        if years_back:
            cutoff = datetime.now() - timedelta(days=years_back * 365)
            conditions.append("start_date >= ?")
            params.append(cutoff.strftime("%Y-%m-%d"))

        where_clause = "WHERE " + " AND ".join(conditions)
        
        return self.con.execute(f"""
            SELECT 
                striker as player,
                COUNT(DISTINCT match_id) as innings,
                SUM(runs_off_bat) as runs,
                COUNT(*) as balls,
                SUM(CASE WHEN runs_off_bat = 4 THEN 1 ELSE 0 END) as fours,
                SUM(CASE WHEN runs_off_bat = 6 THEN 1 ELSE 0 END) as sixes,
                SUM(CASE WHEN wicket_type IS NOT NULL AND player_dismissed = striker THEN 1 ELSE 0 END) as outs,
                MAX(runs_off_bat) as highest_score -- Note: This is per-ball MAX, we need per-inning MAX in actual implementation
            FROM balls 
            {where_clause}
            GROUP BY striker
        """, params).df()

    def get_db_stats(self):
        balls = self.con.execute("SELECT COUNT(*) FROM balls").fetchone()[0]
        matches = self.con.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
        return {"balls": balls, "matches": matches}
