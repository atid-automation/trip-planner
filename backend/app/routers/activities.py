from typing import List
from fastapi import APIRouter, HTTPException, status

from app.models.schemas import Activity, ActivityCreate, ActivityUpdate
from app.services import trip_service

router = APIRouter(prefix="/api/trips/{trip_id}/days/{day_id}/activities", tags=["Activities"])


@router.get("", response_model=List[Activity], status_code=status.HTTP_200_OK)
def get_activities(trip_id: str, day_id: str):
    try:
        return trip_service.list_activities(trip_id, day_id)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.TripDayNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("", response_model=Activity, status_code=status.HTTP_201_CREATED)
def create_activity(trip_id: str, day_id: str, act_create: ActivityCreate):
    try:
        return trip_service.create_new_activity(trip_id, day_id, act_create)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.TripDayNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{activity_id}", response_model=Activity, status_code=status.HTTP_200_OK)
def get_activity(trip_id: str, day_id: str, activity_id: str):
    try:
        return trip_service.get_activity(trip_id, day_id, activity_id)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.TripDayNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.ActivityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{activity_id}", response_model=Activity, status_code=status.HTTP_200_OK)
def update_activity(trip_id: str, day_id: str, activity_id: str, act_update: ActivityUpdate):
    try:
        return trip_service.update_existing_activity(trip_id, day_id, activity_id, act_update)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.TripDayNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.ActivityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(trip_id: str, day_id: str, activity_id: str):
    try:
        trip_service.remove_activity(trip_id, day_id, activity_id)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.TripDayNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.ActivityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
