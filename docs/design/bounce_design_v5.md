# Bounce — Design System v5.0
**Mobile-first · Responsive · Light mode · Google Cloud Rapid Agent Hackathon 2026**

> Single source of truth for all UI styling, screens, component specs, and copy.
> Supersedes Design System v3.0.
>
> Architecture, data, algorithms, roles → `bounce_prd_v5.md`

---

# Part 0 — Visual Identity

## 0.1 — Logo System

**New wordmark (v5):** Single PNG with purple "Bounce" wordmark + lime "o", black background. Transparent-treating achieved via `mix-blend-mode: screen` on the `<img>` element — black pixels blend into any dark background.

**Spec:**
- Aspect ratio: 1108 × 273
- In-app height: 36px (sidebar), 26px (mobile top bar), 60px (marketing), 80px (splash)
- Background treatment: `mix-blend-mode: screen` — works on `var(--purple)` sidebar

**Component:**
```jsx
function Logomark({ size = 'md' }) {
  const heights = { sm: 26, md: 36, lg: 60, xl: 80 };
  const h = heights[size] || 36;
  const w = Math.round(h * (1108 / 273));
  return (
    <span style={{ display: 'inline-flex', width: w, height: h, flexShrink: 0 }}>
      <img
        src={BOUNCE_LOGO_URI} // base64 data URI
        alt="Bounce"
        style={{ width: '100%', height: '100%', objectFit: 'contain',
                 mixBlendMode: 'screen', display: 'block' }}
      />
    </span>
  );
}
```

**Previous SVG logomark** (fallback if PNG not available):
```svg
<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
  <rect width="40" height="40" rx="9" fill="#1A0A6B"/>
  <text x="9" y="29" font-family="'Baloo 2', cursive" font-weight="800" font-size="24" fill="#C8E64A">b</text>
  <circle cx="29" cy="10" r="4" fill="#C8E64A"/>
  <path d="M22 22 Q26 14 27 12" stroke="#C8E64A" stroke-width="1.5" fill="none" stroke-dasharray="2 3"/>
</svg>
```

## 0.2 — Bounce Avatar

```css
.bounce-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--purple); color: var(--lime);
  font-family: var(--font-logo); font-weight: 800; font-size: 20px;
  display: inline-flex; align-items: center; justify-content: center;
  border: 2px solid var(--lime);
}
.bounce-avatar-sm { width: 28px; height: 28px; font-size: 14px; border-width: 1.5px; }
.bounce-avatar-lg { width: 72px; height: 72px; font-size: 36px; box-shadow: var(--shadow-bounce); }
```

## 0.3 — Mascot (Bounce pinpoint)

SVG location-pin character. Used as FAB glyph and loading mascot.

FAB: deep-purple 64×64 circle, lime ring border, mascot PNG as background-image (130% size, center 30% position).

---

# Part 1 — Design Tokens

Paste this block at the top of `style.css`. Use only these variables — no raw hex in component CSS.

## 1.1 — Color Palette

