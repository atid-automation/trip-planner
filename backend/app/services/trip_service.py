from typing import List, Optional, Dict, Any
from datetime import date

from app.models.schemas import (
    Trip, TripCreate, TripUpdate, User,
    TripDay, TripDayCreate, TripDayUpdate,
    Activity, ActivityCreate, ActivityUpdate,
    Expense, ExpenseCreate, ExpenseUpdate,
    BudgetUpdate, BudgetSummary
)
from app.data import trip_store
from app.services import auth_service


class TripNotFoundError(Exception):
    pass


class TripDayNotFoundError(Exception):
    pass


class ActivityNotFoundError(Exception):
    pass


class ExpenseNotFoundError(Exception):
    pass


class NotAuthorizedError(Exception):
    pass


class BudgetValidationError(Exception):
    pass


class ExpenseValidationError(Exception):
    pass


def _get_trip_or_error(trip_id: str, user: User) -> Trip:
    owner = trip_store.get_trip_owner(trip_id)
    if owner is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    if owner != user.id:
        raise NotAuthorizedError("You are not authorized to access this trip")
    trip = trip_store.get_trip_by_id(trip_id, user.id)
    if trip is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    return trip


def list_all_trips(user: User) -> List[Trip]:
    return trip_store.get_all_trips(user.id)


def get_trip(trip_id: str, user: User) -> Trip:
    return _get_trip_or_error(trip_id, user)


def create_new_trip(trip_create: TripCreate, user: User) -> Trip:
    return trip_store.create_trip(trip_create, user.id)


def update_existing_trip(trip_id: str, trip_update: TripUpdate, user: User) -> Trip:
    _get_trip_or_error(trip_id, user)
    trip = trip_store.update_trip(trip_id, trip_update, user.id)
    if trip is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    return trip


def remove_trip(trip_id: str, user: User) -> None:
    _get_trip_or_error(trip_id, user)
    deleted = trip_store.delete_trip(trip_id, user.id)
    if not deleted:
        raise TripNotFoundError(f"Trip {trip_id} not found")


def list_days(trip_id: str, user: User) -> List[TripDay]:
    _get_trip_or_error(trip_id, user)
    days = trip_store.get_days_for_trip(trip_id, user.id)
    if days is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    return days


def get_day(trip_id: str, day_id: str, user: User) -> TripDay:
    _get_trip_or_error(trip_id, user)
    day = trip_store.get_day_by_id(trip_id, day_id, user.id)
    if day is None:
        raise TripDayNotFoundError(f"Day {day_id} not found in trip {trip_id}")
    return day


def create_new_day(trip_id: str, day_create: TripDayCreate, user: User) -> TripDay:
    _get_trip_or_error(trip_id, user)
    day = trip_store.create_day(trip_id, day_create, user.id)
    if day is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    return day


def update_existing_day(trip_id: str, day_id: str, day_update: TripDayUpdate, user: User) -> TripDay:
    _get_trip_or_error(trip_id, user)
    day = trip_store.update_day(trip_id, day_id, day_update, user.id)
    if day is None:
        raise TripDayNotFoundError(f"Day {day_id} not found in trip {trip_id}")
    return day


def remove_day(trip_id: str, day_id: str, user: User) -> None:
    _get_trip_or_error(trip_id, user)
    deleted = trip_store.delete_day(trip_id, day_id, user.id)
    if not deleted:
        raise TripDayNotFoundError(f"Day {day_id} not found in trip {trip_id}")


def list_activities(trip_id: str, day_id: str, user: User) -> List[Activity]:
    _get_trip_or_error(trip_id, user)
    activities = trip_store.get_activities_for_day(trip_id, day_id, user.id)
    if activities is None:
        raise TripDayNotFoundError(f"Day {day_id} not found in trip {trip_id}")
    return activities


def get_activity(trip_id: str, day_id: str, activity_id: str, user: User) -> Activity:
    _get_trip_or_error(trip_id, user)
    if trip_store.get_day_by_id(trip_id, day_id, user.id) is None:
        raise TripDayNotFoundError(f"Day {day_id} not found in trip {trip_id}")
    activity = trip_store.get_activity_by_id(trip_id, day_id, activity_id, user.id)
    if activity is None:
        raise ActivityNotFoundError(f"Activity {activity_id} not found in day {day_id}")
    return activity


def create_new_activity(trip_id: str, day_id: str, act_create: ActivityCreate, user: User) -> Activity:
    _get_trip_or_error(trip_id, user)
    activity = trip_store.create_activity(trip_id, day_id, act_create, user.id)
    if activity is None:
        if trip_store.get_day_by_id(trip_id, day_id, user.id) is None:
            raise TripDayNotFoundError(f"Day {day_id} not found in trip {trip_id}")
        raise TripNotFoundError(f"Trip {trip_id} not found")
    return activity


