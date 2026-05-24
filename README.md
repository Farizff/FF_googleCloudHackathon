# Bounce

The only AI travel agent built for groups.

Bounce is an AI-powered group travel planning app for the Google Cloud Rapid Agent Hackathon 2026, MongoDB Partner Track.

## Live demo

- Live app/API: https://bounce-api-4dynllwdeq-as.a.run.app/
- Health check: https://bounce-api-4dynllwdeq-as.a.run.app/health
- Judge instructions: https://bounce-api-4dynllwdeq-as.a.run.app/judge/instructions

## Judge test mode

Judges can test Bounce without local setup:

```bash
BASE="https://bounce-api-4dynllwdeq-as.a.run.app"

curl "$BASE/health"
curl "$BASE/judge/instructions"
curl -X POST "$BASE/judge/seed-demo-trip"
curl -X POST "$BASE/judge/trigger-disruption"
curl -X POST "$BASE/judge/reset"
```

Suggested judge path:

1. Open the live app.
2. Confirm the API status badge or `/health` response.
3. Review the Tokyo Reunion planning UI: trip prompt, profile details, itinerary, budget, map, and flight options.
4. Review group features: member status, suggestion review, FlockMode creation, Flock schedule, and reconvene details.
5. Review active-trip support: today schedule, flight status, and split-bill UI.
6. Use the judge panel to seed the demo trip, trigger a disruption, and reset if needed.

## Submission package

BNC-031 demo/submission artifacts live under [`docs/submission/`](docs/submission/):

- [`demo-video-script.md`](docs/submission/demo-video-script.md) — 3-minute recording script.
- [`devpost-draft.md`](docs/submission/devpost-draft.md) — copy-ready Devpost draft.
- [`judge-instructions.md`](docs/submission/judge-instructions.md) — copy-ready judge guide.
- [`screenshots/`](docs/submission/screenshots/) — live app screenshot evidence.

## Product docs

These two synchronized v2.1 docs are the project source of truth:

- [Technical PRD](docs/prd/bounce_prd_v2.md) — tool contracts, schemas, algorithms, cloud setup, demo scenario data, and build order.
- [Design System](docs/design/bounce_design_v2.md) — UI styling, screens, flows, components, visual identity, and microcopy.

When a feature crosses the boundary, use the PRD for data/logic and the Design System for presentation.

## Deployment target

- Google Cloud project: `project-411e0419-48bd-4b5b-97f`
- Default Google Cloud region: `asia-southeast1` (Singapore)
- Backend/frontend host: Google Cloud Run service `bounce-api`
- Primary database: MongoDB Atlas
- Live sync/chat: Firebase Realtime Database

## Current implementation status

The fixed Kanban contract is tracked in [`docs/kanban/bounce_fixed_kanban.md`](docs/kanban/bounce_fixed_kanban.md).

Current checkpoint:

- Core backend, agent tools, frontend shell, live Firebase integration, live MongoDB Atlas wiring, Cloud Run deployment, and production smoke checks are complete.
- BNC-031 submission package is prepared in `docs/submission/` and awaits final video upload / Devpost submission.

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

## License

MIT. See [`LICENSE`](LICENSE).
