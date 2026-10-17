# activeprime-nhan

UI test automation for the mock "GenericCRM" data quality app, built with
**Playwright for Python (sync API)** and **pytest**, using the Page Object Model.

## Prerequisites

- Python 3.10+
- Nothing else for the app: it is included in this repo under `app/`
  (unmodified files from the assessment)

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

## Run the app under test

The tests expect the app (the `app/` folder of this repo) to already be served at
`http://localhost:8080`. They do not start it, and they never modify it. In a separate
terminal, from the repo root:

```bash
python -m http.server 8080 --directory app
```

If the app is not reachable, the run aborts immediately with that instruction.

## Run the tests

```bash
pytest                                   # all tests, headless Chromium
pytest tests/test_data_issues.py::test_edit_final_row_value   # a single test
pytest --headed --slowmo 300             # watch the browser
pytest --browser firefox                 # needs: playwright install firefox
pytest --base-url http://localhost:9000  # app served elsewhere (or set PYTEST_BASE_URL)
```

Every test is independent: each gets a fresh browser context and starts from
`/index.html`, so tests can run alone, in any order.

## Debugging failures

On failure, a screenshot and a Playwright trace are written to `test-results/`.
Open a trace with:

```bash
playwright show-trace test-results/<test-folder>/trace.zip
```

## Reporting (Allure)

Every `pytest` run writes raw results to `allure-results/` (cleared at the start of each run).
The report shows, per test: a readable title, description, severity and tags; the page-object
steps and assertions that ran; a final-page screenshot ("Failure screenshot" on failure); and,
for failed tests, the Playwright `trace.zip` with the command to open it. The run also records
environment info (browser and version, headless, base URL, OS, Python/Playwright/pytest versions)
and groups failures into assertion failures vs. locator/timeout errors
(`reporting/categories.json`).

Running the tests needs only the Python packages from `requirements.txt`. Viewing the report
additionally needs the **Allure CLI** (a Java program, so it also needs Java 8+):

```bash
brew install allure                     # macOS; installs Java as a dependency
# or: npm install -g allure-commandline   (plus a JDK)
```

```bash
allure serve allure-results                                   # build and open in the browser
allure generate allure-results -o allure-report --clean       # static report in allure-report/
```

Without the CLI you still get `allure-results/`, and failed traces can be opened directly with
`playwright show-trace` or by dropping `trace.zip` on https://trace.playwright.dev.
Trend history across runs comes from the published GitHub Pages report (see CI below); locally
each run starts without history.

## Project layout

```
conftest.py                 fixtures: app-reachable guard, expect timeout, app/dashboard/issues_page
pytest.ini                  base_url, failure artifacts (trace + screenshot), Allure output, strict markers
pyproject.toml              ruff configuration
app/                        the app under test (index.html, vf-container.html, app.html), unmodified
pages/
  app_shell.py              index.html, welcome modal + banner, access to the nested iframes
  dashboard_page.py         dashboard -> "Review & Fix Issues"
  data_issues_page.py       issue grid, select-all, selection counter
  components/issue_card.py  one issue card (checkbox, radios, original/final rows, inline edit)
tests/test_data_issues.py   the 5 tests
utils/allure_helpers.py     Allure attachments (screenshot, trace) and environment info
reporting/categories.json   Allure failure categories
.github/workflows/tests.yml lint, test, Allure report, GitHub Pages publish
```

## Design notes

The app is deliberately awkward to automate; these are the decisions that handle it:

- **Nested iframes.** The application is `index.html` > `#outerFrame` > `#appFrame`.
  `AppShell.frame` returns the innermost `FrameLocator`; all page objects are scoped to it.
- **No sleeps.** Overlays and delays (welcome modal after ~800 ms, loading spinner, grid
  loading after a random 0.5-5 s, "Saving..." spinner on edits) are handled with Playwright
  auto-waiting and web-first `expect` assertions. The expect timeout is raised to 10 s in
  `conftest.py`.
- **Welcome modal / banner.** `AppShell.open()` waits for the modal (it appears on a timer),
  clicks "Got it", and dismisses the banner, so tests always begin from a clean page.
- **Locating cards.** Cards are found with `[data-record-id]`. `data-testid="issue_grid"` is
  only set on every third card, so it must not be used to count or iterate the grid.
- **Role/label locators first** (`get_by_role("checkbox", ...)`, `get_by_role("radio", ...)`),
  with the app's stable `data-row-type` / `data-record-id` attributes for structure.
- **External fonts blocked.** `app.html` `@import`s Google Fonts. The `app` fixture aborts
  those requests so a slow or offline machine cannot delay the page `load` event. The app
  files themselves are never touched.
- **Transient values.** After choosing the "original" radio or editing a cell, the final row
  shows "Saving..." for a moment. Assertions on `card.final_value` retry until the value settles.

## Code quality

```bash
ruff check .
ruff format --check .
```

## CI

`.github/workflows/tests.yml` runs on every push to `main`, every pull request, and manually
(*Actions > UI tests > Run workflow*). It:

1. installs the Python dependencies and Chromium (browsers are cached per Playwright version),
2. runs `ruff`,
3. serves `./app` on port 8080 and waits until it answers,
4. runs `pytest`,
5. generates the Allure report (carrying trend history over from the last published report),
6. uploads `allure-report/` and `allure-results/` as artifacts (always) and the `test-results/`
   traces (on failure).

On `main` the report is also published to GitHub Pages, even when tests fail:

**https://thanhnhan262.github.io/activeprime-nhan/**

Pull requests never publish; download the `allure-report` artifact from the run instead
(unzip it and run `allure open <folder>`; opening `index.html` directly from disk does not work).

### One-time GitHub setup

In the repository: **Settings > Pages > Build and deployment > Source = GitHub Actions**.
Until this is set, the `deploy-report` job fails (the tests themselves are unaffected). Pages on
a private repository requires a paid GitHub plan.
