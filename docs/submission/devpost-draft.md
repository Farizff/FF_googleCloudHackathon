# Bounce Devpost Draft

Status: copy-ready draft for BNC-031. Replace bracketed fields before final submission.

## Project name

Bounce

## Tagline

The only AI travel agent built for groups.

## Short description

Bounce helps groups plan, adapt, and settle trips together. It turns one natural-language trip prompt into a group-aware itinerary, flight options, FlockMode sub-groups, disruption recovery, reminders, and split-bill settlement.

## Inspiration

Group trips break down because planning is scattered across chats, spreadsheets, maps, booking links, and payment apps. One person usually becomes the unpaid project manager. Bounce was built around the reality that group travel is not just itinerary generation — it is coordination, governance, live changes, and fairness.

## What it does

Bounce provides:

- Conversational trip planning from one natural-language message.
- Profile gap-fill for missing constraints like dietary needs and pace.
- Group-aware itinerary planning with arrival buffers and visible reasoning.
- Flight search/risk scoring with budget, recommended, and premium options.
- FlockMode for splitting a group into smaller sub-groups with leaders, mini-schedules, and reconvene details.
- Member suggestion review for organisers and co-leaders.
- Live disruption handling through judge test mode.
- Private compliance reminders so visa/passport information is not broadcast to the whole group.
- Split-bill logging with multiple split modes and settlement balances.
- Judge-ready endpoints to reset, seed, and trigger the demo scenario.

## How we built it

- Frontend: responsive vanilla HTML/CSS/JavaScript app shell.
- Backend: FastAPI service deployed on Google Cloud Run.
- Database: MongoDB Atlas, with seeded demo trip data and backend judge endpoints.
- Real-time sync: Firebase Realtime Database publisher integration.
- Cloud: Google Cloud Run in `asia-southeast1`, Secret Manager for live configuration, and Firebase/GCP readiness docs.
- Testing: deterministic Python tests for agent tools, backend APIs, infrastructure readiness, Firebase publishing, and judge routes.

## Google Cloud usage

Bounce uses Google Cloud Run for the live API/app host and Google Secret Manager for production configuration. Firebase Realtime Database supports live group update publishing. The deployed Cloud Run service exposes health and judge-mode endpoints for reviewers.

Live app/API:
https://bounce-api-4dynllwdeq-as.a.run.app/

Judge instructions:
https://bounce-api-4dynllwdeq-as.a.run.app/judge/instructions

## MongoDB usage

Bounce uses MongoDB Atlas as the primary trip database. The live Cloud Run service is wired to a Secret Manager `mongodb-uri` secret and the deployed judge endpoints write demo state to MongoDB-backed collections.

## Judge test mode

Judges can test the app without setup:

1. Open the live app: https://bounce-api-4dynllwdeq-as.a.run.app/
2. Check `/health` or the visible API status badge.
3. Use the judge panel to seed the demo trip.
4. Trigger the disruption flow.
5. Review the UI sections for planning, FlockMode, active trip, and split bill.

Direct endpoints:

```text
GET  /health
GET  /judge/instructions
POST /judge/reset
POST /judge/seed-demo-trip
POST /judge/trigger-disruption
```

## Challenges we ran into

- Keeping the scope realistic for a hackathon while still showing the full group-travel story.
- Separating deterministic demo behavior from live provider dependencies so judges can test reliably.
- Wiring deployed Cloud Run to MongoDB Atlas and Firebase while keeping secrets out of the repo.
- Designing group features that respect privacy, especially visa/compliance reminders.

## Accomplishments we are proud of

- A fixed Kanban contract with 31 cards and explicit cut scope.
- Live Cloud Run deployment with health and judge endpoints.
- MongoDB Atlas-backed judge smoke tests passing on the deployed service.
- Firebase Realtime Database publishing verified from live chat/update paths.
- A demo-first frontend that shows the core group travel flows in one reviewer-friendly app.

## What we learned

Group travel AI needs more than itinerary generation. The hard parts are shared decision-making, permission boundaries, private constraints, live disruption recovery, and money. Building Bounce forced the architecture to treat those as first-class product features.

## What's next

- Add production authentication.
- Replace more deterministic demo providers with live travel APIs as quota allows.
- Expand booking handoff support.
- Add richer mobile polish and accessibility checks.
- Turn FlockMode into a deeper collaborative planning surface.

## Built with

Google Cloud Run, Google Secret Manager, Firebase Realtime Database, MongoDB Atlas, FastAPI, Python, JavaScript, HTML, CSS.

## Links

- Live demo: https://bounce-api-4dynllwdeq-as.a.run.app/
- Source code: https://github.com/Farizff/FF_googleCloudHackathon
- Judge instructions: https://bounce-api-4dynllwdeq-as.a.run.app/judge/instructions
- Demo video: [add final video URL]
