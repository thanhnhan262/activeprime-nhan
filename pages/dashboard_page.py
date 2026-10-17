from __future__ import annotations

import allure
from playwright.sync_api import FrameLocator

from pages.base_page import BasePage
from pages.data_issues_page import DataIssuesPage


class DashboardPage(BasePage):
    def __init__(self, app: FrameLocator) -> None:
        super().__init__(app)
        self.review_and_fix_button = app.get_by_role("button", name="Review & Fix Issues")

    @allure.step("Open Data Issues via 'Review & Fix Issues'")
    def go_to_data_issues(self) -> DataIssuesPage:
        """Open the Data Issues page and wait until the (randomly delayed) grid has loaded."""
        self.review_and_fix_button.click()
        issues_page = DataIssuesPage(self.app)
        issues_page.wait_until_loaded()
        return issues_page
