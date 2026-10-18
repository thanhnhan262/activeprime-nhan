"""Selection counter tracks checked issues."""

from __future__ import annotations

import allure
from playwright.sync_api import expect

from pages.data_issues_page import DataIssuesPage

EXPECTED_ISSUE_COUNT = 10

pytestmark = [
    allure.epic("GenericCRM data quality"),
    allure.feature("Data Issues grid"),
]


@allure.story("Selection")
@allure.title("Selection counter tracks checked issues")
@allure.description(
    "Select cards 1, 3 and 5, then select all, then deselect all, verifying the "
    "'N issue(s) selected' counter at each stage."
)
@allure.severity(allure.severity_level.NORMAL)
@allure.tag("selection")
def test_checkbox_selection_count(issues_page: DataIssuesPage) -> None:
    expect(issues_page.cards).to_have_count(EXPECTED_ISSUE_COUNT)

    for position in (1, 3, 5):  # 1st, 3rd and 5th cards (1-based)
        issues_page.card(position - 1).select()
    with allure.step("Assert the counter shows '3 issue(s) selected'"):
        expect(issues_page.selection_bar).to_have_text("3 issue(s) selected")

    issues_page.select_all()
    with allure.step(f"Assert the counter shows '{EXPECTED_ISSUE_COUNT} issue(s) selected'"):
        expect(issues_page.selection_bar).to_have_text(f"{EXPECTED_ISSUE_COUNT} issue(s) selected")

    issues_page.deselect_all()
    with allure.step("Assert the selection counter is no longer visible"):
        expect(issues_page.selection_bar).not_to_be_visible()
