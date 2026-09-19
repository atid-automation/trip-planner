from typing import List
from fastapi import APIRouter, HTTPException, status, Depends

from app.models.schemas import Expense, ExpenseCreate, ExpenseUpdate, User
from app.services import trip_service
from app.security import get_current_user

router = APIRouter(prefix="/api/trips/{trip_id}/expenses", tags=["Expenses"])


@router.get("", response_model=List[Expense], status_code=status.HTTP_200_OK)
def get_expenses(trip_id: str, current_user: User = Depends(get_current_user)):
    try:
        return trip_service.list_expenses(trip_id, current_user)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.NotAuthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("", response_model=Expense, status_code=status.HTTP_201_CREATED)
def create_expense(trip_id: str, expense_create: ExpenseCreate, current_user: User = Depends(get_current_user)):
    try:
        return trip_service.create_new_expense(trip_id, expense_create, current_user)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.NotAuthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except trip_service.ExpenseValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{expense_id}", response_model=Expense, status_code=status.HTTP_200_OK)
def get_expense(trip_id: str, expense_id: str, current_user: User = Depends(get_current_user)):
    try:
        return trip_service.get_expense(trip_id, expense_id, current_user)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.ExpenseNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.NotAuthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/{expense_id}", response_model=Expense, status_code=status.HTTP_200_OK)
def update_expense(trip_id: str, expense_id: str, expense_update: ExpenseUpdate, current_user: User = Depends(get_current_user)):
    try:
        return trip_service.update_existing_expense(trip_id, expense_id, expense_update, current_user)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.ExpenseNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.NotAuthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except trip_service.ExpenseValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(trip_id: str, expense_id: str, current_user: User = Depends(get_current_user)):
    try:
        trip_service.remove_expense(trip_id, expense_id, current_user)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.ExpenseNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.NotAuthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
