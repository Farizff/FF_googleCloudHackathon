from fastapi import FastAPI

from api.routes.chat import router as chat_router
from api.routes.disruptions import router as disruptions_router
from api.routes.flight_status import router as flight_status_router
from api.routes.flights import router as flights_router
from api.routes.group import router as group_router
from api.routes.itinerary import router as itinerary_router
from api.routes.judge import router as judge_router
from api.routes.trip import router as trip_router

app = FastAPI(title="Bounce API", version="v0")
app.include_router(chat_router)
app.include_router(disruptions_router)
app.include_router(flight_status_router)
app.include_router(flights_router)
app.include_router(group_router)
app.include_router(itinerary_router)
app.include_router(judge_router)
app.include_router(trip_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Return a minimal health response for Cloud Run and local checks."""
    return {"status": "ok", "app": "Bounce", "version": "v0"}
