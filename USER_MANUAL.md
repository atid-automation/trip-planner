# Trip Planner MVP v6 — User Manual

A complete guide to using the Trip Planner web application.

- **Version 2** added **user accounts, secure login/registration, JWT authentication, and per-user trip ownership**. Every trip belongs to a specific user; users can only see and modify their own itineraries.
- **Version 3** added **trip costs, currency support, budget management, and automated over-budget detection**.
- **Version 4** added a **full Travel Journal CRUD subsystem** with dated narrative entries, newest-first sorting, and ownership enforcement.
- **Version 5** added a **responsive mobile-friendly interface** with mobile navigation and viewport adaptations.
- **Version 6** migrates the persistence layer from **JSON files to an ACID-compliant relational SQLite database (`data/app.db`)**. Relational tables with foreign keys and cascade deletions are introduced while preserving 100% of existing REST API endpoints, business logic, authorization rules, and frontend behavior.

**What's New in Version 6 — SQLite Relational Database Migration**

Version 6 transitions the application from flat JSON file storage to a relational SQLite database. Highlights:

- **Relational SQLite Persistence (`data/app.db`)** — Replaced `data/trips.json` and `data/users.json` with 6 normalized relational tables: `users`, `trips`, `trip_days`, `activities`, `expenses`, and `journal_entries`
- **Database Integrity & Foreign Key Enforcement** — SQLite foreign key constraints are enforced on every database connection (`PRAGMA foreign_keys = ON;`). Parent-child relationships feature `ON DELETE CASCADE` so deleting a trip automatically removes all associated days, activities, expenses, and journal entries with zero orphan records
- **Zero API or UI Breaking Changes** — 100% compatibility with existing automation test suites and user workflows. All URLs, response formats, validation rules, and `data-testid` attributes remain identical
- **Automated Migration Tool (`migrate_to_sqlite.py`)** — Run `python migrate_to_sqlite.py` to seamlessly migrate existing Version 5 JSON records into SQLite while preserving all IDs and relational associations
- **Database Initialization & Reset Tooling (`init_db.py`)** — Run `python init_db.py` to set up tables and seed data, or `python init_db.py --reset` to restore a clean deterministic state
- **Direct SQL Inspection for QA** — Predictable, standard table and column names (`users.id`, `trips.user_id`, `expenses.trip_id`, etc.) allow students and test automation engineers to write SQL inspection queries directly against `data/app.db`

**What's New in Version 4 — Travel Journal CRUD**

Version 4 introduces a full Travel Journal so you can record narrative entries for a trip alongside budget and expenses. Highlights:

- **Journal entries embedded per trip** — every trip has a `journal_entries[]` array; entries are scoped to trip ownership and cascade-deleted with the trip
- **Full CRUD via both UI and REST API** — Add, View, Edit, and Delete journal entries with a responsive card grid UI and 5 dedicated endpoints (`GET/POST /api/trips/{id}/journal`, `GET/PUT/DELETE /api/trips/{id}/journal/{entry_id}`)
- **Immutable business rules** enforced 3-deep (Pydantic schema → service → frontend): title 1–100 chars, content 1–5000 chars, date MUST fall within trip start/end inclusive
- **Server-authoritative newest-first sort order** — journal entries always returned sorted by `date DESC, created_at DESC`; frontend defensively re-sorts again on receive for deterministic display
- **3 updated seed trips with realistic journal data** — Vietnam (3 entries: Arrival Hanoi 10-01, Ha Long Bay 10-02, Da Nang Beach 10-04 sorted newest-first), Europe (3 entries: Paris 05-02, Amsterdam 05-07, Rome 05-12), Tokyo intentionally has 0 entries for empty-state automation fixtures
- **New stable `data-testid` attributes** (`journal-section`, `add-journal-entry`, per-card action attributes, journal modal form fields, `journal-view-edit-btn`) for reliable Playwright/Selenium automation
- **Transparent V3 → V4 field migration** — legacy V3 trips lacking a `journal_entries` key automatically receive `journal_entries: []` on first read and the file is written back (existing trips become V4-ready with zero manual JSON editing)
- **Automation-friendly empty-state & populated fixtures** — Bob's Tokyo trip has exactly **0** journal entries (empty card grid with "No journal entries yet" placeholder), Alice's Vietnam trip has exactly **3** entries sorted oldest-first on disk but rendered newest-first in UI (10-04 → 10-02 → 10-01), Alice's Europe trip has exactly **3** more entries for cross-trip journal assertions

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
- Legacy V3 trips (lacking `journal_entries` key) automatically get an empty `journal_entries: []` array injected on first read via V3→V4 migration

### Stopping the Server

Press `Ctrl + C` in the terminal window where the server is running.

---

