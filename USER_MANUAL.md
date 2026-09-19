# Trip Planner MVP v3 — User Manual

A complete guide to using the Trip Planner web application.

**Version 2** added **user accounts, secure login/registration, JWT authentication, and per-user trip ownership**. Every trip now belongs to a specific user; users can only see and modify their own itineraries.

**What's New in Version 3 — Trip Costs & Budget Management**

Version 3 introduces a full budget and expense subsystem so you can track the cost of every trip. Highlights:

- **Budget & Currency fields** on every trip — set a total budget in one of 7 supported currencies (USD, EUR, GBP, ILS, VND, THB, JPY)
- **Authoritative Budget Summary** with 4 live KPI tiles (Budget, Spent, Remaining, Over Budget) computed server-side using Decimal rounding to eliminate 0.1+0.2=0.30000000000000004 float drift
- **Over-budget detection** with a red badge that appears automatically when total expenses exceed the budget
- **6 expense categories**: Accommodation, Food, Transportation, Activities, Shopping, Other
- **Immutable business rules** enforced by both client and server (see Validation Rules): expense currency MUST match trip currency, expense date MUST fall within trip range, amount strictly > 0
- **3 updated seed trips** with realistic budgets and pre-populated expenses (Vietnam 2000 USD / 4 expenses, Tokyo 300,000 JPY / 5 expenses, Europe 5000 EUR / 6 expenses)
- **New stable `data-testid` attributes** on every Budget and Expense control for reliable automation testing
- **Transparent V2 → V3 field migration** — legacy V2 trips (missing budget/currency/expenses) are auto-filled with `budget=0.0`, `currency="USD"`, and `expenses=[]` on first read

---

## Getting Started

### Prerequisites

- **Python 3.10** or newer
- **pip** (Python package manager)
- A modern web browser (Chrome, Firefox, Edge, Safari)

### Installation

