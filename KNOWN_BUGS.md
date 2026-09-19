# Known Bugs - Trip Planner v2

This document lists all confirmed bugs, validation gaps, and data integrity issues discovered in the Trip Planner application. Bugs #1 through #10 originated in Version 1 and are still present in Version 2. Bugs #11 onwards are **new to Version 2** (introduced or exposed by the authentication, multi-user, JWT, and migration features).

---

## ⚠️ Status of V1 Bugs in V2

| Bug # | Title | Status in V2 | Notes |
|-------|-------|--------------|-------|
| 1 | Day date outside trip range — no validation | **Unchanged** | V2 auth scoping added, date-range check still missing |
| 2 | Trip date update doesn't revalidate existing days | **Unchanged** | Same data-integrity gap |
| 3 | `TripUpdate` validator bypassed when only one date field sent | **Unchanged** | Pydantic schema unchanged |
| 4 | Duplicate day dates per trip allowed | **Unchanged** | No uniqueness constraint added |
| 5 | Whitespace-only names pass backend validation | **Unchanged** | `min_length=1` still accepts `"   "` — also applies to new `User.full_name` and `Trip.name` / `Activity.name` |
| 6 | JSON store concurrent write race condition → data loss | **Worse** | Now affects **both** `trips.json` **and** `users.json` (see Bug #15) |
| 7 | `/api/system/reset` — public wipe endpoint, no auth | **Partially Resolved** | Now requires a valid JWT. However **any** authenticated user can still wipe the entire global state — see Bug #11. |
| 8 | `allow_origins=["*"]` + `allow_credentials=True` in CORS | **Unchanged (Active)** | Still dangerous; see Bug #19. |
| 9 | No optimistic concurrency / conflict detection | **Unchanged** | All PUT endpoints still last-write-wins |
| 10 | Duplicate activity names within same day allowed | **Unchanged** | No dedupe |

---

## Bug #11: `/api/system/reset` Still Wipes ALL Users' Data Globally — No Per-User Scope

**Severity:** High (Security / Data Loss)  
**Area:** Backend — System Endpoint + Reset Service Logic

**Description:**  
In V2 the reset endpoint is no longer *anonymous* (Bug #7 is partially closed). However, it still wipes **every user's data globally**: all custom registered accounts are deleted (only Alice + Bob are recreated), and all trips — including those owned by users other than the caller — are reverted to seed. In a multi-user app this means a single low-privilege user can destroy *everyone else's* accounts and itineraries. Reset should either (a) reset only the calling user's trips + account, or (b) require a separate admin role.

**Steps to reproduce:**
1. Register new user `eve@example.com` / create a trip.
2. Login as `bob@example.com` and click **Reset Data**.
3. Try to login as `eve@example.com` → fails (account wiped). Eve's trip is gone; Bob's Tokyo trip recreated.

**Affected code locations:**
- [trip_service.py — reset_seed_data()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/services/trip_service.py#L154-L156) — Calls BOTH `trip_store.reset_to_seed_data()` (wipes all trips) AND `auth_service.reset_users_to_seed()` (wipes ALL users back to 2 seed accounts)
- [auth_service.py — reset_users_to_seed()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/services/auth_service.py#L69-L78) — Overwrites users.json with only Alice + Bob, unconditionally removing every registered user
- [system.py — reset_data()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/routers/system.py#L10-L13) — No role check; accepts any valid JWT; `current_user` is injected but never used for scoping

---

## Bug #12: JWT SECRET_KEY Hardcoded in Source — Zero Secrets Rotation, Same Key Across All Installs

**Severity:** Critical (Security)  
**Area:** Backend — JWT Signing / Security Module

**Description:**  
The HS256 signing key used to mint and verify every JWT token is hardcoded as a plain string literal in `security.py` and committed to the repository. Because it never changes, every installed copy of the app uses the **same key**. Any attacker with repo read access can forge arbitrary JWTs (including spoofing `sub: "user-alice"` or any other user ID) and authenticate to *any* deployed instance. Additionally there is no key-rotation mechanism — once leaked, previously-issued tokens can never be revoked server-side (see also Bug #13).

**Recommendation:** Load `SECRET_KEY` from an environment variable, generate a random key on first launch if missing, and log a loud warning in development if the default is still in use.

**Affected code locations:**
- [security.py — SECRET_KEY constant](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/security.py#L11-L13) — The literal string is in source code and returned directly to `jwt.encode` / `jwt.decode`

---

## Bug #13: JWT Tokens Are Server-Irrevocable and Valid for Full 24 Hours (No Refresh, No Logout, No Idle Timeout)

**Severity:** High (Security)  
**Area:** Backend — Session / Token Lifecycle + Frontend — Logout

**Description:**  
A JWT once issued is trusted until its `exp` claim — set to **24 hours after login** — regardless of any server-side state. This has three concrete consequences:

1. **Logout is client-side only.** The "Logout" button in the header simply calls `clearAuth()` which removes the token from `localStorage`. The server has no token-blacklist and never learns about logout. If the JWT was captured (e.g. via XSS, logs, or shoulder-surfed from localStorage), it remains usable for up to 24 hours even after the user clicked Logout.
2. **No idle-time-based expiry.** A token issued Monday 10am works Tuesday 9:59am regardless of whether the user has been idle for 23.9 hours.
3. **No refresh-token rotation.** If a user stays signed in for 24h and 1 minute, they will be forcibly signed out with no graceful way to renew the token without retyping credentials.

**Affected code locations:**
- [security.py — create_access_token()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/security.py#L30-L38) — Fixed 24h exp, no `iat`, no `jti` (token ID for blacklist)
- [frontend/app.js — clearAuth() + Logout handler](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/frontend/app.js#L38-L40) — No server-side revocation, purely removes localStorage keys
- [frontend/app.js — apiRequest() 401 handler](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/frontend/app.js#L108-L133) — No refresh path, only clear-and-error

---

## Bug #14: No Rate Limiting or Account Lockout on Login/Register — Trivial Brute Force and Email Enumeration

**Severity:** High (Security)  
**Area:** Backend — Authentication Endpoints

**Description:**  
Both `POST /api/auth/login` and `POST /api/auth/register` accept unlimited requests per IP / per email with zero delay, zero captcha, zero account lockout, and zero per-IP throttling. An attacker can:

- **Brute-force passwords** against any known account (e.g., `alice@example.com`) at line speed. bcrypt (12 rounds by default in passlib) provides ~some~ protection, but against the seed users with password `Password123!` a determined attacker will find the match, and there is nothing to slow them down at the network/app layer.
- **Enumerate registered emails** using the registration endpoint: even though the login endpoint correctly uses a generic 401 (per Bug #21 below), the *registration* endpoint returns a clear **409 Conflict** for an existing email and **201 Created** for a new one — a trivial oracle. Combined with no rate-limit, the attacker can sweep a dictionary of emails against `/register`.

**Affected code locations:**
- [auth.py — login()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/routers/auth.py#L22-L27) — No throttle/lockout before or after `login_user` call
- [auth.py — register()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/routers/auth.py#L12-L19) — 409 status leaks "Email already exists"; no throttling
- No rate-limiting middleware in [main.py](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/main.py) at all

---

## Bug #15: Concurrent Write Race Condition Now Affects `data/users.json` Too → Duplicate-Email Account Creation Possible

**Severity:** Critical (Data Integrity + Security)  
**Area:** Backend — Persistence (user_store.py)

**Description:**  
This is Bug #6 applied to the new V2 users.json persistence layer. `user_store.create_user` / `create_user_from_dict` / `reset_users` all use the same naive read-modify-write pattern:
```
_read_users_file() → append to list → _write_users_file()
```
with **no file locking, no threading.Lock, and no transaction**. Two near-simultaneous `POST /api/auth/register` calls with the **same email** can interleave as follows:

1. Request A calls `email_exists()` → False (no user yet).
2. Request B calls `email_exists()` → False (same empty file).
3. Both A and B proceed to `_read_users_file()` (both get `[]`), append their copy, and `_write_users_file()`.
4. **Result:** `users.json` contains **two rows with identical emails** (possibly different passwords, same case).

Because `get_user_by_email` returns the **first** match (line 62-63 iterates and breaks), subsequent logins will authenticate against whichever record the iteration finds first — silently losing access to the other account's data. Combined with the V1 race in trips.json, under any concurrent load the app can silently lose account data.

**Affected code locations:**
- [user_store.py — _read_users_file / _write_users_file](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/data/user_store.py#L19-L30) — No locking mechanism at all
- [user_store.py — create_user()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/data/user_store.py#L80-L91) — `email_exists` check and file-write are not atomic; no post-write re-read
- [user_store.py — create_user_from_dict()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/data/user_store.py#L94-L98) — Same pattern, called from `ensure_seed_users` startup hook (if two workers launch they can both seed)

---

## Bug #16: Email Normalization Race — Register Email Case-Sensitive But Login Case-Insensitive → Duplicate Accounts + Shadowed Logins

**Severity:** Medium-High (Data Integrity + Auth Confusion)  
**Area:** Backend — Email Normalization (auth_service + user_store)

**Description:**  
There is an asymmetry in how email case is handled:

- **At registration** (`register_user` → `email_exists` → `get_user_by_email` → `.lower()`): comparison is case-insensitive on the **read side**, but when the record is eventually **written** it uses whatever case the user typed in the form. This in itself is fine.
- **The race window:** Because `user_store.create_user` never performs a **post-write uniqueness check/re-read**, and because of Bug #15's concurrent write gap, the following (adversarial) scenario works reliably:
  1. Attacker registers `Alice@Example.com` → succeeds because before-write `.lower()` finds no match (if only `alice@example.com` exists the lowercase comparison **catches** it — good).
  2. BUT: if two sequential concurrent regs race at microsecond scale (see Bug #15): Request 1's `email_exists()` returns False, Request 2's `email_exists()` also returns False, Request 3's `email_exists()` returns False, all 3 are written. `users.json` will contain rows `alice@example.com`, `Alice@example.com`, `ALICE@EXAMPLE.COM` (each with different password hashes).
  3. Now when a real Alice logs in with the email `alice@example.com` and *her* password, `get_user_with_password` iterates and returns the **first** matching row based on `.lower()` — depending on file order, Alice may or may not be able to sign in with her password (she will only match the hash stored against the first match). She has no way to tell which account she logged into; the `user.id` returned will be one of the 3 `user-{uuid}` IDs at random.

This also exists even without race: if an admin directly edits `users.json` to add two rows with same email different case, login becomes non-deterministic.

**Affected code locations:**
- [user_store.py — get_user_with_password()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/data/user_store.py#L67-L73) — Iterates and returns first case-insensitive match; no check for duplicates
- [user_store.py — create_user()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/data/user_store.py#L80-L91) — Does NOT normalize email to lowercase before writing
- [auth_service.py — ensure_seed_users()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/services/auth_service.py#L54-L66) — Compares lowercase for existence check but writes seed `email` with the original casing (fine for seeds, but the pattern is the same as the registration race)

---

## Bug #17: V1→V2 Migration Function Is Called INSIDE `_read_trips_file` → Infinite Rewrite Loop If `SEED_TRIPS` Ever Lacks `user_id`

**Severity:** Medium-High (Data Integrity / Performance Degradation)  
**Area:** Backend — Data Migration (trip_store.py)

**Description:**  
`_read_trips_file` → `json.load` → `_migrate_trips_if_needed(data)` → if any trip lacks `user_id`, patch and **immediately call `_write_trips_file(data)`**, then return `data` to caller.

The code currently works because `SEED_TRIPS` (in `seed_data.py`) has been hand-patched to include `user_id` keys, and `reset_to_seed_data()` writes the fully-populated dict. But consider any of these future/edge cases:

1. **If someone edits `seed_data.py` and forgets `user_id` in one of the 3 SEED_TRIPS entries**, `reset_to_seed_data` writes the bad JSON, then on the *next* API call `_read_trips_file` detects the missing key, re-assigns it, re-writes. But next `reset_to_seed_data` overwrites with the bad version again. Result: on **every API call** that reads trips we pay an extra disk write — a file-trash loop.
2. **If the disk fills up during `_write_trips_file(data)` inside the migration**, `_migrate_trips_if_needed` will raise an uncaught `OSError`. Since migration happens inside `_read_trips_file`, **read operations now have a write-path side effect that can fail** — every trip-reading endpoint (including `GET /api/trips`, which callers expect to be safe/idempotent) will 500 on a read-only request just because a write failed.
3. **Migration never verifies it succeeded.** After write, code does not re-read the file; it simply returns the mutated in-memory list. If `_write_trips_file` silently truncated the JSON (partial write), the caller will not see the mismatch until the next restart.

**Affected code locations:**
- [trip_store.py — _read_trips_file](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/data/trip_store.py#L26-L33) — Read function has side-effect write; no write-error protection
- [trip_store.py — _migrate_trips_if_needed](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/data/trip_store.py#L42-L50) — Writes immediately without wrapping in try/except; no post-write verification; no version flag (e.g. `schema_version`) to prevent reruns

---

## Bug #18: Frontend Never Re-Hydrates `currentUserData` from `/api/auth/me` Response → Stale Full-Name Display After Server-Side Profile Change

**Severity:** Low-Medium (UX / Cache Staleness)  
**Area:** Frontend — Bootstrap Auth Flow

**Description:**  
On `DOMContentLoaded`, if a token is already present in `localStorage`, the frontend calls:
```js
await apiRequest('/api/auth/me');
```
and then proceeds to `renderTripsList()`. But the returned user object — which contains the **latest** server-side `full_name` and `email` — is **discarded**. The code keeps using the stale `currentUserData` JSON that was saved to `localStorage` at the moment of the original login.

If a user were renamed server-side (e.g. through a `/PUT /api/auth/me` endpoint added later, or by directly editing `users.json` on disk), the header `#current-user-display` will keep showing the old name until the user logs out and back in again — a **clear inconsistency with server state** that persists for up to 24 hours (Bug #13's token lifetime).

Note: The app currently has **no update-profile endpoint**, so this is a latent bug exposed by the current architecture. But even editing `users.json` manually produces the stale UI.

**Affected code locations:**
- [frontend/app.js — DOMContentLoaded boot](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/frontend/app.js#L997-L1009) — The awaited result of `apiRequest('/api/auth/me')` has its `data` thrown away; `setAuth` is never called to refresh the in-memory `currentUserData` + `localStorage.USER_KEY` copy
- Compare login handler [frontend/app.js line 219-222](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/frontend/app.js#L218-L223) — correctly calls `setAuth(data.access_token, data.user)` after login, but boot has no equivalent refresh

---

## Bug #19: `allow_origins=["*"]` + `allow_credentials=True` + JWT in Auth Header → Credentialed Cross-Origin Reads Still Possible via CORS Misconfiguration

**Severity:** High (Security)  
**Area:** Backend — CORS Middleware

**Description:**  
V2 inherited the V1 CORS setup unchanged. Browsers *should* refuse `Access-Control-Allow-Origin: *` when credentials are involved, but the configuration is still dangerous:

1. The middleware still advertises `"*"` origins. In many CDN / WAF / proxy configurations this silently gets "reflected" back as the caller's actual Origin (because some implementations treat `*` plus `credentials` as "reflect the Origin header"), enabling cookie/header read on arbitrary sites.
2. Even without credential reflection, a **read-only non-credentialed cross-origin** request from an attacker's site can still reach all public read endpoints that don't require Authorization headers — specifically `/api/health` and the `GET /docs` OpenAPI schema. That's not catastrophic, but combined with Bug #14 it gives the attacker one more path to confirm the app is alive before probing `/register` email enumeration.
3. Critically: since the **JWT is in the `Authorization: Bearer…` header** (NOT in a cookie), the browser's "block credentials when ACAO is *" rule is not actually engaged for a manually-built `fetch`/`XMLHttpRequest` that manually sets the Authorization header. If an attacker can trick an authed user into executing JS on another origin (e.g., via DNS rebind, MITM on non-HTTPS localhost, or browser extension with broad host permissions), they can trivially set `Authorization` header manually and bypass the rule entirely. CORS was never designed to protect headers a script itself controls. This is not CORS's job — but it is made **strictly worse** by advertising `allow_origins=["*"]`, because developers or reverse proxies may then assume that any origin is intentional.

Recommendation for V3+: set `allow_origins` explicitly to `["http://localhost:8000", "http://127.0.0.1:8000"]` for dev, and add no wildcard origins when credentials/auth headers are in use.

**Affected code locations:**
- [main.py — CORSMiddleware](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/main.py#L16-L22) — Same insecure combo unchanged from V1

---

## Bug #20: Register + Login Have No Input-Length Upper Bounds — bcrypt Truncation Attack Surface + Disk-DoS

**Severity:** Medium (Security + Availability)  
**Area:** Backend — User Schemas + Persistence

**Description:**  
The Pydantic schemas set `password: str = Field(..., min_length=6)` with no `max_length`. The password is then fed directly to `pwd_context.hash(password)` (bcrypt). **bcrypt has a hard 72-byte input limit** — bytes beyond the 72nd are silently ignored. Two attack surfaces result:

1. **Truncation collision:** If a user registers with 80-byte password `A…ABBBB`, then tries to log in with a 72-byte password consisting of just the first 72 bytes of `A…A`, bcrypt will accept it. This is a known bcrypt property and is acceptable only if the application normalizes inputs. Our app does not cap, does not pre-hash, and provides no warning.
2. **Disk DoS:** `full_name` also has no `max_length`. A `UserCreate` with `full_name` = 10 MB of unicode characters and `password` = 10 MB string will be validated by Pydantic as a valid string, sent to `hash_password`, and both fields persisted to `users.json`. bcrypt will hash megabytes blocking the event loop for seconds and thrashing CPU; then a ~10 MB JSON record is appended to `users.json`. With no rate limit (Bug #14) this is a cheap storage / CPU exhaustion attack.

**Affected code locations:**
- [schemas.py — UserCreate.password](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/models/schemas.py#L94-L106) — No `max_length` on password, password_confirmation, full_name, email
- [schemas.py — UserBase.full_name](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/models/schemas.py#L86-L91) — No max_length
- [security.py — hash_password()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/security.py#L19-L21) — No length check before `pwd_context.hash`

---

## Bug #21: Login 401 Message Generic — BUT Register 409 IS an Email-Enumeration Oracle (Residual Side Channel)

**Severity:** Medium (Privacy / Info Disclosure)  
**Area:** Backend — Auth Endpoints

**Description:**  
Good news: the login endpoint correctly uses a single generic message `"Invalid email or password."` for both wrong-password AND nonexistent-email, so `/login` alone cannot enumerate emails. However, the `/register` endpoint returns clearly distinguishable responses:

- Email **not** registered → HTTP **201 Created** (and actually stores the user)
- Email **already** registered → HTTP **409 Conflict** with body `{"detail": "Email already exists"}`

Because there is **no rate limiting** (Bug #14) and registration itself is a public unauthenticated endpoint, any attacker can enumerate registered emails at line speed. The mitigation usually used here is to always return the same public-facing "If your email is not registered, we have sent a confirmation link" for both paths — but our app uses in-band signaling (409 vs 201) as the UX flow.

**Affected code locations:**
- [auth.py — register() 409 status](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/routers/auth.py#L12-L19) — Clear 201 vs 409 divergence
- [auth.py — login() 401 status](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/routers/auth.py#L22-L27) — Correct: identical error message regardless of which branch failed

---

## Bug #22: `trip_service` Performs 2 Uncoordinated `_read_trips_file()` Disk Reads Per Sub-Resource Request — Torn-Read Races Possible

**Severity:** Medium (Data Integrity + Resource Waste)  
**Area:** Backend — Trip Service Layer + Trip Store Interaction Pattern

**Description:**  
The `_get_trip_or_error(trip_id, user)` helper does:
```python
owner = trip_store.get_trip_owner(trip_id)   # FIRST disk read of trips.json
...
trip  = trip_store.get_trip_by_id(trip_id, user.id) # SECOND disk read of trips.json
```
Each call is a full `json.load()` from disk with **no lock, no cache, no transaction context shared between the two calls**. This creates a torn-read race:

- Between the owner check (call 1) and the get-trip check (call 2), another concurrent writer can `DELETE`/`update_trip`/`reset_to_seed_data` the trips file.
- Result A: `get_trip_owner` returns "alice owns trip-2"; then a reset runs; then `get_trip_by_id` reads the new seed trips file and re-checks user_id == alice. This case is "fine" (correct 404 if trip gone, correct 403 if user mismatch) but wastes CPU re-parsing a ~1300 line JSON file twice per API call — sub-resource endpoints (`POST /api/trips/{id}/days/{id}/activities/{id}`) end up parsing `trips.json` **3 or even 4 times** per request because the service layer calls `_get_trip_or_error` AND then trip_store's get_day_by_id AND then trip_store's delete_activity / etc each re-read the file separately.
- Result B (bad): Owner check returns `None` (trip doesn't exist → would be 404) but between calls a writer creates the trip for another user under the same ID; subsequent reads now see owner != user → 403. This is arguably still "secure" (403 better than 404 leak), but semantically wrong for API callers that are polling / watching a resource, and impossible to document consistently.

**Affected code locations:**
- [trip_service.py — _get_trip_or_error](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/services/trip_service.py#L29-L38) — Back-to-back store calls without shared data context
- [trip_service.py — list_days / get_day / update_day / delete_day / list_activities etc](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/services/trip_service.py#L68-L152) — All sub-resource methods call `_get_trip_or_error` once then call the store AGAIN with user_id, incurring at least double parse

---

## Bug #23: Password-Confirmation Field Is NOT Sent Over the Wire (UX Edge Case)

**Wait — no.** The frontend DOES send `password_confirmation` in the register body. However, note the following known **UX-only** caveat: **The backend does not strip/redact `password` and `password_confirmation` from the FastAPI error body when schema validation fails (422).** For example, if you register with `password="123"` (too short), the raw `loc`, `input` values in Pydantic's 422 error **include the literal passwords the user typed**, and the frontend passes that raw `detail` straight to `renderRegister → register-error-general` text box AND to `showToast`. If a user is using a shared screen/projector/recording, their intended password appears on-screen in plaintext as part of the validation error.

**Severity:** Low-Medium (UX / Shoulder-Surfing Privacy)  
**Area:** Backend → Frontend Error Rendering

**Affected code locations:**
- [frontend/app.js — Register submit catch block](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/frontend/app.js#L312-L322) — `err.message` (which can contain the `data.detail` Pydantic 422 error with nested `input` password fields) is written verbatim to DOM innerHTML and shown in toast
- [schemas.py — UserCreate class](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v2/backend/app/models/schemas.py#L94-L106) — No `json_schema_extra` / Field masking directive; FastAPI echoes the invalid values on 422

---

## Summary Table (V1 + V2 Bugs Combined)

| # | Title | Severity | Category | App Version |
|---|-------|----------|----------|-------------|
| 1 | Day date outside trip schedule — no validation | High | Data Integrity | V1, V2 |
| 2 | Trip date update doesn't check existing days | High | Data Integrity | V1, V2 |
| 3 | `TripUpdate` validator bypass when only one date sent | High | Validation Bypass | V1, V2 |
| 4 | Duplicate day dates allowed per trip | Medium | Data Quality | V1, V2 |
| 5 | Whitespace-only names pass backend validation | Low-Med | Data Quality | V1, V2 |
| 6 | JSON store concurrent write race (trips.json) — data loss | High | Data Loss | V1, V2 |
| 7 | `/api/system/reset` public wipe endpoint (v1) | **Critical** → Partial Fix in V2 | Security | V1: Critical, V2: See Bug #11 |
| 8 | `allow_origins=["*"]` + `allow_credentials=True` CORS | High | Security | V1, V2 → see also #19 |
| 9 | No optimistic concurrency — silent last-write-wins | Medium | Integrity/UX | V1, V2 |
| 10 | Duplicate activity names within same day — no guard | Low-Med | Data Quality | V1, V2 |
| **11** | **Reset endpoint wipes *all users* globally — any authed user can destroy others' accounts** | **High** | Security / Data Loss | **V2 ONLY** |
| **12** | **JWT SECRET_KEY hardcoded in repo — same key on every install, forgeable tokens** | **Critical** | Security | **V2 ONLY** |
| **13** | **JWT tokens irrevocable for 24h — Logout is client-only; no refresh / idle timeout** | **High** | Security / Session | **V2 ONLY** |
| **14** | **No rate-limiting / lockout on login + register → brute force + email enumeration** | **High** | Security | **V2 ONLY** |
| **15** | **users.json concurrent write race → duplicate-email accounts possible** | **Critical** | Integrity + Security | **V2 ONLY** |
| **16** | **Email case asymmetry — register case-write but login case-i compare + #15 → non-deterministic login** | **Medium-High** | Integrity / Auth | **V2 ONLY** |
| **17** | **Migration called inside read → extra disk write on every GET if seed trips ever lack user_id; read ops have write-side-effect failure paths** | **Medium-High** | Performance + Integrity | **V2 ONLY** |
| **18** | **Frontend boot /me response discarded → stale full_name display after server profile change** | **Low-Med** | UX / Cache Staleness | **V2 ONLY** |
| **19** | **Permissive CORS + JWT-in-header combination → manual-Auth-header cross-origin reads not blocked by browsers** | **High** | Security | **V2 ONLY (escalated by JWT auth)** |
| **20** | **No max_length on password, full_name → bcrypt truncation + CPU / disk DoS** | **Medium** | Security + Availability | **V2 ONLY** |
| **21** | **Register 201 vs 409 is a public email-enumeration oracle (no rate-limit, Bug #14, amplifies it)** | **Medium** | Privacy / Disclosure | **V2 ONLY** |
| **22** | **Double file-reparse per sub-resource API call in _get_trip_or_error → torn read races + 2–4x JSON loads per request** | **Medium** | Performance + Integrity | **V2 ONLY (pattern amplified by ownership lookups)** |
| **23** | **Failed 422 registration echoes user's raw password input value into error shown in DOM/toast → shoulder-surf** | **Low-Med** | UX Privacy | **V2 ONLY** |
