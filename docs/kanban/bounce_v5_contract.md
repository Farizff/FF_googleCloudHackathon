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

- **BV5-006 — Implement v5 demo data and phase dispatcher**
  - Objective: Encode the 5-trip v5 demo dataset and route/phase dispatch behavior.
  - Acceptance:
    - Home shows Lisbon planning, Tokyo active, and 3 past trips.
    - `trip.state` controls phase and nav.
    - Tokyo active uses `activeDay: 3` and `totalDays: 7`.
    - Wrap screens read from `WRAP_DATA[trip.id]` with destination local currency only.

- **BV5-007 — Build Home and Entry Conversation screens**
  - Objective: Implement the v5 Home screen and static L1 Plan a new trip entry.
  - Acceptance:
    - Home sections and TripCard states match PRD/design v5.
    - Plan CTA copy matches v5: `Your trip starts here. Tell me what you've got in mind.`
    - Entry has free-text textarea, mascot/hero treatment, trip-type chips, and deterministic Bounce response.

- **BV5-008 — Build Profile tabs with anchored save buttons**
  - Objective: Implement v5 tabbed profile UI and save-button placement fixes.
  - Acceptance:
    - Tabs: About me, Food & diet, How I travel, Past trips, Passport & visas.
    - Editable tabs have bottom-anchored `Save changes` buttons.
    - Past trips tab is read-only and has no save button.
    - Save action produces visible demo feedback.

- **BV5-009 — Build Planning itinerary, budget, map, flights, and suggestions**
  - Objective: Implement the planning phase demo screens and role-aware controls.
  - Acceptance:
    - Itinerary layout has day rail, view toggles, activity cards, BudgetCard, and map placeholder/card.
    - Admin roles see 3-dot activity menus in planning; members do not directly edit.
    - Budget editor has two inputs and bottom save behavior.
    - Flights show 3 options per origin group with risk labels.
    - Suggestions show 2 pending items and lime nav badge positioned over the icon.

- **BV5-010 — Build Active Today, FlockMode, disruption, expenses, and alerts**
  - Objective: Implement active-trip screens and demo interactions.
  - Acceptance:
    - Today screen uses Tokyo Day 3 data and quick actions.
    - FlockMode switcher, active flock schedule, countdown, SVG map, and photo-sharing placeholder render.
    - Disruption modal shows 3 alternatives and uses `Lock this in & ping everyone →` / `Not now` copy.
    - Expenses include 4 split modes and 6 categories with visible local state updates.
    - Alerts have populated/empty states per v5.

- **BV5-011 — Build Post-trip Wrap screens**
  - Objective: Implement trip-aware wrap screens for all 3 past trips.
  - Acceptance:
    - Each past trip renders unique total, per-person amount, category breakdown, settlements, and BounceSay insight.
    - Destination local currency is used only; no USD conversion is shown.
    - Travel DNA does not appear.

- **BV5-012 — Build Bounce assistant panel, FAB, and role labels**
  - Objective: Implement the v5 Bounce chat surface and role-specific permission copy.
  - Acceptance:
    - FAB matches v5 mascot/ring/pulse behavior.
    - Chat panel has dialog ARIA, header, message stream, pill input, and close behavior.
    - Permission label changes for Organiser/Co-leader, Flock leader, and Member.
    - L1 responses are deterministic and do not fetch.

- **BV5-013 — Build draggable Judge / Demo Controls panel**
  - Objective: Implement the v5 judge panel as the primary demo driver.
  - Acceptance:
    - Panel starts bottom-left, has z-index 500, and can be dragged.
    - Panel toggles open/collapsed with lime pill `⚡ Demo controls`.
    - Role selector, phase selector, Trigger disruption, and Reset demo controls work visibly.
    - Label is `⚡ Demo controls · drag me`.

- **BV5-014 — Add v5 prototype automated checks**
  - Objective: Guard the v5 prototype against regressions and accidental scope violations.
  - Acceptance:
    - Tests verify required v5 copy, routes/hash states, nav labels, CUT placeholders, and no removed routes.
    - Tests verify no localStorage/sessionStorage usage in the prototype.
    - Tests verify FlockMode photo sharing remains placeholder-only.
    - Tests verify the prototype contains no obvious external asset/script requests except any explicitly approved Babel CDN exception from PRD v5.

- **BV5-015 — Local visual/responsive smoke pass**
  - Objective: Verify the v5 prototype manually and/or through browser smoke at desktop, tablet, and mobile widths.
  - Acceptance:
    - 1280px+ full layout works.
    - 900-1280px itinerary/right-rail behavior works.
    - <900px mobile drawer and stacked layout work down to 360px.
    - Browser console has no startup errors.
    - Representative demo path from PRD Part 12 works end to end.

### IN_PROGRESS

- None.

### BLOCKED

- **BV5-016 — Decide and perform deployment path**
  - Objective: Choose whether to deploy the v5 prototype to existing Cloud Run, Firebase Hosting, or keep local only until L2 integration.
  - Acceptance:
    - Fariz-approved deployment target is recorded.
    - If deployed, hosted URL loads the v5 prototype and `/health` remains healthy.
    - Smoke evidence records exact URLs, status codes, and revision/version identifier.
  - Blocker: needs Fariz decision after local v5 L1 prototype is built and smoke-tested.

- **BV5-017 — Reconcile L2 backend contract to v5**
  - Objective: Align production API contracts with v5 without overbuilding beyond the approved prototype/deployment mode.
  - Acceptance:
    - `/health` can report v5-shaped status when L2 mode is enabled.
    - `/api/chat` SSE contract is documented/tested or explicitly deferred.
    - MongoDB/Firebase collection/path names match v5 PRD where L2 is in scope.
    - Existing live deployment is not broken by prototype work.
  - Blocker: should not start until Fariz approves L2 work after the L1 prototype path is clear.

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

Recommended next action: **BV5-006 — Implement v5 demo data and phase dispatcher**.

Reason: the v5 L1 prototype now has the phase-aware app shell, global/trip nav, dynamic trip context card, user pill, and mobile drawer foundation. The next safe, surgical step is to refine the five-trip demo dataset and route/phase dispatcher against the v5 PRD.
