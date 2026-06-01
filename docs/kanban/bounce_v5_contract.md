# Bounce v5 Repository Contract and Fixed Kanban

Source of truth: `docs/prd/bounce_prd_v5.md` and `docs/design/bounce_design_v5.md`, committed with Fariz's confirmation on 2026-05-31.

This contract records the BV5-001 decision and controls all v5 implementation work. It does not rewrite the older BNC v2/v3 Kanban history; those files remain historical/project-status references.

---

## BV5-001 decision — execution mode

Chosen mode: **Option C — two-track path**.

1. Build a clean v5 **L1 single-file prototype** first.
2. Keep the existing deployed v3 app untouched until Fariz explicitly approves a deployment/merge path.
3. Treat `docs/prd/bounce_prd_v5.md` and `docs/design/bounce_design_v5.md` as the current v5 source of truth.
4. Treat v2/v3 source docs and old BNC Kanban cards as historical references unless a specific legacy behavior is intentionally carried forward.
5. Do not start v5 L2 backend reconciliation or production deployment until the L1 prototype direction is proven and Fariz approves the next step.

Reason: v5 conflicts with the current repo baseline in a fundamental way. The current app is a deployed multi-file v2/v3-style implementation, while PRD v5 asks for a single-file L1 prototype with inline assets, deterministic demo data, no localStorage/sessionStorage, and no fetch calls for prototype state.

---

## Scope-control rules

1. This v5 list is fixed. Do not silently add BV5 cards.
2. Track progress by status changes only: `TODO`, `IN_PROGRESS`, `BLOCKED`, `DONE`, or `CUT`.
3. If implementation reveals missing work, stop and ask Fariz before expanding the list.
4. Preserve Fariz's 12 commandments during execution: read before writing, keep changes surgical, test intent, surface conflicts, and checkpoint with commit/push between coherent tasks.
5. Do not reopen `CUT` scope unless Fariz explicitly approves it.
6. Do not build FlockMode photo sharing, multi-city trips, removed routes, Travel DNA, dark mode, or native apps under this list.
7. Usage-limit preflight: before starting each implementation card, estimate whether the 5-hour/weekly Hermes limit is enough; warn Fariz before starting if it may not be.

---

## Current repo gap snapshot

- Existing README and older Kanban files previously centered v2.1/v3 work; v5 now supersedes those docs for new implementation.
- Existing frontend files are split across `frontend/index.html`, `frontend/app.js`, `frontend/style.css`, assets, manifest, and service worker.
- Existing `frontend/style.css` starts with old Yale/lemon tokens, not v5 purple/lime/orange tokens.
- Existing frontend uses external Google Maps behavior and static asset files; v5 L1 requires inline/base64 assets and no external requests, except the PRD's explicit Babel CDN note if JSX is used.
- Existing Cloud Run deployment remains valuable as a stable demo baseline, but it should not be overwritten by v5 until BV5-016 is approved.

---

## Fixed v5 Kanban

### TODO

### IN_PROGRESS

- None.

### BLOCKED

- None.

### DONE

- **BV5-000 — Read-only v5 analysis and fixed Kanban draft**
  - Completed in chat on 2026-05-31 before committing canonical v5 docs.

- **BV5-001 — Decide v5 execution mode and repository contract**
  - Completed decision: Option C — two-track path.
  - Acceptance met:
    - Execution mode is recorded in this document.
    - The repo now has canonical v5 PRD/design docs.
    - Older BNC v2/v3 cards were not silently rewritten.

- **BV5-002 — Add v5 source-of-truth docs to repo**
  - Completed with Fariz confirmation on 2026-05-31.
  - Files:
    - `docs/prd/bounce_prd_v5.md`
    - `docs/design/bounce_design_v5.md`
  - Acceptance met:
    - v5 docs are present in repo with supplied content.
    - README points to v5 as current source of truth.
    - v2/v3 docs remain available as historical references.

- **BV5-003 — Create the v5 L1 prototype shell**
  - Completed on 2026-05-31.
  - Files:
    - `frontend/bounce_v5_prototype.html`
    - `tests/frontend/test_bv5_003_prototype_shell.py`
  - Acceptance met:
    - Prototype loads as one self-contained HTML file.
    - No build step is required.
    - No localStorage/sessionStorage or network calls are used for L1 state.
    - Demo data is declared as `const` objects near the top of the inline script.
    - Existing deployed v3 app files were not modified.

