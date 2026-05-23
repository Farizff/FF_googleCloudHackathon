# Bounce Implementation Task Breakdown Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build Bounce, an AI-powered group travel planning hackathon app, from the supplied Technical PRD v1.0, with a working demo path for the Tokyo reunion scenario and a deployable Cloud Run app.

**Architecture:** Implement a FastAPI backend with modular agent tools, MongoDB-backed seed/demo data, a lightweight PWA frontend, and Cloud Run deployment. Start with deterministic local/demo functionality, then add live integrations and cloud services only after the core loop works end-to-end.

**Tech Stack:** Python 3.11+, FastAPI, MongoDB Atlas, vanilla HTML/CSS/JS PWA, Google Cloud Run, Vertex/Gemini-compatible agent behavior, Firebase Realtime DB, Google Maps, Amadeus, SendGrid, Cloud Vision, Pub/Sub/Scheduler.

---

## Current context

- Repo: `https://github.com/Farizff/FF_googleCloudHackathon`
- Local workspace: `C:/Users/fariz/projects/FF_googleCloudHackathon`
- Current branch: `main`
- Existing files: `README.md`, `.gitignore`
- Google Cloud project currently configured on this machine: `project-411e0419-48bd-4b5b-97f`
- Current configured Cloud Run region from previous setup: `asia-southeast2`
- PRD required region: `asia-southeast1` / Jakarta

## Important PRD amendments to include before implementation

Add these requirements to the project docs before coding:

1. **Demo friend group must include varying nationalities**, not all US citizens, so the visa/compliance reminder feature is testable.
   - Keep origins as SFO/LAX/JFK/SEA/ORD for the demo routes.
   - Add nationality/passport diversity to seeded traveller profiles, e.g. US, India, Indonesia, Japan, Canada, UK, Singapore, Australia.
   - Do not broadcast private visa/compliance status to the group.

2. **Every screen/step where chat is available must support ongoing back-and-forth**, not just one-shot prompts.
   - Chat state must persist per trip/session.
   - Users must be able to refine, correct, and ask follow-up questions from planning, itinerary, FlockMode, disruption, and expense screens.

3. **Frontend typography must use Geometri**, inspired by Google/Airbnb visual language.
   - Add font handling in `frontend/style.css`.
   - If the exact font file cannot be bundled, use a documented fallback stack and keep the design Geometri-like.

---

## Phase 0 — Project foundation and PRD alignment

### Task 0.1: Save source PRD inside the repo

**Objective:** Preserve the provided PRD as project source-of-truth documentation.

**Files:**
- Create: `docs/prd/bounce_prd_v1.md`

**Steps:**
1. Copy the supplied `bounce_prd_v1.md` into `docs/prd/bounce_prd_v1.md`.
2. Do not edit the original text except for formatting preservation if needed.
3. Verify with `git diff -- docs/prd/bounce_prd_v1.md`.
4. Commit: `docs: add Bounce technical PRD v1`.

**Verification:** PRD exists in repo and can be read from GitHub.

### Task 0.2: Add PRD amendment document

**Objective:** Record the three user-supplied additions without losing PRD traceability.

**Files:**
- Create: `docs/prd/bounce_prd_amendments.md`
- Modify: `README.md`

**Steps:**
1. Create amendment doc with sections:
   - Demo nationality diversity
   - Persistent back-and-forth chat everywhere
   - Geometri typography requirement
2. Link it from `README.md` under a “Product docs” section.
3. Commit: `docs: add PRD amendments`.

**Verification:** README links to both PRD and amendments.

### Task 0.3: Resolve region/project naming decision

**Objective:** Avoid deploying to the wrong GCP region or project.

**Files:**
- Modify: `README.md`
- Create: `.env.example`

**Steps:**
1. Decide whether to follow PRD (`asia-southeast1`) or current gcloud config (`asia-southeast2`).
2. For hackathon compliance, prefer PRD region `asia-southeast1` unless user explicitly says otherwise.
3. Put `GCP_PROJECT_ID=project-411e0419-48bd-4b5b-97f` in `.env.example` as placeholder-style example, not secret.
4. Put `GCP_REGION=asia-southeast1` in `.env.example` if using PRD region.
5. Commit: `chore: document deployment environment defaults`.

**Verification:** `README.md` clearly says which region the app deploys to.

### Task 0.4: Add MIT license

**Objective:** Match PRD requirement: public GitHub repo with MIT license.

**Files:**
- Create: `LICENSE`

