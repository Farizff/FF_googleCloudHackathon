# Bounce — Technical PRD v5.0
## Google Cloud Rapid Agent Hackathon 2026 · MongoDB Partner Track
## Supersedes all previous versions (v4.0, v3.0, v2.1)

> **For all engineers and AI coding assistants.**
> This is the single authoritative specification. Every feature, schema, algorithm, data flow, and acceptance criterion lives here. No separate delta docs exist.
> Do not build anything not in this document. When in doubt, stop and ask.
>
> **Layer annotations:** `[L1]` = Prototype only (vanilla JS/HTML, no backend). `[L2]` = Production integration (Vertex AI, MongoDB Atlas, Firebase).

---

## AI BUILD INSTRUCTIONS

Before writing any code:

1. Build prototype as a **single HTML file** — vanilla JS + CSS, no build step, no framework.
2. All assets (fonts, images, icons) **base64-embedded inline** — no external requests.
3. JSX compiled via Babel standalone loaded from CDN in-page.
4. All state lives in React `useState` / `useReducer`. No localStorage/sessionStorage in prototype.
5. Demo data declared as `const` objects at top of data file — no fetch calls.
6. **Read this file completely** before generating any code. Ask if anything is ambiguous.

---

## Quick Reference

| Item | Value |
|---|---|
| App name | Bounce |
| AI persona | Bounce — warm, competent, occasionally witty travel companion |
| Hackathon | Google Cloud Rapid Agent Hackathon 2026 |
| Partner track | MongoDB (MCP integration is primary judging lens) |
| GCP region | `asia-southeast1` |
| Primary AI [L2] | Vertex AI + Gemini via Google Cloud Agent Builder (SSE streaming) |
| Primary DB [L2] | MongoDB Atlas M0, MCP-enabled |
| Realtime [L2] | Firebase Realtime Database (Spark plan) |
| Hosting [L2] | Cloud Run (min-instances=1) + Firebase Hosting |
| Flight tracking [L2] | AeroDataBox via RapidAPI |
| Frontend (prototype) | Vanilla JS + CSS, single HTML file |
| Frontend (production) | React (post-hackathon) |
| Demo URL [L2] | `https://bounce-app.web.app` |

---

## Part 1 — Product Overview

### 1.1 What Bounce Does

Bounce is a group travel planning app. One app handles the full trip lifecycle:

- **PLANNING:** itinerary building, budget setting, flight tracking, polls, AI suggestions
- **ACTIVE:** real-time flock coordination (FlockMode), day-of itinerary, disruption alerts, live expense logging
- **POST-TRIP:** spend breakdown, expense settlement, memories

### 1.2 Platform

Web app, responsive, mobile-friendly. Native apps deferred to v2. Minimum supported width: 360px.

### 1.3 Design Mode

**Mobile-first · Responsive · Light mode only.** Dark mode is out of scope for v1.

---

## Part 2 — Routing Table

```
/                    → Home (trips list)
/trip/:id            → Trip hub (phase dispatcher)
/trip/:id/plan       → Planning view
/trip/:id/active     → Active/today view
/trip/:id/flock      → FlockMode
/trip/:id/wrap       → Post-trip wrap
/chat                → New trip entry (AI conversation)
/join/:token         → Join trip
```

**Removed routes (do not build):** `/compliance`, `/waiting`, `/predeparture`

**[L1] Prototype routing:** Hash-based via `#screen=X&phase=Y&user=Z`. No History API required.

**[L2] Production routing:** History API SPA router. Firebase Hosting rewrite: all paths → `/index.html`.

---

## Part 3 — Role & Permission Matrix

| Action | Organiser | Co-leader | Member |
|---|:---:|:---:|:---:|
| Edit itinerary directly | ✓ | ✓ | ✗ |
| Submit suggestion for review | ✓ | ✓ | ✓ |
| Invite members | ✓ | ✓ | ✗ |
| Set / edit trip budget | ✓ | ✓ | ✗ |
| Accept / decline suggestions | ✓ | ✓ | ✗ |
| Vote on polls | ✓ | ✓ | ✓ |
| Log expenses | ✓ | ✓ | ✓ |
| View itinerary | ✓ | ✓ | ✓ |
| Activate FlockMode | ✓ | ✓ | ✗ |
| Edit Flock-scoped items (Flock leader) | ✓ | ✓ | ✓\* |
| Mark trip complete | ✓ | ✗ | ✗ |
| Remove members | ✓ | ✗ | ✗ |
| Assign / remove Co-leader | ✓ | ✗ | ✗ |
| View compliance cards | Own only | Own only | Own only |

