from __future__ import annotations

from collections.abc import Generator
from datetime import datetime, timezone
from pathlib import Path
import shutil

import sqlite3
import pytest
from fastapi.testclient import TestClient

from api.main import app
from cockpit.database import (
    CockpitStore,
    get_trades_db_path,
    migrate_trades_db,
)
from cockpit.models import Trade


COCKPIT_TEST_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
COCKPIT_TEST_LOOKUP_DB_PATH = COCKPIT_TEST_DATA_DIR / "cockpit-lookup-test.duckdb"
COCKPIT_TEST_TRADES_DB_PATH = COCKPIT_TEST_DATA_DIR / "cockpit-trades-test.sqlite"
COCKPIT_TEST_FINANCES_DB_PATH = COCKPIT_TEST_DATA_DIR / "cockpit-finances-test.sqlite"
COCKPIT_TEST_INITIAL_BANK_BALANCE = 70560.67
COCKPIT_TEST_INITIAL_WALLET_BALANCE = 29980.76
COCKPIT_TEST_INITIAL_BANK_DEPOSIT = 100541.43


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    source_lookup_db_path = COCKPIT_TEST_DATA_DIR / "ipl.duckdb"

    if COCKPIT_TEST_LOOKUP_DB_PATH.exists():
        COCKPIT_TEST_LOOKUP_DB_PATH.unlink()
    if COCKPIT_TEST_TRADES_DB_PATH.exists():
        COCKPIT_TEST_TRADES_DB_PATH.unlink()
    if COCKPIT_TEST_FINANCES_DB_PATH.exists():
        COCKPIT_TEST_FINANCES_DB_PATH.unlink()
    shutil.copy2(source_lookup_db_path, COCKPIT_TEST_LOOKUP_DB_PATH)
    monkeypatch.setenv("IPL_COCKPIT_DB_PATH", str(COCKPIT_TEST_LOOKUP_DB_PATH))
    monkeypatch.setenv("IPL_COCKPIT_TRADES_DB_PATH", str(COCKPIT_TEST_TRADES_DB_PATH))
    monkeypatch.setenv("FINANCES_DB_PATH", str(COCKPIT_TEST_FINANCES_DB_PATH))
    with TestClient(app) as test_client:
        finances = getattr(app.state, "finances", None)
        if finances is not None:
            balances = finances.get_balances()
            if balances["bank"] == 0.0 and balances["wallet"] == 0.0:
                finances.deposit_to_bank(COCKPIT_TEST_INITIAL_BANK_DEPOSIT)
                finances.topup_wallet(COCKPIT_TEST_INITIAL_WALLET_BALANCE)
        yield test_client
    if COCKPIT_TEST_LOOKUP_DB_PATH.exists():
        COCKPIT_TEST_LOOKUP_DB_PATH.unlink()
    if COCKPIT_TEST_TRADES_DB_PATH.exists():
        COCKPIT_TEST_TRADES_DB_PATH.unlink()
    if COCKPIT_TEST_FINANCES_DB_PATH.exists():
        COCKPIT_TEST_FINANCES_DB_PATH.unlink()


