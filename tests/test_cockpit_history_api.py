from __future__ import annotations

import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from api.main import app


COCKPIT_TEST_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
COCKPIT_HISTORY_IPL_LOOKUP_DB_PATH = COCKPIT_TEST_DATA_DIR / "cockpit-history-ipl.duckdb"
COCKPIT_HISTORY_IPL_TRADES_DB_PATH = COCKPIT_TEST_DATA_DIR / "cockpit-history-ipl.sqlite"
COCKPIT_HISTORY_ODI_DB_PATH = COCKPIT_TEST_DATA_DIR / "cockpit-history-odi.sqlite"
COCKPIT_HISTORY_FINANCES_DB_PATH = COCKPIT_TEST_DATA_DIR / "cockpit-history-finances.sqlite"
COCKPIT_HISTORY_INITIAL_BANK_BALANCE = 70560.67
COCKPIT_HISTORY_INITIAL_WALLET_BALANCE = 29980.76
COCKPIT_HISTORY_INITIAL_BANK_DEPOSIT = 100541.43


@pytest.fixture()
def history_client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    source_lookup_db_path = COCKPIT_TEST_DATA_DIR / "ipl.duckdb"

    for path in (
        COCKPIT_HISTORY_IPL_LOOKUP_DB_PATH,
        COCKPIT_HISTORY_IPL_TRADES_DB_PATH,
        COCKPIT_HISTORY_ODI_DB_PATH,
        COCKPIT_HISTORY_FINANCES_DB_PATH,
    ):
        if path.exists():
            path.unlink()

    shutil.copy2(source_lookup_db_path, COCKPIT_HISTORY_IPL_LOOKUP_DB_PATH)
    monkeypatch.setenv("IPL_COCKPIT_DB_PATH", str(COCKPIT_HISTORY_IPL_LOOKUP_DB_PATH))
    monkeypatch.setenv("IPL_COCKPIT_TRADES_DB_PATH", str(COCKPIT_HISTORY_IPL_TRADES_DB_PATH))
    monkeypatch.setenv("ODI_COCKPIT_DB_PATH", str(COCKPIT_HISTORY_ODI_DB_PATH))
    monkeypatch.setenv("FINANCES_DB_PATH", str(COCKPIT_HISTORY_FINANCES_DB_PATH))

    with TestClient(app) as test_client:
        finances = getattr(app.state, "finances", None)
        if finances is not None:
            balances = finances.get_balances()
            if balances["bank"] == 0.0 and balances["wallet"] == 0.0:
                finances.deposit_to_bank(COCKPIT_HISTORY_INITIAL_BANK_DEPOSIT)
                finances.topup_wallet(COCKPIT_HISTORY_INITIAL_WALLET_BALANCE)
        yield test_client

    for path in (
        COCKPIT_HISTORY_IPL_LOOKUP_DB_PATH,
        COCKPIT_HISTORY_IPL_TRADES_DB_PATH,
        COCKPIT_HISTORY_ODI_DB_PATH,
        COCKPIT_HISTORY_FINANCES_DB_PATH,
    ):
        if path.exists():
            path.unlink()


def _create_active_trade(
    client: TestClient,
    *,
    format_key: str,
    season: int,
    match_date: datetime,
    team_1: str,
    team_2: str,
    favourite_team: str,
    home_ground: str,
    stadium: str,
) -> int:
    payload = {
        "season": season,
        "match_date": match_date.isoformat(),
        "team_1": team_1,
        "team_2": team_2,
        "favourite_team": favourite_team,
        "home_ground": home_ground,
        "stadium": stadium,
        "bankroll": 100.0,
        "selected_team_before_toss": favourite_team,
        "back_odds_before_toss": 57,
        "lay_odds_before_toss": 58,
        "toss_winner": favourite_team,
        "toss_decision": "bat",
        "selected_team_after_toss": team_2 if favourite_team == team_1 else team_1,
        "back_odds_after_toss": 64,
        "lay_odds_after_toss": 66,
    }

    response = client.post(f"/api/cockpit/trades?format={format_key}", json=payload)
    assert response.status_code == 201
    trade = response.json()
    assert trade["status"] == "ACTIVE"

    bet_response = client.post(
        f"/api/cockpit/trades/{trade['id']}/bets?format={format_key}",
        json={
            "team": favourite_team,
            "bet_type": "BACK",
            "odds_paise": 90,
            "stake": 100,
        },
    )
    assert bet_response.status_code == 201

    settle_response = client.post(
        f"/api/cockpit/trades/{trade['id']}/settle?format={format_key}",
        json={
            "winner": "team_1" if favourite_team == team_1 else "team_2",
            "sentiment": "achieved",
            "fav_sub_30_loss": False,
            "targeted_pnl": 10.0,
            "achieved_yield": 15.0,
        },
    )
    assert settle_response.status_code == 200

    return int(trade["id"])


def test_history_single_format_filters_by_season_and_date(
    history_client: TestClient,
) -> None:
    today = datetime.now(timezone.utc).date()
    recent_match_date = datetime.combine(today - timedelta(days=2), datetime.min.time(), tzinfo=timezone.utc)
    old_match_date = datetime.combine(today - timedelta(days=14), datetime.min.time(), tzinfo=timezone.utc)

    recent_trade_id = _create_active_trade(
        history_client,
        format_key="ipl",
        season=2026,
        match_date=recent_match_date,
        team_1="MI",
        team_2="CSK",
        favourite_team="MI",
        home_ground="FAV",
        stadium="WANKHEDE",
    )
    _create_active_trade(
        history_client,
        format_key="ipl",
        season=2025,
        match_date=old_match_date,
        team_1="RCB",
        team_2="KKR",
        favourite_team="RCB",
        home_ground="FAV",
        stadium="CHINNASWAMY",
    )

    response = history_client.get(
        "/api/cockpit/history/trades?format_scope=single&format=ipl&season=2026&date_range=7d"
    )
    assert response.status_code == 200
    rows = response.json()
    assert [row["id"] for row in rows] == [recent_trade_id]
    assert rows[0]["format_key"] == "ipl"
    assert rows[0]["format_label"] == "IPL"
    assert rows[0]["season"] == 2026


