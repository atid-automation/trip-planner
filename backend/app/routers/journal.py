from typing import List
from fastapi import APIRouter, HTTPException, status, Depends

from app.models.schemas import JournalEntry, JournalEntryCreate, JournalEntryUpdate, User
from app.services import trip_service
from app.security import get_current_user

router = APIRouter(prefix="/api/trips/{trip_id}/journal", tags=["Journal"])


@router.get("", response_model=List[JournalEntry], status_code=status.HTTP_200_OK)
def get_journal_entries(trip_id: str, current_user: User = Depends(get_current_user)):
    try:
        return trip_service.list_journal_entries(trip_id, current_user)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.NotAuthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("", response_model=JournalEntry, status_code=status.HTTP_201_CREATED)
def create_journal_entry(trip_id: str, entry_create: JournalEntryCreate, current_user: User = Depends(get_current_user)):
    try:
        return trip_service.create_new_journal_entry(trip_id, entry_create, current_user)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.NotAuthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except trip_service.JournalValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{entry_id}", response_model=JournalEntry, status_code=status.HTTP_200_OK)
def get_journal_entry(trip_id: str, entry_id: str, current_user: User = Depends(get_current_user)):
    try:
        return trip_service.get_journal_entry(trip_id, entry_id, current_user)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.JournalEntryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.NotAuthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/{entry_id}", response_model=JournalEntry, status_code=status.HTTP_200_OK)
def update_journal_entry(trip_id: str, entry_id: str, entry_update: JournalEntryUpdate, current_user: User = Depends(get_current_user)):
    try:
        return trip_service.update_existing_journal_entry(trip_id, entry_id, entry_update, current_user)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.JournalEntryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.NotAuthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except trip_service.JournalValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journal_entry(trip_id: str, entry_id: str, current_user: User = Depends(get_current_user)):
    try:
        trip_service.remove_journal_entry(trip_id, entry_id, current_user)
    except trip_service.TripNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.JournalEntryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except trip_service.NotAuthorizedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
