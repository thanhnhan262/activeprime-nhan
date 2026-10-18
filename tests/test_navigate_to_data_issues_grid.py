"""Data Issues grid shows 10 issue cards."""

from __future__ import annotations

import allure
from playwright.sync_api import expect

from pages.dashboard_page import DashboardPage

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
