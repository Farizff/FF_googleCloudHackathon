# Bounce — Technical PRD v2.1 (synchronized)
## Google Cloud Rapid Agent Hackathon 2026 · MongoDB Partner Track

> **CS and Aero engineers: read this entire document before writing any code.**
> Every schema, every API, every algorithm, every build sequence is here.
> If something is not here, ask in the team chat before improvising.
>
> **For all UI implementation, components, and screen specifications, see `bounce_design_v2.md`.**
> **For demo scenario member assignments, FlockMode composition, and timing, this PRD is the source of truth.**

---

## Quick reference

| Item | Value |
|---|---|
| App name | Bounce |
| Persona | Bounce (the AI travel companion) |
| Hackathon | Google Cloud Rapid Agent Hackathon 2026 |
| Partner track | MongoDB |
| Submission target | 1 day before hard deadline (always submit early) |
| GCP region | `asia-southeast1` |
| Primary AI | Vertex AI + Gemini via Google Cloud Agent Builder |
| Primary DB | MongoDB Atlas M0 (free, MCP-enabled) |
| Hosting | Google Cloud Run (min 1 instance — paid for warm start) |
| Repository | GitHub public, MIT license |
| Demo length | 3 minutes primary + Devpost screenshots for full coverage |

---

# PART 0 — DAY 1 CRITICAL CHECKLIST

> **Nothing below is optional. Every item on this list must be actioned on Day 1 or the build is at risk.**
> CS engineer owns this list. Aero engineer assists where flagged.

## P0.1 — Amadeus production credentials (CS, Day 1, blocking)

The Amadeus test sandbox returns fabricated flight numbers. The demo cannot use it. Production credentials must be applied for on Day 1 because approval takes 1–5 business days.

**Action:**
1. Go to `developers.amadeus.com` and create an account
2. Create a new app, request **Production** environment access
3. Project description: "Google Cloud Rapid Agent Hackathon 2026 — group travel planning agent"
4. Submit and check email for approval (usually within 48 hours)
5. While waiting, build against test sandbox with mock-marked data
6. Once approved, run validation: search SFO→NRT flights and confirm real flight numbers (e.g. UA837, NH106) come back
7. If denied or delayed past Day 3, email `developer-support@amadeus.com` directly with hackathon details

**Validation script (run as soon as keys arrive):**
```python
from amadeus import Client
amadeus = Client(client_id=PROD_ID, client_secret=PROD_SECRET, hostname='production')
r = amadeus.shopping.flight_offers_search.get(
    originLocationCode='SFO', destinationLocationCode='NRT',
    departureDate='2026-10-15', adults=1, max=3
)
print([(o['validatingAirlineCodes'][0], o['itineraries'][0]['segments'][0]['number']) for o in r.data])
# Expected: [('UA', '837'), ('NH', '106'), ...] — real numbers, not fakes
```

## P0.2 — GCP project + paid services setup (CS, Day 1)

```bash
# Project creation
gcloud projects create bounce-hackathon-2026 --name="Bounce"
gcloud config set project bounce-hackathon-2026

# Enable billing (required for paid items below)
# Do this via console: GCP Console → Billing → Link billing account

# Enable all required APIs in one command
gcloud services enable \
  run.googleapis.com aiplatform.googleapis.com dialogflow.googleapis.com \
  pubsub.googleapis.com cloudscheduler.googleapis.com translate.googleapis.com \
  maps-backend.googleapis.com places-backend.googleapis.com \
  firebasedatabase.googleapis.com secretmanager.googleapis.com

# Set region
gcloud config set run/region asia-southeast1
```

**Paid configurations (approved budget approximately $20 for the hackathon period):**

Cloud Run minimum instances — prevents cold start:
```bash
# After first deployment
gcloud run services update bounce-api --min-instances=1 --region=asia-southeast1
```

AeroDataBox RapidAPI Basic plan — subscribe at `rapidapi.com/aedbx-aedbx/api/aerodatabox/pricing`. Basic tier: $10/month, 5,000 calls. Required for live flight tracking.

## P0.3 — MongoDB Atlas + MCP setup (CS, Day 1)

1. Create free M0 cluster at `cloud.mongodb.com` — region: AWS / Singapore (closest to GCP `asia-southeast1`)
2. Database: `bounce`
3. Create these 10 MongoDB collections immediately (empty is fine):
   - `traveller_profiles`
   - `group_trips`
   - `itineraries`
   - `flight_performance`
   - `airline_ratings`
   - `visa_requirements`
   - `venue_enrichment`
   - `expenses`
   - `suggestions`
   - `notification_log`

   > Note: `chat_threads` is **not** a MongoDB collection. Chat messages live in Firebase Realtime Database for live sync — see Part 7.4.
4. Network access: whitelist `0.0.0.0/0` for hackathon simplicity
5. Database user: `bounce-app` with read/write to `bounce` database
6. Enable MongoDB MCP server — follow `mongodb.com/docs/atlas/data-api/mcp/`
7. Save connection string to GCP Secret Manager as `mongodb-uri`

## P0.4 — Firebase Realtime Database (CS, Day 1)

```bash
npm install -g firebase-tools
firebase login
firebase use --add bounce-hackathon-2026
firebase init database
```

Database structure (initial rules — open during hackathon):
```json
{
  "rules": {
    ".read": "auth != null || true",
    ".write": "auth != null || true"
  }
}
```

> Real auth not implemented for hackathon. Acknowledge in Devpost description.

## P0.5 — Pre-seed datasets (Aero engineer owns, Days 1–3)

Three datasets must be ready before itinerary generation can be tested end-to-end. Aero engineer curates these in parallel with CS engineer's tool building.

### P0.5.a — `airline_ratings` (top 100 airlines)

Format: JSON file at `db/seed/airline_ratings.json`. Source: Skytrax 2024 rankings (publicly available at `skytraxratings.com`). Update last verified to today's date.

```json
[
  {
    "iata": "NH",
    "name": "All Nippon Airways",
    "skytrax_rating": 5,
    "airhelp_score": 8.21,
    "last_verified": "2026-MM-DD"
  },
  {
    "iata": "JL", "name": "Japan Airlines",
    "skytrax_rating": 5, "airhelp_score": 8.15,
    "last_verified": "2026-MM-DD"
  }
  // ... 98 more
]
```

Minimum coverage: all 5-star and 4-star Skytrax airlines, plus all major US (UA, DL, AA, AS, B6, WN), European (BA, AF, KL, LH, IB, FR, U2), Asian (NH, JL, KE, OZ, SQ, CX, TG, MH, GA), Middle Eastern (EK, EY, QR, SV), and Australian (QF, JQ, VA) carriers.

### P0.5.b — `visa_requirements` (top 30 common pairs, manually validated)

Format: JSON file at `db/seed/visa_requirements.json`. Source: manually verified from each country's official embassy or government immigration website. Validated by Aero engineer.

```json
[
  {
    "passport_iso": "IDN",
    "destination_iso": "JPN",
    "visa_required": true,
    "visa_type": "consulate-visa",
    "processing_days_min": 5,
    "processing_days_max": 14,
    "official_url": "https://www.id.emb-japan.go.jp/visa.html",
    "fee_usd_estimate": 25,
    "notes": "Standard tourist visa. Single entry, up to 90 days. Apply via Japan Embassy Jakarta or visa application center.",
    "last_verified": "2026-MM-DD"
  }
]
```

**Required 30 pairs** (judges most likely to test these — make all bidirectional where it makes sense):

Indonesians → Japan / Singapore / Australia / USA / UK / Schengen
Indians → Japan / USA / UK / Schengen / Singapore / Australia
US passport → Japan / China / Brazil / Schengen / UK / Australia
UK passport → USA / Japan / Australia / Schengen
Filipinos → Japan / Singapore / USA / Schengen
Brazilians → Japan / USA / Schengen / UK
Egyptians → Japan / USA / UK
Mexicans → Japan / USA / UK / Schengen

For anything not in this seed, Gemini web search fallback (see Tool 12: `get_visa_requirements`).

### P0.5.c — `venue_enrichment` (top 100 venue categories globally)

