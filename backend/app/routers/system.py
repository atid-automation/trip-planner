from fastapi import APIRouter, status, Depends

from app.services import trip_service
from app.models.schemas import User
from app.security import get_current_user

router = APIRouter(prefix="/api/system", tags=["System"])


@router.post("/reset", status_code=status.HTTP_200_OK)
def reset_data(current_user: User = Depends(get_current_user)):
    trip_service.reset_seed_data()
    return {"message": "Data reset to seed state successfully"}