**Steps:**
1. Add standard MIT License with copyright holder `Farizff` or user-approved name.
2. Commit: `docs: add MIT license`.

**Verification:** GitHub displays MIT license.

---

## Phase 1 — Repository skeleton and backend baseline

### Task 1.1: Create exact PRD directory structure

**Objective:** Establish the repo layout before feature work.

**Files:**
- Create directories:
  - `agent/tools/`
  - `api/routes/`
  - `db/schemas/`
  - `db/seed/`
  - `frontend/`
  - `tests/agent/`
  - `tests/api/`
  - `tests/db/`

**Steps:**
1. Add `.gitkeep` files only where needed for empty directories.
2. Commit: `chore: create project structure`.

**Verification:** `find`/file listing shows PRD structure exists.

### Task 1.2: Add Python dependencies

**Objective:** Define the backend runtime dependencies.

**Files:**
- Create: `requirements.txt`

**Initial dependencies:**
```txt
fastapi
uvicorn[standard]
pydantic
pydantic-settings
python-dotenv
pymongo
httpx
pytest
pytest-asyncio
```

**Later dependencies:**
Add integration libraries only when implementing those integrations:
- `googlemaps`
- `amadeus`
- `sendgrid`
- `google-cloud-translate`
- `google-cloud-vision`
- `firebase-admin`

**Steps:**
1. Add minimal requirements.
2. Verify install in a virtual environment.
3. Commit: `chore: add backend requirements`.

**Verification:** `python -m pip install -r requirements.txt` succeeds.

### Task 1.3: Add FastAPI app shell

**Objective:** Provide a runnable backend with health endpoint.

**Files:**
- Create: `api/main.py`
- Create: `api/__init__.py`
- Create: `api/routes/__init__.py`
- Create: `tests/api/test_health.py`

**Endpoints:**
- `GET /health` → `{"status":"ok","app":"Bounce"}`

**Steps:**
1. Write test for `/health`.
2. Implement FastAPI app.
3. Run test.
4. Commit: `feat: add FastAPI health endpoint`.

**Verification:** `pytest tests/api/test_health.py -v` passes.

### Task 1.4: Add Dockerfile and local run docs

**Objective:** Make backend container-ready for Cloud Run.

**Files:**
- Create: `Dockerfile`
- Modify: `README.md`

**Requirements:**
- Listen on `0.0.0.0:$PORT`.
- Start command: `uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8080}`.

**Steps:**
1. Add Dockerfile.
2. Add local run instructions.
3. Build locally if Docker is available.
4. Commit: `chore: add Cloud Run Dockerfile`.

**Verification:** Container starts and `/health` responds.

---

## Phase 2 — Schemas and seed data first

### Task 2.1: Add MongoDB schema JSON files

**Objective:** Capture all PRD collection schemas as versioned artifacts.

**Files:**
- Create: `db/schemas/traveller_profiles.schema.json`
- Create: `db/schemas/group_trips.schema.json`
- Create: `db/schemas/itineraries.schema.json`
- Create: `db/schemas/venues.schema.json`
- Create: `db/schemas/flight_performance.schema.json`
- Create: `db/schemas/expenses.schema.json`
- Create: `db/schemas/suggestions.schema.json`
- Create: `db/schemas/notification_log.schema.json`

**Steps:**
1. Convert PRD schema descriptions into JSON Schema-like files.
2. Keep validation pragmatic; do not over-engineer.
3. Commit: `docs: add MongoDB collection schemas`.

**Verification:** All expected schema files exist.

### Task 2.2: Seed Tokyo venues, minimum 25

**Objective:** Make venue search and itinerary generation deterministic.

**Files:**
- Create: `db/seed/seed_venues_tokyo.json`
- Create: `tests/db/test_seed_venues.py`

**Requirements:**
- At least 25 venues.
- Include all PRD named venues.
- Include geographic clusters.
- Include dietary tags, opening hours, coordinates, intensity, and price.

**Steps:**
1. Write test asserting at least 25 venues and required fields.
2. Add venue seed JSON.
3. Run test.
4. Commit: `data: add Tokyo venue seed data`.

**Verification:** `pytest tests/db/test_seed_venues.py -v` passes.

### Task 2.3: Seed demo travellers with varied nationalities

**Objective:** Implement the user amendment for visa/compliance testing.

**Files:**
- Create: `db/seed/seed_demo_trip.json`
- Create: `tests/db/test_demo_trip_seed.py`

