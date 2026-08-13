"""Login tests. P1, everything else depends on this."""
import re
import pytest
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


@pytest.mark.smoke
def test_valid_login_reaches_products(page, config):
    """TC-01: A valid user lands on the product page."""
    LoginPage(page, config).open().login_as("standard")

    inventory = InventoryPage(page, config)
    inventory.wait_until_ready()

    expect(page).to_have_url(re.compile(r"inventory"))
    assert inventory.items.count() > 0, "Logged in but no products rendered"


@pytest.mark.smoke
@pytest.mark.parametrize("username,password,expected", [
    ("standard_user", "wrong_password", "Username and password do not match"),
    ("no_such_user", "secret_sauce", "Username and password do not match"),
    ("", "secret_sauce", "Username is required"),
    ("standard_user", "", "Password is required"),
])
def test_invalid_login_shows_error(page, config, username, password, expected):
    """TC-02 to TC-05: bad credentials rejected with a clear message."""
    login = LoginPage(page, config).open().login(username, password)

    expect(login.error).to_be_visible()
    expect(login.error).to_contain_text(expected)

    # rejected users must not get through
    expect(page).not_to_have_url(re.compile(r"inventory"))


def test_locked_out_user_is_refused(page, config):
    """TC-06: locked account refused even with the correct password."""
    login = LoginPage(page, config).open().login_as("locked_out")

    expect(login.error).to_contain_text("locked out")
    expect(page).not_to_have_url(re.compile(r"inventory"))


def test_logout_ends_the_session(page, config):
    """TC-07: logout ends the session and returns to login."""
    LoginPage(page, config).open().login_as("standard")

    inventory = InventoryPage(page, config)
    inventory.wait_until_ready()
    inventory.logout()

    expect(page.locator("#login-button")).to_be_visible()
