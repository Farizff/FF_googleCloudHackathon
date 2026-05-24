# Bounce Design v2 Application Audit

Status: applied to the frontend app shell.

Source of truth: `docs/design/bounce_design_v2.md`.

## Verified design-system coverage

- **Design tokens:** `frontend/style.css` starts with the Bounce v2 light-mode token block and uses the documented brand, semantic, neutral, typography, spacing, radius, shadow, z-index, and transition variables.
- **Typography base:** body now follows the v2 typography reset: `var(--font-sans)`, `var(--text-base)`, `var(--leading-normal)`, and font smoothing.
- **Visual identity:** the auth/hero screen uses the Bounce v2 SVG logomark structure from Part 0 instead of a generic text-only badge.
- **Cards and surfaces:** planning, profile, itinerary, budget, map, group, suggestion, FlockMode, active-trip, split-bill, and judge panels use the v2 card/radius/shadow/token language.
- **Buttons and chips:** primary, secondary, danger, quick-chip, member-chip, and suggestion controls use v2 pill shapes, brand colors, semantic states, and tokenized spacing.
- **Phase navigation:** bottom navigation now follows the v2 phase-adaptive tab structure with `.nav-tab`, `.nav-icon`, `.nav-label`, and active-trip phase handling.
- **Demo path mapping:** the frontend exposes the v2 3-minute demo screens: auth, entry conversation, profile gap-fill, itinerary, map, flight selection, group dashboard, suggestion review, FlockMode, active trip, split bill, and judge-ready controls.
- **Responsive behavior:** the app keeps a mobile-first layout and expands cards on desktop for demo recording.

## Intentional hackathon simplifications

- Icons use lightweight text glyphs instead of an external Tabler Icons dependency to keep the static frontend dependency-free.
- The map is a static tokenized preview rather than a live Google Maps canvas in the frontend shell.
- The app shell is demo-first and seeded; live backend verification remains in the judge panel.

## Verification commands

```bash
python -m pytest tests/api/test_judge.py tests/infra/test_verify_mongodb_atlas.py
```

Additional static checks performed:

- Confirmed `frontend/index.html` contains the v2 logomark SVG.
- Confirmed `frontend/style.css` contains the v2 token block and phase-adaptive `.nav-tab` navigation styles.
- Confirmed repo sync after commit/push with `git rev-list --left-right --count main...origin/main`.