\* Flock leaders can edit their own Flock's sub-itinerary during FlockMode.

**Prototype behaviour:** Activity card edits → `alert('Edit activity (demo)')` for all roles. Suggestions screen shows 2 pending items. Accept/decline = toast notification.

---

## Part 4 — Information Architecture

### 4.1 Navigation Modes

Two nav modes, separated by whether the user is inside a trip.

**Global nav (no active trip):**
- Home (trips list)
- Plan a new trip
- Join a trip
- Profile (accessed via user pill at sidebar bottom — not a nav item)

**Trip-scoped nav (inside a trip):**
- Header strip: `← All trips` back link + trip context card (phase + name)
- Nav items adapt to trip phase:

| Planning phase | Active phase | Post-trip phase |
|---|---|---|
| Group | Today | Trip recap |
| Itinerary | FlockMode | Settle up |
| Flights | Itinerary | |
| Suggestions (badge) | Expenses | |
| | Alerts | |
| | Suggestions (badge) | |

### 4.2 Phase Detection

Trip phase is determined by `trip.state` field:
- `"planning"` → planning nav + planning screens
- `"active"` → active nav + today screen as entry
- `"past"` → post-trip nav + wrap screen as entry

---

## Part 5 — Demo Data

### 5.1 Trips

**Trip 1 — Maya's 30th · Lisbon · PLANNING**

```js
{
  id: 'lisbon-bday',
  name: "Maya's 30th",
  city: 'Lisbon', country: 'Portugal',
  dates: 'Jul 12 – Jul 17, 2025',
  state: 'planning',
  daysToGo: 48, totalDays: 6,
  budget: { total: 2950, perDay: 98, currency: 'EUR' },
  members: ['maya','sofiaA','priyaN','chloe','zara'],
}
```

Members: Maya Chen (Organiser · LHR), Sofia Andrade (Co-leader · AMS), Priya Nair (Member · LHR), Chloe Martin (Member · CDG), Zara Ahmed (Member · MAN)

**Trip 2 — The Reunion · Tokyo · ACTIVE · Day 3 of 7**

```js
{
  id: 'reunion-tk26',
  name: 'The Reunion',
  city: 'Tokyo', country: 'Japan',
  dates: 'Oct 15 – Oct 21, 2026',
  state: 'active',
  activeDay: 3, totalDays: 7,
  members: ['alex','priya','marcus','sofia','jake','aditya','emma','carlos','liam','rania'],
}
```

**Past Trips (3):**

| Trip | Dates | People | Total | Currency |
|---|---|---|---|---|
| CDMX reunion | Jun 2025 | 4 | MX$37,000 (MX$9,250/person) | MXN |
| Seoul food crawl | Nov 2025 | 6 | ₩5,900,000 (₩983,000/person) | KRW |
| Lisbon long weekend | Apr 2026 | 4 | €1,160 (€290/person) | EUR |

**Currency rule:** All wrap screens display destination local currency only. No USD conversion shown.

### 5.2 Multi-City Note [NOT BUILT IN PROTOTYPE]

```js
// MULTI-CITY: PRD supports multiple cities per trip.
// Current demo uses single-city. Extend cities[] array to enable.
// e.g. { id: 'trip1', cities: ['Tokyo', 'Kyoto', 'Osaka'], ... }
```

---

## Part 6 — Screen Catalogue

### 6.1 Home (trips list)

**Component tree:**
```
HomeScreen
  PageBody
    PlanNewTripCTA (deep-purple card, lime + icon)
    TripsSectionUpcoming
      SectionLabel "Upcoming trips"
      TripsRow
        TripCard (planning state) × N
    TripsSectionActive
      SectionLabel "On the road right now"  
      TripsRow
        TripCard (active state) × N
    TripsSectionPast
      SectionLabel "Past trips"
      TripsRow
        TripCard (past state) × N
```

**TripCard states:**
- Planning: lime "In planning" badge · days-to-go counter
- Active: orange "● Day X/Y" badge
- Past: star rating pill + photo count

