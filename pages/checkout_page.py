"""Checkout, across its three steps."""
from playwright.sync_api import expect
from core.base_page import BasePage


class CheckoutPage(BasePage):
    def __init__(self, page, config):
        super().__init__(page, config)
        self.first_name = page.locator("#first-name")
        self.last_name = page.locator("#last-name")
        self.postal_code = page.locator("#postal-code")
        self.continue_button = page.locator("#continue")
        self.finish_button = page.locator("#finish")
        self.error = page.locator("[data-test='error']")
        self.complete_header = page.locator(".complete-header")
        self.total_label = page.locator(".summary_total_label")

    def wait_until_ready(self):
        expect(self.first_name).to_be_visible(timeout=self.timeout)

    def fill_details(self, first, last, postcode):
        self.first_name.fill(first)
        self.last_name.fill(last)
        self.postal_code.fill(postcode)
        self.continue_button.click()
        return self

    def finish(self):
        self.finish_button.click()
        return self
