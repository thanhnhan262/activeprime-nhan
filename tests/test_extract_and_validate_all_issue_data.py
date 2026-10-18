"""Every issue card has a non-empty sfid in its original row."""

from __future__ import annotations

import allure
from playwright.sync_api import expect

from pages.data_issues_page import DataIssuesPage

EXPECTED_ISSUE_COUNT = 10

pytestmark = [
    allure.epic("GenericCRM data quality"),
    allure.feature("Data Issues grid"),
]


@allure.story("Issue data")
@allure.title("Every issue card has a non-empty sfid in its original row")
@allure.description(
    "Extract the original row of all 10 cards and verify each has a non-empty sfid."
)
@allure.severity(allure.severity_level.CRITICAL)
@allure.tag("data")
def test_extract_and_validate_all_issue_data(issues_page: DataIssuesPage) -> None:
    with allure.step(f"Assert {EXPECTED_ISSUE_COUNT} issue cards are displayed"):
        expect(issues_page.cards).to_have_count(EXPECTED_ISSUE_COUNT)

    cards = issues_page.all_cards()
    assert len(cards) == EXPECTED_ISSUE_COUNT

    for position, card in enumerate(cards, start=1):
        original = card.original_row()
        with allure.step(f"Assert card #{position} has a non-empty sfid"):
            assert original.get("sfid"), (
                f"Card #{position}: original row has an empty sfid: {original}"
            )