**Empty state:** "Your trips will appear here. Ready to bounce?" with Plan CTA.

### 6.2 Entry Conversation (Plan a new trip)

**[L1]:** Static entry screen with textarea + Bounce mascot hero. Quick-select chips for trip type.

**[L2]:** POST `/api/chat` → SSE streaming response from Agent Builder. EventSource appends tokens as they arrive.

Bounce auto-parses destination, dates, group size, interests from free-text. No form fields required.

### 6.3 Join Trip

URL: `/join/:token` (production) / screen `joinTrip` (prototype)

Shows trip context card (destination, dates, organiser name). Accepts invite code. Redirects to profile completion on first join.

### 6.4 Profile (tabbed)

Access: user pill at sidebar bottom. First-time users land on About me tab.

**Tabs:**
1. **About me** — name, pronouns, home airport, travel experience, emergency contact, avatar
2. **Food & diet** — dietary restrictions (multi-select chips), strictness level, allergens, free-text notes
3. **How I travel** — interests (chips), pace preference, group-vs-solo tendency, prayer time observance
4. **Past trips** — currently-planning highlight + completed trips with cover orbs
5. **Passport & visas** — nationality, passport expiry, country-specific requirements (private to user)

**Save button:** Persistent at the bottom of each tab's content (not floating). Anchored below last form element. `onClick={() => alert('Saved (demo)')}` in prototype.

### 6.5 Planning — Itinerary

**Layout:** 3-column — day-nav rail (left) · activity cards (center) · budget + map (right)

**View toggle:** Chip row: **Compact** | **Timeline** (default is Duolingo/duo — no chip; clicking active chip returns to default)

**Per-activity 3-dot menu (planning phase, admin roles only):**
- ✏️ Edit → `alert('Edit activity (demo)')`
- 🔄 Suggest swap → `alert('Suggest a swap (demo)')`
- 🗑️ Remove → `alert('Remove activity (demo)')`
Members' edits log as suggestions, not direct changes.

**Budget editor (right rail):**
- Collapsed: shows `Today's budget · $X/$Y · progress bar`
- Expanded (click Edit): two inputs — Trip total per person + Daily cap (derived but overridable)
- **Save button:** Persistent at bottom of edit card (not floating). `onClick closes edit mode`.

### 6.6 Planning — Flights

Shows 3 flight options per origin group. Each card: airline, flight number, dep/arr times, duration, price, risk score.

Risk score: 0–100. Low < 75, Moderate 75–85, High > 85.

### 6.7 Planning — Suggestions

Badge: lime-green unread count, positioned top-right of nav icon (app-icon badge style). Min 16px. White number text.

List of pending suggestions from members. Organiser/Co-leader see Accept + Decline buttons. Members see their own suggestions with status.

### 6.8 FlockMode Creation (planning phase entry point)

Organiser divides group into Flocks (sub-groups). Each Flock gets a name, leader, activity, and reconvene time. Unassigned pool visible until all members assigned.

CTA: single "Start FlockMode →" button (not Save + Start).

### 6.9 Active — Today

Shows current day's schedule. Top status banner shows day count and weather.

**[L1]:** Uses `currentTrip.activeDay` to pick correct itinerary day. Defaults to Day 3 for The Reunion demo.

Quick actions rail: Report disruption · Log expense · Open FlockMode.

### 6.10 Active — FlockMode

Flock switcher (3 cards). Active Flock view: schedule, countdown to reconvene, Flock positions map (SVG).

**Photo sharing placeholder [NOT BUILT]:**
```jsx
<div className="card dashed">
  <div>📸</div>
  <p>Photo sharing coming soon</p>
  <p className="caption">Share live photos with your Flock during the adventure.</p>
</div>
```

**⚠️ IMPORTANT — AI gate for photo sharing feature:**
Before building FlockMode photo sharing, the AI must stop and explicitly ask for:
1. Authorization to proceed with this feature
2. Required assets (user photos, permissions model, storage bucket details)
3. Confirmation of the privacy/consent UX flow
4. Backend storage provider decision (GCS, S3, Firebase Storage, etc.)
Do not build this feature without explicit human sign-off.

### 6.11 Active — Disruption Modal

Triggered when venue closes. Shows 3 alternative venues with transit time, cost, duration, and reasoning. Organiser/Co-leader can select and broadcast to all members.