1. **From the project root**, create and activate a virtual environment (recommended):

   **Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   **Windows (Command Prompt):**
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate.bat
   ```

   **macOS / Linux:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies** (V2 adds bcrypt/passlib, JWT, and email validation packages):
   ```bash
   pip install -r backend/requirements.txt
   ```

### Running the Application

From the `backend` directory (with your virtual environment activated):

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Once the server starts, open your browser and visit:

- **Application (Login Page):** <http://localhost:8000/>
- **Interactive API Docs (Swagger UI):** <http://localhost:8000/docs>
- **ReDoc API Docs:** <http://localhost:8000/redoc>
- **Health Check:** <http://localhost:8000/api/health>

> The `--reload` flag automatically restarts the server when code files change. This is useful during development.

**First-Run Startup Behavior:**
- Two demo user accounts are created automatically (see [Seed Development Users](#seed-development-users))
- Three sample itineraries are written, pre-assigned to Alice and Bob (asymmetric ownership — see [Trip Ownership](#trip-ownership))
- If a legacy V1 `data/trips.json` exists (without `user_id`), it is transparently migrated so you won't lose data

### Stopping the Server

Press `Ctrl + C` in the terminal window where the server is running.

---

## User Accounts & Authentication (NEW in Version 2)

Version 2 introduces multi-user support. You must sign in to create, view, or modify any trip. A signed-out user only sees the Login page.

### Seed Development Users

For convenience during development and testing, two pre-configured accounts are always available. These credentials are also printed on the Login page as a demo hint.

| Name         | Email                 | Password        | Sample Trips Owned (after reset)                              | Budget (total)    | Currencies (trips)       | # Expenses (total) |
|--------------|-----------------------|-----------------|----------------------------------------------------------------|-------------------|--------------------------|--------------------|
| Alice Smith  | `alice@example.com`   | `Password123!`  | 2 trips — Vietnam Adventure + European Backpacking            | USD 2,000 + EUR 5,000 = USD 7,000 equiv | Vietnam: USD, Europe: EUR | 4 + 6 = **10** |
| Bob Johnson  | `bob@example.com`     | `Password123!`  | 1 trip — Tokyo Discovery                                      | JPY 300,000       | Tokyo: JPY               | **5** |

> **Tip:** Use Alice to test features that require multiple itineraries with different currencies, and Bob to test isolated single-trip budget scenarios in JPY.

### Registering a New Account

1. Click **Register** in the top-right of the header (or the "Register" link on the Login form).
2. The Register form appears with four fields:
   - **Full Name** (required, at least 1 character)
   - **Email** (required, must be a valid email address; each email can only be used once — duplicate returns "Email already exists")
   - **Password** (required, minimum 6 characters)
   - **Confirm Password** (required, must match the password exactly)
3. Click **Register**.

On success (HTTP 201), you are returned to the Login page and can sign in immediately with your new credentials.

### Signing In (Login)

1. On the landing page, the Login form is shown.
2. Enter:
   - **Email** — e.g., `alice@example.com`
   - **Password** — e.g., `Password123!`
3. Click **Sign In**.

On success:
- A JSON Web Token (JWT) and your user profile are stored in your browser's `localStorage`
- The header updates to show your full name and email next to the **Reset Data** and **Logout** buttons
- You are taken to the Trips List view showing **your** trips only

If the email or password is incorrect, the error message shown is always the generic text **"Invalid email or password."** — the system intentionally does not reveal whether an account exists for a given email, to prevent attackers from guessing which accounts are registered.

### Session Expiry and Re-Validation

- Your JWT token expires **24 hours** after login.
- On every page load the app calls `GET /api/auth/me` to verify that the token is still valid.
- If any API call returns HTTP 401 (invalid, expired, or missing token), the app clears your session, shows a "Session expired" toast, and returns you to the Login page.

### Signing Out (Logout)

Click the **Logout** button in the top-right header. This clears your tokens from `localStorage` and returns you to the Login page. Logout is a purely client-side action — no server call is needed.

---

## Application Overview

**Starting screen:** After login, the application consists of three main screens. If you are not logged in, only the Login / Register views are available.

1. **Trips List** — View all of **your** trips (you never see other users' trips)
2. **Create / Edit Trip** — Add or modify a trip (automatically assigned to you)
3. **Trip Details** — Manage a trip's itinerary (days and activities), but only if you are the owner

### Navigation (Logged In)

- Click the **Trip Planner** logo/title in the header at any time to return to the Trips List.
- Use the **Back to Trips** button on other screens to go back.
- Use the **Reset Data** button in the top-right to restore **all users + all trips** to the initial seed state (see [Resetting Data](#resetting-data)).
- Click **Logout** at any time to end your session.

### Navigation (Signed Out)

- Use the **Login** and **Register** buttons in the header to switch between the two views.

---

## Trip Ownership (NEW in Version 2)

Every trip in the system is owned by exactly one user. The ownership rule is enforced **server-side** and never trusts any identifier sent by the client — the owner is always derived from the JWT attached to the request.

- **Listing trips (`GET /api/trips`)** returns only trips whose `user_id` matches the authenticated caller.
- **Creating a trip (`POST /api/trips`)** sets `user_id` to your ID. Including a `user_id` in the request body has no effect — it's overwritten server-side.
- **Reading / Updating / Deleting a specific trip** (`GET / PUT / DELETE /api/trips/{trip_id}`):
  - If the trip **does not exist at all** → HTTP 404 Not Found
  - If the trip **exists but belongs to another user** → HTTP 403 Forbidden
  - If the trip **belongs to you** → 200/204 success

This same pattern applies recursively to days and activities — accessing a day or activity that lives under another user's trip always returns 403.

### Why Ownership Matters

Because Alice owns 2 trips and Bob owns 1 trip in the seed data, you can immediately verify that isolation is working correctly by signing in as Alice → count 2, sign in as Bob → count 1.

---

## Budget Management (NEW in Version 3)

Every trip now has a **Budget** section visible at the top of the Trip Details page, right below the Trip Header. Budget is **per trip** and always expressed in a single currency (the trip's currency).

> ⚠️ **Warning (Known Bug #24):** Changing the trip's currency after you have already recorded expenses is **discouraged**. Existing expense rows keep their original `currency` field stored, but the Budget Summary's `total_spent` will be re-summed using the **new trip currency symbol** against the **original expense numerals**, producing misleading KPIs. Recommended workflow: set the correct budget + currency **before** adding expenses, or delete all expenses first before switching currency.

### Budget Section UI (4 KPI Tiles + Progress Bar)

The Budget section displays 4 colored tiles and a progress bar, all re-fetched in real-time whenever you open or modify a trip:

| Tile / Element            | Meaning                                                                 | `data-testid` attribute        |
|---------------------------|-------------------------------------------------------------------------|--------------------------------|
| **Budget**                | The total trip budget you set (0 if unset).                            | `budget-amount`, `budget-currency` |
| **Spent**                 | Sum of all expenses recorded so far (server-side Decimal 2-dp sum).    | `budget-spent`                 |
| **Remaining**             | `Budget - Spent`. Green if ≥ 0, **red** if negative.                   | `budget-remaining`             |
| **Over Budget** badge     | Red pill badge that appears when `Spent > Budget`. Hidden otherwise.   | `budget-over-budget`           |
| **Progress bar**          | Fill % = `Spent / Budget`. Colors: green (<80%), amber (80–100%), red (>100%). If `Budget = 0` the bar shows 0% (see Known Bug #30). | *(rendered inside budget tiles container)* |
| **Edit Budget** button    | Opens the modal form to change budget amount and/or currency.          | `save-budget` (submit button)  |

### How to View or Edit the Budget

1. Navigate to any trip's **Trip Details** page.
2. Scroll down to the **Budget** section (between the Trip Header and Expenses table).
3. To edit: click **Edit Budget** → a modal opens with 2 fields:
   - **Budget Amount** (required, numeric, ≥ 0)
   - **Currency** (required dropdown, 7 options: USD / EUR / GBP / ILS / VND / THB / JPY)
4. Click **Save Changes**. The 4 KPI tiles and progress bar refresh instantly.

### Behavior When Budget = 0

- All expenses will show the trip as **Over Budget** immediately (since any positive amount > 0).
- The progress bar displays 0% (Known Bug #30 — division by zero guard returns 0 instead of 100%+).
- The Remaining tile shows a negative number (e.g., `−1,250.00`) in red text.

---

## Expenses (NEW in Version 3)

Expenses are the line items that make up your trip's actual spending. Each expense belongs to exactly one trip and is listed in a sortable table below the Budget section. Adding/editing/deleting expenses automatically re-triggers a Budget Summary recalculation.

### Supported Currencies & Categories

**7 supported currencies** (same enum for both trip currency and expenses — note the trip-currency lock rule below):

| Code | Symbol | Common Use                          |
|------|--------|-------------------------------------|
| USD  | $      | United States Dollar                |
| EUR  | €      | Eurozone                            |
| GBP  | £      | British Pound                       |
| ILS  | ₪      | Israeli New Shekel                  |
| VND  | ₫      | Vietnamese Dong                     |
| THB  | ฿      | Thai Baht                           |
| JPY  | ¥      | Japanese Yen                        |

**6 expense categories** (selectable dropdown when adding/editing):

| Category         | Typical Examples                                                        |
|------------------|-------------------------------------------------------------------------|
| Accommodation    | Hotels, hostels, Airbnb, homestays                                     |
| Food             | Restaurants, cafes, street food, groceries                             |
| Transportation   | Flights, trains, buses, taxis, car rentals, ferries                    |
| Activities       | Museum tickets, tours, events, entrance fees, shows                    |
| Shopping         | Souvenirs, clothing, electronics                                       |
| Other            | Anything not fitting the above (travel insurance, visa fees, tips, …)  |

### ⚠️ 3 Immutable Business Rules (you WILL hit 400 errors if you ignore these)

1. **Currency Match Lock:** An expense's `currency` **MUST equal its parent trip's currency**. In the UI the currency dropdown is **disabled** (locked to trip currency) when you add/edit an expense. If you bypass the UI and call the API directly with a mismatched currency, the server returns **HTTP 400 Expense currency must match trip currency**.
2. **Date in Trip Range:** An expense's `date` **MUST fall between the trip's start_date and end_date inclusive**. If the trip spans `2026-10-01 → 2026-10-10`, `2026-09-30` and `2026-10-11` are both rejected as **HTTP 400 Expense date must be within trip date range**. *(Known Bugs #27 and #28: editing an expense with an unchanged date can still fail if you later shrunk the trip range; the workaround is to edit the expense date first before saving.)*
3. **Amount Strictly Positive + 2-Decimal Rounding:** Every expense amount must be **strictly greater than 0** (`amount > 0`). `0.00` and negative amounts both return **HTTP 400 Expense amount must be greater than 0**. Sub-cent values like `0.001` pass all validators but are rounded to `0.00` at persistence (Known Bug #25), at which point the row becomes un-editable. Always use exactly 2 decimal digits.

### Expenses Table UI

The Expenses section shows:

- An **Add Expense** button (top-right, purple) — `data-testid="add-expense"`
- A responsive table with 5 columns:

| Column     | Content                                                                     |
|------------|-----------------------------------------------------------------------------|
| Date       | The expense date (YYYY-MM-DD)                                               |
| Category   | One of the 6 categories (with badge styling)                                |
| Description| Free text (min 1 char) — store receipt #s, vendor name, etc.                |
| Amount     | Formatted currency (e.g., `$1,250.00`)                                      |
| Actions    | Edit icon ✏️ and Delete icon 🗑️ for each row                               |

- Table wrapper `data-testid="expense-list"`
- Each row has action buttons: `edit-expense-btn-{id}` and `delete-expense-btn-{id}`

### How to Add an Expense

1. Open Trip Details → scroll to **Expenses** section.
2. Click **Add Expense** → modal opens with 5 fields:

| Field           | Type       | Required? | Constraints                                                                 | `data-testid`        |
|-----------------|------------|-----------|-----------------------------------------------------------------------------|----------------------|
| **Description** | Text       | ✅ Yes    | min 1 character                                                             | `expense-description`|
| **Category**    | Dropdown   | ✅ Yes    | 6 options (Accommodation / Food / Transportation / Activities / Shopping / Other) | `expense-category` |
| **Amount**      | Number     | ✅ Yes    | strictly > 0, 2 decimal digits recommended                                  | `expense-amount`     |
| **Currency**    | Dropdown   | ✅ (auto) | **DISABLED** — auto-locked to the trip's currency. You cannot change it here. | `expense-currency` |
| **Date**        | Date picker| ✅ Yes    | must be between trip start_date and end_date inclusive                      | `expense-date`       |

3. Click **Add Expense** (submit button `data-testid="save-expense"`).
4. The Expenses table re-renders and the Budget KPI tiles update to include the new amount.

### How to Edit an Expense

1. Click the ✏️ **Edit** icon on the row you want to modify.
2. The same 5-field modal opens with current values pre-filled.
3. Change any field (except Currency, which remains locked) and click **Save Changes**.

> **Known Bug #27:** The frontend sends all 5 fields in the PUT payload even when you only changed Description. This means the date validation (Rule #2) runs against the pre-filled date **as if you just entered it**. If you previously shrunk the trip's end_date to be earlier than this expense's date, the edit will fail even though you only wanted to fix a typo in the description. Workaround: update the expense date to a valid in-range date as part of the same edit.

### How to Delete an Expense

1. Click the 🗑️ **Delete** icon on the row.
2. A confirmation modal asks "Are you sure you want to delete this expense?".
3. Click **Confirm Delete**. The row disappears and the Budget KPI tiles refresh (Spent goes down, Remaining goes up, Over Budget badge may hide).

### V3 Data-testid Reference for Automation Testers

All new V3 controls expose stable `data-testid` attributes. Use these selectors instead of brittle XPath or CSS-class queries when writing Playwright / Selenium / Puppeteer tests:

| Area          | `data-testid`                  | What it selects                                                |
|---------------|--------------------------------|----------------------------------------------------------------|
| **Budget**    | `budget-amount`                | Budget KPI tile — numeric value element                        |
| **Budget**    | `budget-currency`              | Currency label inside Budget tile (e.g., "USD", "EUR")         |
| **Budget**    | `budget-spent`                 | Spent KPI tile value                                           |
| **Budget**    | `budget-remaining`             | Remaining KPI tile value                                       |
| **Budget**    | `budget-over-budget`           | Over Budget red pill badge (only present when over budget)     |
| **Budget**    | `save-budget`                  | Save/Submit button inside the Edit Budget modal                |
| **Expenses**  | `add-expense`                  | Add Expense button (top of Expenses section)                   |
| **Expenses**  | `expense-list`                 | Wrapper `<div>` / `<table>` containing all expense rows        |
| **Expenses**  | `save-expense`                 | Save/Submit button inside Add/Edit Expense modal               |
| **Expenses**  | `expense-description`          | Description input field in add/edit expense modal              |
| **Expenses**  | `expense-category`             | Category `<select>` in add/edit expense modal                  |
| **Expenses**  | `expense-amount`               | Amount `<input>` in add/edit expense modal                     |
| **Expenses**  | `expense-currency`             | Currency `<select>` (disabled) in add/edit expense modal       |
| **Expenses**  | `expense-date`                 | Date `<input>` in add/edit expense modal                       |
| **Expenses**  | `edit-expense-btn-{expenseId}` | Per-row Edit icon button (replace `{expenseId}` with real ID)  |
| **Expenses**  | `delete-expense-btn-{expenseId}` | Per-row Delete icon button (replace `{expenseId}` with real ID) |

> To obtain real expense IDs for automation scripts, after login call `GET /api/trips/{tripId}/expenses` — the response is a JSON array where each object has an `id` field (UUID).

---

## Trips List

The Trips List is the first screen you see after login. It displays all your trips as cards in a responsive grid. Trips belonging to other users are never shown.

Each trip card shows:
- **Destination** (on the colored banner at top)
- **Trip Name**
- **Date Range** (Start date — End date)
- **Duration** (number of days)
- **Itinerary Summary** (number of days added + number of activities planned)

### Creating a New Trip

1. Click the **Create Trip** button (purple, top-right).
2. Fill in the form fields:
   - **Trip Name** (required) — e.g., "Summer Europe Tour"
   - **Destination** (required) — e.g., "France, Italy, Spain"
   - **Start Date** (required) — First day of the trip
   - **End Date** (required) — Last day of the trip (must be on or after start date)
3. Click **Create Trip**.

The new trip is automatically assigned to your account (no client choice about ownership). You will be taken to the Trip Details page to build the itinerary.

### Viewing Trip Details

- Click **View Details** on any trip card to open the Trip Details page. If someone shares a link to a trip you don't own, you'll get a 403 error.

### Editing a Trip

- Click the **pencil icon** (Edit) on any trip card.
  OR
- From the Trip Details page, click the **Edit Trip** button.

Make changes in the form and click **Save Changes**.

### Deleting a Trip

- Click the **trash icon** (Delete) on any trip card.
  OR
- From the Trip Details page, click the **Delete** button.
- Confirm the deletion when prompted.

> ⚠️ **Warning:** Deleting a trip permanently removes it and all its days and activities. This action cannot be undone. Only the trip owner can delete their trips — other users get a 403.

---

## Trip Details

The Trip Details page lets you build and manage the full itinerary for a trip. It is only accessible to the trip's owner (any other user receives HTTP 403 Forbidden).

### Trip Header

At the top, you will find:
- Trip **destination** and **name**
- **Date range**, **duration**, and **itinerary summary** (total days + activities)
- **Edit Trip** and **Delete** buttons

### Itinerary Section

The Itinerary section lists each day of your trip in chronological order.

### Adding a Day

1. Click the **Add Day** button (purple, top-right of the Itinerary section).
2. In the popup form:
   - **Date** (required) — The date for this day. Should fall within the trip's date range.
   - **Title** (optional) — A short title for the day, e.g., "Arrival in Paris", "Beach Day", "Travel to Rome".
3. Click **Add Day**.

> **Tip:** You can add days on any date (including dates outside the trip range — the app does not enforce this currently, but it's good practice to keep days inside the trip's start/end dates).

### Editing a Day

1. Click the **pencil icon** (Edit day) in the top-right corner of the day card.
2. Update the date and/or title.
3. Click **Save Changes**.

### Deleting a Day

1. Click the **trash icon** (Delete day) in the top-right corner of the day card.
2. Confirm the deletion when prompted.

> ⚠️ **Warning:** Deleting a day also deletes all activities assigned to that day.

---

## Activities

Each day can have multiple activities (attractions, events, transportation, meals, etc.). Adding/editing/deleting activities is only allowed if you own the parent trip.

### Adding an Activity

1. On any day card, click the **Add Activity** button (outlined, dashed border) at the bottom of the card.
2. In the popup form:
   - **Activity Name** (required) — e.g., "Visit the Eiffel Tower"
   - **Location** (optional) — e.g., "Champ de Mars, Paris"
   - **Description** (optional) — Any notes, such as booking confirmations, tips, times, etc.
3. Click **Add Activity**.

### Editing an Activity

1. Click the **pencil icon** to the right of the activity.
2. Update any fields.
3. Click **Save Changes**.

### Deleting an Activity

1. Click the **trash icon** to the right of the activity.
2. Confirm the deletion when prompted.

---

## Resetting Data

At any time, any **authenticated** user can restore the entire application to its deterministic seed state. Resetting affects **all users and all trips** globally, not just the current user's data.

> **NEW in V2:** Reset is no longer a public unauthenticated endpoint — you must be signed in to use it.

### Option 1: Via the UI

1. Sign in as any user.
2. Click the **Reset Data** button in the top-right header (only visible when signed in).
3. Confirm the reset when prompted in the modal dialog.

After reset, you will still be signed in with your existing session, but the following state is restored globally:
- Two user accounts: Alice (2 trips) and Bob (1 trip). Your custom-registered accounts are removed.
- Three sample itineraries with original full contents and ownership assignments
- Any custom trips, days, and activities you created are wiped

### Option 2: Via the API

Using `curl`, Postman, or any HTTP client. Since reset requires authentication, you must first obtain a JWT:

```bash
# 1. Login to get a token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"Password123!"}' | jq -r .access_token)