**Requirements:**
- Preserve 10 friends and origins from PRD.
- Add varied `nationality` and `passport_country` values.
- Include dietary restrictions from PRD.
- Assign organiser/co-leader/member roles.

**Suggested demo diversity:**
- Hassan: Indonesia passport, SFO, Halal
- Aditya: India passport, SFO
- Reza: United States passport, SFO
- Priya: India passport, LAX, Vegetarian
- Marcus: Canada passport, LAX
- Sofia: Mexico passport, JFK
- Tom: United Kingdom passport, JFK
- Yuki: Japan passport, SEA, Gluten-free
- Dev: Singapore passport, SEA
- James: Australia passport, ORD

**Steps:**
1. Write test requiring at least 5 distinct passport countries.
2. Add demo trip seed.
3. Run test.
4. Commit: `data: add diverse demo trip seed`.

**Verification:** Test proves nationality diversity.

### Task 2.4: Seed flight performance data

**Objective:** Support demo routes and judge fallback behavior.

**Files:**
- Create: `db/seed/seed_flight_performance.json`
- Create: `tests/db/test_flight_seed.py`

**Requirements:**
- Include all specified demo flights: UA837, NH10, JL62, DL166, NH106, JL5, NH9, UA79, NH176, DL637, NH12, UA881.
- Target 200+ route records if time permits.
- At minimum, implement required demo records plus judge-route fallback logic later.

**Steps:**
1. Write test for required route IDs.
2. Add seed data.
3. Run test.
4. Commit: `data: add flight performance seed data`.

**Verification:** Required demo flights are present.

---

## Phase 3 — Database layer and core agent tools

### Task 3.1: Add settings module

**Objective:** Centralize environment configuration.

**Files:**
- Create: `api/settings.py`
- Create: `tests/api/test_settings.py`

**Settings:**
- `GCP_PROJECT_ID`
- `GCP_REGION`
- `MONGODB_CONNECTION_STRING`
- `MONGODB_DATABASE`
- all API key placeholders from PRD

**Steps:**
1. Write tests for default/dev settings behavior.
2. Implement Pydantic settings.
3. Commit: `chore: add application settings`.

**Verification:** Tests pass without real secrets.

### Task 3.2: Add MongoDB client helper with test-safe fallback

**Objective:** Allow tools to read/write MongoDB, while tests can run without Atlas.

**Files:**
- Create: `db/client.py`
- Create: `tests/db/test_client.py`

**Approach:**
- Use `pymongo.MongoClient` when `MONGODB_CONNECTION_STRING` exists.
- Provide clean error messages when missing.
- For unit tests, use lightweight fake repository objects rather than requiring live MongoDB.

**Steps:**
1. Write tests for missing config behavior.
2. Implement client helper.
3. Commit: `feat: add MongoDB client helper`.

**Verification:** Tests pass without Atlas credentials.

### Task 3.3: Implement `get_traveller_profile`

**Objective:** First MongoDB read tool.

**Files:**
- Create: `agent/tools/get_traveller_profile.py`
- Create: `tests/agent/test_get_traveller_profile.py`

**Tool contract:** PRD Part 8.

**Steps:**
1. Write tests for found and `USER_NOT_FOUND` cases.
2. Implement tool function with dependency-injected collection.
3. Commit: `feat: add traveller profile tool`.

**Verification:** Tool returns `{"profile": ...}` or standard error.

### Task 3.4: Implement `save_itinerary`

**Objective:** First MongoDB write tool.

**Files:**
- Create: `agent/tools/save_itinerary.py`
- Create: `tests/agent/test_save_itinerary.py`

**Initial scope:**
- Save itinerary to MongoDB.
- Stub Firebase side effect with a clear TODO/fallback until Firebase phase.

**Steps:**
1. Write tests for insert/update behavior.
2. Implement write function.
3. Commit: `feat: add save itinerary tool`.

**Verification:** Returns `itinerary_id`, `success`, `updated_at`.

### Task 3.5: Implement `search_venues`

**Objective:** Query venues with PRD filters.

**Files:**
- Create: `agent/tools/search_venues.py`
- Create: `tests/agent/test_search_venues.py`

**Required filters:**
- Seasonal closure
- Group capacity
- Dietary compatibility
- Day-of-week opening hours
- Hidden gem ratio
- Mobility/accessibility

**Steps:**
1. Write tests for each filter.
2. Implement pure filtering helpers first.
3. Add collection query wrapper.
4. Commit: `feat: add venue search tool`.

**Verification:** Tests cover dietary and opening-hour constraints.

