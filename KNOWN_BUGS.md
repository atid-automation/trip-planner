# Known Bugs - Trip Planner v1

This document lists all confirmed bugs, validation gaps, and data integrity issues discovered in the Trip Planner application.

---

## Bug #1: Day Trip Can Be Added Outside the Trip's Date Schedule (No Validation)

**Severity:** High (Data Integrity)  
**Area:** Backend — Trip Day Creation / Update

**Description:**  
When creating or updating a Trip Day, the system does **not** validate that the day's `date` falls within the parent Trip's `start_date` and `end_date` range. This allows days to be scheduled weeks, months, or even years outside the trip's actual itinerary.

**Steps to reproduce:**
1. Create a Trip with `start_date=2026-10-01` and `end_date=2026-10-10`.
2. Call `POST /api/trips/{trip_id}/days` with `{"date": "2025-01-01"}` (nearly 2 years before the trip).
3. The day is created successfully with no error.

**Affected code locations:**
- [trip_store.py — create_day()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/app/data/trip_store.py#L152-L167) — No date-range check against trip.
- [trip_store.py — update_day()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/app/data/trip_store.py#L170-L183) — Same gap on update.
- [schemas.py — TripDayCreate / TripDayUpdate](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/app/models/schemas.py#L26-L38) — Pydantic models lack a date-range validator.
- [trip_service.py — create_new_day / update_existing_day](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/app/services/trip_service.py#L68-L82) — Service layer passes through without validation.
- [app.js — openDayForm() onSubmit](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/frontend/app.js#L536-L569) — Frontend also has no client-side date-range guard.

---

## Bug #2: Updating a Trip's Dates Does Not Validate Existing Days

**Severity:** High (Data Integrity)  
**Area:** Backend — Trip Update

**Description:**  
When a Trip's `start_date` or `end_date` is updated (narrowed), the system does **not** check whether existing Trip Days still fall inside the new date range. This silently produces orphaned days that are chronologically "outside" the trip.

**Steps to reproduce:**
1. Create a Trip `2026-10-01 → 2026-10-10` with a day on `2026-10-05`.
2. `PUT /api/trips/{id}` with `{"start_date": "2026-10-07", "end_date": "2026-10-10"}`.
3. The existing day `2026-10-05` now sits **before** `start_date` — no warning, no rejection.

**Affected code locations:**
- [trip_store.py — update_trip()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/app/data/trip_store.py#L107-L122) — Updates dates but never scans existing `days[]`.
- [trip_service.py — update_existing_trip()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/app/services/trip_service.py#L39-L43) — No validation hook.

---

## Bug #3: TripUpdate Validator Cannot See Existing Dates — Allows end_date < Current start_date

**Severity:** High (Validation Bypass)  
**Area:** Backend — Pydantic Schema

**Description:**  
The `TripUpdate` `end_date_after_start_date` field validator only inspects the **incoming** payload via `values.data.get("start_date")`. If the caller updates only `end_date` (leaving `start_date` out of the request), the validator sees `start_date=None` and **skips the check entirely**. This lets you set `end_date` to a value earlier than the **existing** trip's `start_date`.

**Steps to reproduce:**
1. Trip has `start_date=2026-10-01`, `end_date=2026-10-10`.
2. `PUT /api/trips/{id}` → `{"end_date": "2026-09-01"}` (no start_date sent).
3. Validator does not run → trip now has `end_date` 1 month **before** `start_date`.

The same issue exists when only updating `start_date` to a value later than the existing `end_date`.

**Affected code locations:**
- [schemas.py — TripUpdate.end_date_after_start_date](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/app/models/schemas.py#L69-L74) — Only checks payload values, not persisted trip.

---

## Bug #4: Duplicate Day Dates Allowed (No Uniqueness Constraint)

**Severity:** Medium (Data Quality)  
**Area:** Backend — Trip Day

**Description:**  
You can create any number of Trip Days with the **exact same `date`** within a single Trip. The system enforces no uniqueness, so users can end up with "Day 3" and "Day 4" both showing `2026-10-03` with different activity lists.

**Steps to reproduce:**
1. Create a Trip with any date range.
2. `POST /days` with `{"date": "2026-10-05"}` → succeeds.
3. Repeat `POST /days` with the same date → succeeds again (duplicate).

**Affected code locations:**
- [trip_store.py — create_day()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/app/data/trip_store.py#L152-L167) — Appends without checking `d["date"]` collision.
- [trip_store.py — update_day()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/app/data/trip_store.py#L170-L183) — Can update a day's date to collide with another existing day.

---

## Bug #5: Whitespace-Only Names Pass Backend Validation

**Severity:** Low to Medium (Data Quality)  
**Area:** Backend — Pydantic Schemas

**Description:**  
Pydantic's `min_length=1` on `Trip.name`, `Trip.destination`, and `Activity.name` accepts strings that contain **only whitespace** (e.g. `"   "`) because length is computed without stripping. The frontend trims inputs before sending, but a direct API caller can create records with invisible blank names.

**Affected code locations:**
- [schemas.py — TripBase](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/app/models/schemas.py#L45-L56) — `name` and `destination` use `min_length=1` without a strip pattern.
- [schemas.py — ActivityBase](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/app/models/schemas.py#L6-L10) — Same issue for `Activity.name`.

---

## Bug #6: JSON File Store — Race Condition on Concurrent Writes (Data Loss / Corruption)

**Severity:** High (Data Loss)  
**Area:** Backend — Data Persistence

**Description:**  
The JSON file store uses a naive **read → modify → write** pattern with **no file locking, no transactions, and no in-memory mutex**. Two concurrent API requests will interleave:

1. Request A reads `trips.json`.
2. Request B reads the same `trips.json`.
3. Request A writes its changes.
4. Request B writes its own copy (stale since step 2).

**Result:** Request A's changes are **permanently lost**. Under sufficient concurrency, partial writes can also corrupt the JSON file.

**Affected code locations:**
- [trip_store.py — _read_trips_file / _write_trips_file](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/app/data/trip_store.py#L24-L35) — No `fcntl` / `msvcrt` locking, no `threading.Lock`.
- Every mutating function (`create_trip`, `update_trip`, `delete_trip`, `create_day`, `update_day`, `delete_day`, `create_activity`, `update_activity`, `delete_activity`, `reset_to_seed_data`) is affected.

---

## Bug #7: /api/system/reset — No Authentication / No CSRF Guard — Anyone Can Wipe All Data

**Severity:** Critical (Security / Data Loss)  
**Area:** Backend — System Endpoint

**Description:**  
`POST /api/system/reset` is a **public, unauthenticated** endpoint that deletes every user's trip data and overwrites it with seed data. Combined with the permissive CORS policy (Bug #8), any third-party website can craft a cross-origin request to destroy all data while a user is logged in.

The endpoint also has no rate limiting.

**Affected code locations:**
- [system.py — reset_data()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/app/routers/system.py#L8-L10) — Zero authorization checks.
- [main.py — CORS allow_origins=["*"]](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/main.py#L15-L21) — Combined with Bug #8, enables trivial CSRF wipe.

---

## Bug #8: Overly Permissive CORS with Credentials

**Severity:** High (Security)  
**Area:** Backend — CORS Middleware

**Description:**  
FastAPI CORS middleware is configured with **both**:
- `allow_origins=["*"]` — **any** domain
- `allow_credentials=True` — cookies / auth headers allowed

This is a well-known dangerous combination. Browsers technically reject `Access-Control-Allow-Origin: *` when credentials are included, but the configuration still advertises intent to trust every origin. Cross-origin frontend apps (or malicious sites) can still hit read endpoints without credentials.

**Affected code locations:**
- [main.py — CORSMiddleware configuration](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/main.py#L15-L21)

---

## Bug #9: No Optimistic Concurrency / No Conflict Detection

**Severity:** Medium (Data Integrity)  
**Area:** Backend — All Update Endpoints

**Description:**  
None of the `PUT` endpoints (`/trips/{id}`, `/days/{id}`, `/activities/{id}`) implement any form of version check (ETag, `If-Match`, `updated_at` timestamp, etc.). If two users open the same trip and edit it simultaneously, the second save **silently overwrites** the first user's changes with no merge, conflict alert, or "stale edit" error.

**Affected code locations:**
- [trip_store.py — update_trip()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/app/data/trip_store.py#L107-L122)
- [trip_store.py — update_day()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/app/data/trip_store.py#L170-L183)
- [trip_store.py — update_activity()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/app/data/trip_store.py#L237-L254)

---

## Bug #10: Duplicate Activity Names Allowed Within a Day

**Severity:** Low to Medium (Data Quality / UX)  
**Area:** Backend — Activity Creation / Update

**Description:**  
Within a single Trip Day, multiple activities can share an identical `name`, `location`, and `description`. While not a hard error, this commonly indicates accidental double-entry — the system provides no guard or warning.

**Affected code locations:**
- [trip_store.py — create_activity()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/app/data/trip_store.py#L217-L234) — No dedupe check against existing activities on the day.
- [trip_store.py — update_activity()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v1/backend/app/data/trip_store.py#L237-L254) — Same gap on update.

---

## Summary Table

| # | Title | Severity | Category |
|---|-------|----------|----------|
| 1 | Day trip added outside trip schedule — no validation | High | Data Integrity |
| 2 | Trip date update doesn't check existing days | High | Data Integrity |
| 3 | TripUpdate validator bypassed when only one date sent | High | Validation Bypass |
| 4 | Duplicate day dates allowed per trip | Medium | Data Quality |
| 5 | Whitespace-only names pass backend validation | Low-Med | Data Quality |
| 6 | JSON store concurrent write race condition — data loss | High | Data Loss |
| 7 | `/api/system/reset` public wipe endpoint — no auth | Critical | Security |
| 8 | `allow_origins=["*"]` + `allow_credentials=True` CORS | High | Security |
| 9 | No optimistic concurrency — silent last-write-wins | Medium | Integrity/UX |
| 10 | Duplicate activity names within same day — no guard | Low-Med | Data Quality |
