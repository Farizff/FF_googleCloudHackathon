# Bounce Fixed Kanban Contract

Source of truth: `docs/prd/bounce_prd_v2.md` v2.1, audited against the repository on 2026-05-24.

This Kanban is intentionally **fixed**. It is a task contract, not a receipt log.

## Scope-control rules

1. Do not add new cards silently.
2. If implementation reveals a missing task, pause and ask Fariz before expanding this list.
3. Mark progress by changing status only: `TODO`, `IN_PROGRESS`, `BLOCKED`, `DONE`, or `CUT`.
4. Prefer completing existing cards over splitting them further, unless Fariz approves a scope change.
5. Checkpoint progress between cards with tests plus commit/push when changes are coherent.
6. PRD out-of-scope features stay cut unless every kept feature is done and Fariz approves reopening scope.

## Audit baseline

Repository evidence at audit time:

- `python -m pytest` passes: 84 tests passed.
- Implemented backend/tool files include:
  - `api/main.py`
  - `api/routes/disruptions.py`
  - `api/routes/expenses.py`
  - `api/routes/judge.py`
  - `agent/tools/get_traveller_profile.py`
  - `agent/tools/search_venues.py`
  - `agent/tools/save_itinerary.py`
  - `agent/tools/get_transit_time.py`
  - `agent/tools/optimise_route.py`
  - `agent/tools/get_weather.py`
  - `agent/tools/score_flight_risk.py`
  - `agent/tools/get_multi_modal_transport.py`
  - `agent/tools/apply_disruption.py`
  - `agent/tools/notify_contacts.py`
  - `agent/tools/get_visa_requirements.py`
  - `agent/tools/poll_flight_status.py`
- Seed/schema files exist under `db/schemas/` and `db/seed/`.
- Frontend is only a placeholder at audit time: `frontend/.gitkeep`.
- Workers are only a placeholder at audit time: `workers/.gitkeep`.

---

## Fixed Kanban

### DONE

- **BNC-001 — Repository foundation**
  - PRD/design docs, README, license, requirements, Dockerfile, `.env.example`, and backend test skeleton exist.
  - Acceptance: repo has source docs and deterministic local test loop.

- **BNC-002 — MongoDB schema files**
  - JSON schemas exist for the PRD collections.
  - Acceptance: schema tests pass.

- **BNC-003 — Seed datasets**
  - Seed files exist for airline ratings, visa requirements, venue enrichment, demo trip, Tokyo venues, and flight performance.
  - Acceptance: seed validation tests pass.

- **BNC-004 — FastAPI health endpoint**
  - Minimal backend app exists with `/health`.
  - Acceptance: health test passes.

- **BNC-005 — Core profile and venue tools**
  - Covers PRD tools: `get_traveller_profile`, `search_venues`.
  - Acceptance: agent tests pass.

- **BNC-006 — Itinerary persistence tool**
  - Covers PRD tool: `save_itinerary`.
  - Acceptance: agent tests pass.

- **BNC-007 — Transit, weather, and route optimisation tools**
  - Covers PRD tools/algorithms: `get_transit_time`, `get_weather`, `optimise_route`, energy logic.
  - Acceptance: agent tests pass.

- **BNC-008 — Flight risk scoring tool**
  - Covers PRD formula: `score_flight_risk`.
  - Acceptance: agent tests pass.

- **BNC-009 — Multi-modal transport tool**
  - Covers PRD tool: `get_multi_modal_transport` / Rome2Rio-shaped transport options.
  - Acceptance: agent tests pass.

- **BNC-010 — Disruption mitigation backend**
  - Covers PRD `apply_disruption` tool and `/trigger-disruption` route.
  - Acceptance: agent and API disruption tests pass.

- **BNC-011 — Notification tool**
  - Covers PRD tool: `notify_contacts`.
  - Acceptance: agent tests pass.

- **BNC-012 — Visa requirement lookup tool**
  - Covers PRD tool: `get_visa_requirements`.
  - Acceptance: agent tests pass.

- **BNC-013 — Flight status polling tool**
  - Covers PRD tool: `poll_flight_status`.
  - Acceptance: agent tests pass.

- **BNC-014 — Split bill backend**
  - Covers PRD split-bill settlement algorithm and logging modes at backend level.
  - Acceptance: expense API tests pass.

- **BNC-015 — Judge test mode backend**
  - Covers PRD judge endpoints: reset, seed demo trip, trigger disruption, instructions.
  - Acceptance: judge API tests pass.

- **BNC-019 — Agent system prompt and Agent Builder config**
  - Covers PRD Part 5 system prompt and fixed Part 8 tool registration.
  - Acceptance: `agent/system_prompt.txt` and `agent/agent_config.yaml` exist, register the fixed 14-tool PRD set, and config contract tests pass.

- **BNC-020 — Search accommodation tool**
  - Covers PRD Tool 3: Google Places-shaped hotel search with deterministic price estimates/disclaimer.
  - Acceptance: `agent/tools/search_accommodation.py` exists, returns labelled accommodation options, filters unsafe booking URLs, and agent tests pass.

