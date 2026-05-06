# cockpit/database.py
# Repository layer for the Cockpit trading module.

from __future__ import annotations

import os
import sqlite3
import threading
from collections.abc import Generator, Sequence
from datetime import datetime as _datetime
from datetime import timezone
from typing import TypedDict, cast

import duckdb

from config.settings import (
    IPL_COCKPIT_DB_PATH,
    IPL_COCKPIT_TRADES_DB_PATH,
    ODI_COCKPIT_DB_PATH,
)
from cockpit.models import TRADE_WRITE_COLUMNS, Match, Trade, TradeDbValue, TradeSentiment


_FORMAT_DB_ENV: dict[str, str] = {
    "ipl": "IPL_COCKPIT_DB_PATH",
    "odi": "ODI_COCKPIT_DB_PATH",
}

_FORMAT_DB_DEFAULT: dict[str, str] = {
    "ipl": IPL_COCKPIT_DB_PATH,
    "odi": ODI_COCKPIT_DB_PATH,
}

_FORMAT_TRADES_DB_ENV: dict[str, str] = {
    "ipl": "IPL_COCKPIT_TRADES_DB_PATH",
    "odi": "ODI_COCKPIT_DB_PATH",
}

_FORMAT_TRADES_DB_DEFAULT: dict[str, str] = {
    "ipl": IPL_COCKPIT_TRADES_DB_PATH,
    "odi": ODI_COCKPIT_DB_PATH,
}

_INIT_LOCK = threading.Lock()
_INITIALIZED_DATABASES: dict[str, tuple[str, str]] = {}


def _ensure_parent_dir(path: str) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def _sqlite_connect(path: str, read_only: bool) -> sqlite3.Connection:
    if read_only:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True, check_same_thread=False)
    else:
        con = sqlite3.connect(path, check_same_thread=False)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def _table_names_sqlite(con: sqlite3.Connection) -> set[str]:
    rows = con.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
    ).fetchall()
    return {str(row[0]) for row in rows}


def _sqlite_table_columns(con: sqlite3.Connection, table_name: str) -> list[str]:
    rows = con.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [str(row[1]) for row in rows]


def _sqlite_table_info(con: sqlite3.Connection, table_name: str) -> list[tuple[object, ...]]:
    return con.execute(f"PRAGMA table_info({table_name})").fetchall()


def _sqlite_has_unique_index(
    con: sqlite3.Connection,
    table_name: str,
    column_names: Sequence[str],
) -> bool:
    expected_columns = [str(column) for column in column_names]
    for index_row in con.execute(f"PRAGMA index_list({table_name})").fetchall():
        if int(index_row[2]) != 1:
            continue
        index_name = str(index_row[1])
        index_columns = [
            str(column_row[2])
            for column_row in con.execute(f"PRAGMA index_info({index_name})").fetchall()
        ]
        if index_columns == expected_columns:
            return True
    return False


def _sqlite_foreign_key_has_rule(
    con: sqlite3.Connection,
    table_name: str,
    *,
    from_column: str,
    ref_table: str,
    ref_column: str,
    on_delete: str | None = None,
) -> bool:
    target_delete = on_delete.upper() if on_delete is not None else None
    for fk_row in con.execute(f"PRAGMA foreign_key_list({table_name})").fetchall():
        if str(fk_row[2]) != ref_table:
            continue
        if str(fk_row[3]) != from_column:
            continue
        if str(fk_row[4]) != ref_column:
            continue
        if target_delete is not None and str(fk_row[6]).upper() != target_delete:
            continue
        return True
    return False


def _sqlite_trade_database_ready(path: str, *, require_lookup_tables: bool) -> bool:
    if not os.path.exists(path):
        return False

    con = _sqlite_connect(path, read_only=True)
    try:
        table_names = _table_names_sqlite(con)
        required_tables = {"matches", "trades", "bets"}
        if require_lookup_tables:
            required_tables.update({"teams", "venues"})
        if not required_tables.issubset(table_names):
            return False

        matches_columns = _sqlite_table_columns(con, "matches")
        trades_columns = _sqlite_table_columns(con, "trades")
        bets_columns = _sqlite_table_columns(con, "bets")
        matches_info = {str(row[1]): row for row in _sqlite_table_info(con, "matches")}
        trades_info = {str(row[1]): row for row in _sqlite_table_info(con, "trades")}
        bets_info = {str(row[1]): row for row in _sqlite_table_info(con, "bets")}

        if "match_id" not in trades_columns:
            return False
        if "trade_id" not in bets_columns:
            return False
        if not {"season", "match_date", "team_1", "team_2", "stadium"}.issubset(matches_columns):
            return False
        if cast(int, matches_info["match_date"][3]) != 1:
            return False
        if cast(int, trades_info["match_id"][3]) != 1:
            return False
        if cast(int, bets_info["trade_id"][3]) != 1:
            return False
        if not _TRADE_REQUIRED_COLUMNS.issubset(trades_columns):
            return False
        if _TRADE_LEGACY_COLUMNS.intersection(trades_columns):
            return False
        if not _sqlite_has_unique_index(
            con,
            "matches",
            ("season", "match_date", "team_1", "team_2"),
        ):
            return False
        if not _sqlite_foreign_key_has_rule(
            con,
            "trades",
            from_column="match_id",
            ref_table="matches",
            ref_column="id",
        ):
            return False
        if not _sqlite_foreign_key_has_rule(
            con,
            "bets",
            from_column="trade_id",
            ref_table="trades",
            ref_column="id",
            on_delete="CASCADE",
        ):
            return False
        return True
    finally:
        con.close()


