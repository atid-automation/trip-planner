import time
import uuid
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Dict, Any, Tuple

from app.models.schemas import (
    Trip, TripCreate, TripUpdate,
    TripDay, TripDayCreate, TripDayUpdate,
    Activity, ActivityCreate, ActivityUpdate,
    Expense, ExpenseCreate, ExpenseUpdate,
    JournalEntry, JournalEntryCreate, JournalEntryUpdate
)
from app.data.database import get_db, init_schema, reset_database

DEFAULT_DEMO_USER_ID = "user-alice"


def _ensure_db() -> None:
    init_schema()


def _generate_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _round_amount(amount: float) -> float:
    return float(Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def reset_to_seed_data() -> None:
    reset_database()


def _row_to_activity(row: Any) -> Activity:
    return Activity(
        id=row["id"],
        name=row["name"],
        location=row["location"],
        description=row["description"]
    )


def _row_to_trip_day(row: Any, activities: List[Activity]) -> TripDay:
    return TripDay(
        id=row["id"],
        date=row["date"],
        title=row["title"],
        activities=activities
    )


def _row_to_expense(row: Any, trip_id: str) -> Expense:
    return Expense(
        id=row["id"],
        trip_id=trip_id,
        description=row["description"],
        category=row["category"],
        amount=_round_amount(float(row["amount"])),
        currency=row["currency"],
        date=row["date"]
    )


def _row_to_journal_entry(row: Any, trip_id: str) -> JournalEntry:
    created_at = row["created_at"]
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)
    updated_at = row["updated_at"]
    if isinstance(updated_at, str):
        updated_at = datetime.fromisoformat(updated_at)

    return JournalEntry(
        id=row["id"],
        trip_id=trip_id,
        title=row["title"],
        content=row["content"],
        date=row["date"],
        created_at=created_at,
        updated_at=updated_at
    )


def _get_days_and_activities_for_trip(conn: Any, trip_id: str) -> List[TripDay]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM trip_days WHERE trip_id = ? ORDER BY date ASC, rowid ASC", (trip_id,))
    day_rows = cur.fetchall()

    days: List[TripDay] = []
    for d_row in day_rows:
        cur.execute("SELECT * FROM activities WHERE day_id = ? ORDER BY rowid ASC", (d_row["id"],))
        act_rows = cur.fetchall()
        activities = [_row_to_activity(a) for a in act_rows]
        days.append(_row_to_trip_day(d_row, activities))
    return days


def _row_to_trip(row: Any, days: List[TripDay]) -> Trip:
    return Trip(
        id=row["id"],
        user_id=row["user_id"],
        name=row["name"],
        destination=row["destination"],
        start_date=row["start_date"],
        end_date=row["end_date"],
        budget=_round_amount(float(row["budget"])),
        currency=row["currency"],
        days=days
    )


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
            # FIX: move any slow work outside the 'with get_db()' block, or
            # batch the sub-queries instead of processing rows one by one.
            time.sleep(0.05 * len(trip_rows))  # delay grows with number of trips
            days = _get_days_and_activities_for_trip(conn, t_row["id"])
            result.append(_row_to_trip(t_row, days))
        return result


def get_trip_by_id(trip_id: str, user_id: Optional[str] = None) -> Optional[Trip]:
    _ensure_db()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM trips WHERE id = ?", (trip_id,))
        row = cur.fetchone()
        if not row:
            return None
        if user_id is not None and row["user_id"] != user_id:
            return None
        days = _get_days_and_activities_for_trip(conn, trip_id)
        return _row_to_trip(row, days)


def get_trip_owner(trip_id: str) -> Optional[str]:
    _ensure_db()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
        row = cur.fetchone()
        if row:
            return row["user_id"]
        return None


def get_trip_date_range(trip_id: str, user_id: Optional[str] = None) -> Optional[Tuple[str, str]]:
    _ensure_db()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id, start_date, end_date FROM trips WHERE id = ?", (trip_id,))
        row = cur.fetchone()
        if not row:
            return None
        if user_id is not None and row["user_id"] != user_id:
            return None
        return (row["start_date"], row["end_date"])


