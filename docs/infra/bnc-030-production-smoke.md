# BNC-030 — Production Deployment and Smoke Tests

Date: 2026-05-24

## Result

BNC-030 has a production smoke checkpoint deployed on Cloud Run. The public API URL and Cloud Run-hosted frontend URL are live, `/health` passes, judge instructions are live, and live `/chat` publishes to Firebase RTDB.

The remaining MongoDB-backed judge write actions are blocked by BNC-017 because Atlas Network Access still appears to reject Cloud Run egress. Secret Manager and Cloud Run MongoDB wiring now exist.

## Deployment target

- Google Cloud project: `project-411e0419-48bd-4b5b-97f`
- Region: `asia-southeast1`
- Cloud Run service: `bounce-api`
- Revision: `bounce-api-00011-gj6`
- Public URL: <https://bounce-api-4dynllwdeq-as.a.run.app>
- Alternate URL reported by deploy: <https://bounce-api-167980864337.asia-southeast1.run.app>

## Runtime configuration verified

Cloud Run environment currently includes:

- `GCP_PROJECT_ID=project-411e0419-48bd-4b5b-97f`
- `GCP_REGION=asia-southeast1`
- `FIREBASE_DATABASE_URL=https://project-411e0419-48bd-4b5b-97f-default-rtdb.asia-southeast1.firebasedatabase.app`
- `MONGODB_DATABASE=bounce`
- `MONGODB_CONNECTION_STRING` from Secret Manager secret `mongodb-uri:latest`

Secret Manager now contains `mongodb-uri`. The remaining blocker is Atlas Network Access for Cloud Run egress.

## Changes made during BNC-030

- Added `frontend` to the Docker build context and Dockerfile so Cloud Run serves the hosted app shell at `/`.
- Removed `frontend` from `.dockerignore`.
- Added regression coverage that Cloud Run runtime packaging includes both `workers` and `frontend`.
- Changed judge MongoDB dependency failures from unhandled 500s into loud `503 MONGODB_PROVIDER_NOT_CONFIGURED` / `503 MONGODB_PROVIDER_UNAVAILABLE` responses.
- Added regression coverage for the judge 503 behavior.

## Verification

Local tests:

```text
python -m pytest tests/infra/test_cloud_run_docker_context.py tests/api/test_judge.py
7 passed

python -m pytest
138 passed
```

Cloud Run deploy:

```text
Service [bounce-api] revision [bounce-api-00011-gj6] has been deployed and is serving 100 percent of traffic.
```

Smoke tests:

```text
GET /health -> HTTP 200
{"status":"ok","app":"Bounce","version":"v0"}

GET / -> HTTP 200
<title>Bounce — Group travel genius</title>

GET /app.js -> HTTP 200
const API_BASE = window.BOUNCE_API_BASE || '';

GET /judge/instructions -> HTTP 200
Bounce Judge Test Mode

POST /judge/seed-demo-trip -> HTTP 503
{"detail":{"code":"MONGODB_PROVIDER_UNAVAILABLE","message":"Atlas TLS handshake failed from Cloud Run; allow Cloud Run egress in Atlas Network Access."}}

POST /chat -> HTTP 200
planning_response_path=/trips/trip_bnc030_smoke/threads/main/msg_5e3a080066764f2e9d09d08c534a725b
```

Firebase RTDB smoke:

```text
Readback confirmed messages under /trips/trip_bnc030_smoke/threads/main.
Probe data was deleted after verification.
```

## Boundary / blocker

BNC-030 cannot be fully closed as production-complete until Atlas Network Access allows Cloud Run to connect to MongoDB. Until then:

- `/health` is live.
- The hosted app shell is live at `/`.
- `/judge/instructions` is live.
- `/chat` works and writes to Firebase RTDB.
- Cloud Run has `MONGODB_CONNECTION_STRING` from Secret Manager.
- MongoDB-backed judge mutations correctly fail loud with `503 MONGODB_PROVIDER_UNAVAILABLE`.

## Next recommended card

`BNC-017 — add Atlas Network Access allowlist for Cloud Run egress, then rerun deployed judge smoke tests`