---

## Phase 4 — Route optimization and scheduling

### Task 4.1: Add geospatial/time utilities

**Objective:** Support route optimization without external APIs first.

**Files:**
- Create: `agent/tools/utils_geo.py`
- Create: `agent/tools/utils_time.py`
- Create: `tests/agent/test_utils_geo.py`
- Create: `tests/agent/test_utils_time.py`

**Functions:**
- Haversine distance
- Day-of-week conversion
- HH:MM parsing/formatting
- Time overlap detection

**Steps:**
1. Write unit tests.
2. Implement helpers.
3. Commit: `feat: add route utility helpers`.

**Verification:** Utility tests pass.

### Task 4.2: Implement `get_transit_time` with fallback

**Objective:** Support Maps API but keep demo functional without key/quota.

**Files:**
- Create: `agent/tools/get_transit_time.py`
- Create: `tests/agent/test_get_transit_time.py`

**Behavior:**
- If `GOOGLE_MAPS_API_KEY` exists, call Google Maps.
- If missing/quota error, return estimate using distance-based fallback.
- Add group-size transport note for groups larger than 6.

**Steps:**
1. Test fallback path.
2. Test group-size note.
3. Implement Maps path behind config.
4. Commit: `feat: add transit time tool`.

**Verification:** Works without a Maps API key.

### Task 4.3: Implement `optimise_route`

**Objective:** Build the scheduling algorithm from PRD.

**Files:**
- Create: `agent/tools/optimise_route.py`
- Create: `tests/agent/test_optimise_route.py`

**Required algorithm order:**
1. Geographic clustering
2. Order clusters by earliest opening
3. Sequence within clusters
4. Flatten
5. Energy logic overlay
6. Assign times
7. Peak avoidance notes
8. Dining placement, if practical in this phase

**Steps:**
1. Write tests for relaxed/moderate/packed max stops.
2. Write tests for high-intensity AM and low-intensity PM ordering.
3. Write tests that every item has reasoning.
4. Implement minimal algorithm.
5. Commit: `feat: add route optimisation tool`.

**Verification:** Schedule contains required fields and one-line reasoning.

---

## Phase 5 — Bounce conversation API and persistent chat

### Task 5.1: Add Bounce system prompt

**Objective:** Store the persona and behavioral rules from PRD.

**Files:**
- Create: `agent/system_prompt.txt`
- Create: `tests/agent/test_system_prompt.py`

**Steps:**
1. Copy PRD system prompt.
2. Add amendment: chat must support follow-up/back-and-forth wherever chat appears.
3. Test that required phrases/rules exist.
4. Commit: `feat: add Bounce system prompt`.

**Verification:** Test confirms persona and “exactly 3 options” rule.

### Task 5.2: Add chat models and in-memory/session persistence

**Objective:** Make chat multi-turn from the start.

**Files:**
- Create: `api/routes/chat.py`
- Create: `api/models.py`
- Create: `tests/api/test_chat.py`

**Endpoint:**
- `POST /chat`

**Request fields:**
- `trip_id`
- `user_id`
- `message`
- `screen_context` (`planning`, `itinerary`, `flock_mode`, `disruption`, `expenses`, etc.)

**Response fields:**
- `bounce_response`
- `conversation_id`
- optional structured actions

**Steps:**
1. Write test: first message introduces Bounce.
2. Write test: follow-up message preserves `conversation_id`.
3. Implement deterministic local response engine first.
4. Commit: `feat: add persistent chat endpoint`.

**Verification:** Chat can go back and forth without resetting context.

### Task 5.3: Add PII guard to chat

**Objective:** Implement PRD security layer early.

**Files:**
- Create: `api/security.py`
- Modify: `api/routes/chat.py`
- Create: `tests/api/test_security.py`

**Steps:**
1. Test passport/card/national ID detection.
2. Implement regex guard.
3. Wire into `/chat` before agent processing.
4. Commit: `feat: add chat PII guard`.

**Verification:** Sensitive-looking data receives Bounce safety response and is not stored.

### Task 5.4: Add role-aware suggestion handling

**Objective:** Support organiser/co-leader vs member governance.

**Files:**
- Create: `api/governance.py`
- Modify: `api/routes/chat.py`
- Create: `tests/api/test_governance.py`

**Steps:**
1. Test organiser can apply change.
2. Test member message is logged as suggestion.
3. Implement `require_admin` and `can_apply_changes`.
4. Commit: `feat: add group governance helpers`.