- **BV5-004 — Apply v5 visual identity and design tokens**
  - Completed on 2026-05-31.
  - Files:
    - `frontend/bounce_v5_prototype.html`
    - `tests/frontend/test_bv5_004_visual_identity.py`
  - Acceptance met:
    - `:root` includes v5 design-system tokens for brand, accents, semantic colors, categories, typography, spacing, radius, shadows, and z-index.
    - Component CSS uses variables instead of raw component-level hex values.
    - Bounce logomark fallback, Bounce avatar, FAB alert state, cards, tags, and button variants exist in the prototype shell.

- **BV5-005 — Implement v5 app shell, navigation, and mobile drawer**
  - Completed on 2026-05-31.
  - Files:
    - `frontend/bounce_v5_prototype.html`
    - `tests/frontend/test_bv5_005_app_shell_navigation.py`
  - Acceptance met:
    - Global nav shows Home, Plan a new trip, and Join a trip.
    - Profile is accessed through the user pill.
    - Trip-scoped nav adapts for planning, active, and past trips.
    - `← All trips` exits trip context and closes the drawer.
    - Trip context card uses selected trip name/city/state dynamically.
    - Mobile top bar, drawer, and backdrop are stateful; nav/backdrop clicks close the drawer under the v5 900px breakpoint.

- **BV5-006 — Implement v5 demo data and phase dispatcher**
  - Completed on 2026-05-31.
  - Files:
    - `frontend/bounce_v5_prototype.html`
    - `tests/frontend/test_bv5_006_demo_data_dispatcher.py`
  - Acceptance met:
    - Home data now contains Lisbon planning, Tokyo active, and 3 past trips from PRD v5.
    - `trip.state` drives default phase selection through `phaseForTrip(trip)`.
    - Tokyo active uses `activeDay: 3` and `totalDays: 7`.
    - Hash-based prototype routing uses the v5 L1 `screen=X&phase=Y&user=Z` shape with trip id support.
    - Wrap data is keyed by `WRAP_DATA[trip.id]` and uses destination local currency only.

- **BV5-007 — Build Home and Entry Conversation screens**
  - Completed on 2026-05-31.
  - Files:
    - `frontend/bounce_v5_prototype.html`
    - `tests/frontend/test_bv5_007_home_entry.py`
  - Acceptance met:
    - Home screen uses the v5 `home-plan-new` CTA, Upcoming/Active/Past sections, and TripCard component markers.
    - TripCard states include planning `In planning`, active `● Day X/Y`, past `⭐ rating`, days-to-go, cover area, trip metadata, and avatar stack.
    - Plan CTA copy matches v5: `Your trip starts here. Tell me what you've got in mind.`
    - Entry Conversation screen has textarea, Bounce mascot hero, trip-type chips, deterministic Bounce response, and no network/SSE calls in L1.

- **BV5-008 — Build Profile tabs with anchored save buttons**
  - Completed on 2026-06-01.
  - Files:
    - `frontend/bounce_v5_prototype.html`
    - `tests/frontend/test_bv5_008_profile_tabs.py`
  - Acceptance met:
    - Profile has tabs for About me, Food & diet, How I travel, Past trips, and Passport & visas.
    - Editable tabs have bottom-anchored `Save changes` buttons.
    - Past trips is read-only and has no save button.
    - Save action produces visible local demo feedback.

- **BV5-009 — Build Planning itinerary, budget, map, flights, and suggestions**
  - Completed on 2026-06-01.
  - Files:
    - `frontend/bounce_v5_prototype.html`
    - `tests/frontend/test_bv5_009_planning.py`
  - Acceptance met:
    - Itinerary layout has day rail, view toggles, activity cards, BudgetCard, and map placeholder/card.
    - Admin roles see 3-dot activity menus in planning; members get read-only/suggestion copy.
    - Budget editor has two inputs and bottom save behavior.
    - Flights show 3 options per origin group with risk labels.
    - Suggestions show 2 pending items and a lime nav badge positioned over the icon/label.

- **BV5-010 — Build Active Today, FlockMode, disruption, expenses, and alerts**
  - Completed on 2026-06-01.
  - Files:
    - `frontend/bounce_v5_prototype.html`
    - `tests/frontend/test_bv5_010_active_trip.py`
  - Acceptance met:
    - Today screen uses Tokyo Day 3 data and quick actions.
    - FlockMode switcher, active flock schedule, countdown, SVG map, and photo-sharing placeholder render.
    - Disruption modal shows 3 alternatives and uses `Lock this in & ping everyone →` / `Not now` copy.
    - Expenses include 4 split modes and 6 categories with visible local state updates.
    - Alerts have populated and empty states.

