# Trip Planner MVP (Version 4)

A small, simple Trip Planner web application built as the foundation for a Test Automation Engineering training course.

## Application Description

The Trip Planner allows users to create and manage travel itineraries. Each itinerary (trip) contains a name, destination, date range, a configurable budget with a currency, an expenses ledger, a travel journal for diary entries, and a set of days, each of which can have multiple activities/attractions.

**Version 2** extended Version 1 by adding **user accounts, secure registration/login, JWT-based authentication, and per-user trip ownership scoping**.

**Version 3** extends Version 2 by adding **trip-level budget management with a currency field, a full expense CRUD ledger with categories, automated over-budget detection, date-range validation for expenses, and currency-match enforcement** on every expense. All existing V1/V2 functionality is preserved 100% — budget and expenses are additive features.

**Version 4** extends Version 3 by adding a **full Travel Journal CRUD system** with dated entries, title + multi-line plain-text content, server-generated timestamps, date-range validation against the trip, and ownership-enforced endpoints. A dedicated Journal section appears on the Trip Details page showing entries sorted newest-first with view/create/edit/delete modals. All existing V1–V3 functionality is preserved 100% — the journal is a purely additive feature.

This is intentionally small, simple, and deterministic, designed for easy testing and future extension.

## What's New in Version 4

- **Travel Journal CRUD**: Every trip now carries a nested `journal_entries[]` array; full REST CRUD is exposed under `/api/trips/{trip_id}/journal[/:entry_id]` with standard GET/POST/PUT/DELETE verbs
- **JournalEntry Data Model**: Each entry has `id` (prefix `je-`), `trip_id`, `title` (1–100 chars, required), `content` (1–5000 chars, plain text, required), `date` (ISO date, required), and server-generated `created_at` / `updated_at` timestamps (ISO 8601 with time; client cannot set them)
- **Newest-First Sorting**: Journal list endpoint returns entries sorted by `date DESC, created_at DESC` so the most recent diary entry always appears first; client performs a defensive secondary sort for display
- **Date-Range Validation**: Journal `date` MUST fall inside its trip's `[start_date, end_date]` window; out-of-range values return HTTP 400 with a deterministic message (enforced both create and update paths when date actually changes)
- **Length & Presence Validation**: Title/content cannot be whitespace-empty; title max 100 chars, content max 5000 chars — same rules on client and server with identical wording
- **Plain-Text Multiline Rendering**: Journal content is stored and rendered as plain text; line breaks are preserved via `white-space: pre-wrap` and `word-break: break-word`; content is HTML-escaped before injection (no markdown, no rich text, no HTML interpretation — XSS-safe)
- **Authorization Enforcement**: Every journal endpoint resolves ownership through the trip → authenticated user chain; Bob cannot read/create/edit/delete entries on Alice's trips (HTTP 403); non-existent entry_id returns HTTP 404
- **Cascade Delete via Nesting**: Journal entries live inside the trip object in `trips.json`; deleting a trip automatically deletes all its journal entries with zero orphan records (no extra cleanup code)
- **Trip Date Edit Flexibility**: Editing a trip's `start_date` / `end_date` is allowed even if existing journal entries fall outside the new range (consistent with V3 expense-date handling — validation runs only on journal entry create/update, not on trip edit). Existing entries are never auto-deleted or modified by a trip date change
- **Dedicated UI Section on Trip Details**: Journal section (indigo/violet theme) sits between Expenses and Itinerary sections, showing entry cards with date badge, title, and short content preview; click a card to open a full-width "View Entry" modal (max-w-2xl); add/edit/delete icons with `stopPropagation` so icon-clicks don't also trigger view
- **View + Edit/Delete Modals**: Standalone view modal renders multiline content with pre-wrap + escapeHtml; view modal has a shortcut Edit button; create/edit form reuses the generic `showModalForm` pattern with title input, date input, content textarea; delete uses confirm-modal before DELETE
- **Updated Seed Data**: Alice's Vietnam Adventure (trip-1) ships with 3 chronological entries dated 2026-10-01, 2026-10-02, 2026-10-04 (verifies newest-first sort → 10-04 appears top); Alice's European Backpacking (trip-3) has 3 entries dated 2026-05-01, 2026-05-03, 2026-05-07; Bob's Tokyo Discovery (trip-2) intentionally has zero journal entries so tests can confirm empty-state rendering
- **Automation TestIDs**: Journal section exposes `data-testid="journal-section"`, add button `add-journal-entry`, per-card `journal-entry-card` / `journal-title` / `journal-date` / `journal-content-preview`, per-row `edit-journal-entry` / `delete-journal-entry`, form fields `journal-title` / `journal-date` / `journal-content`, submit `save-journal-entry`, and view-modal shortcut `journal-view-edit-btn`
- **Transparent Field Migration**: Pre-V4 `trips.json` records that lack a `journal_entries` key are upgraded in-place on first read to `"journal_entries": []` — no manual editing, no data loss

## What's New in Version 3

