"""WorkFlow Pro tests, Parts 1 and 3 of the case study.

SKIPPED ON PURPOSE: app.workflowpro.com is fictional and cannot be
reached. These are here to show the design. The framework they use is
the same one proven in tests/ui/, which does run.
"""
import re
import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.skip(reason="Target application is fictional")


# ─────────────────────────────────────────────────────────────
# PART 1: the corrected version of the flaky tests
# ─────────────────────────────────────────────────────────────

def login(page, base_url, email, password, totp_secret=None):
    """Login, including the optional 2FA screen."""
    page.goto(f"{base_url}/login")
    expect(page.get_by_role("button", name="Log in")).to_be_visible()

    page.get_by_label("Email").fill(email)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Log in").click()

    # Wait for whichever screen arrives. Some accounts get 2FA.
    otp_field = page.get_by_label("Verification code")
    dashboard = page.locator(".welcome-message")
    expect(otp_field.or_(dashboard).first).to_be_visible()

    if otp_field.is_visible():
        if not totp_secret:
            raise RuntimeError(
                f"Account {email} needs 2FA but no test secret was configured."
            )
        import pyotp
        otp_field.fill(pyotp.TOTP(totp_secret).now())
        page.get_by_role("button", name="Verify").click()


@pytest.mark.smoke
def test_user_login(page, config):
    """Fixed login test. expect() polls, plain assert does not."""
    login(page, config["base_url"], "admin@company1.com", "password")

    expect(page).to_have_url(re.compile(r"/dashboard"))
    expect(page.locator(".welcome-message")).to_be_visible()


@pytest.mark.smoke
def test_tenant_isolation(page, config):
    """Fixed tenant test.

    Original used .all() on an unloaded page, got an empty list, looped
    zero times and passed without checking anything.
    """
    login(page, config["base_url"], "user@company2.com", "password")

    cards = page.locator(".project-card")

    # Wait for the list before counting anything
    expect(cards.first).to_be_visible(timeout=config["timeout"])

    count = cards.count()
    assert count > 0, "No project cards rendered, cannot verify isolation"

    # Positive: everything shown belongs to the right company
    for i in range(count):
        expect(cards.nth(i)).to_contain_text("Company2")

    # Negative: nothing from another company leaked in.
    # The original never checked this, so a leak showing both companies
    # would have passed.
    expect(page.get_by_text("Company1")).to_have_count(0)


# ─────────────────────────────────────────────────────────────
# PART 3: API and UI integration
# ─────────────────────────────────────────────────────────────

@pytest.mark.integration
def test_project_creation_flow(page, config, api_client, unique_name):
    """API owns the write, UI owns whether it reaches a user.

    Isolation checked at both layers because they fail independently.
    """

    # 1. Create through the API
    name = unique_name("project")
    response = api_client.post(
        "/projects",
        json={"name": name, "description": "Automated test"},
        tenant_id=config["tenants"]["company1"]["id"],
    )
    assert response.status_code == 201, f"Create failed: {response.text}"
    project = response.json()
    assert project["status"] == "active"

    # 2. Confirm it reaches the user in the web UI
    login(page, config["base_url"], "admin@company1.com", "password")
    card = page.locator(".project-card", has_text=name)
    expect(card).to_be_visible(timeout=config["timeout"])

    # 3. API isolation: ask as company2, expect a refusal not an
    # empty list. A 200 with [] is ambiguous.
    cross = api_client.get(
        f"/projects/{project['id']}",
        tenant_id=config["tenants"]["company2"]["id"],
    )
    assert cross.status_code in (403, 404), (
        f"Isolation breach: company2 received {cross.status_code}"
    )

    # 4. UI isolation in a fresh session so the company1 cookie
    # does not carry over
    c2_context = page.context.browser.new_context()
    c2_page = c2_context.new_page()
    login(c2_page, config["base_url"], "user@company2.com", "password")
    expect(c2_page.get_by_text(name)).to_have_count(0)
    c2_context.close()

    # 5. Mobile: layout only. Logic is covered above and BrowserStack
    # sessions are billed per minute.
    # See docs/TESTING_APPROACH.md for the BrowserStack connection details.
