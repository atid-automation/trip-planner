import json
import os
import uuid
from typing import List, Optional, Dict, Any
from pathlib import Path

from app.models.schemas import User, UserCreate
from app.security import hash_password

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
USERS_FILE = DATA_DIR / "users.json"


def _ensure_data_dir() -> None:
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_users_file() -> List[Dict[str, Any]]:
    _ensure_data_dir()
    if not USERS_FILE.exists():
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_users_file(users: List[Dict[str, Any]]) -> None:
    _ensure_data_dir()
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def _generate_id() -> str:
    return f"user-{uuid.uuid4().hex[:12]}"


def _dict_to_user(data: Dict[str, Any]) -> User:
    return User(
        id=data["id"],
        full_name=data["full_name"],
        email=data["email"]
    )


def get_all_users() -> List[User]:
    users_data = _read_users_file()
    return [_dict_to_user(u) for u in users_data]


def get_user_by_id(user_id: str) -> Optional[User]:
    users_data = _read_users_file()
    for u in users_data:
        if u["id"] == user_id:
            return _dict_to_user(u)
    return None


def get_user_by_email(email: str) -> Optional[User]:
    users_data = _read_users_file()
    email_lower = email.lower()
    for u in users_data:
        if u["email"].lower() == email_lower:
            return _dict_to_user(u)
    return None


def get_user_with_password(email: str) -> Optional[Dict[str, Any]]:
    users_data = _read_users_file()
    email_lower = email.lower()
    for u in users_data:
        if u["email"].lower() == email_lower:
            return u
    return None


def email_exists(email: str) -> bool:
    return get_user_by_email(email) is not None


def create_user(user_create: UserCreate) -> User:
    users_data = _read_users_file()
    new_user_id = _generate_id()
    new_user = {
        "id": new_user_id,
        "full_name": user_create.full_name,
        "email": user_create.email,
        "password_hash": hash_password(user_create.password)
    }
    users_data.append(new_user)
    _write_users_file(users_data)
    return _dict_to_user(new_user)


def create_user_from_dict(user_dict: Dict[str, Any]) -> User:
    users_data = _read_users_file()
    users_data.append(user_dict)
    _write_users_file(users_data)
    return _dict_to_user(user_dict)


def reset_users(seed_users: List[Dict[str, Any]]) -> None:
    _ensure_data_dir()
    _write_users_file(seed_users)
