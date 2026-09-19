import uuid
from typing import List, Optional, Dict, Any

from app.models.schemas import User, UserCreate
from app.security import hash_password
from app.data.database import get_db, init_schema


def _ensure_db() -> None:
    init_schema()


def _generate_id() -> str:
    return f"user-{uuid.uuid4().hex[:12]}"


def _row_to_user(row: Any) -> User:
    return User(
        id=row["id"],
        full_name=row["full_name"],
        email=row["email"]
    )


def _row_to_dict(row: Any) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "email": row["email"],
        "password_hash": row["password_hash"]
    }


def get_all_users() -> List[User]:
    _ensure_db()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, email FROM users ORDER BY rowid ASC")
        rows = cursor.fetchall()
        return [_row_to_user(r) for r in rows]


def get_user_by_id(user_id: str) -> Optional[User]:
    _ensure_db()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, email FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return _row_to_user(row)
        return None


def get_user_by_email(email: str) -> Optional[User]:
    _ensure_db()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, email FROM users WHERE LOWER(email) = LOWER(?)", (email,))
        row = cursor.fetchone()
        if row:
            return _row_to_user(row)
        return None


def get_user_with_password(email: str) -> Optional[Dict[str, Any]]:
    _ensure_db()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, email, password_hash FROM users WHERE LOWER(email) = LOWER(?)", (email,))
        row = cursor.fetchone()
        if row:
            return _row_to_dict(row)
        return None


def email_exists(email: str) -> bool:
    return get_user_by_email(email) is not None


def create_user(user_create: UserCreate) -> User:
    _ensure_db()
    new_user_id = _generate_id()
    pw_hash = hash_password(user_create.password)
    with get_db() as conn:
        with conn:
            conn.execute(
                """
                INSERT INTO users (id, full_name, email, password_hash)
                VALUES (?, ?, ?, ?)
                """,
                (new_user_id, user_create.full_name, user_create.email, pw_hash)
            )
    return User(
        id=new_user_id,
        full_name=user_create.full_name,
        email=user_create.email
    )


def create_user_from_dict(user_dict: Dict[str, Any]) -> User:
    _ensure_db()
    with get_db() as conn:
        with conn:
            conn.execute(
                """
                INSERT INTO users (id, full_name, email, password_hash)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    full_name = excluded.full_name,
                    email = excluded.email,
                    password_hash = excluded.password_hash
                """,
                (user_dict["id"], user_dict["full_name"], user_dict["email"], user_dict["password_hash"])
            )
    return User(
        id=user_dict["id"],
        full_name=user_dict["full_name"],
        email=user_dict["email"]
    )


def reset_users(seed_users: List[Dict[str, Any]]) -> None:
    _ensure_db()
    with get_db() as conn:
        with conn:
            seed_user_ids = [u["id"] for u in seed_users]
            if seed_user_ids:
                placeholders = ",".join("?" for _ in seed_user_ids)
                conn.execute(f"DELETE FROM users WHERE id NOT IN ({placeholders})", seed_user_ids)
            else:
                conn.execute("DELETE FROM users")
            for u in seed_users:
                conn.execute(
                    """
                    INSERT INTO users (id, full_name, email, password_hash)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        full_name = excluded.full_name,
                        email = excluded.email,
                        password_hash = excluded.password_hash
                    """,
                    (u["id"], u["full_name"], u["email"], u["password_hash"])
                )
