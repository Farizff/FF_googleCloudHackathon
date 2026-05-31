# Bounce v5 PRD + Design Analysis and Fixed Kanban

Source documents reviewed read-only on 2026-05-31:

- `bounce_prd_v5.md` supplied in chat/cache: Technical PRD v5.0.
- `bounce_design_v5.md` supplied in chat/cache: Design System v5.0.
- Existing repo docs used only for comparison:
  - `docs/prd/bounce_prd_v2.md`
  - `docs/design/bounce_design_v2.md`
  - `docs/design/bounce_design_v3.0.md`
  - `docs/kanban/bounce_fixed_kanban.md`
  - `docs/kanban/frontend_usability_kanban.md`

This document is an analysis/checkpoint artifact only. It does not replace the supplied v5 PRD/design files, and it does not implement product changes.

---

## Scope-control rules for the v5 Kanban

1. This v5 list is fixed once accepted by Fariz. Do not silently add cards.
2. Track progress by changing status on existing cards only: `TODO`, `IN_PROGRESS`, `BLOCKED`, `DONE`, or `CUT`.
3. If implementation reveals missing work, stop and ask Fariz before expanding this list.
4. Preserve Fariz's 12 commandments during execution: read before writing, keep changes surgical, test intent, surface conflicts, and checkpoint with commit/push between coherent tasks.
5. Do not reopen `CUT` scope unless Fariz explicitly approves it.
6. Do not build FlockMode photo sharing, multi-city trips, removed routes, Travel DNA, dark mode, or native apps under this list.
7. Usage-limit preflight: before starting each implementation card, estimate whether the 5-hour/weekly Hermes limit is enough; warn Fariz before starting if it may not be.

---

## High-level change summary

v5 is not a small polish pass. It is a substantial product reset from the existing v2/v3 repo baseline.

### Product and architecture changes

- **New authoritative source:** v5 supersedes v4, v3, and v2.1. Existing repo docs still point to v2.1, so implementation must avoid mixing old and new scope accidentally.
- **Prototype-first instruction:** v5 explicitly requires a **single HTML prototype** with vanilla JS/CSS, no build step, no framework, inline/base64 assets, React state only if JSX is used, and no localStorage/sessionStorage.
- **Layer separation:** v5 introduces `[L1]` prototype vs `[L2]` production integration annotations.
- **Routing changes:** v5 routes are simplified to `/`, `/trip/:id`, `/trip/:id/plan`, `/trip/:id/active`, `/trip/:id/flock`, `/trip/:id/wrap`, `/chat`, and `/join/:token`.
- **Removed routes:** `/compliance`, `/waiting`, and `/predeparture` must not be built.
- **State model:** phase now comes from `trip.state` values: `planning`, `active`, `past`.
- **Demo data reset:** v5 demo path centers on 5 trips: Lisbon planning, Tokyo active, and 3 past trips. Existing frontend currently presents the older Tokyo-centric demo flow.
- **MongoDB emphasis:** MongoDB Atlas with MCP remains a primary judging lens.
- **Backend endpoint contract updated:** `/health` now expects `{"status":"ok","version":"v5","mongo":"connected","firebase":"connected"}` in v5, while the existing README still documents `version":"v0"`.

### Role and permission changes

- Role matrix is reduced to **Organiser**, **Co-leader**, and **Member** in the main PRD table.
- Flock leader behavior still exists as a contextual permission during FlockMode: Flock-scoped edits apply directly, main trip suggestions are logged.
- Prototype behavior is explicitly demo-oriented: activity edits can alert; suggestions show 2 pending items; accept/decline can toast.

### Navigation changes

- v5 replaces the previous broader navigation with two modes:
  - Global: Home, Plan a new trip, Join a trip, Profile via user pill.
  - Trip-scoped: phase-specific nav items.
- Sidebar context card must show the active trip dynamically, not hardcoded copy.
- Suggestions badge becomes a lime app-icon badge over the nav icon, not a red/inline tag.

### UI/design changes