Format: JSON at `db/seed/venue_enrichment.json`. Stores intelligence Google Places API does not provide. Aero engineer curates from general travel knowledge — these are category-level defaults, not specific venues.

```json
[
  {
    "category_pattern": "buddhist_temple",
    "google_place_types": ["place_of_worship", "tourist_attraction"],
    "physical_intensity": "low",
    "estimated_duration_minutes": 60,
    "crowd_peak_weekday": {"start": "10:00", "end": "14:00"},
    "crowd_peak_weekend": {"start": "09:00", "end": "16:00"},
    "customs": {
      "dress_code": "covered shoulders and knees",
      "shoes_off": true,
      "head_covering": false,
      "photography_allowed": "exterior only typically",
      "behavioural_notes": "remain quiet, do not point feet at altar"
    },
    "dietary_relevance": "none",
    "child_friendly": true,
    "elderly_friendly": true,
    "wheelchair_accessibility": "varies"
  },
  {
    "category_pattern": "art_museum",
    "google_place_types": ["museum", "art_gallery"],
    "physical_intensity": "medium",
    "estimated_duration_minutes": 120,
    "crowd_peak_weekday": {"start": "11:00", "end": "15:00"},
    "crowd_peak_weekend": {"start": "10:00", "end": "17:00"},
    "customs": {"photography_allowed": "no flash", "behavioural_notes": "no food or drink"},
    "child_friendly": false,
    "elderly_friendly": true,
    "wheelchair_accessibility": "usually full"
  }
  // ... 98 more categories
]
```

**Required 100 categories** organised by group:
- Religious sites (temple, mosque, church, shrine, synagogue) × major traditions
- Cultural (museum types — art, history, science, contemporary)
- Outdoor (park, garden, beach, hiking trail, viewpoint)
- Food (street market, fine dining, casual restaurant, food hall, café)
- Entertainment (theme park, observatory, immersive experience, performance)
- Shopping (department store, district shopping, boutique, market)
- Activity (escape room, sports activity, cooking class)
- Transit (train station observation, scenic ride)
- Historical (castle, palace, ruin, monument, memorial)
- Nature (zoo, aquarium, botanical garden, nature reserve)

If Google Places API returns a venue type not in this enrichment, the agent uses category-fallback defaults (medium intensity, 90min duration, no specific customs). The agent never crashes on unknown venue types.

---

# PART 1 — PRODUCT OVERVIEW

## 1.1 What Bounce is

Bounce is an AI-powered group travel planning app. It handles everything from the first conversation to the final expense settlement. The core innovation: treating group coordination, multi-modal transport, per-member compliance, FlockMode for parallel sub-group adventures, and real-time disruption as first-class features.

Bounce is also a persona. The AI presents itself as "Bounce" — a warm, competent, occasionally witty travel companion.

## 1.2 Group types

Detected automatically from the initial conversation:
- **Friends** — flexible schedule, equal cost split, nightlife eligible
- **Family** — multi-generational logic, child venues, elderly pacing, rest blocks
- **Office** — professional tone, team-building venues, expense report structure

## 1.3 Trip modes

- **International** — full flow including flights, visa compliance, currency, customs
- **Domestic** — simplified flow, no flights/visa/currency, all core features remain

## 1.4 Bounce persona

System prompt-enforced behaviours:
- Always introduces as "Bounce" on first interaction
- Speaks first person, casual but competent
- Keeps responses concise — never walls of text
- Celebrates milestones ("Your trip is locked in!")
- Handles disruptions calmly ("Heads up — slight hiccup. I've already found 3 alternatives.")
- Never robotic, never corporate
- Acknowledges when it does not know something — never fabricates
- Honest about data sources ("I pulled live flights from Amadeus — prices are estimates until you book")

## 1.5 Demo scenario — The Reunion

10 Bay Area friends, 26–28 years old, reuniting 5 years after college. Tokyo, 10 days, $3,500 per person target.

| Member | Origin | Nationality | Japan visa |
|---|---|---|---|
| Alex Chen (organiser) | SFO | USA | Visa-free |
| Priya Patel (co-leader) | SFO | India | **Required** |
| Marcus Johnson | SFO | USA | Visa-free |
| Sofia Gutierrez | LAX | Mexico | Visa-free |
| Jake Kim | LAX | South Korea | Visa-free |
| Aditya Sharma | JFK | India | **Required** |
| Emma Clarke | JFK | UK | Visa-free |
| Carlos Mendez | SEA | Brazil | Visa-free |
| Liam Murphy | SEA | Ireland | Visa-free |
| Rania Hassan | ORD | Egypt | **Required** |

Three need visas (privacy-preserving compliance feature: Priya, Aditya, Rania receive private nudges).

**FlockMode on Day 5** — main organiser Alex creates 3 Flocks, reconvene at Shinjuku Station East Exit at 18:30:

| Flock | Name | Leader | Members | Activity |
|---|---|---|---|---|
| Flock 1 | The Explorers | Priya | Alex, Priya, Aditya, Emma | teamLab Borderless (Odaiba) |
| Flock 2 | The Foodies | Marcus | Marcus, Sofia, Liam | Tsukiji Outer Market + Yanaka neighbourhood |
| Flock 3 | The Shoppers | Jake | Jake, Carlos, Rania | Harajuku Takeshita Street + Shibuya |

**Disruption on Day 7** (demo trigger) — main group's afternoon venue closure. Bounce returns 3 alternatives via the apply_disruption pipeline (see Part 6.3).

## 1.6 Out of scope (do not build)

These features were considered and explicitly **cut** during planning. If you find yourself building any of them, stop and reconfirm with the team. Cuts were made to protect the 16-day timeline and focus on demo-differentiating features.

| Cut feature | Reason |
|---|---|
| **Travel DNA read-back on subsequent trips** | The Travel DNA is generated at trip end and saved to the profile (kept). Reading it back on the next trip to influence planning is cut — never demonstrated in the 3-minute demo. The data flywheel story is told in the Devpost description. |
| **Receipt scanning via Cloud Vision API** | Manual expense entry only. Vision API quota was a real risk and the demo barely shows receipt capture. |
| **AI-generated packing list** | Replaced with a static template per group type if pre-departure screen is built at all. Not on the demo path. |
| **AI-generated trip narrative at post-trip** | Replaced with a structured summary card (spending breakdown, Travel DNA cards, next trip seeds). The narrative was decorative. |
| **Multi-language UI** | English-only interface. Cloud Translation API is used only for contact notification emails. |
| **Cultural briefing per nationality at trip confirmation** | Replaced by just-in-time customs prompts in the venue cards (`customs_note` field). Saves a screen, keeps the feature value. |
| **In-app GPS / real-time location tracking** | "Open in Google Maps" button hands off to native navigation. No GPS tracking in Bounce. |

If any of these would have moved the needle for Silicon Valley judges, the team's prior assessment was that they would not. Revisit only after every kept feature on the testing checklist (Part 15) is passing.

---

# PART 2 — ARCHITECTURE

## 2.1 System overview

```
User (browser / PWA)
       │
       ├── Firebase Realtime DB ◄── (broadcasts state changes to all members)
       │
       ▼
Google Cloud Run (FastAPI backend, min 1 instance)
       │
       ├── Google Cloud Agent Builder (Gemini + Vertex AI streaming)
       │      │
       │      ├── 14 agent tools (see Part 5)
       │      │
       │      └── System prompt loaded from agent/system_prompt.txt
       │
       ├── MongoDB Atlas via MCP (all data layer)
       ├── Firebase Realtime DB (group event broadcasting, chat threads)
       ├── Cloud Pub/Sub (disruption events, flight status changes)
       └── Cloud Scheduler (timed reminders)
```

## 2.2 GCP services

| Service | Purpose | Cost |
|---|---|---|
| Vertex AI + Gemini | Agent reasoning, all NLU | Free quota |
| Google Cloud Agent Builder | Tool orchestration, streaming | Free tier |
| Firebase Realtime DB | Live group sync, chat threads | Free Spark |
| Cloud Pub/Sub | Disruption events, alerts | Free tier |
| Cloud Scheduler | Timed reminders | 3 jobs free |
| Cloud Run | Backend hosting | **$5–10/mo (min instance)** |
| Google Maps Platform | Directions, Places, Maps JS | $200/mo credit |
| Secret Manager | API keys | Free tier |

