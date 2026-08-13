# Test data

Data is kept separate from test logic so a change to expected values
does not require editing a test.

`test_data.json` holds input values and expected messages for the login
and checkout cases. `../config/environments.yaml` holds user accounts
and URLs per environment.

Credentials here are the public demo accounts published by saucedemo.com.
Real credentials belong in environment variables and never in the
repository, since anything committed stays in version history
permanently.

For data created during a run, tests generate unique names using the
`unique_name` fixture in `conftest.py`, so parallel runs never collide.