- **Brand palette changed:** old Yale/lemon/teal tokens are replaced by deep purple + lime + orange.
- **Logo changed:** v5 calls for a PNG wordmark with `mix-blend-mode: screen`; old SVG is fallback only.
- **Typography changed:** v5 uses Nunito/Baloo 2-oriented tokens and larger display scale.
- **Layout changed:** desktop sidebar is 240px; mobile uses a drawer below 900px.
- **Mobile-first requirement strengthened:** minimum supported width is 360px, with explicit `<900px` behavior.
- **Cards/buttons/tags rewritten:** components must use v5 tokens and avoid raw hex in component CSS.
- **Save button placement fixed:** profile tabs and budget editor save buttons must be anchored at the bottom of the section content, not floating/sticky.
- **Judge panel changed:** draggable bottom-left panel with open/collapsed states and `⚡ Demo controls · drag me` label.
- **FAB changed:** 64x64 purple circle, lime ring, mascot background, alert pulse.

### Screen changes

- **Home:** now shows Plan CTA plus Upcoming, Active, and Past trip sections.
- **Entry conversation:** v5 wants a static L1 entry screen with free-text textarea and quick-select chips, later SSE in L2.
- **Profile:** now tabbed with About me, Food & diet, How I travel, Past trips, Passport & visas.
- **Planning itinerary:** now has day rail, activity view variants, budget editor, map placeholder/card, admin 3-dot menus.
- **Flights:** shows 3 options per origin group with risk score thresholds.
- **Suggestions:** pending suggestion workflow with role-gated Accept/Decline.
- **FlockMode:** split creation in planning and active Flock view are separate concepts.
- **Active Today:** uses `currentTrip.activeDay`; includes quick action rail.
- **Expenses:** 4 split modes and 6 categories.
- **Wrap:** trip-aware wrap data by `WRAP_DATA[trip.id]`, destination local currency only.
- **Travel DNA:** removed from v1 scope.

### Explicit non-build changes

- FlockMode photo sharing remains placeholder only.
- Multi-city trips remain future scope only.
- Travel DNA is removed.
- Multi-currency trip budget remains future scope.
- Suggestions-to-itinerary animation remains future scope.
- Member join post-code flow is specced but not built in prototype.

---

## Current repo gap snapshot

Read-only repo evidence from this pass:

- Existing fixed Kanban is v2.1-based and has BNC-001 through BNC-040 mostly complete, with BNC-031 blocked on human submission work.
- Existing frontend files are split across `frontend/index.html`, `frontend/app.js`, `frontend/style.css`, assets, manifest, and service worker.
- Existing `frontend/style.css` still starts with old Yale/lemon tokens, not v5 purple/lime/orange tokens.
- Existing frontend uses external Google Maps behavior and static asset files; v5 L1 says all assets should be inline/base64 and no external requests.
- Existing README still names v2.1 docs as the source of truth and documents `/health` as `version: v0`.
- Existing Cloud Run URL and backend deployment may remain valuable, but v5 needs a deliberate choice: either build the L1 single-file prototype first, then reconcile L2 backend, or retrofit the existing deployed app toward v5.

---

## Fixed v5 Kanban

### TODO

- **BV5-001 — Decide v5 execution mode and repository contract**
  - Objective: Choose whether v5 work is a fresh L1 single-file prototype, a retrofit of the existing deployed app, or a two-track plan.
  - Files likely touched: `README.md`, `docs/kanban/bounce_v5_analysis_and_kanban.md`, optionally `docs/prd/` and `docs/design/` if Fariz approves committing the full v5 source docs.
  - Acceptance:
    - Fariz-approved execution mode is recorded.
    - The repo clearly states which PRD/design version is authoritative for future work.
    - Existing BNC v2/v3 cards are not silently rewritten.

- **BV5-003 — Create the v5 L1 prototype shell**
  - Objective: Establish the v5 single-file prototype boundary required by PRD v5 AI build instructions.
  - Files likely touched: `frontend/bounce_v5_prototype.html` or Fariz-approved equivalent path, plus tests.
  - Acceptance:
    - Prototype loads as one HTML file.
    - No build step is required.
    - No localStorage/sessionStorage is used.
    - Demo data is declared as `const` objects near the top.
    - No network fetches are required for L1 demo state.

- **BV5-004 — Apply v5 visual identity and design tokens**
  - Objective: Replace old Yale/lemon visual language in the v5 prototype with the purple/lime/orange v5 system.
  - Files likely touched: v5 prototype HTML/CSS section, asset embedding helper if needed.
  - Acceptance:
    - `:root` includes v5 tokens from the design system.
    - Component CSS uses variables, not raw component-level hex values except inside token definitions or encoded assets.
    - Bounce avatar, fallback logo, FAB, cards, tags, and buttons match v5 specs.

