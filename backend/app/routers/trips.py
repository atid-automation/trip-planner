from typing import List
from fastapi import APIRouter, HTTPException, status

from app.models.schemas import Trip, TripCreate, TripUpdate
from app.services import trip_service

router = APIRouter(prefix="/api/trips", tags=["Trips"])


@router.get("", response_model=List[Trip], status_code=status.HTTP_200_OK)
def get_trips():
    return trip_service.list_all_trips()


@router.post("", response_model=Trip, status_code=status.HTTP_201_CREATED)
def create_trip(trip_create: TripCreate):
    try:
        return trip_service.create_new_trip(trip_create)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{trip_id}", response_model=Trip, status_code=status.HTTP_200_OK)
def get_trip(trip_id: str):
    try:
        return trip_service.get_trip(trip_id)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{trip_id}", response_model=Trip, status_code=status.HTTP_200_OK)
def update_trip(trip_id: str, trip_update: TripUpdate):
    try:
        return trip_service.update_existing_trip(trip_id, trip_update)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: str):
    try:
        trip_service.remove_trip(trip_id)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