```css
:root {
  /* ── Brand purple ── */
  --purple:        #1A0A6B;   /* primary nav, headers, CTAs, avatar bg */
  --purple-mid:    #4A2FC4;   /* interactive: buttons, links, focus rings */
  --purple-light:  #6B50E8;   /* hover states */
  --purple-tint:   #EDE9FF;   /* background tint on purple surfaces */

  /* ── Accent: Lime ── */
  --lime:          #C8E64A;   /* badges, active chips, add buttons, nav badge */
  --lime-dark:     #8DC63F;   /* feature bg, hover on lime */
  --lime-tint:     #F0FFD4;   /* callout backgrounds */
  --lime-text:     #3A5200;   /* text ON lime — WCAG AA 5.1:1 */

  /* ── Accent: Orange/Energy ── */
  --orange:        #F47B20;   /* CTA sections, energy moments */
  --orange-yellow: #FBBF24;   /* gradient pair with orange */
  --orange-tint:   #FFF7ED;   /* light orange bg */

  /* ── Gradient orbs (decorative) ── */
  --orb-1: radial-gradient(circle at 40% 30%, #FFAA3C 0%, #F47B20 60%, #E84040 100%);
  --orb-2: radial-gradient(circle at 35% 30%, #FBD0D9 0%, #FBBF8C 70%, #F9A270 100%);
  --orb-3: radial-gradient(circle at 35% 30%, #26C9B5 0%, #8DC63F 60%, #C8E64A 100%);
  --orb-4: radial-gradient(circle at 40% 30%, #C68CFB 0%, #7C3AED 60%, #5A18C4 100%);

  /* ── Semantic ── */
  --success:       #16A34A;
  --success-tint:  #F0FDF4;
  --warning:       #D97706;
  --warning-tint:  #FFF7ED;
  --danger:        #DC2626;
  --danger-tint:   #FEF2F2;
  --danger-text:   #7F1D1D;

  /* ── Activity category colors ── */
  --cat-food:      #F47B20;
  --cat-culture:   #7C3AED;
  --cat-nature:    #16A34A;
  --cat-transport: #1A0A6B;
  --cat-shopping:  #EC4899;
  --cat-hotel:     #C8E64A;
  --cat-nightlife: #4A2FC4;
  --cat-wellness:  #0D9488;

  /* ── Neutrals ── */
  --bg-page:       #FAF8FF;
  --bg-card:       #FFFFFF;
  --bg-raised:     #FAFAFA;

  /* ── Text ── */
  --text-primary:  #1A1A2E;
  --text-secondary:#5B5F6E;
  --text-tertiary: #9CA3AF;
  --text-inverse:  #FFFFFF;

  /* ── Borders ── */
  --border-light:  #ECE9F4;
  --border-medium: #D1CEDB;
  --border-strong: #9CA3AF;

  /* ── Typography ── */
  --font-logo:    'Baloo 2', system-ui, cursive;
  --font-display: 'Nunito', system-ui, sans-serif;
  --font-sans:    'Nunito', system-ui, sans-serif;
  --font-mono:    'SF Mono', 'Fira Code', ui-monospace, monospace;

  /* ── Type scale ── */
  --text-xs:   11px;   /* labels, tags, timestamps */
  --text-sm:   13px;   /* captions, secondary info */
  --text-base: 15px;   /* body text */
  --text-md:   17px;   /* subheadings, card titles */
  --text-lg:   20px;   /* section headings */
  --text-xl:   26px;   /* screen titles */
  --text-2xl:  34px;   /* hero numbers */
  --text-3xl:  48px;   /* large numeric display */

  /* ── Leading ── */
  --leading-tight:   1.2;
  --leading-normal:  1.5;
  --leading-relaxed: 1.65;

  /* ── Spacing ── */
  --sp-1: 4px;  --sp-2: 8px;   --sp-3: 12px; --sp-4: 16px;
  --sp-5: 20px; --sp-6: 24px;  --sp-8: 32px; --sp-10: 40px;
  --sp-12: 48px; --sp-16: 64px;

  /* ── Border radius ── */
  --r-xs:   6px;  --r-sm:  10px; --r-md: 14px;  --r-lg: 18px;
  --r-xl:  24px;  --r-2xl: 30px; --r-pill: 99px;

  /* ── Shadows ── */
  --shadow-card:   0 1px 3px rgba(26,10,107,.05), 0 0 0 .5px rgba(26,10,107,.04);
  --shadow-raised: 0 6px 20px rgba(26,10,107,.08);
  --shadow-float:  0 12px 36px rgba(26,10,107,.14);
  --shadow-bounce: 0 6px 28px rgba(26,10,107,.32);

  /* ── Z-index ── */
  --z-nav:     100;
  --z-chat:    200;
  --z-overlay: 300;
  --z-toast:   400;
  --z-judge:   500;

  /* ── Transitions ── */
  --t-fast:   140ms ease;
  --t-normal: 220ms ease;
  --t-slow:   320ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

## 1.2 — Token Usage Rules

| Token | Use for | Never use for |
|---|---|---|
| `--purple` | Nav bg, avatar bg, section headers, CTAs | Body text on white |
| `--purple-mid` | Buttons, links, active states | Large bg fills |
| `--lime` | Active chips, add buttons, **nav badges**, recommended tag | Error or warning states |
| `--lime-text` | Text ON lime surfaces only | Anything not on lime bg |
| `--orange` | CTA energy moments, disruption accent | Standard UI actions |
| `--text-secondary` | Captions, metadata, helper text | Headings |

---

# Part 2 — Typography

```css
h1, h2, h3, h4, h5, h6,
.t-display, .t-hero, .t-heading {
  font-family: var(--font-display);
  font-weight: 800;
  margin: 0;
  letter-spacing: -0.01em;
}

