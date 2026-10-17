from __future__ import annotations

import re

import allure
from playwright.sync_api import Locator

EMPTY_CELL_PLACEHOLDER = "\u2014"  # the app renders empty values as an em dash

_HEADER_NAMES_JS = """
els => els.map(e => {
    const label = e.querySelector(':scope > span');   // skips the tooltip text in the header
    return (label ? label.textContent : e.textContent).trim();
})
"""


class IssueCard:
    """One issue card: a header with a checkbox plus an original / suggested / final table."""

    def __init__(self, root: Locator) -> None:
        self.root = root
        self.checkbox = root.get_by_role("checkbox")
        self.original_radio = root.get_by_role("radio", name=re.compile(r"^Select original value"))
        self.suggested_radio = root.get_by_role(
            "radio", name=re.compile(r"^Select suggested value")
        )
        # The editable cell of the final row (the issue column); text is "Saving..." mid-update.
        self.final_value = self._row("final").locator(".cell-editable")

    def _row(self, row_type: str) -> Locator:
        return self.root.locator(f'tr[data-row-type="{row_type}"]')

    @property
    def sfid(self) -> str:
        return self.root.get_attribute("data-record-id") or ""

    @allure.step("Read the original row of the card")
    def original_row(self) -> dict[str, str]:
        """Original row as ``{column header: value}``, including the ``sfid`` column."""
        headers = self.root.locator("thead th").evaluate_all(_HEADER_NAMES_JS)
        cells = [text.strip() for text in self._row("original").locator("td").all_text_contents()]
        # The first column only holds the "Original" row label.
        return {
            header: "" if value == EMPTY_CELL_PLACEHOLDER else value
            for header, value in zip(headers[1:], cells[1:], strict=True)
        }

    def original_issue_value(self) -> str:
        """Original value of the column flagged as having the issue."""
        text = self._row("original").locator("td.cell-issue").inner_text().strip()
        return "" if text == EMPTY_CELL_PLACEHOLDER else text

    @allure.step("Tick the card checkbox")
    def select(self) -> None:
        self.checkbox.check()

    @allure.step("Choose the original value")
    def select_original(self) -> None:
        self.original_radio.check()

    @allure.step("Edit the final value to {value} and confirm with Enter")
    def edit_final_value(self, value: str) -> None:
        """Inline-edit the final row's issue column and confirm with Enter."""
        self.final_value.click()
        editor = self.root.get_by_role("textbox")
        editor.clear()
        editor.fill(value)
        editor.press("Enter")
