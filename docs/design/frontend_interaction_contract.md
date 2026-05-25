# Bounce Frontend Interaction Contract

Source: `frontend/index.html`, `frontend/app.js`, `docs/prd/bounce_prd_v2.md`, and `docs/design/bounce_design_v2.md`.

Purpose: BNC-032 defines the MVP behavior contract for every visible clickable control in the hosted Bounce frontend. The target is **demo-usable MVP**: every visible control must produce useful visible feedback. Backend-backed behavior is preferred where already available; deterministic local state is acceptable where backend work would exceed the approved frontend usability pass.

## Behavior categories

- **Backend-backed:** calls an existing API route and renders the result or error.
- **Local-state MVP:** updates deterministic frontend state and visible UI without claiming live persistence.
- **Navigation:** scrolls/navigates to a visible section.
- **Disabled/unavailable:** visibly disabled with a reason. Use only if a useful MVP behavior is unsafe or misleading.

## Global acceptance rules

1. Every `<button>` must have one of: explicit JavaScript behavior, navigation behavior, `disabled`, or a documented `data-action`/`data-state` behavior.
2. Every click must visibly change one or more of: selected state, status line, response text, card content, badge/count, output panel, or scroll target.
3. Backend failures must show a user-facing fallback or error; they must not fail silently.
4. Demo/local-state behavior must be deterministic and honest. Do not imply unavailable live services succeeded.
5. The hosted URL must be smoke-tested after deployment.

---

## Control inventory and MVP behavior

### Auth / entry

- `#start-button` — **Local-state MVP**
  - Current label: `Let's go →`
  - Behavior: validate/accept traveller name, personalize UI copy, show status/output confirmation, scroll to trip prompt.

- `#send-trip-prompt` — **Backend-backed with local fallback**
  - Current label: `Send to Bounce →`
  - Behavior: call `/chat` with prompt, selected preferences, and current trip context; render response and planning snapshot. If `/chat` fails, render deterministic local planning snapshot and show fallback status.

- `.quick-chip[data-category="Culture"]` — **Local-state MVP**
  - Behavior: toggle selected planning category and append/reflect culture preference in trip prompt/planning state.

- `.quick-chip[data-category="Food"]` — **Local-state MVP**
  - Behavior: toggle selected planning category and append/reflect food preference in trip prompt/planning state.

- `.quick-chip[data-category="Shopping"]` — **Local-state MVP**
  - Behavior: toggle selected planning category and append/reflect shopping preference in trip prompt/planning state.

- `.quick-chip[data-mode="International"]` — **Local-state MVP**
  - Behavior: toggle international mode and reflect international arrival buffer in planning/status copy.

### Profile gap-fill

- Profile chip `Halal-friendly` — **Local-state MVP**
  - Behavior: toggle selected preference and update profile/preferences summary.

- Profile chip `Art` — **Local-state MVP**
  - Behavior: toggle selected preference and update profile/preferences summary.

- Profile chip `Food` — **Local-state MVP**
  - Behavior: toggle selected preference and update profile/preferences summary.

- Profile chip `Low walking first day` — **Local-state MVP**
  - Behavior: toggle selected preference and update profile/preferences summary; planning copy should mention lower Day 1 intensity when selected.

### Flights / map / planning cards

- `.flight-option-card` cards — **Local-state MVP**
  - Behavior: selectable cards; selected card receives visible state and status/output updates.

- `.map-canvas` — **Local-state MVP**
  - Behavior: show route/pin summary based on current planning snapshot and selected flight/itinerary state. It may remain a tokenized map preview in MVP.

### Group dashboard and suggestions

- `#split-into-flocks` — **Navigation + local-state MVP**
  - Current label: `Split into Flocks`
  - Behavior: populate default Flock state, status confirms split, scroll to FlockMode creation.

- `.sug-accept` — **Local-state MVP**
  - Current label: `Accept`
  - Behavior: apply suggestion to itinerary card, mark suggestion accepted, decrement/update badge/status.

