"""Helpers that enrich the Allure report: environment info, screenshots and traces."""

from __future__ import annotations

import platform
import re
import shutil
from importlib import metadata
from pathlib import Path

import allure
from playwright.sync_api import Page

CATEGORIES_FILE = Path(__file__).resolve().parent.parent / "reporting" / "categories.json"


def write_environment(
    results_dir: str | Path,
    *,
    browser_name: str,
    browser_version: str,
    headless: bool,
    base_url: str | None,
) -> None:
    """Write ``environment.properties`` and ``categories.json`` into the Allure results folder."""
    results = Path(results_dir)
    results.mkdir(parents=True, exist_ok=True)

    properties = {
        "Browser": browser_name,
        "Browser.Version": browser_version,
        "Headless": str(headless).lower(),
        "Base.URL": base_url or "n/a",
        "OS": f"{platform.system()} {platform.release()}",
        "Python.Version": platform.python_version(),
        "Playwright.Version": metadata.version("playwright"),
        "Pytest.Version": metadata.version("pytest"),
    }
    lines = (f"{key}={value}" for key, value in properties.items())
    (results / "environment.properties").write_text("\n".join(lines) + "\n", encoding="utf-8")

    if CATEGORIES_FILE.is_file():
        shutil.copy(CATEGORIES_FILE, results / "categories.json")


def attach_screenshot(page: Page, name: str) -> None:
    """Attach a PNG of the page; never let a screenshot problem change the test result."""
    try:
        allure.attach(page.screenshot(), name=name, attachment_type=allure.attachment_type.PNG)
    except Exception as exc:  # e.g. the page/browser is already closed
        allure.attach(
            f"Could not capture screenshot: {exc}",
            name=f"{name} (unavailable)",
            attachment_type=allure.attachment_type.TEXT,
        )


def find_trace(output_dir: str | Path, test_name: str) -> Path | None:
    """Locate the ``trace.zip`` pytest-playwright wrote for ``test_name``."""
    slug = re.sub(r"[^a-z0-9]+", "-", test_name.lower()).strip("-")
    matches = sorted(Path(output_dir).glob(f"*{slug}*/trace.zip"))
    return matches[0] if matches else None


def attach_trace(output_dir: str | Path, test_name: str) -> None:
    """Attach the Playwright trace (if any) plus the command to open it."""
    trace = find_trace(output_dir, test_name)
    if trace is None:
        return
    allure.attach.file(
        str(trace),
        name="Playwright trace (trace.zip)",
        attachment_type="application/zip",
        extension="zip",
    )
    allure.attach(
        f"playwright show-trace {trace}\n\nor drop the attached trace.zip on https://trace.playwright.dev",
        name="How to open the trace",
        attachment_type=allure.attachment_type.TEXT,
    )
