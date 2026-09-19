from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.routers import trips, days, activities, system, auth, budget, expenses
from app.services import auth_service

app = FastAPI(
    title="Trip Planner API",
    description="Version 3 - Trip Planner with Budget Management",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(trips.router)
app.include_router(days.router)
app.include_router(activities.router)
app.include_router(budget.router)
app.include_router(expenses.router)
app.include_router(system.router)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok", "version": "3.0.0"}


@app.on_event("startup")
async def on_startup():
    auth_service.ensure_seed_users()
