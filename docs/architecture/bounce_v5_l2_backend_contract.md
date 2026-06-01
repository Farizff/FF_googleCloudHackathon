# Bounce v5 L2 backend contract reconciliation

Date: 2026-06-01
Card: BV5-017 — Reconcile L2 backend contract to v5

## Boundary

This checkpoint reconciles the repository's backend contract with PRD v5 without replacing the live `bounce-api` deployment and without claiming live MongoDB/Firebase/Agent Builder connectivity.

In scope:

- Add a v5-shaped `/health` response when L2 mode is explicitly enabled.
- Record the v5 `/api/chat` SSE contract and explicitly defer implementation until Agent Builder streaming is approved/configured.
- Record the MongoDB collection names and Firebase RTDB paths from PRD v5.
- Preserve the existing deployed `bounce-api` behavior unless a future deployment card explicitly changes it.

Out of scope for this checkpoint:

- Replacing the existing deployed `bounce-api` service.
- Implementing live Agent Builder SSE streaming.
- Migrating/renaming existing live MongoDB data.
- Wiring new Firebase production paths.
- Building CUT items from the v5 contract.

## Runtime mode

The existing backend remains `v0` by default.

Set this environment variable to make `/health` report the v5 L2 shape:

```bash
BOUNCE_API_MODE=v5
```

When enabled, `/health` returns:

```json
{
  "status": "ok",
  "app": "Bounce",
  "version": "v5",
  "mongo": "configured | not_configured",
  "firebase": "configured | not_configured",
  "mode": "l2"
}
```

`mongo` is `configured` only when `MONGODB_CONNECTION_STRING` is present. `firebase` is `configured` only when `FIREBASE_DATABASE_URL` is present. This avoids falsely claiming live provider connectivity during a local contract checkpoint.

## `/api/chat` SSE contract

PRD v5 target for POST `/api/chat`:

```python
@app.post("/api/chat")
async def chat_endpoint(payload: ChatPayload):
    async def event_stream():
        async for chunk in agent_builder_stream(payload):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
```

Status: **explicitly deferred**.

Reason: the current repo has a deterministic local `/chat` JSON endpoint with Firebase publish behavior. PRD v5 requires Google Cloud Agent Builder SSE streaming for `/api/chat`, but this checkpoint does not have an approved/configured Agent Builder stream provider. A future L2 implementation should add the `/api/chat` SSE route behind an injected `agent_builder_stream(payload)` seam, with tests for:

- `Content-Type: text/event-stream`
- `Cache-Control: no-cache`
- `X-Accel-Buffering: no`
- token events in `data: ...\n\n` format
- terminal `data: [DONE]\n\n`
- provider-not-configured failure shape without silent fallback

## MongoDB collections

PRD v5 collection names to use where L2 work is in scope:

- `group_trips` — trip metadata, member list, phase, budget
- `itineraries` — day-by-day activity arrays, flock assignments
- `expenses` — log entries with split mode + member refs
- `suggestions` — pending member suggestions with status
- `traveller_profiles` — per-member profile data, partially private
- `flights` — flight options per trip, per origin group

## Firebase Realtime Database paths

PRD v5 paths to use where L2 work is in scope:

- `trips/{tripId}/members/{memberId}/location` — real-time location during FlockMode
- `trips/{tripId}/alerts` — push alerts broadcast to all members
- `trips/{tripId}/flock_status` — Flock check-in status

## Deployment note

The existing live `bounce-api` service remains untouched by this checkpoint. It should continue returning the default v0 health shape until Fariz explicitly approves a deployment that enables `BOUNCE_API_MODE=v5` or replaces the service.