# 2. Call reset with the token in the Authorization header
curl -X POST http://localhost:8000/api/system/reset \
  -H "Authorization: Bearer $TOKEN"
```

### Sample Trips + Ownership After Reset

After reset, the following trips are available (ownership is intentionally asymmetric). All 3 trips carry realistic V3 budgets and pre-seeded expenses:

| # | Trip Name              | Destination | Dates                | Owner   | Budget   | Currency | # Expenses | Representative Seed Expense                          | Notable Itinerary                                                                         |
|---|------------------------|-------------|----------------------|---------|----------|----------|------------|-------------------------------------------------------|-------------------------------------------------------------------------------------------|
| 1 | Vietnam Adventure      | Vietnam     | Oct 1–10, 2026       | Alice   | 2,000    | USD      | 4          | Hotel Stays — $500 Accommodation (Oct 1)              | Day 1: Arrival in Hanoi; Day 2: Ha Long Bay Cruise; Day 3: Hanoi → Da Nang flight, ...   |
| 2 | Tokyo Discovery        | Japan       | Nov 15–22, 2026      | Bob     | 300,000  | JPY      | 5          | Ryokan Accommodation — ¥80,000 Accommodation (Nov 15) | Day 1: Shibuya Crossing; Day 2: Senso-ji Temple / Asakusa, ...                            |
| 3 | European Backpacking   | Europe      | May 1–14, 2027       | Alice   | 5,000    | EUR      | 6          | Paris Hotel — €700 Accommodation (May 1)              | Day 1–2: Paris; seed includes transport + meals across 4 countries (ready for you to extend!) |

---

## Data Storage

All data is saved as two human-readable JSON files in the project-root `data/` directory. **Files are created automatically — you never need to create them manually.**

```
data/
├── trips.json     # All trips, days, activities, user_id ownership, budget, currency, embedded expenses[]
└── users.json     # User accounts (email, full_name, + bcrypt password_hash)
```

### Trip JSON Model (V3)

A representative trip record. **Expenses are EMBEDDED inside each trip object** as a nested `expenses` array — there is no separate `expenses.json` file.

```json
{
  "id": "trip-vietnam-uuid",
  "user_id": "user-alice-uuid",
  "name": "Vietnam Adventure",
  "destination": "Vietnam",
  "start_date": "2026-10-01",
  "end_date": "2026-10-10",
  "budget": 2000.0,
  "currency": "USD",
  "days": [
    {
      "id": "day-1-uuid",
      "date": "2026-10-01",
      "title": "Arrival in Hanoi",
      "activities": [
        { "id": "act-1", "name": "Check into hotel", "location": "Hanoi Old Quarter", "description": "" }
      ]
    }
  ],
  "expenses": [
    {
      "id": "exp-1-uuid",
      "description": "Hotel Stays",
      "category": "Accommodation",
      "amount": 500.00,
      "currency": "USD",
      "date": "2026-10-01"
    },
    {
      "id": "exp-2-uuid",
      "description": "Street Food Tour",
      "category": "Food",
      "amount": 45.50,
      "currency": "USD",
      "date": "2026-10-02"
    }
  ]
}
```

### User Data Security Note

**Passwords are NEVER stored in plaintext.** The `users.json` file contains only a `password_hash` field using the bcrypt algorithm (you'll see strings starting with `$2b$…`). Neither the API nor any UI response ever returns or leaks the password hash.

You can verify this by opening `data/users.json` after creating a user — the literal string you typed as a password will not appear anywhere.

### Backing Up Your Data

To back up everything (trips + user accounts), copy the entire `data/` folder to a safe location:

```bash
# Windows (PowerShell)
Copy-Item -Recurse data data-backup-$(Get-Date -Format yyyyMMdd)

