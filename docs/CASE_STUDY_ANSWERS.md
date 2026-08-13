# **B2B SaaS Platform Testing: Multi-Platform Automation**

**Candidate:** Sadhanandham Shakthikumar 

**Role:** Automation Engineering Intern 

**Submitted:** 14 August 2026

The brief says requirements are intentionally incomplete, so I have stated my assumptions as I go and listed the questions I would ask before building this for real.

---

# **Part 1: Debugging Flaky Test Code**

## **The one idea behind all of this**

A test script and a browser are two separate programs running at different speeds. Python runs in microseconds. The browser has to fetch data over the network, run JavaScript, and draw the page, which takes hundreds of milliseconds.

So the script fires a command and immediately moves to the next line while the browser is still working. That gap is a race, and every flaky failure in this file comes from it.

## **Task 1: Flakiness issues**

### **What is already correct**

The four lines that navigate, fill the form, and click are fine. Playwright waits automatically before every action. It checks that the element exists, is visible, and is clickable before doing anything. The login steps are already protected, so adding waits there would not help.

The problem is only in the lines that check results.

### **Issue 1: The URL check does not wait**

assert page.url \== "https://app.workflowpro.com/dashboard"

**`page.url`** reads the address bar once and returns whatever is there at that instant. It does not wait or try again. The click has only just happened, so the browser is usually still on the login page.

There is a second problem. Comparing the full string exactly means a trailing slash or an extra query parameter will fail a login that actually worked.

**Fix:** **`expect(page).to_have_url(re.compile(r"/dashboard"))`**

### **Issue 2: The visibility check does not wait**

assert page.locator(".welcome-message").is\_visible()

**`is_visible()`** answers true or false immediately. If the message has not appeared yet, it says false and the test fails.

Issues 1 and 2 share the same cause, and this is the main point of my answer. Playwright waits automatically when you click or type, but a plain Python `assert` skips all of that. The tool was ready to handle the timing and these lines went around it.

**Fix:** **`expect(page.locator(".welcome-message")).to_be_visible()`**

### **Issue 3: The tenant test passes when it should fail**

projects \= page.locator(".project-card").all()  
for project in projects:  
    assert "Company2" in project.text\_content()

**`.all()`** grabs the list of cards right now. If the dashboard has not finished loading, that list is empty.

An empty list means the loop never runs. No check happens at all. Python reaches the end of the function without any error, so pytest reports the test as passed.

This is the most serious problem here. Issues 1 and 2 fail loudly, so at least someone notices. This one quietly reports success on a test whose whole job is checking that one company cannot see another company's data. It would stay green even during a real data leak, and the team would keep trusting it.

**Fix:** wait for the cards to appear, then check the count is not zero before looping. An empty page now fails with a clear message instead of passing.

### **Issue 4: Reading the card text does not wait**

**`text_content()`** also reads once. A card can exist on the page before its text has loaded, which returns an empty string and fails the check.

**Fix:** use **`to_contain_text()`**, which keeps checking until the text appears.

### **Issue 5: 2FA is not handled**

The brief says some users have two factor authentication. Both tests assume that clicking login goes straight to the dashboard. For a 2FA user it goes to a code entry screen instead, and everything after that fails.

This looks like flakiness because whether 2FA triggers can depend on the account or the network it is coming from. The same test can pass in one place and fail in another with no code change.

**Fix:** after clicking login, wait for whichever screen appears, the dashboard or the code entry, and handle both. If a code is needed but no test secret is configured, fail with a message that says exactly that.

### **Issue 6: The browser is never closed when a test fails**

**`browser.close()`** is the last line, sitting after the checks. When a check fails, Python stops right there and that line never runs. The browser process stays alive.

To be accurate, this does not make this test flaky. It makes other tests flaky. Each leftover browser holds a few hundred megabytes. After several failures the CI machine runs out of memory and unrelated tests start failing for no visible reason.

**Fix:** move the browser setup into a pytest fixture. Fixtures guarantee cleanup runs whether the test passes or fails, so it cannot be forgotten.

### **Issue 7: The isolation check is incomplete**

This is a logic gap rather than a timing bug, but I think it is the most important thing missing.

The test confirms that every project shown belongs to Company2. It never confirms that Company1's projects are not shown. Those are two different things. If a leak displayed both companies side by side, this test would still pass, because it only looks at the cards it found.

Checking isolation needs both halves. The right data is there, and the wrong data is not.

**Fix:** add a check that Company1 content appears zero times.

## **Task 2: Why it fails in CI and not locally**

The code is identical in both places. Only the timing changes.

