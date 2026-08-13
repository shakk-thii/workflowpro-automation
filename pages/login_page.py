"""Login screen. All selectors for this page live here."""
from playwright.sync_api import expect
from core.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page, config):
        super().__init__(page, config)
        self.username = page.locator("#user-name")
        self.password = page.locator("#password")
        self.submit = page.locator("#login-button")
        self.error = page.locator("[data-test='error']")

    def wait_until_ready(self):
        expect(self.submit).to_be_visible(timeout=self.timeout)

    def login(self, username, password):
        self.username.fill(username)
        self.password.fill(password)
        self.submit.click()
        return self

    def login_as(self, user_key):
        user = self.config["users"][user_key]
        return self.login(user["username"], user["password"])
