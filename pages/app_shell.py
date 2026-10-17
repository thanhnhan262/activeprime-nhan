from __future__ import annotations

import allure
from playwright.sync_api import FrameLocator, Page, expect


class AppShell:
    """The outer ``index.html`` document and the iframes wrapping the application.

    Structure: ``index.html`` > ``#outerFrame`` (vf-container.html) > ``#appFrame`` (app.html).
    It also owns the page-level noise that appears on load: the welcome modal (shown after
    ~800 ms, blocks clicks) and the package-version banner.
    """

    PATH = "/index.html"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.welcome_modal = page.get_by_role("dialog", name="Welcome to GenericCRM")
        self.banner = page.get_by_role("alert").filter(has_text="Package v")

    @property
    def frame(self) -> FrameLocator:
        """Locator scope for the real application (the innermost iframe)."""
        return self.page.frame_locator("#outerFrame").frame_locator("#appFrame")

    @allure.step("Open the app and clear the welcome modal and banner")
    def open(self) -> None:
        self.page.goto(self.PATH)
        self.dismiss_welcome_modal()
        self.dismiss_banner()

    @allure.step("Dismiss the welcome modal")
    def dismiss_welcome_modal(self) -> None:
        # The modal is injected by a timer, so wait for it instead of assuming it is there.
        expect(self.welcome_modal).to_be_visible()
        self.welcome_modal.get_by_role("button", name="Got it").click()
        expect(self.welcome_modal).to_be_hidden()

    @allure.step("Dismiss the package-version banner")
    def dismiss_banner(self) -> None:
        self.banner.get_by_role("button", name="Dismiss banner").click()
        expect(self.banner).to_be_hidden()
