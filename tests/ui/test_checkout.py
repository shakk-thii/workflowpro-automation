"""Checkout tests. P1, this is the revenue path."""
import pytest
from playwright.sync_api import expect
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage


@pytest.fixture
def at_checkout(page, config):
    """Gets to the checkout form with one item in the cart."""
    LoginPage(page, config).open().login_as("standard")

    inv = InventoryPage(page, config)
    inv.wait_until_ready()
    inv.add_first_item_to_cart()
    inv.cart_link.click()

    cart = CartPage(page, config)
    cart.wait_until_ready()
    cart.checkout_button.click()

    checkout = CheckoutPage(page, config)
    checkout.wait_until_ready()
    return checkout


@pytest.mark.smoke
def test_complete_checkout_succeeds(at_checkout):
    """TC-14: The full purchase path works end to end."""
    at_checkout.fill_details("Shakthi", "Kumar", "641001")
    at_checkout.finish()

    expect(at_checkout.complete_header).to_contain_text("Thank you")


@pytest.mark.parametrize("first,last,postcode,expected", [
    ("", "Kumar", "641001", "First Name is required"),
    ("Shakthi", "", "641001", "Last Name is required"),
    ("Shakthi", "Kumar", "", "Postal Code is required"),
])
def test_checkout_requires_all_fields(at_checkout, first, last, postcode, expected):
    """TC-15 to TC-17: each required field is validated."""
    at_checkout.fill_details(first, last, postcode)
    expect(at_checkout.error).to_contain_text(expected)
