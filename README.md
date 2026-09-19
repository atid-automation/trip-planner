# Trip Planner MVP (Version 2)

A small, simple Trip Planner web application built as the foundation for a Test Automation Engineering training course.

## Application Description

The Trip Planner allows users to create and manage travel itineraries. Each itinerary (trip) contains a name, destination, date range, and a set of days, each of which can have multiple activities/attractions.

**Version 2** extends Version 1 by adding **user accounts, secure registration/login, JWT-based authentication, and per-user trip ownership scoping**. All existing Version 1 trip/day/activity functionality is preserved — every operation is simply now guarded by authentication and scoped to the signed-in user.

This is intentionally small, simple, and deterministic, designed for easy testing and future extension.

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

| Name         | Email                 | Password        | Number of Trips | Owned Itineraries                          |
|--------------|-----------------------|-----------------|-----------------|--------------------------------------------|
| Alice Smith  | alice@example.com     | `Password123!`  | 2               | Vietnam Adventure, European Backpacking   |
| Bob Johnson  | bob@example.com       | `Password123!`  | 1               | Tokyo Discovery                           |

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

### System

| Method | Endpoint               | Description                                                                                |
|--------|------------------------|--------------------------------------------------------------------------------------------|
| POST   | `/api/system/reset`    | Reset **both** users and trips back to seed state. Requires authentication (any logged-in user may invoke it). |
| GET    | `/api/health`          | Unauthenticated health check. Returns `{"status":"ok","version":"2.0.0"}`.               |

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

**File 1 — `data/trips.json`**: Holds all itineraries (trip + nested days + nested activities). Every trip object carries a `user_id` field linking it to the owning user in `data/users.json`.

**File 2 — `data/users.json`**: Holds user accounts. Each user object contains a `password_hash` field with a bcrypt `$2b$` adaptive hash. The literal plaintext password is **never** written to disk, logged, or returned by any API.

The persistence layer (`backend/app/data/trip_store.py` + `backend/app/data/user_store.py`) fully abstracts all read/write operations. API routes and business logic never touch JSON files directly.

### Trip Ownership & Migration

- **V1 migration (automatic)**: If the app first loads a legacy V1 `trips.json` where any trip dict lacks a `user_id` field, the store immediately assigns ownership via the seed assignment map (trip-1→Alice, trip-2→Bob, trip-3→Alice; unknown IDs default to Alice) and rewrites the file. This migration runs exactly once.
- **Identity never trusted from client**: When a user creates a new trip, `user_id` is injected by the server from the JWT subject claim — a client body cannot spoof ownership by including `user_id` in JSON.
- **Isolation invariant**: The service layer pre-looks-up a trip's owner before every sub-resource call. If owner is `None` → 404; if owner ≠ current JWT user → 403. This ensures every endpoint correctly disambiguates 403 vs 404.

### Trip JSON Model (V2, note new `user_id`):

```json
{
  "id": "trip-1",
  "user_id": "user-alice",
  "name": "Vietnam Adventure",
  "destination": "Vietnam",
  "start_date": "2026-10-01",
  "end_date": "2026-10-10",
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
trip-planner-v2/
├── backend/
│   ├── main.py                      # FastAPI app v2.0.0 entry point + startup seed hook
│   ├── requirements.txt             # Python deps (adds bcrypt/passlib/python-jose/email-validator)
│   └── app/
│       ├── security.py              # NEW: JWT encode/decode, bcrypt, get_current_user Depends
│       ├── models/
│       │   └── schemas.py           # Pydantic models: Trip (+user_id), Day, Activity, User, UserCreate, UserLogin, Token
│       ├── services/
│       │   ├── trip_service.py      # Business logic (now user-aware; NotAuthorizedError for 403)
│       │   └── auth_service.py      # NEW: register, login, ensure_seed_users, reset_users_to_seed
│       ├── data/
│       │   ├── trip_store.py        # Persistence: user_id filter, owner lookup, V1 migration
│       │   ├── user_store.py        # NEW: Persistence for data/users.json (password_hash internal only)
│       │   └── seed_data.py         # SEED_USERS list + SEED_TRIP_USER_ASSIGNMENTS map + trip dicts with user_id injected
│       └── routers/
│           ├── trips.py             # Trip CRUD (Depends(get_current_user), catches NotAuthorizedError→403)
│           ├── days.py              # Day CRUD (same auth + ownership pattern)
│           ├── activities.py        # Activity CRUD (same)
│           ├── auth.py              # NEW: /register, /login, /login/form, /me
│           └── system.py            # /reset (now auth-protected; resets both stores)
├── frontend/
│   ├── index.html                   # SPA shell: login/register views + user-aware header, data-testid attributes
│   └── app.js                       # UI logic: JWT in localStorage, apiRequest wrapper injects Bearer, 401 handler redirects to Login, view guards
├── data/
│   ├── trips.json                   # Created automatically; migrated from V1 if needed
│   └── users.json                   # Created automatically on startup from seed (password_hash only)
└── context/
    ├── Prompt 1 - Version 1.md      # Original V1 specification
    └── Prompt 2 - Authentication & User Accounts (Version 2).md  # V2 specification
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

## Automation-Friendly Design

The application is designed for automated testing:

- **Stable deterministic credentials**: Two fixed seed users with stable IDs and known passwords
- **Asymmetric ownership counts**: Alice (2 trips) vs Bob (1 trip) — any list-length test can immediately confirm correct filtering
- **404 vs 403 disambiguation**: Explicit, testable separation between "resource doesn't exist" and "resource isn't yours"
- **`data-testid` attributes** on every key interactive element:
  - Login form: `login-email`, `login-password`, `login-submit`, `login-form`, `login-error`
  - Register form: `register-fullname`, `register-email`, `register-password`, `register-confirm-password`, `register-submit`, `register-form`, `register-error`
  - Header: `logout`, `current-user-display`
  - All V1 trip/day/activity testids preserved unchanged
- **Predictable REST API with consistent JSON responses**
- **Deterministic reset endpoint**: Authenticated POST to `/api/system/reset` yields byte-identical seed state for both users and trips
- **IDs use a readable prefix pattern** (`trip-*`, `day-*`, `act-*`, `user-*`)
- **Transparent migration from V1 JSON**: Test suites can drop in a V1 `trips.json` and restart without any schema editing

## Future Versions (V3 and beyond)

This application will evolve in future versions to add:
- ✅ **User Registration and Login** — delivered in Version 2
- Travel costs and budget management
- Travel journal
- Mobile/responsive support
- SQLite database persistence (replacing the JSON persistence layer only)
- Third-party / external auth providers
- Maps integration
- AI-powered itinerary suggestions
- Payment / booking integrations
- Admin dashboard
- Additional QA/testing scenarios

The layered architecture is designed to support these additions with minimal changes to existing code — especially the persistence layer abstraction which will allow swapping JSON for a real database by touching only the `backend/app/data/` directory.
