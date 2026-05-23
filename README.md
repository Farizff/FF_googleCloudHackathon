# Bounce

The only AI travel agent built for groups.

Bounce is an AI-powered group travel planning app for the Google Cloud Rapid Agent Hackathon 2026, MongoDB Partner Track.

## Product docs

These two synchronized v2.1 docs are the project source of truth:

- [Technical PRD](docs/prd/bounce_prd_v2.md) — tool contracts, schemas, algorithms, cloud setup, demo scenario data, and build order.
- [Design System](docs/design/bounce_design_v2.md) — UI styling, screens, flows, components, visual identity, and microcopy.

When a feature crosses the boundary, use the PRD for data/logic and the Design System for presentation.

## Deployment target

- Google Cloud project: `bounce-hackathon-2026`
- Default Google Cloud region: `asia-southeast1` (Singapore)
- Backend hosting: Google Cloud Run
- Frontend hosting: Firebase Hosting
- Primary database: MongoDB Atlas M0
- Live sync/chat: Firebase Realtime Database

## Local backend quick start

```bash
python -m venv .venv
source .venv/Scripts/activate  # Git Bash on Windows
python -m pip install -r requirements.txt
python -m pytest
uvicorn api.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok","app":"Bounce","version":"v0"}
```

## Current implementation status

Foundation is being built first:

- Source docs stored in repo
- PRD directory skeleton
- Minimal FastAPI backend
- Health endpoint test

External integrations are added only after the deterministic local loop works.