**1\. The CI machine is slower.** This is the main reason. A laptop draws the dashboard in around 80ms with everything cached and nothing else running. A CI runner is a shared container competing with other jobs, so the same page can take over a second. Same code, opposite result.

**2\. Everything is cold in CI.** Each run starts on a fresh machine with no cached files and no existing connections. It is always the slow path. Locally you run the same page repeatedly, so you are always on the fast path. That is why the bug is invisible while developing.

**3\. Different browsers and screen sizes.** Firefox and Safari load differently from Chrome, so a race that barely passes in one can consistently fail in another. The code only launches Chromium, so it cannot even test the other two.

Screen size matters more than the browser. On a narrow screen the project cards may be hidden behind a menu, so the test genuinely finds nothing. It fails on mobile and passes on desktop, which looks random but is really an assumption nobody wrote down.

**4\. Tenants load at different speeds.** Company1 might have 5 projects and Company2 might have 5,000. One timeout cannot suit both. It will be too short for the big tenant or too slow for everyone else, so failures group by tenant instead of appearing randomly.

**5\. 2FA can trigger only in CI.** If the app asks for a code when it sees an unfamiliar IP address, CI machines get challenged and laptops do not. The test lands on the wrong screen and fails while the app is working perfectly. This is the hardest one to diagnose because nothing is actually broken.

**Why adding a sleep does not fix it.** To survive a slow day the sleep has to be longer. To keep a 400 test suite fast it has to be shorter. No single number works for both. The real problem is that a fixed number is a guess about something that changes every run.

**`expect()`** solves this because it waits for a condition instead of a duration. It checks every 100ms and continues the moment the page is ready. Fast page, it waits 100ms. Slow page, it waits as long as needed. Nothing has to be guessed.

## **Task 3: The corrected version**

The changed lines:

\# was: assert page.url \== "https://app.workflowpro.com/dashboard"  
expect(page).to\_have\_url(re.compile(r"/dashboard"))

\# was: assert page.locator(".welcome-message").is\_visible()  
expect(page.locator(".welcome-message")).to\_be\_visible()

\# was: projects \= page.locator(".project-card").all()  
\#      for project in projects:  
\#          assert "Company2" in project.text\_content()

cards \= page.locator(".project-card")  
expect(cards.first).to\_be\_visible(timeout=15000)

count \= cards.count()  
assert count \> 0, "No project cards rendered, cannot verify tenant isolation"

for i in range(count):  
    expect(cards.nth(i)).to\_contain\_text("Company2")

\# new: the check that was missing  
expect(page.get\_by\_text("Company1")).to\_have\_count(0)

### **Error handling**

**Clear failure messages.** Every check that can fail for an environment reason says what it was verifying, not just that something was false. "No project cards rendered, cannot verify tenant isolation" turns a confusing 2am CI failure into a five second diagnosis.

**Evidence on failure.** Playwright can save a screenshot, a video, and a full trace whenever a test fails. The trace lets you step through exactly what the page looked like at that moment. Saving these only on failure keeps storage costs low.

**Handle 2FA explicitly.** Wait for either the dashboard or the code screen and react to whichever arrives, instead of assuming one.

**No automatic retries.** I would not fix a flaky test by running it again. A test that passes on the third try is usually reporting a real race condition that users also hit, and retrying hides that signal. I would move the flaky test out of the blocking suite so it does not stop the team shipping, log how often it fails, find the real cause from the trace, fix it, then put it back. I would confirm this matches the team's approach first.

### **Reliability improvements**

**Browser setup in a fixture.** Cleanup then runs whether the test passes or fails, so the leak becomes impossible rather than something someone has to remember.

**A fresh browser session per test.** Otherwise the Company1 login cookie carries into the Company2 test, and the isolation test silently checks the wrong company while still appearing to pass.

**A fixed screen size.** Since CI uses different sizes, the test should state what it expects instead of inheriting whatever the machine defaults to.

**URLs and passwords in environment variables.** The hardcoded URL means the tests cannot run against staging without editing the code. Passwords in code get saved into version history permanently and are visible to anyone with repository access.

**A longer timeout only where it is needed.** Slow tenants get their own timeout rather than slowing down every test in the suite.

**Better selectors.** I would target the visible label and button text rather than CSS ids. An id changes when a developer tidies up the styling, which breaks the test even though nothing a user sees has changed. This is a maintenance improvement, not a flakiness fix, and I am not claiming it as one.

## **Assumptions for Part 1**

**2FA.** I assumed test accounts either have 2FA off or provide a fixed code seed. I would need to know which. If 2FA triggers based on the network, the CI machines likely need to be allowlisted.