# macOS / Linux
cp -r data data-backup-$(date +%Y%m%d)
```

To restore, copy the backup files back (while the server is **not** running).

### Moving Data Between Installs

Both JSON files are fully portable across machines and operating systems as long as both Trip Planner installs are the same major version. Transparent in-place migration is applied automatically on first read.

**Migration notes (automatic, no manual editing required):**

- **V1 → V2:** If you copy a legacy V1 `trips.json` (which lacks `user_id` fields) into a V2+ project's `data/` folder, every trip is assigned to Alice by default (with seed trip IDs mapped per the ownership table), and the file is written back with `user_id` injected.
- **V2 → V3 (NEW):** If you copy a V2 `trips.json` (which lacks `budget`, `currency`, and `expenses` fields) into a V3 project, the app automatically fills in `budget: 0.0`, `currency: "USD"`, and `expenses: []` on every trip, then writes the file back. No data loss; you can then set realistic budgets and add expenses via the UI.

---

## Validation Rules

The application enforces the following rules. Validation is performed in both the browser (client-side, for UX) and on the server (server-side, which always takes precedence). Budget & Expense rules are enforced **3-deep** (Pydantic schema → service layer → Decimal rounding at persistence boundary).

### User Account Rules (NEW in V2)
- **Full Name:** Cannot be empty
- **Email:** Must be a valid RFC-compliant email address; must be globally unique across all users (duplicate returns 409 Conflict)
- **Password:** Minimum 6 characters
- **Password Confirmation:** Must match the password exactly (checked both client-side and server-side)
- **Login:** Both a wrong password AND a non-existent email return the **same generic error message** to avoid exposing whether an account exists

### Trips
- **Trip Name:** Cannot be empty
- **Destination:** Cannot be empty
- **Start Date:** Required
- **End Date:** Required, and cannot be earlier than Start Date
- **Budget:** Optional at create (defaults to `0.0`); when provided must be ≥ 0
- **Currency:** Optional at create (defaults to `"USD"`); when provided must be one of `USD | EUR | GBP | ILS | VND | THB | JPY`

### Days
- **Date:** Required

### Activities
- **Activity Name:** Cannot be empty

### Budget & Expense Rules (NEW in V3)

#### Category & Currency Enums
- **Expense Category:** MUST be one of `Accommodation | Food | Transportation | Activities | Shopping | Other` (server uses Pydantic `Literal` — any other value returns **HTTP 422 Validation Error**)
- **Currency (trip & expense):** MUST be one of `USD | EUR | GBP | ILS | VND | THB | JPY`
- **Currency Match (CRITICAL invariant):** Every expense's `currency` MUST exactly equal its parent trip's `currency`. Server returns **HTTP 400 Expense currency must match trip currency** if violated. The UI locks the currency dropdown to trip currency so this normally only happens via raw API calls or Bug #24 (editing trip currency after expenses exist).

#### Monetary Amounts & Decimal Rounding
- **Budget amount:** Must be ≥ 0 (zero is allowed — see "Behavior When Budget = 0" above)
- **Expense amount:** Must be **strictly > 0** (`Field(gt=0)` at schema; additional `if <=0: raise ExpenseValidationError` at service layer). `0.00` and negatives return **HTTP 400 Expense amount must be greater than 0**.
- **Decimal 2-dp rounding at persistence:** All monetary values pass through `Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)` right before JSON write. This avoids the classic `0.1 + 0.2 = 0.30000000000000004` float drift — the Budget Summary KPI `total_spent` will always be an exact 2-decimal sum. *(Known Bug #25: sub-cent amounts like 0.001 pass the amount>0 checks but round down to 0.00, creating an un-editable stuck row.)*

#### Date Range Rule (Expenses)
- **Expense date MUST fall within trip date range:** `trip.start_date ≤ expense.date ≤ trip.end_date` inclusive. Out-of-range dates return **HTTP 400 Expense date must be within trip date range**.
  - On **Create Expense (`POST`):** Rule always runs.
  - On **Update Expense (`PUT`):** Rule only runs if `expense_update.date` is **not None** (PATCH-style skip).
  - *(Known Bug #27 + #28): The frontend sends all 5 fields (including the pre-filled date) in every PUT, even when only description changed. Combined with the ability to shrink the trip's end_date via Edit Trip, this means a legitimate "fix a typo" edit can be rejected because the originally-valid date is now out of range. Workaround: re-select the date field (or change it to a valid in-range value) as part of the same edit.*

#### Authorization & Ownership (Budget & Expense endpoints)
- Budget & Expense endpoints inherit the same per-trip ownership as Days/Activities:
  - Accessing a budget or expense under a non-existent trip → **HTTP 404**
  - Accessing a budget or expense under another user's trip → **HTTP 403**
- No anonymous access: every budget/expense endpoint Depends on `get_current_user`; missing/expired JWT → **HTTP 401**

---

## Troubleshooting

### The server won't start

**Check Python version:**
```bash
python --version
```
You need Python 3.10 or newer.

**Check if port 8000 is already in use:**
Try a different port:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```
Then visit `http://localhost:8080/`.