**Verification:** Member suggestions are not applied directly.

---

## Phase 6 — Basic frontend PWA and visual identity

### Task 6.1: Add frontend shell with Geometri-inspired typography

**Objective:** Create the initial Bounce UI with required font direction.

**Files:**
- Create: `frontend/index.html`
- Create: `frontend/style.css`
- Create: `frontend/app.js`

**Design requirements:**
- Clean Google/Airbnb-inspired look.
- Font: Geometri if available/bundled; fallback stack documented.
- Bounce avatar/personality visible.

**Steps:**
1. Add frontend files.
2. Add CSS variable `--font-primary` with Geometri/fallback stack.
3. Add chat panel and itinerary placeholder.
4. Commit: `feat: add Bounce frontend shell`.

**Verification:** Opening `frontend/index.html` shows the app shell.

### Task 6.2: Wire frontend chat to backend

**Objective:** Enable back-and-forth chat in the browser.

**Files:**
- Modify: `frontend/app.js`
- Modify: `frontend/index.html`
- Create: `tests/api/test_cors_or_static.py` if backend serves frontend

**Steps:**
1. Add chat input/send flow.
2. Preserve `conversation_id` in frontend state.
3. Include `screen_context` in each chat call.
4. Commit: `feat: connect frontend chat to API`.

**Verification:** User can send multiple messages and see Bounce replies.

### Task 6.3: Add PWA manifest and service worker

**Objective:** Meet offline itinerary cache requirement baseline.

**Files:**
- Create: `frontend/manifest.json`
- Create: `frontend/sw.js`
- Modify: `frontend/index.html`

**Steps:**
1. Add manifest with app name Bounce.
2. Cache shell assets.
3. Commit: `feat: add PWA offline shell`.

**Verification:** Browser dev tools show service worker registered.

---

## Phase 7 — Itinerary generation and display

### Task 7.1: Add itinerary route

**Objective:** CRUD endpoint for itinerary documents.

**Files:**
- Create: `api/routes/itinerary.py`
- Modify: `api/main.py`
- Create: `tests/api/test_itinerary.py`

**Endpoints:**
- `GET /itinerary/{itinerary_id}`
- `POST /itinerary`

**Steps:**
1. Write tests with fake store.
2. Implement route.
3. Commit: `feat: add itinerary API`.

**Verification:** Itinerary can be saved and loaded.

### Task 7.2: Generate demo itinerary from seed data

**Objective:** End-to-end deterministic itinerary for the demo.

**Files:**
- Create: `agent/demo_itinerary.py`
- Create: `tests/agent/test_demo_itinerary.py`

**Requirements:**
- Day 1 schedule with reasoning.
- Day 5 FlockMode structure.
- Flight-aware arrival buffers.
- Respect dietary/opening hours.

**Steps:**
1. Test generated itinerary has 10 members and Day 5 flocks.
2. Implement deterministic generator using seed JSON.
3. Commit: `feat: generate demo itinerary`.

**Verification:** Demo itinerary loads without external APIs.

### Task 7.3: Display itinerary in frontend

**Objective:** Show day schedule and reasoning notes.

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/app.js`
- Modify: `frontend/style.css`

**Steps:**
1. Add day cards.
2. Add reasoning notes per schedule item.
3. Add budget summary placeholder.
4. Commit: `feat: display itinerary day view`.

**Verification:** Demo itinerary appears in UI.

---

## Phase 8 — Flights and risk scoring

### Task 8.1: Implement risk scoring pure function

**Objective:** Make flight risk scoring deterministic and testable.

**Files:**
- Create: `agent/tools/score_flight_risk.py`
- Create: `tests/agent/test_score_flight_risk.py`

**Steps:**
1. Test formula with seeded performance data.
2. Test default fallback values.
3. Implement exact PRD weighting.
4. Commit: `feat: add flight risk scoring`.

**Verification:** Scores and tiers match expected values.

### Task 8.2: Implement Amadeus/mock `search_flights`

**Objective:** Return exactly 3 flight options even if sandbox is unreliable.

**Files:**
- Create: `agent/tools/search_flights.py`
- Create: `tests/agent/test_search_flights.py`

**Behavior:**
- If Amadeus credentials exist, call sandbox.
- Else use deterministic mock options from demo route data.
- Always label budget/recommended/premium.

**Steps:**
1. Test mock SFO→NRT returns 3 options.
2. Test fewer-than-3 fallback explanation.
3. Implement Amadeus path.
4. Commit: `feat: add flight search tool`.

**Verification:** SFO→NRT demo works without Amadeus credentials.

### Task 8.3: Add flights API route and frontend card

**Objective:** Surface flight options and risk scores.

**Files:**
- Create: `api/routes/flights.py`
- Modify: `api/main.py`
- Modify: `frontend/app.js`
- Modify: `frontend/style.css`
- Create: `tests/api/test_flights.py`

**Steps:**
1. Add API test for exactly 3 options.
2. Implement route.
3. Add UI cards with risk tier colors.
4. Commit: `feat: add flight options UI`.

**Verification:** UI shows 3 flight cards with risk scores.

---

## Phase 9 — Maps integration

### Task 9.1: Add map container and marker rendering

**Objective:** Show venue pins on the itinerary map.

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/app.js`
- Modify: `frontend/style.css`