def _coerce_optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_iso_datetime(value: object) -> _datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text == "NaT":
        return None
    return _datetime.fromisoformat(text)


def _default_ipl_trades_db_path() -> str:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.abspath(os.path.join(project_root, "data", "ipl_master.sqlite"))


def _legacy_ipl_trades_db_path() -> str:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.abspath(os.path.join(project_root, "data", "ipl_trades.sqlite"))


def _create_sqlite_tables(
    path: str,
    ddl_statements: Sequence[str],
    *,
    table_names: Sequence[str],
) -> None:
    _ensure_parent_dir(path)
    con = _sqlite_connect(path, read_only=False)
    try:
        for ddl in ddl_statements:
            con.execute(ddl)
        con.commit()
    finally:
        con.close()


def _ensure_match_row(con: sqlite3.Connection, match: Match) -> dict[str, object]:
    values = match.to_db_values()
    key_values = [
        values["season"],
        values["match_date"],
        values["team_1"],
        values["team_2"],
    ]
    con.execute(
        """
        INSERT OR IGNORE INTO matches (
            season,
            match_date,
            team_1,
            team_2,
            stadium,
            toss_winner,
            toss_decision
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            values["season"],
            values["match_date"],
            values["team_1"],
            values["team_2"],
            values["stadium"],
            values["toss_winner"],
            values["toss_decision"],
        ],
    )
    result = con.execute(
        """
        SELECT id, season, match_date, team_1, team_2, stadium, toss_winner, toss_decision
        FROM matches
        WHERE season = ? AND match_date = ? AND team_1 = ? AND team_2 = ?
        """,
        key_values,
    ).fetchone()
    if result is None:
        raise RuntimeError("Match insert returned no row")
    columns = [
        "id",
        "season",
        "match_date",
        "team_1",
        "team_2",
        "stadium",
        "toss_winner",
        "toss_decision",
    ]
    match_row = dict(zip(columns, result))
    con.execute(
        """
        UPDATE matches
        SET stadium = ?, toss_winner = ?, toss_decision = ?
        WHERE id = ?
        """,
        [
            values["stadium"],
            values["toss_winner"],
            values["toss_decision"],
            match_row["id"],
        ],
    )
    refreshed = con.execute(
        """
        SELECT id, season, match_date, team_1, team_2, stadium, toss_winner, toss_decision
        FROM matches
        WHERE id = ?
        """,
        [match_row["id"]],
    ).fetchone()
    if refreshed is None:
        raise RuntimeError("Match refresh returned no row")
    return dict(zip(columns, refreshed))


class BetRow(TypedDict):
    id: int
    trade_id: int
    team: str
    bet_type: str
    odds_paise: int
    odds_decimal: float
    stake: float
    liability: float
    is_open: bool
    created_at: str


TEAM_ACRONYMS: dict[str, str] = {
    "Chennai Super Kings": "CSK",
    "Delhi Capitals": "DC",
    "Gujarat Titans": "GT",
    "Kolkata Knight Riders": "KKR",
    "Lucknow Super Giants": "LSG",
    "Mumbai Indians": "MI",
    "Punjab Kings": "PBKS",
    "Rajasthan Royals": "RR",
    "Royal Challengers Bengaluru": "RCB",
    "Sunrisers Hyderabad": "SRH",
}


_DDL_LOOKUP = """
CREATE TABLE IF NOT EXISTS teams (
    season  INTEGER NOT NULL,
    name    VARCHAR NOT NULL,
    acronym VARCHAR,
    PRIMARY KEY (season, name)
)
"""

_DDL_VENUES = """
CREATE TABLE IF NOT EXISTS venues (
    season      INTEGER NOT NULL,
    venue_code  VARCHAR NOT NULL,
    venue_label VARCHAR NOT NULL,
    PRIMARY KEY (season, venue_code)
)
"""

_DDL_MATCHES_SQLITE = """
CREATE TABLE IF NOT EXISTS matches (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    season       INTEGER NOT NULL,
    match_date   TEXT NOT NULL DEFAULT '',
    team_1       TEXT NOT NULL,
    team_2       TEXT NOT NULL,
    stadium      TEXT NOT NULL,
    toss_winner  TEXT,
    toss_decision TEXT CHECK (toss_decision IN ('', 'bat', 'field') OR toss_decision IS NULL),
    UNIQUE (season, match_date, team_1, team_2)
)
"""

def _ddl_trades_sqlite(table_name: str = "trades") -> str:
    return f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    id                        INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id                  INTEGER   NOT NULL,
    favourite_team            TEXT      NOT NULL,
    home_ground               TEXT      NOT NULL
                                  CHECK (home_ground IN ('FAV', 'UG', 'NEU')),
    bankroll                  REAL      NOT NULL DEFAULT 100.0,
    opening_odds              REAL,
    bullet_05_odds            REAL,
    bullet_05_stake           REAL,
    bullet_1_odds             REAL,
    bullet_1_stake            REAL,
    bullet_2_odds             REAL,
    bullet_2_stake            REAL,
    bullet_3_odds             REAL,
    bullet_3_stake            REAL,
    total_stake               REAL,
    target_profit             REAL,
    profit_80pct              REAL,
    exit_target_odds          REAL,
    breakeven_odds            REAL,
    pct_of_target             REAL,
    pct_return_on_stake       REAL,
    exit_odds                 REAL,
    fav_reached_130           INTEGER   NOT NULL DEFAULT 0,
    is_fake_favourite         INTEGER   NOT NULL DEFAULT 0,
    notes                     TEXT,
    crex_url                  TEXT,
    selected_team_before_toss TEXT,
    back_odds_before_toss     INTEGER,
    lay_odds_before_toss      INTEGER,
    selected_team_after_toss  TEXT,
    back_odds_after_toss      INTEGER,
    lay_odds_after_toss       INTEGER,
    result                    TEXT,
    winner                    TEXT,
    actual_profit             REAL,
    trade_sentiment           TEXT
                                  CHECK (trade_sentiment IN ('saved', 'satisfied', 'lost', 'achieved')),
    fav_sub_30_loss           INTEGER   NOT NULL DEFAULT 0,
    missed_swing_team         TEXT,
    missed_swing_back_odds    INTEGER,
    missed_swing_lay_odds     INTEGER,
    missed_swing_bet_index    INTEGER,
    missed_swing_cumulative_stake REAL,
    missed_swing_net_pnl      REAL,
    trade_mistakes            TEXT,
    targeted_pnl              REAL,
    achieved_yield_percentage REAL,
    total_volume_wagered      REAL      NOT NULL DEFAULT 0.0,
    status                    TEXT      NOT NULL DEFAULT 'DRAFT'
                                  CHECK (status IN ('DRAFT', 'ACTIVE', 'SETTLED', 'VOID')),
    created_at                TEXT      NOT NULL,
    updated_at                TEXT      NOT NULL,
    FOREIGN KEY (match_id) REFERENCES matches(id)
)
"""

_DDL_BETS_SQLITE = """
CREATE TABLE IF NOT EXISTS bets (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id     INTEGER NOT NULL,
    team         TEXT NOT NULL,
    bet_type     TEXT NOT NULL CHECK (bet_type IN ('BACK', 'LAY')),
    odds_paise   INTEGER NOT NULL,
    odds_decimal REAL NOT NULL,
    stake        REAL NOT NULL,
    liability    REAL NOT NULL,
    is_open      INTEGER NOT NULL DEFAULT 1,
    created_at   TEXT NOT NULL,
    FOREIGN KEY (trade_id) REFERENCES trades(id) ON DELETE CASCADE
)
"""

_DDL_COCKPIT_META_SQLITE = """
CREATE TABLE IF NOT EXISTS cockpit_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
)
"""

_DDL_SQLITE_TABLES = (
    _DDL_LOOKUP,
    _DDL_VENUES,
    _DDL_MATCHES_SQLITE,
    _ddl_trades_sqlite(),
    _DDL_BETS_SQLITE,
)

_DDL_TRADE_SQLITE_TABLES = (
    _DDL_MATCHES_SQLITE,
    _ddl_trades_sqlite(),
    _DDL_BETS_SQLITE,
)

_TRADE_REQUIRED_COLUMNS = {
    "favourite_team",
    "home_ground",
    "status",
    "created_at",
    "updated_at",
    "fav_sub_30_loss",
    "missed_swing_team",
    "missed_swing_back_odds",
    "missed_swing_lay_odds",
    "missed_swing_bet_index",
    "missed_swing_cumulative_stake",
    "missed_swing_net_pnl",
    "trade_mistakes",
}

_TRADE_LEGACY_COLUMNS = {
    "lowest_fav_odds_paise",
    "post_low_bet_number",
    "post_low_bet_stake",
}


def _database_paths_are_ready(format_key: str, lookup_path: str, trades_path: str) -> bool:
    fmt = format_key.strip().lower()
    cached_paths = _INITIALIZED_DATABASES.get(fmt)
    if cached_paths != (lookup_path, trades_path):
        return False

    if fmt == "ipl":
        return _duckdb_lookup_has_tables(lookup_path) and _sqlite_trade_database_ready(
            trades_path,
            require_lookup_tables=False,
        )
    if fmt == "odi":
        return _sqlite_trade_database_ready(
            lookup_path,
            require_lookup_tables=True,
        )
    return False


def get_db_path(format_key: str) -> str:
    """Return the absolute path to the cockpit lookup database."""
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
    """Return the absolute path to the cockpit trade database."""
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


def get_supported_cockpit_formats() -> tuple[str, ...]:
    """Return the cockpit format keys that have storage paths configured."""
    return tuple(_FORMAT_DB_DEFAULT.keys())


def _duckdb_table_names(con: duckdb.DuckDBPyConnection) -> set[str]:
    rows = con.execute("SHOW TABLES").fetchall()
    return {str(row[0]) for row in rows}


def _duckdb_table_columns(con: duckdb.DuckDBPyConnection, table_name: str) -> list[str]:
    rows = con.execute(f"PRAGMA table_info('{table_name}')").fetchall()
    return [str(row[1]) for row in rows]


def _duckdb_lookup_needs_setup(path: str) -> bool:
    if not os.path.exists(path):
        return True

    con = duckdb.connect(path, read_only=True)
    try:
        table_names = _duckdb_table_names(con)
        if "teams" not in table_names or "venues" not in table_names:
            return True
        return "acronym" not in _duckdb_table_columns(con, "teams")
    finally:
        con.close()


def _duckdb_lookup_has_tables(path: str) -> bool:
    if not os.path.exists(path):
        return False

    con = duckdb.connect(path, read_only=True)
    try:
        table_names = _duckdb_table_names(con)
        return "teams" in table_names and "venues" in table_names
    finally:
        con.close()


def migrate_lookup_db(format_key: str) -> None:
    """Add acronym column to teams table and populate it from TEAM_ACRONYMS."""
    fmt = format_key.strip().lower()
    lookup_path = get_db_path(fmt)
    if not os.path.exists(lookup_path):
        return

    con = duckdb.connect(lookup_path, read_only=True)
    try:
        table_names = _duckdb_table_names(con)
        if "teams" not in table_names or "venues" not in table_names:
            return
        if "acronym" in _duckdb_table_columns(con, "teams"):
            return
    finally:
        con.close()

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


def _sqlite_trade_table_needs_rebuild(con: sqlite3.Connection) -> bool:
    trades_columns = set(_sqlite_table_columns(con, "trades"))
    if not trades_columns:
        return False
    if _TRADE_LEGACY_COLUMNS.intersection(trades_columns):
        return True
    return not _TRADE_REQUIRED_COLUMNS.issubset(trades_columns)


def _sqlite_rebuild_trades_table(path: str) -> None:
    con = sqlite3.connect(path, check_same_thread=False)
    try:
        if "trades" not in _table_names_sqlite(con):
            return
        if not _sqlite_trade_table_needs_rebuild(con):
            return

        con.execute("PRAGMA foreign_keys = OFF")
        con.execute("BEGIN")
        try:
            con.execute("ALTER TABLE trades RENAME TO trades_legacy")
            con.execute(_ddl_trades_sqlite())

            new_columns = _sqlite_table_columns(con, "trades")
            legacy_columns = _sqlite_table_columns(con, "trades_legacy")
            insert_columns = [column for column in new_columns if column in legacy_columns]
            if not insert_columns:
                raise RuntimeError("Could not determine trade columns for migration")

            column_sql = ", ".join(insert_columns)
            con.execute(
                f"INSERT INTO trades ({column_sql}) SELECT {column_sql} FROM trades_legacy"
            )
            con.execute("DROP TABLE trades_legacy")

            max_id_row = con.execute("SELECT MAX(id) FROM trades").fetchone()
            max_id = int(max_id_row[0]) if max_id_row and max_id_row[0] is not None else None
            if max_id is not None:
                try:
                    con.execute(
                        "INSERT OR REPLACE INTO sqlite_sequence (name, seq) VALUES (?, ?)",
                        ["trades", max_id],
                    )
                except sqlite3.OperationalError:
                    pass

            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.execute("PRAGMA foreign_keys = ON")
    finally:
        con.close()


def migrate_trades_db(format_key: str) -> None:
    """Ensure SQLite trade tables exist and legacy columns are removed."""
    fmt = format_key.strip().lower()
    if fmt == "odi":
        path = get_db_path(fmt)
        _create_sqlite_tables(
            path,
            _DDL_SQLITE_TABLES,
            table_names=("bets", "trades", "matches", "teams", "venues"),
        )
        _sqlite_rebuild_trades_table(path)
        return

    trades_path = get_trades_db_path(fmt)
    _create_sqlite_tables(
        trades_path,
        _DDL_TRADE_SQLITE_TABLES,
        table_names=("bets", "trades", "matches"),
    )
    _sqlite_rebuild_trades_table(trades_path)


def _seed_ipl_trade_history_if_needed(format_key: str) -> None:
    """Seed the new IPL master store from the existing trade file when empty."""
    fmt = format_key.strip().lower()
    if fmt != "ipl":
        return

    trades_path = get_trades_db_path(fmt)
    if trades_path != _default_ipl_trades_db_path():
        return
    if not os.path.exists(trades_path):
        return

    con = sqlite3.connect(trades_path, check_same_thread=False)
    try:
        con.execute(_DDL_COCKPIT_META_SQLITE)
        marker_row = con.execute(
            "SELECT value FROM cockpit_meta WHERE key = ?",
            ["ipl_legacy_history_seeded"],
        ).fetchone()
        if marker_row is not None:
            return

        existing_count = int(con.execute("SELECT COUNT(*) FROM trades").fetchone()[0])
        if existing_count > 0:
            con.execute(
                "INSERT OR REPLACE INTO cockpit_meta (key, value) VALUES (?, ?)",
                ["ipl_legacy_history_seeded", _datetime.now(timezone.utc).isoformat()],
            )
            con.commit()
            return
    finally:
        con.close()

    source_path = _legacy_ipl_trades_db_path()
    if not os.path.exists(source_path) or os.path.samefile(source_path, trades_path):
        return

    source_con = sqlite3.connect(source_path, check_same_thread=False)
    try:
        source_tables = _table_names_sqlite(source_con)
        if "trades" not in source_tables or "bets" not in source_tables:
            return

        trade_rows = source_con.execute("SELECT * FROM trades ORDER BY id ASC").fetchall()
        if not trade_rows:
            return

        trade_columns = [
            str(row[1])
            for row in source_con.execute("PRAGMA table_info(trades)").fetchall()
        ]
        bet_columns = [
            str(row[1])
            for row in source_con.execute("PRAGMA table_info(bets)").fetchall()
        ]
        trade_records = [dict(zip(trade_columns, row)) for row in trade_rows]
        bet_records = [
            dict(zip(bet_columns, row))
            for row in source_con.execute("SELECT * FROM bets ORDER BY id ASC").fetchall()
        ]
    finally:
        source_con.close()

    store = CockpitStore(fmt, read_only=False)
    try:
        trade_id_map: dict[int, int] = {}
        for record in trade_records:
            source_trade_id = record.get("id")
            if source_trade_id is None:
                continue

            trade = Trade(
                season=int(record.get("season", 0) or 0),
                match_date=_parse_iso_datetime(record.get("match_date")),
                team_1=str(record.get("team_1", "")),
                team_2=str(record.get("team_2", "")),
                favourite_team=str(record.get("favourite_team", "")),
                home_ground=str(record.get("home_ground", "")),
                stadium=str(record.get("stadium", "")),
                status=str(record.get("status", "DRAFT")),
                toss_winner=_coerce_optional_text(record.get("toss_winner")),
                toss_decision=_coerce_optional_text(record.get("toss_decision")),
                bankroll=float(record.get("bankroll", 100.0) or 0.0),
                opening_odds=(
                    float(record["opening_odds"])
                    if record.get("opening_odds") is not None
                    else None
                ),
                fav_reached_130=bool(record.get("fav_reached_130", 0)),
                is_fake_favourite=bool(record.get("is_fake_favourite", 0)),
                notes=_coerce_optional_text(record.get("notes")),
                crex_url=_coerce_optional_text(record.get("crex_url")),
                selected_team_before_toss=_coerce_optional_text(
                    record.get("selected_team_before_toss")
                ),
                back_odds_before_toss=(
                    int(record["back_odds_before_toss"])
                    if record.get("back_odds_before_toss") is not None
                    else None
                ),
                lay_odds_before_toss=(
                    int(record["lay_odds_before_toss"])
                    if record.get("lay_odds_before_toss") is not None
                    else None
                ),
                selected_team_after_toss=_coerce_optional_text(
                    record.get("selected_team_after_toss")
                ),
                back_odds_after_toss=(
                    int(record["back_odds_after_toss"])
                    if record.get("back_odds_after_toss") is not None
                    else None
                ),
                lay_odds_after_toss=(
                    int(record["lay_odds_after_toss"])
                    if record.get("lay_odds_after_toss") is not None
                    else None
                ),
                result=_coerce_optional_text(record.get("result")),
                winner=_coerce_optional_text(record.get("winner")),
                actual_profit=(
                    float(record["actual_profit"])
                    if record.get("actual_profit") is not None
                    else None
                ),
                trade_sentiment=cast(
                    TradeSentiment | None,
                    _coerce_optional_text(record.get("trade_sentiment")),
                ),
                fav_sub_30_loss=bool(record.get("fav_sub_30_loss", 0)),
                targeted_pnl=(
                    float(record["targeted_pnl"])
                    if record.get("targeted_pnl") is not None
                    else None
                ),
                achieved_yield_percentage=(
                    float(record["achieved_yield_percentage"])
                    if record.get("achieved_yield_percentage") is not None
                    else None
                ),
                total_volume_wagered=(
                    float(record["total_volume_wagered"])
                    if record.get("total_volume_wagered") is not None
                    else 0.0
                ),
                created_at=_parse_iso_datetime(record.get("created_at"))
                or _datetime.now(timezone.utc),
                updated_at=_parse_iso_datetime(record.get("updated_at"))
                or _datetime.now(timezone.utc),
            )

            inserted_trade = store.insert_trade(trade)
            if inserted_trade.id is None:
                continue
            trade_id_map[int(source_trade_id)] = inserted_trade.id

        for record in bet_records:
            source_trade_id = record.get("trade_id")
            if source_trade_id is None:
                continue
            dest_trade_id = trade_id_map.get(int(source_trade_id))
            if dest_trade_id is None:
                continue

            store.insert_bet(
                trade_id=dest_trade_id,
                team=str(record.get("team", "")),
                bet_type=str(record.get("bet_type", "")),
                odds_paise=int(record.get("odds_paise", 0) or 0),
                odds_decimal=float(record.get("odds_decimal", 0.0) or 0.0),
                stake=float(record.get("stake", 0.0) or 0.0),
                liability=float(record.get("liability", 0.0) or 0.0),
                is_open=bool(record.get("is_open", 1)),
                created_at=str(record.get("created_at", "")),
            )
        store._trades_con.execute(_DDL_COCKPIT_META_SQLITE)
        store._trades_con.execute(
            "INSERT OR REPLACE INTO cockpit_meta (key, value) VALUES (?, ?)",
            ["ipl_legacy_history_seeded", _datetime.now(timezone.utc).isoformat()],
        )
        cast(sqlite3.Connection, store._trades_con).commit()
    finally:
        store.close()


def init_db(format_key: str) -> None:
    """Create cockpit tables for a format and ensure the normalized schema exists."""
    fmt = format_key.strip().lower()
    lookup_path = get_db_path(fmt)
    trades_path = get_trades_db_path(fmt)
    current_paths = (lookup_path, trades_path)

    if _database_paths_are_ready(fmt, lookup_path, trades_path):
        if fmt == "ipl":
            _seed_ipl_trade_history_if_needed(fmt)
        return

    with _INIT_LOCK:
        if _database_paths_are_ready(fmt, lookup_path, trades_path):
            if fmt == "ipl":
                _seed_ipl_trade_history_if_needed(fmt)
            return

        if fmt == "ipl":
            if not _duckdb_lookup_has_tables(lookup_path):
                _ensure_parent_dir(lookup_path)
                con = duckdb.connect(lookup_path)
                try:
                    con.execute(_DDL_LOOKUP)
                    con.execute(_DDL_VENUES)
                finally:
                    con.close()
            elif _duckdb_lookup_needs_setup(lookup_path):
                migrate_lookup_db(fmt)

            migrate_trades_db(fmt)
            _seed_ipl_trade_history_if_needed(fmt)
        elif fmt == "odi":
            migrate_trades_db(fmt)
        else:
            migrate_trades_db(fmt)

        _INITIALIZED_DATABASES[fmt] = current_paths


class CockpitStore:
    """Repository for one format's cockpit data."""

    def __init__(self, format_key: str = "ipl", *, read_only: bool = False) -> None:
        self.format_key = format_key.strip().lower()
        self.path = get_db_path(self.format_key)
        self.trades_path = get_trades_db_path(self.format_key)
        self._read_only = read_only
        self._con: duckdb.DuckDBPyConnection | sqlite3.Connection
        self._trades_con: duckdb.DuckDBPyConnection | sqlite3.Connection

        self._con = self._open_lookup_connection(read_only=read_only)
        if self.trades_path == self.path:
            self._trades_con = self._con
        else:
            self._trades_con = self._open_trades_connection(read_only=read_only)

    def _open_lookup_connection(self, *, read_only: bool) -> duckdb.DuckDBPyConnection | sqlite3.Connection:
        if self.format_key == "odi":
            _ensure_parent_dir(self.path)
            return _sqlite_connect(self.path, read_only=read_only)
        _ensure_parent_dir(self.path)
        return duckdb.connect(self.path, read_only=True)

    def _open_trades_connection(self, *, read_only: bool) -> sqlite3.Connection:
        _ensure_parent_dir(self.trades_path)
        return _sqlite_connect(self.trades_path, read_only=read_only)

    def close(self) -> None:
        self._con.close()
        if self._trades_con is not self._con:
            self._trades_con.close()

    def ensure_match(self, match: Match) -> Match:
        connection = cast(sqlite3.Connection, self._trades_con)
        match_row = _ensure_match_row(connection, match)
        return Match.from_row(cast(dict[str, TradeDbValue], match_row))

    def _trade_row_query(self) -> str:
        return """
            SELECT
                t.*,
                m.season,
                m.match_date,
                m.team_1,
                m.team_2,
                m.stadium,
                m.toss_winner,
                m.toss_decision
            FROM trades t
            JOIN matches m ON t.match_id = m.id
        """

    def insert_trade(self, trade: Trade) -> Trade:
        match = self.ensure_match(trade.to_match())
        if match.id is None:
            raise RuntimeError("Match insert returned no id")
        trade.match_id = match.id
        values = trade.to_db_values()
        columns = ", ".join(TRADE_WRITE_COLUMNS)
        placeholders = ", ".join("?" for _ in TRADE_WRITE_COLUMNS)
        ordered_values = [values[column] for column in TRADE_WRITE_COLUMNS]
        sql = f"INSERT INTO trades ({columns}) VALUES ({placeholders})"
        with cast(sqlite3.Connection, self._trades_con):
            cursor = cast(sqlite3.Connection, self._trades_con).execute(sql, ordered_values)
            if cursor.lastrowid is None:
                raise RuntimeError("INSERT returned no trade id")
            trade.id = int(cursor.lastrowid)
        stored = self.get_trade(trade.id)
        return stored if stored is not None else trade

    def update_trade(self, trade: Trade) -> Trade:
        if trade.id is None:
            raise ValueError("Trade id is required for update.")
        match = self.ensure_match(trade.to_match())
        if match.id is None:
            raise RuntimeError("Match insert returned no id")
        trade.match_id = match.id
        values = trade.to_db_values()
        assignments = ", ".join(f"{col} = ?" for col in TRADE_WRITE_COLUMNS)
        ordered_values = [values[column] for column in TRADE_WRITE_COLUMNS]
        sql = f"UPDATE trades SET {assignments} WHERE id = ?"
        with cast(sqlite3.Connection, self._trades_con):
            cast(sqlite3.Connection, self._trades_con).execute(sql, [*ordered_values, trade.id])
        stored = self.get_trade(trade.id)
        return stored if stored is not None else trade

    def delete_trade(self, trade_id: int) -> None:
        connection = cast(sqlite3.Connection, self._trades_con)
        match_row = connection.execute(
            "SELECT match_id FROM trades WHERE id = ?",
            [trade_id],
        ).fetchone()
        if match_row is None:
            return

        match_id = match_row[0]
        with connection:
            connection.execute("DELETE FROM trades WHERE id = ?", [trade_id])
            if match_id is None:
                return

            remaining_trade_row = connection.execute(
                "SELECT COUNT(*) FROM trades WHERE match_id = ?",
                [match_id],
            ).fetchone()
            remaining_trade_count = int(remaining_trade_row[0]) if remaining_trade_row else 0
            if remaining_trade_count == 0:
                connection.execute("DELETE FROM matches WHERE id = ?", [match_id])

    def get_trade(self, trade_id: int) -> Trade | None:
        result = cast(sqlite3.Connection, self._trades_con).execute(
            f"{self._trade_row_query()} WHERE t.id = ?",
            [trade_id],
        )
        row = result.fetchone()
        if row is None:
            return None
        columns = [column[0] for column in result.description or ()]
        return Trade.from_row(dict(zip(columns, row)))

    def list_trades(
        self,
        *,
        season: int | None = None,
        statuses: Sequence[str] | None = None,
        order: str = "DESC",
    ) -> list[Trade]:
        clauses: list[str] = []
        params: list[int | float | str | bool | None] = []

        if season is not None:
            clauses.append("m.season = ?")
            params.append(season)
        if statuses is not None:
            normalized_statuses = [status for status in statuses if status]
            if normalized_statuses:
                if len(normalized_statuses) == 1:
                    clauses.append("t.status = ?")
                    params.append(normalized_statuses[0])
                else:
                    placeholders = ", ".join("?" for _ in normalized_statuses)
                    clauses.append(f"t.status IN ({placeholders})")
                    params.extend(normalized_statuses)

        sql = self._trade_row_query()
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        direction = "ASC" if order.upper() == "ASC" else "DESC"
        sql += f" ORDER BY t.created_at {direction}, t.id {direction}"

        result_set = cast(sqlite3.Connection, self._trades_con).execute(sql, params)
        columns = [column[0] for column in result_set.description or ()]
        return [Trade.from_row(dict(zip(columns, row))) for row in result_set.fetchall()]

    def insert_bet(
        self,
        *,
        trade_id: int,
        team: str,
        bet_type: str,
        odds_paise: int,
        odds_decimal: float,
        stake: float,
        liability: float,
        is_open: bool,
        created_at: str,
    ) -> BetRow:
        connection = cast(sqlite3.Connection, self._trades_con)
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO bets (
                    trade_id,
                    team,
                    bet_type,
                    odds_paise,
                    odds_decimal,
                    stake,
                    liability,
                    is_open,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    trade_id,
                    team,
                    bet_type,
                    odds_paise,
                    odds_decimal,
                    stake,
                    liability,
                    int(is_open),
                    created_at,
                ],
            )
            if cursor.lastrowid is None:
                raise RuntimeError("INSERT returned no bet id")
            bet_id = int(cursor.lastrowid)

        result_cursor = connection.execute(
            "SELECT * FROM bets WHERE trade_id = ? AND id = ?",
            [trade_id, bet_id],
        )
        columns = [column[0] for column in result_cursor.description or ()]
        fetched = result_cursor.fetchone()
        if fetched is None:
            raise RuntimeError("INSERT returned no bet row")
        return cast(BetRow, dict(zip(columns, fetched)))

    def list_bets(self, trade_id: int) -> list[BetRow]:
        result = cast(sqlite3.Connection, self._trades_con).execute(
            "SELECT * FROM bets WHERE trade_id = ? ORDER BY id ASC",
            [trade_id],
        )
        columns = [column[0] for column in result.description or ()]
        return [cast(BetRow, dict(zip(columns, row))) for row in result.fetchall()]

    def get_bet(self, trade_id: int, bet_id: int) -> BetRow | None:
        result = cast(sqlite3.Connection, self._trades_con).execute(
            "SELECT * FROM bets WHERE trade_id = ? AND id = ?",
            [trade_id, bet_id],
        )
        row = result.fetchone()
        if row is None:
            return None
        columns = [column[0] for column in result.description or ()]
        return cast(BetRow, dict(zip(columns, row)))

    def close_bet(self, trade_id: int, bet_id: int) -> BetRow | None:
        current = self.get_bet(trade_id, bet_id)
        if current is None:
            return None
        with cast(sqlite3.Connection, self._trades_con):
            cast(sqlite3.Connection, self._trades_con).execute(
                "UPDATE bets SET is_open = 0 WHERE trade_id = ? AND id = ?",
                [trade_id, bet_id],
            )
        return self.get_bet(trade_id, bet_id)

    def delete_bet(self, trade_id: int, bet_id: int) -> bool:
        connection = cast(sqlite3.Connection, self._trades_con)
        with connection:
            cursor = connection.execute(
                "DELETE FROM bets WHERE trade_id = ? AND id = ?",
                [trade_id, bet_id],
            )
        return cursor.rowcount > 0

    def get_teams(self) -> list[str]:
        rows = cast(duckdb.DuckDBPyConnection | sqlite3.Connection, self._con).execute(
            "SELECT DISTINCT acronym FROM teams WHERE acronym IS NOT NULL ORDER BY acronym"
        ).fetchall()
        return [str(row[0]) for row in rows]

    def get_venues(self) -> list[dict[str, str]]:
        rows = cast(duckdb.DuckDBPyConnection | sqlite3.Connection, self._con).execute(
            """
            SELECT venue_code, MIN(venue_label) AS venue_label
            FROM venues
            GROUP BY venue_code
            ORDER BY venue_label
            """
        ).fetchall()
        return [{"id": str(row[0]), "label": str(row[1])} for row in rows]


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
