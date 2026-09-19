from typing import Optional, List, Dict, Any

from app.models.schemas import User, UserCreate, UserLogin, Token
from app.data import user_store
from app.data.seed_data import SEED_USERS, SEED_TRIP_USER_ASSIGNMENTS
from app.security import verify_password, create_access_token, hash_password
from datetime import timedelta


class EmailAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


def get_user_by_id(user_id: str) -> Optional[User]:
    return user_store.get_user_by_id(user_id)


def get_user_by_email(email: str) -> Optional[User]:
    return user_store.get_user_by_email(email)


def list_all_users() -> List[User]:
    return user_store.get_all_users()


def register_user(user_create: UserCreate) -> User:
    if user_store.email_exists(user_create.email):
        raise EmailAlreadyExistsError("Email already exists")
    return user_store.create_user(user_create)


def login_user(user_login: UserLogin) -> Token:
    user_data = user_store.get_user_with_password(user_login.email)
    if user_data is None:
        raise InvalidCredentialsError("Invalid email or password.")
    if not verify_password(user_login.password, user_data.get("password_hash", "")):
        raise InvalidCredentialsError("Invalid email or password.")
    user = User(
        id=user_data["id"],
        full_name=user_data["full_name"],
        email=user_data["email"]
    )
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(days=1)
    )
    return Token(access_token=access_token, token_type="bearer", user=user)


def ensure_seed_users() -> None:
    existing_users = user_store.get_all_users()
    existing_emails = {u.email.lower() for u in existing_users}
    for seed_user in SEED_USERS:
        if seed_user["email"].lower() in existing_emails:
            continue
        user_dict = {
            "id": seed_user["id"],
            "full_name": seed_user["full_name"],
            "email": seed_user["email"],
            "password_hash": hash_password(seed_user["password"])
        }
        user_store.create_user_from_dict(user_dict)


def reset_users_to_seed() -> None:
    seed_users_with_hashes: List[Dict[str, Any]] = []
    for seed_user in SEED_USERS:
        seed_users_with_hashes.append({
            "id": seed_user["id"],
            "full_name": seed_user["full_name"],
            "email": seed_user["email"],
            "password_hash": hash_password(seed_user["password"])
        })
    user_store.reset_users(seed_users_with_hashes)