**Steps:**
1. Add `#bounce-map` container.
2. If Maps key available, load Google Maps JS.
3. If no key, show graceful static placeholder/list.
4. Commit: `feat: add itinerary map container`.

**Verification:** UI does not break without Maps key.

### Task 9.2: Add Open in Google Maps links

**Objective:** Provide live navigation handoff.

**Files:**
- Modify: `frontend/app.js`

**Steps:**
1. Add URL builder for destination coordinates.
2. Add buttons per venue.
3. Commit: `feat: add open in maps links`.

**Verification:** Links open Google Maps with destination.

---

## Phase 10 — Disruption demo loop

### Task 10.1: Implement `apply_disruption`

**Objective:** Return 3 alternatives and revised schedule for disruption scenario.

**Files:**
- Create: `agent/tools/apply_disruption.py`
- Create: `tests/agent/test_apply_disruption.py`

**Steps:**
1. Test venue closure/flight cancellation alternative ranking.
2. Test exactly 3 alternatives when available.
3. Test schedule excludes already-used venues.
4. Implement pipeline using seeded data and transit fallback.
5. Commit: `feat: add disruption handling tool`.

**Verification:** Demo payload returns alternatives.

### Task 10.2: Add disruption API route

**Objective:** Support the demo trigger button.

**Files:**
- Create: `api/routes/disruption.py`
- Modify: `api/main.py`
- Create: `tests/api/test_disruption.py`

**Endpoint:**
- `POST /trigger-disruption`

**Steps:**
1. Write API test using PRD payload.
2. Implement route.
3. Commit: `feat: add disruption trigger API`.

**Verification:** API returns alternatives and changes summary.

### Task 10.3: Add frontend disruption button

**Objective:** Demo the disruption flow visually.

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/app.js`
- Modify: `frontend/style.css`

**Steps:**
1. Add red “Simulate Disruption” button.
2. Prepopulate PRD demo payload.
3. Render alternative cards.
4. Keep chat available on disruption screen with `screen_context="disruption"`.
5. Commit: `feat: add disruption demo UI`.

**Verification:** Button displays three alternatives in UI.

---

## Phase 11 — FlockMode

### Task 11.1: Add FlockMode backend helpers

**Objective:** Split members into flocks for Day 5.

**Files:**
- Create: `agent/flock_mode.py`
- Create: `tests/agent/test_flock_mode.py`

**Requirements:**
- Explorers, Foodies, Shoppers from PRD.
- Reconvene: Shinjuku Station East Exit, 18:30.

**Steps:**
1. Test flock membership counts.
2. Test reconvene fields.
3. Implement helper.
4. Commit: `feat: add FlockMode helpers`.

**Verification:** Day 5 has three flocks.

### Task 11.2: Add FlockMode UI

**Objective:** Show each Flock with schedule and mini-map placeholder.

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/app.js`
- Modify: `frontend/style.css`

**Steps:**
1. Add Flock cards.
2. Add reconvene card.
3. Keep chat available with `screen_context="flock_mode"`.
4. Commit: `feat: add FlockMode UI`.

**Verification:** User can view flocks and still chat.

---

## Phase 12 — Firebase realtime sync

### Task 12.1: Add Firebase config and admin helper

**Objective:** Prepare Firebase Realtime DB writes.

**Files:**
- Create: `api/firebase_client.py`
- Create: `tests/api/test_firebase_client.py`

**Behavior:**
- If Firebase env vars/credentials exist, initialize admin SDK.
- Else no-op with logged warning for local demo.

**Steps:**
1. Test missing config no-op.
2. Implement helper.
3. Commit: `feat: add Firebase client helper`.

