import json
import os
import uuid
from typing import List, Optional, Dict, Any
from pathlib import Path

from app.models.schemas import (
    Trip, TripCreate, TripUpdate,
    TripDay, TripDayCreate, TripDayUpdate,
    Activity, ActivityCreate, ActivityUpdate
)
from app.data.seed_data import SEED_TRIPS


DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
TRIPS_FILE = DATA_DIR / "trips.json"


def _ensure_data_dir() -> None:
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_trips_file() -> List[Dict[str, Any]]:
    _ensure_data_dir()
    if not TRIPS_FILE.exists():
        reset_to_seed_data()
    with open(TRIPS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_trips_file(trips: List[Dict[str, Any]]) -> None:
    _ensure_data_dir()
    with open(TRIPS_FILE, "w", encoding="utf-8") as f:
        json.dump(trips, f, indent=2, ensure_ascii=False)


def reset_to_seed_data() -> None:
    _ensure_data_dir()
    _write_trips_file(SEED_TRIPS)


def _generate_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _dict_to_trip(data: Dict[str, Any]) -> Trip:
    days = [_dict_to_trip_day(d) for d in data.get("days", [])]
    return Trip(
        id=data["id"],
        name=data["name"],
        destination=data["destination"],
        start_date=data["start_date"],
        end_date=data["end_date"],
        days=days
    )


def _dict_to_trip_day(data: Dict[str, Any]) -> TripDay:
    activities = [_dict_to_activity(a) for a in data.get("activities", [])]
    return TripDay(
        id=data["id"],
        date=data["date"],
        title=data.get("title"),
        activities=activities
    )


def _dict_to_activity(data: Dict[str, Any]) -> Activity:
    return Activity(
        id=data["id"],
        name=data["name"],
        location=data.get("location"),
        description=data.get("description")
    )


def get_all_trips() -> List[Trip]:
    trips_data = _read_trips_file()
    return [_dict_to_trip(t) for t in trips_data]


def get_trip_by_id(trip_id: str) -> Optional[Trip]:
    trips_data = _read_trips_file()
    for t in trips_data:
        if t["id"] == trip_id:
            return _dict_to_trip(t)
    return None


def create_trip(trip_create: TripCreate) -> Trip:
    trips_data = _read_trips_file()
    new_trip_id = _generate_id("trip")
    new_trip = {
        "id": new_trip_id,
        "name": trip_create.name,
        "destination": trip_create.destination,
        "start_date": trip_create.start_date.isoformat(),
        "end_date": trip_create.end_date.isoformat(),
        "days": []
    }
    trips_data.append(new_trip)
    _write_trips_file(trips_data)
    return _dict_to_trip(new_trip)


def update_trip(trip_id: str, trip_update: TripUpdate) -> Optional[Trip]:
    trips_data = _read_trips_file()
    for i, t in enumerate(trips_data):
        if t["id"] == trip_id:
            if trip_update.name is not None:
                t["name"] = trip_update.name
            if trip_update.destination is not None:
                t["destination"] = trip_update.destination
            if trip_update.start_date is not None:
                t["start_date"] = trip_update.start_date.isoformat()
            if trip_update.end_date is not None:
                t["end_date"] = trip_update.end_date.isoformat()
            trips_data[i] = t
            _write_trips_file(trips_data)
            return _dict_to_trip(t)
    return None


def delete_trip(trip_id: str) -> bool:
    trips_data = _read_trips_file()
    original_len = len(trips_data)
    trips_data = [t for t in trips_data if t["id"] != trip_id]
    if len(trips_data) < original_len:
        _write_trips_file(trips_data)
        return True
    return False


def get_days_for_trip(trip_id: str) -> Optional[List[TripDay]]:
    trip = get_trip_by_id(trip_id)
    if trip is None:
        return None
    return trip.days


def get_day_by_id(trip_id: str, day_id: str) -> Optional[TripDay]:
    trip = get_trip_by_id(trip_id)
    if trip is None:
        return None
    for d in trip.days:
        if d.id == day_id:
            return d
    return None


def create_day(trip_id: str, day_create: TripDayCreate) -> Optional[TripDay]:
    trips_data = _read_trips_file()
    for i, t in enumerate(trips_data):
        if t["id"] == trip_id:
            new_day_id = _generate_id("day")
            new_day = {
                "id": new_day_id,
                "date": day_create.date.isoformat(),
                "title": day_create.title,
                "activities": []
            }
            t["days"].append(new_day)
            trips_data[i] = t
            _write_trips_file(trips_data)
            return _dict_to_trip_day(new_day)
    return None


def update_day(trip_id: str, day_id: str, day_update: TripDayUpdate) -> Optional[TripDay]:
    trips_data = _read_trips_file()
    for i, t in enumerate(trips_data):
        if t["id"] == trip_id:
            for j, d in enumerate(t["days"]):
                if d["id"] == day_id:
                    if day_update.date is not None:
                        d["date"] = day_update.date.isoformat()
                    if day_update.title is not None:
                        d["title"] = day_update.title
                    trips_data[i]["days"][j] = d
                    _write_trips_file(trips_data)
                    return _dict_to_trip_day(d)
    return None


def delete_day(trip_id: str, day_id: str) -> bool:
    trips_data = _read_trips_file()
    for i, t in enumerate(trips_data):
        if t["id"] == trip_id:
            original_len = len(t["days"])
            t["days"] = [d for d in t["days"] if d["id"] != day_id]
            if len(t["days"]) < original_len:
                trips_data[i] = t
                _write_trips_file(trips_data)
                return True
            return False
    return False


def get_activities_for_day(trip_id: str, day_id: str) -> Optional[List[Activity]]:
    day = get_day_by_id(trip_id, day_id)
    if day is None:
        return None
    return day.activities


def get_activity_by_id(trip_id: str, day_id: str, activity_id: str) -> Optional[Activity]:
    day = get_day_by_id(trip_id, day_id)
    if day is None:
        return None
    for a in day.activities:
        if a.id == activity_id:
            return a
    return None


def create_activity(trip_id: str, day_id: str, act_create: ActivityCreate) -> Optional[Activity]:
    trips_data = _read_trips_file()
    for i, t in enumerate(trips_data):
        if t["id"] == trip_id:
            for j, d in enumerate(t["days"]):
                if d["id"] == day_id:
                    new_act_id = _generate_id("act")
                    new_activity = {
                        "id": new_act_id,
                        "name": act_create.name,
                        "location": act_create.location,
                        "description": act_create.description
                    }
                    d["activities"].append(new_activity)
                    trips_data[i]["days"][j] = d
                    _write_trips_file(trips_data)
                    return _dict_to_activity(new_activity)
    return None


def update_activity(trip_id: str, day_id: str, activity_id: str, act_update: ActivityUpdate) -> Optional[Activity]:
    trips_data = _read_trips_file()
    for i, t in enumerate(trips_data):
        if t["id"] == trip_id:
            for j, d in enumerate(t["days"]):
                if d["id"] == day_id:
                    for k, a in enumerate(d["activities"]):
                        if a["id"] == activity_id:
                            if act_update.name is not None:
                                a["name"] = act_update.name
                            if act_update.location is not None:
                                a["location"] = act_update.location
                            if act_update.description is not None:
                                a["description"] = act_update.description
                            trips_data[i]["days"][j]["activities"][k] = a
                            _write_trips_file(trips_data)
                            return _dict_to_activity(a)
    return None


def delete_activity(trip_id: str, day_id: str, activity_id: str) -> bool:
    trips_data = _read_trips_file()
    for i, t in enumerate(trips_data):
        if t["id"] == trip_id:
            for j, d in enumerate(t["days"]):
                if d["id"] == day_id:
                    original_len = len(d["activities"])
                    d["activities"] = [a for a in d["activities"] if a["id"] != activity_id]
                    if len(d["activities"]) < original_len:
                        trips_data[i]["days"][j] = d
                        _write_trips_file(trips_data)
                        return True
                    return False
    return False