## 2.3 External APIs

| API | Purpose | Cost |
|---|---|---|
| **Amadeus production** | Live flight search, delay prediction | Free (with hackathon approval) |
| **AeroDataBox** | Live flight status polling | **$10/mo (Basic tier)** |
| Google Places API | Venue search globally (primary venue source) | Within $200 Maps credit |
| Rome2Rio | Multi-modal transport globally | Free tier |
| Open-Meteo | Weather forecasts | No key needed |
| OpenSky Network | Historical flight on-time data | Completely free |
| ExchangeRate-API | Currency conversion | 1500 req/mo free |
| MongoDB Atlas MCP | Data storage and MCP | M0 free |
| SendGrid | Contact notification emails | 100/day free |

**Total paid cost during hackathon: approximately $20.**

---

# PART 3 — ENVIRONMENT VARIABLES

Mirror all in GCP Secret Manager. `.env.example` for local development.

```env
# GCP
GCP_PROJECT_ID=bounce-hackathon-2026
GCP_REGION=asia-southeast1
AGENT_BUILDER_AGENT_ID=

# MongoDB
MONGODB_CONNECTION_STRING=
MONGODB_DATABASE=bounce

# Firebase
FIREBASE_DATABASE_URL=https://bounce-hackathon-2026-default-rtdb.firebaseio.com/
FIREBASE_SERVICE_ACCOUNT_KEY=path/to/key.json

# Google APIs
GOOGLE_MAPS_API_KEY=
GEMINI_API_KEY=

# Amadeus (PRODUCTION — not test)
AMADEUS_CLIENT_ID=
AMADEUS_CLIENT_SECRET=
AMADEUS_HOSTNAME=production

# AeroDataBox via RapidAPI
RAPIDAPI_KEY=
AERODATABOX_HOST=aerodatabox.p.rapidapi.com

# OpenSky (free, register at opensky-network.org)
OPENSKY_USERNAME=
OPENSKY_PASSWORD=

# Rome2Rio
ROME2RIO_API_KEY=

# SendGrid
SENDGRID_API_KEY=
SENDGRID_FROM_EMAIL=bounce@yourdomain.com

# ExchangeRate-API
EXCHANGE_RATE_API_KEY=

# Open-Meteo: no key required
```

---

# PART 4 — REPOSITORY STRUCTURE & BUILD ORDER

```
bounce/
├── README.md                       # Setup + demo instructions
├── LICENSE                         # MIT
├── .env.example
├── .gitignore
├── requirements.txt
├── package.json                    # frontend
├── Dockerfile                      # for Cloud Run
├── cloudbuild.yaml
│
├── agent/
│   ├── system_prompt.txt           # Bounce persona + behavioural rules
│   ├── agent_config.yaml           # Agent Builder tool registration
│   └── tools/                      # 14 agent tools — build in order below
│       ├── get_traveller_profile.py
│       ├── search_venues.py        # Google Places + MongoDB enrichment
│       ├── save_itinerary.py
│       ├── get_transit_time.py     # Google Maps
│       ├── optimise_route.py       # core algorithm
│       ├── get_weather.py          # Open-Meteo
│       ├── search_accommodation.py # Google Places hotels + Gemini estimates
│       ├── search_flights.py       # Amadeus production
│       ├── score_flight_risk.py    # weighted formula
│       ├── get_multi_modal.py      # Rome2Rio
│       ├── apply_disruption.py     # the demo wow moment
│       ├── notify_contacts.py      # SendGrid
│       ├── get_visa_requirements.py # MongoDB + Gemini fallback
│       └── poll_flight_status.py   # AeroDataBox + 30min cache
│
├── db/
│   ├── schemas/                    # JSON Schema per collection
│   └── seed/
│       ├── airline_ratings.json    # top 100 airlines (P0.5.a)
│       ├── visa_requirements.json  # top 30 nationality-destination pairs (P0.5.b)
│       ├── venue_enrichment.json   # 100 venue categories (P0.5.c)
│       └── seed_demo_trip.json     # The Reunion pre-seeded for judges
│
├── api/
│   ├── main.py                     # FastAPI entry
│   └── routes/
│       ├── chat.py                 # POST /chat — main Bounce conversation
│       ├── trip.py                 # CRUD trips
│       ├── itinerary.py
│       ├── disruption.py           # POST /trigger-disruption (demo button)
│       ├── expenses.py             # split bill
│       ├── flights.py
│       ├── flight_status.py        # polling endpoint
│       ├── group.py                # invites, FlockMode, co-leader management
│       └── judge.py                # judge test mode — reset, seed sample data
│
├── workers/
│   ├── flight_poller.py            # Cloud Scheduler-triggered
│   └── reminder_dispatcher.py      # Cloud Scheduler-triggered
│
└── frontend/
    ├── index.html
    ├── manifest.json               # PWA manifest
    ├── sw.js                       # offline itinerary cache
    ├── app.js
    └── style.css
```

## 4.1 Build sequence (CS + Aero in parallel)

**Stop the build at any point if the previous step does not work.** Do not stack failures.

> Tool numbers in Part 8 (Tool Contracts) are logical groupings, not build order. The build sequence below uses tool **names** to avoid confusion.

**Days 1–2 — Foundation**
- (CS) GCP project, all APIs enabled, Cloud Run hello-world deployed
- (CS) MongoDB Atlas cluster live, MCP enabled, all 10 collections created
- (CS) Firebase Realtime DB initialised
- (CS) Amadeus production application submitted
- (Aero) Begin `airline_ratings.json` curation
- (Biz 1) Frontend skeleton: index.html, basic Bounce chat UI (no logic yet)

**Days 3–5 — Core agent loop**
- (CS) Build `get_traveller_profile`, `search_venues` (with Places + enrichment), `save_itinerary` — test each against MongoDB
- (CS) Build `get_transit_time` — verify Maps API returns
- (CS) Build `optimise_route` — implement full algorithm (see Part 6)
- (CS) Build `get_weather` — verify Open-Meteo returns
- (CS) Agent system prompt loaded, basic conversation working end-to-end
- (Aero) Complete `airline_ratings.json` and load to MongoDB
- (Aero) Begin `visa_requirements.json` and `venue_enrichment.json`
- (Biz 1) Profile gap-fill UI with chip selectors
- (Biz 2) Itinerary day view + budget tracker UI

**Days 6–8 — Flights and disruption**
- (CS) Build `search_accommodation` (Google Places hotels)
- (CS) Build `search_flights` — switch to Amadeus production keys
- (CS) Build `score_flight_risk` with airline_ratings lookup
- (CS) Build `get_multi_modal_transport` — Rome2Rio
- (CS) Build `apply_disruption` — full 6-step pipeline (see Part 6)
- (CS) Build `get_visa_requirements` — MongoDB lookup + Gemini fallback
- (Aero) Complete `visa_requirements.json` and `venue_enrichment.json`
- (Biz 2) Google Maps JS embedded, venue pins, route rendering
- (Biz 1) Flight selection UI (handles 5 origin cities × 3 options layout)

**Days 9–11 — Group features**
- (CS) Build `notify_contacts` — SendGrid
- (CS) Firebase real-time sync wired
- (CS) Invite token system + co-leader role management
- (CS) FlockMode backend — Flock CRUD, per-Flock chat threads in Firebase
- (CS) Suggestion aggregation pipeline (members → admin layer)
- (Biz 2) Group dashboard UI
- (Biz 1) FlockMode UI: Flock creation, per-Flock map view, reconvene reminder display
- (Biz 2) Suggestion review panel for admins

**Days 12–13 — Active trip**
- (CS) Build `poll_flight_status` — AeroDataBox + 30min cache + Pub/Sub
- (CS) Cloud Scheduler jobs for: flight polling, evening briefing, check-in reminders
- (CS) Split bill backend: 4 logging modes, settlement algorithm (see Part 6)
- (Biz 1) Split bill UI with 4-mode logging
- (Biz 2) Active trip view, today's schedule, disruption trigger button

