from fastapi import FastAPI

from api.routes.disruptions import router as disruptions_router
from api.routes.judge import router as judge_router

app = FastAPI(title="Bounce API", version="v0")
app.include_router(disruptions_router)
app.include_router(judge_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Return a minimal health response for Cloud Run and local checks."""
    return {"status": "ok", "app": "Bounce", "version": "v0"}