- **BV5-005 — Implement v5 app shell, navigation, and mobile drawer**
  - Objective: Build the global/trip-scoped sidebar behavior and mobile top bar/drawer.
  - Files likely touched: v5 prototype HTML/JS/CSS.
  - Acceptance:
    - Global nav shows Home, Plan, Join, with Profile accessed by user pill.
    - Trip-scoped nav adapts for planning, active, and past trips.
    - `← All trips` exits trip context.
    - Trip context card uses selected trip data dynamically.
    - Mobile drawer opens/closes under 900px and closes on backdrop/nav click.

- **BV5-006 — Implement v5 demo data and phase dispatcher**
  - Objective: Encode the 5-trip v5 demo dataset and route/phase dispatch behavior.
  - Files likely touched: v5 prototype JS data/state section.
  - Acceptance:
    - Home shows Lisbon planning, Tokyo active, and 3 past trips.
    - `trip.state` controls phase and nav.
    - Tokyo active uses `activeDay: 3` and `totalDays: 7`.
    - Wrap screens read from `WRAP_DATA[trip.id]` with destination local currency only.

- **BV5-007 — Build Home and Entry Conversation screens**
  - Objective: Implement the v5 Home screen and static L1 Plan a new trip entry.
  - Files likely touched: v5 prototype screen components.
  - Acceptance:
    - Home sections and TripCard states match PRD/design v5.
    - Plan CTA copy matches v5: `Your trip starts here. Tell me what you've got in mind.`
    - Entry has free-text textarea, mascot/hero treatment, trip-type chips, and deterministic Bounce response.

- **BV5-008 — Build Profile tabs with anchored save buttons**
  - Objective: Implement v5 tabbed profile UI and save-button placement fixes.
  - Files likely touched: v5 prototype screen components.
  - Acceptance:
    - Tabs: About me, Food & diet, How I travel, Past trips, Passport & visas.
    - Editable tabs have bottom-anchored `Save changes` buttons.
    - Past trips tab is read-only and has no save button.
    - Save action produces visible demo feedback.

- **BV5-009 — Build Planning itinerary, budget, map, flights, and suggestions**
  - Objective: Implement the planning phase demo screens and role-aware controls.
  - Files likely touched: v5 prototype screen components/data.
  - Acceptance:
    - Itinerary layout has day rail, view toggles, activity cards, BudgetCard, and map placeholder/card.
    - Admin roles see 3-dot activity menus in planning; members do not directly edit.
    - Budget editor has two inputs and bottom save behavior.
    - Flights show 3 options per origin group with risk labels.
    - Suggestions show 2 pending items and lime nav badge positioned over the icon.

- **BV5-010 — Build Active Today, FlockMode, disruption, expenses, and alerts**
  - Objective: Implement active-trip screens and demo interactions.
  - Files likely touched: v5 prototype screen components/data.
  - Acceptance:
    - Today screen uses Tokyo Day 3 data and quick actions.
    - FlockMode switcher, active flock schedule, countdown, SVG map, and photo-sharing placeholder render.
    - Disruption modal shows 3 alternatives and uses `Lock this in & ping everyone →` / `Not now` copy.
    - Expenses include 4 split modes and 6 categories with visible local state updates.
    - Alerts have populated/empty states per v5.

- **BV5-011 — Build Post-trip Wrap screens**
  - Objective: Implement trip-aware wrap screens for all 3 past trips.
  - Files likely touched: v5 prototype screen components/data.
  - Acceptance:
    - Each past trip renders unique total, per-person amount, category breakdown, settlements, and BounceSay insight.
    - Destination local currency is used only; no USD conversion is shown.
    - Travel DNA does not appear.

- **BV5-012 — Build Bounce assistant panel, FAB, and role labels**
  - Objective: Implement the v5 Bounce chat surface and role-specific permission copy.
  - Files likely touched: v5 prototype screen components/CSS.
  - Acceptance:
    - FAB matches v5 mascot/ring/pulse behavior.
    - Chat panel has dialog ARIA, header, message stream, pill input, and close behavior.
    - Permission label changes for Organiser/Co-leader, Flock leader, and Member.
    - L1 responses are deterministic and do not fetch.