**Days 14–15 — Demo polish**
- (CS) Judge test mode endpoints (`/judge/reset`, `/judge/seed-demo-trip`)
- (CS) Error and loading states across all tools
- (CS) Rate limiting on Bounce chat (5 msgs / 10 sec)
- (CS) Streaming responses verified end-to-end
- (Aero) Seed `seed_demo_trip.json` with The Reunion exactly as scenario
- (All) End-to-end demo walkthrough — fix anything broken

**Day 16 — Submission buffer**
- (Biz 2) Demo video recording
- (Biz 2) Demo video editing — 3 minutes hard cap
- (Biz 1) Devpost form complete with screenshots
- (CS) Final repo cleanup, README, MIT license visible at top
- (CS) Production deployment verified, judge test endpoints live

> **Submit by end of Day 16. Never submit on the deadline day.**

---

# PART 5 — BOUNCE SYSTEM PROMPT

Save as `agent/system_prompt.txt`. Load into Agent Builder.

```
You are Bounce, an AI group travel companion. You are warm, competent, and occasionally witty. You speak like a knowledgeable friend, never like a corporate assistant.

PERSONALITY:
- Introduce yourself as "Bounce" on first interaction only
- Use first person throughout
- Keep responses concise — never walls of text
- Celebrate milestones briefly ("Your trip is locked in!")
- Handle disruptions calmly: "Heads up — [issue]. I've already found 3 alternatives."
- Never use phrases like "I have processed your request" or "Please find below"
- Match the user's tone — casual if they are casual, professional if they are professional (this is important for the Office trip group type)

CORE BEHAVIOURS — APPLY ALWAYS:
- International arrivals require +150min from landing for shared activity start
- Domestic arrivals require +90min
- Departure day: last activity must end >= 3h before departure (international) or >= 2h (domestic)
- Group venues geographically before sequencing by time
- Apply energy logic (see Part 6 algorithm)
- Attach a one-line reasoning note to every scheduling decision
- For disruptions: restructure the affected day fully before responding — do not just flag the problem
- After apply_disruption, always call notify_contacts
- Always present exactly 3 options for any recommendation (accommodation, flights, transport, dining, alternatives) labelled budget / recommended / premium
- If fewer than 3 genuinely exist, return what exists and explain why

INTENT CLASSIFICATION:
When the user sends a message during planning, classify the intent before acting:
- PARTIAL CHANGE: "make Day 2 slower", "remove the museum", "add Tsukiji" → call only the affected tools
- FULL REPLAN: "let's go to Kyoto instead", "change to 14 days", "actually all-vegan trip" → confirm with user first, then re-run the full pipeline
- INFORMATION QUERY: "is tap water safe here?", "what's the tipping rule?" → answer directly, no tool call needed unless you must search the web
- BUDGET QUESTION: "can we afford to add X?" → call budget impact tool, return numeric answer

SECURITY AND PRIVACY:
- Never request passport numbers, payment card details, or national IDs
- If a user shares sensitive data, acknowledge calmly: "Heads up — I don't need or store that. Let's continue without it."
- Only surface booking links from approved domains (see link validation in Part 7)
- Warn before redirecting to any external payment or booking page
- NEVER expose one member's nationality, health, visa status, or budget to other members in the group chat
- When a member's compliance item needs action, message them PRIVATELY — never via the group thread

GROUP GOVERNANCE:
- Organiser: applies changes immediately. Full admin.
- Co-leaders (max 2): identical admin to organiser. Cannot remove the organiser.
- Members: chat messages logged as suggestions. AI aggregates similar requests and surfaces to admins at natural moments. Never apply directly.
- FlockMode: each Flock has its own leader with admin scope WITHIN that Flock only. Cannot affect other Flocks or the main trip. Main organiser is the only one who can start FlockMode and end it.

FLIGHT RECOMMENDATIONS:
- Show 3 options per member's origin city: budget-optimised, recommended (best risk-adjusted), premium
- Show risk score per option with one-paragraph plain-language explanation
- Group members from the same origin city should see flights consolidated

DATA HONESTY:
- Prices are estimates until booking is confirmed at the airline/hotel site
- Flight status is live data with up to 30min staleness
- Crowd patterns are based on category-level data, not real-time crowd sensors
- When data is unavailable, say so. Never fabricate. Never say "I checked" when you have not.

WHEN YOU DO NOT KNOW:
- "I don't have current data on that — let me search." → use web search tool
- "That's outside what I can verify right now. I'd recommend checking [specific source]."
- Never invent venue names, addresses, or prices.

LANGUAGE:
- English only for the app interface
- Notification emails to contacts can be translated to their preferred language

ENERGY LOGIC HARD RULES:
- Day 1 of international travel with timezone delta >= 6h: max 2 activities, lighter intensity (unless user overrides)
- Day 2 of international travel with timezone delta >= 6h: max 3 activities (unless user overrides)
- Insert mandatory midday rest block if children under 10 in group (13:00-14:00, low-intensity venue or café)
- Maximum continuous activity block: 2.5 hours (then 30min break or meal)
- Lunch: between 12:00-14:00. Dinner: 18:00-20:00.

OUTPUT FORMAT:
- For itinerary generation, return structured JSON when the agent tool requires it
- For chat responses, return plain conversational text
- Never wrap chat responses in JSON or code blocks unless the user asks for code
```

---

# PART 6 — KEY ALGORITHMS

## 6.1 Route optimisation algorithm

Implement in `agent/tools/optimise_route.py`. This is the core of itinerary generation. **Follow these steps in exactly this order.**

```python
def optimise_route(venues, date, start_time, pace, group_profile, accommodation_coords):
    """
    venues: list of venue documents (from Google Places + enrichment merge)
    date: ISO date string
    start_time: HH:MM (when the group can begin the day)
    pace: 'relaxed' | 'moderate' | 'packed'
    group_profile: aggregated profile of all participating members
    accommodation_coords: {lat, lng} — anchor point for the day
    """

    day_of_week = get_day_of_week(date)  # 'monday', 'tuesday', etc.

    # STEP 1 — Filter venues
    # Remove closed venues, dietary-incompatible, mobility-incompatible
    eligible = filter_venues(venues, day_of_week, group_profile)

    # STEP 2 — Geographic clustering (radius-based, anchored on accommodation)
    # Cluster venues within 1.5km of each other, max 3 clusters per day
    clusters = radius_cluster(eligible, radius_km=1.5, max_clusters=3, anchor=accommodation_coords)

    # STEP 3 — Order clusters by earliest opening time within each
    clusters = sorted(clusters, key=lambda c: min(
        time_str(v['opening_hours'][day_of_week]['open']) or '23:59' for v in c
    ))

    # STEP 4 — Sequence venues within each cluster by opening time
    for c in clusters:
        c['venues'] = sorted(c['venues'], key=lambda v: v['opening_hours'][day_of_week]['open'] or '23:59')

    # STEP 5 — Flatten to ordered list
    ordered = [v for c in clusters for v in c['venues']]

    # STEP 6 — Apply substantive energy logic
    ordered = apply_energy_logic(ordered, pace, group_profile, date)

    # STEP 7 — Assign arrival/departure times with transit
    current = parse_time(start_time)
    for i, venue in enumerate(ordered):
        open_t = parse_time(venue['opening_hours'][day_of_week]['open'])
        if current < open_t:
            current = open_t
            venue['reasoning'] = f"Start adjusted to venue opening ({open_t})."

        venue['arrival_time'] = format_time(current)
        venue['departure_time'] = format_time(add_minutes(current, venue['estimated_duration_minutes']))

        if i < len(ordered) - 1:
            transit = get_transit_time(
                venue['coordinates'], ordered[i+1]['coordinates'],
                to_unix(venue['departure_time']),
                group_size=group_profile['size']
            )
            venue['transit_to_next_minutes'] = transit['duration_minutes']
            venue['transit_mode'] = transit['mode']
            if transit.get('group_transport_note'):
                venue['group_transport_note'] = transit['group_transport_note']
            current = add_minutes(parse_time(venue['departure_time']), transit['duration_minutes'])

    # STEP 8 — Peak avoidance annotation
    for venue in ordered:
        peak = get_peak_window(venue, day_of_week)
        if peak and times_overlap(venue['arrival_time'], venue['departure_time'],
                                  peak['start_time'], peak['end_time']):
            venue['reasoning'] += f" Note: arrives during peak hours ({peak['start_time']}–{peak['end_time']}). " \
                                  f"Consider shifting earlier if possible."

    # STEP 9 — Dining placement
    # Insert lunch venue near midday geographic position
    # Insert dinner venue near end-of-day geographic position
    ordered = insert_dining(ordered, group_profile, day_of_week)

    return ordered
```

