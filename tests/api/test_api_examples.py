"""API test patterns. Skipped, the WorkFlow Pro API is fictional."""
import pytest

pytestmark = pytest.mark.skip(reason="Target API is fictional")


@pytest.mark.api
def test_create_project_returns_201(api_client, config, unique_name):
    """Happy path: a valid payload creates a project."""
    response = api_client.post(
        "/projects",
        json={"name": unique_name(), "description": "test"},
        tenant_id=config["tenants"]["company1"]["id"],
    )
    assert response.status_code == 201
    assert "id" in response.json()


@pytest.mark.api
def test_missing_required_field_returns_422(api_client, config):
    """Validation: an incomplete payload is rejected."""
    response = api_client.post(
        "/projects",
        json={"description": "no name given"},
        tenant_id=config["tenants"]["company1"]["id"],
    )
    assert response.status_code == 422
    assert "name" in response.text


@pytest.mark.api
def test_unauthenticated_request_returns_401(config):
    """Auth: no token means no access."""
    import requests
    response = requests.get(f"{config['api_url']}/projects", timeout=30)
    assert response.status_code == 401


@pytest.mark.api
def test_nonexistent_project_returns_404(api_client, config):
    """Error handling: a missing record is reported clearly."""
    response = api_client.get(
        "/projects/99999999",
        tenant_id=config["tenants"]["company1"]["id"],
    )
    assert response.status_code == 404
