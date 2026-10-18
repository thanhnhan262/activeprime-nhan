"""Selecting the original value updates the final row."""

from __future__ import annotations

import allure
from playwright.sync_api import expect

from pages.data_issues_page import DataIssuesPage

pytestmark = [
    allure.epic("GenericCRM data quality"),
    allure.feature("Data Issues grid"),
]


@allure.story("Choose value")
@allure.title("Selecting the original value updates the final row")
@allure.description(
    "On the 7th card, select the original value and verify the final row reflects it "
    "instead of the pre-selected suggested value."
)
@allure.severity(allure.severity_level.CRITICAL)
@allure.tag("selection")
def test_select_original_value_updates_final_row(issues_page: DataIssuesPage) -> None:
    card = issues_page.card(6)  # 7th card
    original_value = card.original_issue_value()
    assert original_value, "Precondition: the 7th card has an original value to select"

    with allure.step("Precondition: final row differs from the original value"):
        expect(card.final_value).not_to_have_text(original_value)

    card.select_original()

    # Web-first assertion retries through the transient "Saving..." state.
    with allure.step(f"Assert the final row shows the original value '{original_value}'"):
        expect(card.final_value).to_have_text(original_value)