- **BV5-011 — Build Post-trip Wrap screens**
  - Completed on 2026-06-01.
  - Files:
    - `frontend/bounce_v5_prototype.html`
    - `tests/frontend/test_bv5_011_wrap_screens.py`
  - Acceptance met:
    - Each past trip renders unique total, per-person amount, category breakdown, settlements, and BounceSay insight.
    - Destination local currency is used only; no USD conversion is shown.
    - Travel DNA does not appear.

- **BV5-012 — Build Bounce assistant panel, FAB, and role labels**
  - Completed on 2026-06-01.
  - Files:
    - `frontend/bounce_v5_prototype.html`
    - `tests/frontend/test_bv5_012_bounce_assistant.py`
  - Acceptance met:
    - FAB matches v5 mascot/ring/pulse behavior and opens the assistant.
    - Chat panel has dialog ARIA, header, message stream, pill input, and close behavior.
    - Permission label changes for Organiser/Co-leader, Flock leader, and Member.
    - L1 responses are deterministic and do not fetch.

- **BV5-013 — Build draggable Judge / Demo Controls panel**
  - Completed on 2026-06-01.
  - Files:
    - `frontend/bounce_v5_prototype.html`
    - `tests/frontend/test_bv5_013_demo_controls.py`
  - Acceptance met:
    - Panel starts bottom-left with z-index 500 and can be dragged with pointer events.
    - Panel toggles open/collapsed with lime pill `⚡ Demo controls`.
    - Role selector, phase selector, Trigger disruption, and Reset demo controls work visibly.
    - Label is `⚡ Demo controls · drag me`.

- **BV5-014 — Add v5 prototype automated checks**
  - Completed on 2026-06-01.
  - Files:
    - `tests/frontend/test_bv5_014_automated_checks.py`
    - `tests/frontend/test_bv5_013_demo_controls.py`
  - Acceptance met:
    - Tests verify required v5 copy, routes/hash states, nav labels, CUT placeholders, and no removed routes.
    - Tests verify no localStorage/sessionStorage usage in the prototype.
    - Tests verify FlockMode photo sharing remains placeholder-only.
    - Tests verify the prototype contains no obvious external asset/script requests; no Babel CDN exception is used in the current L1 file.

- **BV5-015 — Local visual/responsive smoke pass**
  - Completed on 2026-06-01.
  - Files:
    - `docs/qa/bv5_015_visual_responsive_smoke.md`
    - `docs/qa/assets/bv5-015/desktop-1280-home.png`
    - `docs/qa/assets/bv5-015/tablet-1024-planning.png`
    - `docs/qa/assets/bv5-015/mobile-360-home.png`
    - `tests/frontend/test_bv5_015_visual_smoke.py`
  - Acceptance met:
    - 1280px+ desktop app shell/full layout smoke captured.
    - 1024px tablet planning itinerary/right-rail behavior smoke captured.
    - 360px mobile stacked layout captured; drawer open/close state verified in browser DOM smoke.
    - Browser console had no startup or representative-path errors.
    - Representative v5 demo path was exercised end to end.

- **BV5-016 — Decide and perform deployment path**
  - Completed on 2026-06-01.
  - Approved path: Option 2 — deploy the v5 prototype to a new Cloud Run service in the existing Google Cloud project.
  - Google Cloud project: `project-411e0419-48bd-4b5b-97f`.
  - Region: `asia-southeast1`.
  - Service: `bounce-v5-prototype`.
  - Public URL: `https://bounce-v5-prototype-4dynllwdeq-as.a.run.app`.
  - Latest ready revision: `bounce-v5-prototype-00012-wsk`.
  - Files:
    - `cloudrun/bounce-v5-prototype/Dockerfile`
    - `cloudrun/bounce-v5-prototype/app.py`
    - `cloudrun/bounce-v5-prototype/index.html`
    - `docs/qa/bv5_016_cloud_run_deployment.md`
    - `tests/infra/test_bv5_016_cloud_run_prototype.py`
  - Acceptance met:
    - Fariz-approved deployment target is recorded.
    - Hosted URL loads the v5 prototype with HTTP 200.
    - `/health` returns HTTP 200 with `status: ok` and `service: bounce-v5-prototype`.
    - Smoke evidence records exact URL, status codes, and revision/version identifier.

