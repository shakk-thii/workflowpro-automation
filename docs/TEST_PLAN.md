# Test Plan

**Project:** WorkFlow Pro, B2B multi-tenant project management SaaS
**Author:** Sadhanandham Shakthikumar
**Date:** August 2026

---

## 1. Purpose

Define what gets tested, in what order, and how we know when testing is done.

## 2. Scope

### In scope

- Authentication, including invalid credentials and locked accounts
- Session handling and logout
- Project listing, sorting, and display
- Cart and checkout, meaning the full transaction path
- API contract for project creation and retrieval
- Tenant isolation at both the API and UI layers
- Role permissions for Admin, Manager, and Employee
- Cross browser on Chrome, Firefox, and Safari
- Mobile layout on iOS and Android through BrowserStack

### Out of scope, and why

| Area | Reason |
|---|---|
| Performance and load | Different tooling and goals. Belongs in its own suite. |
| Penetration testing | Needs a security specialist. Tenant isolation is covered functionally here. |
| Visual regression | Needs a baseline store and a review process. Worth adding later. |
| Third party integrations | No sandbox credentials available. |
| Accessibility | Should be added using axe-core. Not covered here for time. |

## 3. How tests are prioritised

Ranked by what a failure costs the business, not by what is easy to automate.

**Priority 1, runs on every commit.** Anything that stops the business working: login, checkout, and tenant isolation. A failure here loses money or leaks customer data.

**Priority 2, runs on every commit.** High frequency journeys: viewing projects, adding to cart, sorting. Broken daily flows generate support load fast.

**Priority 3, runs nightly.** Edge cases, validation messages, and sorting variants. Real bugs, but they do not stop anyone working.

**Priority 4, on demand.** Cosmetic issues and rarely used admin screens.

Deliberately not automated: one-off exploratory checks, features still changing week to week, and anything where setup costs more than running it manually.

## 4. Approach

**The test pyramid.** Many fast API tests, fewer UI tests, very few full end to end tests. Inverting this produces a suite that is slow and flaky, and a slow suite stops being run.

**Negative cases carry equal weight.** For anything touching money, identity, or tenant boundaries, the failure path is tested as thoroughly as the success path. An Employee being able to delete projects is a security incident, and it is exactly the case people forget.

**Isolation is checked in both directions.** The correct data is present, and the wrong data is absent. Only checking presence means a leak showing two tenants side by side would still pass.

## 5. Environment

| Item | Value |
|---|---|
| Demo target | saucedemo.com |
| Framework | Playwright with pytest |
| Language | Python 3.9 or newer |
| Browsers | Chromium, Firefox, WebKit |
| Mobile | BrowserStack, credentials needed |
| CI | GitHub Actions |

## 6. Test data

Each test creates its own data with a unique name, so tests can run in any order and in parallel without colliding.

Cleanup lives in fixture teardown, never at the end of a test. Fixture cleanup runs whether the test passes or fails. Cleanup written as the last line of a test gets skipped every time the test fails, which is exactly when data was created and needs removing.

Credentials come from config or environment variables, never from the test files.

## 7. Entry criteria

- The build deploys to the test environment
- Test accounts exist with known permissions
- Test data can be seeded or created through the API
- The environment is reachable from CI

## 8. Exit criteria

- All Priority 1 and 2 tests pass
- No open Critical or High severity defects
- Any failure is either fixed or has a documented reason and an owner
- The HTML report is generated and reviewed

## 9. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Flaky tests erode trust in the suite | High | Wait on conditions, never on fixed durations. Quarantine and fix rather than retry. |
| Test data drifts over time | Medium | Unique data per test, cleanup in fixtures |
| BrowserStack cost overruns | Medium | Mobile runs nightly, not per commit. Device list kept small. |
| Suite grows too slow to run | High | Split by layer, run smoke on commit and the full suite nightly |
| Selectors break on frontend changes | Medium | Selectors live only in page objects, one file per screen |

## 10. Reporting

Every run produces an HTML report. Failures automatically capture a screenshot, a video, and a Playwright trace, which allows stepping through exactly what the page looked like at the moment it failed.

Artefacts are kept only on failure to control storage cost.
