# BNC-024 Firebase Real-Time Sync Integration

Date: 2026-05-24

## Card

`BNC-024 — Firebase real-time sync integration`

PRD source: `docs/prd/bounce_prd_v2.md` Days 9–11 build sequence and Part 7.4.

## Completion summary

BNC-024 replaces the earlier no-op/local Firebase route seams with a real Firebase Realtime Database REST publisher.

Implemented:

- `api/firebase_rtdb.py`
  - `FirebaseRtdbPublisher`
  - `FirebaseProviderNotConfigured`
  - `FirebasePublishError`
- `/chat` route now publishes Bounce planning responses to:
  - `/trips/{trip_id}/threads/main/{message_id}`
- `/trigger-disruption` route now uses the real RTDB publisher dependency for itinerary state broadcasts when its MongoDB/tool dependencies are available.
- RTDB publisher supports group state writes to:
  - `/trips/{trip_id}/state/group`
- RTDB publisher supports itinerary state writes to:
  - `/trips/{trip_id}/state/itinerary`
- Missing Firebase config now fails loudly with HTTP `503` instead of silently no-oping.
- `.env.example` now points at the live Bounce GCP/Firebase project values.

## Docker deployment fix discovered during verification

Cloud Run source deployment initially failed because the Docker image did not include the `workers` package, while `api.routes.scheduler` imports `workers.flight_poller`.

Fixed:

- `Dockerfile` now copies `workers/` into the image.
- `.dockerignore` no longer excludes `workers/`.
- Added `tests/infra/test_cloud_run_docker_context.py` so this packaging regression is caught before deployment.

## Verification

RED/GREEN TDD:

```text
python -m pytest tests/api/test_firebase_rtdb_publisher.py -q
RED: ModuleNotFoundError: No module named 'api.firebase_rtdb'
GREEN: 4 passed
```

Docker packaging regression test:

```text
python -m pytest tests/infra/test_cloud_run_docker_context.py -q
RED: missing COPY workers ./workers
GREEN: 1 passed
```

Targeted route tests:

```text
python -m pytest tests/api/test_firebase_rtdb_publisher.py tests/api/test_chat.py tests/api/test_disruptions.py tests/agent/test_save_itinerary.py -q
12 passed
```

Full suite:

```text
python -m pytest -q
136 passed
```

Local live RTDB publisher probe:

```text
/trips/trip_bnc024_probe/threads/main/msg_probe
```

RTDB readback confirmed all expected paths before cleanup:

```json
{
  "state": {
    "group": {"members_ready": 1},
    "itinerary": {"itinerary_id": "iti_probe", "status": "ok"}
  },
  "threads": {
    "main": {
      "msg_probe": {
        "author_id": "bounce",
        "message_id": "msg_probe",
        "role": "assistant",
        "text": "BNC-024 smoke probe"
      }
    }
  }
}
```

Cloud Run deployment:

```text
Service [bounce-api] revision [bounce-api-00007-fdq] has been deployed and is serving 100 percent of traffic.
Service URL: https://bounce-api-167980864337.asia-southeast1.run.app
```

Cloud Run health:

```text
{"status":"ok","app":"Bounce","version":"v0"}
```

Live backend `/chat` to RTDB verification:

```text
POST /chat trip_id=trip_bnc024_live_probe
planning_response_path=/trips/trip_bnc024_live_probe/threads/main/msg_e136b5791ca2446e8e434f7d76ce62bc
```

RTDB readback confirmed:

```json
{
  "author_id": "bounce",
  "message_id": "msg_e136b5791ca2446e8e434f7d76ce62bc",
  "role": "assistant",
  "text": "I can help plan that trip. I’ll start with the group basics, then shape the first itinerary path."
}
```

The live probe data was deleted after verification.

## Boundary

`/trigger-disruption` live end-to-end verification still depends on MongoDB-backed itinerary data and remains gated by `BNC-017`. The Firebase integration itself is implemented, tested with fakes, and verified against live RTDB via the real publisher plus live `/chat` route.

## Status

Complete for Firebase real-time sync integration. `BNC-017` remains blocked on MongoDB Atlas credentials/setup.
