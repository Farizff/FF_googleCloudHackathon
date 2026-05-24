from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.routes.chat import router as chat_router
from api.routes.disruptions import router as disruptions_router
from api.routes.expenses import router as expenses_router
from api.routes.flight_status import router as flight_status_router
from api.routes.flights import router as flights_router
from api.routes.flights_api import router as flights_api_router
from api.routes.flocks import router as flocks_router
from api.routes.group import router as group_router
from api.routes.itinerary import router as itinerary_router
from api.routes.judge import router as judge_router
from api.routes.scheduler import router as scheduler_router
from api.routes.settlements import router as settlements_router
from api.routes.travel_dna import router as travel_dna_router
from api.routes.trip import router as trip_router

app = FastAPI(title="Bounce API", version="v0")
app.include_router(chat_router)
app.include_router(disruptions_router)
app.include_router(expenses_router)
app.include_router(flight_status_router)
app.include_router(flights_router)
app.include_router(flights_api_router)
app.include_router(flocks_router)
app.include_router(group_router)
app.include_router(itinerary_router)
app.include_router(judge_router)
app.include_router(scheduler_router)
app.include_router(settlements_router)
app.include_router(travel_dna_router)
app.include_router(trip_router)

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"


@app.get("/health")
def health() -> dict[str, str]:
    """Return a minimal health response for Cloud Run and local checks."""
    return {"status": "ok", "app": "Bounce", "version": "v0"}


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
