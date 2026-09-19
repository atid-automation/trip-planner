# Known Bugs - Trip Planner v4

This document lists all confirmed bugs, validation gaps, and data integrity issues discovered in the Trip Planner application. Bugs #1 through #23 originated in Version 1 or Version 2 and are still present in Version 4. Bugs #24 through #40 are **new to Version 3** (budget management, expense ledger, currency enforcement). Bugs #41 onwards are **new to Version 4** (introduced or exposed by the Travel Journal CRUD subsystem and related frontend sections).

---

## ⚠️ Status of V1, V2 & V3 Bugs in V4

| Bug # | Title | Status in V4 | Notes |
|-------|-------|--------------|-------|
| 1 | Day date outside trip range — no validation | **Unchanged** | V3 added date-range enforcement for *expenses*; V4 added same enforcement for *journal entries* — but days themselves still accept any date (Bug #35 + Bug #46 amplifications still apply) |
| 2 | Trip date update doesn't revalidate existing days | **Worse in V4** | Editing trip start/end can also invalidate already-persisted expenses AND journal entries silently; see Bug #28 and new V4 Bug #46 |
| 3 | `TripUpdate` validator bypassed when only one date field sent | **Unchanged** | |
| 4 | Duplicate day dates per trip allowed | **Unchanged** | |
| 5 | Whitespace-only names pass backend validation | **Worse in V4** | Now also applies to `Expense.description` AND `JournalEntry.title`/`JournalEntry.content` (min_length=1 accepts `"   "`) — journal has service-layer guards, schema layer still porous (Bug #41) |
| 6 | JSON store concurrent write race condition → data loss | **Worse in V4** | Still affects trips.json; concurrent journal + expense writes → 2× more write windows can clobber each other or lose recently-added days/activities/entries (Bug #52 amplifies) |
| 7 | `/api/system/reset` — wipe endpoint requires auth but still global | **Unchanged** | Still wipes *all* users globally (Bug #11); also wipes all custom journal entries back to seed |
| 8 | `allow_origins=["*"]` + `allow_credentials=True` in CORS | **Unchanged (Active)** | |
| 9 | No optimistic concurrency / conflict detection | **Worse in V4** | Budget PUT + Expense CRUD + Journal CRUD all use last-write-wins; 2 clients editing expenses AND journals concurrently silently corrupt totals + entry order |
| 10 | Duplicate activity names within same day allowed | **Unchanged** | |
| 11 | Reset wipes *all users* globally — any authed user destroys others' data | **Unchanged** | Also now wipes all custom budgets/expenses/journal entries back to seed |
| 12 | JWT SECRET_KEY hardcoded in source | **Unchanged** | |
| 13 | JWT tokens irrevocable for 24 h — Logout client-only | **Unchanged** | |
| 14 | No rate limiting / lockout on login + register | **Unchanged** | |
| 15 | `users.json` concurrent write race → duplicate-email accounts | **Unchanged** | |
| 16 | Email normalization race — register case-write but login case-i | **Unchanged** | |
| 17 | Migration called inside read → extra disk write loop if seed trips lack fields | **Worse in V4** | Now also migrates budget/currency/expenses + NEW `journal_entries` with same pattern; V3 data copied forward writes back with `journal_entries: []` injected |
| 18 | Frontend never re-hydrates user from /me → stale display | **Unchanged** | |
| 19 | Permissive CORS + JWT-in-header → credentialed cross-origin reads | **Unchanged** | |
| 20 | No max_length on password / full_name → bcrypt truncation + DoS | **Unchanged** | |
| 21 | Register 409 vs 201 = public email-enumeration oracle | **Unchanged** | |
| 22 | Service layer double file-reparse per sub-resource → torn reads | **Worse in V4** | Budget summary + expense CRUD + **new journal CRUD** each trigger additional `_read_trips_file()` calls → now 4–8 JSON parses per API call (Bug #51 journal-specific double-parse) |
| 23 | Failed 422 register echoes raw password input into DOM/toast | **Unchanged** | |
| 24 | Currency change via /budget silently mismatches trip.currency vs existing expenses.currency | **Unchanged** | V4 journal entries have no currency field so unaffected; expense Bug #24 is untouched |
| 25 | Amount > 0 validators all run pre-rounding → 0.001 saves as 0.00 → EDIT permanently stuck | **Unchanged** | Expense-only bug; journal has no Decimal/amount fields so not amplified |
| 26 | Expense dict embedded on disk lacks `trip_id` key — read-time injection asymmetry | **Unchanged (now mirrored)** | V4 introduces identical mirror for journal entries (Bug #42) |
| 27 | Expense Edit always sends full 5-field payload → date/currency validation side effects | **Unchanged (now mirrored)** | V4 introduces identical mirror for journal entries (Bug #45 sends all 3 fields) |
| 28 | Edit-trip shrinks date range → existing expenses/days silently violate range; still totaled | **Worse in V4** | V4 journal entries now ALSO become orphans when trip shrinks (Bug #46; same trap as expenses with new Bug #45) |
| 29 | Whitespace-only expense descriptions pass both layers (`"   "`) | **Unchanged (now mirrored)** | V4 journal has exact same whitespace porousness (Bug #41 / #49 — schema accepts, service catches, no persist-time strip) |
| 30 | Budget progress bar shows 0% when budget = $0 even with > $0 spent | **Unchanged** | |
| 31 | Budget/Expense number inputs ignore `min`/`step` attrs; spinner allows negatives/sub-cent | **Unchanged** | Journal date/text inputs unaffected; title/content have maxlength only |
| 32 | Expense ID generator no collision pre-check; seed/runtime ID format divergence | **Unchanged (now mirrored)** | V4 journal has exact same mirror (Bug #43 — seed `je-1-1` pattern vs runtime `je-{uuid12}`) |
| 33 | Trip Create/Edit forms omit budget/currency fields despite TripCreate advertising them | **Unchanged** | |
| 34 | `formatCurrency()` fallback path produces wrong-symbol-order for JPY/VND | **Unchanged** | |
| 35 | Expense date-range hard-enforced; day dates unbounded → asymmetric UX | **Worse in V4** | Now 3-tier asymmetry: Journal entries enforce dates + Expenses enforce dates + Days STILL unbounded |
| 36 | Expense-form currency check uses stale closure `tripCurrency`; 2-tab trap | **Unchanged** | Journal form has no currency field so Bug #36 pattern not directly mirrored — but stale trip.start_date/end_date closure in journal form causes same class of issue (see journal date trap) |
| 37 | Budget GET + GET single-expense handlers missing BudgetValidationError/ExpenseValidationError | **Unchanged (now mirrored & amplified)** | V4 journal GET list + GET single-entry handlers ALSO missing JournalValidationError / ValueError → Bug #44. 4 GET handlers now total share this gap |
| 38 | `formatCurrency` / `formatDate` force `en-US` locale | **Unchanged** | V4 journal entry dates in cards use same `formatDate()` → affected |
| 39 | No per-category expense totals or breakdown in Budget section | **Unchanged** | |
| 40 | Expense/budget service paths each call `_read_trips_file()` 2–3× per request | **Worse in V4** | Now ALSO journal CRUD paths independently re-parse; total per-trip-detail page load = ~8 full JSON file parses |

---

## Bug #41: Journal Title & Content Whitespace-Only Pass Pydantic Schema Layer (`"   "` accepted at 1–5000 chars)

**Severity:** Low (Data Quality / Schema ↔ Service Asymmetry)  
**Area:** Backend — Schema Layer (JournalEntryCreate / JournalEntryUpdate Pydantic Field definitions)

**Description:**
`JournalEntryBase.title = Field(..., min_length=1, max_length=100)` and `content = Field(..., min_length=1, max_length=5000)` count **Python string length**, which includes spaces. A raw API caller sending `{"title": "   ", "content": "   ", "date": "2026-10-05"}` passes Pydantic validation entirely (length 3 ≥ 1 for both). Only later inside `trip_service.create_new_journal_entry()` does the defensive `.strip()` + blankness check kick in with "Title is required" / "Content is required".

- Good news: Service layer guards **do** catch it, so the browser UI (which also runs .trim() onSubmit) + raw API path both produce HTTP 400.
- Bad news: Pydantic schema still reports to Swagger/OpenAPI consumers that any 1+ char string is valid, which misleads automation testers. Error messages also differ: a Pydantic `min_length` violation would be HTTP 422 with a JSON path pointer, but the service guard returns HTTP 400 `{"detail":"Title is required"}` — automation snapshot asserting on error-code-for-whitespace gets 400 not 422.

This is Bug #5 (V1/V2 trip name whitespace) + Bug #29 (V3 expense whitespace) directly mirrored onto the new Journal sub-resource.

**Affected code locations:**
- [schemas.py — JournalEntryBase.title / JournalEntryBase.content fields](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/models/schemas.py#L169-L178) — No whitespace-aware `field_validator`; rely on downstream service blankness check
- [trip_service.py — create_new_journal_entry strip checks](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/services/trip_service.py#L302-L308) — Service guard exists; schema doesn't

---

## Bug #42: Journal Entry Dict Embedded on Disk Lacks `trip_id` Key — Read-Time Injection Asymmetry (Bug #26 Mirror)

**Severity:** Low-Medium (Data Integrity / Portability)  
**Area:** Backend — Trip Store (JournalEntry Serialization Format)

**Description:**
When `trip_store.create_journal_entry()` writes a new journal entry to `trips.json`, the stored dict contains `{id, title, content, date, created_at, updated_at}` but **no `trip_id`**. The field is injected later in `_dict_to_journal_entry(data, trip_id)` at deserialization time using the outer loop context.

This is a direct mirror of Bug #26 (expense on-disk format same issue) but for journal entries. Downstream scenarios at risk:
- Future V6 migrations that flatten `journal_entries[]` into a separate SQL table will silently lose the parent-trip reference because on-disk dicts aren't self-describing.
- API `GET → round-trip → PUT` symmetry is broken: client receives a `JournalEntry` response that echoes `trip_id` (because `_dict_to_journal_entry` injected it), but if they PUT the exact JSON back, `JournalEntryUpdate` model has no `trip_id` field → silently dropped.
- Seed data (seed_data.py `journal_entries`) also omits `trip_id`, so seed-written and runtime-written data are consistent.

**Affected code locations:**
- [trip_store.py — _dict_to_journal_entry()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/data/trip_store.py#L486-L495) — Line 492 injects trip_id at read-time from loop context, not from stored dict
- [trip_store.py — create_journal_entry()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/data/trip_store.py#L522-L544) — Lines 530–537 new_entry dict built without `trip_id` key
- [seed_data.py — trip-1 journal_entries](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/data/seed_data.py#L450-L474) — Seed entries also lack `trip_id` for consistency

---

## Bug #43: Journal ID Generator No Collision Pre-Check; Seed vs Runtime ID-Format Divergence (Bug #32 Mirror)

**Severity:** Low (Probabilistic Integrity)  
**Area:** Backend — Store Layer (Journal ID Generation)

**Description:**
`_generate_id("je")` returns `je-{uuid4_hex_12}` — a 48-bit cryptographically random suffix per entry. Per the Birthday paradox, collision risk is negligible until ~16 M entries. However, **two issues are still present:**

1. **No uniqueness pre-check before append:** `create_journal_entry()` on line 541 calls `t["journal_entries"].append(new_entry)` with **zero check** that `new_entry_id` already exists in `t["journal_entries"]`. A rogue duplicate (e.g., written by manual JSON edit or future migration) would cause `GET/{entry_id}` / PUT / DELETE to behave non-deterministically on the first array match.

2. **ID format divergence:** Seed journal entries in seed_data.py use hardcoded dash-separated IDs like `je-1-1`, `je-1-2`, `je-3-1` (prefix `je-`, trip index `-`, entry index). Runtime entries use `je-{uuid12hex}` (prefix `je-`, single dash, 12 hex). The formats don't collide *today*, but any future tool that tries to parse journal entry IDs "structurally" (e.g., expecting 3 dash-separated tokens) will break on runtime-created entries. Same structural divergence as Bug #32 (expense IDs: seed `exp-1-1` vs runtime `exp-{uuid12}`).

**Affected code locations:**
- [trip_store.py — _generate_id()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/data/trip_store.py#L69-L70) — No uniqueness check for the generated ID
- [trip_store.py — create_journal_entry()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/data/trip_store.py#L522-L544) — Line 529 generates ID; Line 541 appends without a `[id == new_entry_id]` scan first

---

## Bug #44: Journal GET List + GET Single-Entry Handlers Missing `JournalValidationError` / `ValueError` Except Clauses (Bug #37 Mirror & Amplification)

**Severity:** Very Low (Error Handling Completeness)  
**Area:** Backend Router — journal.py

**Description:**
Comparing `journal.py` handlers against each other:
- `POST /{trip_id}/journal` catches **5 exception types**: TripNotFoundError, NotAuthorizedError, JournalValidationError, ValueError, generic
- `PUT /{trip_id}/journal/{entry_id}` catches **5 exception types**: T/NF, JEntryNF, NA, JValidationError, ValueError
- `DELETE /{trip_id}/journal/{entry_id}` catches **3**: T/NF, JEntryNF, NA (safe — delete raises no validation currently)
- `GET /{trip_id}/journal` (list) catches **only 2**: TripNotFoundError, NotAuthorizedError
- `GET /{trip_id}/journal/{entry_id}` (single) catches **only 3**: T/NF, JournalEntryNotFoundError, NA — missing JournalValidationError and ValueError

Today `get_all_journal_entries()` and `get_journal_entry_by_id()` in the trip-store layer don't raise JournalValidationError or ValueError. They just transform dicts. However, the *service* layer (`list_journal_entries` / `get_single_journal_entry`) routes through `_get_trip_or_error` and might one day add consistency checks that raise JournalValidationError (e.g., a new sanity-check that rejects a returned entry with a whitespace-only title from disk). If added, those exceptions bubble to FastAPI's default handler → **HTTP 500 Internal Server Error** + stack trace instead of a clean 400.

This is Bug #37 (Budget GET + Expense GET single — same pattern) directly mirrored and amplified. V4 now has **4 total GET handlers** with the same incomplete exception-set: budget GET, expense GET single, journal GET list, journal GET single.

**Affected code locations:**
- [routers/journal.py — GET list handler](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/routers/journal.py#L11-L18) — Lacks `except JournalValidationError` and `except ValueError`
- [routers/journal.py — GET single handler](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/routers/journal.py#L35-L44) — Lacks the same 2 catches; compare with PUT handler L46–61 for the correct set

---

## Bug #45: Journal Edit Always Sends ALL 3 Fields (title, date, content) in PUT Payload → Date Validation Trap Even For "Edit Title Only" (Bug #27 Mirror)

**Severity:** Medium-High (UX Trap + Validation Side Effects)  
**Area:** Frontend — openJournalEntryForm onSubmit Handler

**Description:**
`openJournalEntryForm` onSubmit handler (both create and edit branches) builds a full 3-key `payload = {title, content, date}` via lines 1348–1351. For the *edit* (PUT) branch this means:

- Backend PUT receives explicit values for every field, including `date`, even if user only opened the modal to fix a typo in `title`.
- Service-layer correctly skips checks when `entry_update.X is None` (PATCH-style: line 328 computes title_to_check / date_to_check / content_to_check based on `if entry_update.X is not None`). **But the frontend NEVER sends None.** So `if entry_update.date is not None` is always True → date-range validation runs against the current trip start/end, even if the date value was never touched by the user.

Combined with Bug #46 (trip shrinking leaves journal entry dates orphaned), user is permanently trapped: open journal entry je-1-3 dated 2026-10-04 → trip was later shrunk to end 2026-10-03 → click Edit, fix only title typo → Save → **HTTP 400 Journal entry date must be within trip dates**. User doesn't understand why they got a date error when they only edited the title. Error message doesn't surface that the *unchanged* date was re-validated against shrunk trip range.

Runtime-tested and confirmed: PUT je-1-3 with payload `{title:"Renamed", content:"...", date:"2026-10-04"}` against trip shrunk to end 2026-10-03 → HTTP 400 trap triggered.

This is Bug #27 (expense PUT sends all 5 fields) exactly mirrored onto journals with a 3-field variant.

**Affected code locations:**
- [frontend/app.js — openJournalEntryForm onSubmit payload construction](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/frontend/app.js#L1336-L1361) — Lines 1348–1351 unconditionally build all 3 keys; no PATCH-style diffing for only changed fields
- Contrast with [trip_service.py — update_existing_journal_entry](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/services/trip_service.py#L318-L342) — Lines 323–336 correctly use `if entry_update.X is not None:` guards, but the frontend never sends None so the smart conditional short-circuit is unreachable

---

## Bug #46: Edit Trip Shrinks Date Range → Existing Journal Entries Now Quietly Out-of-Range (Bug #28 Mirror & Amplifier of Bug #45)

**Severity:** High (Data Integrity + UX Trap Amplifier; combines with Bug #45 → permanently un-editable entries)  
**Area:** Backend — Trip Update Service Path (No Sub-Resource Re-Validation)

**Description:**
When `PUT /api/trips/{id}` (Edit Trip form) shortens a trip's end_date (e.g., Vietnam Adventure from 2026-10-10 → 2026-10-03), the backend saves the new dates but **never re-validates** existing journal entries against the new range. Newly introduced consequences in V4:

1. Seeded Vietnam journal entry je-1-3 (dated 2026-10-04 — "Da Nang Beach Afternoon") becomes an **orphan** — still stored, still GET'able, still visible in the journal card grid — but its date **2026-10-04 > new end_date 2026-10-03**. Runtime test confirmed: `GET je-1-3` returns 200 OK even with shrunk trip.

2. V4 Journal date range rule is hard-enforced on CREATE and UPDATE. But CREATE-only enforcement means the orphaned entry can never again be edited through the frontend. Because of Bug #45 (PUT always sends date), any attempt to edit even the title alone → date re-validation → 400 trap.

3. Combined with Bug #28 (expense orphans from V3), a single Edit Trip "shrink end_date by 1 week" operation can now silently orphan: days (Bug #1 unbounded anyway), expenses (Bug #28), AND journal entries (Bug #46). Three separate resource types all violating their date-range invariants with no UI warning and no cascade fix.

Runtime-tested and confirmed: trip-1 shrunk to end 2026-10-03 → GET je-1-3 still returned 200 with date 2026-10-04 (orphan preserved), then PUT je-1-3 (title-only-edit via Bug #45 3-field payload) failed with date-range error.

**Affected code locations:**
- [trip_service.py — update_existing_trip()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/services/trip_service.py#L67-L72) — Calls trip_store.update_trip then returns immediately; no scan of days[]/expenses[]/journal_entries[] arrays
- [trip_store.py — update_trip()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/data/trip_store.py#L176-L193) — Blindly overwrites start_date/end_date with no checks
- [frontend/app.js — openTripForm submit handler](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/frontend/app.js#L553-L593) — Client-side checks only compare start vs end; never scans existing days/expenses/journal_entries

---

## Bug #47: Journal Entry Date-Range Error Messages Diverge Between Backend (Single Combined ISO-Date String) vs Frontend (Two Separate Locale-Formatted Strings) → Automation Snapshots Break On Raw API Path

**Severity:** Low-Medium (Automation Snapshot Consistency / API-UI Asymmetry)  
**Area:** Both — Error Message Copy (trip_service._validate_journal_date vs frontend openJournalEntryForm onSubmit)

**Description:**
When a journal entry date falls outside the trip window, users and automation tests receive **different exact error text** depending on whether the request came via the browser form or a raw API call:

| Caller          | Route       | Error message text |
|-----------------|-------------|--------------------|
| Frontend JS     | (client check, no request sent) | **Two separate messages:** <br> 1. `"Journal entry date must be on or after trip start (Oct 1, 2026)"` <br> 2. `"Journal entry date must be on or before trip end (Oct 3, 2026)"` |
| Backend service | HTTP 400    | **Single combined message:** <br> `"Journal entry date must be within trip dates (2026-10-01 to 2026-10-03)"` (ISO format, en dash) |

Differences:
1. **Quantity:** 2 messages vs 1
2. **Format:** Locale-formatted `Mon DD, YYYY` (via `formatDate` with hardcoded en-US — Bug #38) vs `YYYY-MM-DD` ISO
3. **Wording:** "on or after trip start (X)" / "on or before trip end (Y)" vs "within trip dates (X to Y)"

An automation test written against the raw API that asserts on exact substring `"Journal entry date must be on or after"` will fail because server never emits that. Conversely, a frontend UI snapshot asserting "error toast should say 'within trip dates'" fails because the UI's own pre-flight check is always hit first and emits different text.

Runtime test confirmed server message: `POST {date:2099-01-01} → 400 {"detail":"Journal entry date must be within trip dates (2026-10-01 to 2026-10-03)"}`.

**Affected code locations:**
- [trip_service.py — _validate_journal_date() message template](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/services/trip_service.py#L272-L280) — Single combined message with ISO dates from raw Date objects
- [frontend/app.js — openJournalEntryForm onSubmit date checks](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/frontend/app.js#L1342-L1346) — Two separate checks with locale-formatted dates from `formatDate()`

---

## Bug #48: JournalEntryUpdate.title/content Reject 0-Len Empty String At Schema Layer With Generic Pydantic 422 But Service Layer Would Return Custom 400 → Asymmetric Error Code For Empty Put Payload

**Severity:** Very Low (Automation Footgun — Asymmetric error codes for similar input)  
**Area:** Backend — Schema Layer vs Service Layer (JournalEntryUpdate Pydantic Field vs service update_existing_journal_entry)

**Description:**
Two near-identical payloads to `PUT /journal/{id}` return **different HTTP codes and error formats**:

| Payload (PUT)                               | Who rejects it | HTTP code | `detail` field                               |
|---------------------------------------------|----------------|-----------|-----------------------------------------------|
| `{"title": ""}` (zero-length string)        | Pydantic schema `Field(None, min_length=1)` | **422** | Array-of-errors format with JSON pointer `body/title` |
| `{"title": "   "}` (3 spaces, length = 3)   | Service layer `if not title_to_check.strip()` | **400** | Single string `"Title is required"`          |

Pydantic rejects empty-string (`len=0`) before ever reaching service because `min_length=1` fires. But whitespace-only (`len=3`) passes Pydantic and is instead rejected by service at line 328 with a different code and message format.

Automation snapshots asserting "All invalid title payloads return HTTP 400" or "All title errors use single-string detail format" break because they encounter two different error envelopes depending on whether the input was truly empty vs whitespace-only. Not a crash. Very Low severity.

**Affected code locations:**
- [schemas.py — JournalEntryUpdate.title / content fields](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/models/schemas.py#L188-L192) — `min_length=1` rejects empty string at schema layer before service runs
- [trip_service.py — update_existing_journal_entry strip check](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/services/trip_service.py#L326-L330) — Service catches whitespace-only via strip; never runs for empty-string case that Pydantic intercepted

---

## Bug #49: Journal Content Field Saved Verbatim With Leading/Trailing Whitespace — No `.strip()` Normalization At Persist Time

**Severity:** Low (Data Quality / Display Tidiness)  
**Area:** Backend — Service + Store Layer (create_journal_entry / update_journal_entry)

**Description:**
Bug #41 covers blankness-rejection via `.strip()` at the service gate (title/content that's all-whitespace is rejected). But for legitimate content that *has* some leading/trailing whitespace around real text — e.g., `title: "  Da Nang Beach!!!  "` or `content: "\n\n  Great day!\n\n"` — the service accepts it **as-is** with no `.strip()` normalization before writing to disk.

Frontend displays:
- Titles via `escapeHtml(journal.title)` in the card header → renders with visible padding spaces.
- Content in the view modal via `escapeHtml(journal.content)` with `white-space: pre-wrap` → shows blank leading/trailing newlines as actual vertical space in the rendered view dialog.

Not a crash or data loss issue, but automation snapshot tests that compare exact title strings ("Da Nang Beach!!!" vs "  Da Nang Beach!!!  ") or assert content element bounding-box height will flake depending on whether a user typed padding whitespace.

This is a parallel of Bug #29 (whitespace expense descriptions) except here it's **non-blank whitespace padding**, not blank-pass-through.

**Affected code locations:**
- [trip_service.py — create_new_journal_entry passes title/content verbatim after blank-check](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/services/trip_service.py#L302-L316) — Only checks `if not .strip()` (blankness), never assigns stripped values back
- [trip_service.py — update_existing_journal_entry same issue](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/services/trip_service.py#L318-L342) — Lines 323–330 compute merged title_to_check/content_to_check for validation but write the raw values not `.strip()`-normalized versions

---

## Bug #50: Delete Journal Entry Is NOT Idempotent — Spec/README Promises 204 Always But Code Returns HTTP 404 For Missing / Already-Deleted Entry (API Contract Violation)

**Severity:** Medium (API Contract Bug / REST Semantics)  
**Area:** Backend — Service Layer → Router (removed_journal_entry + DELETE route)

**Description:**
The project [README.md line 268](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/README.md) documentation for Journal endpoints explicitly promises idempotent DELETE behavior: *"Deleting an already-deleted entry still returns 204 No Content."*

**Actual code behavior is the opposite.** Runtime test confirmed:
1. First `DELETE /api/trips/trip-1/journal/je-335590b810a7` → HTTP 204 (correct — entry existed, now deleted)
2. Second `DELETE /api/trips/trip-1/journal/je-335590b810a7` of the **same ID** → **HTTP 404** with body `{"detail":"Journal entry not found"}` — directly violating the published spec.

Root cause chain:
- `trip_store.delete_journal_entry()` returns `False` if entry_id isn't in the array (or entry is another user's via ownership scoping — both paths same False).
- Service `removed_journal_entry()` on L345–349 checks `if not deleted: raise JournalEntryNotFoundError(entry_id)`.
- Router DELETE handler L63–71 catches `JournalEntryNotFoundError` and returns HTTP 404.

For REST idempotency the correct behavior is: if entry doesn't exist, "resource is absent" is the desired post-condition of DELETE, so return 204 regardless. (The frontend confirm flow never double-deletes in normal UX because it removes the card after first confirmation — this bug only hits raw API consumers and automation retries.)

Medium severity not because it breaks UX but because it's a direct published-spec violation that API consumers will rely on for retry logic.

**Affected code locations:**
- [trip_service.py — removed_journal_entry() raise path](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/services/trip_service.py#L345-L349) — Line 347 raises JournalEntryNotFoundError when store returns False
- [trip_store.py — delete_journal_entry() returns False instead of treating no-op as success for idempotency](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/data/trip_store.py#L569-L582)
- [routers/journal.py — DELETE handler returns 404](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/routers/journal.py#L63-L71) — Line 67: `except JournalEntryNotFoundError` → 404

---

## Bug #51: V4 Journal Sub-Resource Amplifies Bug #22 — Every Journal Endpoint Double-Parses trips.json (Ownership Check → Store CRUD → Summary)

**Severity:** Very Low (Performance)  
**Area:** Backend — Service Layer vs Store Layer (No shared file-read context)

**Description:**
Bug #22 (V2) documented that activity creation calls `_get_trip_or_error()` (ownership check → 1× full JSON parse via get_trip_owner) and then immediately the store's create_activity calls `_read_trips_file()` AGAIN (2× parse) with no mutations in between. Bug #40 (V3) amplified this to 2–3× per expense/budget call.

**V4 amplifies further. Every single Journal endpoint performs independent, unshared `_read_trips_file()` calls:**

| Endpoint                        | `_read_trips_file()` calls | Where                              |
|---------------------------------|----------------------------|------------------------------------|
| GET list /journal               | 2× minimum                 | `_get_trip_or_error` (1) + `trip_store.get_all_journal_entries` (2) |
| GET single /journal/{id}        | 2× minimum                 | Same pattern |
| POST /journal                   | 3× minimum                 | `_get_trip_or_error` (1) + `store.create_journal_entry` (2 read + write-back parse on write) + `store.get_all` re-read in response |
| PUT /journal/{id}               | 3× minimum                 | Same triple pattern |
| DELETE /journal/{id}            | 2× minimum                 | Ownership (1) + store delete write-op (2) |

Combined with expenses and budget, the frontend's `renderTripDetails` Promise.all (lines 680–692) dispatches **6 concurrent GET requests** (trip, budgetSummary, expenses, journal) — each independently re-parsing trips.json. For a page load alone: ~8 trips.json full parses. Demo MVP with 3 trips = fine performance, but it widens Bug #6 (concurrent write race windows) substantially.

**Affected code locations:**
- [trip_service.py — journal functions (all 5)](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/services/trip_service.py#L283-L349) — Each calls `_get_trip_or_error()` first, then immediately calls a store CRUD function that re-opens the file independently
- [trip_store.py — all journal functions](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/data/trip_store.py#L498-L582) — Each top-level store function calls `_read_trips_file()` without any shared/cached context from the preceding ownership check

---

## Bug #52: Journal CRUD Expands Bug #6 (JSON Write Race) — Each Journal Create/Update/Delete Mutates trips.json, Widening Concurrent Write Windows vs V3

**Severity:** Low-Medium (Concurrent Integrity — Amplifies Bug #6 and Bug #51)  
**Area:** Backend — Store Layer (all trip_store journal write paths with read-modify-write pattern)

**Description:**
Bug #6 (V1/V2) documents that `trip_store` uses read-modify-write for trips.json with no file lock: concurrent writers can lose data. Bug #40 (V3) noted expense/budget added 2–3 extra writes per operation.

**V4 journal doubles the mutation surface. Each journal write path (create/update/delete):**
1. `_read_trips_file()` → parse entire trips.json tree (3 trips, potentially 1000s of lines with days/activities/expenses/journal)
2. Mutate one nested entry deep inside the `t["journal_entries"]` array
3. `_write_trips_file(data)` → serialize + overwrite entire file with `json.dumps()`

If an expense CRUD runs concurrently with a journal CRUD (two browser tabs, or one user clicks "Add Expense" and "Add Journal Entry" in quick succession), the slower write-back clobbers the faster one's change. Combined with days/activities/budget writes, V4 has more overlapping write windows than any previous version.

Low-Medium severity because concurrent edits are rare in a demo MVP, but this is the technical-debt ceiling of the flat-file architecture — V5 (if it adds another embedded resource) will hit this even harder.

**Affected code locations:**
- [trip_store.py — create_journal_entry() read-modify-write](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/data/trip_store.py#L522-L544)
- [trip_store.py — update_journal_entry()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/data/trip_store.py#L547-L566)
- [trip_store.py — delete_journal_entry()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/data/trip_store.py#L569-L582)
- All three paths share Bug #6's unsynchronized `_read_trips_file()` + `_write_trips_file()` pair

---

## Bug #53: Trip Response Model Omits `expenses[]` and `journal_entries[]` Arrays From GET /trips/{id} Response — Clients Must Make 2–3 Extra API Calls Per Trip; Asymmetry With On-Disk Embedded Format

**Severity:** Very Low (API Design Asymmetry / Performance Note — not a bug per se, but documentation-worthy)  
**Area:** Both — Schemas.py Trip response model vs on-disk format and frontend load pattern

**Description:**
On disk, every trip object fully embeds `expenses[]` and `journal_entries[]` arrays. But the `Trip` response Pydantic model at schemas.py lines 111–117 defines only:

```python
class Trip(TripBase):
    id: str
    user_id: str
    days: List[TripDay]
    # NO expenses: List[Expense] field
    # NO journal_entries: List[JournalEntry] field
```

This means `GET /api/trips/{id}` never returns expenses or journal entries. Callers **must** issue 3 round-trips:
1. `GET /trips/{id}` → trip header + days[] only
2. `GET /trips/{id}/budget` → budget summary
3. `GET /trips/{id}/expenses` → expenses array
4. `GET /trips/{id}/journal` → journal entries array  **(V4 NEW)**

The frontend correctly handles this with `Promise.all` (lines 680–692) so users don't notice, but:
- It's confusing for API consumers reading the Swagger docs who see `days` on the Trip model but not the other two embedded resources.
- It's asymmetric with the documented on-disk JSON model presented in USER_MANUAL.md (which shows expenses[] and journal_entries[] as part of the trip JSON record in `data/trips.json`).

Very Low severity; not a crash or data bug — listed here because it's a real API/on-disk divergence that testers encounter when comparing raw store JSON and raw API JSON side-by-side.

**Affected code locations:**
- [schemas.py — Trip response model](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/backend/app/models/schemas.py#L111-L117) — Lists only `days: List[TripDay]`; omits expenses and journal_entries even though both are on disk
- [frontend/app.js — renderTripDetails Promise.all (4 parallel fetches per trip)](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v4/frontend/app.js#L680-L692)

---

## Summary Table (Combined — V1, V2, V3, and NEW V4 Bugs)

| # | Title | Severity | Category | App Version |
|---|-------|----------|----------|-------------|
| … | (V1/V2 #1–#23 unchanged / V3-amplified per V4-Status table above) | … | … | V1, V2, V3 → carry into V4 |
| **24** | **Currency change via /budget silently mismatches trip.currency vs existing expenses.currency → KPI tiles display wrong money symbol (sum-of-USD labeled EUR)** | **Critical** | Financial Data Integrity | **V3** (carried unchanged into V4) |
| **25** | **Amount > 0 validators all run pre-rounding → 0.001 saves as 0.00 → subsequent EDIT permanently stuck (PUT rejects amount 0.00)** | **High** | Integrity + UX Trap | **V3** (carried into V4) |
| **26** | Expense dict embedded on disk lacks `trip_id` key — round-trip/migration asymmetry | Low-Med | Portability | V3 (mirrored in V4) |
| **27** | Frontend expense edit always sends all 5 fields → date/currency/amount validations trigger even for "edit description only" | Med-High | UX / Validation Side Effects | V3 (mirrored in V4) |
| **28** | Edit-trip shrinks date range → existing expenses/days silently violate range; budget summary still totals orphans into KPIs | High | Integrity + Bug Amplifier | V3 (worse in V4 with journal) |
| **29** | Expense.description min_length=1 still accepts whitespace-only (3 spaces passes schema + service) | Medium | Data Quality | V3 (mirrored in V4) |
| **30** | Budget progress bar + % show 0% when budget = 0 and spent > 0 (visually understates over-budget state) | Low-Med | UX Visual Inconsistency | V3 (carried into V4) |
| **31** | Budget amount + expense amount number inputs silently ignore `min`/`step` attrs (field whitelist too narrow) | Low-Med | UX + #25 Enabler | V3 (carried into V4) |
| **32** | Expense ID generator has no collision check; seed IDs use a different string pattern than runtime UUIDs | Low | Probabilistic Integrity | V3 (mirrored in V4) |
| **33** | Trip Create/Edit forms omit budget/currency fields even though `TripCreate` schema advertises them in Swagger | Low-Med | Missing Feature / API-UI Asymmetry | V3 (carried into V4) |
| **34** | `formatCurrency` fallback string-concat path produces inconsistent `"JPY 140000.00"`-style output | Low | Localization Display | V3 (carried into V4) |
| **35** | Expense dates are hard-enforced inside trip range; day dates are not → asymmetric UX; V4 adds journal bounded also | Low-Med | Spec Compliance Inconsistency | V3 (worse in V4 — now 3-tier) |
| **36** | Expense-form currency check uses stale closure `tripCurrency`; 2-tab budget-currency change → submit looks clean client-side, server returns 400 | Low | Stale State | V3 (carried into V4) |
| **37** | Budget GET + GET single-expense handlers missing `BudgetValidationError` / `ExpenseValidationError` → 500 for future maintenance | Very Low | Error Handling | V3 (worse in V4 — now 4 GET handlers) |
| **38** | `formatCurrency` / `formatDate` force `en-US` locale — automation snapshots differ on non-English Chrome profiles | Low | i18n / Snapshots | V3 (carried into V4; journal dates affected too) |
| **39** | No per-category expense totals or breakdown anywhere in Budget section | Low | Missing UX Feature | V3 (carried into V4) |
| **40** | Expense/budget service paths each call `_read_trips_file()` 2–3× per request → more race windows + CPU waste | Very Low | Performance / Amplifies #6 and #22 | V3 (worse in V4 with journal) |
| **41** | **Journal title/content whitespace-only passes Pydantic schema (min_length=1 counts spaces); rejected only later at service** | **Low** | Data Quality / Schema↔Service Asymmetry | **V4 ONLY** |
| **42** | **Journal entry dict embedded on disk LACKS `trip_id` key — read-time injection asymmetry (Bug #26 mirror)** | **Low-Med** | Portability / Migration Safety | **V4 ONLY** |
| **43** | **Journal ID generator no collision pre-check; seed `je-1-1` dash pattern diverges from runtime `je-{uuid12}` dash-hex pattern** | **Low** | Probabilistic Integrity / ID Format Consistency | **V4 ONLY** |
| **44** | **Journal GET list + GET single handlers missing JournalValidationError/ValueError except clauses (Bug #37 mirror)** | **Very Low** | Error Handling Completeness | **V4 ONLY** |
| **45** | **Journal edit always sends ALL 3 fields (title+content+date) PUT → date validation trap for "edit title only" (Bug #27 mirror)** | **Med-High** | UX Trap / Validation Side Effects | **V4 ONLY** |
| **46** | **Edit trip shrinks range → existing journal entries become date-orphans; combined with Bug #45 entries become un-editable forever** | **High** | Data Integrity + Bug Amplifier (combines with #45) | **V4 ONLY** |
| **47** | **Journal date-out-of-range error messages: backend = single ISO-dates combined message; frontend = 2 locale-formatted separate messages → automation snapshots diverge on raw API path** | **Low-Med** | Automation Snapshot / API-UI Message Consistency | **V4 ONLY** |
| **48** | **JournalEntryUpdate Pydantic rejects empty-string title with 422 but whitespace-only → 400 service error; asymmetric error-code pair for similar "blank title" payloads** | **Very Low** | Automation Footgun / Error Code Consistency | **V4 ONLY** |
| **49** | **Journal title/content saved with verbatim leading/trailing whitespace; no strip() normalization at persist time → UI display padding + snapshot flakiness** | **Low** | Data Quality / Display Consistency | **V4 ONLY** |
| **50** | **Journal DELETE is NOT idempotent — spec/README promises 204 always, code returns 404 for missing/deleted entry (runtime confirmed)** | **Medium** | API Contract / REST Semantics | **V4 ONLY** |
| **51** | **V4 journal sub-resource amplifies Bug #22: every journal endpoint double/triple-parses trips.json (ownership → store CRUD → return)** | **Very Low** | Performance / Bug #52 Enabler | **V4 ONLY** |
| **52** | **Journal CRUD creates 3 more read-modify-write paths against trips.json → substantially widens Bug #6 concurrent-write race windows** | **Low-Med** | Concurrent Integrity / Architectural Debt | **V4 ONLY** |
| **53** | **Trip response model (GET /trips/{id}) omits `expenses[]` & `journal_entries[]` even though both are embedded on disk; frontend must 3 extra calls per trip** | **Very Low** | API↔Storage Asymmetry / DX note | **V4** (first surfaced V3 expense, amplified V4 journal) |