## 6.2 Substantive energy logic

Implement in `apply_energy_logic`. This is what makes the scheduling defensible.

```python
def calculate_venue_energy_cost(venue, weather_data):
    """Each venue gets a 1-10 energy cost score."""
    intensity_map = {'high': 3.0, 'medium': 2.0, 'low': 1.0}
    cost = intensity_map.get(venue['physical_intensity'], 2.0)

    # Duration modifier (every 30 min beyond first hour = +0.25)
    extra_30min_blocks = max(0, (venue['estimated_duration_minutes'] - 60) // 30)
    cost += extra_30min_blocks * 0.25

    # Heat exposure modifier
    if venue.get('outdoor', False) and weather_data.get('high_c', 0) > 28:
        cost += 0.5

    # Crowd peak modifier (visiting during peak = more tiring)
    # This is computed at scheduling time

    return round(cost, 2)

def apply_energy_logic(ordered_venues, pace, group_profile, date):
    """
    Apply daily energy budget, jet lag mitigation, group composition modifiers.
    Returns reordered venue list with mandatory rest blocks inserted.
    """

    # Daily energy budget by pace
    budget_map = {'relaxed': 15, 'moderate': 22, 'packed': 30}
    budget = budget_map[pace]

    # Group composition modifiers
    if any(m['age'] >= 65 for m in group_profile['members']):
        budget *= 0.8  # Elderly reduce budget 20%
    if any(m['age'] < 10 for m in group_profile['members']):
        budget *= 0.85  # Children reduce budget 15%

    # Jet lag modifier (unless overridden)
    if group_profile.get('jet_lag_active') and not group_profile.get('jet_lag_override'):
        day_num = get_day_number(date, group_profile['arrival_date'])
        if day_num == 1:
            budget *= 0.6
        elif day_num == 2:
            budget *= 0.8

    # Front-load: sort by energy cost descending
    # but preserve geographic ordering from cluster step
    # (do this within each geographic cluster, not globally)

    # Insert mandatory midday rest if children under 10
    if any(m['age'] < 10 for m in group_profile['members']):
        ordered_venues = insert_rest_block(ordered_venues, time="13:00", duration=60)

    # Track running energy expenditure during scheduling
    # If exceeds 70% of budget before 15:00, insert a 30min breather
    running_cost = 0
    for i, venue in enumerate(ordered_venues):
        running_cost += venue.get('energy_cost', 2.0)
        if running_cost > (budget * 0.7) and parse_time(venue['departure_time']) < parse_time('15:00'):
            insert_breather_after(ordered_venues, i, duration=30)
            venue['reasoning'] += " Built in a breather here — you'll have covered a lot of ground."
            break

    return ordered_venues
```

## 6.3 Disruption mitigation pipeline (the demo wow moment)

Implement in `agent/tools/apply_disruption.py`.

```python
def apply_disruption(itinerary_id, event_type, affected_day_numbers, current_location, description):
    """
    The 6-step pipeline shown in the demo. Must complete in under 8 seconds end-to-end.
    """

    # STEP 1: Pub/Sub event already fired upstream — this function handles the response
    log_disruption_event(itinerary_id, event_type, description)

    # STEP 2: Calculate available time window
    itinerary = db.itineraries.find_one({"itinerary_id": itinerary_id})
    trip = db.group_trips.find_one({"trip_id": itinerary['trip_id']})
    profiles = get_group_profiles(trip['members'])
    affected_day = next(d for d in itinerary['days'] if d['day_number'] in affected_day_numbers)
    available_minutes = calculate_window(affected_day, event_type)

    # STEP 3: Query MongoDB for compatible alternative venues near current location
    # Uses Google Places + enrichment in a single search_venues call
    dietary_union = aggregate_dietary(profiles)
    candidates = search_venues_nearby(
        coordinates=current_location,
        radius_km=3,
        date=affected_day['date'],
        dietary_restrictions=dietary_union,
        mobility_max=max_mobility(profiles),
        group_size=len(trip['members']),
        exclude_venue_ids=[s['venue_id'] for s in affected_day['shared_schedule']],
        limit=15
    )

    # STEP 4: Google Maps Distance Matrix — filter to reachable in time window
    candidates_reachable = []
    for v in candidates:
        transit = get_transit_time(current_location, v['coordinates'],
                                   to_unix_now(), group_size=len(trip['members']))
        # Must fit: transit + venue_duration + buffer < available_window
        if transit['duration_minutes'] + v['estimated_duration_minutes'] + 30 < available_minutes:
            v['transit_minutes_from_disruption'] = transit['duration_minutes']
            v['group_transport_note'] = transit.get('group_transport_note')
            candidates_reachable.append(v)

    # STEP 5: Rank by fit — Vertex AI scores each based on group profile match
    ranked = vertex_ai_rank_alternatives(candidates_reachable, profiles, available_minutes)

    # STEP 6: Return exactly 3 alternatives labelled budget/recommended/premium
    top_3 = label_three_options(ranked[:3])

    # STEP 7 (post-selection, separate call): when user picks one
    # - Update itinerary with new schedule for affected day
    # - Save to MongoDB
    # - Write Firebase update to broadcast to all members
    # - Call notify_contacts with disruption context

    return {
        "alternatives": top_3,
        "available_window_minutes": available_minutes,
        "notification_context": {
            "event_description": description,
            "changes_summary": "Day rebuilt with alternatives near current location."
        }
    }
```

## 6.4 Flight risk scoring formula

```
Dimension 1 — On-time performance (35%)
  if route in flight_performance: score = on_time_pct × 100
  else: score = amadeus_delay_prediction × 100
  fallback: 75

Dimension 2 — Airline reliability (25%)
  lookup airline_iata in airline_ratings collection
  score = (skytrax_rating / 5) × 100
  fallback (airline not in lookup): 60

Dimension 3 — Time-of-day reliability (20%)
  slot from departure_datetime.hour:
    05-08 → early_morning, 08-12 → morning,
    12-17 → afternoon, 17-23 → evening
  if route in flight_performance: score = departure_time_reliability[slot]
  fallback: early_morning=88, morning=82, afternoon=70, evening=65

Dimension 4 — Seasonal adjustment (10%)
  if route in flight_performance:
    multiplier = seasonal_risk[departure_month].risk_multiplier
    score = min(100, (1 / multiplier) × 100)
  fallback multiplier: 1.0 → score 100

Dimension 5 — Connection adequacy (10%)
  direct flight: 100
  1 stop >90min: 80
  1 stop 60-90min: 60
  1 stop <60min: 30

OVERALL = (D1×0.35) + (D2×0.25) + (D3×0.20) + (D4×0.10) + (D5×0.10)

TIER:
  75-100: Low risk (green)
  50-74: Moderate (amber)
  0-49: High risk (red)
```

## 6.5 Settlement algorithm (minimum transactions)

Implement in `api/routes/expenses.py`.

