# cockpit/database.py
# DuckDB-backed repository for the Cockpit trading module.
# One lookup DuckDB per format. IPL trades live in a separate trades DB.

from __future__ import annotations

import os
from collections.abc import Generator

import duckdb

from cockpit.models import TRADE_WRITE_COLUMNS, Trade


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

_FORMAT_DB_ENV: dict[str, str] = {
    "ipl": "IPL_COCKPIT_DB_PATH",
    "odi": "ODI_COCKPIT_DB_PATH",
}

_FORMAT_DB_DEFAULT: dict[str, str] = {
    "ipl": "data/ipl.duckdb",
    "odi": "data/odi_cockpit.duckdb",
}

_FORMAT_TRADES_DB_ENV: dict[str, str] = {
    "ipl": "IPL_COCKPIT_TRADES_DB_PATH",
    "odi": "ODI_COCKPIT_DB_PATH",
}

_FORMAT_TRADES_DB_DEFAULT: dict[str, str] = {
    "ipl": "data/ipl_trades.duckdb",
    "odi": "data/odi_cockpit.duckdb",
}


def get_db_path(format_key: str) -> str:
    """Return the absolute path to the cockpit DuckDB for a given format."""
    fmt = format_key.strip().lower()
    env_var = _FORMAT_DB_ENV.get(fmt)
    if env_var:
        override = os.getenv(env_var)
        if override:
            return os.path.abspath(override)

    default = _FORMAT_DB_DEFAULT.get(fmt)
    if default is None:
        raise ValueError(f"Unknown cockpit format: {fmt!r}. Add it to _FORMAT_DB_DEFAULT.")

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.abspath(os.path.join(project_root, default))


def get_trades_db_path(format_key: str) -> str:
    """Return the absolute path to the cockpit trades DuckDB for a given format."""
    fmt = format_key.strip().lower()
    env_var = _FORMAT_TRADES_DB_ENV.get(fmt)
    if env_var:
        override = os.getenv(env_var)
        if override:
            return os.path.abspath(override)

    default = _FORMAT_TRADES_DB_DEFAULT.get(fmt)
    if default is None:
        raise ValueError(
            f"Unknown cockpit format: {fmt!r}. Add it to _FORMAT_TRADES_DB_DEFAULT."
        )

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.abspath(os.path.join(project_root, default))


def _ensure_parent_dir(path: str) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


# ---------------------------------------------------------------------------
# Schema DDL
# ---------------------------------------------------------------------------

_DDL_TRADES = """
CREATE SEQUENCE IF NOT EXISTS trades_id_seq START 1;

CREATE TABLE IF NOT EXISTS trades (
    id                  INTEGER   PRIMARY KEY DEFAULT nextval('trades_id_seq'),
    season              INTEGER   NOT NULL,
    match_date          TIMESTAMP,
    team_1              VARCHAR   NOT NULL,
    team_2              VARCHAR   NOT NULL,
    favourite_team      VARCHAR   NOT NULL,
    home_ground         VARCHAR   NOT NULL
                            CHECK (home_ground IN ('FAV', 'UG', 'NEU')),
    stadium             VARCHAR   NOT NULL,
    status              VARCHAR   NOT NULL DEFAULT 'DRAFT'
                            CHECK (status IN ('DRAFT', 'ACTIVE')),
    toss_winner         VARCHAR,
    toss_decision       VARCHAR
                            CHECK (toss_decision IN ('', 'bat', 'field')),
    bankroll            DOUBLE    NOT NULL DEFAULT 100.0,
    opening_odds        DOUBLE,
    bullet_05_odds      DOUBLE,
    bullet_05_stake     DOUBLE,
    bullet_1_odds       DOUBLE,
    bullet_1_stake      DOUBLE,
    bullet_2_odds       DOUBLE,
    bullet_2_stake      DOUBLE,
    bullet_3_odds       DOUBLE,
    bullet_3_stake      DOUBLE,
    total_stake         DOUBLE,
    target_profit       DOUBLE,
    profit_80pct        DOUBLE,
    exit_target_odds    DOUBLE,
    breakeven_odds      DOUBLE,
    actual_profit       DOUBLE,
    pct_of_target       DOUBLE,
    pct_return_on_stake DOUBLE,
    exit_odds           DOUBLE,
    result              VARCHAR   CHECK (result IN ('OPEN', 'LOST', 'SAT', 'SAV+', 'SAV-')),
    fav_reached_130     BOOLEAN   NOT NULL DEFAULT FALSE,
    is_fake_favourite   BOOLEAN   NOT NULL DEFAULT FALSE,
    notes               VARCHAR,
    selected_team_before_toss VARCHAR,
    back_odds_before_toss INTEGER,
    lay_odds_before_toss INTEGER,
    selected_team_after_toss  VARCHAR,
    back_odds_after_toss      INTEGER,
    lay_odds_after_toss       INTEGER,
    created_at          TIMESTAMP NOT NULL,
    updated_at          TIMESTAMP NOT NULL,
    odds_after_1st_over DOUBLE
)
"""