**Screen size.** I assumed a standard desktop size where the cards appear in a grid. Does the mobile version use a different layout, which would need its own selectors?

**Test data.** I assumed each tenant has a known set of projects. Checking against data the test does not control is unstable. Can the tenants be reset to a known state before a run?

**Identifying the tenant.** The test looks for the text "Company2" inside the cards. That assumes the name always appears there. A dedicated tenant attribute in the HTML would be far more reliable. Could one be added?

**Timeout.** I used 15 seconds as a guess. I would want the real load times per tenant so the number comes from data.

---

# **Part 2: Test Framework Design**

## **Folder structure**

workflowpro-automation/  
├── config/  
│   ├── environments.yaml     \# URLs for local, staging, production, and each tenant  
│   ├── browsers.yaml         \# browser and device settings  
│   └── roles.yaml            \# what each role is allowed to do  
│  
├── core/  
│   ├── base\_page.py          \# shared behaviour for all pages  
│   ├── api\_client.py         \# logged in HTTP session for API calls  
│   └── auth.py               \# login and session handling  
│  
├── pages/                    \# one file per screen, holds all the selectors  
│   ├── login\_page.py  
│   ├── dashboard\_page.py  
│   └── project\_page.py  
│  
├── tests/  
│   ├── api/                  \# fast, run on every commit  
│   ├── ui/                   \# slower, run on every commit  
│   ├── integration/          \# API and UI together  
│   └── mobile/               \# slowest and costs money, run nightly  
│  
├── fixtures/  
│   └── conftest.py           \# shared setup and cleanup  
│  
├── reports/                  \# screenshots, videos, traces  
├── .github/workflows/        \# CI pipeline  
└── requirements.txt

## **Why it is shaped this way**

The rule I followed is that things which change for different reasons should live in different places.

Selectors change when the frontend changes, so they all live in **`pages/`**. URLs change when infrastructure changes, so they live in **`config/`**. Test intent changes when the product changes, so it lives in **`tests/`**. If a developer renames a CSS class, only one file should need editing no matter how many tests use it.

I split tests by layer rather than by feature because the layers cost very different amounts to run. API tests take milliseconds. Mobile tests on BrowserStack take minutes and cost money per session. Splitting this way lets the CI pipeline pick exactly which group to run and when.

## **Page objects**

Each screen gets a class that holds its selectors and the actions you can do on it. Tests then call those actions instead of touching the page directly.

Two reasons this matters.

The two tests in Part 1 already repeat the same eight lines of login code. At fifty tests, changing the login flow means fifty edits and you will miss some. Test suites do not usually die from being wrong. They die from being too expensive to maintain.

It also makes tests readable. **`dashboard.create_project("Q3 Migration")`** can be reviewed for correctness by someone who has never used Playwright.

One rule I would enforce: every page object must define what "finished loading" means for that screen. Since the app loads content dynamically, each page needs one element that proves it is genuinely ready. Putting that in the page object means no test ever has to guess.

## **Configuration**

Three things vary independently, and the common mistake is treating them as one.

**Environment:** local, staging, production. Different base URLs.

**Tenant:** company1, company2. Different subdomains, different data sizes, so different timeouts.

**Browser:** Chrome, Firefox, Safari, plus mobile devices through BrowserStack.

All three live in YAML config files. Nothing is hardcoded in a test. The command line picks the combination:

**pytest \--env=staging \--tenant=company2 \--browser=firefox**

The order of precedence is command line first, then environment variables, then the YAML defaults. Passwords and API keys never go in YAML. They are referenced as variables and filled in at runtime.

The goal is that the same test file runs against any environment, any tenant, and any browser without a single line of code changing. Any other approach means either duplicating tests per tenant or editing source code to switch targets.

Tenant timeouts go in config too. The brief says tenants load at different speeds, and if that difference is written into individual tests it gets scattered everywhere. In config it is one visible line per tenant.

## **User roles**

The three roles have different permissions, so I would store the expected permissions in a config file rather than in the tests. One test can then loop over all three roles and check both what they can do and what they cannot.

The negative cases matter more than the positive ones. An Employee being able to delete projects is a security bug, and it is exactly the case people forget to write a test for.

## **Login speed**

Logging in through the UI before every test is slow and pointlessly re-tests the login flow hundreds of times. The better approach is to log in once per role and tenant, save the session, and reuse it for tests that just need to be logged in. Login itself still gets tested properly, from a clean start, in its own test file.

The trade-off worth naming: reusing sessions is faster but weakens isolation. For a multi tenant product I would keep a separate saved session per tenant and role, and still start each test from a fresh browser session, so cookies never cross between companies.

## **Missing requirements**