**Reinstall dependencies (bcrypt/passlib/JWT packages may be missing):**
```bash
pip install --force-reinstall -r backend/requirements.txt
```

### The Login page shows but I can't sign in (wrong password error even with correct credentials)

- Confirm you are using a valid account: try the seed users `alice@example.com` / `Password123!` or `bob@example.com` / `Password123!`
- If you used a newly registered account and still can't log in, verify the password you entered on registration (the app performs case-sensitive comparison)
- Perform a [Reset](#resetting-data) via API using the curl sample above to ensure seed accounts exist
- Check the server terminal for startup errors — if `ensure_seed_users` failed (e.g., disk full or `data/` not writable), user accounts may not have been created

### "Session expired. Please log in again." toast appears

This happens when:
1. Your token has expired (24 hours after login — normal expected behavior)
2. The server was restarted and data was cleared (token still references a user that no longer exists in `data/users.json`)
3. You manually deleted `localStorage` items while the app was open

Just sign in again to get a new token.

### The website shows a blank page / errors

1. Open the browser's **Developer Tools** (F12) and check the **Console** tab for errors.
2. Check the terminal where the server is running for any error messages (common ones: ImportError for `email_validator` or `bcrypt` — re-run `pip install -r backend/requirements.txt`).
3. Ensure you've completed the Installation steps.
4. Check the **Network** tab in DevTools: requests should carry an `Authorization: Bearer …` header after login; 401/403 responses should have a JSON `{"detail": …}` body explaining the reason.

### Trips aren't saving / user accounts aren't persisting

- Check that the `data/` folder exists in the **project root** (not inside `backend/`) and is writable.
- Check the server terminal for file permission errors.
- If a JSON file was manually edited, ensure it's valid JSON. (You can use an online JSON linter.)
- **WARNING:** If you are using an editor/IDE formatter that reformats JSON on save, disable auto-format for the `data/` folder — the app writes JSON without whitespace; rewriting it while the server runs can produce race conditions.

### I'm getting 403 Forbidden on a trip I should own

Double-check that you are signed in as the right user (look at the header display). Remember:
- Alice owns trips #1 (Vietnam) and #3 (European Backpacking)
- Bob owns trip #2 (Tokyo) only

If you registered a custom account, only the trips you created with that account will be accessible.

### Date inputs don't work on my browser

Ensure you are using a modern, updated browser. Date inputs are standard HTML5 features supported by all recent browsers.

### Register says "Email already exists" but I don't remember creating that user

Two possibilities:
1. Another user or a test script registered the email (since emails are globally unique)
2. The seed `alice@example.com` / `bob@example.com` emails are always present after any reset — use a different email for custom accounts

### Budget KPI tiles show the wrong currency symbol after I edited trip currency (Known Bug #24)

**Symptom:** You set a trip to USD, added $500 in expenses, then used Edit Budget to switch currency to EUR. Now the "Spent" tile says **€500.00** even though the actual expenses are still stored as `currency: "USD"`.

**Root cause:** Known Bug #24. The Budget Summary sums expense.amount numerals and then formats the sum with the **trip's current currency**, ignoring each expense row's own stored currency code.

**Workaround (recommended workflow):**
1. Set budget + currency **once, before adding any expenses**.
2. If you really need to change currency with existing expenses, either:
   a. **Delete all expenses first** → change currency → re-enter them in the new currency, OR
   b. Accept the mixed state (the raw JSON in `data/trips.json` still contains each expense's original currency so you can manually audit it later).

### Editing an expense errors with "date out of range" even though I only changed the description (Known Bugs #27 + #28)

**Symptom:** You added an expense with date `2026-10-09` when trip end_date was `2026-10-10`. Later you shrink the trip end_date to `2026-10-05`. Now you try to edit only the expense's description text (because there's a typo) → you get HTTP 400 "date out of range".

**Root cause:** Known Bug #27 (frontend sends ALL 5 fields in PUT, not just the changed ones) + #28 (Edit Trip allows shrinking the range with no revalidation of existing expenses).

**Workaround:** When editing the expense, **re-select the date field** to a date that is currently within the (now-shrunk) trip range, make your description change, then Save. Alternatively, Reset Data and don't shrink trip date ranges after adding expenses.

### Sub-cent expense amounts get accepted by the frontend, save as $0.00, then can never be edited again (Known Bug #25)

**Symptom:** You typed `0.001` in the amount field. The form accepted it, the row appeared, but the amount shows `$0.00`. When you try to edit it to fix the typo, the Save button always fails with "amount must be > 0".

**Root cause:** Known Bug #25. Amount validators check `> 0` (0.001 passes all 3 layers: Pydantic `Field(gt=0)`, service `if <=0: raise`, and rounding). Only at persistence does `Decimal("0.001").quantize(Decimal("0.01"))` round it to `Decimal("0.00")`. Then ExpenseUpdate.amount uses `Field(None, gt=0)` so `0.00` fails validation on every subsequent PUT.

**Workaround:** Delete the stuck row and re-add with a proper 2-decimal amount (`0.01` minimum). Never type sub-cent amounts.

### Whitespace-only expense rows appearing (Known Bug #29)

**Symptom:** An expense shows up with an empty description cell. You're certain you never typed an empty string.

**Root cause:** Known Bug #29. The backend only validates `description: Optional[str] = Field(None, min_length=1)` — but `min_length=1` counts spaces. Strings like `"   "` (3 spaces) pass with length 3. The frontend `.trim()`s the description before display so it *looks* empty even though the raw stored value is spaces.

**Workaround:** Type actual non-space characters for descriptions; when testing, don't submit spaces-only. To fix an existing row, edit the description.

### Progress bar shows 0% but I'm clearly Over Budget (Known Bug #30)

**Symptom:** Budget = `0.00` (default or never set), you have $1,250 in expenses, Over Budget red badge is showing correctly, Remaining = `−$1,250.00` red — but the progress bar fill is 0%.

**Root cause:** Known Bug #30. The frontend progress-percent formula is `Math.round((spent / budget) * 100)`. To avoid `Infinity` when `budget === 0`, the code has a guard `if (!budget) return 0` — which returns 0% instead of 100%+.

**Workaround:** Give the trip a non-zero budget (even $0.01). The bar will then show an accurate (likely massively over-100%) red fill.

### Wrong thousands-separator or decimal-point formatting in progress bar / KPI tiles for my locale (Known Bug #38)

**Symptom:** You are in a locale where decimals use comma (e.g., Germany `1.250,00 €`) but the app shows everything as `$1,250.00` (US format) regardless of browser language.

**Root cause:** Known Bug #38. The `formatCurrency()` helper hard-codes `Intl.NumberFormat('en-US', ...)` — it never reads `navigator.language`.

**Workaround:** Accept en-US formatting, or for automation comparisons, always compare the raw numeric values from the API instead of the on-screen formatted strings.

### Two-tab edit produces "currency mismatch" even though the dropdown is disabled (Known Bug #36)

**Symptom:** Open Alice's Vietnam trip in Tab A and Tab B simultaneously. In Tab A: Edit Budget → switch currency to EUR → Save (success). In Tab B (still showing old currency USD in the header): click Add Expense → the Currency dropdown correctly shows USD and is disabled → Save → 400 "Expense currency must match trip currency".

**Root cause:** Known Bug #36. Tab B's closure-captured `trip.currency` was snapshotted when Trip Details first rendered. Tab A changing it server-side never invalidated Tab B's in-memory trip object, so the form pre-fills and submits `currency: "USD"` against a trip that is now `"EUR"` — hence currency mismatch.

**Workaround:** After editing a trip's budget/currency in one tab, **refresh the other tabs** before attempting expense CRUD. In automation scripts, always re-fetch `GET /api/trips/{id}` before calling POST /expenses if another process may have touched the trip.

### Progress bar / totals don't add up when an expense category is filtered or I'm looking at a partial view (Known Bug #39)

**Symptom:** The "Spent" tile = $1,250 but when you manually add the visible rows you only count $800.

**Root cause:** Known Bug #39 — category totals row is not yet displayed, and if you filtered the UI (e.g., scrolled such that some rows are hidden / or you have a client-side filter in a future build), the KPI tiles always reflect the **full server-side sum of ALL expenses**, not a partial client-side view.

**Workaround:** KPI tiles are always the authoritative source. If you need per-category breakdowns, call `GET /api/trips/{id}/expenses` and sum by `.category` in your own client/script, or wait for a future release that adds category subtotals.

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Submit a form (while typing in a field) | `Enter` |
| Close a modal/popup | Click outside modal or press `Esc` |

---

## Tips for Effective Trip Planning

1. **Plan your dates first** — Create the trip with accurate start/end dates, then add days in order.
2. **Give days meaningful titles** — Instead of "Day 1", use "Arrival in Bangkok" to make scanning easier.
3. **Add locations to activities** — Future versions will use these for maps and budget features.
4. **Use descriptions for details** — Store booking numbers, opening hours, and tips there.
5. **Reset if something goes wrong** — The Reset Data button produces a globally deterministic state: Alice=2 trips, Bob=1 trip, freshly-hashed bcrypt passwords for both.
6. **Use Bob for isolation testing** — Bob's single Tokyo trip is a great control case for verifying 403 cross-user behavior (Alice can't see/edit it, and Bob can't see Alice's two trips).
7. **Set Budget + Currency FIRST before adding expenses** — Because of Known Bug #24 (currency mismatch KPI drift), always configure the trip's budget and currency via Edit Budget **before** you begin adding expense rows. If you later change currency with expenses already recorded, delete the expenses first or accept the mixed state.
8. **Use the 6 expense categories deliberately** —
   - `Accommodation` = lodging (hotels, hostels, Airbnb, homestays)
   - `Food` = meals, cafes, street food, groceries
   - `Transportation` = flights, trains, buses, taxis, ferries, car rentals, fuel
   - `Activities` = tickets, tours, shows, entry fees
   - `Shopping` = souvenirs, clothing, electronics
   - `Other` = travel insurance, visa fees, tips, miscellaneous
   
   Consistent categorization makes it easier to add up per-category spending in the future (see Known Bug #39 — per-category totals are not yet displayed in the UI but are trivially computable from the API response).
9. **Save receipts in the Description field** — The description field is the ideal place to store a receipt number ("Receipt #A1B2C3"), vendor name ("Blue Lagoon Seafood"), or even a short note like "Split 3 ways — my share $22.50". Future export features will rely on this text.
10. **Use Alice's Vietnam trip + Reset Data for repeatable automation fixtures** — After a reset, Alice's Vietnam Adventure is always in a **$1,250 spent / $2,000 budget = 62.5% spent, NOT over budget** state (progress bar should be amber/green, Remaining = $750, Over Budget badge hidden). This is an excellent deterministic state for verifying that your Playwright/Selenium selectors (`budget-spent`, `budget-remaining`, progress bar color threshold, over-budget badge visibility) work correctly before you test custom scenarios.
11. **Use Bob's Tokyo trip for isolated single-currency JPY testing** — Bob has exactly one trip (Tokyo, ¥300,000, JPY, 5 expenses). If you're testing Yen-specific formatting or budget-over-budget thresholds in a currency where 1 unit has no cents (JPY is a zero-decimal currency in real life but our app still uses 2 decimals for consistency), Bob's Tokyo trip is the cleanest isolated fixture (no risk of accidentally asserting against Alice's USD/EUR trips).

