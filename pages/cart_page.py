"""Shopping cart."""
from playwright.sync_api import expect
from core.base_page import BasePage


class CartPage(BasePage):
    def __init__(self, page, config):
        super().__init__(page, config)
        self.title = page.locator(".title")
        self.items = page.locator(".cart_item")
        self.checkout_button = page.locator("#checkout")
        self.continue_shopping = page.locator("#continue-shopping")

    def wait_until_ready(self):
        expect(self.title).to_have_text("Your Cart", timeout=self.timeout)

    def remove_first_item(self):
        self.items.first.locator("button").click()
        return self
