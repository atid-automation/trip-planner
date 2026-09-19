# Load-Test Bug: GET /api/trips — Latency Spike Under Concurrent Load

> **Version:** 6 (SQLite Edition)  
> **Type:** Performance bug — invisible at low concurrency, severe under load  
> **Endpoint affected:** `GET /api/trips`  
> **Difficulty for students:** Beginner–Intermediate

---

## 1. Background

The Trip Planner API stores trips in a SQLite database. When a user requests their
list of trips, the server opens a single database connection and iterates over every
trip row, performing additional sub-queries for each trip's days and activities.

An **artificial delay** was introduced inside this loop — while the DB connection
is still open — to simulate a realistic class of performance defect: an expensive
per-row operation (slow sub-query, external API call, heavy computation) that blocks
the connection for the duration of the iteration.

---

## 2. The Bug

### File
`backend/app/data/trip_store.py` — function `get_all_trips()`

### Buggy Code

```python
def get_all_trips(user_id: str) -> List[Trip]:
    _ensure_db()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM trips WHERE user_id = ? ORDER BY start_date ASC, rowid ASC", (user_id,))
        trip_rows = cur.fetchall()
        result: List[Trip] = []
        for t_row in trip_rows:
            # BUG (load-test): simulates an expensive per-row operation (e.g. a
            # slow sub-query or external API call) performed while the DB
            # connection is still open.  With a single user the delay is barely
            # noticeable, but under concurrent load the connection pool is
            # exhausted, causing cascading timeouts and dramatic latency spikes.
            # FIX: remove the time.sleep line below.
            time.sleep(0.05 * len(trip_rows))  # delay grows with number of trips
            days = _get_days_and_activities_for_trip(conn, t_row["id"])
            result.append(_row_to_trip(t_row, days))
        return result
```

### Why is this realistic?

This pattern — doing slow work **inside an open DB connection** — is extremely
common in production codebases:

| Real-world equivalent | Example |
|-----------------------|---------|
| N+1 query problem | One SELECT per row instead of a JOIN |
| Slow external API | Fetching exchange rates per trip row |
| CPU-heavy work | Serializing / encrypting large blobs per row |
| Missing index | Full table scan repeated for every row |

---

## 3. Behaviour

### With a single user (normal use)

The seed data contains a small number of trips per user (e.g. 3–5).  
Total delay per request ≈ `0.05 s × N_trips × N_trips` — for 4 trips this is ~0.8 s.  
The UI feels slightly slow but **fully functional**. No errors.

### Under concurrent load (load test)

SQLite serialises access when many threads hold connections open simultaneously.  
When dozens of virtual users all call `GET /api/trips` at once, each request holds
its DB connection open for the entire sleep duration.  
Requests pile up, the `timeout=15.0` on the SQLite connection is reached, and
FastAPI starts returning **HTTP 500** errors or very high latency (>10 s).

---

## 4. How to Discover It With Locust

### Locust script

```python
# locustfile.py
from locust import HttpUser, task, between

AUTH_EMAIL = "alice@example.com"
AUTH_PASSWORD = "password123"


class TripPlannerUser(HttpUser):
    wait_time = between(0.5, 1.5)
    token = None

    def on_start(self):
        """Log in and store the JWT token."""
        resp = self.client.post(
            "/api/auth/login",
            json={"email": AUTH_EMAIL, "password": AUTH_PASSWORD},
        )
        if resp.status_code == 200:
            self.token = resp.json().get("access_token")

    @property
    def auth_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    @task
    def list_trips(self):
        """The endpoint under test — should be fast under load."""
        self.client.get("/api/trips", headers=self.auth_headers, name="GET /api/trips")
```

### Running the test

```bash
# Install Locust (one-time)
pip install locust

# Start with 10 users, ramp up 2/s, run for 60 seconds
locust -f locustfile.py \
       --host=http://localhost:8000 \
       --users 10 \
       --spawn-rate 2 \
       --run-time 60s \
       --headless
```

Open `http://localhost:8089` for the live web UI (omit `--headless`).

### Pass / Fail thresholds (suggested)

| Metric | Expected (healthy) | Failing (buggy) |
|--------|--------------------|-----------------|
| Average response time | < 500 ms | > 3 000 ms |
| 95th percentile (p95) | < 1 000 ms | > 8 000 ms |
| Error rate | 0 % | > 5 % |

Students can tune `--users` and `--spawn-rate` to move between pass and fail:

- **5 users** → likely passes (borderline slow but under thresholds)  
- **20 users** → likely fails (p95 breaches 1 s threshold)  
- **50 users** → severe failures (timeouts, HTTP 500s)

---

## 5. Root Cause Explained

```
User A → GET /api/trips → opens DB conn → sleeps 0.8 s ──────────────────▶ closes conn
User B → GET /api/trips → opens DB conn → sleeps 0.8 s ───────────────────────────────▶
User C → GET /api/trips → waiting for DB lock ────────────────────────────────────────────▶ TIMEOUT
User D → GET /api/trips → waiting ...
```

SQLite serialises concurrent access; with `time.sleep` inside the connection
context, each request blocks the DB for `0.05 × N_trips × N_trips` seconds.
As concurrency grows, total wait time scales **O(users × trips²)** — a classic
concurrency bottleneck.

---

## 6. The Fix

Remove the `time.sleep` line. In a real codebase, the equivalent fix is:

1. **Batch the sub-queries** — use a JOIN instead of N+1 selects.
2. **Move slow work outside the DB connection context** — release the connection first, then do the heavy work.
3. **Use an async ORM or connection pool** that does not block the event loop.

### Fixed Code

```python
def get_all_trips(user_id: str) -> List[Trip]:
    _ensure_db()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM trips WHERE user_id = ? ORDER BY start_date ASC, rowid ASC",
            (user_id,)
        )
        trip_rows = cur.fetchall()
        result: List[Trip] = []
        for t_row in trip_rows:
            days = _get_days_and_activities_for_trip(conn, t_row["id"])
            result.append(_row_to_trip(t_row, days))
        return result
```

**One-line change:** delete `time.sleep(0.05 * len(trip_rows))`.

---

## 7. Lesson Summary

| Concept | Takeaway |
|---------|----------|
| **Load testing vs. functional testing** | A function can return correct data and still be unusable under real traffic. |
| **Concurrency bottlenecks** | Holding a resource (DB connection) open during slow work starves other requests. |
| **Performance thresholds** | A test only "fails" if you define what "too slow" means. Thresholds make it actionable. |
| **N+1 query pattern** | Doing one query per row in a loop is a classic anti-pattern that worsens linearly with data size. |
| **Tunable load** | Adjusting `--users` / `--spawn-rate` moves the test from pass to fail, showing students the system's breaking point. |

---

*This bug was intentionally introduced into Trip Planner v6 as a teaching tool.  
Remove the `time.sleep` line in `backend/app/data/trip_store.py → get_all_trips()` to restore normal behaviour.*
