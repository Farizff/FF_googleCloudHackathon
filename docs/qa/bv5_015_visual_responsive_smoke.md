# BV5-015 Local visual/responsive smoke pass

Date: 2026-06-01 09:08 SEAST  
Prototype: `frontend/bounce_v5_prototype.html`  
Runner: Playwright Chromium screenshots plus Hermes browser DOM smoke.

## Viewport evidence

- `1280x900 desktop`
  - Screenshot: `docs/qa/assets/bv5-015/desktop-1280-home.png`
  - Result: desktop: app shell and full layout rendered.
  - Evidence: global sidebar/nav, Home CTA, upcoming/active/past trip grids, Bounce FAB, and Demo Controls are visible.

- `1024x768 tablet`
  - Screenshot: `docs/qa/assets/bv5-015/tablet-1024-planning.png`
  - Result: tablet: itinerary/right-rail layout rendered.
  - Evidence: Lisbon planning board, day rail, itinerary content, BudgetCard, and offline map placeholder are visible together at the 900-1280px range.

- `360x800 mobile`
  - Screenshot: `docs/qa/assets/bv5-015/mobile-360-home.png`
  - Result: mobile: drawer opens/closes and stacked layout rendered down to 360px.
  - Evidence: mobile top bar is rendered at 360px; browser DOM smoke toggled drawer state open and closed without errors.

## Console and startup status

- Browser console startup errors: none.
- Hermes browser console after representative path: `console_messages=[]`, `js_errors=[]`.
- Playwright Chromium screenshots completed for all three target viewport sizes.

## Representative demo path smoke

Result: representative demo path completed end to end.

Steps exercised in the browser DOM smoke:

1. Home loaded with Upcoming, Active, and Past trip sections.
2. Plan a new trip opened the entry conversation.
3. Filled the trip prompt and submitted `Ready to bounce →`.
4. Verified deterministic Bounce response text appeared.
5. Opened Lisbon planning board and verified BudgetCard/map placeholder.
6. Jumped to Tokyo active trip and verified Tokyo Day 3 content.
7. Triggered disruption and verified Shinjuku rain disruption modal.
8. Opened FlockMode and verified photo sharing placeholder remains placeholder-only.
9. Opened Expenses and Alerts.
10. Opened Post-trip Wrap and verified destination local currency copy.
11. Opened Chat and verified deterministic offline response copy.
12. Toggled drawer state open/closed and verified state/class changes.

Browser DOM smoke result:

```json
{
  "innerWidth": 1254,
  "allOk": true,
  "steps": [
    "home",
    "entry",
    "planning",
    "active",
    "disruption",
    "flock",
    "expenses",
    "alerts",
    "wrap",
    "chat",
    "drawer-state"
  ]
}
```

## Commands run

```bash
npx -y playwright screenshot --browser=chromium --viewport-size=1280,900 --full-page file:///.../frontend/bounce_v5_prototype.html#screen=home&phase=home&user=maya tmp/bv5-smoke/desktop-1280-home.png
npx -y playwright screenshot --browser=chromium --viewport-size=1024,768 --full-page file:///.../frontend/bounce_v5_prototype.html#screen=trip&phase=planning-itinerary&user=maya&trip=lisbon-bday tmp/bv5-smoke/tablet-1024-planning.png
npx -y playwright screenshot --browser=chromium --viewport-size=360,800 --full-page file:///.../frontend/bounce_v5_prototype.html#screen=home&phase=home&user=maya tmp/bv5-smoke/mobile-360-home.png
```
