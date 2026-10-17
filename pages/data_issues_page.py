from __future__ import annotations

import allure
from playwright.sync_api import FrameLocator, Locator, expect

from pages.base_page import BasePage
from pages.components.issue_card import IssueCard


class DataIssuesPage(BasePage):
    def __init__(self, app: FrameLocator) -> None:
        super().__init__(app)
        # NOTE: do not use data-testid="issue_grid" to find cards; the app only sets it on
        # every third card. `data-record-id` is present on every card.
        self.cards: Locator = app.locator("[data-record-id]")
        self.loading_indicator = app.get_by_text("Loading issues...")
        self.select_all_checkbox = app.get_by_role("checkbox", name="Select all issues")
        # The "N issue(s) selected" bar; hidden while nothing is selected.
        self.selection_bar = app.get_by_role("alert")

    @allure.step("Wait for the issues grid to finish loading")
    def wait_until_loaded(self) -> None:
        expect(self.loading_indicator).to_be_hidden()
        expect(self.cards.first).to_be_visible()

    def card(self, index: int) -> IssueCard:
        """Card by zero-based position on the grid."""
        return IssueCard(self.cards.nth(index))

    def card_by_sfid(self, sfid: str) -> IssueCard:
        return IssueCard(self.app.locator(f'[data-record-id="{sfid}"]'))

    def all_cards(self) -> list[IssueCard]:
        return [self.card(i) for i in range(self.cards.count())]

    @allure.step("Tick the 'Select all' checkbox")
    def select_all(self) -> None:
        self.select_all_checkbox.check()

    @allure.step("Untick the 'Select all' checkbox")
    def deselect_all(self) -> None:
        self.select_all_checkbox.uncheck()