def update_existing_activity(trip_id: str, day_id: str, activity_id: str, act_update: ActivityUpdate, user: User) -> Activity:
    _get_trip_or_error(trip_id, user)
    if trip_store.get_day_by_id(trip_id, day_id, user.id) is None:
        raise TripDayNotFoundError(f"Day {day_id} not found in trip {trip_id}")
    activity = trip_store.update_activity(trip_id, day_id, activity_id, act_update, user.id)
    if activity is None:
        raise ActivityNotFoundError(f"Activity {activity_id} not found in day {day_id}")
    return activity


def remove_activity(trip_id: str, day_id: str, activity_id: str, user: User) -> None:
    _get_trip_or_error(trip_id, user)
    if trip_store.get_day_by_id(trip_id, day_id, user.id) is None:
        raise TripDayNotFoundError(f"Day {day_id} not found in trip {trip_id}")
    deleted = trip_store.delete_activity(trip_id, day_id, activity_id, user.id)
    if not deleted:
        raise ActivityNotFoundError(f"Activity {activity_id} not found in day {day_id}")


def get_budget_summary(trip_id: str, user: User) -> BudgetSummary:
    _get_trip_or_error(trip_id, user)
    summary = trip_store.calculate_budget_summary(trip_id, user.id)
    if summary is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    return BudgetSummary(**summary)


def update_budget(trip_id: str, budget_update: BudgetUpdate, user: User) -> BudgetSummary:
    _get_trip_or_error(trip_id, user)
    if budget_update.budget < 0:
        raise BudgetValidationError("Budget must be greater than or equal to zero")
    trip = trip_store.update_budget(trip_id, budget_update.budget, budget_update.currency, user.id)
    if trip is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    summary = trip_store.calculate_budget_summary(trip_id, user.id)
    return BudgetSummary(**summary)


def _validate_expense_date(expense_date: date, trip_id: str, user: User) -> None:
    date_range = trip_store.get_trip_date_range(trip_id, user.id)
    if date_range is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    start_str, end_str = date_range
    trip_start = date.fromisoformat(start_str)
    trip_end = date.fromisoformat(end_str)
    if expense_date < trip_start or expense_date > trip_end:
        raise ExpenseValidationError(
            f"Expense date must be within trip dates ({trip_start.isoformat()} to {trip_end.isoformat()})"
        )


def list_expenses(trip_id: str, user: User) -> List[Expense]:
    _get_trip_or_error(trip_id, user)
    expenses = trip_store.get_all_expenses(trip_id, user.id)
    if expenses is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    return expenses


def get_expense(trip_id: str, expense_id: str, user: User) -> Expense:
    _get_trip_or_error(trip_id, user)
    expense = trip_store.get_expense_by_id(trip_id, expense_id, user.id)
    if expense is None:
        raise ExpenseNotFoundError(f"Expense {expense_id} not found in trip {trip_id}")
    return expense


def create_new_expense(trip_id: str, expense_create: ExpenseCreate, user: User) -> Expense:
    trip = _get_trip_or_error(trip_id, user)
    if expense_create.currency != trip.currency:
        raise ExpenseValidationError(
            f"Expense currency ({expense_create.currency}) must match trip currency ({trip.currency})"
        )
    if expense_create.amount <= 0:
        raise ExpenseValidationError("Expense amount must be greater than zero")
    _validate_expense_date(expense_create.date, trip_id, user)
    expense = trip_store.create_expense(trip_id, expense_create, user.id)
    if expense is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    return expense


def update_existing_expense(trip_id: str, expense_id: str, expense_update: ExpenseUpdate, user: User) -> Expense:
    trip = _get_trip_or_error(trip_id, user)
    existing = trip_store.get_expense_by_id(trip_id, expense_id, user.id)
    if existing is None:
        raise ExpenseNotFoundError(f"Expense {expense_id} not found in trip {trip_id}")

    currency_to_check = expense_update.currency if expense_update.currency is not None else existing.currency
    if currency_to_check != trip.currency:
        raise ExpenseValidationError(
            f"Expense currency ({currency_to_check}) must match trip currency ({trip.currency})"
        )

    if expense_update.amount is not None and expense_update.amount <= 0:
        raise ExpenseValidationError("Expense amount must be greater than zero")

    date_to_check = expense_update.date if expense_update.date is not None else existing.date
    if expense_update.date is not None:
        _validate_expense_date(date_to_check, trip_id, user)

    expense = trip_store.update_expense(trip_id, expense_id, expense_update, user.id)
    if expense is None:
        raise ExpenseNotFoundError(f"Expense {expense_id} not found in trip {trip_id}")
    return expense


def remove_expense(trip_id: str, expense_id: str, user: User) -> None:
    _get_trip_or_error(trip_id, user)
    deleted = trip_store.delete_expense(trip_id, expense_id, user.id)
    if not deleted:
        raise ExpenseNotFoundError(f"Expense {expense_id} not found in trip {trip_id}")


def reset_seed_data() -> None:
    trip_store.reset_to_seed_data()
    auth_service.reset_users_to_seed()
