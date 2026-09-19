import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

# Default database location: <project_root>/data/app.db
DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
DEFAULT_DB_PATH = DEFAULT_DATA_DIR / "app.db"


def get_db_path() -> Path:
    env_path = os.environ.get("TRIP_PLANNER_DB")
    if env_path:
        return Path(env_path).resolve()
    return DEFAULT_DB_PATH


def ensure_db_directory(db_path: Optional[Path] = None) -> None:
    target = db_path or get_db_path()
    target.parent.mkdir(parents=True, exist_ok=True)


def create_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    target = db_path or get_db_path()
    ensure_db_directory(target)
    conn = sqlite3.connect(str(target), timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def get_db(db_path: Optional[Path] = None) -> Generator[sqlite3.Connection, None, None]:
    conn = create_connection(db_path)
    try:
        yield conn
    finally:
        conn.close()


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trips (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    destination TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    budget REAL NOT NULL DEFAULT 0.0,
    currency TEXT NOT NULL DEFAULT 'USD',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trip_days (
    id TEXT PRIMARY KEY,
    trip_id TEXT NOT NULL,
    date TEXT NOT NULL,
    title TEXT,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS activities (
    id TEXT PRIMARY KEY,
    day_id TEXT NOT NULL,
    name TEXT NOT NULL,
    location TEXT,
    description TEXT,
    FOREIGN KEY (day_id) REFERENCES trip_days(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS expenses (
    id TEXT PRIMARY KEY,
    trip_id TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS journal_entries (
    id TEXT PRIMARY KEY,
    trip_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    date TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_trips_user_id ON trips(user_id);
CREATE INDEX IF NOT EXISTS idx_trip_days_trip_id ON trip_days(trip_id);
CREATE INDEX IF NOT EXISTS idx_activities_day_id ON activities(day_id);
CREATE INDEX IF NOT EXISTS idx_expenses_trip_id ON expenses(trip_id);
CREATE INDEX IF NOT EXISTS idx_journal_entries_trip_id ON journal_entries(trip_id);
"""


def init_schema(db_path: Optional[Path] = None) -> None:
    with get_db(db_path) as conn:
        with conn:
            conn.executescript(SCHEMA_SQL)


def drop_schema(db_path: Optional[Path] = None) -> None:
    drop_sql = """
    DROP TABLE IF EXISTS journal_entries;
    DROP TABLE IF EXISTS expenses;
    DROP TABLE IF EXISTS activities;
    DROP TABLE IF EXISTS trip_days;
    DROP TABLE IF EXISTS trips;
    DROP TABLE IF EXISTS users;
    """
    with get_db(db_path) as conn:
        with conn:
            conn.executescript(drop_sql)


def is_database_initialized(db_path: Optional[Path] = None) -> bool:
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        return cursor.fetchone() is not None


def is_database_empty(db_path: Optional[Path] = None) -> bool:
    if not is_database_initialized(db_path):
        return True
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS count FROM users")
        row = cursor.fetchone()
        return row["count"] == 0


def seed_database(db_path: Optional[Path] = None) -> None:
    from app.data.seed_data import SEED_USERS, SEED_TRIPS
    from app.security import hash_password

    init_schema(db_path)
    with get_db(db_path) as conn:
        with conn:
            # 1. Insert seed users
            for u in SEED_USERS:
                conn.execute(
                    """
                    INSERT INTO users (id, full_name, email, password_hash)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        full_name = excluded.full_name,
                        email = excluded.email,
                        password_hash = excluded.password_hash
                    """,
                    (u["id"], u["full_name"], u["email"], hash_password(u["password"]))
                )

            # 2. Insert seed trips
            for t in SEED_TRIPS:
                conn.execute(
                    """
                    INSERT INTO trips (id, user_id, name, destination, start_date, end_date, budget, currency)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        user_id = excluded.user_id,
                        name = excluded.name,
                        destination = excluded.destination,
                        start_date = excluded.start_date,
                        end_date = excluded.end_date,
                        budget = excluded.budget,
                        currency = excluded.currency
                    """,
                    (
                        t["id"],
                        t["user_id"],
                        t["name"],
                        t["destination"],
                        t["start_date"],
                        t["end_date"],
                        float(t.get("budget", 0.0)),
                        t.get("currency", "USD")
                    )
                )

                # Insert trip days and activities
                for d in t.get("days", []):
                    conn.execute(
                        """
                        INSERT INTO trip_days (id, trip_id, date, title)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                            trip_id = excluded.trip_id,
                            date = excluded.date,
                            title = excluded.title
                        """,
                        (d["id"], t["id"], d["date"], d.get("title"))
                    )
                    for a in d.get("activities", []):
                        conn.execute(
                            """
                            INSERT INTO activities (id, day_id, name, location, description)
                            VALUES (?, ?, ?, ?, ?)
                            ON CONFLICT(id) DO UPDATE SET
                                day_id = excluded.day_id,
                                name = excluded.name,
                                location = excluded.location,
                                description = excluded.description
                            """,
                            (a["id"], d["id"], a["name"], a.get("location"), a.get("description"))
                        )

                # Insert expenses
                for e in t.get("expenses", []):
                    conn.execute(
                        """
                        INSERT INTO expenses (id, trip_id, description, category, amount, currency, date)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                            trip_id = excluded.trip_id,
                            description = excluded.description,
                            category = excluded.category,
                            amount = excluded.amount,
                            currency = excluded.currency,
                            date = excluded.date
                        """,
                        (
                            e["id"],
                            t["id"],
                            e["description"],
                            e["category"],
                            float(e["amount"]),
                            e["currency"],
                            e["date"]
                        )
                    )

                # Insert journal entries
                for j in t.get("journal_entries", []):
                    conn.execute(
                        """
                        INSERT INTO journal_entries (id, trip_id, title, content, date, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                            trip_id = excluded.trip_id,
                            title = excluded.title,
                            content = excluded.content,
                            date = excluded.date,
                            created_at = excluded.created_at,
                            updated_at = excluded.updated_at
                        """,
                        (
                            j["id"],
                            t["id"],
                            j["title"],
                            j["content"],
                            j["date"],
                            str(j.get("created_at")),
                            str(j.get("updated_at"))
                        )
                    )


def reset_database(db_path: Optional[Path] = None) -> None:
    drop_schema(db_path)
    init_schema(db_path)
    seed_database(db_path)
