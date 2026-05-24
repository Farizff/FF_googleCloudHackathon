# Bounce Demo Video Script

Status: ready-to-record script for BNC-031.
Target length: 3 minutes hard cap.
Primary live app: https://bounce-api-4dynllwdeq-as.a.run.app/

## Recording setup

- Browser: full-width desktop window.
- Start on the live Bounce app homepage.
- Keep the demo tight: do not explain implementation details on camera unless they support the user value.
- If a live API is slow, use the seeded UI and judge panel as the fallback path.

## Voiceover + screen timeline

### 0:00-0:15 — Hook

Screen: Bounce hero / app shell.

Voiceover:
> Planning one group trip should not take six group chats, five spreadsheets, and one exhausted organiser. Bounce is the AI travel agent built for groups.

Show:
- Bounce logo and tagline.
- Tokyo Reunion demo shell.

### 0:15-0:50 — Conversational planning

Screen: Tell me about your trip.

Voiceover:
> Alex can describe the trip in one natural message: ten friends, Tokyo reunion, food, culture, shopping, and an easy first day. Bounce turns that into structured trip details, asks only for genuine gaps, and keeps private travel preferences separate from group decisions.

Show:
- Trip prompt box.
- Quick details chips.
- Private visa reminder card.

### 0:50-1:15 — Itinerary, flights, budget, map

Screen: Day 1 itinerary, budget estimate, map preview, flight cards.

Voiceover:
> Bounce plans around the real constraints: staggered international arrivals, jet lag, dietary needs, budget, routes, and flight risk. The first shared activity starts only after the group is ready, and flight choices are labelled budget, recommended, and premium with risk scores.

Show:
- Group-ready reasoning line.
- Budget estimate.
- Map preview.
- ANA NH106 recommended card.

### 1:15-1:50 — Group planning + FlockMode

Screen: Group dashboard, suggestion review, FlockMode creation/active view.

Voiceover:
> Groups do not move as one all day. Bounce lets organisers review member suggestions, split travellers into Flocks, assign leaders, and set reconvene details so everyone can explore without losing the group plan.

Show:
- 7 joined / 3 pending group status.
- Suggestion review actions.
- Flock creation and active Flock schedule.
- Reconvene location/time.

### 1:50-2:30 — Judge disruption path

Screen: Judge panel and disruption flow.

Voiceover:
> For judges, the demo includes a test mode. Seed the reunion, trigger a disruption, and Bounce shows how the plan adapts. The backend is live on Cloud Run, writes demo state to MongoDB Atlas, and publishes real-time updates through Firebase Realtime Database.

Show:
- API online badge.
- Seed demo trip button.
- Trigger disruption button.
- Any visible API response or disruption result.

### 2:30-3:00 — Active trip + split bill + close

Screen: Today tab and Split tab.

Voiceover:
> During the trip, Bounce keeps the group moving: today’s schedule, flight status, Flock expenses, and settlement summaries are all in one place. Bounce is not a generic chatbot — it is a group travel operating system.

Show:
- Today in Tokyo.
- Split bill 4-mode UI.
- Balance cards.
- End on Bounce logo or hero.

## Backup short pitch

> Bounce is the only AI travel agent built for groups. It combines conversational planning, group governance, FlockMode, live disruption handling, private compliance reminders, and split bills into one judge-ready travel app deployed on Google Cloud Run with MongoDB Atlas and Firebase Realtime Database.