- **BV5-017 — Reconcile L2 backend contract to v5**
  - Completed on 2026-06-01.
  - Boundary: local/backend contract reconciliation only; no live `bounce-api` replacement and no Agent Builder/Firebase/MongoDB live provider claim.
  - Files:
    - `api/main.py`
    - `api/settings.py`
    - `docs/architecture/bounce_v5_l2_backend_contract.md`
    - `tests/api/test_bv5_017_l2_backend_contract.py`
  - Acceptance met:
    - `/health` can report a v5-shaped L2 status when `BOUNCE_API_MODE=v5` is enabled.
    - `/api/chat` SSE streaming contract is documented and explicitly deferred until Agent Builder streaming is configured/approved.
    - MongoDB collection names and Firebase RTDB paths match PRD v5 where L2 work is in scope.
    - Existing live `bounce-api` deployment remains untouched by this checkpoint.

## Approved v5 polish addendum

Source of approval: Fariz approved creating and working **BV5-A02** on 2026-06-01 after the V5 judge/demo polish audit.

Scope-control rules:

1. This addendum is fixed to the approved V5 polish sequence; do not silently add more BV5-A cards.
2. Keep changes limited to the separate V5 prototype service unless Fariz explicitly approves changing the main `bounce-api` app.
3. Use deterministic local L1 behavior for prototype polish; do not claim live backend join behavior.
4. Stop after one card when working under the 5-hour/weekly usage-limit boundary.

### TODO

- **BV5-A04 — Add disruption locked and pinged confirmation**
  - Source: V5 judge/demo polish audit on 2026-06-01.
  - Deliverable: after `Lock this in & ping everyone →`, show visible confirmation that the disruption alternative was locked and the group ping was drafted.
  - Acceptance: disruption modal close action leaves visible confirmation; no network/storage is introduced; existing active-trip tests remain green.

### IN_PROGRESS

- None.

### BLOCKED

- None.

### DONE

- **BV5-A02 — Fix global Join a trip nav**
  - Status: DONE.
  - Source: V5 judge/demo polish audit on 2026-06-01.
  - Files:
    - `frontend/bounce_v5_prototype.html`
    - `cloudrun/bounce-v5-prototype/index.html`
    - `tests/frontend/test_bv5_a02_join_trip.py`
  - Acceptance met:
    - Global `Join a trip` nav opens a deterministic V5 L1 Join screen.
    - Join screen includes invite-code entry and a visible invite-preview action.
    - The screen clearly states that the backend join flow stays deferred in L1.
    - Main `bounce-api` deployment remains untouched.

- **BV5-A03 — Make Plan-new-trip response reflect typed prompt**
  - Status: DONE.
  - Source: V5 judge/demo polish audit on 2026-06-01.
  - Files:
    - `frontend/bounce_v5_prototype.html`
    - `cloudrun/bounce-v5-prototype/index.html`
    - `tests/frontend/test_bv5_a03_prompt_destination.py`
  - Acceptance met:
    - Deterministic plan-entry response echoes obvious prompt destinations for Tokyo, Lisbon, and Seoul.
    - Unknown destinations still fall back to Lisbon demo copy.
    - No network/storage was introduced.
    - Main `bounce-api` deployment remains untouched.

### CUT — do not build without approval

- FlockMode photo sharing beyond the placeholder.
- Multi-city trip support beyond comments/placeholders.
- Travel DNA or post-trip personality read-back.
- Removed routes: `/compliance`, `/waiting`, `/predeparture`.
- Dark mode.
- Native mobile apps.
- Receipt scanning.
- AI packing list.
- AI-generated trip narrative.
- Multi-language UI.
- Cultural briefing screen per nationality.
- Multi-currency budget switcher.
- Suggestions-to-itinerary animation beyond toast/local visible MVP.
- Member join post-code flow beyond the v5 L1 Join screen unless approved.
- Backend rebuild beyond explicit v5 L2 cards.

---

## Current next card recommendation

Recommended next action: **BV5-A04 — Add disruption locked and pinged confirmation**.

Reason: BV5-A03 is implemented and verified. The next approved V5 polish addendum item is to leave visible confirmation after the disruption lock-and-ping action. Do not start it without Fariz approval and a usage-limit preflight.
