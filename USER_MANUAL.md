# Trip Planner MVP v2 — User Manual

A complete guide to using the Trip Planner web application.

**Version 2** adds **user accounts, secure login/registration, JWT authentication, and per-user trip ownership**. Every trip now belongs to a specific user; users can only see and modify their own itineraries.

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

| Name         | Email                 | Password        | Sample Trips Owned (after reset)                              |
|--------------|-----------------------|-----------------|----------------------------------------------------------------|
| Alice Smith  | `alice@example.com`   | `Password123!`  | 2 trips — Vietnam Adventure + European Backpacking            |
| Bob Johnson  | `bob@example.com`     | `Password123!`  | 1 trip — Tokyo Discovery                                      |

> **Tip:** Use Alice to test features that require multiple existing itineraries, and Bob to test isolation.

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

After reset, the following trips are available (ownership is intentionally asymmetric):

| # | Trip Name              | Destination | Dates                | Owner   | Notable Itinerary                                                                         |
|---|------------------------|-------------|----------------------|---------|-------------------------------------------------------------------------------------------|
| 1 | Vietnam Adventure      | Vietnam     | Oct 1–10, 2026       | Alice   | Day 1: Arrival in Hanoi; Day 2: Ha Long Bay Cruise; Day 3: Hanoi → Da Nang flight, ...   |
| 2 | Tokyo Discovery        | Japan       | Nov 15–22, 2026      | Bob     | Day 1: Shibuya Crossing; Day 2: Senso-ji Temple / Asakusa, ...                            |
| 3 | European Backpacking   | Europe      | May 1–14, 2027       | Alice   | Empty itinerary (ready for you to build!)                                                 |

---

## Data Storage

All data is saved as two human-readable JSON files in the project-root `data/` directory. **Files are created automatically — you never need to create them manually.**

```
data/
├── trips.json     # All trips, days, activities + user_id ownership
└── users.json     # User accounts (email, full_name, + bcrypt password_hash)
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

Both JSON files are fully portable across machines and operating systems as long as both Trip Planner installs are the same major version.

**Migration note when moving V1 → V2:** If you copy a legacy V1 `trips.json` (which lacks `user_id` fields) into a V2 project's `data/` folder, the V2 app will **automatically migrate it on first read** — every trip gets assigned to Alice by default (with seed trip IDs mapped per the ownership table), and the file is written back with `user_id` injected. No manual JSON editing is required.

---

## Validation Rules

The application enforces the following rules. Validation is performed in both the browser (client-side, for UX) and on the server (server-side, which always takes precedence).

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

### Days
- **Date:** Required

### Activities
- **Activity Name:** Cannot be empty

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

*Version 2.0.0 — Trip Planner MVP with User Accounts & JWT Authentication*
