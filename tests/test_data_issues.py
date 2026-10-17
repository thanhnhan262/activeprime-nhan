"""Data Issues grid tests. Every test starts from /index.html via the ``app`` fixture."""

from __future__ import annotations

import allure
from playwright.sync_api import expect

from pages.dashboard_page import DashboardPage
from pages.data_issues_page import DataIssuesPage

EXPECTED_ISSUE_COUNT = 10

pytestmark = [
    allure.epic("GenericCRM data quality"),
    allure.feature("Data Issues grid"),
]


@allure.story("Navigation")
@allure.title("Data Issues grid shows 10 issue cards")
@allure.description(
    "From the dashboard, open 'Review & Fix Issues' and verify the grid lists 10 issue cards."
)
@allure.severity(allure.severity_level.BLOCKER)
@allure.tag("smoke", "navigation")
def test_navigate_to_data_issues_grid(dashboard: DashboardPage) -> None:
    issues_page = dashboard.go_to_data_issues()

    with allure.step(f"Assert {EXPECTED_ISSUE_COUNT} issue cards are displayed"):
        expect(issues_page.cards).to_have_count(EXPECTED_ISSUE_COUNT)


@allure.story("Issue data")
@allure.title("Every issue card has a non-empty sfid in its original row")
@allure.description(
    "Extract the original row of all 10 cards and verify each has a non-empty sfid that "
    "matches the card's record id."
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
        with allure.step(f"Assert card #{position} has a non-empty sfid matching its record id"):
            assert original.get("sfid"), (
                f"Card #{position}: original row has an empty sfid: {original}"
            )
            assert original["sfid"] == card.sfid, (
                f"Card #{position}: sfid does not match the record id"
            )


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


@allure.story("Edit value")
@allure.title("Editing the final row shows the typed value")
@allure.description(
    "On card 00Qak00000RHtuzEAD, replace the final Street value with '123 Test Street'."
)
@allure.severity(allure.severity_level.CRITICAL)
@allure.tag("edit")
def test_edit_final_row_value(issues_page: DataIssuesPage) -> None:
    new_value = "123 Test Street"
    card = issues_page.card_by_sfid("00Qak00000RHtuzEAD")
    expect(card.root).to_have_count(1)

    card.edit_final_value(new_value)

    with allure.step(f"Assert the final row shows '{new_value}'"):
        expect(card.final_value).to_have_text(new_value)


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