- `.sug-modify` — **Local-state MVP**
  - Current label: `Modify`
  - Behavior: reveal an editable modification prompt or reuse trip prompt with suggestion text, status explains next step.

- `.sug-decline` — **Local-state MVP**
  - Current label: `Decline`
  - Behavior: mark suggestion declined, update badge/status, keep itinerary unchanged.

### FlockMode

- Flock name inputs — **Local-state MVP**
  - Behavior: edits update Flock state and are reflected in active Flock heading after Start FlockMode.

- `#start-flockmode` — **Local-state MVP**
  - Current label: `Start FlockMode →`
  - Behavior: activate FlockMode, update active Flock heading/reconvene copy from current inputs, set bottom nav phase/status, scroll to active Flock view.

### Active trip

- `.ask-bounce-button` — **Backend-backed with local fallback**
  - Current label: `Ask Bounce anything about today →`
  - Behavior: reveal inline active-trip question prompt or prefill main prompt with contextual question; call `/chat` where available and render answer. If unavailable, show deterministic useful active-trip answer.

### Split bill

- Expense mode tab `Everyone` — **Local-state MVP**
  - Behavior: select split mode, update `aria-selected`, update split-between copy.

- Expense mode tab `Specific people` — **Local-state MVP**
  - Behavior: select split mode, update `aria-selected`, update split-between copy to named subset.

- Expense mode tab `My Flock` — **Local-state MVP**
  - Behavior: select split mode, update `aria-selected`, update split-between copy to active Flock.

- Expense mode tab `Just me` — **Local-state MVP**
  - Behavior: select split mode, update `aria-selected`, update split-between copy to traveller only.

- Expense category chip `🍜 Food` — **Local-state MVP**
  - Behavior: select category and show selected state.

- Expense category chip `🚇 Transport` — **Local-state MVP**
  - Behavior: select category and show selected state.

- Expense category chip `🎟 Activity` — **Local-state MVP**
  - Behavior: select category and show selected state.

- `#log-expense` — **Backend-backed if available, local fallback required**
  - Current label: `Log expense`
  - Behavior: read amount, description, selected split mode, selected category; call existing expense route if compatible, otherwise update local balance cards/status/output deterministically.

### Judge/backend panel

- `#health-button` — **Backend-backed**
  - Current label: `Check health`
  - Behavior: call `/health`, show status/output.

- `#seed-button` — **Backend-backed**
  - Current label: `Seed demo trip`
  - Behavior: call `/judge/seed-demo-trip`, show status/output, update demo state if successful.

- `#disruption-button` — **Backend-backed with visible fallback/error**
  - Current label: `Trigger disruption`
  - Behavior: call `/judge/trigger-disruption`, show alternatives/status/output; update disruption/itinerary UI with returned data where available. If call fails, show error and deterministic local disruption state only if clearly labelled fallback.

### Bottom navigation

- `.bottom-nav a[href="#entry-conversation"]` — **Navigation**
  - Behavior: scroll to planning entry. Active tab state should update.

- `.bottom-nav a[href="#active-trip-view"]` — **Navigation**
  - Behavior: scroll to active trip. Active tab state should update.

- `.bottom-nav a[href="#map-preview"]` — **Navigation**
  - Behavior: scroll to map preview. Active tab state should update.

- `.bottom-nav a[href="#split-bill"]` — **Navigation**
  - Behavior: scroll to split bill. Active tab state should update.

- `.bottom-nav a[href="#demo-title"]` — **Navigation**
  - Behavior: scroll to judge/demo panel. Active tab state should update.

---

## Verification plan

- Add static/frontend test that inventories visible buttons and verifies intentional behavior metadata or known selectors.
- Run existing backend tests plus new frontend control test.
- Run local browser smoke if possible.
- Deploy to Cloud Run.
- Smoke hosted URL and representative controls after deployment.
