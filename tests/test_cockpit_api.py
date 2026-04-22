from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    trades_db_path = Path(__file__).resolve().parents[1] / "data" / "cockpit-trades-test.duckdb"
    if trades_db_path.exists():
        trades_db_path.unlink()
    monkeypatch.setenv("IPL_COCKPIT_TRADES_DB_PATH", str(trades_db_path))
    with TestClient(app) as test_client:
        yield test_client
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


def test_cockpit_routes_support_crud(client: TestClient) -> None:
    empty_summary = client.get("/api/cockpit/summary")
    assert empty_summary.status_code == 200
    assert empty_summary.json()["total_trades"] == 0
    assert empty_summary.json()["running_pnl"] == []

    empty_trades = client.get("/api/cockpit/trades")
    assert empty_trades.status_code == 200
    assert empty_trades.json() == []

    draft_response = client.post(
        "/api/cockpit/trades",
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
    assert draft_response.status_code == 201
    trade = draft_response.json()
    trade_id = trade["id"]
    assert trade["status"] == "DRAFT"
    assert trade["result"] == "OPEN"
    assert trade["total_stake"] is None
    assert trade["alert_bullet3_active"] is False
    assert trade["opening_odds"] == 1.57
    assert trade["toss_winner"] is None
    assert trade["toss_decision"] is None
    assert trade["selected_team_before_toss"] == "MI"
    assert trade["back_odds_before_toss"] == 57
    assert trade["lay_odds_before_toss"] == 58

    pending_response = client.get("/api/cockpit/trades?status=DRAFT")
    assert pending_response.status_code == 200
    assert len(pending_response.json()) == 1
    assert pending_response.json()[0]["id"] == trade_id

    summary_before_activation = client.get("/api/cockpit/summary")
    assert summary_before_activation.status_code == 200
    assert summary_before_activation.json()["total_trades"] == 0

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
    trade = update_response.json()
    assert trade["status"] == "ACTIVE"
    assert trade["toss_winner"] == "MI"
    assert trade["toss_decision"] == "bat"
    assert trade["selected_team_after_toss"] == "CSK"
    assert trade["back_odds_after_toss"] == 64
    assert trade["lay_odds_after_toss"] == 66

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

    bullet_response = client.patch(
        f"/api/cockpit/trades/{trade_id}/bullet",
        json={
            "bullet_number": 0,
            "odds": 1.5,
            "stake": 10,
        },
    )
    assert bullet_response.status_code == 200
    trade = bullet_response.json()
    assert trade["total_stake"] == 10.0

    close_response = client.patch(
        f"/api/cockpit/trades/{trade_id}/close",
        json={
            "exit_odds": 0.0,
            "fav_reached_130": True,
            "is_fake_favourite": False,
            "notes": "test close",
        },
    )
    assert close_response.status_code == 200
    trade = close_response.json()
    assert trade["result"] == "LOST"
    assert trade["actual_profit"] == -10.0

    summary = client.get("/api/cockpit/summary")
    assert summary.status_code == 200
    payload = summary.json()
    assert payload["total_trades"] == 1
    assert payload["lost_count"] == 1
    assert payload["running_pnl"] == [-10.0]
