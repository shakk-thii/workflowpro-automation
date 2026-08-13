# Setup and push

Run these in order from inside the `workflowpro-automation` folder.

## 1. Install

macOS or Linux:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

Windows PowerShell:

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

## 2. Run the suite

```
pytest
```

Expect around 17 tests to pass and 7 to be skipped. The skipped ones are
the WorkFlow Pro tests, which cannot run because the app is fictional.

This creates `reports/report.html`. Open it to check it looks right.

## 3. Push to GitHub

Create an empty repository at https://github.com/new named
`workflowpro-automation`. Do not add a README or .gitignore, the repo
already has both.

Then:

```
git init
git add -A
git commit -m "QA automation framework and case study"
git branch -M main
git remote add origin https://github.com/shakk-thii/workflowpro-automation.git
git push -u origin main
```

GitHub will ask for a password. Use a personal access token, not your
account password. Create one at Settings, Developer settings, Personal
access tokens, Tokens (classic), with the `repo` scope ticked.

## 4. Submit

Repository URL: https://github.com/shakk-thii/workflowpro-automation