```python
def calculate_settlement(trip_id):
    """
    Returns minimum-transaction settlement plan.
    Uses greedy matching of largest creditor to largest debtor.
    """
    expenses = list(db.expenses.find({"trip_id": trip_id}))

    # Calculate net balance per member
    balances = {}  # user_id → net (positive = owed money, negative = owes)
    for exp in expenses:
        # The logger paid the full amount
        balances[exp['logged_by_user_id']] = balances.get(exp['logged_by_user_id'], 0) + exp['amount_usd']
        # Each participant owes their share
        if exp['split_type'] == 'equal':
            share = exp['amount_usd'] / len(exp['participants'])
            for uid in exp['participants']:
                balances[uid] = balances.get(uid, 0) - share
        elif exp['split_type'] == 'custom':
            for split in exp['custom_splits']:
                balances[split['user_id']] = balances.get(split['user_id'], 0) - split['amount_usd']

    # Round to 2 decimals
    balances = {k: round(v, 2) for k, v in balances.items()}

    # Separate creditors (positive) and debtors (negative)
    creditors = sorted([(uid, bal) for uid, bal in balances.items() if bal > 0],
                       key=lambda x: -x[1])
    debtors = sorted([(uid, -bal) for uid, bal in balances.items() if bal < 0],
                     key=lambda x: -x[1])

    # Greedy matching
    transactions = []
    while creditors and debtors:
        c_id, c_amt = creditors[0]
        d_id, d_amt = debtors[0]
        transfer = min(c_amt, d_amt)

        transactions.append({"from": d_id, "to": c_id, "amount_usd": round(transfer, 2)})

        new_c = round(c_amt - transfer, 2)
        new_d = round(d_amt - transfer, 2)

        creditors.pop(0)
        debtors.pop(0)
        if new_c > 0.01:
            creditors.insert(0, (c_id, new_c))
        if new_d > 0.01:
            debtors.insert(0, (d_id, new_d))

    return transactions
```

---

# PART 7 — DATA SCHEMAS

## 7.1 `traveller_profiles`

```json
{
  "user_id": "string (unique)",
  "created_at": "ISODate",
  "name": "string",
  "age": "number",
  "nationality": "string (ISO 3166 alpha-3)",
  "passport_country": "string (ISO 3166 alpha-3)",
  "home_currency": "string (ISO 4217)",
  "home_timezone": "string (IANA)",
  "home_city_iata": "string",
  "languages_spoken": ["string"],
  "dietary": {
    "restrictions": ["halal | kosher | vegan | vegetarian | pescatarian | jain | no_pork | no_beef | no_alcohol | none"],
    "allergies": [{"item": "string", "severity": "preference | intolerance | anaphylactic"}],
    "strictness": "flexible | strict | certified_only"
  },
  "mobility": "full | limited | wheelchair",
  "physical_fitness": "low | average | high",
  "observance_blocks": [{
    "label": "string",
    "time": "HH:MM",
    "duration_minutes": "number",
    "frequency": "daily | weekly | once",
    "facility_type": "mosque | church | temple | synagogue | quiet_space | any | none"
  }],
  "preferences": {
    "pace": "relaxed | moderate | packed",
    "wake_time": "HH:MM",
    "interests": ["string"],
    "crowd_tolerance": "avoid | tolerate | unbothered"
  },
  "budget_private": {
    "total_amount": "number",
    "currency": "string",
    "is_per_person": true
  },
  "travel_dna": {
    "primary_style": "string",
    "energy_level": "string",
    "last_updated": "ISODate"
  }
}
```

## 7.2 `group_trips`

```json
{
  "trip_id": "string (uuid)",
  "created_at": "ISODate",
  "invite_token": "string (uuid, expires at departure_date)",
  "group_type": "friends | family | office",
  "trip_mode": "international | domestic",
  "status": "planning | confirmed | active | completed",
  "special_occasion": "string | null",
  "destination_city": "string",
  "destination_country": "string",
  "destination_iata": "string",
  "members": [{
    "user_id": "string",
    "name": "string",
    "role": "organiser | co_leader | member",
    "origin_city_iata": "string",
    "arrival_datetime": "ISODate",
    "joined_at": "ISODate",
    "profile_complete": "boolean",
    "shares_compliance_with_admins": true
  }],
  "contacts": [{
    "name": "string",
    "relationship": "string",
    "email": "string",
    "detail_level": "full | summary | updates_only",
    "language": "string (ISO 639)"
  }],
  "office_details": {
    "company_name": "string | null",
    "cost_centre": "string | null"
  },
  "shared_budget_estimate_usd": "number",
  "all_members_budget_ok": "boolean",
  "jet_lag_override": false
}
```

## 7.3 `itineraries`

```json
{
  "itinerary_id": "string",
  "trip_id": "string",
  "created_at": "ISODate",
  "updated_at": "ISODate",
  "status": "draft | confirmed | active | completed",
  "accommodation": {
    "name": "string",
    "address": "string",
    "coordinates": {"lat": "number", "lng": "number"},
    "check_in": "ISODate",
    "check_out": "ISODate",
    "price_per_night_usd": "number (estimate)",
    "google_place_id": "string",
    "booking_url": "string (verified domain)",
    "option_tier": "budget | recommended | premium"
  },
  "days": [{
    "day_number": "number",
    "date": "ISODate",
    "flock_mode_active": "boolean",
    "flock_mode_start_time": "HH:MM | null",
    "flock_mode_end_time": "HH:MM | null (set when organiser ends)",
    "flocks": [{
      "flock_id": "string",
      "flock_name": "string",
      "flock_leader_user_id": "string",
      "member_ids": ["string"],
      "schedule": ["...schedule items..."],
      "reconvene_time": "HH:MM",
      "reconvene_location": "string",
      "reconvene_coordinates": {"lat": "number", "lng": "number"}
    }],
    "shared_schedule": [{
      "order": "number",
      "venue_id": "string (Google place_id)",
      "venue_name": "string",
      "category": "string",
      "coordinates": {"lat": "number", "lng": "number"},
      "arrival_time": "HH:MM",
      "departure_time": "HH:MM",
      "transit_to_next_minutes": "number | null",
      "transit_mode": "string | null",
      "group_transport_note": "string | null",
      "reasoning": "string (required, one line)",
      "customs_note": "string | null",
      "booking_required": "boolean",
      "booking_status": "not_needed | needed | booked | confirmed",
      "energy_cost": "number"
    }],
    "weather": {
      "high_c": "number",
      "low_c": "number",
      "precipitation_mm": "number",
      "condition": "string"
    },
    "day_budget_used_usd": "number",
    "flight_note": "string | null"
  }],
  "flights": [{
    "flight_number": "string",
    "airline_iata": "string",
    "origin_iata": "string",
    "destination_iata": "string",
    "departure_datetime": "ISODate",
    "arrival_datetime": "ISODate",
    "member_ids": ["string"],
    "risk_score": "number",
    "risk_tier": "low | moderate | high",
    "option_tier": "budget | recommended | premium",
    "live_status": "scheduled | active | delayed | landed | cancelled | unknown",
    "live_status_last_polled": "ISODate"
  }],
  "disruption_log": [{
    "timestamp": "ISODate",
    "event_type": "string",
    "description": "string",
    "affected_day_numbers": ["number"],
    "resolution": "string"
  }],
  "share_url_token": "string"
}
```

## 7.4 `chat_threads` (Firebase, not MongoDB — for live sync)

```
/trips/{trip_id}/threads/main/{message_id}/{author_id, text, timestamp, role}
/trips/{trip_id}/threads/flocks/{flock_id}/{message_id}/{author_id, text, timestamp}
/trips/{trip_id}/state/{itinerary_updated_at, last_disruption_at}
```

## 7.5 `expenses`

```json
{
  "expense_id": "string (uuid)",
  "trip_id": "string",
  "logged_by_user_id": "string",
  "logged_at": "ISODate",
  "amount": "number",
  "currency": "string (ISO 4217)",
  "amount_usd": "number (converted at log time using ExchangeRate-API)",
  "exchange_rate_used": "number",
  "category": "food | transport | accommodation | activity | shopping | other",
  "description": "string",
  "flock_id": "string | null",
  "logging_mode": "everyone | specific_people | my_flock | just_me",
  "participants": ["string (user_ids)"],
  "split_type": "equal | custom",
  "custom_splits": [{"user_id": "string", "amount_usd": "number"}],
  "day_number": "number | null"
}
```

## 7.6 `airline_ratings`, `visa_requirements`, `venue_enrichment`

See Part 0.5 for full structures and seed instructions.

---

# PART 8 — TOOL CONTRACTS

All tools return `{"error": {"code": "...", "message": "..."}}` on failure. Bounce's system prompt handles user-facing error messaging based on error code.