**Verification:** Local app runs without Firebase secrets.

### Task 12.2: Wire Firebase update in `save_itinerary`

**Objective:** Trigger realtime updates on itinerary save.

**Files:**
- Modify: `agent/tools/save_itinerary.py`
- Modify: `tests/agent/test_save_itinerary.py`

**Steps:**
1. Add fake Firebase client test.
2. Call `trips/{trip_id}/itinerary_updated_at` write after save.
3. Commit: `feat: broadcast itinerary updates`.

**Verification:** Test proves side-effect call.

---

## Phase 13 — Notifications and reminders

### Task 13.1: Implement `notify_contacts` with SendGrid fallback

**Objective:** Send/log notifications without breaking local demo.

**Files:**
- Create: `agent/tools/notify_contacts.py`
- Create: `tests/agent/test_notify_contacts.py`

**Behavior:**
- If SendGrid key exists, send email.
- Else write pending/mock notification log.
- Translate if translation credentials available; otherwise send English.

**Steps:**
1. Test log entry creation.
2. Test language fallback.
3. Implement SendGrid path.
4. Commit: `feat: add contact notification tool`.

**Verification:** Notification log gets records.

### Task 13.2: Add basic reminder definitions

**Objective:** Represent smart reminders before creating Scheduler jobs.

**Files:**
- Create: `agent/reminders.py`
- Create: `tests/agent/test_reminders.py`

**Steps:**
1. Model reminder types from PRD.
2. Implement reconvene reminder calculation.
3. Commit: `feat: add reminder definitions`.

**Verification:** FlockMode T-30 reminder time is calculated.

---

## Phase 14 — Expenses and split bill

### Task 14.1: Add expense models and API

**Objective:** Support manual expense logging first.

**Files:**
- Create: `api/routes/expenses.py`
- Modify: `api/main.py`
- Create: `tests/api/test_expenses.py`

**Endpoints:**
- `POST /expenses`
- `GET /expenses/{trip_id}`
- `GET /expenses/{trip_id}/settlement`

**Steps:**
1. Test equal split.
2. Test flock-level expense tag.
3. Implement endpoints.
4. Commit: `feat: add expense API`.

**Verification:** Settlement math works for sample expenses.

### Task 14.2: Add expense frontend