- **Trip Budget**: Every trip now has a configurable `budget` (non-negative float) and a `currency` chosen from seven supported currencies (USD, EUR, GBP, ILS, VND, THB, JPY)
- **Budget Summary Calculation**: Backend authoritatively computes `total_spent`, `remaining`, and an `over_budget` boolean on every read — results are rounded to 2 decimal places via Decimal arithmetic (no float drift)
- **Over-Budget Detection**: UI colour-codes the remaining tile and displays a prominent red badge when an expense pushes spending past the budget
- **Full Expense CRUD**: Create, read, update, delete individual expenses nested under `/api/trips/{trip_id}/expenses` with ownership scoped to the trip owner
- **Six Expense Categories**: Accommodation, Food, Transportation, Activities, Shopping, Other — each rendered as a coloured badge
- **Currency Match Enforcement**: Every expense must carry the same `currency` as its parent trip; mismatched values return HTTP 400
- **Expense Date-Range Validation**: Expense `date` must fall inside its trip's [start_date, end_date] window; out-of-range dates return HTTP 400
- **Amount Rules**: Expense `amount` is strictly positive; budget may be zero or positive
- **Updated Seed Data**: Each of the 3 sample trips now ships with realistic budget + expenses seed data (Vietnam: $2000 USD / 4 expenses; Tokyo: ¥300,000 JPY / 5 expenses; Europe: €5000 EUR / 6 expenses)
- **Automation Selectors**: Budget summary tiles expose `budget-amount`, `budget-currency`, `budget-spent`, `budget-remaining`, `budget-over-budget` testids; expense form exposes `expense-description`, `expense-category`, `expense-amount`, `expense-currency`, `expense-date` and `save-expense`
- **Transparent Field Migration**: V2 trips.json records that lack `budget`, `currency` or the embedded `expenses` array are upgraded in-place on first read to default values (budget=0, currency=USD, expenses=[])

## What's New in Version 2

- **User Accounts**: Register with email and password, or sign in with existing credentials
- **Secure Password Hashing**: Passwords stored as adaptive bcrypt hashes (never plaintext)
- **JWT Authentication**: HS256 signed tokens carrying authenticated user identity
- **Trip Ownership**: Every trip belongs to one user; users can only read/write their own trips
- **Authorization Enforcement**: Server strictly separates 404 (resource does not exist) from 403 (resource exists but belongs to another user)
- **Protected Reset**: Seed reset now requires authentication; restores both user accounts and trip ownership deterministically
- **Automatic Migration**: Version 1 `data/trips.json` files (without `user_id`) are transparently upgraded on first read
- **New Seed Development Users**: Two stable, deterministic dev accounts with asymmetric trip counts

## Architecture Overview

```
┌────────────────────────────────────────────────────────┐
│         Frontend (HTML + Vanilla JS + Tailwind)        │
│  Login/Register views · JWT in localStorage · Logout   │
└───────────────────────────┬────────────────────────────┘
                            │  REST API (JSON) + Authorization: Bearer <jwt>
┌───────────────────────────▼────────────────────────────┐
│               FastAPI Backend (Python)                 │
│  ┌───────────────────────────┐  ┌────────────────────┐ │
│  │         Routes            │  │  Business Logic    │ │
│  │ (trips/days/activities/   │  │ trip_service +     │ │
│  │  auth + system/reset)     │  │ auth_service       │ │
│  └───────────────┬───────────┘  └──────────┬─────────┘ │
│                  │  Depends(current_user)             │
│         ┌────────▼────────┐                         │
│         │  security.py    │  JWT decode + bcrypt     │
│         │  (passwords,    │  verify + User injection │
│         │   JWT, Deps)    │                         │
│         └───────┬─────────┘                         │
│         ┌───────▼─────────────────┐                   │
│         │   Persistence Layer     │                   │
│         └──┬───────────────┬──────┘                   │
└────────────┼───────────────┼──────────────────────────┘
     ┌───────▼───────┐ ┌────▼──────────────┐
     │  JSON File    │ │  JSON File        │
     │ data/trips.json│ │ data/users.json   │
     │ (trip.user_id)│ │ (password_hash)   │
     └───────────────┘ └───────────────────┘
```

## Technology Stack

### Backend
- **Python 3.10+**
- **FastAPI** — Web framework for REST API
- **Pydantic v2** — Data validation (including EmailStr)
- **Uvicorn** — ASGI server
- **passlib + bcrypt** — Adaptive password hashing
- **python-jose + cryptography** — JWT signing/verification (HS256)
- **email-validator** — RFC-compliant email validation

### Frontend
- **HTML5** — Markup (single page, multiple views)
- **Vanilla JavaScript (ES6+)** — UI logic (no frameworks)
- **Tailwind CSS** (via CDN) — Styling
- **REST API** — Communication with backend; every request carries JWT when authed
- **localStorage** — Persists JWT token and current user profile

### Data Persistence
- **JSON files** under project-root `data/` directory:
  - `data/trips.json` — Trips + nested days/activities (each trip has `user_id`)
  - `data/users.json` — User accounts (with `password_hash`, no plaintext)

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- A modern web browser

