# Bounce Frontend Usability Kanban Addendum

Source of truth: Fariz approval on 2026-05-25 to expand the fixed Bounce Kanban with BNC-032 through BNC-040.

Approved scope: **Option A — Demo-usable MVP**. Make every visible button/control visibly do something useful, using deterministic local frontend state where backend support is missing. Prefer existing backend APIs where already available, but do not expand into a full backend rebuild without new approval.

Deployment target: existing Cloud Run service `bounce-api` in project `project-411e0419-48bd-4b5b-97f`, region `asia-southeast1`.

## Scope-control rules

1. This addendum is the approved expansion to the fixed Kanban. Do not silently add BNC-041+ cards.
2. Keep PRD CUT items out of scope unless Fariz explicitly reopens them.
3. Demo-usable MVP means controls may use local state when backend routes are missing, but every visible interaction must produce clear visible feedback.
4. If a control cannot be safely implemented in this pass, it must be disabled or labelled as unavailable with a visible reason.
5. Checkpoint coherent progress with tests and commit/push before deployment.
6. Final acceptance requires hosted URL smoke verification, not only local tests.

---

## TODO

- None.

## IN_PROGRESS

- None.

## BLOCKED

- None.

## DONE

- **BNC-040 — Deploy and hosted usability smoke**
  - PRD source: Part 16 deployment and Part 17 hosted URL/judge instructions.
  - Deliverable: deploy updated frontend/backend container to existing Cloud Run service and smoke hosted interactions.
  - Acceptance: hosted URL loads, `/health` passes, `/app.js` serves current code, `/chat` works or falls back visibly, judge endpoints pass, and representative visible controls produce useful feedback.
  - Completed checkpoint: Cloud Run revision `bounce-api-00016-wv7` serves 100% traffic for `https://bounce-api-4dynllwdeq-as.a.run.app`; hosted `/health`, `/`, `/app.js?v=20260525v3`, `/style.css?v=20260525v3`, `/assets/logo.svg`, `/assets/v3-1.png`, `/judge/seed-demo-trip`, and `/itineraries/iti_tokyo_reunion_2026` returned HTTP 200. Browser visual smoke confirmed the v3 purple/lime desktop layout, left sidebar, graphics, itinerary cards, static map fallback, and no console errors on initial load.

- **BNC-032 — Frontend usability audit and interaction contract**
  - PRD source: Part 4 frontend files, Part 12 judge test mode, Part 14 demo script, Part 15 testing checklist; design source: `docs/design/bounce_design_v2.md`.
  - Deliverable: inventory every visible clickable control and define its intended MVP behavior.
  - Acceptance: every visible button/control is classified as backend-backed, local-state, navigation, disabled, or intentionally unavailable; no ambiguous clickable controls remain.
  - Evidence: `docs/design/frontend_interaction_contract.md`.

- **BNC-033 — Wire core planning controls**
  - PRD source: Part 14 demo script 0:15-1:15 and Part 15 core loop/flights/maps.
  - Deliverable: quick planning chips, prompt submission, planning response, budget, flight, and map preview interactions.
  - Acceptance: user can tap chips or type a trip prompt, submit it, and see coherent planning cards update; flight option selection and map preview feedback are visible.
  - Evidence: `frontend/app.js`, `frontend/style.css`, `tests/frontend/test_bnc032_frontend_usability.py`.

- **BNC-034 — Wire profile and preference controls**
  - PRD source: Days 3-5 profile gap-fill UI and Part 15 profile gap-fill checklist.
  - Deliverable: profile chips toggle selected/unselected state and feed into demo planning state.
  - Acceptance: selected preferences visibly persist and are reflected in status/output or subsequent planning copy.
  - Evidence: profile-chip local state in `frontend/app.js`.

- **BNC-035 — Wire group suggestion controls**
  - PRD source: Days 9-11 suggestion aggregation pipeline and Part 15 group checklist.
  - Deliverable: Accept, Modify, and Decline controls with deterministic visible state transitions.
  - Acceptance: accepting applies suggestion to itinerary text, modifying reveals an editable path, declining updates count/status.
  - Evidence: suggestion handlers and state styles in `frontend/app.js` and `frontend/style.css`.

- **BNC-036 — Wire FlockMode controls**
  - PRD source: Part 1.5 FlockMode composition, Days 9-11 FlockMode UI, Part 14 demo script 1:15-1:50.
  - Deliverable: Split into Flocks, editable flock names, and Start FlockMode interactions update active Flock view.
  - Acceptance: user can move from group dashboard to active FlockMode and see edits reflected in the active trip/Flock state.
  - Evidence: FlockMode local state handlers in `frontend/app.js`.

- **BNC-037 — Wire active trip Ask Bounce control**
  - PRD source: Part 5 intent classification and Part 14 active trip flow.
  - Deliverable: Ask Bounce anything opens an inline prompt or reuses existing chat and calls `/chat` where available.
  - Acceptance: user can ask a contextual active-trip question and see a visible answer or deterministic fallback.
  - Evidence: `askBounceAboutToday()` in `frontend/app.js`.

- **BNC-038 — Wire split bill controls**
  - PRD source: Days 12-13 split bill backend/UI and Part 15 split bill checklist.
  - Deliverable: split tabs, amount/description/category controls, and Log expense update balances through existing API or deterministic local state.
  - Acceptance: all 4 split modes visibly select, category chips select, and logging an expense updates status/output/balance display.
  - Evidence: split bill local-state handlers in `frontend/app.js`.

- **BNC-039 — Add frontend smoke tests for controls**
  - PRD source: Part 15 testing checklist and Day 14-15 polish requirement to fix anything broken.
  - Deliverable: local automated guard that fails when visible buttons lack intentional behavior metadata, a click handler path, navigation target, or disabled state.
  - Acceptance: test suite includes frontend control coverage and passes locally.
  - Evidence: `tests/frontend/test_bnc032_frontend_usability.py`; local frontend test subset: 14 passed.

## CUT — do not build without approval

- Backend rebuild beyond thin adapters required for visible MVP feedback.
- PRD CUT items from `docs/kanban/bounce_fixed_kanban.md`.
- Live GPS/location tracking, receipt scanning, multi-language UI, AI packing lists, and other explicitly cut features.

---

## Current next card recommendation

Recommended next action: **No frontend-usability cards remain**.

Reason: BNC-032 through BNC-040 are implemented, deployed, and smoke-verified. BNC-031 remains outside this addendum and is team-owned/human submission work.