_DDL_TEAMS = """
CREATE TABLE IF NOT EXISTS teams (
    season  INTEGER NOT NULL,
    name    VARCHAR NOT NULL,
    acronym VARCHAR,
    PRIMARY KEY (season, name)
)
"""

# Canonical mapping: full team name → 2-4 letter acronym
TEAM_ACRONYMS: dict[str, str] = {
    "Chennai Super Kings":        "CSK",
    "Delhi Capitals":              "DC",
    "Gujarat Titans":              "GT",
    "Kolkata Knight Riders":       "KKR",
    "Lucknow Super Giants":        "LSG",
    "Mumbai Indians":              "MI",
    "Punjab Kings":                "PBKS",
    "Rajasthan Royals":            "RR",
    "Royal Challengers Bengaluru": "RCB",
    "Sunrisers Hyderabad":         "SRH",
}

_DDL_VENUES = """
CREATE TABLE IF NOT EXISTS venues (
    season       INTEGER NOT NULL,
    venue_code   VARCHAR NOT NULL,
    venue_label  VARCHAR NOT NULL,
    PRIMARY KEY (season, venue_code)
)
"""


# ---------------------------------------------------------------------------
# init_db
# ---------------------------------------------------------------------------

def init_db(format_key: str) -> None:
    """Create cockpit tables for a format.

    IPL stores trade history in a dedicated trades database so the main
    data/ipl.duckdb file only holds lookup tables.
    """
    fmt = format_key.strip().lower()

    lookup_path = get_db_path(fmt)
    _ensure_parent_dir(lookup_path)
    con = duckdb.connect(lookup_path)
    try:
        con.execute(_DDL_TEAMS)
        con.execute(_DDL_VENUES)
        if fmt != "ipl":
            con.execute(_DDL_TRADES)
    finally:
        con.close()

    trades_path = get_trades_db_path(fmt)
    if trades_path != lookup_path:
        _ensure_parent_dir(trades_path)
        con = duckdb.connect(trades_path)
        try:
            con.execute(_DDL_TRADES)
        finally:
            con.close()

    migrate_trades_db(fmt)
    migrate_lookup_db(fmt)


def migrate_lookup_db(format_key: str) -> None:
    """Add acronym column to teams table and populate it from TEAM_ACRONYMS."""
    fmt = format_key.strip().lower()
    lookup_path = get_db_path(fmt)
    _ensure_parent_dir(lookup_path)
    con = duckdb.connect(lookup_path)
    try:
        con.execute("ALTER TABLE teams ADD COLUMN IF NOT EXISTS acronym VARCHAR")
        for full_name, acronym in TEAM_ACRONYMS.items():
            con.execute(
                "UPDATE teams SET acronym = ? WHERE name = ? AND acronym IS NULL",
                [acronym, full_name],
            )
    finally:
        con.close()


