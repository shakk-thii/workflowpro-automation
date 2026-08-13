"""Cart tests."""
import pytest
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage


@pytest.fixture
def inventory(page, config):
    LoginPage(page, config).open().login_as("standard")
    inv = InventoryPage(page, config)
    inv.wait_until_ready()
    return inv


@pytest.mark.smoke
def test_adding_an_item_updates_the_badge(inventory):
    """TC-11: The cart count reflects what was added."""
    inventory.add_first_item_to_cart()
    expect(inventory.cart_badge).to_have_text("1")


def test_added_item_appears_in_the_cart(page, config, inventory):
    """TC-12: item is in the cart, not just counted on the badge."""
    inventory.add_first_item_to_cart()
    inventory.cart_link.click()

    cart = CartPage(page, config)
    cart.wait_until_ready()
    expect(cart.items).to_have_count(1)


def test_removing_an_item_empties_the_cart(page, config, inventory):
    """TC-13: removal clears the cart and the badge."""
    inventory.add_first_item_to_cart()
    inventory.cart_link.click()

    cart = CartPage(page, config)
    cart.wait_until_ready()
    cart.remove_first_item()

    expect(cart.items).to_have_count(0)
    expect(page.locator(".shopping_cart_badge")).to_have_count(0)