## Installation

1. Navigate to the project root directory and create a virtual environment (recommended):

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies (V2 adds auth packages to the V1 set):

```bash
pip install -r backend/requirements.txt
```

## How to Run the Backend

From the project root directory (with virtual environment activated):

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will start on:
- **Frontend (Login page)**: `http://localhost:8000/`
- **API base**: `http://localhost:8000/api/`
- **API Docs (Swagger UI)**: `http://localhost:8000/docs`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`
- **Health check**: `http://localhost:8000/api/health`

The `--reload` flag enables hot-reloading during development.

**Startup Behaviour**:
- On first launch, two seed development users (Alice + Bob) are created automatically in `data/users.json`
- Seed trip itineraries are written to `data/trips.json`, with ownership assigned (2 trips for Alice, 1 for Bob)
- If a pre-existing V1 `trips.json` exists (without `user_id`), transparent migration injects user ownership into every trip and writes the file back — no manual editing needed

## How to Use the Frontend

The frontend is served automatically by FastAPI at `http://localhost:8000/`. There is no separate frontend server.

### Authentication Flow

1. **Landing page**: If you are not signed in, you are shown the Login form (with Register link and demo credentials hint)
2. **Register a new account**: Click "Register" in the header. Provide full name, email, password (≥ 6 chars), and confirmation. After successful 201 response you are returned to the Login form
3. **Login**: Submit email + password. On success the JWT is written to `localStorage`, and the UI redirects to your trip list
4. **Authenticated header**: Once signed in, the header displays your full name and email alongside a "Reset Data" button and a `data-testid="logout"` Logout button
5. **Logout**: Clicking Logout clears tokens from localStorage and returns to the Login view
6. **Session expiry**: A 401 response from any API call clears the session locally and shows a "Session expired" toast before returning to the Login view

### Seed Development Users (for testing)

Both accounts share the same password for convenience in test automation. The ownership split is intentionally asymmetric so tests can immediately verify isolation and filtering.

| Name         | Email                 | Password        | Number of Trips | Owned Itineraries                          | Budget    | Currency | Number of Expenses | Number of Journal Entries |
|--------------|-----------------------|-----------------|-----------------|--------------------------------------------|-----------|----------|--------------------|--------------------------|
| Alice Smith  | alice@example.com     | `Password123!`  | 2               | Vietnam Adventure, European Backpacking   | $2,000    | USD      | 4 (Vietnam) + 6 (Europe) | 3 (Vietnam) + 3 (Europe) |
| Bob Johnson  | bob@example.com       | `Password123!`  | 1               | Tokyo Discovery                           | ¥300,000  | JPY      | 5                  | 0 (intentionally empty) |

These credentials are also displayed on the Login page itself as a demo hint block.

## API Overview

### Authentication (`/api/auth/*`)

All auth endpoints accept JSON bodies. Login response contains both the JWT and the current user profile.

| Method | Endpoint                  | Description                                                                                  | Request Body Fields                                      |
|--------|---------------------------|----------------------------------------------------------------------------------------------|----------------------------------------------------------|
| POST   | `/api/auth/register`      | Create a new user account. Returns 201 with the created User (no password fields).           | `full_name`, `email`, `password` (≥6), `password_confirmation` (match) |
| POST   | `/api/auth/login`         | Authenticate with email + password. Returns 200 with JWT `access_token` + nested `user`.     | `email`, `password`                                      |
| POST   | `/api/auth/login/form`    | OAuth2-compatible form-data variant (not in schema; for Swagger UI "Authorize" button).     | form-data: `username` (=email), `password`              |
| GET    | `/api/auth/me`            | Retrieve currently authenticated user (used by UI boot to validate existing localStorage token). | — requires valid JWT in `Authorization: Bearer …` header |

### Trips — **Requires Authentication**

All trip endpoints filter by the authenticated user (you only see your own trips) and enforce ownership on every read/write.

