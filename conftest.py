"""Shared fixtures. Cleanup here runs even when a test fails."""
import os
import uuid
import pytest
import yaml
from pathlib import Path

CONFIG_DIR = Path(__file__).parent / "config"


def pytest_addoption(parser):
    parser.addoption("--env", default="demo", help="local, demo, staging")
    parser.addoption("--tenant", default="company1", help="which tenant to test")


@pytest.fixture(scope="session")
def config(request):
    """Load settings once per run."""
    with open(CONFIG_DIR / "environments.yaml") as f:
        data = yaml.safe_load(f)

    env = request.config.getoption("--env")
    tenant = request.config.getoption("--tenant")

    return {
        "env": env,
        "tenant": tenant,
        "base_url": data["environments"][env]["base_url"],
        "api_url": data["environments"][env].get("api_url"),
        "timeout": data["tenants"][tenant]["timeout_ms"],
        "users": data["environments"][env].get("users", {}),
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, config):
    """Pin viewport. CI defaults vary and narrow screens hide elements."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture
def unique_name():
    """Unique data per test so parallel runs do not collide."""
    def _make(prefix="test"):
        return f"{prefix}-{uuid.uuid4().hex[:8]}"
    return _make

@pytest.fixture(scope="session")
def api_client(config):
    """HTTP session for API tests.

    Only used by the WorkFlow Pro tests, which are skipped because the
    API is fictional. Kept so the fixture contract is complete.
    """
    from core.api_client import APIClient
    return APIClient(
        base_url=config.get("api_url") or "",
        token=os.getenv("API_TOKEN", "placeholder-token"),
    )
