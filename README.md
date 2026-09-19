# Trip Planner MVP (Version 1)

A small, simple Trip Planner web application built as the foundation for a Test Automation Engineering training course.

## Application Description

The Trip Planner allows users to create and manage travel itineraries. Each itinerary (trip) contains a name, destination, date range, and a set of days, each of which can have multiple activities/attractions.

This is Version 1 — intentionally small, simple, and deterministic, designed for easy testing and future extension.

## Architecture Overview

```
┌───────────────────────────────────────────┐
│  Frontend (HTML + Vanilla JS + Tailwind)  │
└───────────────────┬───────────────────────┘
                    │  REST API (JSON)
┌───────────────────▼───────────────────────┐
│         FastAPI Backend (Python)          │
│  ┌─────────────┐  ┌───────────────────┐   │
│  │   Routes    │  │  Business Logic   │   │
│  └──────┬──────┘  └────────┬──────────┘   │
│         └────────┬─────────┘              │
│         ┌────────▼─────────┐              │
│         │ Persistence Layer│              │
│         └────────┬─────────┘              │
└──────────────────┼────────────────────────┘
         ┌─────────▼─────────┐
         │  JSON File Store  │
         │   data/trips.json │
         └───────────────────┘
```

## Technology Stack

### Backend
- **Python 3.10+**
- **FastAPI** — Web framework for REST API
- **Pydantic** — Data validation
- **Uvicorn** — ASGI server

### Frontend
- **HTML5** — Markup
- **Vanilla JavaScript (ES6+)** — UI logic (no frameworks)
- **Tailwind CSS** (via CDN) — Styling
- **REST API** — Communication with backend

### Data Persistence
- **JSON file** (`data/trips.json`) — No database in Version 1

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- A modern web browser

## Installation

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create a virtual environment (recommended):

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## How to Run the Backend

From the `backend` directory (with virtual environment activated):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will start on:
- **API**: `http://localhost:8000/api/`
- **Frontend**: `http://localhost:8000/`
- **API Docs (Swagger UI)**: `http://localhost:8000/docs`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`
- **Health check**: `http://localhost:8000/api/health`

The `--reload` flag enables hot-reloading during development.

## How to Run the Frontend

The frontend is served automatically by the FastAPI backend at `http://localhost:8000/`. There is no separate frontend server required.

On first run, seed data is automatically created in `data/trips.json`.

## API Overview

### Trips

| Method | Endpoint                 | Description              |
|--------|--------------------------|--------------------------|
| GET    | `/api/trips`             | List all trips           |
| POST   | `/api/trips`             | Create a new trip        |
| GET    | `/api/trips/{trip_id}`   | Get trip details         |
| PUT    | `/api/trips/{trip_id}`   | Update a trip            |
| DELETE | `/api/trips/{trip_id}`   | Delete a trip            |

### Trip Days

| Method | Endpoint                                      | Description                |
|--------|-----------------------------------------------|----------------------------|
| GET    | `/api/trips/{trip_id}/days`                   | List days for a trip       |
| POST   | `/api/trips/{trip_id}/days`                   | Add a day to a trip        |
| GET    | `/api/trips/{trip_id}/days/{day_id}`          | Get day details            |
| PUT    | `/api/trips/{trip_id}/days/{day_id}`          | Update a day               |
| DELETE | `/api/trips/{trip_id}/days/{day_id}`          | Delete a day               |

### Activities

| Method | Endpoint                                                                    | Description                   |
|--------|-----------------------------------------------------------------------------|-------------------------------|
| GET    | `/api/trips/{trip_id}/days/{day_id}/activities`                            | List activities for a day     |
| POST   | `/api/trips/{trip_id}/days/{day_id}/activities`                            | Add an activity to a day      |
| GET    | `/api/trips/{trip_id}/days/{day_id}/activities/{activity_id}`              | Get activity details          |
| PUT    | `/api/trips/{trip_id}/days/{day_id}/activities/{activity_id}`              | Update an activity           |
| DELETE | `/api/trips/{trip_id}/days/{day_id}/activities/{activity_id}`              | Delete an activity           |