.t-display { font-size: var(--text-3xl); line-height: 1.05; letter-spacing: -0.025em; }
.t-hero    { font-size: var(--text-xl);  line-height: var(--leading-tight); letter-spacing: -0.015em; }
.t-heading { font-size: var(--text-lg);  line-height: var(--leading-tight); }
.t-title   { font-size: var(--text-md);  font-weight: 700; }
.t-body    { font-size: var(--text-base);font-weight: 500; line-height: var(--leading-relaxed); }
.t-caption { font-size: var(--text-sm);  font-weight: 500; color: var(--text-secondary); }
.t-label   { font-size: var(--text-xs);  font-weight: 800; letter-spacing: 0.08em;
             text-transform: uppercase; color: var(--text-tertiary); }
.t-mono    { font-family: var(--font-mono); font-size: var(--text-sm); }
```

---

# Part 3 — Component Library

## 3.1 — Buttons

All states:

| Variant | Default | Hover | Active | Disabled |
|---|---|---|---|---|
| `btn-primary` | `--purple-mid` bg, white text | `--purple-light`, translateY(-1px) | scale(.98) | opacity .45 |
| `btn-purple` | `--purple` bg, `--lime` text | #251175 bg | — | opacity .45 |
| `btn-lime` | `--lime` bg, `--lime-text` | `--lime-dark`, white text | — | opacity .45 |
| `btn-ghost` | transparent, border `--border-light` | border `--purple-mid`, `--purple` text | — | opacity .45 |
| `btn-danger` | `--danger` bg, white text | darker danger | — | opacity .45 |

Sizes: default (12px 22px), `btn-sm` (7px 14px), `btn-lg` (16px 32px), `btn-full` (width 100%).

## 3.2 — Cards

```css
.card           /* white bg, border, shadow-card, r-xl, sp-5 sp-6 padding */
.card-purple    /* --purple bg, white text */
.card-lime      /* --lime-tint bg, lime border */
.card-warning   /* --warning-tint bg, orange border */
.card-danger    /* --danger-tint bg, red border */
.card-elevated  /* shadow-raised */
```

## 3.3 — Nav Items

```css
.nav-item {
  display: flex; align-items: center; gap: var(--sp-3);
  padding: 11px var(--sp-4); border-radius: var(--r-lg);
  color: rgba(255,255,255,.7);
  font-size: var(--text-base); font-weight: 600;
}
.nav-item:hover { background: rgba(255,255,255,.06); color: #fff; }
.nav-item.active { background: var(--lime); color: var(--purple); font-weight: 800; }
```

## 3.4 — Notification Badge (Fix 5)

**Spec:** Lime-green badge positioned top-right of the nav icon. App-icon badge style — NOT an inline tag.

```jsx
<span className="nav-icon" style={{ position: 'relative', display: 'inline-flex' }}>
  {icon}
  {badge > 0 && (
    <span style={{
      position: 'absolute', top: -7, right: -7,
      background: 'var(--lime)', color: 'var(--lime-text)',
      fontSize: 9, fontWeight: 900,
      minWidth: 16, height: 16,
      borderRadius: 99,
      display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
      padding: '0 3px',
      border: '2px solid var(--purple)',
    }}>
      {badge}
    </span>
  )}
</span>
```

Rules:
- Color: `var(--lime)` (not red — low contrast against purple nav bg)
- Text: `var(--lime-text)` (#3A5200) — WCAG AA compliant on lime
- Min size: 16px
- Position: top-right of icon, overlapping
- Border: 2px `var(--purple)` cutout creates visual separation from nav bg
- Hide when count = 0
- Appears on: Suggestions nav item in planning and active phases

## 3.5 — Activity Cards (Itinerary)

Three variants:

**duo (default):** Large icon wrap left, name + reason + tag row. 6px left border in category color.

**timeline:** Icon above time left column, name + reason right. Tall left border.

**compact:** Small icon, name only (no reason text). Minimal padding.

All variants: position relative for 3-dot menu anchor.

**3-dot menu (admin only, planning phase):**

```
⋯ trigger (32×32 circle, top-right of card, appears on hover)
↓
Dropdown (absolute, 180px min-width, z-index 50)
  ✏️ Edit
  🔄 Suggest swap
  🗑️ Remove (danger color)
```

## 3.6 — Save Buttons

**Rule:** Save buttons are anchored to the bottom of their section content. Not floating, not sticky. Rendered as last element before the closing div of each editable section.

Applies to:
- Each tab of the Profile page (About me, Food & diet, How I travel, Passport & visas)
- Budget editor (itinerary right rail)
- Activity edit mode (future)

```jsx
{/* Save button — anchored to bottom of section content */}
<div style={{ marginTop: 24, paddingTop: 16, borderTop: '1px solid var(--border-light)' }}>
  <button className="btn btn-primary" onClick={() => alert('Saved (demo)')}>
    Save changes
  </button>
</div>
```

## 3.7 — Rec Cards

```css
.rec-card         /* white bg, 2px border, r-xl, cursor pointer */
.rec-card:hover   /* border --purple-mid, translateY(-2px), shadow-raised */
.rec-card.selected { border-color: var(--purple-mid); background: var(--purple-tint); }
.rec-card.recommended { border-color: var(--lime-dark); }
```

Recommended badge: lime pill, top-left overhang, `top: -12px; left: sp-5`.

## 3.8 — Tags

```css
.tag            /* inline-flex, r-pill, xs text, 700 weight, 3px 10px padding */
.tag-purple     /* --purple-tint bg, --purple-mid text */
.tag-lime       /* --lime-tint bg, --lime-text, lime-dark border */
.tag-orange     /* --orange-tint bg, amber text */
.tag-success    /* --success-tint bg, success text */
.tag-warning    /* --warning-tint bg, warning text */
.tag-danger     /* --danger-tint bg, danger-text */
.tag-ghost      /* transparent bg, secondary text, border */
```

## 3.9 — Bounce FAB

64×64 circle, positioned `bottom: sp-8; right: sp-8`. Mascot PNG as background. Lime ring border (3px solid var(--lime)).

**Alert state:** Pulsing lime ring animation (`pulse-ring`, 1.8s).

```css
.bounce-fab.has-alert::before {
  content: ''; position: absolute; inset: -6px;
  border-radius: 50%; border: 2px solid var(--lime);
  animation: pulse-ring 1.8s ease infinite;
}
@keyframes pulse-ring {
  0%  { transform: scale(.92); opacity: .8; }
  70% { transform: scale(1.3); opacity: 0; }
  100%{ opacity: 0; }
}
```

## 3.10 — Judge / Demo Controls Panel (Fix 2)

Draggable panel, bottom-left initial position. `z-index: var(--z-judge)` (500).

**States:** Open (full panel) → Collapsed (lime pill "⚡ Demo controls"). Toggle via × button.

```css
.judge-panel {
  position: fixed; /* x/y via inline style */
  background: var(--purple); color: #fff;
  border-radius: var(--r-xl); padding: var(--sp-3);
  z-index: var(--z-judge); border: 2px solid var(--lime);
  box-shadow: var(--shadow-float);
  min-width: 240px; user-select: none;
}
.judge-panel-grip { cursor: grab; }
.judge-panel-grip:active { cursor: grabbing; }
```

Label: `⚡ Demo controls · drag me`

Contents: role selector (Organiser / Co-leader / Member), phase selector, Trigger disruption button, Reset demo button.

---

# Part 4 — Layout System

## 4.1 — App Shell

```css
.app-shell {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  min-height: 100vh;
}
```

## 4.2 — Sidebar

```
Sidebar (240px, position: sticky, height: 100vh, --purple bg)
  sidebar-brand      ← Logomark
  nav-items          ← top-level OR trip-scoped
  sidebar-trip-card  ← (when inTrip) phase label + trip name
  sidebar-footer     ← user pill (MemberAvatar + name + role)
```

Trip context card: 3px lime left-border, rgba(255,255,255,.06) bg.

## 4.3 — Page Layouts

```css
.page-body     { padding: sp-8 sp-8 sp-12; max-width: 1320px; margin: 0 auto; }
.layout-3col   { grid-template-columns: 220px minmax(0, 1fr) 300px; }
.layout-2col   { grid-template-columns: minmax(0, 1fr) 340px; }
```

## 4.4 — Mobile Responsive

Breakpoints (match prototype exactly):

| ≥ 1280px | 900–1280px | < 900px |
|---|---|---|
| Full 3-col | Itinerary 2-col, right rail below | Sidebar drawer, all stacked 1-col |

```css
@media (max-width: 900px) {
  .app-shell { grid-template-columns: 1fr; }
  .sidebar {
    position: fixed; left: 0; top: 0; width: 280px;
    transform: translateX(-100%);
    transition: transform 260ms cubic-bezier(.4,0,.2,1);
    z-index: 200;
  }
  .sidebar.open { transform: translateX(0); }
  .mobile-topbar { display: flex !important; }
  .page-body { padding: 16px !important; }
  .trip-cover { height: 160px; }
  .trips-row { grid-template-columns: 1fr; }
  .disruption-sheet { max-width: 100% !important; border-radius: 0; min-height: 100vh; }
  .bounce-panel { width: 100vw; }
}
.mobile-topbar { display: none; } /* hidden on desktop */
```

Mobile top bar: 40px burger button + Logomark sm + Ask Bounce icon.

---

# Part 5 — Screen Component Trees

## 5.1 — Home

```
HomeScreen
  PageBody
    button.home-plan-new (deep-purple gradient)
      .home-plan-new-icon (lime square, + glyph, 56px)
      .home-plan-new-body
        .home-plan-new-title "Plan a new trip"
        .home-plan-new-sub "Your trip starts here. Tell me what you've got in mind."
      .home-plan-new-arrow →
    SectionLabel "Upcoming trips" (if any)
    .trips-row
      TripCard × N (planning state)
    SectionLabel "On the road right now" (if any)
    .trips-row
      TripCard × N (active state)
    SectionLabel "Past trips" (if any)
    .trips-row
      TripCard × N (past state)
```

**TripCard:**
```
.trip-card (button, white bg, overflow: hidden)
  .trip-cover (180px, gradient fallback, cover image)
    .trip-state-badge (top-left)
      tag.tag-lime "In planning"     ← planning
      tag.orange "● Day X/Y"         ← active
      tag.ghost "⭐ 4.9"             ← past
  .trip-meta
    row: .trip-name + days-to-go (planning only)
    row: dates + city
    AvatarStack (max 5)
```

## 5.2 — Itinerary

```
ItineraryScreen
  PageBody
    .layout-3col
      [Left] DayNavRail
        DayButton × totalDays (active state = lime bg)
      [Center] col
        row: ViewToggleChips + TripInfoBadge
        DayHeader (date, weather, label)
        BounceSay (day intro)
        col.gap-3
          ActivityCard × items (variant = cardVariant)
            ActivityCardMenu (3-dot, admin only)
      [Right] col
        BudgetCard
          [collapsed] label + amount/cap + ProgressBar + Edit btn
          [expanded]
            label "Edit budget" + Cancel + Save budget btn
            input: Trip total per person ($)
            input: Daily cap ($)
            BounceSay (calculation note)
            button.btn-primary "Save budget"  ← Fix 4
        MapPlaceholder or MapCard
```

## 5.3 — Profile

```
ProfilePageFull
  PageBody
    .layout-2col
      [Left 200px] col.gap-1
        TabButton × 5 (active = lime tint + purple text)
      [Right] col
        [tab = 'about']   ProfileTabAbout + SaveBtn  ← Fix 4
        [tab = 'dietary'] ProfileTabDietary + SaveBtn  ← Fix 4
        [tab = 'interests'] ProfileTabInterests + SaveBtn  ← Fix 4
        [tab = 'trips']   ProfileTabTrips (read-only, no save btn)
        [tab = 'compliance'] ProfileTabCompliance + SaveBtn  ← Fix 4
```

**SaveBtn (Fix 4):**
```jsx
<div style={{ marginTop: 24, paddingTop: 16, borderTop: '1px solid var(--border-light)' }}>
  <button className="btn btn-primary">Save changes</button>
</div>
```

## 5.4 — Wrap (Post-Trip)

```
WrapScreen (trip-aware via WRAP_DATA[trip.id])
  PageBody
    col.gap-5
      TripTitle + subtitle
      .card.card-purple (hero stats)
        row:
          col: label "Total spent" + .t-display (currencySymbol + amount) + per-person note
          col: label "Highlights" + highlight rows
      .grid-2col
        .card "By category"
          CategoryBar × categories (local currency symbol + %)
          BounceSay (trip insight)
        .card "Settle up"
          SettlementRow × settlements
            MemberAvatar → MemberAvatar
            name pays name · amount (local currency)
          settled-all badge (if settledAll = true)
      BounceSay.purple (follow-up trip suggestion)
```

---

# Part 6 — Navigation Patterns

## 6.1 — Sidebar Context Switch

When `inTrip = false`: show top-level nav (Home, Plan, Join).
When `inTrip = true`: show `← All trips` + trip context card + phase-appropriate items.

The trip context card shows `currentTrip.name · currentTrip.city` dynamically (not hardcoded).

## 6.2 — Mobile Drawer

At < 900px, sidebar transforms to a slide-in drawer. Opens via ☰ burger button in mobile top bar. Closed via backdrop tap or any nav item click.

Backdrop: `rgba(0,0,0,.4)`, z-index 150.

---

# Part 7 — Bounce Assistant

## 7.1 — Chat Panel

Slide-in from right, 440px width (full-width on mobile < 900px). Z-index 200.

```
.bounce-panel
  .bounce-panel-header (--purple bg)
    BounceAvatar
    name "Bounce" + role permission label
    × close button
  .bounce-msg-stream (flex-1, overflow-y auto)
    msg.msg-bounce | msg.msg-user × N
  .bounce-input-area
    .pill-input-bar
      input (placeholder: "Ask Bounce anything…")
      button.pill-submit-btn ↑
```

Permission label by role:
- Organiser/Co-leader: "Changes apply directly"
- Flock leader: "Flock changes apply directly · main suggestions logged"
- Member: "Suggestions logged for organiser"

## 7.2 — BounceSay (contextual)

Inline callout inside screen content. Three variants: default (lime), purple, danger.

```css
.bounce-say {
  display: flex; align-items: flex-start; gap: var(--sp-3);
  padding: var(--sp-4) var(--sp-5);
  background: var(--lime-tint); border-left: 4px solid var(--lime-dark);
  border-radius: 0 var(--r-lg) var(--r-lg) 0;
}
.bounce-say.purple { background: var(--purple-tint); border-left-color: var(--purple-mid); }
.bounce-say.danger { background: var(--danger-tint); border-left-color: var(--danger); }
```

## 7.3 — FAB Spec

See Part 3.9. Uses mascot PNG background. Alert state = pulsing lime ring.

---

# Part 8 — Future Feature Placeholders

## 8.1 — FlockMode Photo Sharing [NOT BUILT]

Placeholder rendered inside FlockActiveScreen:
```jsx
<div className="card" style={{ borderStyle: 'dashed', background: 'var(--bg-raised)', textAlign: 'center', padding: 24 }}>
  <div style={{ fontSize: 32 }}>📸</div>
  <p style={{ fontWeight: 700, marginTop: 8 }}>Photo sharing coming soon</p>
  <p className="t-caption mt-2">Share live photos with your Flock during the adventure.</p>
</div>
```

Visual spec for when built:
- Grid of 2–3 thumbnails per Flock
- Upload FAB: camera icon, lime background
- Privacy toggle: "My Flock only" / "Everyone"
- Consent prompt on first upload
- Storage: Firebase Storage / GCS (to be decided)

**⚠️ AI gate:** Do not build without explicit authorization. See PRD v5 §6.10.

## 8.2 — Multi-City Trips [NOT BUILT]

Current trips use single city. Multi-city: extend `cities[]` array on trip object. Itinerary would need city header breaks between days.

City switcher in itinerary: pills above day nav rail.

---

# Part 9 — Accessibility

```css
*:focus-visible {
  outline: 2.5px solid var(--purple-mid);
  outline-offset: 2px;
  border-radius: 4px;
}
```

## 9.1 — Contrast Ratios (WCAG AA)

| Combination | Ratio | Pass |
|---|---|---|
| `--purple` on white | 12.4:1 | ✓ |
| White on `--purple` | 12.4:1 | ✓ |
| `--lime-text` on `--lime` | 5.1:1 | ✓ |
| `--lime` on `--purple` | 5.8:1 | ✓ (logo, FAB) |
| `--purple-mid` on white | 6.7:1 | ✓ |
| `--text-secondary` on white | 4.8:1 | ✓ |

## 9.2 — Required ARIA

| Component | ARIA |
|---|---|
| Bounce chat panel | `role="dialog" aria-label="Bounce assistant" aria-modal="true"` |
| Nav badge | `aria-label="N pending suggestions"` |
| Logomark img | `alt="Bounce"` |
| FAB | `aria-label="Chat with Bounce"` |
| Loading state | `aria-live="polite"` |

---

# Part 10 — Brand Voice & Copy Guidelines

## 10.1 — Brand Personality

| Bounce IS | Bounce is NOT |
|---|---|
| Warm · Socially intelligent · Clear | Corporate · Technical · Productivity-sounding |
| Optimistic · Collaborative · Decisive | Robotic · Overly Gen Z or meme-heavy |
| Playful (restrained) · Modern | Trying too hard · Apologetic |

## 10.2 — Writing Principles

1. **Clarity over cleverness** — instant comprehension first.
2. **Write emotionally, not technically** — how planning feels, not backend complexity.
3. **Keep copy short and airy** — short paragraphs, let the UI explain.
4. **Avoid overusing "AI"** — Bounce feels magical, not technical.
5. **Make it collaborative** — groups, friends, together. Not solo.

## 10.3 — UX Copy Reference

| Context | Copy |
|---|---|
| App tagline | "Plan trips together, without the chaos." |
| Entry placeholder | "Your trip starts here. Tell me what you've got in mind." |
| Entry CTA | "Ready to bounce →" |
| Bounce thinking | "Organising everyone's ideas ●●●" |
| Disruption CTA | "Lock this in & ping everyone →" |
| Disruption cancel | "Not now" |
| Members header | "Who's going" |
| Apply suggestion | "Lock this in & ping everyone →" |
| Sidebar: active trip | "On the trip" |
| Sidebar: post-trip | "Wrapped" |
| Confirmation CTA | "Continue planning →" / "Start planning →" |
| Reset | "↻ Reset demo" |

## 10.4 — Loading States

| Context | Copy |
|---|---|
| Generating itinerary | "Organising everyone's ideas…" |
| Finding flights | "Finding the best options for your group…" |
| Bounce thinking | "Organising everyone's ideas ●●●" |
| Empty suggestions | "No suggestions yet. Trip looks great." |
| Empty home | "Your trips will appear here. Ready to bounce?" |

## 10.5 — Bounce Persona

> "The friend who somehow keeps the whole trip together."

- Short sentences. Explains why, not just what.
- Celebrates wins. Admits uncertainty.
- Never says "Certainly!" or "Of course!"
- Speaks before the user asks. Notices things.
- Visual: deep purple avatar, lime "B". Messages in off-white bubble.

---

# Part 11 — Animation & Motion

```css
/* Entry: subtle fade-up */
.fade-up { animation: fadeUp 280ms ease; }
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }

