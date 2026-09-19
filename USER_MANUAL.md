# Trip Planner MVP v1 — User Manual

A complete guide to using the Trip Planner web application.

---

## Getting Started

### Prerequisites

- **Python 3.10** or newer
- **pip** (Python package manager)
- A modern web browser (Chrome, Firefox, Edge, Safari)

### Installation

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment (recommended):**

   **Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   **Windows (Command Prompt):**
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate.bat
   ```

   **macOS / Linux:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

From the `backend` directory (with your virtual environment activated):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Once the server starts, open your browser and visit:

- **Application:** <http://localhost:8000/>
- **Interactive API Docs (Swagger UI):** <http://localhost:8000/docs>
- **ReDoc API Docs:** <http://localhost:8000/redoc>
- **Health Check:** <http://localhost:8000/api/health>

> The `--reload` flag automatically restarts the server when code files change. This is useful during development.

### Stopping the Server

Press `Ctrl + C` in the terminal window where the server is running.

---

## Application Overview

The Trip Planner consists of three main screens:

1. **Trips List** — View all of your trips
2. **Create / Edit Trip** — Add or modify a trip
3. **Trip Details** — Manage a trip's itinerary (days and activities)

### Navigation

- Click the **Trip Planner** logo/title in the header at any time to return to the Trips List.
- Use the **Back to Trips** button on other screens to go back.
- Use the **Reset Data** button in the top-right to restore all data to the initial sample state (see [Resetting Data](#resetting-data)).

---

## Trips List

The Trips List is the home screen of the application. It displays all your trips as cards in a responsive grid.

Each trip card shows:
- **Destination** (on the colored banner at top)
- **Trip Name**
- **Date Range** (Start date — End date)
- **Duration** (number of days)
- **Itinerary Summary** (number of days added + number of activities planned)

### Creating a New Trip

1. Click the **Create Trip** button (purple, top-right).
2. Fill in the form fields:
   - **Trip Name** (required) — e.g., "Summer Europe Tour"
   - **Destination** (required) — e.g., "France, Italy, Spain"
   - **Start Date** (required) — First day of the trip
   - **End Date** (required) — Last day of the trip (must be on or after start date)
3. Click **Create Trip**.

You will be automatically taken to the Trip Details page to build the itinerary.

### Viewing Trip Details

- Click **View Details** on any trip card to open the Trip Details page.

### Editing a Trip

- Click the **pencil icon** (Edit) on any trip card.
  OR
- From the Trip Details page, click the **Edit Trip** button.

Make changes in the form and click **Save Changes**.

### Deleting a Trip

- Click the **trash icon** (Delete) on any trip card.
  OR
- From the Trip Details page, click the **Delete** button.
- Confirm the deletion when prompted.

> ⚠️ **Warning:** Deleting a trip permanently removes it and all its days and activities. This action cannot be undone.

---

## Trip Details

The Trip Details page lets you build and manage the full itinerary for a trip.

### Trip Header

At the top, you will find:
- Trip **destination** and **name**
- **Date range**, **duration**, and **itinerary summary** (total days + activities)
- **Edit Trip** and **Delete** buttons

### Itinerary Section

The Itinerary section lists each day of your trip in chronological order.

### Adding a Day

1. Click the **Add Day** button (purple, top-right of the Itinerary section).
2. In the popup form:
   - **Date** (required) — The date for this day. Should fall within the trip's date range.
   - **Title** (optional) — A short title for the day, e.g., "Arrival in Paris", "Beach Day", "Travel to Rome".
3. Click **Add Day**.

> **Tip:** You can add days on any date (including dates outside the trip range — the app does not enforce this currently, but it's good practice to keep days inside the trip's start/end dates).

### Editing a Day

1. Click the **pencil icon** (Edit day) in the top-right corner of the day card.
2. Update the date and/or title.
3. Click **Save Changes**.

### Deleting a Day

1. Click the **trash icon** (Delete day) in the top-right corner of the day card.
2. Confirm the deletion when prompted.

> ⚠️ **Warning:** Deleting a day also deletes all activities assigned to that day.

---

## Activities

Each day can have multiple activities (attractions, events, transportation, meals, etc.).

### Adding an Activity

1. On any day card, click the **Add Activity** button (outlined, dashed border) at the bottom of the card.
2. In the popup form:
   - **Activity Name** (required) — e.g., "Visit the Eiffel Tower"
   - **Location** (optional) — e.g., "Champ de Mars, Paris"
   - **Description** (optional) — Any notes, such as booking confirmations, tips, times, etc.
3. Click **Add Activity**.

### Editing an Activity

1. Click the **pencil icon** to the right of the activity.
2. Update any fields.
3. Click **Save Changes**.

### Deleting an Activity

1. Click the **trash icon** to the right of the activity.
2. Confirm the deletion when prompted.

---

## Resetting Data

At any time, you can restore the application to its original state with three sample trips.

### Option 1: Via the UI

1. Click the **Reset Data** button in the top-right header of any screen.
2. Confirm the reset when prompted.

### Option 2: Via the API

Using `curl`, Postman, or any HTTP client:

```bash
curl -X POST http://localhost:8000/api/system/reset
```

### Sample Trips Included

After reset, the following trips are available:

1. **Vietnam Adventure** (Vietnam) — Oct 1–10, 2026
   - Day 1: Arrival in Hanoi (Old Quarter walking tour, airport transfer)
   - Day 2: Ha Long Bay Cruise (Ha Long Bay, night market)
   - Day 3: Hanoi to Da Nang (flight)

2. **Tokyo Discovery** (Japan) — Nov 15–22, 2026
   - Day 1: Arrival and Shibuya (Shibuya Crossing)
   - Day 2: Ancient Asakusa (Senso-ji Temple)

3. **European Backpacking** (Europe) — May 1–14, 2027
   - Empty itinerary (ready for you to build!)

---

## Data Storage

All trip data is saved to a single JSON file at:

```
data/trips.json
```

This file is created automatically when you first run the application.

### Backing Up Your Data

To back up your trips, simply copy the `data/trips.json` file to a safe location. To restore, copy it back (while the server is not running).

### Moving Data Between Installs

The `trips.json` file is fully portable. You can copy it to another instance of the Trip Planner (same version) and it will work without modification.

---

## Validation Rules

The application enforces the following rules:

### Trips
- **Trip Name:** Cannot be empty
- **Destination:** Cannot be empty
- **Start Date:** Required
- **End Date:** Required, and cannot be earlier than Start Date

### Days
- **Date:** Required

### Activities
- **Activity Name:** Cannot be empty

> Validation is performed in both the browser (client-side) and on the server (server-side). Server-side validation always takes precedence.

---

## Troubleshooting

### The server won't start

**Check Python version:**
```bash
python --version
```
You need Python 3.10 or newer.

**Check if port 8000 is already in use:**
Try a different port:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```
Then visit `http://localhost:8080/`.

