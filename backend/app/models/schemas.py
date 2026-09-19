from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict
from typing import List, Optional, Literal, Annotated, Union
from datetime import date as Date, datetime

EXPENSE_CATEGORIES = Literal["Accommodation", "Food", "Transportation", "Activities", "Shopping", "Other"]
SUPPORTED_CURRENCIES = Literal["USD", "EUR", "GBP", "ILS", "VND", "THB", "JPY"]

EXPENSE_CATEGORY_VALUES = ["Accommodation", "Food", "Transportation", "Activities", "Shopping", "Other"]
SUPPORTED_CURRENCY_VALUES = ["USD", "EUR", "GBP", "ILS", "VND", "THB", "JPY"]


class JournalEntryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Title is required (max 100 characters)")
    content: str = Field(..., min_length=1, max_length=5000, description="Content is required (max 5000 characters)")
    date: Date


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntryUpdate(BaseModel):
    model_config = ConfigDict(union_types_strategy="left_to_right")
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    date: Optional[Date] = None


class JournalEntry(JournalEntryBase):
    id: str
    trip_id: str
    created_at: datetime
    updated_at: datetime


class ActivityBase(BaseModel):
    name: str = Field(..., min_length=1, description="Activity name is required")
    location: Optional[str] = None
    description: Optional[str] = None


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    model_config = ConfigDict(union_types_strategy="left_to_right")
    name: Optional[str] = Field(None, min_length=1)
    location: Optional[str] = None
    description: Optional[str] = None


class Activity(ActivityBase):
    id: str


class TripDayBase(BaseModel):
    date: Date
    title: Optional[str] = None


class TripDayCreate(TripDayBase):
    pass


class TripDayUpdate(BaseModel):
    model_config = ConfigDict(union_types_strategy="left_to_right")
    date: Optional[Date] = None
    title: Optional[str] = None


class TripDay(TripDayBase):
    id: str
    activities: List[Activity] = []


class TripBase(BaseModel):
    name: str = Field(..., min_length=1, description="Trip name is required")
    destination: str = Field(..., min_length=1, description="Destination is required")
    start_date: Date
    end_date: Date

    @field_validator("end_date")
    def end_date_after_start_date(cls, v, values):
        start_date = values.data.get("start_date")
        if start_date and v < start_date:
            raise ValueError("End date cannot be earlier than start date")
        return v


class TripCreate(TripBase):
    budget: Optional[float] = Field(0.0, ge=0, description="Trip budget must be >= 0")
    currency: Optional[SUPPORTED_CURRENCIES] = "USD"


class TripUpdate(BaseModel):
    model_config = ConfigDict(union_types_strategy="left_to_right")
    name: Optional[str] = Field(None, min_length=1)
    destination: Optional[str] = Field(None, min_length=1)
    start_date: Optional[Date] = None
    end_date: Optional[Date] = None

    @field_validator("end_date")
    def end_date_after_start_date(cls, v, values):
        start_date = values.data.get("start_date")
        if start_date and v and v < start_date:
            raise ValueError("End date cannot be earlier than start date")
        return v


class Trip(TripBase):
    id: str
    user_id: str
    budget: float = 0.0
    currency: str = "USD"
    days: List[TripDay] = []


class BudgetUpdate(BaseModel):
    model_config = ConfigDict(union_types_strategy="left_to_right")
    budget: float = Field(..., ge=0, description="Budget must be >= 0")
    currency: Optional[SUPPORTED_CURRENCIES] = None


class BudgetSummary(BaseModel):
    budget: float
    currency: str
    total_spent: float
    remaining: float
    over_budget: bool


class ExpenseBase(BaseModel):
    description: str = Field(..., min_length=1, description="Description is required")
    category: EXPENSE_CATEGORIES
    amount: float = Field(..., gt=0, description="Amount must be greater than 0")
    currency: SUPPORTED_CURRENCIES
    date: Date


class ExpenseCreate(ExpenseBase):
    @field_validator("amount")
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class ExpenseUpdate(BaseModel):
    model_config = ConfigDict(union_types_strategy="left_to_right")
    description: Optional[str] = Field(None, min_length=1)
    category: Optional[EXPENSE_CATEGORIES] = None
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[SUPPORTED_CURRENCIES] = None
    date: Optional[Date] = None

    @field_validator("amount")
    def amount_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class Expense(ExpenseBase):
    id: str
    trip_id: str


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=1, description="Full name is required")
    email: EmailStr = Field(..., description="Email is required")


class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=1, description="Full name is required")
    email: EmailStr = Field(..., description="Email is required")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    password_confirmation: str = Field(..., description="Password confirmation is required")

    @field_validator("password_confirmation")
    def passwords_match(cls, v, values):
        password = values.data.get("password")
        if password and v != password:
            raise ValueError("Passwords do not match")
        return v


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email is required")
    password: str = Field(..., description="Password is required")


class User(UserBase):
    id: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User