/* Staggered children */
.stagger > *:nth-child(1){animation-delay:0ms}
.stagger > *:nth-child(2){animation-delay:60ms}
.stagger > *:nth-child(3){animation-delay:120ms}

/* Skeleton shimmer */
.skeleton {
  background: linear-gradient(90deg, var(--border-light) 0%, var(--bg-raised) 50%, var(--border-light) 100%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease infinite;
}
@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }

/* Firebase sync flash */
.firebase-flash { animation: flashUpdate 900ms ease; }
@keyframes flashUpdate { 0%,100%{background:inherit} 30%,70%{background:var(--lime-tint)} }
```

---

# Part 12 — Icon Reference

CDN: `https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css`

| Feature | Icon | Feature | Icon |
|---|---|---|---|
| Home | `ti-home` | Itinerary | `ti-map-2` |
| Today | `ti-calendar-today` | Bounce/Chat | `ti-message-circle-2` |
| Expenses | `ti-receipt-2` | Profile | `ti-user` |
| Alerts | `ti-bell` | Flights | `ti-plane` |
| FlockMode | `ti-feather` | Disruption | `ti-alert-triangle` |
| Budget | `ti-wallet` | Expense | `ti-coin` |
| Map pin | `ti-map-pin` | Group | `ti-users-group` |
| Co-leader | `ti-crown` | Flock leader | `ti-star` |
| Back | `ti-arrow-left` | Close | `ti-x` |
| Judge mode | `ti-bolt` | Settings | `ti-settings` |

---

*Bounce Design System v5.0 — May 2026*
*Mobile-first · Responsive · Light mode · Google Cloud Rapid Agent Hackathon 2026*
*Consolidates: Design System v3.0 + v5 changes summary*