## User Accounts & Authentication (NEW in Version 2)

Version 2 introduces multi-user support. You must sign in to create, view, or modify any trip. A signed-out user only sees the Login page.

### Seed Development Users

For convenience during development and testing, two pre-configured accounts are always available. These credentials are also printed on the Login page as a demo hint.

| Name         | Email                 | Password        | Sample Trips Owned (after reset)                              | Budget (total)    | Currencies (trips)       | # Expenses (total) | # Journal Entries (total) |
|--------------|-----------------------|-----------------|----------------------------------------------------------------|-------------------|--------------------------|--------------------|---------------------------|
| Alice Smith  | `alice@example.com`   | `Password123!`  | 2 trips — Vietnam Adventure + European Backpacking            | USD 2,000 + EUR 5,000 = USD 7,000 equiv | Vietnam: USD, Europe: EUR | 4 + 6 = **10** | Vietnam: 3 (10-01 / 10-02 / 10-04) + Europe: 3 = **6** |
| Bob Johnson  | `bob@example.com`     | `Password123!`  | 1 trip — Tokyo Discovery                                      | JPY 300,000       | Tokyo: JPY               | **5** | **0** (empty-state fixture — intentionally zero) |

> **Tip:** Use Alice to test features that require multiple itineraries with populated journal entries (Vietnam has 3 sorted newest-first). Use Bob to test the Travel Journal empty-state "No journal entries yet" placeholder grid because Tokyo has exactly 0 journal entries.

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
3. **Trip Details** — Manage a trip's itinerary (days and activities), budget, expenses, AND (NEW in V4) travel journal — but only if you are the owner

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

This same pattern applies recursively to days, activities, expenses, AND (V4) journal entries — accessing a day, activity, expense, or journal entry that lives under another user's trip always returns 403. Journal entries are additionally scoped inside their trip: accessing `/api/trips/trip-2/journal/je-1-3` (an entry under Alice's Vietnam trip but via Bob's Tokyo trip route) correctly 404s because je-1-3 isn't inside trip-2's `journal_entries[]`.

### Why Ownership Matters

Because Alice owns 2 trips and Bob owns 1 trip in the seed data, and their journal entry counts are asymmetric (Alice = 6 total, Bob = 0), you can immediately verify isolation works correctly by: sign in as Alice → open Vietnam → Journal section shows 3 cards. Sign in as Bob → open Tokyo → Journal section shows "No journal entries yet" placeholder, 0 cards, no Add button hidden.

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

## Travel Journal (NEW in Version 4)

The Travel Journal lets you record narrative diary entries, notes, and memories for each trip. Each journal entry belongs to exactly one trip and is displayed as a responsive card grid below the Expenses section. Journal entries cascade-delete with their trip (deleting a trip permanently removes all its journal entries).

