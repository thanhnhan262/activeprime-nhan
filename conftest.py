"""Shared pytest fixtures.

The app under test lives in ``app/`` and is served manually
(``python -m http.server 8080 --directory app``). Tests never start the server themselves;
they only verify it is reachable so a missing server produces one clear message instead of
five confusing timeouts.
"""

from __future__ import annotations

import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterator

import pytest
from playwright.sync_api import Browser, Page, expect

from pages.app_shell import AppShell
from pages.dashboard_page import DashboardPage
from pages.data_issues_page import DataIssuesPage
from utils.allure_helpers import attach_screenshot, attach_trace, write_environment

# The grid loads after a random 0.5-5 s delay, so web-first assertions need more headroom
# than Playwright's 5 s default.
EXPECT_TIMEOUT_MS = 10_000

EXTERNAL_FONT_URLS = re.compile(r"https://fonts\.(googleapis|gstatic)\.com/.*")


@pytest.fixture(scope="session", autouse=True)
def _configure_expect() -> Iterator[None]:
    expect.set_options(timeout=EXPECT_TIMEOUT_MS)
    yield
    expect.set_options(timeout=None)


@pytest.fixture(scope="session", autouse=True)
def _app_is_running(base_url: str | None) -> None:
    """Abort the whole run early, with instructions, if the app is not being served."""
    if not base_url:
        pytest.exit(
            "No base URL configured. Set `base_url` in pyproject.toml or pass --base-url.", 2
        )

    url = f"{base_url.rstrip('/')}/index.html"
    if urllib.parse.urlparse(url).scheme not in ("http", "https"):
        pytest.exit(f"Unsupported base URL scheme: {url}", 2)

    try:
        with urllib.request.urlopen(url, timeout=3) as response:  # scheme validated above
            if response.status != 200:
                raise OSError(f"HTTP {response.status}")
    except (urllib.error.URLError, OSError) as exc:
        pytest.exit(
            f"App under test is not reachable at {url} ({exc}).\n"
            "Start it first: in a separate terminal, from the repo root, run:\n"
            "  python3 -m http.server 8080 --directory app",
            2,
        )


@pytest.fixture
def app(page: Page) -> AppShell:
    """Fresh browser page opened on index.html with the welcome modal/banner dismissed."""
    # app.html @imports Google Fonts. Fonts are irrelevant to the tests, but a slow or blocked
    # request delays the page `load` event, so never depend on the external host.
    page.route(EXTERNAL_FONT_URLS, lambda route: route.abort())
    shell = AppShell(page)
    shell.open()
    return shell


@pytest.fixture
def dashboard(app: AppShell) -> DashboardPage:
    return DashboardPage(app.frame)


@pytest.fixture
def issues_page(dashboard: DashboardPage) -> DataIssuesPage:
    """The Data Issues page with the grid fully loaded."""
    return dashboard.go_to_data_issues()


# --------------------------------------------------------------------------------------
# Allure reporting
# --------------------------------------------------------------------------------------

_PHASE_REPORTS = pytest.StashKey[dict[str, pytest.TestReport]]()


def _has_failed(item: pytest.Item) -> bool:
    reports = item.stash.get(_PHASE_REPORTS, {})
    return any(report.failed for report in reports.values())


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Iterator[None]:
    """Remember each phase's report (setup/call/teardown) so fixtures can see the outcome."""
    outcome = yield
    report = outcome.get_result()
    item.stash.setdefault(_PHASE_REPORTS, {})[report.when] = report


@pytest.fixture(scope="session", autouse=True)
def _allure_environment(
    pytestconfig: pytest.Config, browser: Browser, browser_name: str, base_url: str | None
) -> None:
    results_dir = pytestconfig.getoption("allure_report_dir", default=None)
    if not results_dir:  # Allure disabled (no --alluredir)
        return
    write_environment(
        results_dir,
        browser_name=browser_name,
        browser_version=browser.version,
        headless=not pytestconfig.getoption("--headed"),
        base_url=base_url,
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item: pytest.Item) -> Iterator[None]:
    """Attach the final page state to the test result, whether it passed or failed.

    Done right after the test body (page still open, Allure still inside the test) so the
    screenshot is listed on the test itself rather than under a fixture teardown.
    """
    outcome = yield
    page = item.funcargs.get("page") if hasattr(item, "funcargs") else None
    if page is not None:
        failed = outcome.excinfo is not None
        attach_screenshot(page, "Failure screenshot" if failed else "Final page state")


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_runtest_teardown(item: pytest.Item) -> Iterator[None]:
    """Attach the Playwright trace of a failed test.

    pytest-playwright only writes trace.zip when the browser context closes, which happens
    during fixture teardown, so the file is attached after the teardown has finished.
    """
    yield
    if _has_failed(item):
        attach_trace(item.config.getoption("--output"), item.name)
