from typing import Dict, Optional

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    # Context manager triggers startup/shutdown so the engine pool is initialized.
    with TestClient(app) as test_client:
        yield test_client


def _get_active_format_key(client: TestClient) -> str:
    health_response = client.get("/health")
    assert health_response.status_code == 200

    health_payload = health_response.json()
    formats_loaded = health_payload.get("formats_loaded")
    assert isinstance(formats_loaded, list)

    if not formats_loaded:
        pytest.skip("No active formats loaded; manifest/execute tests are not applicable.")

    return str(formats_loaded[0])


def _find_function_with_required_context(manifest_payload: Dict[str, object]) -> Optional[str]:
    categories = manifest_payload.get("categories")
    if not isinstance(categories, list):
        return None

    for category in categories:
        if not isinstance(category, dict):
            continue
        functions = category.get("functions")
        if not isinstance(functions, list):
            continue
        for function in functions:
            if not isinstance(function, dict):
                continue
            required_context = function.get("required_context")
            function_key = function.get("key")
            if (
                isinstance(required_context, list)
                and len(required_context) > 0
                and isinstance(function_key, str)
                and function_key
            ):
                return function_key
    return None


def test_health_endpoint_contract(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, dict)
    assert "status" in payload
    assert "formats_loaded" in payload
    assert "total_matches" in payload
    assert isinstance(payload["status"], str)
    assert isinstance(payload["formats_loaded"], list)
    assert isinstance(payload["total_matches"], dict)


def test_formats_endpoint_contract(client: TestClient) -> None:
    response = client.get("/api/v1/formats")
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, list)

    if payload:
        first_entry = payload[0]
        assert isinstance(first_entry, dict)
        assert {"key", "label", "icon", "has_manifest"}.issubset(first_entry.keys())


def test_manifest_endpoint_contract(client: TestClient) -> None:
    format_key = _get_active_format_key(client)
    response = client.get(f"/api/v1/{format_key}/manifest")
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, dict)
    assert payload.get("format_key") == format_key
    assert "categories" in payload
    assert "context_fields" in payload
    assert "output_types" in payload
    assert isinstance(payload["categories"], list)
    assert isinstance(payload["context_fields"], dict)
    assert isinstance(payload["output_types"], list)


def test_execute_requires_context_for_manifest_function(client: TestClient) -> None:
    format_key = _get_active_format_key(client)
    manifest_response = client.get(f"/api/v1/{format_key}/manifest")
    assert manifest_response.status_code == 200
    manifest_payload = manifest_response.json()

    function_key = _find_function_with_required_context(manifest_payload)
    if function_key is None:
        pytest.skip("No manifest function with required_context found for this format.")

    execute_response = client.post(
        f"/api/v1/{format_key}/execute/{function_key}",
        json={"params": {}},
    )
    assert execute_response.status_code == 400

    payload = execute_response.json()
    assert isinstance(payload, dict)
    assert payload.get("error") == "HTTP_ERROR"
    assert payload.get("status_code") == 400
    assert "Required selection missing" in str(payload.get("detail", ""))