These are the gaps I hit while designing, and what I would ask before building.

### **Test data**

Can the tenants be reset to a known state before a test run, or does everyone share an environment with manually created data? This is the biggest unknown and everything else depends on it.

Is there a way to clean up test data, or does cleanup have to go through the same public API used to create it?

Are tests allowed to run against production? The original code points at the live URL, which suggests they might be. If so, cleanup matters much more and destructive tests need to be kept well away.

How much data does the largest tenant actually have? My timeout numbers are guesses. Real figures would let me size them properly.

### **Parallel execution**

Is the environment safe for tests running at the same time, or do they interfere with each other? This decides whether tests can run in parallel at all.

Can two tests use the same tenant simultaneously? If yes, every test must create uniquely named data.

What suite runtime is acceptable? A 40 minute suite stops being run on every commit and quietly becomes a nightly job nobody watches. That number decides how much parallelism is worth building.

### **BrowserStack and cost**

How many parallel sessions does the plan allow? That is a hard limit on how fast the mobile suite can run and I cannot design the pipeline without it.

Which devices do customers actually use? Testing everything is neither affordable nor useful. Real usage data would let me pick three or four that cover most users.

Should mobile run on every commit or nightly? My assumption is nightly, because sessions cost money and mobile bugs are usually layout problems rather than logic ones. That is a business decision, so I would want it confirmed.

### **Reporting**

Who reads the results and when? A developer needs a failure in their pull request within minutes. A QA lead needs trends over weeks. Those are two different outputs.

Is there already a reporting tool in use? I would not introduce a new one if the team has something working.

Is flakiness tracked as a number? Without knowing how often each test fails over time, you cannot tell a genuinely flaky test from one that is correctly catching a real intermittent bug.

### **Access**

Are test accounts set up with 2FA off, and can the CI machines be allowlisted?

Does staging hold a realistic amount of data, or is it small enough that timing problems only show up in production?

How are API tokens issued for tests and how long do they last? A token expiring halfway through a run looks exactly like flakiness.

### **Scope**

Are accessibility, performance, and visual testing in scope? None are mentioned, all are common for this kind of product, and each would change the structure. I assumed they are out of scope but designed so they could be added as new test folders without rearranging anything.

---

# **Part 3: API and UI Integration Test**

## **My approach**

The scenario crosses three layers, so the main decision is which layer checks what. Testing the same thing three times is waste. Testing it nowhere is a gap.

**The API checks the write.** Did the project get created, with the right details, under the right company.

**The web UI checks that it reaches the user.** This is the part an API test cannot cover, because a project can exist in the database and still never appear on screen.

**Mobile checks layout only.** I am not re-running business logic on a BrowserStack session that is slow and costs money per minute. The logic is already covered above.

**Tenant isolation is checked twice, at the API and in the UI.** This is deliberate. They can fail independently. The API can block access correctly while the UI leaks data through a filter that runs in the browser, and the reverse is also possible.

## **The test**

@pytest.mark.integration  
def test\_project\_creation\_flow(page, api\_client, config, project\_factory):

    \# 1\. Create the project through the API  
    project\_name \= unique\_name("integration")  
    project \= project\_factory(  
        tenant\_id=config.tenants\["company1"\]\["tenant\_id"\],  
        name=project\_name,  
    )  
    assert project\["status"\] \== "active"

    \# 2\. Check it appears in the web UI for the right company  
    login(page, config, tenant="company1", role="admin")  
    DashboardPage(page, config).open("/dashboard")

    card \= page.locator(".project-card", has\_text=project\_name)  
    expect(card).to\_be\_visible(timeout=config.tenants\["company1"\]\["timeout\_ms"\])

    \# 3\. Isolation at the API layer.  
    \# Ask for company1's project while acting as company2.  
    \# Expect a refusal, not an empty result.  
    response \= api\_client.get(  
        f"{config.api\_url}/projects/{project\['id'\]}",  
        headers={"X-Tenant-ID": config.tenants\["company2"\]\["tenant\_id"\]},  
    )  
    assert response.status\_code in (403, 404), (  
        f"Tenant isolation breach: company2 got {response.status\_code}"  
    )

    \# 4\. Isolation at the UI layer, in a separate browser session  
    \# so company1's login cookie does not carry over.  
    c2\_page \= new\_session(page, config, tenant="company2", role="admin")  
    DashboardPage(c2\_page, config).open("/dashboard")  
    expect(c2\_page.get\_by\_text(project\_name)).to\_have\_count(0)

    \# 5\. Mobile: layout only  
    with browserstack\_session(config, "ios\_safari") as mobile\_page:  
        login(mobile\_page, config, tenant="company1", role="admin")  
        DashboardPage(mobile\_page, config).open("/dashboard")

        mobile\_card \= mobile\_page.locator(".project-card", has\_text=project\_name)  
        expect(mobile\_card).to\_be\_visible(timeout=30000)

        \# The card must not run off the side of the screen  
        box \= mobile\_card.bounding\_box()  
        assert box\["width"\] \<= mobile\_page.viewport\_size\["width"\]