def test_history_all_formats_merges_rows_and_keeps_format_metadata(
    history_client: TestClient,
) -> None:
    today = datetime.now(timezone.utc).date()
    first_match_date = datetime.combine(today - timedelta(days=3), datetime.min.time(), tzinfo=timezone.utc)
    second_match_date = datetime.combine(today - timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)

    ipl_trade_id = _create_active_trade(
        history_client,
        format_key="ipl",
        season=2026,
        match_date=first_match_date,
        team_1="MI",
        team_2="CSK",
        favourite_team="MI",
        home_ground="FAV",
        stadium="WANKHEDE",
    )
    odi_trade_id = _create_active_trade(
        history_client,
        format_key="odi",
        season=2026,
        match_date=second_match_date,
        team_1="IND",
        team_2="AUS",
        favourite_team="IND",
        home_ground="FAV",
        stadium="WANKHEDE",
    )

    response = history_client.get(
        "/api/cockpit/history/trades?format_scope=all&date_range=7d"
    )
    assert response.status_code == 200
    rows = response.json()
    assert [row["id"] for row in rows] == [odi_trade_id, ipl_trade_id]
    assert {row["format_key"] for row in rows} == {"ipl", "odi"}
    assert {row["format_label"] for row in rows} == {"IPL", "ODI"}


def test_history_supports_arbitrary_day_windows(history_client: TestClient) -> None:
    today = datetime.now(timezone.utc).date()
    in_range_match_date = datetime.combine(today - timedelta(days=2), datetime.min.time(), tzinfo=timezone.utc)
    out_of_range_match_date = datetime.combine(today - timedelta(days=10), datetime.min.time(), tzinfo=timezone.utc)

    in_range_trade_id = _create_active_trade(
        history_client,
        format_key="ipl",
        season=today.year,
        match_date=in_range_match_date,
        team_1="MI",
        team_2="CSK",
        favourite_team="MI",
        home_ground="FAV",
        stadium="WANKHEDE",
    )
    _create_active_trade(
        history_client,
        format_key="ipl",
        season=today.year,
        match_date=out_of_range_match_date,
        team_1="RCB",
        team_2="KKR",
        favourite_team="RCB",
        home_ground="FAV",
        stadium="CHINNASWAMY",
    )

    response = history_client.get("/api/cockpit/history/trades?format_scope=single&format=ipl&date_range=10d")
    assert response.status_code == 200
    rows = response.json()
    assert [row["id"] for row in rows] == [in_range_trade_id]


def test_history_supports_arbitrary_month_windows(history_client: TestClient) -> None:
    today = datetime.now(timezone.utc).date()
    in_range_match_date = datetime.combine(today - timedelta(days=40), datetime.min.time(), tzinfo=timezone.utc)
    out_of_range_match_date = datetime.combine(today - timedelta(days=70), datetime.min.time(), tzinfo=timezone.utc)

    in_range_trade_id = _create_active_trade(
        history_client,
        format_key="odi",
        season=today.year,
        match_date=in_range_match_date,
        team_1="IND",
        team_2="AUS",
        favourite_team="IND",
        home_ground="FAV",
        stadium="WANKHEDE",
    )
    _create_active_trade(
        history_client,
        format_key="odi",
        season=today.year,
        match_date=out_of_range_match_date,
        team_1="ENG",
        team_2="NZ",
        favourite_team="ENG",
        home_ground="FAV",
        stadium="EDGBASTON",
    )

    response = history_client.get("/api/cockpit/history/trades?format_scope=single&format=odi&date_range=2m")
    assert response.status_code == 200
    rows = response.json()
    assert [row["id"] for row in rows] == [in_range_trade_id]


def test_history_summary_uses_the_same_filters(history_client: TestClient) -> None:
    today = datetime.now(timezone.utc).date()
    first_match_date = datetime.combine(today - timedelta(days=3), datetime.min.time(), tzinfo=timezone.utc)
    second_match_date = datetime.combine(today - timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)

    _create_active_trade(
        history_client,
        format_key="ipl",
        season=2026,
        match_date=first_match_date,
        team_1="MI",
        team_2="CSK",
        favourite_team="MI",
        home_ground="FAV",
        stadium="WANKHEDE",
    )
    _create_active_trade(
        history_client,
        format_key="odi",
        season=2026,
        match_date=second_match_date,
        team_1="IND",
        team_2="AUS",
        favourite_team="IND",
        home_ground="FAV",
        stadium="WANKHEDE",
    )

    response = history_client.get("/api/cockpit/history/summary?format_scope=all&date_range=7d")
    assert response.status_code == 200
    payload = response.json()
    assert payload["format_scope"] == "all"
    assert payload["format_key"] is None
    assert payload["format_keys"] == ["ipl", "odi"]
    assert payload["trade_count"] == 2
    assert payload["settled_trade_count"] == 2
    assert payload["positive_trades"] == 2
    assert payload["negative_trades"] == 0
    assert payload["total_realized_pnl"] > 0
    assert payload["total_volume_wagered"] > 0


def test_history_custom_date_range_rejects_missing_bounds(history_client: TestClient) -> None:
    response = history_client.get(
        "/api/cockpit/history/trades?format_scope=single&format=ipl&date_range=custom"
    )
    assert response.status_code == 400
    assert "date_from" in response.json()["detail"]