### System

| Method | Endpoint               | Description                    |
|--------|------------------------|--------------------------------|
| POST   | `/api/system/reset`    | Reset all data to seed state   |
| GET    | `/api/health`          | Health check endpoint          |

### HTTP Status Codes

- **200 OK** — Successful retrieval or update
- **201 Created** — Successful creation
- **204 No Content** — Successful deletion
- **400 Bad Request** — Invalid input or validation error
- **404 Not Found** — Requested entity does not exist

Error responses use the format:

```json
{
    "detail": "Trip not found"
}
```

## Data Storage Explanation

All data is stored in a single JSON file at `data/trips.json` (relative to the project root).

The persistence layer (`backend/app/data/trip_store.py`) abstracts all read/write operations. The API routes and business logic never access the JSON file directly.

This design is intentional: a future version will replace the JSON store with SQLite by updating only the persistence layer, with no changes needed to the API routes or business logic.

**Data Model:**

```json
{
  "id": "trip-1",
  "name": "Vietnam Adventure",
  "destination": "Vietnam",
  "start_date": "2026-10-01",
  "end_date": "2026-10-10",
  "days": [
    {
      "id": "day-1-1",
      "date": "2026-10-01",
      "title": "Arrival in Hanoi",
      "activities": [
        {
          "id": "act-1-1-1",
          "name": "Arrive in Hanoi",
          "location": "Noi Bai Airport",
          "description": "..."
        }
      ]
    }
  ]
}
```

## Project Structure

```
trip-planner-v1/
├── backend/
│   ├── main.py                      # FastAPI app entry point
│   ├── requirements.txt             # Python dependencies
│   └── app/
│       ├── models/
│       │   └── schemas.py           # Pydantic models (Trip, Day, Activity)
│       ├── services/
│       │   └── trip_service.py      # Business logic / service layer
│       ├── data/
│       │   ├── trip_store.py        # Persistence layer (JSON file)
│       │   └── seed_data.py         # Initial seed data
│       └── routers/
│           ├── trips.py             # Trip CRUD endpoints
│           ├── days.py              # Day CRUD endpoints
│           ├── activities.py        # Activity CRUD endpoints
│           └── system.py            # System/reset endpoints
├── frontend/
│   ├── index.html                   # Main HTML page (all views)
│   └── app.js                       # Frontend UI logic (Vanilla JS)
├── data/
│   └── trips.json                   # Data file (created automatically)
└── context/
    └── Prompt 1 - ... .md           # Original specification
```

## How to Reset Seed Data

There are two ways to reset the application to its initial state:

### Option 1: Via the UI
Click the **Reset Data** button in the top-right header of the application.

### Option 2: Via the API
```bash
curl -X POST http://localhost:8000/api/system/reset
```

Both methods will restore the 3 sample trips and overwrite any changes.

## Validation Rules

The application enforces the following validation rules (both client-side and server-side):

- **Trip name**: Required, cannot be empty
- **Destination**: Required, cannot be empty
- **Start date**: Required
- **End date**: Required, cannot be earlier than start date
- **Day date**: Required
- **Activity name**: Required, cannot be empty

## Automation-Friendly Design

The application is designed for automated testing:

- Stable HTML structure with semantic elements
- `data-testid` attributes on key interactive elements (buttons, forms, inputs)
- Predictable REST API with consistent JSON responses
- Deterministic seed data (no randomization)
- No unnecessary animations or timing-dependent behavior
- IDs use a readable prefix pattern (`trip-*`, `day-*`, `act-*`)

## Future Versions

This application will evolve in future versions to add:
- User Registration and Login
- Travel costs and budget management
- Travel journal
- Mobile/responsive support
- SQLite database persistence
- Additional QA/testing scenarios

The architecture is designed to support these additions with minimal changes to existing code.