## Tool 1 — `get_traveller_profile`

```
Input: {"user_id": "string"}
Output: {"profile": <traveller_profiles document>}
Errors: USER_NOT_FOUND
```

## Tool 2 — `search_venues`

```
Input: {
  "city": "string",
  "destination_country": "string",
  "date": "YYYY-MM-DD",
  "categories": ["string (optional)"],
  "group_dietary_restrictions": ["string"],
  "group_interests": ["string"],
  "mobility_max": "full | limited | wheelchair",
  "group_size": "number",
  "limit": "number (default 20)"
}
Output: {"venues": [<merged Places + enrichment>], "total_found": number}
```

Implementation:
1. Call Google Places API `nearbysearch` with `type=tourist_attraction` and other types based on `categories`
2. For each result, look up enrichment by Google type → category_pattern in `venue_enrichment`
3. Merge: Places provides name, coordinates, opening_hours, rating, photos; enrichment provides physical_intensity, peak_hours, customs, child_friendly, etc.
4. If no enrichment match, use category-fallback defaults (medium intensity, 90min duration, no specific customs)
5. Filter out venues incompatible with dietary restrictions and mobility level
6. Sort by Google rating descending

## Tool 3 — `search_accommodation`

```
Input: {"city", "check_in", "check_out", "group_size", "budget_tier"}
Output: {"options": [3 accommodation options labelled budget/recommended/premium]}
```

Implementation: Google Places API hotel search → for each result, Gemini-generated price estimate based on category (budget hotel ~$80/night, mid-range ~$180, premium ~$350+ adjusted per city). Display price as estimate with note: "Final price confirmed at booking site."

## Tool 4 — `get_transit_time`

```
Input: {origin coords, dest coords, departure_unix_timestamp, mode, group_size}
Output: {duration_minutes, distance_km, mode, group_transport_note}
```

`group_transport_note` populated when `group_size > 6`: e.g. "10 people: chartered minibus (~$80) or 3 taxis (~$95 total)."

## Tool 5 — `optimise_route`

See Part 6.1.

## Tool 6 — `get_weather`

```
Input: {"lat", "lng", "date"}
Output: {"high_c", "low_c", "precipitation_mm", "condition"}
```

Implementation: Open-Meteo `/forecast` endpoint, no API key needed.

## Tool 7 — `search_flights`

```
Input: {origin, destination, departure_date, return_date, adults, max_budget_usd, preferred_airlines, max_duration_hours}
Output: {"options": [3 flights labelled budget/recommended/premium]}
```

Uses Amadeus production. Returns top 3 by configurable criteria. Each option includes flight_number, price, duration, stops, departure/arrival times.

## Tool 8 — `score_flight_risk`

See Part 6.4 for formula. Reads from `airline_ratings` and `flight_performance` collections.

## Tool 9 — `get_multi_modal_transport`

```
Input: {origin, destination, date, group_size}
Output: {"options": [up to 3 transport modes]}
```

Rome2Rio search → consolidate to 3 best options by time/cost balance.

## Tool 10 — `apply_disruption`

See Part 6.3.

## Tool 11 — `save_itinerary`

```
Input: {"itinerary": <full document>}
Side effect: Write to Firebase /trips/{trip_id}/state/itinerary_updated_at = NOW
Output: {"itinerary_id", "success", "updated_at"}
```

## Tool 12 — `get_visa_requirements`

```
Input: {"passport_iso", "destination_iso"}
Output: <visa_requirements document>
```

Implementation:
1. Check `visa_requirements` MongoDB collection — if found and `last_verified` within 90 days, return
2. Otherwise call Gemini web search with structured prompt (see Part 0)
3. Parse JSON response from Gemini
4. Cache result to MongoDB with 30-day TTL
5. Always include "verify with embassy" note

## Tool 13 — `notify_contacts`

```
Input: {"trip_id", "trigger_event", "notification_context"}
Output: {"sent": number, "failed": number}
```

Uses SendGrid. For each contact: detail_level determines message template, language determines Cloud Translation API call (only feature using translation in the build).

## Tool 14 — `poll_flight_status`

```
Input: {"flight_number", "departure_date"}
Output: {"status", "scheduled_departure", "actual_departure", "scheduled_arrival", "actual_arrival", "delay_minutes"}
```

Implementation:
1. Check MongoDB cache — if polled within 30 minutes, return cached
2. Otherwise call AeroDataBox `flights/number/{flight_number}/{date}` endpoint
3. Cache result with timestamp
4. If status changed from previous poll, publish to Pub/Sub topic `flight-status-change`
5. Pub/Sub subscriber fires Firebase update to affected members

---

# PART 9 — DISRUPTION TRIGGER (Demo Button)

The demo includes a manually-triggered disruption to showcase the AI mitigation.

```
POST /trigger-disruption
{
  "itinerary_id": "string",
  "event_type": "flight_cancellation | venue_closure | flight_delay",
  "description": "string",
  "affected_day_numbers": [number],
  "current_location": {"lat", "lng"}
}
```

Response: alternatives + map pins. UI shows: disruption banner, 3 alternative cards on map, admin can tap to accept. Firebase update broadcasts to all members.

---

# PART 10 — REMINDER SYSTEM

Cloud Scheduler triggers. Five reminders critical for the demo:

| Reminder | Trigger | Recipient | Method |
|---|---|---|---|
| Visa application window | T-21 days, per nationality | Individual member (private) | Email |
| Check-in open | T-24h | All members | Firebase push |
| Leave home alert | Calculated per member origin | Individual | Firebase push |
| FlockMode reconvene | T-30min before reconvene_time | Flock members | Firebase push |
| Budget 80% threshold | When expenses reach 80% | Organiser + co-leaders only | Firebase push |

Cloud Scheduler job:
```bash
gcloud scheduler jobs create http bounce-reminder-dispatcher \
  --schedule="*/15 * * * *" \
  --uri="https://bounce-api-XXX.run.app/internal/dispatch-reminders" \
  --http-method=POST
```

Reminder dispatcher endpoint scans active trips, identifies due reminders, fires them, marks as sent in MongoDB to prevent duplicates.

---

# PART 11 — SECURITY LAYER

## 11.1 PII detection (no Cloud DLP)

```python
import re
PII_PATTERNS = {
    'passport_number': r'[A-Z]{1,2}\d{6,9}',
    'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
    'ssn_us': r'\b\d{3}-\d{2}-\d{4}\b',
    'national_id_id': r'\b\d{12,16}\b',
}

def check_for_pii(message):
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, message):
            return True, pii_type
    return False, None
```

When PII detected, Bounce responds (system prompt rule): "Heads up — I don't need or store that. Let's continue without it."

## 11.2 Booking link validation

```python
APPROVED_DOMAINS = [
    'booking.com', 'expedia.com', 'hotels.com', 'agoda.com',
    'airbnb.com', 'google.com', 'skyscanner.com', 'kayak.com',
    'ana.co.jp', 'jal.com', 'united.com', 'delta.com', 'aa.com',
    'singaporeair.com', 'garuda-indonesia.com', 'qantas.com',
    'lufthansa.com', 'airfrance.com', 'klm.com', 'britishairways.com'
]

def validate_booking_link(url):
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.replace('www.', '')
    return any(domain.endswith(approved) for approved in APPROVED_DOMAINS)
```

## 11.3 Rate limiting

Per user: max 5 chat messages per 10 seconds. Implement in `api/routes/chat.py`:

```python
from collections import defaultdict
from time import time
rate_buckets = defaultdict(list)

def check_rate(user_id):
    now = time()
    rate_buckets[user_id] = [t for t in rate_buckets[user_id] if now - t < 10]
    if len(rate_buckets[user_id]) >= 5:
        return False
    rate_buckets[user_id].append(now)
    return True
```

---

# PART 12 — JUDGE TEST MODE

Endpoints judges use to test all features without setting up from scratch.

```
POST /judge/reset
  Clears the demo trip and reseeds The Reunion fresh

POST /judge/seed-demo-trip
  Creates The Reunion trip with all 10 members pre-loaded

POST /judge/trigger-disruption
  Fires the demo disruption (Day 3 flight UA837 cancelled)

GET /judge/instructions
  Returns plain-text guide for what features to test
```