> ⚠️ **Warning (Known Bug #45 + #46 — Trip Shrinking Trap):** If you later edit the trip's start/end date to *shrink* the date range, any already-persisted journal entries whose dates now fall outside the new range become "orphans". They still display in the card grid and can be viewed/deleted, but **editing any field (even just title) will fail with a date-range error** because the frontend always re-sends the unchanged date field in the PUT payload. **Recommended workflow:** Finalize the trip date range **before** writing journal entries. If you must shrink later, adjust affected entry dates first, or delete and re-create them.

### ⚠️ 3 Immutable Business Rules (you WILL hit 400 errors if you ignore these)

1. **Title Length Rule:** A journal entry `title` MUST be **between 1 and 100 characters after trimming whitespace**. Strings of all-spaces ("   ") are treated as blank and rejected with **HTTP 400 Title is required**. Titles exactly 101 characters or longer return **HTTP 400 Title must not exceed 100 characters**.
2. **Content Length Rule:** A journal entry `content` MUST be **between 1 and 5000 characters after trimming whitespace**. All-whitespace bodies are rejected with **HTTP 400 Content is required**. Content over 5000 chars returns **HTTP 400 Content must not exceed 5000 characters**. The frontend textarea has a `maxlength='5000'` hard guard so UI users cannot type beyond the limit.
3. **Date in Trip Range Rule:** A journal entry `date` MUST fall within trip start_date and end_date inclusive. Outside-range dates return **HTTP 400 Journal entry date must be within trip dates (YYYY-MM-DD to YYYY-MM-DD)** (raw API) or two separate messages with locale-formatted dates (browser form; see Known Bug #47 for exact-message mismatch details). *(Known Bug #45 + #46 Trap: if you shrink the trip range after entries exist, editing an orphaned entry's title or content alone fails because the frontend re-sends the unchanged out-of-range date in the same PUT.)*

### Journal Section UI (Card Grid + Add Button)

The Journal section appears below the Expenses table and shows:

- A section header **"Travel Journal"** with entry count badge (e.g., "3 entries") — wrapper `data-testid="journal-section"`
- An **Add Journal Entry** purple button — `data-testid="add-journal-entry"` (top-right of section)
- A responsive card grid. Every card shows:
  - **Date chip** (top-left, badge styling with locale-formatted date from `formatDate()`)
  - **Title** (bold header, truncates visually at 1 line via CSS)
  - **Content preview** (first ~200 characters of content with newlines flattened to spaces — clicking the card opens the full view modal)
  - **Right-side action icons:** ✏️ Edit (`data-journal-action="edit"` on the inner button) and 🗑️ Delete (`data-journal-action="delete"` on the inner button) — both are inside a flex container with `onclick="event.stopPropagation()"` to prevent bubbling the card's default View-full-journal handler
- **Empty-state placeholder:** If `journal_entries.length === 0` (Bob's Tokyo trip!), the grid is replaced with a centered card containing `"No journal entries yet — add your first memory with the button above."` — excellent automation empty-state selector target.

**Sort order (authoritative — automation depends on this!):** Journal entries are ALWAYS sorted:
1. **`date` descending** (newest dated entry first), then
2. **`created_at` descending** (entries created later appear above entries created earlier on the same date).

Vietnam seed entries after reset (expected card order — newest at top):
1. `je-1-3` date=2026-10-04 "Da Nang Beach Afternoon" (top)
2. `je-1-2` date=2026-10-02 "Ha Long Bay Magic"
3. `je-1-1` date=2026-10-01 "Arrival in Hanoi" (bottom)

### How to Add a Journal Entry

1. Open Trip Details → scroll to the **Travel Journal** section (below Expenses).
2. Click **Add Journal Entry** (`add-journal-entry`). A modal opens with 3 fields:

| Field           | Type       | Required? | Constraints                                                                 | `data-testid`        |
|-----------------|------------|-----------|-----------------------------------------------------------------------------|----------------------|
| **Title**       | Text input | ✅ Yes    | 1–100 chars after trim; frontend enforces `maxlength='100'` HTML attr      | `journal-title`      |
| **Date**        | Date picker| ✅ Yes    | must be within trip start_date ≤ date ≤ end_date inclusive                  | `journal-date`       |
| **Content**     | Textarea   | ✅ Yes    | 1–5000 chars after trim; frontend enforces `maxlength='5000'` HTML attr; renders in view modal with `white-space: pre-wrap` so paragraph breaks are preserved | `journal-content` |

3. Click **Add Entry** (submit button `data-testid="save-journal-entry"`).
4. Card grid re-renders with the new entry inserted at the correct sort position based on date DESC.

### How to Edit a Journal Entry

1. Click the ✏️ **Edit** icon on any journal card. The same 3-field modal opens with current values pre-filled (the Edit-path submit uses same `save-journal-entry` testid as Add — check form title text to distinguish).
2. Change any field(s) and click **Save Changes**.

> **Known Bug #45 (Edit Trap when combined with #46):** Even if you only edited the title, the frontend sends ALL 3 fields (title, content, date) in the PUT payload to the server. If you previously shrunk the trip's date range and the entry's stored date now falls outside, you will get HTTP 400 "date must be within trip range" even though you touched only title/content. Workaround: in the same edit, explicitly change the date field to a value currently inside the (now-shrunk) trip range, make your title/content change, then Save.

### How to View a Journal Entry (full content)

1. Click the card body anywhere that is not the Edit or Delete icon button.
2. A custom hand-built modal opens (not the generic showModalForm dialog) showing:
   - Entry title in full
   - Entry date
   - **Full content** with `white-space: pre-wrap` so newlines, indentation, and paragraph spacing render exactly as you typed them — text passes through `escapeHtml()` for XSS safety before insertion so raw HTML in your content won't execute
   - A shortcut ✏️ **Edit Entry** button (`data-testid="journal-view-edit-btn"`) to jump straight to the edit form without closing the view
3. Click outside modal or press **Esc** to close.

### How to Delete a Journal Entry

1. Click the 🗑️ **Delete** icon on the journal card.
2. A browser-native `confirm("Are you sure you want to delete this journal entry?")` dialog appears. (This is intentionally a native confirm, unlike some modal-based confirm flows elsewhere — automation scripts can handle it with `page.on('dialog', d => d.accept())`).
3. Confirm. The card is removed and the remaining grid re-renders with correct sort order.

> **API Note / Known Bug #50:** The published README spec says journal DELETE is idempotent: deleting an already-deleted entry should return 204. The actual code returns **HTTP 404 Journal entry not found** on the second delete of the same entry. If you write retry loops in raw API scripts, catch the 404 and treat it as success rather than throwing. The browser UX never double-deletes so this is only a raw-API concern.

### V4 Journal Data-testid Reference for Automation Testers

All V4 journal UI elements have stable selectors. Use these rather than brittle class-names.

| Area            | Selector / `data-testid` / attr                         | What it selects                                                                 |
|-----------------|----------------------------------------------------------|---------------------------------------------------------------------------------|
| **Journal outer section** | `data-testid="journal-section"`                 | Outermost `<div>` wrapper containing header, count badge, Add button, and grid  |
| **Add button**  | `data-testid="add-journal-entry"`                       | Purple "Add Journal Entry" button at top-right of journal section               |
| **Modal fields** | `data-testid="journal-title"`                           | Title `<input>` in Add/Edit Journal modal (maxlength=100)                       |
| **Modal fields** | `data-testid="journal-date"`                            | Date `<input>` in Add/Edit Journal modal                                        |
| **Modal fields** | `data-testid="journal-content"`                         | Content `<textarea>` in Add/Edit Journal modal (maxlength=5000)                 |
| **Modal submit** | `data-testid="save-journal-entry"`                      | Submit button in Add/Edit Journal modal (shared testid for both add and edit; check `.textContent` if you need to disambiguate) |
| **Per-card action** | `[data-journal-action="view"]` on the outer card flex  | The clickable whole-card wrapper that triggers View-full-content modal (contains the action div inside) |
| **Per-card action** | inner button with `data-journal-action="edit"` / `edit-journal-entry` class | Per-card Edit icon button — click for Edit modal  |
| **Per-card action** | inner button with `data-journal-action="delete"` / `delete-journal-entry` class | Per-card Delete icon button — click for confirm  |
| **View modal**  | `data-testid="journal-view-edit-btn"`                   | Edit shortcut button inside the View-full-content modal — click jumps to Edit   |

> **How to obtain real journal entry IDs for automation scripts:** After login call `GET /api/trips/{tripId}/journal` — the response is a JSON array sorted newest-first by (date DESC, created_at DESC); each object has `id` like `je-1-3` (seed) or `je-335590b810a7` (runtime UUID12-suffix pattern).

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

> **Note:** Budget, currency, and journal entries are not settable in the Create Trip form. New trips default to `budget = 0.00`, `currency = "USD"`, `journal_entries = []`. After creating, visit Edit Budget to set a realistic budget and currency; visit the Travel Journal section to add entries.

### Viewing Trip Details

- Click **View Details** on any trip card to open the Trip Details page. If someone shares a link to a trip you don't own, you'll get a 403 error.

### Editing a Trip

- Click the **pencil icon** (Edit) on any trip card.
  OR
- From the Trip Details page, click the **Edit Trip** button.

Make changes in the form and click **Save Changes**.

> ⚠️ **Warning (Bug #2 + #28 + #46 — Date Shrinking Hazard):** If you reduce the start_date (push it later) or reduce the end_date (push it earlier) — any existing days, expenses, or (V4) journal entries with dates now outside the new range become orphans. Expense and Journal edit PUTs will fail with range errors if you try to edit other fields on those orphaned records. Budget summary still sums orphaned expenses. Journal entries remain viewable/deletable but not editable. Recommended: don't shrink trip dates after you've started filling in real content.

### Deleting a Trip

- Click the **trash icon** (Delete) on any trip card.
  OR
- From the Trip Details page, click the **Delete** button.
- Confirm the deletion when prompted.

> ⚠️ **Warning:** Deleting a trip permanently removes it and all its days, activities, expenses, AND (V4) journal entries. All embedded sub-resources are deleted with the trip (cascade). This action cannot be undone. Only the trip owner can delete their trips — other users get a 403.

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

> **Tip:** You can add days on any date (including dates outside the trip range — the app does not enforce this currently, but it's good practice to keep days inside the trip's start/end dates). (See V4 Known Bug #35 — now 3-tier asymmetric enforcement: journal bounded, expense bounded, days STILL unbounded.)

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
- Any custom trips, days, activities, expenses, AND (V4) journal entries you created are wiped
- Alice's Vietnam Adventure → 3 journal entries in specific sorted order (10-04 top, 10-02 middle, 10-01 bottom)
- Alice's European Backpacking → 3 journal entries
- Bob's Tokyo Discovery → **0 journal entries** (empty-state placeholder grid)

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

After reset, the following trips are available (ownership is intentionally asymmetric). All 3 trips carry realistic V3 budgets, pre-seeded expenses, and V4 journal data:

| # | Trip Name              | Destination | Dates                | Owner   | Budget   | Currency | # Expenses | # Journal Entries | Representative Seed Entry / Expense                          | Notable Itinerary                                                                         |
|---|------------------------|-------------|----------------------|---------|----------|----------|------------|-------------------|---------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| 1 | Vietnam Adventure      | Vietnam     | Oct 1–10, 2026       | Alice   | 2,000    | USD      | 4          | **3** (sorted newest-first: 10-04, 10-02, 10-01) | Hotel Stays — $500 Accommodation (Oct 1); **"Da Nang Beach Afternoon"** (Oct 4 — top card) | Day 1: Arrival in Hanoi; Day 2: Ha Long Bay Cruise; Day 3: Hanoi → Da Nang flight, ...   |
| 2 | Tokyo Discovery        | Japan       | Nov 15–22, 2026      | Bob     | 300,000  | JPY      | 5          | **0** (empty state) | Ryokan Accommodation — ¥80,000 Accommodation (Nov 15)        | Day 1: Shibuya Crossing; Day 2: Senso-ji Temple / Asakusa, ...; **no journal entries (placeholder grid)** |
| 3 | European Backpacking   | Europe      | May 1–14, 2027       | Alice   | 5,000    | EUR      | 6          | **3** (Paris → Amsterdam → Rome sequence) | Paris Hotel — €700 Accommodation (May 1); "First Day in Paris" (May 2 — 1 of 3)           | Day 1–2: Paris; seed includes transport + meals across 4 countries; 3 journal narrative entries |

---

## Data Storage

All data is saved as two human-readable JSON files in the project-root `data/` directory. **Files are created automatically — you never need to create them manually.**

```
data/
├── trips.json     # All trips, days, activities, user_id ownership, budget, currency, embedded expenses[], embedded journal_entries[]
└── users.json     # User accounts (email, full_name, + bcrypt password_hash)
```

### Trip JSON Model (V4)

A representative trip record. **Expenses are EMBEDDED inside each trip object as a nested `expenses` array. Journal entries are ALSO EMBEDDED inside each trip object as a nested `journal_entries` array.** There is no separate `expenses.json` or `journal_entries.json` file.

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
    }
  ],
  "journal_entries": [
    {
      "id": "je-1-1",
      "title": "Arrival in Hanoi",
      "content": "Long flight but excited to be here. Old Quarter is bustling. Checked into hotel around 3pm — small room but great location right next to Hoan Kiem Lake. Dinner street food nearby: pho bo and banh mi, $5 total for both!",
      "date": "2026-10-01",
      "created_at": "2026-10-01T19:30:00",
      "updated_at": "2026-10-01T19:30:00"
    },
    {
      "id": "je-1-2",
      "title": "Ha Long Bay Magic",
      "content": "Overnight cruise. Woke up to misty karsts through the cabin window. Kayaked around hidden lagoons in the afternoon. Sunrise on the sundeck tomorrow will be unforgettable.",
      "date": "2026-10-02",
      "created_at": "2026-10-02T20:15:00",
      "updated_at": "2026-10-02T20:15:00"
    }
  ]
}
```

> **Note (Known Bug #53 — API vs On-Disk Asymmetry):** The raw JSON on disk contains `expenses[]` and `journal_entries[]` inside each trip. However, the REST API `GET /api/trips/{id}` response model ONLY includes `days[]` — it does NOT include the expenses or journal entries arrays. To fetch the full state that matches on-disk JSON, call all 4 endpoints separately:
> 1. `GET /api/trips/{id}` (header + days only)
> 2. `GET /api/trips/{id}/budget` (budget KPIs)
> 3. `GET /api/trips/{id}/expenses` (expenses array)
> 4. `GET /api/trips/{id}/journal` (journal_entries array)
> The frontend does this correctly via `Promise.all` in `renderTripDetails`.

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
- **V2 → V3:** If you copy a V2 `trips.json` (which lacks `budget`, `currency`, and `expenses` fields) into a V3 project, the app automatically fills in `budget: 0.0`, `currency: "USD"`, and `expenses: []` on every trip, then writes the file back. No data loss; you can then set realistic budgets and add expenses via the UI.
- **V3 → V4 (NEW):** If you copy a V3 `trips.json` (which lacks the `journal_entries` key on any trip) into a V4 project, the V4 migration automatically appends `journal_entries: []` to every trip missing it, then writes the file back. Trips keep all existing budget/currency/expenses data intact; they simply gain an empty journal array ready to accept entries.

---

## Validation Rules

The application enforces the following rules. Validation is performed in both the browser (client-side, for UX) and on the server (server-side, which always takes precedence). Budget & Expense rules are enforced **3-deep** (Pydantic schema → service layer → Decimal rounding at persistence boundary). Journal rules are also enforced 3-deep (Pydantic schema → service layer whitespace + length + range checks → frontend `maxlength` + pre-flight checks).

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
- **Date is NOT bounded inside trip start/end range** (Known Bug #1; Known Bug #35 amplified in V4 — expenses and journal entries ARE bounded but days are not)

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

### Travel Journal Rules (NEW in V4)

#### Title & Content Lengths
- **Journal Title:** MUST be **1 to 100 characters after trimming**. Empty string rejected client-side; all-whitespace `"   "` rejected at service with **HTTP 400 Title is required**; 101+ chars rejected at both layers with **HTTP 400 Title must not exceed 100 characters**. Title input enforces `maxlength="100"` in the HTML so users typing cannot overflow (submitting a longer value via raw API is still caught by schema + service).
- **Journal Content:** MUST be **1 to 5000 characters after trimming**. Empty string or all-whitespace → **HTTP 400 Content is required**; 5001+ chars → **HTTP 400 Content must not exceed 5000 characters**. Textarea enforces `maxlength="5000"` HTML hard cap for UI users.
- *(Known Bug #41 + #49): Whitespace-only payloads pass Pydantic schema because min_length counts spaces (caught by service), and non-blank padding whitespace like `"  Title  "` is stored verbatim with no strip() normalization at persist time.*

#### Date Range Rule (Journal Entries)
- **Journal entry date MUST fall within trip date range:** `trip.start_date ≤ journal_entry.date ≤ trip.end_date` inclusive. Out-of-range dates → **HTTP 400 Journal entry date must be within trip dates (YYYY-MM-DD to YYYY-MM-DD)** (raw API) or two separate browser-formatted messages (see Known Bug #47 for exact divergence).
  - On **Create Entry (`POST`):** Rule always runs.
  - On **Update Entry (`PUT`):** Rule only runs if `entry_update.date` is explicitly not None (PATCH-style guard exists at service line 336).
  - *(Known Bug #45 + #46 trap):** Even though the server correctly skips date validation when date=None in PUT, the frontend ALWAYS sends all 3 fields (including the unchanged date) in the PUT payload, so date is never None from the server's perspective on any browser edit. Shrink the trip range → orphaned entries → even "Edit title only" → 400 date error. Workaround: pick a new, valid in-range date as part of the same edit dialog, or delete and re-create the entry.*

#### Authorization & Ownership (Journal endpoints)
- Journal endpoints inherit per-trip ownership:
  - Accessing `/api/trips/{nonExistentId}/journal` → **HTTP 404**
  - Accessing `/api/trips/{someoneElsesTripId}/journal/...` → **HTTP 403**
  - Accessing an entry_id that does not exist inside the specified trip's journal_entries[] → **HTTP 404** (even if the same entry_id exists under a different trip and you own that other trip — entries are scoped to URL trip_id first for security)
- No anonymous access: all 5 journal endpoints (GET list / POST / GET single / PUT / DELETE) Depends on `get_current_user`; missing/expired JWT → **HTTP 401**.
- DELETE ownership note: deleting an entry you don't own or that doesn't exist returns **HTTP 404** in violation of the README idempotency spec (Known Bug #50); robust scripts should treat 404 on DELETE as "already gone, success".

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

### Editing a journal entry errors with "date must be within trip dates" even though I only changed the title (Known Bugs #45 + #46)

**Symptom:** You added a journal entry dated `2026-10-09` when the trip end_date was `2026-10-10`. Later you edit the trip and shrink end_date to `2026-10-05`. Now you open the journal entry just to fix a typo in the title (you never touch the date picker) → Save → HTTP 400 "Journal entry date must be within trip dates".

**Root cause:** Known Bug #45 (frontend always sends ALL 3 fields — title + content + date — in PUT even for a "title-only" edit) + Bug #46 (Edit Trip shrinks range with no revalidation of existing entries). The unchanged 2026-10-09 date is still present in the PUT body and triggers server validation.

**Workaround:** In the same edit dialog, **manually re-select the date field to a date inside the now-shrunk range**, fix your title typo, Save. Alternatively: delete the orphaned entry and re-create it with a corrected date. Best practice: lock in trip dates before writing journal entries.

### After shrinking trip end_date by 1 week I see journal cards with dates that appear outside the trip range (Known Bug #46)

**Symptom:** Vietnam Adventure was 10-01 → 10-10, had an entry dated 10-09. Later you edit trip to end 10-05. The journal card grid still shows the 10-09 entry prominently at top (it's newest-first sorted). Clicking Edit fails immediately with a date error.

**Root cause:** Known Bug #46. No cascading revalidation happens when you save an edited trip. Orphaned entries (dates now out of range) are left in-place in `journal_entries[]` and are still rendered, still deletable, still GET'able via API — but UPDATE is blocked by the journal date-range rule.

**Workaround:** Open each affected journal entry → set a valid date + Save. Or delete them. Or reset data. Shrinking trip dates after entries exist is not a recommended workflow.

### Cannot save a new journal entry with 101+ char title / 5001+ char content (Validation Rule, not a bug)

**Symptom:** Title field will not accept typing past 100 characters in the UI. Content textarea will not accept typing past 5000 characters. Trying the same via raw API returns HTTP 400 "… must not exceed N characters".

**Root cause:** Working as designed. Journal rule #1 (title 1–100) and #2 (content 1–5000) are enforced with `maxlength` in the HTML and matching server checks.

**Workaround:** Break overly long entries into multiple entries on consecutive days (dates can be repeated across entries — there is no "1 journal entry per day" rule), or shorten title by moving extra verbiage into the content body.

### Delete journal entry twice returns 404 (vs spec-promised 204) when writing retry loops (Known Bug #50)

**Symptom:** A script calls `DELETE /api/trips/trip-1/journal/je-xyz` twice (retry on transient network). First call → 204 (success). Second call → 404 (script crashes because code expects 204 per README spec).

**Root cause:** Known Bug #50 (API contract bug). Code path: store returns False when entry is gone → service raises JournalEntryNotFoundError → router catches and returns 404. Spec says deleting an already-deleted entry should be idempotent 204.

**Workaround:** In raw API retry logic for DELETE journal, treat BOTH 204 AND 404 as acceptable success outcomes for the "resource is gone" post-condition. In browser UX this never surfaces because the card is removed from DOM after first confirmation and is never clickable again.

### Empty-state journal placeholder not showing for a trip that should have 0 entries

**Symptom:** Bob's Tokyo trip has 0 journal entries, but instead of the empty placeholder card you see a blank section, or the Add button is missing.

**Root cause:** Most likely you added an entry in a prior session and didn't reset; or `data/trips.json` was manually edited and the trip has an entry with a blank title that renders invisibly.

**Workaround:** Click Reset Data. After a fresh reset Bob's Tokyo Discovery is guaranteed to have `journal_entries: []` exactly. The empty state placeholder "No journal entries yet — add your first memory with the button above." should render reliably. For automation, always assert the placeholder only immediately after a reset before running any journal CRUD on Bob's Tokyo trip.

### Journal card order changed after refresh / seed entries not in the order I expected (Sort stability — not a bug, but documentation)

**Symptom:** You expected journal cards sorted by created_at, or by index-in-array on disk, but instead they're sorted by date DESC + created_at DESC. Alice's Vietnam entries always appear Da Nang (10-04) at top, not Arrival Hanoi (10-01).

**Root cause:** Working as designed. Both the backend (store sort at line L505: `sorted(entries, key=lambda e: (e["date"], e["created_at"]), reverse=True)`) and frontend defensively re-sort again after receipt. The authoritative sort is newest-first by date, tiebreak newest-first by creation timestamp.

**Workaround:** Automation assertions should always compare against newest-first sorted order. For Vietnam seed fixtures after reset: assert order 1 = je-1-3 (10-04), order 2 = je-1-2 (10-02), order 3 = je-1-1 (10-01).

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
6. **Use Bob for isolation testing** — Bob's single Tokyo trip is a great control case for verifying 403 cross-user behavior (Alice can't see/edit it, and Bob can't see Alice's two trips). Also Bob's Tokyo has **0 journal entries** — perfect for testing the V4 Journal empty-state placeholder card and Add-button flow from scratch.
7. **Set Budget + Currency FIRST before adding expenses** — Because of Known Bug #24 (currency mismatch KPI drift), always configure the trip's budget and currency via Edit Budget **before** you begin adding expense rows. If you later change currency with expenses already recorded, delete the expenses first or accept the mixed state.
8. **Finalize trip date range BEFORE writing journal entries** — Due to Known Bug #46 + #45 trap (shrinking trip → orphan journal entries → editing ANY field fails because date is resent), do all your Edit Trip date changes FIRST, THEN start creating journal entries. You can still edit trip dates and expand the range later (expanding never causes orphans); only shrinking creates the trap.
9. **Use the 6 expense categories deliberately** —
   - `Accommodation` = lodging (hotels, hostels, Airbnb, homestays)
   - `Food` = meals, cafes, street food, groceries
   - `Transportation` = flights, trains, buses, taxis, ferries, car rentals, fuel
   - `Activities` = tickets, tours, shows, entry fees
   - `Shopping` = souvenirs, clothing, electronics
   - `Other` = travel insurance, visa fees, tips, miscellaneous
   
   Consistent categorization makes it easier to add up per-category spending in the future (see Known Bug #39 — per-category totals are not yet displayed in the UI but are trivially computable from the API response).
10. **Save receipts in the Expense Description field and narrative in Journal Content** — Two separate fields for two separate use cases! Expense.description = "Receipt #A1B2C3 Blue Lagoon Seafood, split 3 ways my share $22.50" (structured, for financial recordkeeping). Journal.content = "Dinner at this amazing street-side seafood spot in Da Nang tonight. The owner recommended the grilled clams and they were life-changing. Sat next to a couple from Melbourne who gave us great tips for Hoi An tomorrow." (free-form narrative, paragraphs, memories — `pre-wrap` rendering preserves line breaks perfectly).
11. **Multiple journal entries per day are allowed and encouraged** — There is no "1 entry per day" constraint. Record morning, afternoon, evening entries separately on 2026-10-04 if you want; created_at DESC tiebreaker ensures the evening entry sorts above the morning entry when dates are equal, giving correct intra-day chronology newest-first.
12. **Use Alice's Vietnam trip + Reset Data for repeatable journal automation fixtures** — After a reset, Alice's Vietnam Adventure Journal section is always in a **3 entries sorted newest-first** state:
    - Card 1 (top): `je-1-3` dated 2026-10-04 "Da Nang Beach Afternoon" (created 22:00, updated 22:05)
    - Card 2 (middle): `je-1-2` dated 2026-10-02 "Ha Long Bay Magic"
    - Card 3 (bottom): `je-1-1` dated 2026-10-01 "Arrival in Hanoi"
    
    This is the cleanest deterministic fixture for testing your Playwright/Selenium journal selectors: empty → not (Bob), 3-entry grid → yes (Alice Vietnam), correct sort order → verified, per-card edit/delete actions → accessible.
13. **Use Alice's Europe trip for cross-trip journal isolation testing** — Alice owns both Vietnam AND Europe, so after login the Trips List shows 2 cards and each trip's journal is isolated. Europe has 3 journal entries (Paris May 2, Amsterdam May 7, Rome May 12). Verify that opening Vietnam's journal never shows Rome entries, and vice versa — great smoke test for the `GET /api/trips/{id}/journal` scoping-by-trip-id security rule.
14. **Use Bob's Tokyo trip exclusively for the empty-state → add entry → now 1 entry flow** — Bob's Tokyo reliably has 0 entries after every reset. This is the perfect fixture to test: (1) placeholder card renders; (2) `add-journal-entry` clickable; (3) first POST succeeds; (4) grid renders with 1 card and placeholder has been removed. No other seed trip provides the "zero → one" transition in as clean a starting state.
15. **Verify the budget + expense + journal baseline together** — After every reset, Alice's Vietnam has a combined, deterministic state you can assert in full-page tests: Budget $2,000 USD, Spent $1,250, Remaining $750 (NOT over budget → progress bar amber/green, Over badge HIDDEN), 4 expenses in table, **3 journal entries sorted 10-04 / 10-02 / 10-01**. Running one broad "after-reset Vietnam sanity check" against this combined baseline catches regressions across V2 (ownership) + V3 (budget/expense) + V4 (journal) in a single Playwright run.

---

## Technical Notes (Advanced Users)

### API Usage & Authentication

All UI actions are backed by a fully-documented REST API. You can explore it at:

- **Swagger UI (interactive):** <http://localhost:8000/docs>
- **OpenAPI JSON schema:** <http://localhost:8000/openapi.json>

**Important — JWT Requirement:** Every trip/day/activity/budget/expense/journal endpoint and the reset endpoint requires the caller to present a valid JWT in the `Authorization` header as `Bearer <token>`. Unauthenticated calls return HTTP 401.

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

### Example: Listing + Creating Journal Entries via API (V4)

```bash
# Get Alice's token and a real trip ID (Vietnam = trip-1)
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"Password123!"}' | jq -r .access_token)

# List Alice's Vietnam journal entries (should be 3, sorted newest-first: 10-04, 10-02, 10-01)
curl -s http://localhost:8000/api/trips/trip-1/journal \
  -H "Authorization: Bearer $TOKEN" | jq -c '.[] | {id, date, title}'

# Create a new journal entry via raw API (expect 201)
curl -s -X POST http://localhost:8000/api/trips/trip-1/journal \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Last Minute Shopping",
    "content": "Picked up a silk scarf for Mom from the night market before the flight. Great price after bargaining.",
    "date": "2026-10-10"
  }' | jq '{id, created_at}'
```

---

## Getting Help

For technical issues, refer to:
1. This user manual
2. The project's `README.md` for architecture and setup details
3. The Swagger API docs at `/docs` for API-specific help
4. `KNOWN_BUGS.md` for a list of confirmed issues, especially if you hit unexpected behaviour

---

*Version 4.0.0 — Trip Planner MVP with Travel Journal CRUD, Budget Management & JWT Authentication*