def migrate_trades_db(format_key: str) -> None:
    """Add any missing columns to an existing trades table."""
    fmt = format_key.strip().lower()
    trades_path = get_trades_db_path(fmt)
    _ensure_parent_dir(trades_path)
    con = duckdb.connect(trades_path)
    try:
        new_trade_columns = [
            ("status", "VARCHAR"),
            ("selected_team_before_toss", "VARCHAR"),
            ("back_odds_before_toss", "INTEGER"),
            ("lay_odds_before_toss", "INTEGER"),
            ("selected_team_after_toss", "VARCHAR"),
            ("back_odds_after_toss", "INTEGER"),
            ("lay_odds_after_toss", "INTEGER"),
            ("odds_after_1st_over", "DOUBLE"),
        ]
        for col_name, col_type in new_trade_columns:
            con.execute(
                f"ALTER TABLE trades ADD COLUMN IF NOT EXISTS {col_name} {col_type}"
            )
        for column_name in ("toss_winner", "toss_decision"):
            try:
                con.execute(f"ALTER TABLE trades ALTER COLUMN {column_name} DROP NOT NULL")
            except Exception:
                pass
            try:
                con.execute(f"ALTER TABLE trades ALTER COLUMN {column_name} DROP DEFAULT")
            except Exception:
                pass
        try:
            con.execute("ALTER TABLE trades ALTER COLUMN status SET DEFAULT 'DRAFT'")
        except Exception:
            pass
        con.execute(
            """
            UPDATE trades
            SET status = COALESCE(
                status,
                CASE
                    WHEN selected_team_before_toss IS NULL
                        AND back_odds_before_toss IS NULL
                        AND lay_odds_before_toss IS NULL
                        AND selected_team_after_toss IS NULL
                        AND back_odds_after_toss IS NULL
                        AND lay_odds_after_toss IS NULL
                        AND COALESCE(toss_winner, '') = ''
                        AND COALESCE(toss_decision, '') = ''
                    THEN 'DRAFT'
                    ELSE 'ACTIVE'
                END
            )
            """
        )
        try:
            con.execute("ALTER TABLE trades ALTER COLUMN status SET NOT NULL")
        except Exception:
            pass
        legacy_before_exists = con.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'trades' AND column_name = 'fav_before_toss'
            LIMIT 1
            """
        ).fetchone()
        legacy_before_odds_exists = con.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'trades' AND column_name = 'odds_before_toss'
            LIMIT 1
            """
        ).fetchone()
        legacy_after_exists = con.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'trades' AND column_name = 'fav_after_toss'
            LIMIT 1
            """
        ).fetchone()
        legacy_after_odds_exists = con.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'trades' AND column_name = 'odds_after_toss'
            LIMIT 1
            """
        ).fetchone()
        if legacy_before_exists is not None and legacy_before_odds_exists is not None:
            con.execute(
                """
                UPDATE trades
                SET selected_team_before_toss = COALESCE(selected_team_before_toss, fav_before_toss),
                    back_odds_before_toss = COALESCE(
                        back_odds_before_toss,
                        CASE
                            WHEN odds_before_toss IS NULL THEN NULL
                            ELSE CAST(ROUND((odds_before_toss - 1) * 100) AS INTEGER)
                        END
                    )
                """
            )
        if legacy_after_exists is not None and legacy_after_odds_exists is not None:
            con.execute(
                """
                UPDATE trades
                SET selected_team_after_toss = COALESCE(selected_team_after_toss, fav_after_toss),
                    back_odds_after_toss = COALESCE(
                        back_odds_after_toss,
                        CASE
                            WHEN odds_after_toss IS NULL THEN NULL
                            ELSE CAST(ROUND((odds_after_toss - 1) * 100) AS INTEGER)
                        END
                    )
                """
            )
        has_legacy_santhel_url = con.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'trades' AND column_name = 'santhel_url'
            LIMIT 1
            """
        ).fetchone()
        if has_legacy_santhel_url is not None:
            con.execute("DELETE FROM trades WHERE santhel_url IS NOT NULL")
            con.execute("ALTER TABLE trades DROP COLUMN santhel_url")
        con.execute("DROP TABLE IF EXISTS santhel_config")
    finally:
        con.close()


# ---------------------------------------------------------------------------
# CockpitStore
# ---------------------------------------------------------------------------

class CockpitStore:
    """DuckDB repository for one format's cockpit data."""

    def __init__(self, format_key: str = "ipl", *, read_only: bool = False) -> None:
        self.format_key = format_key.strip().lower()
        self.path = get_db_path(self.format_key)
        self.trades_path = get_trades_db_path(self.format_key)
        _ensure_parent_dir(self.path)
        self._con = duckdb.connect(self.path, read_only=read_only)
        if self.trades_path == self.path:
            self._trades_con = self._con
        else:
            _ensure_parent_dir(self.trades_path)
            self._trades_con = duckdb.connect(self.trades_path, read_only=read_only)

    def close(self) -> None:
        self._con.close()
        if self._trades_con is not self._con:
            self._trades_con.close()

    # ------------------------------------------------------------------ trades

    def insert_trade(self, trade: Trade) -> Trade:
        values = trade.to_db_values()
        columns = ", ".join(TRADE_WRITE_COLUMNS)
        placeholders = ", ".join("?" for _ in TRADE_WRITE_COLUMNS)
        ordered_values = [values[column] for column in TRADE_WRITE_COLUMNS]
        sql = f"INSERT INTO trades ({columns}) VALUES ({placeholders}) RETURNING id"
        row = self._trades_con.execute(sql, ordered_values).fetchone()
        if row is None:
            raise RuntimeError("INSERT returned no id")
        trade.id = int(row[0])
        return trade

    def update_trade(self, trade: Trade) -> Trade:
        if trade.id is None:
            raise ValueError("Trade id is required for update.")
        values = trade.to_db_values()
        assignments = ", ".join(f"{col} = ?" for col in TRADE_WRITE_COLUMNS)
        ordered_values = [values[column] for column in TRADE_WRITE_COLUMNS]
        sql = f"UPDATE trades SET {assignments} WHERE id = ?"
        self._trades_con.execute(sql, [*ordered_values, trade.id])
        return trade

    def delete_trade(self, trade_id: int) -> None:
        self._trades_con.execute("DELETE FROM trades WHERE id = ?", [trade_id])

    def get_trade(self, trade_id: int) -> Trade | None:
        result = self._trades_con.execute("SELECT * FROM trades WHERE id = ?", [trade_id])
        row = result.fetchone()
        if row is None:
            return None
        columns = [column[0] for column in result.description or ()]
        return Trade.from_row(dict(zip(columns, row)))

    def list_trades(
        self,
        *,
        season: int | None = None,
        result: str | None = None,
        is_fake_favourite: bool | None = None,
        status: str | None = None,
        order: str = "DESC",
    ) -> list[Trade]:
        clauses: list[str] = []
        params: list[int | float | str | bool | None] = []

        if season is not None:
            clauses.append("season = ?")
            params.append(season)
        if result is not None:
            clauses.append("result = ?")
            params.append(result)
        if is_fake_favourite is not None:
            clauses.append("is_fake_favourite = ?")
            params.append(is_fake_favourite)
        if status is not None:
            clauses.append("status = ?")
            params.append(status)

        sql = "SELECT * FROM trades"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        direction = "ASC" if order.upper() == "ASC" else "DESC"
        sql += f" ORDER BY created_at {direction}, id {direction}"

        result_set = self._trades_con.execute(sql, params)
        columns = [column[0] for column in result_set.description or ()]
        return [Trade.from_row(dict(zip(columns, row))) for row in result_set.fetchall()]

    # ------------------------------------------------------------------ teams

    def get_teams(self) -> list[str]:
        rows = self._con.execute(
            "SELECT DISTINCT acronym FROM teams WHERE acronym IS NOT NULL ORDER BY acronym"
        ).fetchall()
        return [str(row[0]) for row in rows]

    # ----------------------------------------------------------------- venues

    def get_venues(self) -> list[dict[str, str]]:
        """Returns list of {id: venue_code, label: venue_label} dicts."""
        rows = self._con.execute(
            """
            SELECT venue_code, MIN(venue_label) AS venue_label
            FROM venues
            GROUP BY venue_code
            ORDER BY venue_label
            """,
        ).fetchall()
        return [{"id": str(row[0]), "label": str(row[1])} for row in rows]

# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------

def get_db(
    format_key: str = "ipl",
    *,
    read_only: bool = False,
) -> Generator[CockpitStore, None, None]:
    """FastAPI dependency factory. Yields one CockpitStore per request."""
    store = CockpitStore(format_key, read_only=read_only)
    try:
        yield store
    finally:
        store.close()
