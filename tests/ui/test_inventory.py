"""Product listing tests."""
import pytest
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


@pytest.fixture
def inventory(page, config):
    """Log in and return a loaded product page."""
    LoginPage(page, config).open().login_as("standard")
    inv = InventoryPage(page, config)
    inv.wait_until_ready()
    return inv


@pytest.mark.smoke
def test_all_products_are_listed(inventory):
    """TC-08: The expected number of products renders."""
    expect(inventory.items).to_have_count(6)


def test_sort_by_price_low_to_high(inventory):
    """TC-09: check the list order, not just the dropdown value."""
    inventory.sort_by("lohi")
    prices = inventory.item_prices()
    assert prices == sorted(prices), f"Not sorted ascending: {prices}"


def test_sort_by_name_z_to_a(inventory):
    """TC-10: Reverse alphabetical sort."""
    inventory.sort_by("za")
    names = inventory.item_names()
    assert names == sorted(names, reverse=True), f"Not sorted Z to A: {names}"