- **BNC-021 — Search flights tool**
  - Covers PRD Tool 7: Amadeus-shaped flight search with budget/recommended/premium option labelling.
  - Acceptance: `agent/tools/search_flights.py` exists, normalizes Amadeus and flat offer shapes, applies budget/duration/preferred-airline filters, supports optional risk scorer output, and agent tests pass.

### TODO

- **BNC-016 — Cloud/GCP project readiness**
  - PRD source: Part 0.2, Part 16.
  - Deliverable: confirm required APIs, billing, Secret Manager, and Cloud Run settings for the real project.
  - Acceptance: deployed API health endpoint returns OK from Cloud Run and min instance is configured.

- **BNC-017 — MongoDB Atlas and MCP live setup**
  - PRD source: Part 0.3.
  - Deliverable: confirm live Atlas cluster, database, 10 collections, app user, connection string secret, and MCP enablement.
  - Acceptance: deployed backend can read/write expected collections without local mocks.

- **BNC-018 — Firebase Realtime Database live setup**
  - PRD source: Part 0.4, Part 7.4.
  - Deliverable: configure Firebase project/database and initial rules for hackathon demo.
  - Acceptance: backend can broadcast itinerary/state updates to Firebase paths from the PRD.

- **BNC-022 — Chat and planning API**
  - PRD source: Part 5, Part 8, Part 11.3, Part 13.
  - Deliverable: `api/routes/chat.py` for Bounce conversation entry, PII guard, rate limit, streamed loading states, and tool orchestration boundary.
  - Acceptance: natural-language trip entry produces or updates a planning response path with tested error/loading behavior.

- **BNC-023 — Trip/itinerary/flight/group API routes**
  - PRD source: Part 4 repo structure and Part 7 schemas.
  - Deliverable: `api/routes/trip.py`, `itinerary.py`, `flights.py`, `flight_status.py`, and `group.py`.
  - Acceptance: CRUD and group-governance flows are test-covered against PRD schemas.

- **BNC-024 — Firebase real-time sync integration**
  - PRD source: Days 9–11 build sequence, Part 7.4.
  - Deliverable: real Firebase broadcaster implementation replacing no-op/local test doubles.
  - Acceptance: itinerary and group state changes appear in Firebase for all members.

- **BNC-025 — Invite, co-leader, suggestions, and FlockMode backend**
  - PRD source: Days 9–11 build sequence, Part 1.5, Part 5 group governance.
  - Deliverable: invite token system, role management, member suggestions, Flock CRUD, Flock chat thread paths.
  - Acceptance: organiser/co-leader/Flock leader permissions match PRD rules in tests.

- **BNC-026 — Reminder workers and scheduler endpoints**
  - PRD source: Part 10 and Days 12–13 build sequence.
  - Deliverable: `workers/flight_poller.py`, `workers/reminder_dispatcher.py`, and internal scheduler endpoints if needed.
  - Acceptance: due reminders are sent once and flight status changes publish notifications.

- **BNC-027 — Frontend foundation and app shell**
  - PRD source: Part 4 repo structure, design doc cross-reference.
  - Deliverable: `frontend/index.html`, `manifest.json`, `sw.js`, `app.js`, and `style.css`.
  - Acceptance: app shell loads locally and can call backend health/demo endpoints.

- **BNC-028 — Core planning UI**
  - PRD source: Days 3–8 build sequence and Part 15 core loop/flights/maps.
  - Deliverable: chat entry, profile gap-fill, itinerary day view, budget tracker, Maps JS pins/routes, flight selection layout.
  - Acceptance: core loop, flights, and maps checklist items in Part 15 pass manually or through tests where practical.

- **BNC-029 — Group, FlockMode, active trip, and split bill UI**
  - PRD source: Days 9–13 build sequence and Part 15 group/FlockMode/split bill.
  - Deliverable: group dashboard, suggestion review, Flock creation/map view/reconvene display, active trip view, split bill UI.
  - Acceptance: group, FlockMode, disruption trigger, and split bill checklist items pass.

- **BNC-030 — Production deployment and smoke tests**
  - PRD source: Part 16.
  - Deliverable: container build, Cloud Run deploy, env/secrets wired, frontend deploy.
  - Acceptance: hosted app URL and API URL work, `/health` passes, judge endpoints live.

- **BNC-031 — Demo/submission package**
  - PRD source: Part 14 and Part 17.
  - Deliverable: 3-minute demo video, Devpost form, screenshots, public repo verification, judge instructions.
  - Acceptance: all Devpost checklist items are complete before the submission buffer ends.

### CUT — do not build without approval

These are explicitly out of scope in PRD Part 1.6:

- Travel DNA read-back on later trips.
- Receipt scanning via Cloud Vision API.
- AI-generated packing list.
- AI-generated trip narrative.
- Multi-language UI.
- Cultural briefing screen per nationality.
- In-app GPS / real-time location tracking.

---

## Current next card recommendation

Recommended next card: **BNC-016 — Cloud/GCP project readiness**.

Reason: the fixed local agent tool set is now complete. The remaining skipped foundation work starts with live GCP readiness before larger chat/API/frontend integration.
