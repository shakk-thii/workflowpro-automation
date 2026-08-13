"""Product listing, shown after a successful login."""
from playwright.sync_api import expect
from core.base_page import BasePage


class InventoryPage(BasePage):
    def __init__(self, page, config):
        super().__init__(page, config)
        self.title = page.locator(".title")
        self.items = page.locator(".inventory_item")
        self.cart_badge = page.locator(".shopping_cart_badge")
        self.cart_link = page.locator(".shopping_cart_link")
        self.sort_dropdown = page.locator("[data-test='product-sort-container']")
        self.menu_button = page.locator("#react-burger-menu-btn")
        self.logout_link = page.locator("#logout_sidebar_link")

    def wait_until_ready(self):
        expect(self.title).to_have_text("Products", timeout=self.timeout)

    def add_first_item_to_cart(self):
        self.items.first.locator("button").click()
        return self

    def item_names(self):
        return self.page.locator(".inventory_item_name").all_text_contents()

    def item_prices(self):
        raw = self.page.locator(".inventory_item_price").all_text_contents()
        return [float(p.replace("$", "")) for p in raw]

    def sort_by(self, option):
        self.sort_dropdown.select_option(option)
        return self

    def logout(self):
        self.menu_button.click()
        expect(self.logout_link).to_be_visible()
        self.logout_link.click()
        return self
