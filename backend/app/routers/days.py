from typing import List
from fastapi import APIRouter, HTTPException, status, Depends

from app.models.schemas import TripDay, TripDayCreate, TripDayUpdate, User
from app.services import trip_service
from app.security import get_current_user

router = APIRouter(prefix="/api/trips/{trip_id}/days", tags=["Trip Days"])


@router.get("", response_model=List[TripDay], status_code=status.HTTP_200_OK)
def get_days(trip_id: str, current_user: User = Depends(get_current_user)):
    try:
        return trip_service.list_days(trip_id, current_user)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.NotAuthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("", response_model=TripDay, status_code=status.HTTP_201_CREATED)
def create_day(trip_id: str, day_create: TripDayCreate, current_user: User = Depends(get_current_user)):
    try:
        return trip_service.create_new_day(trip_id, day_create, current_user)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.NotAuthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/{day_id}", response_model=TripDay, status_code=status.HTTP_200_OK)
def get_day(trip_id: str, day_id: str, current_user: User = Depends(get_current_user)):
    try:
        return trip_service.get_day(trip_id, day_id, current_user)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.TripDayNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.NotAuthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/{day_id}", response_model=TripDay, status_code=status.HTTP_200_OK)
def update_day(trip_id: str, day_id: str, day_update: TripDayUpdate, current_user: User = Depends(get_current_user)):
    try:
        return trip_service.update_existing_day(trip_id, day_id, day_update, current_user)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.TripDayNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.NotAuthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{day_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_day(trip_id: str, day_id: str, current_user: User = Depends(get_current_user)):
    try:
        trip_service.remove_day(trip_id, day_id, current_user)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.TripDayNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.NotAuthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