---

## Technical Notes (Advanced Users)

### API Usage & Authentication

All UI actions are backed by a fully-documented REST API. You can explore it at:

- **Swagger UI (interactive):** <http://localhost:8000/docs>
- **OpenAPI JSON schema:** <http://localhost:8000/openapi.json>

**Important — JWT Requirement:** Every trip/day/activity endpoint and the reset endpoint requires the caller to present a valid JWT in the `Authorization` header as `Bearer <token>`. Unauthenticated calls return HTTP 401.

You can use the Swagger UI "Authorize" button (🔒) and enter:
- **Username:** `alice@example.com` (an email address — the Swagger form uses "username" for OAuth2 compatibility)
- **Password:** `Password123!`

After authorizing, the Swagger UI will automatically attach the token to every "Try it out" request.

### Example: Listing Your Trips via API

```bash
# Get a token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@example.com","password":"Password123!"}' | jq -r .access_token)

# List Bob's trips (should return exactly 1 — Tokyo Discovery)
curl -s http://localhost:8000/api/trips \
  -H "Authorization: Bearer $TOKEN" | jq '.[].name'
```

### Example: Creating a Trip via API

```bash
TOKEN=... # use your JWT
curl -X POST http://localhost:8000/api/trips \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Weekend in Lisbon",
    "destination": "Portugal",
    "start_date": "2027-03-05",
    "end_date": "2027-03-07"
  }'
```

The created trip will have `user_id` automatically set to your user ID — including a `user_id` field in the request body has **no** effect (server always uses JWT identity).

---

## Getting Help

For technical issues, refer to:
1. This user manual
2. The project's `README.md` for architecture and setup details
3. The Swagger API docs at `/docs` for API-specific help
4. `KNOWN_BUGS.md` for a list of confirmed issues, especially if you hit unexpected behaviour

---

*Version 3.0.0 — Trip Planner MVP with Budget Management & JWT Authentication*