**Reinstall dependencies:**
```bash
pip install --force-reinstall -r requirements.txt
```

### The website shows a blank page / errors

1. Open the browser's **Developer Tools** (F12) and check the **Console** tab for errors.
2. Check the terminal where the server is running for any error messages.
3. Ensure you've completed the Installation steps (especially `pip install -r requirements.txt`).

### Trips aren't saving

- Check that the `data/` folder exists in the project root and is writable.
- Check the server terminal for file permission errors.
- If `trips.json` was manually edited, ensure it is valid JSON. (You can use a JSON linter online.)

### Date inputs don't work on my browser

Ensure you are using a modern, updated browser. Date inputs are standard HTML5 features supported by all recent browsers.

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Submit a form (while typing in a field) | `Enter` |
| Close a modal/popup | Click outside modal or press `Esc` |

---

## Tips for Effective Trip Planning

1. **Plan your dates first** — Create the trip with accurate start/end dates, then add days in order.
2. **Give days meaningful titles** — Instead of "Day 1", use "Arrival in Bangkok" to make scanning easier.
3. **Add locations to activities** — Future versions will use these for maps and budget features.
4. **Use descriptions for details** — Store booking numbers, opening hours, and tips there.
5. **Reset if something goes wrong** — The Reset Data button is non-destructive for the sample trips and always produces a known-good state.

---

## Technical Notes (Advanced Users)

### API Usage

All UI actions are backed by a fully-documented REST API. You can explore it at:

- **Swagger UI (interactive):** <http://localhost:8000/docs>
- **OpenAPI JSON schema:** <http://localhost:8000/openapi.json>

This allows you to script bulk imports, export data, or connect other tools programmatically.

### Example: Creating a Trip via API

```bash
curl -X POST http://localhost:8000/api/trips \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekend in Lisbon",
    "destination": "Portugal",
    "start_date": "2027-03-05",
    "end_date": "2027-03-07"
  }'
```

---

## Getting Help

For technical issues, refer to:
1. This user manual
2. The project's `README.md` for architecture and setup details
3. The Swagger API docs at `/docs` for API-specific help

---

*Version 1.0.0 — Trip Planner MVP*
