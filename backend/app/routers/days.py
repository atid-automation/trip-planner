from typing import List
from fastapi import APIRouter, HTTPException, status

from app.models.schemas import TripDay, TripDayCreate, TripDayUpdate
from app.services import trip_service

router = APIRouter(prefix="/api/trips/{trip_id}/days", tags=["Trip Days"])


@router.get("", response_model=List[TripDay], status_code=status.HTTP_200_OK)
def get_days(trip_id: str):
    try:
        return trip_service.list_days(trip_id)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("", response_model=TripDay, status_code=status.HTTP_201_CREATED)
def create_day(trip_id: str, day_create: TripDayCreate):
    try:
        return trip_service.create_new_day(trip_id, day_create)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{day_id}", response_model=TripDay, status_code=status.HTTP_200_OK)
def get_day(trip_id: str, day_id: str):
    try:
        return trip_service.get_day(trip_id, day_id)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.TripDayNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{day_id}", response_model=TripDay, status_code=status.HTTP_200_OK)
def update_day(trip_id: str, day_id: str, day_update: TripDayUpdate):
    try:
        return trip_service.update_existing_day(trip_id, day_id, day_update)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.TripDayNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{day_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_day(trip_id: str, day_id: str):
    try:
        trip_service.remove_day(trip_id, day_id)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.TripDayNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