The judge test mode is documented prominently in the README and Devpost description. A judge can:
1. Click the demo trip link → see The Reunion fully populated
2. Click the disruption button → see mitigation in action
3. Type "let's go to Lisbon instead" → see full re-plan capability
4. Create their own trip from scratch with any destination → see judge test mode

---

# PART 13 — ERROR AND LOADING STATES

System prompt includes user-facing messages for each error code. Examples:

| Error | Bounce response |
|---|---|
| Amadeus unavailable | "Couldn't pull live flights right now — give it a moment, or tell me which airline you prefer and I'll work with what I have." |
| AeroDataBox quota exceeded | "Live status isn't available for this flight right now — check the airline's app for the latest." |
| Places API empty | "I didn't find venues matching that — want to widen the criteria or try a different category?" |
| Visa data unavailable | "I couldn't verify visa requirements right now — please check the [country] embassy website to confirm." |
| Disruption mitigation no candidates | "No alternative venues fit your window — would you like to head back to the hotel and rest instead?" |

Loading states for long operations (itinerary generation can take 20s+):

```
[Bounce] Pulling venues for Tokyo...
[Bounce] Checking everyone's dietary needs...
[Bounce] Building Day 1 around your arrival times...
[Bounce] Optimising routes — nearly there.
```

Implement as streamed intermediate messages from the agent during multi-step tool calls.

---

# PART 14 — DEMO SCRIPT (3 minutes)

| Time | Content |
|---|---|
| 0:00-0:15 | Bounce logo. "10 friends. 5 cities. 1 reunion. Planning it used to take weeks." Cut to chat. |
| 0:15-0:50 | Alex types entry message. Bounce extracts everything. One follow-up question. Profile gaps filled. |
| 0:50-1:15 | Itinerary loads with Maps. Highlight: flight-aware buffer ("LA group lands at 14:30 — first shared activity starts after group ready time + 90min"). Flight risk card showing NH106 (Low, 84) vs alternative (Moderate). |
| 1:15-1:50 | Jump to Day 5. Bounce suggests FlockMode. Organiser creates 3 Flocks (Explorers, Foodies, Shoppers — see Part 1.5). Each Flock gets mini-map. Reconvene reminder at 18:00 before 18:30 meetup. |
| 1:50-2:30 | Click disruption trigger. **Day 7 venue closure** — afternoon venue showing as closed for private event. Bounce returns 3 alternatives with map pins, transit times, reasoning. Admin picks Mori Art Museum. Firebase pushes to all members instantly. Show notification email **Rania's mother** receives (Rania needed a visa — closes the compliance feature loop). |
| 2:30-3:00 | Quick flash: split bill — expense logged via 4-mode UI → running balance. Settlement card showing minimum transactions. Travel DNA cards. 3 next destination suggestions. Bounce logo. |

The Devpost description fills in: per-member visa compliance (screenshot of Priya's private notification), live flight status tracking, FlockMode private chat threads, multi-modal transport options, judge test mode link.

---

# PART 15 — TESTING CHECKLIST (Day 15)

Must pass all before submission:

**Core loop:**
- [ ] Conversational entry extracts all key details from one natural-language message
- [ ] Profile gap-fill shows only genuine blanks
- [ ] Itinerary, accommodation, map load together in one output
- [ ] Every scheduling decision shows one-line reasoning
- [ ] Dietary restrictions respected across the entire itinerary
- [ ] Energy logic visibly reduces Day 1 intensity for jet lag (timezone delta >= 6h)

**Flights:**
- [ ] Amadeus production returns real flight numbers (UA837, NH106, etc.)
- [ ] Each flight has a risk score + tier
- [ ] Exactly 3 options per origin city
- [ ] Member selection works for all 5 origin cities in The Reunion demo

**Maps:**
- [ ] Google Maps JS renders in-app
- [ ] All venues pinned with correct coordinates
- [ ] "Open in Google Maps" works for live navigation
- [ ] Recommended route drawn between stops

**Group:**
- [ ] Invite link generates and works for new members
- [ ] Member suggestion logged (not applied)
- [ ] Co-leader can apply changes
- [ ] Firebase pushes change to all members in real-time
- [ ] Per-member nationality visa info shown only to that member (not group)

**FlockMode:**
- [ ] Organiser creates Flocks
- [ ] Each Flock has its own leader, schedule, chat thread
- [ ] Reconvene reminder fires 30min before
- [ ] Expenses can be logged per Flock or to specific members

**Disruption:**
- [ ] Trigger button fires the full pipeline
- [ ] 3 alternatives returned with reasoning
- [ ] Selecting alternative updates itinerary
- [ ] Firebase pushes to all members
- [ ] Notification email sent to contacts

**Flight status:**
- [ ] AeroDataBox returns real status for a known flight
- [ ] Cache works (no duplicate calls within 30min)
- [ ] Pub/Sub fires on status change
- [ ] Firebase notification reaches affected members

**Split bill:**
- [ ] All 4 logging modes work (everyone / specific / my Flock / just me)
- [ ] Currency conversion uses live rates
- [ ] Settlement calculation produces minimum transactions
- [ ] Cross-Flock expense logging works

**Judge test mode:**
- [ ] `/judge/reset` clears state and reseeds
- [ ] Typing "Lisbon" instead of "Tokyo" generates a real itinerary
- [ ] Typing "let's switch to Kyoto" mid-plan triggers confirmation and re-plan
- [ ] Any group size 2-20 works
- [ ] Domestic mode (SF → LA) skips flight scoring and visa

**Performance:**
- [ ] Streaming responses visible during long operations
- [ ] No Cloud Run cold starts (min instance set)
- [ ] Itinerary generation under 30 seconds end-to-end
- [ ] Disruption mitigation under 8 seconds end-to-end

---

# PART 16 — DEPLOYMENT (Day 16)

```bash
# Build container
docker build -t gcr.io/bounce-hackathon-2026/bounce-api:v1 .

# Push
docker push gcr.io/bounce-hackathon-2026/bounce-api:v1

# Deploy to Cloud Run with min instance
gcloud run deploy bounce-api \
  --image=gcr.io/bounce-hackathon-2026/bounce-api:v1 \
  --region=asia-southeast1 \
  --min-instances=1 \
  --max-instances=10 \
  --memory=1Gi \
  --cpu=1 \
  --allow-unauthenticated \
  --set-env-vars-from-file=.env.prod

# Verify
curl https://bounce-api-XXX.run.app/health
# Expected: {"status": "ok", "version": "v1"}
```

Frontend deployment: Firebase Hosting (free, fast).

```bash
firebase deploy --only hosting
```

URL structure:
- App: `https://bounce-hackathon-2026.web.app`
- API: `https://bounce-api-XXX.run.app`
- Demo trip direct link: `https://bounce-hackathon-2026.web.app/trip/reunion-demo`

---

# PART 17 — DEVPOST SUBMISSION CHECKLIST

- [ ] Project name: Bounce
- [ ] Tagline: "The only AI travel agent built for groups"
- [ ] Hosted URL: `https://bounce-hackathon-2026.web.app`
- [ ] GitHub repo public with MIT license at top of README
- [ ] Demo video 3 minutes uploaded
- [ ] Description covers: problem, solution, all 6 differentiating features, MongoDB MCP integration depth, judge test instructions
- [ ] Tech stack listed: Vertex AI + Gemini, Agent Builder, MongoDB MCP, Firebase, Cloud Pub/Sub, Cloud Scheduler, Amadeus, AeroDataBox, Rome2Rio, Google Maps
- [ ] Screenshots: chat entry, itinerary view, Maps, FlockMode, disruption mitigation, split bill, judge test mode
- [ ] Judge instructions: "Click here for the demo trip → click 'Trigger Disruption' to see mitigation → type 'let's go to Paris instead' to see full re-plan capability"

---

*Bounce — Technical PRD v2.0 — Confidential, internal use only*
*Built for the Google Cloud Rapid Agent Hackathon 2026*
