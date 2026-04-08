"""
DAL Connection - opens and verifies the DuckDB database connection.
"""

import duckdb

from core.exceptions import DataIntegrityError


def _open_duckdb_connection(db_path: str) -> duckdb.DuckDBPyConnection:
    """Create a read-only DuckDB connection."""
    return duckdb.connect(db_path, read_only=True)


class DALConnection:
    """
    Manages the DuckDB connection lifecycle and schema verification.
    DataAccess inherits from this class.
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        try:
            self.con = _open_duckdb_connection(db_path)
        except (duckdb.Error, OSError, RuntimeError, ValueError, TypeError) as e:
            raise DataIntegrityError(
                f"FATAL: Could not connect to DuckDB at {db_path}. Error: {e}"
            )

        self.tables = set(r[0] for r in self.con.execute("SHOW TABLES").fetchall())
        mandatory_tables = ["matches", "balls"]
        for table in mandatory_tables:
            if table not in self.tables:
                raise DataIntegrityError(f"FATAL: Database at {db_path} is missing mandatory table '{table}'.")

        self.match_cols = set(r[1] for r in self.con.execute("PRAGMA table_info('matches')").fetchall())
        mandatory_cols = ["match_id", "start_date", "venue", "team_bat_1", "team_bat_2", "winner"]
        for col in mandatory_cols:
            if col not in self.match_cols:
                raise DataIntegrityError(
                    f"FATAL: Table 'matches' is missing mandatory column '{col}'. Schema drift detected."
                )

        self.ball_cols = set(r[1] for r in self.con.execute("PRAGMA table_info('balls')").fetchall())
        mandatory_ball_cols = ["match_id", "innings", "striker", "bowler", "runs_off_bat", "extras"]
        for col in mandatory_ball_cols:
            if col not in self.ball_cols:
                raise DataIntegrityError(
                    f"FATAL: Table 'balls' is missing mandatory column '{col}'. Schema drift detected."
                )

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
        row = self.con.execute(
            """
            SELECT COUNT(*) FROM matches
            WHERE (balls_inn2 IS NULL OR wickets_inn2 IS NULL)
              AND lower(trim(coalesce(winner, ''))) NOT IN ('', 'none', 'nan', 'no result', 'abandoned')
            """
        ).fetchone()
        suspicious_missing_inn2 = 0 if row is None else int(row[0])

        if suspicious_missing_inn2:
            raise DataIntegrityError(
                f"FATAL: Found {suspicious_missing_inn2} matches with missing innings-2 fields "
                "despite having a declared result. Pipeline/data integrity issue detected."
            )
