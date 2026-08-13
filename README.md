# WorkFlow Pro Test Automation Framework

QA automation case study submission.
**Sadhanandham Shakthikumar** | Automation Engineering Intern | August 2026

---

## An important note on what runs and what does not

The case study is set on a fictional application, `app.workflowpro.com`, which does not exist. Tests written against it cannot execute.

So this repository does two things:

**1. The designed framework for WorkFlow Pro.** Page objects, config, and the corrected tests from Part 1 and the integration test from Part 3. These are marked `@pytest.mark.skip` because the target application is not real. They show the design.

**2. The same framework proven against a real site.** The identical structure runs against `saucedemo.com`, a public demo application. These tests actually execute and produce the report in `reports/`.

I chose this over submitting code that cannot run. The framework is the deliverable, and demonstrating it working on a real target is the only honest way to show it works.

---

## Setup

Requires Python 3.9 or newer.

```bash
git clone https://github.com/shakk-thii/workflowpro-automation.git
cd workflowpro-automation

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
playwright install chromium
```

## Running the tests

```bash
# Everything that can run
pytest

# Only the fast smoke tests
pytest -m smoke

# A different browser
pytest --browser firefox

# Watch it happen in a visible browser
pytest --headed

# Generate the HTML report
pytest --html=reports/report.html --self-contained-html
```

## What is covered

| Area | Tests | Runs |
|---|---|---|
| Login, valid and invalid | 5 | Yes |
| Session and logout | 2 | Yes |
| Product listing and sort | 3 | Yes |
| Cart add and remove | 3 | Yes |
| Checkout, including validation | 4 | Yes |
| WorkFlow Pro login (Part 1) | 2 | Skipped, app is fictional |
| WorkFlow Pro integration (Part 3) | 1 | Skipped, app is fictional |
| API patterns (design only) | 4 | Skipped, API is fictional |
**Totals:** 24 collected, 17 pass, 7 skipped.

## What is not covered, and why

**Performance and load.** Different tooling, different goals. Out of scope for a functional suite.

**Visual regression.** Needs a baseline image store and a review process. Worth adding, but it is a project of its own.

**Accessibility.** Should be added. I would use axe-core through the Playwright integration. Not done here for time.

**Real mobile devices.** Requires BrowserStack credentials. The connection code is included and documented but cannot run without an account.

## Layout

```
config/     environment, browser, and role settings
core/       base page class and API client
pages/      one file per screen, all selectors live here
tests/      split by layer: ui, api, integration
docs/       test plan and testing approach
reports/    generated HTML report, traces, screenshots
```

## Documentation

- [Test Plan](docs/TEST_PLAN.md) — scope, priorities, entry and exit criteria
- [Testing Approach](docs/TESTING_APPROACH.md) — the full case study answer
- [Test Cases](docs/TEST_CASES.md) — the case list with priority

## Reports

After a run, open `reports/report.html`.

Failures automatically capture a screenshot, a video, and a Playwright trace. View a trace with:

```bash
playwright show-trace reports/traces/<name>.zip
```