CTA: "Lock this in & ping everyone →"
Cancel: "Not now"

### 6.12 Active — Expenses (Split Bill)

4 split modes: Everyone · Specific people · My Flock · Just me

6 categories: Food · Transport · Accommodation · Activity · Shopping · Other

**[L2]:** Expense list synced to MongoDB. Settlement calculation via minimum-transactions algorithm. Currency conversion via ExchangeRate-API.

### 6.13 Active — Alerts

Push notifications and in-app alerts list. Flight status changes, disruptions, member check-ins.

### 6.14 Post-trip — Wrap

**Trip-aware:** Renders from `WRAP_DATA[trip.id]`. Each past trip shows its own:
- Total spend in destination currency (no USD conversion)
- Per-person amount
- Category breakdown (bar charts, %)
- Settlement summary (who pays whom, how much)
- BounceSay observation

**Travel DNA: REMOVED from v1 scope.**

---

## Part 7 — Screen × State Matrix

| Screen | Loading | Empty | Error | Populated |
|---|---|---|---|---|
| Home | Skeleton trip cards | "Your trips will appear here" + Plan CTA | Toast "Couldn't load trips" + retry | Trip cards by state bucket |
| Entry | — | Cursor blink in textarea | Toast "Something went wrong" | Typed text + Bounce response |
| Profile | Skeleton fields | First-time wizard on About me | Toast + retry | Filled fields |
| Itinerary | Skeleton day rail + cards | "Bounce is building your itinerary…" | "Couldn't generate itinerary" + retry | Day navigation + activity cards |
| Flights | Skeleton rec-cards | "Bounce is looking for flights…" | "Couldn't fetch flights" + manual entry | 3 rec-cards per origin |
| Suggestions | Skeleton | "No suggestions yet. Trip looks great." | Toast | Suggestion cards + Accept/Decline |
| Today | Skeleton | — | Toast + previous day shown | Status banner + schedule |
| FlockMode | Skeleton | — | Toast | Flock switcher + schedule + countdown |
| Disruption | — | — | Toast | 3 alternatives + CTA |
| Expenses | Skeleton | "No expenses logged yet." | Toast | Log form + balance table |
| Wrap | Skeleton | "Nothing to wrap yet." | Toast | Spend breakdown + settlement |
| Alerts | Skeleton | "You're all clear." | Toast | Alert cards |

---

## Part 8 — Data Model → UI Binding

| Data field | UI element |
|---|---|
| `trip.state` | TripCard badge · sidebar nav items · phase dispatcher |
| `trip.activeDay` | TodayScreen day banner + itinerary day picker |
| `trip.totalDays` | "Day X of Y" subtitle in top bar |
| `trip.budget.total` | BudgetCard trip total input (editable) |
| `trip.budget.perDay` | BudgetCard daily cap input (editable) |
| `trip.members[]` | AvatarStack on TripCard + Group screen member list |
| `member.role` | Nav permission gating · 3-dot menu visibility · chat response framing |
| `member.dietary` | Bounce suggestion reasoning on restaurant cards |
| `member.visa` | Compliance card render on Profile (private) |
| `member.flock` | FlockMode assignment + active Flock view |
| `itinerary[day].items[]` | ActivityCard list in Itinerary + Today screens |
| `itinerary[day].flockMode` | Shows FlockMode banner on day card |
| `item.isDisrupted` | "⚠ Venue closed" tag on ActivityCard |
| `item.disruptable` | Enables disruption trigger for item |
| `suggestion.supporters[]` | "N others agree" count on suggestion card |
| `expense.amount` | Split bill balance calculation |
| `expense.splitMode` | Which members see the charge |
| `wrapData[tripId].categories[]` | Category bar charts in WrapScreen |
| `wrapData[tripId].settlements[]` | Settlement rows in WrapScreen |
| `wrapData[tripId].currencySymbol` | Currency prefix on all wrap amounts |

---

## Part 9 — AI Conversation Flows

### 9.1 Entry (new trip)

1. User types trip description in free text
2. **[L1]:** Bounce "types" a response using setTimeout mock
3. **[L2]:** POST `/api/chat` → SSE stream → tokens appended to Bounce message bubble

Bounce parses: destination, dates, group size, budget hints, interests. Auto-populates itinerary draft.

