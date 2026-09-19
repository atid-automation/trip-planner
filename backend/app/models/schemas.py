from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date


class ActivityBase(BaseModel):
    name: str = Field(..., min_length=1, description="Activity name is required")
    location: Optional[str] = None
    description: Optional[str] = None


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    location: Optional[str] = None
    description: Optional[str] = None


class Activity(ActivityBase):
    id: str


class TripDayBase(BaseModel):
    date: date
    title: Optional[str] = None


class TripDayCreate(TripDayBase):
    pass


class TripDayUpdate(BaseModel):
    date: Optional[date] = None
    title: Optional[str] = None


class TripDay(TripDayBase):
    id: str
    activities: List[Activity] = []


class TripBase(BaseModel):
    name: str = Field(..., min_length=1, description="Trip name is required")
    destination: str = Field(..., min_length=1, description="Destination is required")
    start_date: date
    end_date: date

    @field_validator("end_date")
    def end_date_after_start_date(cls, v, values):
        start_date = values.data.get("start_date")
        if start_date and v < start_date:
            raise ValueError("End date cannot be earlier than start date")
        return v


class TripCreate(TripBase):
    pass


class TripUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    destination: Optional[str] = Field(None, min_length=1)
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @field_validator("end_date")
    def end_date_after_start_date(cls, v, values):
        start_date = values.data.get("start_date")
        if start_date and v and v < start_date:
            raise ValueError("End date cannot be earlier than start date")
        return v


class Trip(TripBase):
    id: str
    days: List[TripDay] = []
