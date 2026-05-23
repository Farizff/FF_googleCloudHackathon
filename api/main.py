from fastapi import FastAPI

app = FastAPI(title="Bounce API", version="v0")


@app.get("/health")
def health() -> dict[str, str]:
    """Return a minimal health response for Cloud Run and local checks."""
    return {"status": "ok", "app": "Bounce", "version": "v0"}
