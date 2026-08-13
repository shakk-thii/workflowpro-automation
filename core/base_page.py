"""Shared behaviour for every page object."""
from playwright.sync_api import expect


class BasePage:
    def __init__(self, page, config):
        self.page = page
        self.config = config
        self.timeout = config["timeout"]

    def open(self, path=""):
        self.page.goto(f"{self.config['base_url']}{path}")
        self.wait_until_ready()
        return self

    def wait_until_ready(self):
        """Each page defines the element that proves it has loaded."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must define wait_until_ready()"
        )

    def screenshot(self, name):
        self.page.screenshot(path=f"reports/{name}.png")