**Objective:** Show running balances and settlement card.

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/app.js`
- Modify: `frontend/style.css`

**Steps:**
1. Add expense form.
2. Add settlement summary.
3. Keep chat available with `screen_context="expenses"`.
4. Commit: `feat: add expense UI`.

**Verification:** User can log expense and see balance update.

### Task 14.3: Add receipt scan placeholder / Cloud Vision later

**Objective:** Avoid blocking MVP on camera/Vision.

**Files:**
- Create: `agent/tools/scan_receipt.py`
- Create: `tests/agent/test_scan_receipt.py`

**Steps:**
1. Implement interface with mock extraction first.
2. Add Cloud Vision only if time remains.
3. Commit: `feat: add receipt scan interface`.

**Verification:** Mock scan extracts amount/description from fixture.

---

## Phase 15 — Cloud deployment

### Task 15.1: Add Cloud Build config

**Objective:** Support build/deploy workflow.

**Files:**
- Create: `cloudbuild.yaml`
- Modify: `README.md`

**Steps:**
1. Add build/deploy steps for Cloud Run.
2. Use configured `GCP_REGION`.
3. Commit: `chore: add Cloud Build config`.

**Verification:** Config is valid YAML.

### Task 15.2: Deploy health endpoint to Cloud Run

**Objective:** Confirm cloud deployment before full feature deployment.

**Files:**
- No code changes expected unless deployment issues appear.

**Command:**
```bash
gcloud run deploy bounce-api --source . --region asia-southeast1 --allow-unauthenticated --quiet
```

**Steps:**
1. Deploy minimal app.
2. Hit `/health` on Cloud Run URL.
3. Commit any fixes.

**Verification:** Public Cloud Run URL returns health JSON.

### Task 15.3: Add secrets documentation

**Objective:** Document all required secrets without committing any secrets.

**Files:**
- Modify: `.env.example`
- Create: `docs/deployment/secrets.md`

**Steps:**
1. List every env var from PRD.
2. Add `gcloud secrets create` examples.
3. Commit: `docs: add secrets setup guide`.

**Verification:** No real secrets in git.

---

## Phase 16 — Judge test mode and graceful fallbacks

### Task 16.1: Add destination fallback itinerary generator

**Objective:** Ensure arbitrary destinations do not error.

**Files:**
- Modify: `agent/demo_itinerary.py`
- Create: `tests/agent/test_judge_mode.py`

**Requirements:**
- “Paris” generates a real-looking fallback itinerary.
- Domestic SFO→LA skips visa/customs.
- Office mode changes tone and venue categories.
- Group sizes 2–20 do not error.

**Steps:**
1. Add tests for PRD judge checklist.
2. Implement fallback generator.
3. Commit: `feat: add judge test mode fallbacks`.

**Verification:** Judge scenarios return graceful responses.

### Task 16.2: Add visa/compliance reminder demo logic

**Objective:** Use nationality diversity to demonstrate private reminders.

**Files:**
- Create: `agent/compliance.py`
- Create: `tests/agent/test_compliance.py`

**Scope:**
- Lightweight demo logic, not legal advice.
- Determine whether to show “check visa requirements” reminders per passport country.
- Keep reminders private per member.

**Steps:**
1. Test different passport countries produce individual reminders.
2. Test no group broadcast of private compliance details.
3. Commit: `feat: add private compliance reminders`.

**Verification:** Demo profiles trigger varied reminders.

---

## Phase 17 — Demo polish and video readiness

### Task 17.1: Add demo script mode

**Objective:** Make the 3-minute video flow reproducible.

**Files:**
- Create: `docs/demo/demo_script.md`
- Create: `frontend/demo.js` or add demo mode to `frontend/app.js`

**Steps:**
1. Add exact PRD video script.
2. Add demo data loading button/route.
3. Commit: `docs: add demo script`.

**Verification:** A teammate can follow the script without explanation.

### Task 17.2: Add final README project pitch

**Objective:** Make GitHub repo judge-friendly.

**Files:**
- Modify: `README.md`

**Sections:**
- What Bounce is
- Demo scenario
- Tech stack
- Google Cloud services used
- MongoDB usage
- Local setup
- Deployment
- Demo video placeholder/link

**Steps:**
1. Rewrite README after features stabilize.
2. Commit: `docs: update project README`.

**Verification:** README is clear from GitHub homepage.

### Task 17.3: Final testing checklist pass

**Objective:** Validate against PRD Part 17.

**Files:**
- Create: `docs/testing/judge_checklist_results.md`

**Steps:**
1. Walk through every checklist item.
2. Mark pass/fail/known limitation.
3. Fix critical failures only.
4. Commit: `test: add judge checklist results`.

**Verification:** All core demo items pass or have acceptable fallback.

---

## Risks and mitigation

1. **Too many integrations for hackathon time**
   - Mitigation: implement deterministic local/demo fallbacks first; live APIs later.

2. **Region mismatch**
   - Mitigation: decide early between `asia-southeast1` from PRD and currently configured `asia-southeast2`.

3. **Agent Builder complexity**
   - Mitigation: build local FastAPI tool endpoints and deterministic agent behavior first; register with Agent Builder only after endpoints are stable.

4. **MongoDB Atlas credentials not available**
   - Mitigation: seed JSON + fake repositories for tests; add MongoDB connection later.

5. **Maps/Amadeus/SendGrid quotas or missing keys**
   - Mitigation: every external API tool must have a graceful fallback.

6. **Font licensing/availability for Geometri**
   - Mitigation: use Geometri only if legally available; otherwise document and use similar geometric fallback stack.

---

## Open questions for Fariz before implementation

1. Should deployment follow the PRD region `asia-southeast1` or your current configured region `asia-southeast2`?
2. Do you already have MongoDB Atlas connection details, or should we build with local JSON/fake DB first?
3. Do you want the first MVP to be demo-only deterministic, or should we connect live APIs immediately?
4. Do you have a legal Geometri font file/license, or should we use a close fallback stack?

---

## Recommended first execution batch

Start with these tasks only:

1. Task 0.1 — Save PRD in repo
2. Task 0.2 — Add PRD amendments
3. Task 0.3 — Resolve region/project defaults
4. Task 0.4 — Add MIT license
5. Task 1.1 — Create PRD directory structure
6. Task 1.2 — Add backend requirements
7. Task 1.3 — Add FastAPI health endpoint
8. Task 2.2 — Add Tokyo venue seed
9. Task 2.3 — Add diverse demo trip seed
10. Task 3.3 — First working Mongo/read-style tool, with fake test data if Atlas is not ready

Do not start live integrations until the seed data, backend health endpoint, and core local tests are working.