### 9.2 In-trip Bounce chat

- **Organiser/Co-leader:** "Changes apply directly"
- **Member:** "Suggestions logged for organiser"
- **Flock leader (during FlockMode):** "Flock changes apply directly · main suggestions logged"

Bounce references `activeUser.role` to frame its response.

### 9.3 Disruption

1. Venue closes → disruption event triggers
2. Bounce surfaces 3 alternatives with reasoning
3. User selects → Bounce sends Firebase push to all members

**[L1] Disruption trigger:** Demo button in Judge Panel → `simulateDisruption()` → toast + modal open.

---

## Part 10 — Future Features (NOT IN V1 PROTOTYPE)

### 10.1 FlockMode Photo Sharing

**AI gate (mandatory):** See Section 6.10. Do not build without explicit authorization.

Schema sketch (for future reference):
```js
// FlockPhoto: stored in GCS/Firebase Storage, metadata in MongoDB
{
  tripId: String,
  flockId: Number,
  uploadedBy: String, // member.id
  url: String,
  thumbnailUrl: String,
  timestamp: Date,
  sharedWith: ['flock' | 'everyone'],
  consentGranted: Boolean,
}
```

### 10.2 Multi-City Trips

Current demo: single city per trip. PRD supports multi-city via `cities[]` array on trip object.

```js
// Extend trip object:
{
  id: 'trip-id',
  // MULTI-CITY: PRD supports multiple cities per trip.
  // Current demo uses single-city. Extend cities[] array to enable.
  cities: [{ name: 'Tokyo', nights: 4 }, { name: 'Kyoto', nights: 3 }],
  // ...
}
```

### 10.3 Member Join Flow (Post-Code-Entry)

After `/join/:token`, member needs:
1. Profile completion (About me tab minimum)
2. View of committed itinerary + group
3. Flight selection for their origin

This flow is specced but not built in prototype.

### 10.4 Suggestions ↔ Itinerary Loop

Accept tapping a suggestion should animate the activity into the correct day in the itinerary. Currently: toast only.

### 10.5 Multi-Currency Trip Budget

Trip total + daily budget currently USD only. Currency switcher needed to support EUR, JPY, etc. natively.

---

## Part 11 — [L2] Backend Specification

### 11.1 Health Endpoint

```python
GET /health
→ {"status":"ok","version":"v5","mongo":"connected","firebase":"connected"}
```

### 11.2 Chat Endpoint (SSE)

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

### 11.3 MongoDB Collections

- `group_trips` — trip metadata, member list, phase, budget
- `itineraries` — day-by-day activity arrays, flock assignments
- `expenses` — log entries with split mode + member refs
- `suggestions` — pending member suggestions with status
- `traveller_profiles` — per-member profile data (partially private)
- `flights` — flight options per trip, per origin group

### 11.4 Firebase Collections

- `trips/{tripId}/members/{memberId}/location` — real-time location during FlockMode
- `trips/{tripId}/alerts` — push alerts broadcast to all members
- `trips/{tripId}/flock_status` — Flock check-in status

### 11.5 Deployment

```bash
gcloud run deploy bounce-api \
  --image=gcr.io/bounce-hackathon-2026/bounce-api:v5 \
  --region=asia-southeast1 \
  --min-instances=1 \
  --max-instances=10 \
  --memory=1Gi \
  --allow-unauthenticated
```

`min-instances=1` is required for demo warm start.

---

## Part 12 — Demo Scenario (Judge Mode)

1. Open app → Home shows 5 trips (1 planning, 1 active, 3 past)
2. Click Maya's 30th (Lisbon, planning) → itinerary, budget, flights, suggestions
3. Click back → click The Reunion (Tokyo, active) → Day 3 view, FlockMode, expenses
4. Judge Panel (draggable, bottom-left): switch role between Organiser / Co-leader / Member
5. Trigger disruption → Day 7 teamLab closure → select Mori Art Museum → toast
6. Click past trip (CDMX, Seoul, or Lisbon LW) → wrap screen shows trip-specific local currency data

Judge Panel label: `⚡ Demo controls · drag me`

---

*Bounce Technical PRD v5.0*
*Consolidates: PRD v4.0 + Design v3.0 delta + v5 changes*
*Design system, CSS, and component specs → `bounce_design_v5.md`*
