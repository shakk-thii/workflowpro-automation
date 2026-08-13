# Test Cases

P1 is critical path, P2 is high frequency, P3 is edge cases.

## Authentication

| ID | Case | Expected | Priority | Automated |
|---|---|---|---|---|
| TC-01 | Valid credentials | Product page loads with items | P1 | Yes |
| TC-02 | Wrong password | Error shown, stays on login | P1 | Yes |
| TC-03 | Unknown username | Error shown, stays on login | P1 | Yes |
| TC-04 | Empty username | "Username is required" | P2 | Yes |
| TC-05 | Empty password | "Password is required" | P2 | Yes |
| TC-06 | Locked account, correct password | Refused with lockout message | P1 | Yes |
| TC-07 | Logout | Returned to login, session ended | P1 | Yes |

## Product listing

| ID | Case | Expected | Priority | Automated |
|---|---|---|---|---|
| TC-08 | All products render | Six items shown | P2 | Yes |
| TC-09 | Sort price low to high | List reorders ascending | P3 | Yes |
| TC-10 | Sort name Z to A | List reorders reverse alphabetical | P3 | Yes |

## Cart

| ID | Case | Expected | Priority | Automated |
|---|---|---|---|---|
| TC-11 | Add item | Badge shows 1 | P2 | Yes |
| TC-12 | Added item is in cart | Cart contains the item | P2 | Yes |
| TC-13 | Remove item | Cart empty and badge gone | P2 | Yes |

## Checkout

| ID | Case | Expected | Priority | Automated |
|---|---|---|---|---|
| TC-14 | Complete purchase | Confirmation shown | P1 | Yes |
| TC-15 | Missing first name | "First Name is required" | P1 | Yes |
| TC-16 | Missing last name | "Last Name is required" | P1 | Yes |
| TC-17 | Missing postal code | "Postal Code is required" | P1 | Yes |

## WorkFlow Pro, design only

Cannot run, the application is fictional.

| ID | Case | Expected | Priority |
|---|---|---|---|
| WF-01 | Login without 2FA | Dashboard loads | P1 |
| WF-02 | Login with 2FA | Code screen, then dashboard | P1 |
| WF-03 | Tenant sees only own projects | Own data present, other tenant absent | P1 |
| WF-04 | Create project via API | 201 with project id | P1 |
| WF-05 | Cross tenant API access | 403 or 404, never the data | P1 |
| WF-06 | Employee cannot delete | Delete option not shown | P1 |
| WF-07 | Manager cannot delete | Delete option not shown | P1 |
| WF-08 | Mobile layout | No horizontal overflow | P2 |