def create_trip(trip_create: TripCreate, user_id: str) -> Trip:
    _ensure_db()
    new_trip_id = _generate_id("trip")
    budget = _round_amount(trip_create.budget) if trip_create.budget is not None else 0.0
    currency = trip_create.currency if trip_create.currency is not None else "USD"
    start_date_str = trip_create.start_date.isoformat()
    end_date_str = trip_create.end_date.isoformat()

    with get_db() as conn:
        with conn:
            conn.execute(
                """
                INSERT INTO trips (id, user_id, name, destination, start_date, end_date, budget, currency)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (new_trip_id, user_id, trip_create.name, trip_create.destination, start_date_str, end_date_str, budget, currency)
            )

    return Trip(
        id=new_trip_id,
        user_id=user_id,
        name=trip_create.name,
        destination=trip_create.destination,
        start_date=trip_create.start_date,
        end_date=trip_create.end_date,
        budget=budget,
        currency=currency,
        days=[]
    )


def update_trip(trip_id: str, trip_update: TripUpdate, user_id: str) -> Optional[Trip]:
    _ensure_db()
    with get_db() as conn:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM trips WHERE id = ?", (trip_id,))
            row = cur.fetchone()
            if not row or row["user_id"] != user_id:
                return None

            name = trip_update.name if trip_update.name is not None else row["name"]
            dest = trip_update.destination if trip_update.destination is not None else row["destination"]
            start_date = trip_update.start_date.isoformat() if trip_update.start_date is not None else row["start_date"]
            end_date = trip_update.end_date.isoformat() if trip_update.end_date is not None else row["end_date"]

            conn.execute(
                """
                UPDATE trips
                SET name = ?, destination = ?, start_date = ?, end_date = ?
                WHERE id = ? AND user_id = ?
                """,
                (name, dest, start_date, end_date, trip_id, user_id)
            )

    return get_trip_by_id(trip_id, user_id)


def update_budget(trip_id: str, budget: float, currency: Optional[str], user_id: str) -> Optional[Trip]:
    _ensure_db()
    rounded_budget = _round_amount(budget)
    with get_db() as conn:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM trips WHERE id = ?", (trip_id,))
            row = cur.fetchone()
            if not row or row["user_id"] != user_id:
                return None

            new_currency = currency if currency is not None else row["currency"]
            conn.execute(
                """
                UPDATE trips
                SET budget = ?, currency = ?
                WHERE id = ? AND user_id = ?
                """,
                (rounded_budget, new_currency, trip_id, user_id)
            )

    return get_trip_by_id(trip_id, user_id)


def delete_trip(trip_id: str, user_id: str) -> bool:
    _ensure_db()
    with get_db() as conn:
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM trips WHERE id = ? AND user_id = ?", (trip_id, user_id))
            return cur.rowcount > 0


def get_days_for_trip(trip_id: str, user_id: Optional[str] = None) -> Optional[List[TripDay]]:
    _ensure_db()
    trip = get_trip_by_id(trip_id, user_id)
    if trip is None:
        return None
    return trip.days


def get_day_by_id(trip_id: str, day_id: str, user_id: Optional[str] = None) -> Optional[TripDay]:
    _ensure_db()
    trip = get_trip_by_id(trip_id, user_id)
    if trip is None:
        return None
    for d in trip.days:
        if d.id == day_id:
            return d
    return None


def create_day(trip_id: str, day_create: TripDayCreate, user_id: str) -> Optional[TripDay]:
    _ensure_db()
    with get_db() as conn:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
            row = cur.fetchone()
            if not row or row["user_id"] != user_id:
                return None

            new_day_id = _generate_id("day")
            date_str = day_create.date.isoformat()
            conn.execute(
                """
                INSERT INTO trip_days (id, trip_id, date, title)
                VALUES (?, ?, ?, ?)
                """,
                (new_day_id, trip_id, date_str, day_create.title)
            )
            return TripDay(
                id=new_day_id,
                date=day_create.date,
                title=day_create.title,
                activities=[]
            )


def update_day(trip_id: str, day_id: str, day_update: TripDayUpdate, user_id: str) -> Optional[TripDay]:
    _ensure_db()
    with get_db() as conn:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
            trip_row = cur.fetchone()
            if not trip_row or trip_row["user_id"] != user_id:
                return None

            cur.execute("SELECT * FROM trip_days WHERE id = ? AND trip_id = ?", (day_id, trip_id))
            day_row = cur.fetchone()
            if not day_row:
                return None

            date_str = day_update.date.isoformat() if day_update.date is not None else day_row["date"]
            title = day_update.title if day_update.title is not None else day_row["title"]

            conn.execute(
                """
                UPDATE trip_days
                SET date = ?, title = ?
                WHERE id = ? AND trip_id = ?
                """,
                (date_str, title, day_id, trip_id)
            )

    return get_day_by_id(trip_id, day_id, user_id)


def delete_day(trip_id: str, day_id: str, user_id: str) -> bool:
    _ensure_db()
    with get_db() as conn:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
            trip_row = cur.fetchone()
            if not trip_row or trip_row["user_id"] != user_id:
                return False

            cur.execute("DELETE FROM trip_days WHERE id = ? AND trip_id = ?", (day_id, trip_id))
            return cur.rowcount > 0


def get_activities_for_day(trip_id: str, day_id: str, user_id: Optional[str] = None) -> Optional[List[Activity]]:
    _ensure_db()
    day = get_day_by_id(trip_id, day_id, user_id)
    if day is None:
        return None
    return day.activities


def get_activity_by_id(trip_id: str, day_id: str, activity_id: str, user_id: Optional[str] = None) -> Optional[Activity]:
    _ensure_db()
    day = get_day_by_id(trip_id, day_id, user_id)
    if day is None:
        return None
    for a in day.activities:
        if a.id == activity_id:
            return a
    return None


def create_activity(trip_id: str, day_id: str, act_create: ActivityCreate, user_id: str) -> Optional[Activity]:
    _ensure_db()
    with get_db() as conn:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
            trip_row = cur.fetchone()
            if not trip_row or trip_row["user_id"] != user_id:
                return None

            cur.execute("SELECT id FROM trip_days WHERE id = ? AND trip_id = ?", (day_id, trip_id))
            if not cur.fetchone():
                return None

            new_act_id = _generate_id("act")
            conn.execute(
                """
                INSERT INTO activities (id, day_id, name, location, description)
                VALUES (?, ?, ?, ?, ?)
                """,
                (new_act_id, day_id, act_create.name, act_create.location, act_create.description)
            )
            return Activity(
                id=new_act_id,
                name=act_create.name,
                location=act_create.location,
                description=act_create.description
            )


def update_activity(trip_id: str, day_id: str, activity_id: str, act_update: ActivityUpdate, user_id: str) -> Optional[Activity]:
    _ensure_db()
    with get_db() as conn:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
            trip_row = cur.fetchone()
            if not trip_row or trip_row["user_id"] != user_id:
                return None

            cur.execute("SELECT id FROM trip_days WHERE id = ? AND trip_id = ?", (day_id, trip_id))
            if not cur.fetchone():
                return None

            cur.execute("SELECT * FROM activities WHERE id = ? AND day_id = ?", (activity_id, day_id))
            act_row = cur.fetchone()
            if not act_row:
                return None

            name = act_update.name if act_update.name is not None else act_row["name"]
            loc = act_update.location if act_update.location is not None else act_row["location"]
            desc = act_update.description if act_update.description is not None else act_row["description"]

            conn.execute(
                """
                UPDATE activities
                SET name = ?, location = ?, description = ?
                WHERE id = ? AND day_id = ?
                """,
                (name, loc, desc, activity_id, day_id)
            )

    return get_activity_by_id(trip_id, day_id, activity_id, user_id)


def delete_activity(trip_id: str, day_id: str, activity_id: str, user_id: str) -> bool:
    _ensure_db()
    with get_db() as conn:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
            trip_row = cur.fetchone()
            if not trip_row or trip_row["user_id"] != user_id:
                return False

            cur.execute("SELECT id FROM trip_days WHERE id = ? AND trip_id = ?", (day_id, trip_id))
            if not cur.fetchone():
                return False

            cur.execute("DELETE FROM activities WHERE id = ? AND day_id = ?", (activity_id, day_id))
            return cur.rowcount > 0


def get_all_expenses(trip_id: str, user_id: Optional[str] = None) -> Optional[List[Expense]]:
    _ensure_db()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
        row = cur.fetchone()
        if not row:
            return None
        if user_id is not None and row["user_id"] != user_id:
            return None

        cur.execute("SELECT * FROM expenses WHERE trip_id = ? ORDER BY date ASC, rowid ASC", (trip_id,))
        rows = cur.fetchall()
        return [_row_to_expense(r, trip_id) for r in rows]


def get_expense_by_id(trip_id: str, expense_id: str, user_id: Optional[str] = None) -> Optional[Expense]:
    _ensure_db()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
        row = cur.fetchone()
        if not row:
            return None
        if user_id is not None and row["user_id"] != user_id:
            return None

        cur.execute("SELECT * FROM expenses WHERE id = ? AND trip_id = ?", (expense_id, trip_id))
        r = cur.fetchone()
        if r:
            return _row_to_expense(r, trip_id)
        return None


def create_expense(trip_id: str, expense_create: ExpenseCreate, user_id: str) -> Optional[Expense]:
    _ensure_db()
    with get_db() as conn:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
            row = cur.fetchone()
            if not row or row["user_id"] != user_id:
                return None

            new_exp_id = _generate_id("exp")
            amount = _round_amount(expense_create.amount)
            date_str = expense_create.date.isoformat()

            conn.execute(
                """
                INSERT INTO expenses (id, trip_id, description, category, amount, currency, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (new_exp_id, trip_id, expense_create.description, expense_create.category, amount, expense_create.currency, date_str)
            )

    return get_expense_by_id(trip_id, new_exp_id, user_id)


def update_expense(trip_id: str, expense_id: str, expense_update: ExpenseUpdate, user_id: str) -> Optional[Expense]:
    _ensure_db()
    with get_db() as conn:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
            trip_row = cur.fetchone()
            if not trip_row or trip_row["user_id"] != user_id:
                return None

            cur.execute("SELECT * FROM expenses WHERE id = ? AND trip_id = ?", (expense_id, trip_id))
            exp_row = cur.fetchone()
            if not exp_row:
                return None

            desc = expense_update.description if expense_update.description is not None else exp_row["description"]
            cat = expense_update.category if expense_update.category is not None else exp_row["category"]
            amount = _round_amount(expense_update.amount) if expense_update.amount is not None else exp_row["amount"]
            currency = expense_update.currency if expense_update.currency is not None else exp_row["currency"]
            date_str = expense_update.date.isoformat() if expense_update.date is not None else exp_row["date"]

            conn.execute(
                """
                UPDATE expenses
                SET description = ?, category = ?, amount = ?, currency = ?, date = ?
                WHERE id = ? AND trip_id = ?
                """,
                (desc, cat, amount, currency, date_str, expense_id, trip_id)
            )

    return get_expense_by_id(trip_id, expense_id, user_id)


def delete_expense(trip_id: str, expense_id: str, user_id: str) -> bool:
    _ensure_db()
    with get_db() as conn:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
            trip_row = cur.fetchone()
            if not trip_row or trip_row["user_id"] != user_id:
                return False

            cur.execute("DELETE FROM expenses WHERE id = ? AND trip_id = ?", (expense_id, trip_id))
            return cur.rowcount > 0


def calculate_budget_summary(trip_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    _ensure_db()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id, budget, currency FROM trips WHERE id = ?", (trip_id,))
        trip_row = cur.fetchone()
        if not trip_row:
            return None
        if user_id is not None and trip_row["user_id"] != user_id:
            return None

        budget = _round_amount(float(trip_row["budget"]))
        currency = trip_row["currency"]

        cur.execute("SELECT amount FROM expenses WHERE trip_id = ?", (trip_id,))
        expense_rows = cur.fetchall()
        total_spent = _round_amount(sum(float(r["amount"]) for r in expense_rows))
        remaining = _round_amount(budget - total_spent)
        over_budget = total_spent > budget

        return {
            "budget": budget,
            "currency": currency,
            "total_spent": total_spent,
            "remaining": remaining,
            "over_budget": over_budget
        }


def get_all_journal_entries(trip_id: str, user_id: Optional[str] = None) -> Optional[List[JournalEntry]]:
    _ensure_db()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
        trip_row = cur.fetchone()
        if not trip_row:
            return None
        if user_id is not None and trip_row["user_id"] != user_id:
            return None

        cur.execute("SELECT * FROM journal_entries WHERE trip_id = ? ORDER BY date DESC, created_at DESC", (trip_id,))
        rows = cur.fetchall()
        return [_row_to_journal_entry(r, trip_id) for r in rows]


def get_journal_entry_by_id(trip_id: str, entry_id: str, user_id: Optional[str] = None) -> Optional[JournalEntry]:
    _ensure_db()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
        trip_row = cur.fetchone()
        if not trip_row:
            return None
        if user_id is not None and trip_row["user_id"] != user_id:
            return None

        cur.execute("SELECT * FROM journal_entries WHERE id = ? AND trip_id = ?", (entry_id, trip_id))
        row = cur.fetchone()
        if row:
            return _row_to_journal_entry(row, trip_id)
        return None


def create_journal_entry(trip_id: str, entry_create: JournalEntryCreate, user_id: str) -> Optional[JournalEntry]:
    _ensure_db()
    now_str = datetime.utcnow().isoformat()
    with get_db() as conn:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
            trip_row = cur.fetchone()
            if not trip_row or trip_row["user_id"] != user_id:
                return None

            new_entry_id = _generate_id("je")
            date_str = entry_create.date.isoformat()

            conn.execute(
                """
                INSERT INTO journal_entries (id, trip_id, title, content, date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (new_entry_id, trip_id, entry_create.title, entry_create.content, date_str, now_str, now_str)
            )

    return get_journal_entry_by_id(trip_id, new_entry_id, user_id)


def update_journal_entry(trip_id: str, entry_id: str, entry_update: JournalEntryUpdate, user_id: str) -> Optional[JournalEntry]:
    _ensure_db()
    now_str = datetime.utcnow().isoformat()
    with get_db() as conn:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
            trip_row = cur.fetchone()
            if not trip_row or trip_row["user_id"] != user_id:
                return None

            cur.execute("SELECT * FROM journal_entries WHERE id = ? AND trip_id = ?", (entry_id, trip_id))
            entry_row = cur.fetchone()
            if not entry_row:
                return None

            title = entry_update.title if entry_update.title is not None else entry_row["title"]
            content = entry_update.content if entry_update.content is not None else entry_row["content"]
            date_str = entry_update.date.isoformat() if entry_update.date is not None else entry_row["date"]

            conn.execute(
                """
                UPDATE journal_entries
                SET title = ?, content = ?, date = ?, updated_at = ?
                WHERE id = ? AND trip_id = ?
                """,
                (title, content, date_str, now_str, entry_id, trip_id)
            )

    return get_journal_entry_by_id(trip_id, entry_id, user_id)


def delete_journal_entry(trip_id: str, entry_id: str, user_id: str) -> bool:
    _ensure_db()
    with get_db() as conn:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM trips WHERE id = ?", (trip_id,))
            trip_row = cur.fetchone()
            if not trip_row or trip_row["user_id"] != user_id:
                return False

            cur.execute("DELETE FROM journal_entries WHERE id = ? AND trip_id = ?", (entry_id, trip_id))
            return cur.rowcount > 0