| Method | Endpoint                 | Description              |
|--------|--------------------------|--------------------------|
| GET    | `/api/trips`             | List **your** trips only |
| POST   | `/api/trips`             | Create a new trip (owner = you, identity sourced from JWT — NEVER from client body) |
| GET    | `/api/trips/{trip_id}`   | Get your trip details (403 if another user's; 404 if DNE) |
| PUT    | `/api/trips/{trip_id}`   | Update your trip (403 if another user's; 404 if DNE) |
| DELETE | `/api/trips/{trip_id}`   | Delete your trip (403 if another user's; 404 if DNE) |

### Trip Days — **Requires Authentication**

| Method | Endpoint                                      | Description                |
|--------|-----------------------------------------------|----------------------------|
| GET    | `/api/trips/{trip_id}/days`                   | List days for your trip    |
| POST   | `/api/trips/{trip_id}/days`                   | Add a day to your trip     |
| GET    | `/api/trips/{trip_id}/days/{day_id}`          | Get your day details       |
| PUT    | `/api/trips/{trip_id}/days/{day_id}`          | Update your day            |
| DELETE | `/api/trips/{trip_id}/days/{day_id}`          | Delete your day            |

All day endpoints first verify you own the parent trip — cross-user access to a trip implicitly blocks all its sub-resources with 403.

### Activities — **Requires Authentication**

| Method | Endpoint                                                                    | Description                   |
|--------|-----------------------------------------------------------------------------|-------------------------------|
| GET    | `/api/trips/{trip_id}/days/{day_id}/activities`                            | List activities for your day  |
| POST   | `/api/trips/{trip_id}/days/{day_id}/activities`                            | Add activity to your day      |
| GET    | `/api/trips/{trip_id}/days/{day_id}/activities/{activity_id}`              | Get your activity details     |
| PUT    | `/api/trips/{trip_id}/days/{day_id}/activities/{activity_id}`              | Update your activity          |
| DELETE | `/api/trips/{trip_id}/days/{day_id}/activities/{activity_id}`              | Delete your activity          |

### Budget — **Requires Authentication**

Budget endpoints return a `BudgetSummary` object (`budget`, `currency`, `total_spent`, `remaining`, `over_budget`) computed by the backend authoritatively. All money values are rounded to 2 decimal places using Decimal arithmetic.

| Method | Endpoint                                | Description                                                                                  |
|--------|-----------------------------------------|----------------------------------------------------------------------------------------------|
| GET    | `/api/trips/{trip_id}/budget`           | Fetch budget summary for your trip (403 if another user's trip)                              |
| PUT    | `/api/trips/{trip_id}/budget`           | Update your trip's budget and (optionally) currency. Body: `{ budget: float>=0, currency?: SUPPORTED_CURRENCIES }` |

### Expenses — **Requires Authentication**

All expense endpoints are scoped under their owning trip. Expense ownership is inherited from the trip — if the trip isn't yours the entire sub-resource returns 403 before any expense-level lookup happens.

| Method | Endpoint                                          | Description                                                               |
|--------|---------------------------------------------------|---------------------------------------------------------------------------|
| GET    | `/api/trips/{trip_id}/expenses`                   | List all expenses for your trip (sorted client-side by date descending)  |
| POST   | `/api/trips/{trip_id}/expenses`                   | Create a new expense on your trip (201). Validates currency=trip.currency, amount>0, date in range |
| GET    | `/api/trips/{trip_id}/expenses/{expense_id}`      | Get a single expense (404 if expense DNE on this trip)                   |
| PUT    | `/api/trips/{trip_id}/expenses/{expense_id}`      | Update an expense (same validations as create; fields optional via ExpenseUpdate) |
| DELETE | `/api/trips/{trip_id}/expenses/{expense_id}`      | Delete an expense (204)                                                   |

Supported currencies in V3 (same list for budget and expenses): `USD`, `EUR`, `GBP`, `ILS`, `VND`, `THB`, `JPY`
Expense categories: `Accommodation`, `Food`, `Transportation`, `Activities`, `Shopping`, `Other`

### Journal — **Requires Authentication** (NEW in V4)

All journal endpoints are scoped under their owning trip. Journal ownership is inherited from the trip — if the trip isn't yours the entire sub-resource returns 403 before any entry-level lookup happens. Server-generated `created_at` / `updated_at` timestamps are ISO 8601 strings; clients cannot set or mutate them via any request body.

| Method | Endpoint                                                 | Description                                                                                                                                                                                                 |
|--------|----------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| GET    | `/api/trips/{trip_id}/journal`                           | List all journal entries for your trip, sorted authoritatively by the **server** as `date DESC, created_at DESC` (newest first). Returns `[]` when trip has no entries (HTTP 200).                       |
| POST   | `/api/trips/{trip_id}/journal`                           | Create a new journal entry (HTTP 201). Body: `{ title, content, date }`. Validates: title 1–100 chars (non-whitespace), content 1–5000 chars (non-whitespace), date within trip [start_date, end_date].    |
| GET    | `/api/trips/{trip_id}/journal/{entry_id}`                | Get a single journal entry (HTTP 200). Returns 404 if entry_id does not exist on this trip; 403 if trip belongs to another user.                                                                          |
| PUT    | `/api/trips/{trip_id}/journal/{entry_id}`                | Update a journal entry (HTTP 200). Body uses `JournalEntryUpdate` — **all fields optional** (`title?`, `content?`, `date?`). Missing fields retain existing values. Validations apply only to the merged effective result; date-range check runs only if `date` is actually changed. |
| DELETE | `/api/trips/{trip_id}/journal/{entry_id}`                | Delete a journal entry (HTTP 204). No response body. Idempotent — deleting an already-deleted entry still returns 204 (confirm via GET afterward).                                                       |

**JournalEntry create body example**:
```json
{
  "title": "Arriving in Hanoi",
  "content": "Landed at Noi Bai airport at 6am.\nTook the airport bus into the old quarter.\nStreet food for breakfast — pho bo was amazing.",
  "date": "2026-10-01"
}
```

**JournalEntry response fields**:
- `id`: string, prefix `je-` (e.g., `je-1-4`)
- `trip_id`: string (echoes URL param)
- `title`: string, 1–100 chars
- `content`: string, 1–5000 chars, plain text only (preserves newlines)
- `date`: ISO date string (YYYY-MM-DD)
- `created_at`: ISO 8601 datetime string, server-generated on create, immutable
- `updated_at`: ISO 8601 datetime string, server-generated (same as `created_at` until first PUT), refreshed on every update

Error mapping for journal endpoints (in addition to standard 401/422):
- Trip not found / entry not found → **HTTP 404** (detail: `"Trip not found"` or `"Journal entry not found"`)
- Trip exists but not yours → **HTTP 403** (detail: `"Not authorized"`)
- Domain validation (empty title/whitespace, title too long, content too long, date out of range) → **HTTP 400** (deterministic detail strings matching client-side wording exactly)

### System

| Method | Endpoint               | Description                                                                                |
|--------|------------------------|--------------------------------------------------------------------------------------------|
| POST   | `/api/system/reset`    | Reset **both** users and trips back to seed state. Requires authentication (any logged-in user may invoke it). Resets journal entries along with all other trip data. |
| GET    | `/api/health`          | Unauthenticated health check. Returns `{"status":"ok","version":"4.0.0"}`.               |

### HTTP Status Codes

| Code | Meaning                                                                 |
|------|-------------------------------------------------------------------------|
| **200 OK**           | Successful retrieval, update, or system reset                          |
| **201 Created**      | Successful creation (register, trip, day, activity)                    |
| **204 No Content**   | Successful deletion                                                     |
| **400 Bad Request**  | Domain-level validation (e.g., end_date before start_date, mismatched passwords from service layer) |
| **401 Unauthorized** | Missing, invalid, or expired JWT; or wrong login credentials. Response for failed login is **exactly** `"Invalid email or password."` regardless of cause (prevents email enumeration). |
| **403 Forbidden**    | You are authenticated but the target resource **exists and belongs to a different user** |
| **404 Not Found**    | The target resource does not exist at all (independent of user)        |
| **409 Conflict**     | Duplicate email during registration                                     |
| **422 Unprocessable** | Pydantic schema-level validation (e.g., missing required field, password string too short) |

Pydantic/OpenAPI schema validation returns 422 per FastAPI convention; domain-level service validation returns 400. Both indicate a client-side input problem.

Client `detail` error body shape:

```json
{
    "detail": "Trip not found"
}
```

## Data Storage Explanation

All data is persisted as human-readable JSON in the project-root `data/` directory. Two files are maintained:

**File 1 — `data/trips.json`**: Holds all itineraries (trip + nested days + nested activities + embedded expenses array + embedded journal_entries array). Every trip object carries `user_id`, `budget`, and `currency` fields; each expense lives inside `expenses[]`; each journal entry lives inside `journal_entries[]`.

**File 2 — `data/users.json`**: Holds user accounts. Each user object contains a `password_hash` field with a bcrypt `$2b$` adaptive hash. The literal plaintext password is **never** written to disk, logged, or returned by any API.

The persistence layer (`backend/app/data/trip_store.py` + `backend/app/data/user_store.py`) fully abstracts all read/write operations. API routes and business logic never touch JSON files directly. The physical layout (all sub-resources nested inside trip objects) is intentionally not exposed to callers — nesting journal entries inside trips guarantees that deleting a trip automatically cascade-deletes all its journal entries with zero orphan records.

### Trip Ownership & Migration

- **V1 migration (automatic)**: If the app first loads a legacy V1 `trips.json` where any trip dict lacks a `user_id` field, the store immediately assigns ownership via the seed assignment map (trip-1→Alice, trip-2→Bob, trip-3→Alice; unknown IDs default to Alice) and rewrites the file.
- **V2 → V3 field migration (automatic)**: Any trip dict missing `budget`, `currency`, or an `expenses` array is upgraded transparently on first read: `budget=0.0`, `currency="USD"`, `expenses=[]`.
- **V3 → V4 field migration (automatic)**: Any trip dict missing a `journal_entries` array is upgraded transparently on first read: `"journal_entries": []`. This runs alongside the V3 migration and after V1 ownership injection.
- **Identity never trusted from client**: When a user creates a new trip, `user_id` is injected by the server from the JWT subject claim — a client body cannot spoof ownership by including `user_id` in JSON. The same applies to journal entries: `trip_id` is always derived from the URL path (never the body) and `created_at`/`updated_at` are server-generated only.
- **Isolation invariant**: The service layer pre-looks-up a trip's owner before every sub-resource call. If owner is `None` → 404; if owner ≠ current JWT user → 403. This ensures every endpoint correctly disambiguates 403 vs 404 — including all journal endpoints.
- **Trip date change handling (V4 journal rule)**: Editing a trip's `start_date`/`end_date` does **not** validate or cull existing journal entries. Journal date-range enforcement runs only at journal create/update time (consistent with V3 expense-date handling). If a trip's date window shrinks around existing journals, those journals remain readable/editable/deletable; only *new* create attempts and *date-changing* updates will fail the range check.

### Trip JSON Model (V4 — note new `journal_entries` array alongside `expenses`):

```json
{
  "id": "trip-1",
  "user_id": "user-alice",
  "name": "Vietnam Adventure",
  "destination": "Vietnam",
  "start_date": "2026-10-01",
  "end_date": "2026-10-10",
  "budget": 2000.0,
  "currency": "USD",
  "expenses": [
    {
      "id": "exp-trip1-1",
      "trip_id": "trip-1",
      "description": "Hotels - Hanoi & Ho Chi Minh",
      "category": "Accommodation",
      "amount": 500.0,
      "currency": "USD",
      "date": "2026-10-05"
    }
  ],
  "journal_entries": [
    {
      "id": "je-1-1",
      "trip_id": "trip-1",
      "title": "First day in Hanoi",
      "content": "Landed at 6am after a long flight...\nPho bo for breakfast on the street corner.",
      "date": "2026-10-01",
      "created_at": "2026-09-15T08:00:00.000000",
      "updated_at": "2026-09-15T08:00:00.000000"
    }
  ],
  "days": [
    {
      "id": "day-1-1",
      "date": "2026-10-01",
      "title": "Arrival in Hanoi",
      "activities": [
        {
          "id": "act-1-1-1",
          "name": "Arrive in Hanoi",
          "location": "Noi Bai Airport",
          "description": "..."
        }
      ]
    }
  ]
}
```

### User JSON Model (on disk — note `password_hash`, NO plaintext):

```json
{
  "id": "user-alice",
  "full_name": "Alice Smith",
  "email": "alice@example.com",
  "password_hash": "$2b$12$..."
}
```

The `password_hash` is returned **to zero API responses** — user serialization in every endpoint and service strips this field explicitly.

## Project Structure

```
trip-planner-v4/
├── backend/
│   ├── main.py                      # FastAPI app v4.0.0 entry point: budget + expenses + journal routers included
│   ├── requirements.txt             # Python deps (fastapi, pydantic, uvicorn, bcrypt/passlib, python-jose, email-validator)
│   └── app/
│       ├── security.py              # JWT encode/decode, bcrypt, get_current_user Depends
│       ├── models/
│       │   └── schemas.py           # Pydantic models: JournalEntry/Base/Create/Update, Trip (+budget, +currency), Day, Activity, Expense*, BudgetSummary, BudgetUpdate, User, UserCreate, UserLogin, Token
│       ├── services/
│       │   ├── trip_service.py      # Business logic: trip/day/activity CRUD + budget summary + expense CRUD + journal CRUD + validation errors
│       │   └── auth_service.py      # Register, login, ensure_seed_users, reset_users_to_seed
│       ├── data/
│       │   ├── trip_store.py        # Persistence: owner lookup, V1 user_id migration, V3 budget/currency/expenses migration, V4 journal_entries migration, BudgetSummary calc, expense CRUD, journal CRUD
│       │   ├── user_store.py        # Persistence for data/users.json (password_hash internal only)
│       │   └── seed_data.py         # SEED_USERS list + SEED_TRIP_USER_ASSIGNMENTS + trip dicts with user_id, budget, currency, seed expenses arrays, and seed journal_entries arrays
│       └── routers/
│           ├── trips.py             # Trip CRUD (Depends(get_current_user), catches NotAuthorizedError→403)
│           ├── days.py              # Day CRUD (same auth + ownership pattern)
│           ├── activities.py        # Activity CRUD (same)
│           ├── budget.py            # GET/PUT /api/trips/{trip_id}/budget
│           ├── expenses.py          # GET/POST/PUT/DELETE /api/trips/{trip_id}/expenses[/:expense_id]
│           ├── journal.py           # NEW (V4): GET/POST/PUT/DELETE /api/trips/{trip_id}/journal[/:entry_id]
│           ├── auth.py              # /register, /login, /login/form, /me
│           └── system.py            # /reset (auth-protected; resets both stores incl. journals)
├── frontend/
│   ├── index.html                   # SPA shell: v4 badge in <title> and header, login/register views, data-testid attributes
│   └── app.js                       # UI logic: Budget card + Expenses table/modals + Journal section/view/edit/create/delete modals, formatCurrency, escapeHtml, showModalForm
├── data/
│   ├── trips.json                   # Created automatically; V1/V2/V3 → V4 field migration on first read (adds journal_entries=[])
│   └── users.json                   # Created automatically on startup from seed (password_hash only)
└── context/
    ├── Prompt 1 - Version 1.md                  # Original V1 specification
    ├── Prompt 2 - Authentication & User Accounts (Version 2).md   # V2 specification
    ├── Prompt 3 - Trip Costs & Budget Management (Version 3).md   # V3 specification
    └── Prompt 4 - Travel Journal (Version 4).md                   # V4 specification
```

## How to Reset Seed Data

The reset endpoint now **requires authentication**. After reset both user accounts and trip ownership are restored to the exact deterministic seed state (Alice=2 trips, Bob=1 trip, freshly-bcrypted password hashes).

### Option 1: Via the UI
Sign in as any user, then click the **Reset Data** button in the top-right header (visible only after login). A confirm-modal appears before the reset is sent.

### Option 2: Via the API
```bash
# First get a JWT:
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"Password123!"}' | jq -r .access_token)

# Then reset with the token:
curl -X POST http://localhost:8000/api/system/reset \
  -H "Authorization: Bearer $TOKEN"
```

Without the `Authorization: Bearer …` header the reset endpoint returns HTTP 401.

## Validation Rules

The application enforces the following validation rules (both client-side and server-side):

### Trip / Day / Activity (unchanged from V1)
- **Trip name**: Required, cannot be empty
- **Destination**: Required, cannot be empty
- **Start date**: Required
- **End date**: Required, cannot be earlier than start date
- **Day date**: Required
- **Activity name**: Required, cannot be empty

### New in V2 — User Account Rules
- **Full name**: Required, at least 1 char
- **Email**: Required, must be a valid RFC-5321 address (EmailStr validator)
- **Password**: Required, minimum 6 characters
- **Password confirmation**: Required, must exactly match the password
- **Duplicate email**: Register returns 409 Conflict if the email already exists in `data/users.json`
- **Authentication**: Login returns the exact generic message `"Invalid email or password."` for both unknown-email and wrong-password cases to prevent email-enumeration attacks

### New in V3 — Budget & Expense Rules

Every validation rule below is enforced both on the client (before the request is sent) and on the server (in `trip_service.py`). Server-side takes precedence and is authoritative.

**Expense Category & Currency Enum Rules**:
- Expense `category` MUST be one of: `Accommodation`, `Food`, `Transportation`, `Activities`, `Shopping`, `Other` (exact string, case-sensitive)
- Budget/Expense `currency` MUST be one of: `USD`, `EUR`, `GBP`, `ILS`, `VND`, `THB`, `JPY` (exact uppercase 3-letter ISO 4217 code)
- Values outside these sets fail Pydantic Literal validation (HTTP 422 from schema layer; HTTP 400 from service layer)

**Monetary Amount Rules**:
- Trip `budget`: Must be ≥ 0 (zero budget is valid — no spending allowed yet)
- Expense `amount`: Must be strictly > 0. An expense of 0.00 or a negative amount returns HTTP 400
- All amounts are rounded to 2 decimal places using `Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)` at persistence time to avoid float precision drift

**Currency Match Rule**:
- Expense `currency` MUST equal the parent trip's stored `currency` (e.g., if trip.currency = `JPY`, an expense with currency=`USD` returns 400 with explicit mismatch message)
- This rule is enforced on both `POST` create and `PUT` update paths; on update the check compares the *resulting* currency (update.currency if set, else existing.currency) against trip.currency

**Expense Date-Range Rule**:
- Expense `date` MUST fall within `[trip.start_date, trip.end_date]`, inclusive
- If trip.start = 2026-10-01 and trip.end = 2026-10-10, an expense date of 2026-09-30 or 2026-10-11 returns 400
- On `PUT` update, this check runs only when the `date` field is actually being changed (not passed / `None` → skipped)

**Authorization & Ownership**:
- Budget and expenses inherit ownership from their trip. A request for Bob to GET Alice's `trip-1` budget returns HTTP 403 (not 404)
- Similarly, requesting an expense_id that belongs to another user's trip returns 403; requesting an expense_id that simply does not exist returns 404

### New in V4 — Travel Journal Rules

Every rule below is enforced both on the client (in `app.js` before the fetch) and on the server (in `trip_service.py`). Server-side is authoritative. Error wording on both sides is kept byte-identical for test determinism.

**Journal Title Rules**:
- `title` is required on `POST` create; on `PUT` update, if omitted the existing value is retained
- Title cannot be empty or pure whitespace (`.strip()` length < 1 → HTTP 400 "Title is required")
- Title max length: **100 characters** (Pydantic `max_length=100` in schema + service-layer check; HTTP 400 "Title must be 100 characters or less")

**Journal Content Rules**:
- `content` is required on create; optional on update (retains existing if omitted)
- Content cannot be empty or pure whitespace (HTTP 400 "Content is required")
- Content max length: **5000 characters** (HTTP 400 "Content must be 5000 characters or less")
- Content is stored and rendered as **plain text only**. No markdown, no rich text, no HTML interpretation. Newlines (`\n`) are preserved in rendering via CSS `white-space: pre-wrap`; before DOM injection the string always passes through `escapeHtml()` to prevent XSS

**Journal Date Rules**:
- `date` is required on create; optional on update (retains existing if omitted)
- Date must be a valid ISO 8601 date (YYYY-MM-DD). Invalid strings fail Pydantic `date` coercion (HTTP 422)
- Date **MUST** fall within the parent trip's closed date window `[trip.start_date, trip.end_date]`, inclusive → HTTP 400 "Date must be within the trip date range"
- On `PUT` update, the date-range check runs **only** when the update body actually includes a `date` field (if `date` is `None` or omitted → skipped, preserving the existing date even if the trip window has changed)

**Timestamp Rules (server-only; not validated from client)**:
- `created_at` and `updated_at` are generated by the server using `datetime.utcnow().isoformat()` at write time
- Including `created_at` or `updated_at` in a `POST` body has **no effect** — the Pydantic `JournalEntryCreate` schema excludes them and the store overwrites them unconditionally
- On `PUT` update, only `updated_at` is refreshed; `created_at` is preserved verbatim (immutable after create)

**Authorization & Ownership**:
- All journal endpoints are protected with `Depends(get_current_user)` — a missing/invalid JWT returns HTTP 401 before any business logic runs
- Ownership is always resolved through the *trip* first: if the trip doesn't exist → 404; if the trip exists but `trip.user_id !== current_user.id` → 403
- Because journal entries are nested inside the trip in `trips.json`, deleting a trip via `DELETE /api/trips/{trip_id}` cascade-deletes all its journal entries automatically — there is no way for an orphan journal entry to exist
- Requesting an `entry_id` that does not exist on the given trip returns HTTP 404 ("Journal entry not found") — even if that `entry_id` happens to exist on a different trip owned by the same user (endpoint is scoped by `trip_id`)

## Automation-Friendly Design

The application is designed for automated testing:

- **Stable deterministic credentials**: Two fixed seed users with stable IDs and known passwords
- **Asymmetric ownership counts**: Alice (2 trips) vs Bob (1 trip) — any list-length test can immediately confirm correct filtering
- **404 vs 403 disambiguation**: Explicit, testable separation between "resource doesn't exist" and "resource isn't yours"
- **`data-testid` attributes** on every key interactive element:
  - Login form: `login-email`, `login-password`, `login-submit`, `login-form`, `login-error`
  - Register form: `register-fullname`, `register-email`, `register-password`, `register-confirm-password`, `register-submit`, `register-form`, `register-error`
  - Header: `logout`, `current-user-display`
  - Budget section: `budget-amount`, `budget-currency`, `budget-spent`, `budget-remaining`, `budget-over-budget`, `save-budget` (Edit Budget button)
  - Expenses section: `add-expense`, `expense-list`, `expense-row`, `edit-expense-btn`, `delete-expense-btn`; Expense form: `expense-description`, `expense-category`, `expense-amount`, `expense-currency`, `expense-date`, `save-expense` (submit)
  - **Journal section (NEW in V4)**:
    - Outer wrapper: `journal-section`
    - Add button: `add-journal-entry`
    - Per-card (in list): `journal-entry-card`, `journal-title`, `journal-date`, `journal-content-preview`
    - Per-card action icons: `edit-journal-entry`, `delete-journal-entry` (each uses `event.stopPropagation()` so the click doesn't also fire the parent card's "view" handler)
    - Create/Edit form fields: `journal-title` (text input), `journal-date` (date input), `journal-content` (textarea)
    - Create/Edit form submit button: `save-journal-entry`
    - View-modal edit shortcut: `journal-view-edit-btn`
  - All V1 trip/day/activity testids preserved unchanged
- **Predictable REST API with consistent JSON responses**
- **Deterministic reset endpoint**: Authenticated POST to `/api/system/reset` yields byte-identical seed state for both users and trips (including budget/currency/expenses AND journal entries)
- **IDs use a readable prefix pattern** (`trip-*`, `day-*`, `act-*`, `exp-trip*-*`, `user-*`, `je-*-*` for journal entries)
- **Transparent migration from V1/V2/V3 JSON**: Test suites can drop in a V3 `trips.json` and restart — missing `journal_entries` fields are injected with `[]` default values automatically
- **Newest-first sort is deterministic**: Journal list is sorted server-side as `(date DESC, created_at DESC)`, with a client-side defensive re-sort — for seed data with distinct dates (trip-1: 10-01, 10-02, 10-04) the order is always 10-04 → 10-02 → 10-01 top-to-bottom regardless of array order in storage
- **Empty-state coverage in seed data**: Bob's Tokyo Discovery (trip-2) intentionally has zero journal entries — tests can verify the "No journal entries yet. Add your first memory!" empty-state copy and hidden-row selectors work correctly without needing to manually delete entries first

## Future Versions (V5 and beyond)

This application will evolve in future versions to add:
- ✅ **User Registration and Login** — delivered in Version 2
- ✅ **Travel costs and budget management** — delivered in Version 3
- ✅ **Travel journal** — delivered in Version 4
- Mobile/responsive support
- SQLite database persistence (replacing the JSON persistence layer only)
- Third-party / external auth providers
- Maps integration
- AI-powered itinerary suggestions
- Payment / booking integrations
- Admin dashboard
- Additional QA/testing scenarios

The layered architecture is designed to support these additions with minimal changes to existing code — especially the persistence layer abstraction which will allow swapping JSON for a real database by touching only the `backend/app/data/` directory.