## **Test data**

Two rules.

**Every test creates its own data with a unique name.** Nothing depends on data that already exists, so tests can run in any order and in parallel without colliding. A random suffix on the project name is enough.

**Cleanup lives in the fixture, never at the end of the test.** A fixture's cleanup runs whether the test passes or fails. Cleanup written as the last line of a test gets skipped every time the test fails, which is exactly when you have created data and want it removed.

I would also log cleanup failures rather than raising them. If cleanup throws an error it replaces the real failure in the report, and you end up debugging the wrong problem.

## **Why the isolation checks are written that way**

**The API check expects 403 or 404, not an empty list.** A 200 response with an empty list is ambiguous. It could mean isolation worked, or it could mean a filter matched nothing for an unrelated reason. An explicit refusal is unambiguous. I accept both codes because either is a legitimate design choice, since 404 hides that the project exists and 403 admits it.

**The UI check counts occurrences rather than checking visibility.** Asking "is this hidden" would pass instantly on a page that simply has not loaded yet, which gives false confidence in exactly the situation the test exists to catch. This is the same trap as Issue 3 in Part 1, in a different shape.

**The UI check uses a separate browser session.** Reusing the same one would carry company1's login cookie into the company2 check, and the test would silently verify nothing.

## **BrowserStack**

Being honest about my level, I have not used BrowserStack directly. My understanding is that it is a set of real browsers and phones you connect to remotely, so the test code stays essentially the same and only the connection details change. You pass the device, OS version, and your credentials when connecting, plus a build name so a failed session can be found in their dashboard afterwards.

On cost, my assumption is that mobile runs nightly rather than on every commit, because sessions are billed and mobile bugs are usually layout rather than logic. I would want to know the parallel session limit on the plan before designing the pipeline, since that caps how fast the mobile suite can go.

## **Edge cases**

**Network failures.** You cannot make a real server fail on demand, so I would intercept the request in the browser and force a failure. Playwright can block or fake any request, which makes error states testable properly instead of hoping one occurs.

For genuinely flaky network issues in CI, I would allow a limited retry on the API connection only, not on whole tests. A dropped connection is infrastructure noise. A failed assertion is a real signal, and the two should be treated differently.

**Slow loading.** Handled by per tenant timeouts from config, plus a longer default for BrowserStack sessions, which have network delay to a real device on top of the page load.

**Mobile layout.** The width check catches content running off the side of the screen, which is the most common mobile bug. I would also want to check that buttons are reachable without horizontal scrolling and are large enough to tap, but I would need a design spec before asserting exact numbers.

**Partial failure.** If the API creates the project but the UI check fails, the project still exists. Because cleanup is in the fixture, it still gets removed.

## **Assumptions for Part 3**

**Authentication.** I assumed a token can be obtained from an auth endpoint and lasts for the whole run. If tokens are short lived, the API client needs to refresh them, and a token expiring mid run would look exactly like flakiness.

**Cleanup.** I assumed the delete endpoint exists and removes the record properly. If it only marks it as deleted, the data builds up over time and affects other tests.

**The tenant header.** I assumed the server checks `X-Tenant-ID` against the token. If the server ignores the header and works out the company from the token instead, my cross tenant check proves nothing, because the header would be decorative. This is worth confirming before trusting the test.

**Mobile platform.** I assumed the mobile experience is the website on a phone browser, not a separate app. A native app would need Appium and completely different selectors.

**Visibility.** I assumed a new project appears immediately with no approval step or sync delay. If there is a queue between creating and displaying, the UI check needs to wait for that instead.

## **With more time**

I would add a proper CI pipeline where the fast tests block merges and the slow, paid ones run nightly.

I would track how often each test fails over time, because without that you cannot tell a flaky test from one correctly catching a real bug.

I would add visual comparison on mobile, since that is where my checks are weakest right now. A width check catches content overflowing, but not a layout that is broken while still fitting.

p.s.

To be transparent with the team , i was unfamiliar with BrowserStack methodology and thought i would bring that up now rather than later. I am self aware of my capabilities and my knowledge hence i am keen on learning rather than trying to lie my way in to my role. I want to grasp and understand the case study as much as humanely possible. 

