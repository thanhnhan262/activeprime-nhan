"""Editing the final row shows the typed value."""

from __future__ import annotations

import allure
from playwright.sync_api import expect

from pages.data_issues_page import DataIssuesPage

pytestmark = [
    allure.epic("GenericCRM data quality"),
    allure.feature("Data Issues grid"),
]


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
