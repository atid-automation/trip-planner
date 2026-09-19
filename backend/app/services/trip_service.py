from typing import List, Optional
from fastapi import HTTPException

from app.models.schemas import (
    Trip, TripCreate, TripUpdate,
    TripDay, TripDayCreate, TripDayUpdate,
    Activity, ActivityCreate, ActivityUpdate
)
from app.data import trip_store


class TripNotFoundError(Exception):
    pass


class TripDayNotFoundError(Exception):
    pass


class ActivityNotFoundError(Exception):
    pass


def list_all_trips() -> List[Trip]:
    return trip_store.get_all_trips()


def get_trip(trip_id: str) -> Trip:
    trip = trip_store.get_trip_by_id(trip_id)
    if trip is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    return trip


def create_new_trip(trip_create: TripCreate) -> Trip:
    return trip_store.create_trip(trip_create)


def update_existing_trip(trip_id: str, trip_update: TripUpdate) -> Trip:
    trip = trip_store.update_trip(trip_id, trip_update)
    if trip is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    return trip


def remove_trip(trip_id: str) -> None:
    deleted = trip_store.delete_trip(trip_id)
    if not deleted:
        raise TripNotFoundError(f"Trip {trip_id} not found")


def list_days(trip_id: str) -> List[TripDay]:
    days = trip_store.get_days_for_trip(trip_id)
    if days is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    return days


def get_day(trip_id: str, day_id: str) -> TripDay:
    if trip_store.get_trip_by_id(trip_id) is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    day = trip_store.get_day_by_id(trip_id, day_id)
    if day is None:
        raise TripDayNotFoundError(f"Day {day_id} not found in trip {trip_id}")
    return day


def create_new_day(trip_id: str, day_create: TripDayCreate) -> TripDay:
    day = trip_store.create_day(trip_id, day_create)
    if day is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    return day


def update_existing_day(trip_id: str, day_id: str, day_update: TripDayUpdate) -> TripDay:
    if trip_store.get_trip_by_id(trip_id) is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    day = trip_store.update_day(trip_id, day_id, day_update)
    if day is None:
        raise TripDayNotFoundError(f"Day {day_id} not found in trip {trip_id}")
    return day


def remove_day(trip_id: str, day_id: str) -> None:
    if trip_store.get_trip_by_id(trip_id) is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    deleted = trip_store.delete_day(trip_id, day_id)
    if not deleted:
        raise TripDayNotFoundError(f"Day {day_id} not found in trip {trip_id}")


def list_activities(trip_id: str, day_id: str) -> List[Activity]:
    if trip_store.get_trip_by_id(trip_id) is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    activities = trip_store.get_activities_for_day(trip_id, day_id)
    if activities is None:
        raise TripDayNotFoundError(f"Day {day_id} not found in trip {trip_id}")
    return activities


def get_activity(trip_id: str, day_id: str, activity_id: str) -> Activity:
    if trip_store.get_trip_by_id(trip_id) is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    if trip_store.get_day_by_id(trip_id, day_id) is None:
        raise TripDayNotFoundError(f"Day {day_id} not found in trip {trip_id}")
    activity = trip_store.get_activity_by_id(trip_id, day_id, activity_id)
    if activity is None:
        raise ActivityNotFoundError(f"Activity {activity_id} not found in day {day_id}")
    return activity


def create_new_activity(trip_id: str, day_id: str, act_create: ActivityCreate) -> Activity:
    activity = trip_store.create_activity(trip_id, day_id, act_create)
    if activity is None:
        if trip_store.get_trip_by_id(trip_id) is None:
            raise TripNotFoundError(f"Trip {trip_id} not found")
        raise TripDayNotFoundError(f"Day {day_id} not found in trip {trip_id}")
    return activity


def update_existing_activity(trip_id: str, day_id: str, activity_id: str, act_update: ActivityUpdate) -> Activity:
    if trip_store.get_trip_by_id(trip_id) is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    if trip_store.get_day_by_id(trip_id, day_id) is None:
        raise TripDayNotFoundError(f"Day {day_id} not found in trip {trip_id}")
    activity = trip_store.update_activity(trip_id, day_id, activity_id, act_update)
    if activity is None:
        raise ActivityNotFoundError(f"Activity {activity_id} not found in day {day_id}")
    return activity


def remove_activity(trip_id: str, day_id: str, activity_id: str) -> None:
    if trip_store.get_trip_by_id(trip_id) is None:
        raise TripNotFoundError(f"Trip {trip_id} not found")
    if trip_store.get_day_by_id(trip_id, day_id) is None:
        raise TripDayNotFoundError(f"Day {day_id} not found in trip {trip_id}")
    deleted = trip_store.delete_activity(trip_id, day_id, activity_id)
    if not deleted:
        raise ActivityNotFoundError(f"Activity {activity_id} not found in day {day_id}")


def reset_seed_data() -> None:
    trip_store.reset_to_seed_data()
