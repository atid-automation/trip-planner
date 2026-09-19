from fastapi import APIRouter, HTTPException, status, Depends

from app.models.schemas import BudgetSummary, BudgetUpdate, User
from app.services import trip_service
from app.security import get_current_user

router = APIRouter(prefix="/api/trips/{trip_id}/budget", tags=["Budget"])


@router.get("", response_model=BudgetSummary, status_code=status.HTTP_200_OK)
def get_budget(trip_id: str, current_user: User = Depends(get_current_user)):
    try:
        return trip_service.get_budget_summary(trip_id, current_user)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.NotAuthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("", response_model=BudgetSummary, status_code=status.HTTP_200_OK)
def update_budget(trip_id: str, budget_update: BudgetUpdate, current_user: User = Depends(get_current_user)):
    try:
        return trip_service.update_budget(trip_id, budget_update, current_user)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.NotAuthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except trip_service.BudgetValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