def test_cockpit_ipl_trades_default_path_points_to_master_file(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("IPL_COCKPIT_TRADES_DB_PATH", raising=False)
    default_path = Path(get_trades_db_path("ipl"))
    assert default_path.name == "ipl_master.sqlite"
    assert default_path.parent.name == "data"


def test_cockpit_ipl_trades_db_path_override_is_respected(monkeypatch: pytest.MonkeyPatch) -> None:
    override_path = Path.cwd() / "temp_pytest" / "cockpit-trades-override.sqlite"
    monkeypatch.setenv("IPL_COCKPIT_TRADES_DB_PATH", str(override_path))

    resolved_path = Path(get_trades_db_path("ipl"))

    assert resolved_path == override_path.resolve()
    assert resolved_path.name == "cockpit-trades-override.sqlite"


def test_cockpit_init_db_seeds_the_default_ipl_trade_history(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace_tmp = Path.cwd() / "temp_pytest"
    workspace_tmp.mkdir(exist_ok=True)

    lookup_db_path = workspace_tmp / "cockpit-lookup-seed-test.duckdb"
    trades_db_path = workspace_tmp / "cockpit-trades-seed-test.sqlite"

    if lookup_db_path.exists():
        lookup_db_path.unlink()
    if trades_db_path.exists():
        trades_db_path.unlink()

    shutil.copy2(COCKPIT_TEST_DATA_DIR / "ipl.duckdb", lookup_db_path)
    monkeypatch.setenv("IPL_COCKPIT_DB_PATH", str(lookup_db_path))
    monkeypatch.setenv("IPL_COCKPIT_TRADES_DB_PATH", str(trades_db_path))
    monkeypatch.setattr(
        "cockpit.database._default_ipl_trades_db_path",
        lambda: str(trades_db_path.resolve()),
    )

    from cockpit.database import init_db

    init_db("ipl")

    con = sqlite3.connect(trades_db_path)
    try:
        trade_count = con.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
        bet_count = con.execute("SELECT COUNT(*) FROM bets").fetchone()[0]
    finally:
        con.close()

    assert trade_count > 0
    assert bet_count > 0


def test_cockpit_init_db_does_not_reseed_after_all_trades_are_deleted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace_tmp = Path.cwd() / "temp_pytest"
    workspace_tmp.mkdir(exist_ok=True)

    lookup_db_path = workspace_tmp / "cockpit-lookup-reseed-test.duckdb"
    trades_db_path = workspace_tmp / "cockpit-trades-reseed-test.sqlite"

    if lookup_db_path.exists():
        lookup_db_path.unlink()
    if trades_db_path.exists():
        trades_db_path.unlink()

    shutil.copy2(COCKPIT_TEST_DATA_DIR / "ipl.duckdb", lookup_db_path)
    monkeypatch.setenv("IPL_COCKPIT_DB_PATH", str(lookup_db_path))
    monkeypatch.setenv("IPL_COCKPIT_TRADES_DB_PATH", str(trades_db_path))
    monkeypatch.setattr(
        "cockpit.database._default_ipl_trades_db_path",
        lambda: str(trades_db_path.resolve()),
    )

    from cockpit.database import init_db

    init_db("ipl")

    con = sqlite3.connect(trades_db_path)
    try:
        trade_ids = [
            int(row[0])
            for row in con.execute("SELECT id FROM trades ORDER BY id ASC").fetchall()
        ]
        seeded_trade_count = con.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
    finally:
        con.close()

    assert seeded_trade_count > 0

    store = CockpitStore("ipl", read_only=False)
    try:
        for trade_id in trade_ids:
            store.delete_trade(trade_id)
    finally:
        store.close()

    con = sqlite3.connect(trades_db_path)
    try:
        empty_trade_count = con.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
        empty_bet_count = con.execute("SELECT COUNT(*) FROM bets").fetchone()[0]
    finally:
        con.close()

    assert empty_trade_count == 0
    assert empty_bet_count == 0

    init_db("ipl")

    con = sqlite3.connect(trades_db_path)
    try:
        reseeded_trade_count = con.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
        reseeded_bet_count = con.execute("SELECT COUNT(*) FROM bets").fetchone()[0]
    finally:
        con.close()

    assert reseeded_trade_count == 0
    assert reseeded_bet_count == 0


def test_cockpit_migrate_trades_db_rebuilds_stale_relational_schema(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace_tmp = Path.cwd() / "temp_pytest"
    workspace_tmp.mkdir(exist_ok=True)

    trades_db_path = workspace_tmp / "cockpit-stale-schema.sqlite"
    if trades_db_path.exists():
        trades_db_path.unlink()
    monkeypatch.setenv("IPL_COCKPIT_TRADES_DB_PATH", str(trades_db_path))

    stale_con = sqlite3.connect(trades_db_path)
    try:
        stale_con.execute(
            """
            CREATE TABLE matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                season INTEGER NOT NULL,
                match_date TEXT NOT NULL DEFAULT '',
                team_1 TEXT NOT NULL,
                team_2 TEXT NOT NULL,
                stadium TEXT NOT NULL,
                toss_winner TEXT,
                toss_decision TEXT,
                UNIQUE (season, match_date, team_1, team_2)
            )
            """
        )
        stale_con.execute(
            """
            CREATE TABLE trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                favourite_team TEXT NOT NULL,
                home_ground TEXT NOT NULL,
                bankroll REAL NOT NULL DEFAULT 100.0,
                status TEXT NOT NULL DEFAULT 'DRAFT',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (match_id) REFERENCES matches(id)
            )
            """
        )
        stale_con.execute(
            """
            CREATE TABLE bets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id INTEGER NOT NULL,
                team TEXT NOT NULL,
                bet_type TEXT NOT NULL,
                odds_paise INTEGER NOT NULL,
                odds_decimal REAL NOT NULL,
                stake REAL NOT NULL,
                liability REAL NOT NULL,
                is_open INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY (trade_id) REFERENCES trades(id)
            )
            """
        )
        stale_con.execute(
            """
            INSERT INTO matches (
                season,
                match_date,
                team_1,
                team_2,
                stadium
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (2025, "2025-05-01T00:00:00", "PBKS", "RCB", "M. Chinnaswamy Stadium"),
        )
        stale_con.execute(
            """
            INSERT INTO trades (
                match_id,
                favourite_team,
                home_ground,
                bankroll,
                status,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (1, "RCB", "NEU", 100.0, "ACTIVE", "2025-05-01T00:00:00Z", "2025-05-01T00:00:00Z"),
        )
        stale_con.execute(
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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (1, "PBKS", "BACK", 90, 1.9, 100.0, 90.0, 1, "2025-05-01T00:00:00Z"),
        )
        stale_con.commit()
    finally:
        stale_con.close()

    migrate_trades_db("ipl")

    verify_con = sqlite3.connect(trades_db_path)
    try:
        tables = {
            row[0]
            for row in verify_con.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        assert {"matches", "trades", "bets"}.issubset(tables)

        match_columns = {
            str(row[1]): row
            for row in verify_con.execute("PRAGMA table_info(matches)").fetchall()
        }
        trade_columns = {
            str(row[1]): row
            for row in verify_con.execute("PRAGMA table_info(trades)").fetchall()
        }
        bet_columns = {
            str(row[1]): row
            for row in verify_con.execute("PRAGMA table_info(bets)").fetchall()
        }

        assert int(match_columns["match_date"][3]) == 1
        assert int(trade_columns["match_id"][3]) == 1
        assert int(bet_columns["trade_id"][3]) == 1

        assert "missed_swing_team" in trade_columns
        assert "lowest_fav_odds_paise" not in trade_columns

        assert verify_con.execute("SELECT COUNT(*) FROM matches").fetchone()[0] == 1
        assert verify_con.execute("SELECT COUNT(*) FROM trades").fetchone()[0] == 1
        assert verify_con.execute("SELECT COUNT(*) FROM bets").fetchone()[0] == 1
    finally:
        verify_con.close()
        if trades_db_path.exists():
            trades_db_path.unlink()


def test_cockpit_migrate_trades_db_rebuilds_stale_bets_foreign_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace_tmp = Path.cwd() / "temp_pytest"
    workspace_tmp.mkdir(exist_ok=True)

    trades_db_path = workspace_tmp / "cockpit-stale-bets-foreign-key.sqlite"
    if trades_db_path.exists():
        trades_db_path.unlink()
    monkeypatch.setenv("IPL_COCKPIT_TRADES_DB_PATH", str(trades_db_path))

    stale_con = sqlite3.connect(trades_db_path)
    try:
        stale_con.execute(
            """
            CREATE TABLE matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                season INTEGER NOT NULL,
                match_date TEXT NOT NULL DEFAULT '',
                team_1 TEXT NOT NULL,
                team_2 TEXT NOT NULL,
                stadium TEXT NOT NULL,
                toss_winner TEXT,
                toss_decision TEXT,
                UNIQUE (season, match_date, team_1, team_2)
            )
            """
        )
        stale_con.execute(
            """
            CREATE TABLE trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                favourite_team TEXT NOT NULL,
                home_ground TEXT NOT NULL,
                bankroll REAL NOT NULL DEFAULT 100.0,
                status TEXT NOT NULL DEFAULT 'DRAFT',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (match_id) REFERENCES matches(id)
            )
            """
        )
        stale_con.execute(
            """
            CREATE TABLE bets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id INTEGER NOT NULL,
                team TEXT NOT NULL,
                bet_type TEXT NOT NULL CHECK (bet_type IN ('BACK', 'LAY')),
                odds_paise INTEGER NOT NULL,
                odds_decimal REAL NOT NULL,
                stake REAL NOT NULL,
                liability REAL NOT NULL,
                is_open INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY (trade_id) REFERENCES trades_legacy(id) ON DELETE CASCADE
            )
            """
        )
        stale_con.execute("PRAGMA foreign_keys = OFF")
        stale_con.execute(
            """
            INSERT INTO matches (
                season,
                match_date,
                team_1,
                team_2,
                stadium
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (2025, "2025-05-01T00:00:00", "PBKS", "RCB", "M. Chinnaswamy Stadium"),
        )
        stale_con.execute(
            """
            INSERT INTO trades (
                match_id,
                favourite_team,
                home_ground,
                bankroll,
                status,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (1, "RCB", "NEU", 100.0, "ACTIVE", "2025-05-01T00:00:00Z", "2025-05-01T00:00:00Z"),
        )
        stale_con.execute(
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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (1, "PBKS", "BACK", 90, 1.9, 100.0, 90.0, 1, "2025-05-01T00:00:00Z"),
        )
        stale_con.commit()
    finally:
        stale_con.close()

    migrate_trades_db("ipl")

    verify_con = sqlite3.connect(trades_db_path)
    try:
        verify_con.execute("PRAGMA foreign_keys = ON")
        tables = {
            row[0]
            for row in verify_con.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        assert {"matches", "trades", "bets"}.issubset(tables)

        fk_rows = verify_con.execute("PRAGMA foreign_key_list(bets)").fetchall()
        assert {str(row[2]) for row in fk_rows} == {"trades"}

        assert verify_con.execute("SELECT COUNT(*) FROM bets").fetchone()[0] == 1

        verify_con.execute(
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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (1, "RCB", "LAY", 95, 1.95, 25.0, 23.75, 1, "2025-05-01T00:10:00Z"),
        )
        verify_con.commit()

        assert verify_con.execute("SELECT COUNT(*) FROM bets").fetchone()[0] == 2
    finally:
        verify_con.close()
        if trades_db_path.exists():
            trades_db_path.unlink()


def test_cockpit_migrate_trades_db_recovers_from_stale_trades_legacy_table(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace_tmp = Path.cwd() / "temp_pytest"
    workspace_tmp.mkdir(exist_ok=True)

    trades_db_path = workspace_tmp / "cockpit-stale-legacy.sqlite"
    if trades_db_path.exists():
        trades_db_path.unlink()
    monkeypatch.setenv("ODI_COCKPIT_DB_PATH", str(trades_db_path))

    stale_con = sqlite3.connect(trades_db_path)
    try:
        stale_con.execute(
            """
            CREATE TABLE matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                season INTEGER NOT NULL,
                match_date TEXT NOT NULL DEFAULT '',
                team_1 TEXT NOT NULL,
                team_2 TEXT NOT NULL,
                stadium TEXT NOT NULL,
                toss_winner TEXT,
                toss_decision TEXT,
                UNIQUE (season, match_date, team_1, team_2)
            )
            """
        )
        stale_con.execute(
            """
            CREATE TABLE trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                favourite_team TEXT NOT NULL,
                home_ground TEXT NOT NULL,
                bankroll REAL NOT NULL DEFAULT 100.0,
                status TEXT NOT NULL DEFAULT 'DRAFT',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (match_id) REFERENCES matches(id)
            )
            """
        )
        stale_con.execute(
            """
            CREATE TABLE trades_legacy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                favourite_team TEXT NOT NULL,
                home_ground TEXT NOT NULL,
                bankroll REAL NOT NULL DEFAULT 100.0,
                status TEXT NOT NULL DEFAULT 'DRAFT',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (match_id) REFERENCES matches(id)
            )
            """
        )
        stale_con.execute(
            """
            INSERT INTO matches (
                season,
                match_date,
                team_1,
                team_2,
                stadium
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (2025, "2025-05-01T00:00:00", "PBKS", "RCB", "M. Chinnaswamy Stadium"),
        )
        stale_con.execute(
            """
            INSERT INTO trades_legacy (
                match_id,
                favourite_team,
                home_ground,
                bankroll,
                status,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (1, "RCB", "NEU", 100.0, "ACTIVE", "2025-05-01T00:00:00Z", "2025-05-01T00:00:00Z"),
        )
        stale_con.commit()
    finally:
        stale_con.close()

    migrate_trades_db("odi")

    verify_con = sqlite3.connect(trades_db_path)
    try:
        tables = {
            row[0]
            for row in verify_con.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        assert "trades_legacy" not in tables
        assert {"matches", "trades", "bets"}.issubset(tables)

        trade_rows = verify_con.execute("PRAGMA table_info(trades)").fetchall()
        trade_columns = {str(row[1]): row for row in trade_rows}
        assert "lowest_fav_odds_paise" not in trade_columns
        assert "missed_swing_team" in trade_columns

        trade_count = verify_con.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
        assert trade_count == 1

        trade_row = verify_con.execute(
            """
            SELECT favourite_team, home_ground, status, missed_swing_team
            FROM trades
            """
        ).fetchone()
        assert trade_row == ("RCB", "NEU", "ACTIVE", None)
    finally:
        verify_con.close()
        if trades_db_path.exists():
            trades_db_path.unlink()


def test_cockpit_dropdown_lookups_ignore_season(client: TestClient) -> None:
    teams_2025 = client.get("/api/cockpit/teams?season=2025")
    teams_2026 = client.get("/api/cockpit/teams?season=2026")
    assert teams_2025.status_code == 200
    assert teams_2026.status_code == 200
    assert teams_2025.json()["teams"] == teams_2026.json()["teams"]
    assert len(teams_2025.json()["teams"]) > 0

    venues_2025 = client.get("/api/cockpit/venues?season=2025")
    venues_2026 = client.get("/api/cockpit/venues?season=2026")
    assert venues_2025.status_code == 200
    assert venues_2026.status_code == 200
    assert venues_2025.json()["venues"] == venues_2026.json()["venues"]
    assert len(venues_2025.json()["venues"]) > 0


def test_cockpit_venues_use_short_display_labels(client: TestClient) -> None:
    response = client.get("/api/cockpit/venues?season=2025")
    assert response.status_code == 200

    venues_by_id = {venue["id"]: venue["label"] for venue in response.json()["venues"]}

    expected_labels = {
        "IND_AHMEDABAD": "Narendra Modi (Ahmedabad)",
        "IND_BANGALORE": "Chinnaswamy (Bengaluru)",
        "IND_CHENNAI": "Chepauk (Chennai)",
        "IND_DELHI": "Arun Jaitley (Delhi)",
        "IND_DHARAMSALA": "HPCA Stadium (Dharamshala)",
        "IND_GUWAHATI": "Barsapara (Guwahati)",
        "IND_HYDERABAD": "Rajiv Gandhi (Hyderabad)",
        "IND_JAIPUR": "Sawai Mansingh (Jaipur)",
        "IND_KOLKATA": "Eden Gardens (Kolkata)",
        "IND_LUCKNOW": "Ekana Stadium (Lucknow)",
        "IND_MOHALI_NEW": "Mullanpur Stadium",
        "IND_MUMBAI_WANKHEDE": "Wankhede (Mumbai)",
        "IND_VISAKHAPATNAM": "ACA-VDCA Stadium (Vizag)",
    }

    for venue_id, label in expected_labels.items():
        assert venues_by_id[venue_id] == label


def _create_active_trade(client: TestClient, season: int = 2026) -> int:
    match_date = f"{season}-04-18T00:00:00"
    draft_response = client.post(
        "/api/cockpit/trades",
        json={
            "season": season,
            "match_date": match_date,
            "team_1": "MI",
            "team_2": "CSK",
            "favourite_team": "MI",
            "home_ground": "FAV",
            "stadium": "WANKHEDE",
            "bankroll": 100,
            "selected_team_before_toss": "MI",
            "back_odds_before_toss": 57,
            "lay_odds_before_toss": 58,
        },
    )
    assert draft_response.status_code == 201
    draft_trade = draft_response.json()
    trade_id = draft_trade["id"]
    assert draft_trade["status"] == "DRAFT"
    assert draft_trade["opening_odds"] == 1.57
    assert draft_trade["toss_winner"] is None
    assert draft_trade["toss_decision"] is None
    assert draft_trade["selected_team_before_toss"] == "MI"
    assert draft_trade["back_odds_before_toss"] == 57
    assert draft_trade["lay_odds_before_toss"] == 58

    update_response = client.patch(
        f"/api/cockpit/trades/{trade_id}",
        json={
            "season": season,
            "match_date": match_date,
            "team_1": "MI",
            "team_2": "CSK",
            "favourite_team": "MI",
            "home_ground": "FAV",
            "stadium": "WANKHEDE",
            "toss_winner": "MI",
            "toss_decision": "bat",
            "bankroll": 100,
            "selected_team_before_toss": "MI",
            "back_odds_before_toss": 57,
            "lay_odds_before_toss": 58,
            "selected_team_after_toss": "CSK",
            "back_odds_after_toss": 64,
            "lay_odds_after_toss": 66,
        },
    )
    assert update_response.status_code == 200
    active_trade = update_response.json()
    assert active_trade["status"] == "ACTIVE"
    assert active_trade["toss_winner"] == "MI"
    assert active_trade["toss_decision"] == "bat"
    assert active_trade["selected_team_after_toss"] == "CSK"
    assert active_trade["back_odds_after_toss"] == 64
    assert active_trade["lay_odds_after_toss"] == 66

    return trade_id


def test_cockpit_trade_creation_reuses_the_same_match_row(client: TestClient) -> None:
    first_trade_id = _create_active_trade(client)
    second_trade_id = _create_active_trade(client)

    assert first_trade_id != second_trade_id

    con = sqlite3.connect(COCKPIT_TEST_TRADES_DB_PATH)
    try:
        matches_count = con.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
        trades_count = con.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
    finally:
        con.close()

    assert matches_count == 1
    assert trades_count == 2


def test_cockpit_routes_support_crud(client: TestClient) -> None:
    empty_trades = client.get("/api/cockpit/trades")
    assert empty_trades.status_code == 200
    assert empty_trades.json() == []

    trade_id = _create_active_trade(client)

    pending_response = client.get("/api/cockpit/trades?status=DRAFT")
    assert pending_response.status_code == 200
    assert len(pending_response.json()) == 0

    list_response = client.get("/api/cockpit/trades")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["status"] == "ACTIVE"

    active_response = client.get("/api/cockpit/trades?status=ACTIVE")
    assert active_response.status_code == 200
    assert len(active_response.json()) == 1
    assert active_response.json()[0]["id"] == trade_id

    get_response = client.get(f"/api/cockpit/trades/{trade_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == trade_id

    bet_response = client.post(
        f"/api/cockpit/trades/{trade_id}/bets",
        json={
            "team": "MI",
            "bet_type": "BACK",
            "odds_paise": 90,
            "stake": 100,
        },
    )
    assert bet_response.status_code == 201

    settle_response = client.post(
        f"/api/cockpit/trades/{trade_id}/settle",
        json={
            "winner": "team_1",
            "sentiment": "achieved",
            "fav_sub_30_loss": False,
            "targeted_pnl": 10.0,
            "achieved_yield": 50.0,
        },
    )
    assert settle_response.status_code == 200

    delete_response = client.delete(f"/api/cockpit/trades/{trade_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"deleted": True}

    empty_again = client.get("/api/cockpit/trades")
    assert empty_again.status_code == 200
    assert empty_again.json() == []


def test_cockpit_trade_list_filters_by_match_season(client: TestClient) -> None:
    trade_2025 = _create_active_trade(client, season=2025)
    trade_2026 = _create_active_trade(client, season=2026)

    all_trades = client.get("/api/cockpit/trades")
    assert all_trades.status_code == 200
    assert {trade["id"] for trade in all_trades.json()} == {trade_2025, trade_2026}

    season_2025_response = client.get("/api/cockpit/trades?season=2025")
    assert season_2025_response.status_code == 200
    season_2025_trades = season_2025_response.json()
    assert [trade["id"] for trade in season_2025_trades] == [trade_2025]
    assert season_2025_trades[0]["season"] == 2025

    season_2026_response = client.get("/api/cockpit/trades?season=2026")
    assert season_2026_response.status_code == 200
    season_2026_trades = season_2026_response.json()
    assert [trade["id"] for trade in season_2026_trades] == [trade_2026]
    assert season_2026_trades[0]["season"] == 2026


def test_cockpit_store_delete_trade_removes_bets(monkeypatch: pytest.MonkeyPatch) -> None:
    workspace_tmp = Path.cwd() / "temp_pytest"
    workspace_tmp.mkdir(exist_ok=True)
    trades_db_path = workspace_tmp / "cockpit-trades.sqlite"
    monkeypatch.setenv("ODI_COCKPIT_DB_PATH", str(trades_db_path))

    migrate_trades_db("odi")
    store = CockpitStore("odi", read_only=False)

    try:
        trade = Trade(
            season=2026,
            team_1="MI",
            team_2="CSK",
            favourite_team="MI",
            home_ground="FAV",
            stadium="WANKHEDE",
            bankroll=100.0,
        )
        trade = store.insert_trade(trade)
        assert trade.id is not None

        store.insert_bet(
            trade_id=trade.id,
            team="MI",
            bet_type="BACK",
            odds_paise=90,
            odds_decimal=1.9,
            stake=100.0,
            liability=90.0,
            is_open=True,
            created_at=datetime(2026, 4, 18, tzinfo=timezone.utc).isoformat(),
        )
        assert len(store.list_bets(trade.id)) == 1

        trade_id = trade.id
        assert trade_id is not None
        store.delete_trade(trade_id)
        assert store.get_trade(trade_id) is None
        assert store.list_bets(trade_id) == []

        match_count_row = store._trades_con.execute("SELECT COUNT(*) FROM matches").fetchone()
        assert match_count_row is not None
        row_count = int(match_count_row[0])
        assert row_count == 0
    finally:
        store.close()
        if trades_db_path.exists():
            trades_db_path.unlink()


def test_cockpit_store_delete_trade_keeps_shared_match_row(monkeypatch: pytest.MonkeyPatch) -> None:
    workspace_tmp = Path.cwd() / "temp_pytest"
    workspace_tmp.mkdir(exist_ok=True)
    trades_db_path = workspace_tmp / "cockpit-trades-shared-match.sqlite"
    monkeypatch.setenv("ODI_COCKPIT_DB_PATH", str(trades_db_path))

    migrate_trades_db("odi")
    store = CockpitStore("odi", read_only=False)

    try:
        first_trade = Trade(
            season=2026,
            team_1="MI",
            team_2="CSK",
            favourite_team="MI",
            home_ground="FAV",
            stadium="WANKHEDE",
            bankroll=100.0,
        )
        first_trade = store.insert_trade(first_trade)
        first_trade_id = first_trade.id
        assert first_trade_id is not None
        second_trade = Trade(
            season=2026,
            team_1="MI",
            team_2="CSK",
            favourite_team="MI",
            home_ground="FAV",
            stadium="WANKHEDE",
            bankroll=100.0,
        )
        second_trade = store.insert_trade(second_trade)
        second_trade_id = second_trade.id
        assert second_trade_id is not None

        assert first_trade.match_id == second_trade.match_id

        store.delete_trade(first_trade_id)
        assert store.get_trade(first_trade_id) is None
        assert store.get_trade(second_trade_id) is not None

        match_count_row = store._trades_con.execute("SELECT COUNT(*) FROM matches").fetchone()
        assert match_count_row is not None
        row_count = int(match_count_row[0])
        assert row_count == 1
    finally:
        store.close()
        if trades_db_path.exists():
            trades_db_path.unlink()


def test_cockpit_bet_routes_support_crud_and_validation(client: TestClient) -> None:
    trade_id = _create_active_trade(client)

    missing_trade_response = client.post(
        "/api/cockpit/trades/999999/bets",
        json={
            "team": "MI",
            "bet_type": "BACK",
            "odds_paise": 90,
            "stake": 100,
        },
    )
    assert missing_trade_response.status_code == 404
    assert missing_trade_response.json()["detail"] == "Trade 999999 not found"

    invalid_cases = [
        {
            "team": "MI",
            "bet_type": "HOLD",
            "odds_paise": 90,
            "stake": 100,
        },
        {
            "team": "MI",
            "bet_type": "BACK",
            "odds_paise": 0,
            "stake": 100,
        },
        {
            "team": "MI",
            "bet_type": "LAY",
            "odds_paise": 90,
            "stake": 0,
        },
    ]
    for payload in invalid_cases:
        response = client.post(f"/api/cockpit/trades/{trade_id}/bets", json=payload)
        assert response.status_code == 422

    invalid_team_response = client.post(
        f"/api/cockpit/trades/{trade_id}/bets",
        json={
            "team": "RCB",
            "bet_type": "BACK",
            "odds_paise": 90,
            "stake": 10,
        },
    )
    assert invalid_team_response.status_code == 400
    assert invalid_team_response.json()["detail"] == "Team must match one of the trade teams"

    back_response = client.post(
        f"/api/cockpit/trades/{trade_id}/bets",
        json={
            "team": "MI",
            "bet_type": "BACK",
            "odds_paise": 90,
            "stake": 40,
        },
    )
    assert back_response.status_code == 201
    back_bet = back_response.json()
    assert back_bet["trade_id"] == trade_id
    assert back_bet["team"] == "MI"
    assert back_bet["bet_type"] == "BACK"
    assert back_bet["odds_paise"] == 90
    assert back_bet["odds_decimal"] == pytest.approx(1.9)
    assert back_bet["stake"] == 40.0
    assert back_bet["liability"] == 40.0
    assert back_bet["is_open"] is True
    assert isinstance(back_bet["created_at"], str)
    assert back_bet["created_at"]

    lay_response = client.post(
        f"/api/cockpit/trades/{trade_id}/bets",
        json={
            "team": "CSK",
            "bet_type": "LAY",
            "odds_paise": 120,
            "stake": 20,
        },
    )
    assert lay_response.status_code == 201
    lay_bet = lay_response.json()
    assert lay_bet["liability"] == 24.0
    assert lay_bet["odds_decimal"] == pytest.approx(2.2)
    assert lay_bet["is_open"] is True

    state_response = client.get(f"/api/cockpit/trades/{trade_id}/state")
    assert state_response.status_code == 200
    state = state_response.json()
    assert state["id"] == trade_id
    assert state["net_pnl_team_1"] == 56.0
    assert state["net_pnl_team_2"] == -64.0
    assert state["total_exposure"] == 64.0
    assert state["available_bankroll"] == 36.0

    bankroll_guard_response = client.post(
        f"/api/cockpit/trades/{trade_id}/bets",
        json={
            "team": "MI",
            "bet_type": "BACK",
            "odds_paise": 95,
            "stake": 50,
        },
    )
    assert bankroll_guard_response.status_code == 400
    assert bankroll_guard_response.json()["detail"] == "Insufficient bankroll"

    hedge_response = client.post(
        f"/api/cockpit/trades/{trade_id}/bets",
        json={
            "team": "CSK",
            "bet_type": "BACK",
            "odds_paise": 120,
            "stake": 50,
        },
    )
    assert hedge_response.status_code == 201
    hedge_bet = hedge_response.json()
    assert hedge_bet["trade_id"] == trade_id
    assert hedge_bet["team"] == "CSK"
    assert hedge_bet["bet_type"] == "BACK"
    assert hedge_bet["odds_paise"] == 120
    assert hedge_bet["odds_decimal"] == pytest.approx(2.2)
    assert hedge_bet["stake"] == 50.0
    assert hedge_bet["liability"] == 50.0
    assert hedge_bet["is_open"] is True

    hedge_state_response = client.get(f"/api/cockpit/trades/{trade_id}/state")
    assert hedge_state_response.status_code == 200
    hedge_state = hedge_state_response.json()
    assert hedge_state["net_pnl_team_1"] == 6.0
    assert hedge_state["net_pnl_team_2"] == -4.0
    assert hedge_state["total_exposure"] == 4.0
    assert hedge_state["available_bankroll"] == 96.0

    list_response = client.get(f"/api/cockpit/trades/{trade_id}/bets")
    assert list_response.status_code == 200
    bets = list_response.json()
    assert [bet["id"] for bet in bets] == [back_bet["id"], lay_bet["id"], hedge_bet["id"]]
    assert bets[0]["is_open"] is True
    assert bets[1]["is_open"] is True

    live_view_response = client.get(f"/api/cockpit/trades/{trade_id}/bets?view=live")
    assert live_view_response.status_code == 200
    assert [bet["id"] for bet in live_view_response.json()] == [back_bet["id"], lay_bet["id"], hedge_bet["id"]]

    history_view_response = client.get(f"/api/cockpit/trades/{trade_id}/bets?view=history")
    assert history_view_response.status_code == 200
    assert [bet["id"] for bet in history_view_response.json()] == [back_bet["id"], lay_bet["id"], hedge_bet["id"]]

    close_response = client.patch(
        f"/api/cockpit/trades/{trade_id}/bets/{lay_bet['id']}/close"
    )
    assert close_response.status_code == 200
    closed_bet = close_response.json()
    assert closed_bet["id"] == lay_bet["id"]
    assert closed_bet["is_open"] is False

    state_after_close = client.get(f"/api/cockpit/trades/{trade_id}/state")
    assert state_after_close.status_code == 200
    closed_state = state_after_close.json()
    assert closed_state["net_pnl_team_1"] == -14.0
    assert closed_state["net_pnl_team_2"] == 20.0
    assert closed_state["total_exposure"] == 14.0
    assert closed_state["available_bankroll"] == 86.0

    list_again = client.get(f"/api/cockpit/trades/{trade_id}/bets")
    assert list_again.status_code == 200
    reopened = list_again.json()
    assert reopened[1]["is_open"] is False

    missing_bet_response = client.patch(
        f"/api/cockpit/trades/{trade_id}/bets/999999/close"
    )
    assert missing_bet_response.status_code == 404
    assert missing_bet_response.json()["detail"] == f"Bet 999999 not found for trade {trade_id}"


def test_cockpit_bet_delete_removes_one_bet_and_resets_trade_state(client: TestClient) -> None:
    trade_id = _create_active_trade(client)

    add_response = client.post(
        f"/api/cockpit/trades/{trade_id}/bets",
        json={
            "team": "MI",
            "bet_type": "BACK",
            "odds_paise": 90,
            "stake": 40,
        },
    )
    assert add_response.status_code == 201
    bet = add_response.json()

    delete_response = client.delete(f"/api/cockpit/trades/{trade_id}/bets/{bet['id']}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"deleted": True}

    state_response = client.get(f"/api/cockpit/trades/{trade_id}/state")
    assert state_response.status_code == 200
    state = state_response.json()
    assert state["net_pnl_team_1"] == 0.0
    assert state["net_pnl_team_2"] == 0.0
    assert state["total_exposure"] == 0.0
    assert state["available_bankroll"] == 100.0

    list_response = client.get(f"/api/cockpit/trades/{trade_id}/bets")
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_cockpit_bets_stay_scoped_to_their_trade(client: TestClient) -> None:
    first_trade_id = _create_active_trade(client)
    second_trade_id = _create_active_trade(client)

    first_bet_response = client.post(
        f"/api/cockpit/trades/{first_trade_id}/bets",
        json={
            "team": "MI",
            "bet_type": "BACK",
            "odds_paise": 90,
            "stake": 40,
        },
    )
    assert first_bet_response.status_code == 201

    second_back_response = client.post(
        f"/api/cockpit/trades/{second_trade_id}/bets",
        json={
            "team": "MI",
            "bet_type": "BACK",
            "odds_paise": 95,
            "stake": 25,
        },
    )
    assert second_back_response.status_code == 201

    first_list = client.get(f"/api/cockpit/trades/{first_trade_id}/bets?view=history")
    second_list = client.get(f"/api/cockpit/trades/{second_trade_id}/bets?view=live")

    assert first_list.status_code == 200
    assert second_list.status_code == 200

    first_bets = first_list.json()
    second_bets = second_list.json()

    assert len(first_bets) == 1
    assert len(second_bets) == 1
    assert first_bets[0]["trade_id"] == first_trade_id
    assert second_bets[0]["trade_id"] == second_trade_id
    assert first_bets[0]["id"] != second_bets[0]["id"]


def test_cockpit_trade_settlement_records_metrics_and_locks_trade(client: TestClient) -> None:
    trade_id = _create_active_trade(client)

    first_bet_response = client.post(
        f"/api/cockpit/trades/{trade_id}/bets",
        json={
            "team": "MI",
            "bet_type": "BACK",
            "odds_paise": 90,
            "stake": 40,
        },
    )
    assert first_bet_response.status_code == 201

    second_bet_response = client.post(
        f"/api/cockpit/trades/{trade_id}/bets",
        json={
            "team": "CSK",
            "bet_type": "LAY",
            "odds_paise": 120,
            "stake": 20,
        },
    )
    assert second_bet_response.status_code == 201

    settle_response = client.post(
        f"/api/cockpit/trades/{trade_id}/settle",
        json={
            "winner": "team_1",
            "sentiment": "achieved",
            "fav_sub_30_loss": True,
            "targeted_pnl": 26.15,
            "achieved_yield": 214.0,
        },
    )
    assert settle_response.status_code == 200
    settled_trade = settle_response.json()
    assert settled_trade["status"] == "SETTLED"
    assert settled_trade["winner"] == "team_1"
    assert settled_trade["actual_profit"] == 56.0
    assert settled_trade["trade_sentiment"] == "achieved"
    assert settled_trade["fav_sub_30_loss"] is True
    assert settled_trade["targeted_pnl"] == 26.15
    assert settled_trade["achieved_yield_percentage"] == 214.0
    assert settled_trade["total_volume_wagered"] == 64.0

    get_response = client.get(f"/api/cockpit/trades/{trade_id}")
    assert get_response.status_code == 200
    stored_trade = get_response.json()
    assert stored_trade["status"] == "SETTLED"
    assert stored_trade["winner"] == "team_1"
    assert stored_trade["actual_profit"] == 56.0

    locked_add_response = client.post(
        f"/api/cockpit/trades/{trade_id}/bets",
        json={
            "team": "MI",
            "bet_type": "BACK",
            "odds_paise": 95,
            "stake": 10,
        },
    )
    assert locked_add_response.status_code == 400
    assert locked_add_response.json()["detail"] == "Trade is settled and cannot be modified"

    locked_update_response = client.patch(
        f"/api/cockpit/trades/{trade_id}",
        json={
            "season": 2026,
            "match_date": "2026-04-18T00:00:00",
            "team_1": "MI",
            "team_2": "CSK",
            "favourite_team": "MI",
            "home_ground": "FAV",
            "stadium": "WANKHEDE",
            "bankroll": 100,
            "selected_team_before_toss": "MI",
            "back_odds_before_toss": 57,
            "lay_odds_before_toss": 58,
        },
    )
    assert locked_update_response.status_code == 400
    assert locked_update_response.json()["detail"] == "Trade must be DRAFT or ACTIVE to update"


def test_cockpit_trade_restore_recreates_a_settled_trade_without_recrediting_wallet(
    client: TestClient,
) -> None:
    trade_id = _create_active_trade(client)

    first_bet_response = client.post(
        f"/api/cockpit/trades/{trade_id}/bets",
        json={
            "team": "MI",
            "bet_type": "BACK",
            "odds_paise": 90,
            "stake": 40,
        },
    )
    assert first_bet_response.status_code == 201

    second_bet_response = client.post(
        f"/api/cockpit/trades/{trade_id}/bets",
        json={
            "team": "CSK",
            "bet_type": "LAY",
            "odds_paise": 120,
            "stake": 20,
        },
    )
    assert second_bet_response.status_code == 201

    finances = getattr(app.state, "finances", None)
    assert finances is not None
    wallet_before_settle = finances.get_balances()["wallet"]

    settle_response = client.post(
        f"/api/cockpit/trades/{trade_id}/settle",
        json={
            "winner": "team_1",
            "sentiment": "achieved",
            "fav_sub_30_loss": True,
            "targeted_pnl": 26.15,
            "achieved_yield": 214.0,
        },
    )
    assert settle_response.status_code == 200
    settled_trade = settle_response.json()
    assert settled_trade["status"] == "SETTLED"
    assert settled_trade["actual_profit"] == 56.0

    wallet_after_settle = finances.get_balances()["wallet"]
    assert wallet_after_settle == pytest.approx(wallet_before_settle + 56.0)

    bets_response = client.get(f"/api/cockpit/trades/{trade_id}/bets?view=history")
    assert bets_response.status_code == 200

    delete_response = client.delete(f"/api/cockpit/trades/{trade_id}")
    assert delete_response.status_code == 200

    restore_response = client.post(
        "/api/cockpit/trades/restore",
        json={
            "trade": settled_trade,
            "bets": bets_response.json(),
        },
    )
    assert restore_response.status_code == 200
    restored_trade = restore_response.json()
    assert restored_trade["status"] == "SETTLED"
    assert restored_trade["winner"] == "team_1"
    assert restored_trade["actual_profit"] == 56.0

    assert finances.get_balances()["wallet"] == pytest.approx(wallet_after_settle)


def test_cockpit_trade_void_records_zero_metrics_and_is_listable_with_settled_trades(
    client: TestClient,
) -> None:
    void_trade_id = _create_active_trade(client)

    void_bet_response = client.post(
        f"/api/cockpit/trades/{void_trade_id}/bets",
        json={
            "team": "MI",
            "bet_type": "BACK",
            "odds_paise": 90,
            "stake": 40,
        },
    )
    assert void_bet_response.status_code == 201

    void_response = client.post(f"/api/cockpit/trades/{void_trade_id}/void")
    assert void_response.status_code == 200
    void_trade = void_response.json()
    assert void_trade["status"] == "VOID"
    assert void_trade["winner"] is None
    assert void_trade["actual_profit"] == 0.0
    assert void_trade["targeted_pnl"] == 0.0
    assert void_trade["achieved_yield_percentage"] == 0.0
    assert void_trade["total_volume_wagered"] == 0.0

    void_bets_response = client.get(f"/api/cockpit/trades/{void_trade_id}/bets")
    assert void_bets_response.status_code == 200
    assert len(void_bets_response.json()) == 1

    settled_trade_id = _create_active_trade(client)
    settled_bet_response = client.post(
        f"/api/cockpit/trades/{settled_trade_id}/bets",
        json={
            "team": "MI",
            "bet_type": "BACK",
            "odds_paise": 90,
            "stake": 10,
        },
    )
    assert settled_bet_response.status_code == 201

    settled_response = client.post(
        f"/api/cockpit/trades/{settled_trade_id}/settle",
        json={
            "winner": "team_1",
            "sentiment": "achieved",
            "fav_sub_30_loss": False,
            "targeted_pnl": 10.0,
            "achieved_yield": 100.0,
        },
    )
    assert settled_response.status_code == 200

    list_response = client.get("/api/cockpit/trades?status=SETTLED,VOID")
    assert list_response.status_code == 200
    listed_trades = list_response.json()
    assert {trade["status"] for trade in listed_trades} == {"SETTLED", "VOID"}


def test_existing_flat_trade_table_is_reset_to_normalized_schema(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace_tmp = Path.cwd() / "temp_pytest"
    workspace_tmp.mkdir(exist_ok=True)

    temp_path = workspace_tmp / "cockpit_flat_reset_test"
    if temp_path.exists():
        shutil.rmtree(temp_path, ignore_errors=True)
    temp_path.mkdir(exist_ok=True)

    trades_db_path = temp_path / "cockpit-trades.sqlite"
    monkeypatch.setenv("IPL_COCKPIT_TRADES_DB_PATH", str(trades_db_path))

    legacy_con = sqlite3.connect(trades_db_path)
    try:
        legacy_con.execute(
            """
            CREATE TABLE trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                season INTEGER NOT NULL,
                match_date TEXT,
                team_1 TEXT NOT NULL,
                team_2 TEXT NOT NULL,
                favourite_team TEXT NOT NULL,
                home_ground TEXT NOT NULL CHECK (home_ground IN ('FAV', 'UG', 'NEU')),
                stadium TEXT NOT NULL,
                bankroll REAL NOT NULL DEFAULT 100.0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'DRAFT'
                    CHECK (status IN ('DRAFT', 'ACTIVE', 'SETTLED'))
            )
            """
        )
        legacy_con.execute(
            """
            INSERT INTO trades (
                season,
                match_date,
                team_1,
                team_2,
                favourite_team,
                home_ground,
                stadium,
                bankroll,
                created_at,
                updated_at,
                status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                2025,
                "2025-05-01T00:00:00",
                "PBKS",
                "RCB",
                "RCB",
                "NEU",
                "M. Chinnaswamy Stadium",
                100.0,
                "2025-05-01T00:00:00Z",
                "2025-05-01T00:00:00Z",
                "ACTIVE",
            ),
        )
        legacy_con.commit()
    finally:
        legacy_con.close()

    migrate_trades_db("ipl")

    verify_con = sqlite3.connect(trades_db_path)
    try:
        tables = {
            row[0]
            for row in verify_con.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        assert {"matches", "trades", "bets"}.issubset(tables)

        trade_columns = [
            row[1]
            for row in verify_con.execute("PRAGMA table_info(trades)").fetchall()
        ]
        assert "match_id" in trade_columns
        assert "season" not in trade_columns

        trade_count = verify_con.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
        match_count = verify_con.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
        bet_count = verify_con.execute("SELECT COUNT(*) FROM bets").fetchone()[0]
    finally:
        verify_con.close()

    assert trade_count == 0
    assert match_count == 0
    assert bet_count == 0

    shutil.rmtree(temp_path, ignore_errors=True)


def test_cockpit_cashout_bets_skip_bankroll_guard(client: TestClient) -> None:
    trade_id = _create_active_trade(client)

    update_response = client.patch(
        f"/api/cockpit/trades/{trade_id}",
        json={
            "season": 2026,
            "match_date": "2026-04-18T00:00:00",
            "team_1": "MI",
            "team_2": "CSK",
            "favourite_team": "MI",
            "home_ground": "FAV",
            "stadium": "WANKHEDE",
            "toss_winner": "MI",
            "toss_decision": "bat",
            "bankroll": 1,
            "selected_team_before_toss": "MI",
            "back_odds_before_toss": 57,
            "lay_odds_before_toss": 58,
            "selected_team_after_toss": "CSK",
            "back_odds_after_toss": 64,
            "lay_odds_after_toss": 66,
        },
    )
    assert update_response.status_code == 200

    cashout_response = client.post(
        f"/api/cockpit/trades/{trade_id}/bets",
        json={
            "team": "MI",
            "bet_type": "BACK",
            "odds_paise": 120,
            "stake": 500,
            "purpose": "CASHOUT",
        },
    )
    assert cashout_response.status_code == 201
    cashout_bet = cashout_response.json()
    assert cashout_bet["trade_id"] == trade_id
    assert cashout_bet["team"] == "MI"
    assert cashout_bet["bet_type"] == "BACK"
    assert cashout_bet["odds_paise"] == 120
    assert cashout_bet["stake"] == 500.0
    assert cashout_bet["liability"] == 500.0
    assert cashout_bet["is_open"] is True