- **BV5-013 — Build draggable Judge / Demo Controls panel**
  - Objective: Implement the v5 judge panel as the primary demo driver.
  - Files likely touched: v5 prototype JS/CSS.
  - Acceptance:
    - Panel starts bottom-left, has z-index 500, and can be dragged.
    - Panel toggles open/collapsed with lime pill `⚡ Demo controls`.
    - Role selector, phase selector, Trigger disruption, and Reset demo controls work visibly.
    - Label is `⚡ Demo controls · drag me`.

- **BV5-014 — Add v5 prototype automated checks**
  - Objective: Guard the v5 prototype against regressions and accidental scope violations.
  - Files likely touched: `tests/frontend/` or equivalent test path.
  - Acceptance:
    - Tests verify required v5 copy, routes/hash states, nav labels, CUT placeholders, and no removed routes.
    - Tests verify no localStorage/sessionStorage usage in the prototype.
    - Tests verify FlockMode photo sharing remains placeholder-only.
    - Tests verify the prototype contains no obvious external asset/script requests except any explicitly approved Babel CDN exception from PRD v5.

- **BV5-015 — Local visual/responsive smoke pass**
  - Objective: Verify the v5 prototype manually and/or through browser smoke at desktop, tablet, and mobile widths.
  - Files likely touched: smoke evidence doc if needed.
  - Acceptance:
    - 1280px+ full layout works.
    - 900-1280px itinerary/right-rail behavior works.
    - <900px mobile drawer and stacked layout work down to 360px.
    - Browser console has no startup errors.
    - Representative demo path from PRD Part 12 works end to end.

### IN_PROGRESS

- None.

### BLOCKED

- **BV5-002 — Add v5 source-of-truth docs to repo if approved**
  - Objective: Commit `bounce_prd_v5.md` and `bounce_design_v5.md` into canonical repo paths only after Fariz confirms this is desired.
  - Files likely touched: `docs/prd/bounce_prd_v5.md`, `docs/design/bounce_design_v5.md`, `README.md`.
  - Acceptance:
    - v5 docs are present in repo with exact supplied content.
    - README points to v5 as current source of truth.
    - v2/v3 docs remain available as historical references, not deleted.
  - Blocker: needs Fariz approval because the current request was to analyze supplied files read-only, not to commit the full supplied PRD/design as canonical docs.

- **BV5-016 — Decide and perform deployment path**
  - Objective: Choose whether to deploy the v5 prototype to existing Cloud Run, Firebase Hosting, or keep local only until L2 integration.
  - Files likely touched: deployment docs/config only after approval.
  - Acceptance:
    - Fariz-approved deployment target is recorded.
    - If deployed, hosted URL loads the v5 prototype and `/health` remains healthy.
    - Smoke evidence records exact URLs, status codes, and revision/version identifier.
  - Blocker: needs Fariz decision after BV5-001 because v5 can be implemented as local L1 prototype, deployed prototype, or retrofit of existing app.

- **BV5-017 — Reconcile L2 backend contract to v5**
  - Objective: Align production API contracts with v5 without overbuilding beyond the approved prototype/deployment mode.
  - Files likely touched: backend routes/docs/tests only after L2 approval.
  - Acceptance:
    - `/health` can report v5-shaped status when L2 mode is enabled.
    - `/api/chat` SSE contract is documented/tested or explicitly deferred.
    - MongoDB/Firebase collection/path names match v5 PRD where L2 is in scope.
    - Existing live deployment is not broken by prototype work.
  - Blocker: should not start until Fariz approves L2 work after the L1 prototype path is clear.

### DONE

- **BV5-000 — Read-only v5 analysis and fixed Kanban draft**
  - Objective: Analyze supplied v5 PRD/design and create this fixed task breakdown.
  - Acceptance:
    - v5 changes are summarized.
    - Fixed stable card IDs exist.
    - CUT scope is preserved.
    - No product implementation was performed.

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

Recommended next action: **BV5-001 — Decide v5 execution mode and repository contract**.

Reason: v5 conflicts with the current repo baseline in a fundamental way. The PRD requires a single-file L1 prototype with inline assets/no storage/no fetch, while the existing app is a deployed multi-file v2/v3-style implementation. Starting implementation before choosing the execution mode would violate the 12 commandments by mixing scope and risking broad, non-surgical changes.
