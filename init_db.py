#!/usr/bin/env python3
"""
Initialize or reset the SQLite database for Trip Planner (Version 6).

Usage:
    python init_db.py           # Initializes database schema and seeds if empty
    python init_db.py --reset   # Drops existing tables, recreates schema, and seeds deterministic data
"""

import sys
import argparse
from pathlib import Path

# Add backend directory to sys.path so app modules can be imported
backend_dir = Path(__file__).resolve().parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.data.database import (
    get_db_path,
    init_schema,
    seed_database,
    reset_database,
    is_database_empty,
    get_db
)


def print_database_summary() -> None:
    db_path = get_db_path()
    with get_db() as conn:
        cur = conn.cursor()
        users_count = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        trips_count = cur.execute("SELECT COUNT(*) FROM trips").fetchone()[0]
        days_count = cur.execute("SELECT COUNT(*) FROM trip_days").fetchone()[0]
        acts_count = cur.execute("SELECT COUNT(*) FROM activities").fetchone()[0]
        exp_count = cur.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
        je_count = cur.execute("SELECT COUNT(*) FROM journal_entries").fetchone()[0]

    print(f"Database location: {db_path}")
    print(f"Summary of records in SQLite database:")
    print(f"  - Users:           {users_count}")
    print(f"  - Trips:           {trips_count}")
    print(f"  - Trip Days:       {days_count}")
    print(f"  - Activities:      {acts_count}")
    print(f"  - Expenses:        {exp_count}")
    print(f"  - Journal Entries: {je_count}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize or reset SQLite database for Trip Planner.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop all existing tables, re-create schema, and re-populate deterministic seed data"
    )
    args = parser.parse_args()

    db_path = get_db_path()
    print(f"Trip Planner V6 - SQLite Database Manager")
    print(f"Target DB: {db_path}")

    if args.reset:
        print("Resetting database (dropping existing schema, recreating tables, seeding data)...")
        reset_database()
        print("Database reset successfully.")
    else:
        init_schema()
        if is_database_empty():
            print("Database was empty; seeding initial deterministic dataset...")
            seed_database()
            print("Seeded successfully.")
        else:
            print("Database tables verified. (Existing data preserved; use --reset to overwrite).")

    print_database_summary()


if __name__ == "__main__":
    main()
