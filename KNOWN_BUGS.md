# Known Bugs - Trip Planner v3

This document lists all confirmed bugs, validation gaps, and data integrity issues discovered in the Trip Planner application. Bugs #1 through #23 originated in Version 1 or Version 2 and are still present in Version 3. Bugs #24 onwards are **new to Version 3** (introduced or exposed by the budget management, expense ledger, currency enforcement, and related frontend sections).

---

## ⚠️ Status of V1 & V2 Bugs in V3

| Bug # | Title | Status in V3 | Notes |
|-------|-------|--------------|-------|
| 1 | Day date outside trip range — no validation | **Unchanged** | V3 added date-range enforcement for *expenses*, but days themselves still accept any date (Bug #35 amplifies this) |
| 2 | Trip date update doesn't revalidate existing days | **Worse in V3** | Editing trip start/end can also invalidate already-persisted expenses silently; see Bug #28 |
| 3 | `TripUpdate` validator bypassed when only one date field sent | **Unchanged** | |
| 4 | Duplicate day dates per trip allowed | **Unchanged** | |
| 5 | Whitespace-only names pass backend validation | **Worse in V3** | Now also applies to `Expense.description` (min_length=1 accepts `"   "`) |
| 6 | JSON store concurrent write race condition → data loss | **Unchanged** | Still affects trips.json; concurrent expense writes can clobber each other or lose recently-added days/activities |
| 7 | `/api/system/reset` — public wipe endpoint, no auth | **Partially Resolved** | Still wipes *all* users globally (Bug #11) |
| 8 | `allow_origins=["*"]` + `allow_credentials=True` in CORS | **Unchanged (Active)** | |
| 9 | No optimistic concurrency / conflict detection | **Worse in V3** | Budget PUT uses last-write-wins; 2 clients editing expenses + budget concurrently silently corrupt totals |
| 10 | Duplicate activity names within same day allowed | **Unchanged** | |
| 11 | Reset wipes *all users* globally — any authed user destroys others' data | **Unchanged** | Also now wipes all custom budgets/expenses back to seed |
| 12 | JWT SECRET_KEY hardcoded in source | **Unchanged** | |
| 13 | JWT tokens irrevocable for 24 h — Logout client-only | **Unchanged** | |
| 14 | No rate limiting / lockout on login + register | **Unchanged** | |
| 15 | `users.json` concurrent write race → duplicate-email accounts | **Unchanged** | |
| 16 | Email normalization race — register case-write but login case-i | **Unchanged** | |
| 17 | Migration called inside read → extra disk write loop if seed trips lack user_id | **Worse in V3** | Now also migrates budget/currency/expenses with same pattern |
| 18 | Frontend never re-hydrates user from /me → stale display | **Unchanged** | |
| 19 | Permissive CORS + JWT-in-header → credentialed cross-origin reads | **Unchanged** | |
| 20 | No max_length on password / full_name → bcrypt truncation + DoS | **Unchanged** | |
| 21 | Register 409 vs 201 = public email-enumeration oracle | **Unchanged** | |
| 22 | Service layer double file-reparse per sub-resource → torn reads | **Worse in V3** | Budget summary + expense CRUD each trigger additional `_read_trips_file()` calls → now 3–6 JSON parses per API call |
| 23 | Failed 422 register echoes raw password input into DOM/toast | **Unchanged** | |

---

## Bug #24: Currency Change on Budget Silently Breaks All Existing Expenses (Financial Misrepresentation)

**Severity:** Critical (Data Integrity + Financial Display)  
**Area:** Backend — Budget Service + Store Layer

**Description:**
`PUT /api/trips/{id}/budget` accepts an *optional* `currency` override (see `BudgetUpdate.currency`). If the caller changes `trip.currency` from (say) USD to EUR while 4 expenses exist in USD, the backend performs **zero migration or validation** on the embedded expenses array. Every persisted expense still carries `currency: USD`. But `calculate_budget_summary()` returns `currency = trip.currency` (the new EUR code) and `total_spent = sum(exp.amounts)` — summing USD numeric values and *labelling* them EUR. The frontend then renders `formatCurrency(1250, "EUR")` → **€1,250.00** for what is actually $1,250.00 USD. This is a direct monetary misrepresentation with 2nd-order effects:
- `remaining` and `over_budget` compare apples to oranges
- Adding a *new* expense after the currency change forces the new EUR currency, so the ledger ends up mixing USD-denominated rows with EUR-denominated rows under a single "EUR" column heading
- Because the Expense currency field renders in every table row, the user can see mismatches in the UI but the KPI tiles + progress bar still lie

**Steps to reproduce:**
1. Log in as Alice → open Vietnam Adventure (currency USD, budget 2000, 4 USD expenses = 1250 spent).
2. Call `PUT /api/trips/trip-1/budget` with body `{"budget": 2000, "currency": "EUR"}` (token in header).
3. Reload trip details → **Budget KPI shows "€2,000.00" / "Spent €1,250.00" but every expense row still displays $500.00 / $300.00 etc.** Progress bar still coloured indigo (under budget).

**Mitigation options:** (a) refuse currency change if any expenses exist, (b) change currency only + rewrite every `expense.currency` to the new code (no rate conversion, consistent relabel), or (c) remove currency override from `BudgetUpdate` entirely — currency can only be set at trip creation.

**Affected code locations:**
- [trip_service.py — update_budget()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/services/trip_service.py#L176-L184) — No check that `expenses[]` already exist in a different currency; passes raw `currency` override straight through to trip_store
- [trip_store.py — update_budget()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/data/trip_store.py#L196-L208) — Overwrites `t["currency"]` with no awareness of expenses
- [trip_store.py — calculate_budget_summary()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/data/trip_store.py#L458-L476) — Line 465 returns `trip.currency` unconditionally and never cross-checks `expenses[].currency`

---

## Bug #25: Sub-Cent Expense Amounts (e.g. 0.001) Pass All Validators → Rounded to $0.00 → Permanently Un-Editable Expense Row

**Severity:** High (Data Integrity + UX Trap)  
**Area:** Backend — Validation Stack (Schema → Service → Store)

**Description:**
The expense amount > 0 rule is enforced in three places, but **none of them sees the *post-rounding* value**:
1. `ExpenseCreate.amount: Field(gt=0)` — Pydantic rejects negative/zero but accepts `0.0001`
2. `ExpenseCreate.field_validator("amount") amount_positive` — Duplicates check, also passes `0.0001`
3. `trip_service.create_new_expense()` — `if expense_create.amount <= 0:` — same check again

Then `trip_store.create_expense()` finally calls `_round_amount(expense_create.amount)` → `Decimal("0.0001").quantize(0.01)` = `0.00`. A row is stored with `amount: 0.00`, violating the "amount strictly > 0" business rule on disk.

Worse: the user cannot recover. If they try to EDIT the description (or any other field) later, the frontend sends the full expense object as `PUT` payload (Bug #27). The payload includes `amount: 0.00`. `ExpenseUpdate.amount = Field(None, gt=0)` now rejects **0.0** with HTTP 422. The row is permanently stuck: the user can only delete it, not modify any part of it.

The same trap exists with `BudgetUpdate.budget = Field(ge=0)`. `budget = 0.001` is accepted by schema (≥0), stored as 0.00 after rounding. No user-facing problem there though because 0.00 is a legitimate budget.

**Steps to reproduce:**
1. Alice → Vietnam Adventure → Add Expense with `amount = 0.005`, category=Food, date=2026-10-05 (everything else valid).
2. Backend returns HTTP 201 Created with `amount: 0.01` if the user types 0.005 (because HALF_UP rounds 0.005 → 0.01, *but* typing 0.003 → rounds to 0.00 and triggers this bug).
3. Call `PUT /api/trips/trip-1/expenses/{exp_id}` with body `{description: "test2", category:"Food", amount:0.00, currency:"USD", date:"2026-10-05"}` — returns HTTP 422 because 0.00 is not strictly greater than 0.

**Affected code locations:**
- [schemas.py — ExpenseCreate / ExpenseUpdate amount fields](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/models/schemas.py#L105-L133) — Schema layer validates pre-rounding
- [trip_service.py — create_new_expense amount check](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/services/trip_service.py#L216-L224) — Line 222 runs check BEFORE rounding
- [trip_service.py — update_existing_expense amount check](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/services/trip_service.py#L243-L244) — Same issue on update path
- [trip_store.py — _round_amount()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/data/trip_store.py#L73-L74) — Where the rounding that triggers the trap happens

---

## Bug #26: Expense Embedded in trips.json Lacks `trip_id` Field — Read-Time Injection Means Direct Store Export Inconsistent

**Severity:** Low-Medium (Data Integrity / Portability)  
**Area:** Backend — Trip Store (Expense Serialization Format)

**Description:**
When `trip_store.create_expense()` writes a new expense to `trips.json`, the stored dict contains `{id, description, category, amount, currency, date}` but **no `trip_id`**. The field is injected later in `_dict_to_expense(data, trip_id)` at deserialization time using the loop context. This is technically fine for the app itself, but causes subtle failures in any downstream scenario:
- If a future V6 migration reads `trips.json` and flattens expenses to a separate SQL table, the programmer will assume every expense dict is self-describing — they'll lose the parent trip reference.
- The DELETE endpoint `remove_expense` + `update_expense` first look up the trip by `trip_id` param (scoped ownership) and then iterate the nested array. This works, but the Expense Pydantic response model always echoes `trip_id` back. An API client that does a GET → round-trips the exact JSON back as a PUT → sends an explicit `trip_id` in the body. `ExpenseUpdate` model ignores it (no such field), so it's dropped. Still no crash, but this is a landmine for any developer who expects symmetrical round-trip semantics.

**Affected code locations:**
- [trip_store.py — create_expense()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/data/trip_store.py#L394-L414) — Line 401-408: dict created without `trip_id` key
- [trip_store.py — update_expense()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/data/trip_store.py#L418-L439) — Same, doesn't write trip_id
- Compare to [seed_data.py expenses](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/data/seed_data.py#L32-L62) — Seed expenses also lack the `trip_id` key, so seed-written data is consistent with runtime-written data.

---

## Bug #27: Expense Edit Always Sends the Full 5-Field Payload → Triggers Date + Currency Validation on Fields the User Never Intended to Change

**Severity:** Medium-High (UX Trap + Validation Side Effects)  
**Area:** Frontend — openExpenseForm onSubmit Handler

**Description:**
`openExpenseForm` onSubmit (both create and edit branches) builds a full 5-key `payload = {description, category, amount, currency, date}`. For an *edit* flow this means:
- The backend `PUT` receives explicit values for every field, including `date` and `currency` and `amount`, even if the user only opened the modal to change the description text.
- Now the service-layer checks (which *correctly* skip check-when-None for update): `expense_update.date is not None` → ALWAYS true because we sent a date string → date validation runs against the current trip start/end, even if the date value hasn't changed. That's mostly fine UNTIL Bug #28's scenario hits: the trip start/end was later contracted (via Edit Trip form) to shrink and no longer covers the existing expense date. Now the user simply cannot edit ANY field on that expense — description, amount, category all fail because the unchanged date triggers the range error with no way for the user to fix it from inside the dialog (they'd have to know to also bump the date field within the new range; but the UI doesn't tell them that's what broke, and the error message says "Expense date must be within trip dates" which is confusing because they didn't touch the date).

This behaviour is asymmetric with days/activities — the Update Activity form only sends non-null overrides. Expenses send all fields.

**Affected code locations:**
- [frontend/app.js — openExpenseForm onSubmit payload construction](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/frontend/app.js#L1104-L1134) — Lines 1120-1125 build the full payload every time; no PATCH-style diffing
- Contrast with [trip_service.py — update_existing_expense](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/services/trip_service.py#L231-L253) — Lines 237-248 correctly use `if expense_update.X is not None:` guards, but the frontend never sends None, so the smart conditional is unreachable

---

## Bug #28: Edit Trip Shrinks Date Range → Existing Expenses (and Days) Now Quietly Violating Range; Budget Summary Still Adds Them

**Severity:** High (Data Integrity + Amplifies Bug #27)  
**Area:** Backend — Trip Update Service Path (No Sub-Resource Re-Validation)

**Description:**
When a user calls `PUT /api/trips/{id}` (Edit Trip form) to shorten a trip's end_date (e.g. Vietnam from 2026-10-10 → 2026-10-05), the backend saves the new dates but **never re-validates** existing days and expenses against the new range. Consequences:
1. 3 seeded Vietnam expenses dated 2026-10-05, 2026-10-03, 2026-10-01 still show fine in the list, but a 4th expense dated 2026-10-02 also exists (seed). All OK. But if user shortens trip end to 2026-10-03, then the expense dated 2026-10-05 (Hotel) becomes orphaned.
2. `calculate_budget_summary()` still includes the orphaned expense in the total (because it sums everything in the array), so spending totals do not match the UI's visible trip window — **user is over-budget because of an expense that technically happened "after the trip ended" according to the trip metadata.**
3. Worse: combined with Bug #27, user cannot EDIT any field on any of those now-out-of-range expenses. Save always fails with the date-range error.
4. Even worse: Day date validation (Bug #1) never existed, so activities can also fall outside trip dates with no enforcement.

The spec explicitly says expense date must be inside trip date range — but it applies only on create/update, not on trip shrinkage. Either add a cascading re-validation with informative error messages, or auto-strike-out/hide orphaned expenses, or refuse to shrink dates when sub-resources fall outside.

**Affected code locations:**
- [trip_service.py — update_existing_trip()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/services/trip_service.py#L67-L72) — Calls trip_store.update_trip then returns immediately; no scan of days[] or expenses[] arrays
- [trip_store.py — update_trip()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/data/trip_store.py#L176-L193) — Blindly overwrites start_date/end_date with no checks
- [frontend/app.js — openTripForm submit handler](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/frontend/app.js#L553-L593) — Client-side checks only compare start vs end; never scans existing days/expenses

---

## Bug #29: Whitespace-Only Expense Descriptions Pass Both Layers (`"   "`)

**Severity:** Medium (Data Quality / UX)  
**Area:** Backend Schema + Frontend Validation (Expense)

**Description:**
Expense.description schema: `Field(..., min_length=1)` accepts `min_length` on **Python string length** — which counts whitespace. So a user POSTing `{"description": "   ", ...}` (3 spaces) passes Pydantic validation. The service layer has no `description.strip()` check. The frontend catches this (`!values.description || !values.description.trim()` in onSubmit) — **but only if the expense goes through the browser**. An API-only caller (curl, Postman, test script) can create blank-looking expenses.

Because description renders inside `data-testid="expense-description-text"` as an empty div, automated tests can't distinguish a legitimate empty description vs a validation bug — flaky automation.

This is Bug #5 applied specifically to the new Expense.description field (the original V1/V2 bug also applied to Trip.name, Activity.name).

**Affected code locations:**
- [schemas.py — ExpenseBase.description](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/models/schemas.py#L105-L110) — `min_length=1` with no whitespace-aware validator; no field_validator
- [schemas.py — ExpenseUpdate.description](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/models/schemas.py#L121-L123) — Same gap on the edit path
- [trip_service.py — create_new_expense / update_existing_expense](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/services/trip_service.py#L216-L253) — No description.trim()/blankness check anywhere in service layer

---

## Bug #30: Budget Progress Bar Shows 0% When Budget = $0 (Even When Over-Budget with $1000 Spent)

**Severity:** Low-Medium (UX / Visual Inconsistency)  
**Area:** Frontend — Budget KPI Tile + Progress Bar Rendering

**Description:**
Two expressions:
- Spent % (KPI tile footer): `bs.budget > 0 ? Math.round(...) : 0` → 0%
- Progress bar width: `Math.min(bs.budget > 0 ? (...) : 0, 100)` → 0%

If budget is 0.00 (which is a valid budget state; budget is allowed `ge=0`), any non-zero spending puts the trip **mathematically over-budget**. But users will see a green/indigo 0% bar and no visual "over" cue in the bar itself. The only over-budget cues are:
- Over Budget red badge (good — does show)
- Remaining tile switches to red bg + remaining negative (good — does show)
- BUT the progress bar itself stays thin indigo, not full red. Visually a user scanning the bar section will miss the over-budget condition because the most eye-catching element (the bar) is empty and indigo.

**Affected code locations:**
- [frontend/app.js — renderTripDetailsContent progress div](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/frontend/app.js#L721-L723) — Lines 708 and 722 both divide-by-zero guard to 0

---

## Bug #31: Budget + Expense Number Inputs Lack `min="0"` / `step="0.01"` HTML Attributes → Poor UX + Data Entry Rounding Surprises

**Severity:** Low-Medium (UX + Tiny Data Integrity Footgun)  
**Area:** Frontend — Modal Form Field Config (showModalForm) + openBudgetForm / openExpenseForm

**Description:**
The new V3 forms (`Edit Budget`, `Add/Edit Expense`) use number-type inputs with bare minimum config:
- `{id: 'budget', type: 'number'}` — no min, no step
- `{id: 'amount', type: 'number'}` — no min, no step

Consequences:
- Browser number spinner arrows can decrement budget below 0 → user sees a negative value in the box, submits, client validation rejects. OK (caught), but spinning the spinner down on budget = 0 and continuing holds at 0; for negative user has to type it manually, still caught.
- More importantly: mobile / input-method users get **step=any** semantics, allowing them to enter `0.0009` → submit → rounds to 0.00 (and see Bug #25 trap if amount > 0 but rounds to 0.00).
- The HTML5 constraint validation (`reportValidity()`) that browsers have is bypassed anyway since we use novalidate + our own JS checks. But adding `min`, `max`, `step` improves accessibility (screen readers announce constraints), and on-screen keyboards adapt.
- For the currency select dropdown on Expense Add/Edit: `disabled: true` attribute works, BUT the `select` case for showModalForm only renders the attribute in the opening tag — correctly handled. Good.
- But for number inputs in showModalForm, we *also* don't handle arbitrary extra attributes like `min`, `step` — we only check for `placeholder`, `required`, and `disabled`. The template is [app.js](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/frontend/app.js#L1167-L1193) line 1181: it hardcodes a fixed whitelist. Adding a `min` or `step` key to a field config is silently ignored.

Net: a field config like `{ id:'amount', type:'number', min:'0.01', step:'0.01' }` would do nothing — min/step attrs are not in the template. So even if a future engineer tried to fix Bug #25 via HTML attributes, they wouldn't apply.

**Affected code locations:**
- [frontend/app.js — showModalForm select input rendering](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/frontend/app.js#L1168-L1182) — Lines 1172-1179 select case has hardcoded attribute whitelist; number/input case same
- [frontend/app.js — openBudgetForm fields config](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/frontend/app.js#L1040-L1048) — No min/step specified (wouldn't work anyway)
- [frontend/app.js — openExpenseForm fields config](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/frontend/app.js#L1066-L1078) — Same

---

## Bug #32: Expense ID Collision Risk — Same `_generate_id("exp")` Prefix But Incremented UUID Counter Per-File (No Global Namespace Guard)

**Severity:** Low (Probabilistic Integrity)  
**Area:** Backend — Store Layer (ID Generation)

**Description:**
`_generate_id("exp")` returns `exp-{uuid4_hex_12}`. This uses a cryptographically-random 48-bit suffix per expense → collision risk is ~1 in 2^24 with ~16M expenses (Birthday paradox). In the context of this demo MVP with at most hundreds of expenses per user it's essentially impossible. HOWEVER — there is a *different* collision class: seed expenses in seed_data.py use hardcoded IDs like `exp-1-1`, `exp-2-1`. Runtime-created expenses use `_generate_id("exp")` and get UUID-style 12-hex: `exp-fa3b7c9d...`. The formats never overlap because of the different separator pattern: seed has dash between trip index and counter (exp-1-1), runtime dashes only once between prefix and UUID. OK for now, BUT — if a future developer ever manually adds `exp-something` in a migrated JSON file that doesn't follow the runtime UUID pattern, ID uniqueness is no longer enforceable (the store never checks uniqueness before append). `create_expense` on line 411 calls `t["expenses"].append(new_expense)` with **no pre-check that `new_exp_id` already exists** in `t["expenses"]`. A rogue existing row with the same 48-bit UUID suffix would quietly coexist, causing:
- `GET /expenses/{id}` returns the first match only (depending on array order)
- PUT / DELETE return status based on the first match they hit (non-deterministic if duplicates exist)
- `calculate_budget_summary` sums both duplicates (double-counting)

**Affected code locations:**
- [trip_store.py — _generate_id()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/data/trip_store.py#L69-L70) — No uniqueness check for the returned ID
- [trip_store.py — create_expense()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/data/trip_store.py#L394-L414) — Line 400 calls the generator and line 411 appends without a collision check

---

## Bug #33: Newly Created Trips Don't Default to Create-Form Budget Values (Create Form Silent 0/USD even though Schema Accepts User-Provided)

**Severity:** Low-Medium (Missing-Frontend Feature)  
**Area:** Frontend Trip Create Form + Backend Schema Asymmetry

**Description:**
Backend `TripCreate` schema accepts `budget` (default 0.0) and `currency` (default USD) as optional fields on trip creation. The frontend Create Trip form (`openTripForm`) only exposes 4 fields: `name`, `destination`, `start_date`, `end_date`. The submit payload is:
```js
const payload = { name, destination, start_date, end_date };
```
— no `budget` or `currency`. This means **every trip created via the UI always gets 0.00 USD, requiring a separate visit to Edit Budget afterward.**

This isn't a crash, but it's a spec/design gap: users might assume setting budget upfront during creation would be possible. The Edit Trip form has the same gap (no budget/currency fields, and `TripUpdate` schema also lacks them — so even a direct API call can't fix it via the trip endpoint, you *must* use `/budget` endpoint). Backend intentional — but then the `TripCreate` schema shouldn't advertise budget/currency fields as user-settable at trip-creation time, because that misleads API users (Swagger UI) about what the UI supports.

**Affected code locations:**
- [schemas.py — TripCreate budget/currency fields](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/models/schemas.py#L65-L67) — Declares settable fields that the UI never uses
- [schemas.py — TripUpdate](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/models/schemas.py#L70-L81) — Lacks any budget/currency fields; Edit Trip route can never change budget even via API
- [frontend/app.js — trip form submit payload](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/frontend/app.js#L573-L589) — Line 575 builds only the 4 keys

---

## Bug #34: `formatCurrency()` Fallback Path Produces `"${currency} ${amount}"` — Wrong Symbol Order for JPY/VND

**Severity:** Low (Localization Display)  
**Area:** Frontend — formatCurrency Helper

**Description:**
Normal path uses `Intl.NumberFormat(style: 'currency', currency: 'JPY')` → displays `¥140,000` (symbol before, no decimals; although our force-to-2dp override makes it `¥140,000.00`).

If Intl fails for any reason (rare — Safari private mode in some older iOS, SSR, or malformed currency code sent somehow), the fallback string concatenation kicks in:
```js
return `${currency || ''} ${Number(amount).toFixed(2)}`
```
Result for Japanese Yen: `"JPY 140000.00"` — reads OK, but if `currency` were ever sent as a SYMBOL instead of a code (it's not, schema always sends code), we'd get `"¥ 140000.00"` with a spurious space. Not a crash, but the `data-testid="budget-amount"` value differs between working-Intl and fallback-Intl environments, causing flaky snapshot tests that assert on exact formatted strings.

**Affected code locations:**
- [frontend/app.js — formatCurrency()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/frontend/app.js#L145-L157) — Lines 154-155 fallback branch

---

## Bug #35: Expense Date-Range Validation Enforced But Expense Days Are Not (Spec Inconsistency Within V3)

**Severity:** Low-Medium (Spec Compliance Inconsistency)  
**Area:** Both — Validation Rule Asymmetry between Expenses and Days

**Description:**
Prompt 3 clearly introduced a rule *for expenses*: "Expense date MUST fall within trip start/end dates". The V2/V3 implementation did not retroactively apply the same rule for **trip days** (Bug #1). Resulting asymmetric UX:
- User can create a day on 2026-11-01 for the Tokyo trip (starts 2026-11-15) → **Allowed** (no validation anywhere)
- User creates an expense with that same date 2026-11-01 → **Rejected** (HTTP 400 date out of range)

This is semantically inconsistent: a day can exist outside the trip window but an expense cannot. Most users expect days to be bounded similarly (or, alternatively, both unbounded with soft UI warnings instead of hard HTTP 400). Test engineers writing automation will discover this asymmetry during exploratory test runs because the two resources — which both have a `date` field nested under a trip — behave divergently on the same date value.

**Affected code locations:**
- [trip_service.py — _validate_expense_date](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/services/trip_service.py#L187-L197) — Hard enforcement for expenses only
- [trip_service.py — create_new_day / update_existing_day](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/services/trip_service.py#L98-L118) — No equivalent validation for days

---

## Bug #36: Expense Form Disabled-Currency `<select>` Not Protected Against DOM Tampering Before Client Validation

**Severity:** Low (Defense-in-Depth)  
**Area:** Frontend — openExpenseForm Submitter

**Description:**
The currency `<select>` in the Expense modal has `disabled: true` for good UX ("locked to trip currency"). However:
- A user with DevTools open can right-click → **Inspect** → remove the `disabled` attribute, then pick a different currency in the dropdown.
- Client validation on submit DOES check `values.currency !== tripCurrency` → throws explicit error. Good.
- If the user ALSO opens DevTools → Sources → sets breakpoint on the submit handler and monkey-patches `tripCurrency` variable to the wrong code, or just calls the onSubmit with arbitrary payload, the frontend check is bypassed entirely. In that case server-side validation still catches mismatches. **OK, not a real vulnerability.**
- But there's a subtler issue: The form has `novalidate` attribute, so HTML5's own `required` validation never runs on the disabled `<select>`. If someone also clears out all `<option>` children of the select (tamper), `el.value` returns `""`, client validation at line 1109 ("Currency is required") catches it. OK.
- HOWEVER — line 1110 (`values.currency !== tripCurrency`) compares against **the variable that was captured in the closure when the form opened**. If the trip currency itself is changed *in a second tab* while the modal was open (e.g., user has two tabs, edits budget currency to EUR in tab B, then in tab A saves an expense that still has `tripCurrency = USD` cached), client-side check says "USD == USD → OK". Server then receives expense.currency=USD, trip.currency=EUR → returns 400 mismatch. The user gets a server error message for a UI action that looked clean. Stale closure bug with cross-tab state.

**Affected code locations:**
- [frontend/app.js — openExpenseForm expense onSubmit currency check](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/frontend/app.js#L1109-L1112) — Uses closure-captured `tripCurrency` from function definition time, not re-fetched at submit

---

## Bug #37: GET /budget Endpoint Missing BudgetValidationError / ValueError Except Clauses — Minor Error Surface Gap

**Severity:** Very Low (Error Handling Completeness)  
**Area:** Backend Router — budget.py

**Description:**
Comparing budget.py GET handler vs PUT handler:
- `GET get_budget()` only catches `TripNotFoundError → 404` and `NotAuthorizedError → 403`
- `PUT update_budget()` additionally catches `BudgetValidationError → 400` and `ValueError → 400`

Currently `get_budget_summary()` in the service layer cannot raise `BudgetValidationError` (it only calculates from on-disk state, no user input). But if a future maintenance programmer adds some "Budget sanity check" that raises BudgetValidationError on GET (e.g., detects an inconsistent currency), the exception will bubble up to FastAPI's default handler → HTTP **500 Internal Server Error** with a generic traceback instead of a clear 400. Same as what's already protected on PUT. PUT has the protection; GET doesn't. Easy fix: copy the 2 extra `except` clauses to GET.

Same issue with expense `GET /{expense_id}` handler: catches TripNotFound, ExpenseNotFound, NotAuthorized, but NOT ExpenseValidationError or ValueError. Currently get_expense() raises none of those — but future-proofing is violated.

(For comparison: `create_expense` POST, PUT, and expense DELETE all include ExpenseValidationError/ValueError handlers — except GET single expense.)

**Affected code locations:**
- [backend/app/routers/budget.py — GET handler](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/routers/budget.py#L10-L17) — Lacks BudgetValidationError and ValueError catches
- [backend/app/routers/expenses.py — GET single expense](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/routers/expenses.py#L35-L44) — Lacks ExpenseValidationError and ValueError catches

---

## Bug #38: Intl.NumberFormat Default Locale `en-US` Hardcoded — Comma-Thousands Separators Everywhere Regardless of Browser Language

**Severity:** Low (Internationalization)  
**Area:** Frontend — formatCurrency + formatDate

**Description:**
Both `formatCurrency` (new in V3) and `formatDate` (V2) are hardcoded to locale string `'en-US'`:
```js
new Intl.NumberFormat('en-US', ...)
new Date(d).toLocaleDateString('en-US', ...)
```
Users with browser locale set to `de-DE`, `fr-FR`, `ja-JP` etc. will still see amounts formatted with commas as thousands separator and period as decimal point (e.g., Europe sees `€5,000.00` instead of their local `€5.000,00`). Minor cosmetic issue in a demo MVP, but — the `data-testid="budget-amount"` DOM value uses this formatting, so a test engineer running automation on a German Chrome profile could see different formatted strings and fail assertions.

**Affected code locations:**
- [frontend/app.js — formatDate()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/frontend/app.js#L138-L143) — Hardcoded en-US
- [frontend/app.js — formatCurrency()](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/frontend/app.js#L145-L157) — Hardcoded en-US

---

## Bug #39: No Category Column Totals / Breakdown in Budget Section (Spec-Gap UX)

**Severity:** Low (Missing Feature / Expected UX)  
**Area:** Frontend — Budget Summary Display

**Description:**
The V3 spec is vague on this, but every standard expense-tracking UX shows at least:
- A category aggregate ("Food: $300 — 24% of spend", "Accommodation: $500 — 40%", etc.)
- OR a donut/bar chart (spec says "No charts/AI", so skip the visual but still the text data).

Currently the V3 Budget section only shows the 4 aggregate KPIs but never breaks down which category contributed how much. Users must manually add rows per category in their head. Not a crash/bug, but automation testers writing "expense by category" tests for V3 will naturally look for an aggregate tile and find it missing — they'll categorise this as a "V3 bug/missing feature" during reporting.

**Affected code locations:**
- [frontend/app.js — Budget 4-tile grid](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/frontend/app.js#L699-L723) — No category aggregate block inserted between KPI row and progress bar

---

## Bug #40: Deleting an Expense Does Not Refresh Any Server-Side Budget Summary Cached Copy (Store Layer Double-Parse Pattern)

**Severity:** Very Low (Performance / Architecturally Inconsistent)  
**Area:** Backend — Ownership Enforcement + Redundant Parsing

**Description:**
Every single expense operation (create/update/delete) AND budget summary GET, AND the budget PUT all call:
1. `_get_trip_or_error()` → `get_trip_owner(trip_id)` → 1st `_read_trips_file()` + full JSON parse
2. Then immediately call their respective store CRUD method → 2nd `_read_trips_file()` call (same file, same data, no mutations in between)
3. Then many methods also call `calculate_budget_summary()` at the end → **3rd** full `_read_trips_file()` for the same trip

In total, creating an expense parses trips.json **3 times**. Combined with the V2 double-parse issue (Bug #22), a single POST to create an activity on a day inside a trip already had 2-4 parses; in V3 the budget paths push this to 3-6. Performance is still fine for a demo MVP with 3 trips in the file, but concurrent writers (Bug #6) have *more windows* to race between the read and write paths within one API call.

This is essentially Bug #22 extended; logged separately because the new V3 store functions (`update_budget`, `calculate_budget_summary`, expense CRUD) all re-parse independently and never share a loaded in-memory context with the ownership check.

**Affected code locations:**
- [trip_service.py — _get_trip_or_error vs expense CRUD](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/services/trip_service.py#L43-L253) — Every expense/budget function pairs an ownership check with a store call with no shared context
- [trip_store.py — get_trip_owner + get_all_expenses](file:///d:/Apps/AI-Native%20Automation%20Engineer/trip-planner-app/trip-planner-v3/backend/app/data/trip_store.py#L138-L379) — Each top-level function opens and parses the JSON file independently with no cache/lock context

---

## Summary Table (Combined — V1, V2, and NEW V3 Bugs)

| # | Title | Severity | Category | App Version |
|---|-------|----------|----------|-------------|
| … | (V1/V2 #1–#23 unchanged) | … | … | V1, V2 → carry into V3 |
| **24** | **Currency change via /budget silently mismatches trip.currency vs existing expenses.currency → KPI tiles display wrong money symbol (sum-of-USD labeled EUR)** | **Critical** | Financial Data Integrity | **V3 ONLY** |
| **25** | **Amount > 0 validators all run pre-rounding → 0.001 saves as 0.00 → subsequent EDIT permanently stuck (PUT rejects amount 0.00)** | **High** | Integrity + UX Trap | **V3 ONLY** |
| **26** | Expense dict embedded on disk lacks `trip_id` key — round-trip/migration asymmetry | Low-Med | Portability | V3 ONLY |
| **27** | Frontend expense edit always sends all 5 fields → date/currency/amount validations trigger even for "edit description only" | Med-High | UX / Validation Side Effects | V3 ONLY |
| **28** | Edit-trip shrinks date range → existing expenses/days silently violate range; budget summary still totals orphans into KPIs | High | Integrity + Bug Amplifier | V3 ONLY |
| **29** | Expense.description min_length=1 still accepts whitespace-only (3 spaces passes schema + service) | Medium | Data Quality | V3 ONLY |
| **30** | Budget progress bar + % show 0% when budget = 0 and spent > 0 (visually understates over-budget state) | Low-Med | UX Visual Inconsistency | V3 ONLY |
| **31** | Budget amount + expense amount number inputs silently ignore `min`/`step` attrs (field whitelist too narrow); spinner allows negatives and sub-cent entries | Low-Med | UX + #25 Enabler | V3 ONLY |
| **32** | Expense ID generator has no collision check; seed IDs use a different string pattern than runtime UUIDs | Low | Probabilistic Integrity | V3 ONLY |
| **33** | Trip Create/Edit forms omit budget/currency fields even though `TripCreate` schema advertises them in Swagger | Low-Med | Missing Feature / API-UI Asymmetry | V3 ONLY |
| **34** | `formatCurrency` fallback string-concat path produces inconsistent `"JPY 140000.00"`-style output | Low | Localization Display | V3 ONLY |
| **35** | Expense dates are hard-enforced inside trip range; day dates are not → asymmetric UX for same-date sibling resources | Low-Med | Spec Compliance Inconsistency | V3 ONLY |
| **36** | Expense-form currency check uses stale closure `tripCurrency`; 2-tab budget-currency change → submit looks clean client-side, server returns 400 | Low | Stale State | V3 ONLY |
| **37** | Budget GET + GET single-expense handlers missing `BudgetValidationError` / `ExpenseValidationError` → 500 for future maintenance | Very Low | Error Handling | V3 ONLY |
| **38** | `formatCurrency` / `formatDate` force `en-US` locale — automation snapshots differ on non-English Chrome profiles | Low | i18n / Snapshots | V3 ONLY |
| **39** | No per-category expense totals or breakdown anywhere in Budget section | Low | Missing UX Feature | V3 ONLY |
| **40** | Expense/budget service paths each call `_read_trips_file()` 2–3× per request → more race windows + CPU waste | Very Low | Performance / Amplifies #6 and #22 | V3 ONLY |
