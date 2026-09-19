from fastapi import APIRouter, status

from app.services import trip_service

router = APIRouter(prefix="/api/system", tags=["System"])


@router.post("/reset", status_code=status.HTTP_200_OK)
def reset_data():
    trip_service.reset_seed_data()
    return {"message": "Data reset to seed state successfully"}
