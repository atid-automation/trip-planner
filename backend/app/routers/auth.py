from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.models.schemas import User, UserCreate, UserLogin, Token
from app.services import auth_service
from app.security import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(user_create: UserCreate):
    try:
        return auth_service.register_user(user_create)
    except auth_service.EmailAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(user_login: UserLogin):
    try:
        return auth_service.login_user(user_login)
    except auth_service.InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/login/form", response_model=Token, status_code=status.HTTP_200_OK, include_in_schema=False)
async def login_form(form_data: OAuth2PasswordRequestForm = Depends()):
    user_login = UserLogin(email=form_data.username, password=form_data.password)
    try:
        return auth_service.login_user(user_login)
    except auth_service.InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=User, status_code=status.HTTP_200_OK)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
