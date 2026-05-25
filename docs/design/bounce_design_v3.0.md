# Bounce — Design System v3.0
**Desktop-first · Light mode only · Google Cloud Rapid Agent Hackathon 2026**

> For Biz 1, Biz 2, and CS engineers. This is the single source of truth for all UI.
>
> **v3.0 ground-up rewrite.** Old Yale Blue/Lemon Chiffon system removed. Dark mode removed. Mobile-specific layout removed. New colour palette from landing page. New font system. Itinerary screen rebuilt (Duolingo-inspired). Screen 12 merged into Screen 11. Travel DNA, receipt scanning, packing list, trip narrative, multi-language, cultural briefing, and GPS tracking removed.
>
> `bounce_prd_v2.md` is still source of truth for tool contracts, schemas, and algorithms. This document is source of truth for all UI styling, screens, flows, and copy.

---

# PART 0 — VISUAL IDENTITY

## 0.1 — The Bounce Logomark

Rounded square app-icon in deep purple. Bold lowercase **b** in lime-yellow. Small filled circle upper-right connected by dashed arc — the trajectory of a bounce.

**SVG logomark** — save as `public/logo.svg`:

```svg
<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Bounce">
  <rect width="40" height="40" rx="9" fill="#1A0A6B"/>
  <text x="9" y="29" font-family="'Baloo 2', cursive"
        font-weight="800" font-size="24" fill="#C8E64A">b</text>
  <circle cx="29" cy="10" r="4" fill="#C8E64A"/>
  <path d="M22 22 Q26 14 27 12" stroke="#C8E64A" stroke-width="1.5"
        fill="none" stroke-dasharray="2 3" stroke-linecap="round" opacity="0.6"/>
</svg>
```

## 0.2 — Wordmark

```css
.bounce-wordmark { display: flex; align-items: center; gap: 8px; }
.bounce-wordmark span {
  font-family: var(--font-logo);
  font-size: 22px; font-weight: 800;
  color: var(--text-primary); letter-spacing: -0.5px;
}
```

## 0.3 — Brand Mark Sizes

| Context | Size | Notes |
|---|---|---|
| Favicon | 16×16, 32×32 | favicon.ico / favicon.svg |
| PWA icon | 192×192, 512×512 | icon-192.png, icon-512.png — for "Add to Home Screen" |
| App header | 32×32 | Inline SVG with wordmark beside it |
| Bounce avatar | 40×40 | Rendered CSS — `.bounce-avatar` |
| Entry hero avatar | 64×64 | Rendered CSS — `.bounce-avatar-lg` |

## 0.4 — PWA Manifest

Paste into `/public/manifest.json`. Makes the app installable on desktop and mobile home screens.

```json
{
  "name": "Bounce",
  "short_name": "Bounce",
  "description": "Group travel planning, together.",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#FFFFFF",
  "theme_color": "#1A0A6B",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

## 0.5 — Bounce Persona

Bounce is a competent, energetic travel-obsessed friend. Not a robot. Not an assistant.

| Dimension | Description |
|---|---|
| Voice | Short sentences. Explains why, not just what. Celebrates wins. Admits uncertainty. |
| Visual | Deep purple avatar, lime-yellow letter B. Messages in warm off-white (#F7F7F2) bubble. |
| Behaviour | Speaks before the user asks. Notices things. Never says "Certainly!" or "Of course!" |
| Avatar rule | Never use a generic icon. Always use `.bounce-avatar` CSS component. |

---

# PART 1 — DESIGN TOKENS

Paste this entire block at the top of `style.css`. Use only these variables — never raw hex values in component CSS.

## 1.1 — Colour Palette

Extracted directly from the Bounce landing page. Deep purple is primary. Lime-yellow is the primary accent. Orange-yellow is the CTA/energy colour. No Yale Blue. No Lemon Chiffon. No dark mode.

```css
:root {
  /* ── Brand ── */
  --purple:        #1A0A6B;   /* primary — nav, headers, CTAs, avatar */
  --purple-mid:    #4A2FC4;   /* interactive — buttons, links, focus */
  --purple-light:  #6B50E8;   /* hover states */
  --purple-tint:   #EDE9FF;   /* bg tint on purple surfaces */

  /* ── Accent — Lime ── */
  --lime:          #C8E64A;   /* primary accent — badges, active chips, add button */
  --lime-dark:     #8DC63F;   /* deeper lime — feature bg, hover */
  --lime-tint:     #F0FFD4;   /* light lime bg for callouts */
  --lime-text:     #3A5200;   /* text ON lime surfaces — WCAG AA */

  /* ── Accent — Orange/Energy ── */
  --orange:        #F47B20;   /* CTA sections, energy moments */
  --orange-yellow: #FBBF24;   /* gradient pair with orange */
  --orange-tint:   #FFF7ED;   /* light orange bg */

  /* ── Gradient orbs (decorative only) ── */
  --orb-1: radial-gradient(circle at 40% 40%, #F47B20 0%, #E84040 100%);
  --orb-2: radial-gradient(circle at 40% 40%, #F9C6D4 0%, #FBBF8C 100%);
  --orb-3: radial-gradient(circle at 35% 35%, #14B8A6 0%, #8DC63F 100%);
  --orb-4: radial-gradient(circle at 40% 40%, #A855F7 0%, #7C3AED 100%);

  /* ── Semantic ── */
  --success:       #16A34A;
  --success-tint:  #F0FDF4;
  --warning:       #D97706;
  --warning-tint:  #FFF7ED;
  --danger:        #DC2626;
  --danger-tint:   #FEF2F2;
  --danger-text:   #7F1D1D;

  /* ── Activity category colours (itinerary only) ── */
  --cat-food:      #F47B20;   /* restaurants, cafes */
  --cat-culture:   #7C3AED;   /* museums, temples, art */
  --cat-nature:    #16A34A;   /* parks, outdoors */
  --cat-transport: #1A0A6B;   /* transit, flights, transfers */
  --cat-shopping:  #EC4899;   /* markets, malls */
  --cat-hotel:     #C8E64A;   /* accommodation */
  --cat-nightlife: #4A2FC4;   /* bars, clubs */
  --cat-wellness:  #0D9488;   /* spa, gym */

  /* ── Neutral ── */
  --bg-page:       #F8F8F8;
  --bg-card:       #FFFFFF;
  --bg-raised:     #FAFAFA;

  /* ── Text ── */
  --text-primary:  #1A1A2E;
  --text-secondary:#6B7280;
  --text-tertiary: #9CA3AF;
  --text-inverse:  #FFFFFF;

  /* ── Borders ── */
  --border-light:  #E5E7EB;
  --border-medium: #D1D5DB;
  --border-strong: #9CA3AF;

  /* ── Typography ── */
  --font-logo:     'Baloo 2', cursive;
  --font-display:  'Nunito', 'Outfit', sans-serif;
  --font-sans:     'Nunito', 'Outfit', sans-serif;
  --font-mono:     'SF Mono', 'Fira Code', monospace;

  /* ── Type scale ── */
  --text-xs:   11px;   /* labels, tags, timestamps */
  --text-sm:   13px;   /* captions, secondary info */
  --text-base: 15px;   /* body text, default */
  --text-md:   17px;   /* subheadings, card titles */
  --text-lg:   20px;   /* section headings */
  --text-xl:   24px;   /* screen titles */
  --text-2xl:  30px;   /* hero numbers, expense amounts */
  --text-3xl:  40px;   /* large numeric display */

  /* ── Leading ── */
  --leading-tight:   1.25;
  --leading-normal:  1.5;
  --leading-relaxed: 1.7;

  /* ── Spacing ── */
  --sp-1:  4px;   --sp-2:  8px;   --sp-3:  12px;  --sp-4:  16px;
  --sp-5:  20px;  --sp-6:  24px;  --sp-8:  32px;  --sp-10: 40px;
  --sp-12: 48px;  --sp-16: 64px;

  /* ── Border radius ── */
  --r-xs:   4px;   --r-sm:   8px;   --r-md:  12px;  --r-lg:  16px;
  --r-xl:   20px;  --r-2xl:  24px;  --r-pill: 99px;

  /* ── Shadows ── */
  --shadow-card:   0 1px 4px rgba(0,0,0,.06), 0 0 0 .5px rgba(0,0,0,.04);
  --shadow-raised: 0 4px 12px rgba(0,0,0,.08);
  --shadow-float:  0 8px 24px rgba(26,10,107,.12);
  --shadow-bounce: 0 4px 20px rgba(26,10,107,.3);

  /* ── Z-index ── */
  --z-nav:     100;
  --z-chat:    200;
  --z-overlay: 300;
  --z-toast:   400;
  --z-judge:   500;

  /* ── Transitions ── */
  --t-fast:   120ms ease;
  --t-normal: 200ms ease;
  --t-slow:   300ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

## 1.2 — Token Usage Rules

| Token | When to use | Never use for |
|---|---|---|
| `--purple` | Primary CTAs, nav bg, avatar bg, section headers | Body text on white |
| `--purple-mid` | Buttons, links, active states, submit arrow | Large background fills |
| `--lime` | Active chips, add buttons, badges, recommended tag | Error or warning states |
| `--lime-text` | Text ON lime surfaces only — `#3A5200` | Anything not on lime bg |
| `--orange` | CTA blob, energy moments, disruption accent | Standard UI actions |
| `--cat-*` | Itinerary activity category colour coding only | Any other UI purpose |
| `--success` | Confirmed, booked, joined states | General positive feedback |
| `--warning` | Pending, estimated data, moderate alerts | Errors |
| `--danger` | Disruption, cancellation, errors | Warnings or pending |

## 1.3 — Member Avatar Colour System

10 members need distinct, non-clashing avatar backgrounds. Assign by index (0–9) in join order.

```javascript
const MEMBER_COLOURS = [
  { bg: '#1A0A6B', text: '#C8E64A' },  // 0 — deep purple / lime
  { bg: '#F47B20', text: '#FFFFFF' },  // 1 — orange
  { bg: '#7C3AED', text: '#FFFFFF' },  // 2 — violet
  { bg: '#16A34A', text: '#FFFFFF' },  // 3 — green
  { bg: '#EC4899', text: '#FFFFFF' },  // 4 — pink
  { bg: '#0D9488', text: '#FFFFFF' },  // 5 — teal
  { bg: '#C8E64A', text: '#1A0A6B' },  // 6 — lime / purple text
  { bg: '#D97706', text: '#FFFFFF' },  // 7 — amber
  { bg: '#4A2FC4', text: '#FFFFFF' },  // 8 — mid-purple
  { bg: '#E84040', text: '#FFFFFF' },  // 9 — red
];
// Usage: member.avatar { background: MEMBER_COLOURS[member.joinIndex % 10].bg }
```

---

# PART 2 — TYPOGRAPHY

## 2.1 — Font Stack

| Role | Primary | Alternative 1 | Alternative 2 |
|---|---|---|---|
| Logo / Wordmark | Baloo 2 (wt 800) | Baloo 2 only — no fallback for logo | — |
| Headings / Display | Nunito (wt 800) | Outfit (wt 800) | DM Sans (wt 800) |
| Body / UI | Nunito (wt 400, 500, 600) | Outfit (wt 400, 500, 600) | DM Sans (wt 400, 500, 600) |

## 2.2 — Google Fonts Import (Nunito — recommended)

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@800&family=Nunito:wght@400;500;600;800&display=swap" rel="stylesheet">
```

## 2.3 — Alternative: Outfit

```html
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@800&family=Outfit:wght@400;500;600;800&display=swap" rel="stylesheet">
```

Then swap `--font-display` and `--font-sans` to `'Outfit'` in the token block.

## 2.4 — Type Utility Classes

```css
body {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--text-primary);
  background: var(--bg-page);
  line-height: var(--leading-normal);
  -webkit-font-smoothing: antialiased;
}

h1, h2, h3, .t-hero, .t-heading, .t-display {
  font-family: var(--font-display);
  font-weight: 800;
}

.t-display { font-size: var(--text-3xl); line-height: 1.1; letter-spacing: -1px; }
.t-hero    { font-size: var(--text-xl);  line-height: var(--leading-tight); letter-spacing: -0.5px; }
.t-heading { font-size: var(--text-lg);  line-height: var(--leading-tight); letter-spacing: -0.2px; }
.t-title   { font-size: var(--text-md);  font-weight: 600; line-height: var(--leading-tight); }
.t-body    { font-size: var(--text-base);font-weight: 400; line-height: var(--leading-relaxed); }
.t-caption { font-size: var(--text-sm);  color: var(--text-secondary); }
.t-label   { font-size: var(--text-xs);  font-weight: 600; letter-spacing: 0.07em; text-transform: uppercase; color: var(--text-tertiary); }
.t-mono    { font-family: var(--font-mono); font-size: var(--text-sm); }
```

| Screen context | Class |
|---|---|
| Screen title | `.t-hero` |
| Section heading | `.t-heading` |
| Card title | `.t-title` |
| Body paragraph | `.t-body` |
| Secondary info | `.t-caption` |
| Tags, timestamps | `.t-label` |
| Large amounts | `.t-display` |
| Bounce messages | `.t-body` (main) / `.t-caption` (contextual) |

---

# PART 3 — LAYOUT & NAVIGATION

> **Desktop-first.** Max content width 1280px. Sidebar navigation on the left. No bottom nav bar — mobile out of scope for now.

## 3.1 — Desktop Page Shell

```css
.app-shell {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 100vh;
  max-width: 1280px;
  margin: 0 auto;
  background: var(--bg-page);
}
.sidebar      { grid-column: 1; background: var(--purple); padding: var(--sp-6) var(--sp-4); }
.main-content { grid-column: 2; padding: var(--sp-8); overflow-y: auto; }
```

## 3.2 — Sidebar Navigation

```css
.sidebar-logo {
  font-family: var(--font-logo); font-size: 24px; font-weight: 800;
  color: var(--text-inverse); letter-spacing: -0.5px;
  margin-bottom: var(--sp-8);
}
.sidebar-logo .accent { color: var(--lime); }

.nav-item {
  display: flex; align-items: center; gap: var(--sp-3);
  padding: var(--sp-3) var(--sp-4); border-radius: var(--r-lg);
  color: rgba(255,255,255,0.6); font-size: var(--text-base); font-weight: 500;
  cursor: pointer; transition: all var(--t-fast);
  text-decoration: none; margin-bottom: var(--sp-1);
}
.nav-item:hover        { background: rgba(255,255,255,0.08); color: white; }
.nav-item.active       { background: var(--lime); color: var(--purple); font-weight: 700; }
.nav-item.active .nav-icon { color: var(--purple); }
.nav-icon { font-size: 20px; }
```

## 3.3 — Phase-Adaptive Sidebar

| Phase | Nav items |
|---|---|
| `data-phase="planning"` | Home · Group · Itinerary · Visa · Profile |
| `data-phase="active"` | Today · Map · Bounce · Expenses · Alerts |
| `data-phase="post"` | Home · Summary · Settlement · Profile |

```javascript
function setPhase(phase) {
  document.querySelector('.sidebar').dataset.phase = phase;
}
// 'planning' → entry conversation complete
// 'active'   → departure date reached
// 'post'     → return date reached
```

## 3.4 — Top Bar

```css
.top-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--sp-4) var(--sp-8);
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-light);
  position: sticky; top: 0; z-index: var(--z-nav);
}
.top-bar-title {
  font-family: var(--font-display); font-weight: 800;
  font-size: var(--text-xl); color: var(--text-primary);
}
```

---

# PART 4 — CORE COMPONENTS

## 4.1 — Cards

```css
.card {
  background: var(--bg-card); border-radius: var(--r-xl);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-card);
  padding: var(--sp-5) var(--sp-6);
  margin-bottom: var(--sp-4);
}
.card-purple  { background: var(--purple); color: white; border: none; }
.card-lime    { background: var(--lime-tint); border-color: var(--lime-dark); }
.card-warning { background: var(--warning-tint); border-color: var(--warning); }
.card-danger  { background: var(--danger-tint); border-color: var(--danger); border-width: 1.5px; }
.card-elevated { box-shadow: var(--shadow-raised); }
```

## 4.2 — Progress Bar

One component used across all progress contexts: group join %, day budget, profile steps, trip budget.

```css
.progress-wrap  { display: flex; flex-direction: column; gap: var(--sp-2); }
.progress-label {
  display: flex; justify-content: space-between;
  font-size: var(--text-sm); font-weight: 600; color: var(--text-secondary);
}
.progress-track {
  width: 100%; height: 10px;
  background: var(--border-light);
  border-radius: var(--r-pill);
  overflow: hidden;
}
.progress-fill {
  height: 100%; border-radius: var(--r-pill);
  background: linear-gradient(90deg, var(--purple-mid) 0%, var(--lime) 100%);
  transition: width var(--t-slow);
}

/* State variants */
.progress-fill.success { background: linear-gradient(90deg, #16A34A 0%, var(--lime) 100%); }
.progress-fill.warning { background: linear-gradient(90deg, var(--orange) 0%, var(--orange-yellow) 100%); }
.progress-fill.danger  { background: linear-gradient(90deg, var(--danger) 0%, #F87171 100%); }
```

| Context | State |
|---|---|
| Group join % | Default (purple → lime). Label: "7 of 10 joined" |
| Profile steps | Default. Label: "Step 2 of 3" |
| Day budget < 60% | Default |
| Day budget 60–80% | `.warning` |
| Day budget 80%+ | `.danger` |

```html
<!-- Usage pattern -->
<div class="progress-wrap">
  <div class="progress-label">
    <span>7 of 10 joined</span>
    <span>70%</span>
  </div>
  <div class="progress-track">
    <div class="progress-fill" style="width: 70%"></div>
  </div>
</div>
```

## 4.3 — Buttons

```css
.btn {
  display: inline-flex; align-items: center; justify-content: center;
  gap: var(--sp-2); padding: 12px 24px; border-radius: var(--r-xl);
  font-family: var(--font-sans); font-size: var(--text-base); font-weight: 700;
  cursor: pointer; transition: all var(--t-fast); border: none;
  text-decoration: none; white-space: nowrap;
}
.btn-primary { background: var(--purple-mid); color: white; }
.btn-primary:hover  { background: var(--purple-light); transform: translateY(-1px); }
.btn-primary:active { transform: scale(0.98); }
.btn-lime    { background: var(--lime); color: var(--purple); }
.btn-lime:hover    { background: var(--lime-dark); color: white; }
.btn-outline { background: transparent; color: var(--purple-mid); border: 2px solid var(--purple-mid); }
.btn-outline:hover { background: var(--purple-tint); }
.btn-ghost   { background: transparent; color: var(--text-secondary); border: 1.5px solid var(--border-light); }
.btn-ghost:hover   { border-color: var(--border-medium); color: var(--text-primary); }
.btn-danger  { background: var(--danger); color: white; }
.btn-sm   { padding: 8px 16px; font-size: var(--text-sm); border-radius: var(--r-lg); }
.btn-lg   { padding: 16px 36px; font-size: var(--text-md); border-radius: var(--r-xl); }
.btn-full { width: 100%; }
```

## 4.4 — Chips & Tags

```css
/* Selectable chip */
.chip {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 8px 16px; border-radius: var(--r-pill);
  font-size: var(--text-sm); font-weight: 600;
  border: 2px solid var(--border-light);
  background: var(--bg-card); color: var(--text-secondary);
  cursor: pointer; transition: all var(--t-fast); user-select: none;
}
.chip:hover    { border-color: var(--purple-mid); color: var(--purple); }
.chip.selected { border-color: var(--lime-dark); background: var(--lime-tint); color: var(--lime-text); }
.chip.selected::before { content: '✓ '; font-size: 11px; }

/* Status tag */
.tag {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 10px; border-radius: var(--r-pill);
  font-size: var(--text-xs); font-weight: 700; white-space: nowrap;
}
.tag-purple  { background: var(--purple-tint);  color: var(--purple-mid); }
.tag-lime    { background: var(--lime-tint);    color: var(--lime-text); border: 1px solid var(--lime-dark); }
.tag-orange  { background: var(--orange-tint);  color: #92400E; }
.tag-success { background: var(--success-tint); color: var(--success); }
.tag-warning { background: var(--warning-tint); color: var(--warning); }
.tag-danger  { background: var(--danger-tint);  color: var(--danger-text); }
```

## 4.5 — Inputs & Form Elements

```css
.input {
  width: 100%; padding: 12px 16px; border-radius: var(--r-lg);
  border: 2px solid var(--border-light); background: var(--bg-card);
  font-family: var(--font-sans); font-size: var(--text-base);
  color: var(--text-primary); outline: none;
  transition: border-color var(--t-fast);
}
.input:focus       { border-color: var(--purple-mid); }
.input::placeholder { color: var(--text-tertiary); }
.input.error       { border-color: var(--danger); }

/* Chat-to-form sync animation */
.input.bounce-updated { animation: bounceFieldUpdate 600ms ease; }
@keyframes bounceFieldUpdate {
  0%,100% { border-color: var(--border-light); }
  30%,70%  { border-color: var(--lime-dark); background: var(--lime-tint); }
}
```

## 4.6 — Pill Input Bar (entry & CTA screens)

```css
.pill-input-bar {
  display: flex; align-items: center;
  background: white; border-radius: var(--r-pill);
  border: 2px solid var(--border-light);
  padding: 6px 6px 6px 20px;
  width: 100%; max-width: 640px;
  box-shadow: var(--shadow-raised);
}
.pill-input-bar input {
  flex: 1; border: none; background: transparent;
  font-family: var(--font-sans); font-size: var(--text-base);
  color: var(--text-primary); outline: none;
}
.pill-input-bar input::placeholder { color: var(--text-tertiary); }
.pill-add-btn {
  width: 38px; height: 38px; border-radius: 50%;
  background: var(--lime); border: none;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; font-size: 22px; color: var(--purple);
}
.pill-submit-btn {
  width: 38px; height: 38px; border-radius: 50%;
  background: var(--purple-mid); border: none;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: white; font-size: 18px;
}
```

> **Important:** `.pill-input-bar` is for the landing/entry screens. `.bounce-textarea` + `.bounce-send` from Part 5 is for the in-app chat panel. Do not swap them.

## 4.7 — Unified 3-Option Recommendation Component

Used for flights, accommodation, transport, disruption alternatives. All contexts use the same component.

```css
.rec-set  { display: flex; flex-direction: column; gap: var(--sp-3); margin-bottom: var(--sp-5); }
.rec-card {
  background: var(--bg-card); border-radius: var(--r-xl);
  border: 2px solid var(--border-light); padding: var(--sp-5);
  cursor: pointer; position: relative;
  transition: border-color var(--t-fast), box-shadow var(--t-fast);
}
.rec-card:hover     { border-color: var(--purple-mid); box-shadow: var(--shadow-raised); }
.rec-card.selected  { border-color: var(--purple-mid); background: var(--purple-tint); }
.rec-card.recommended { border-color: var(--lime-dark); box-shadow: var(--shadow-raised); }

.rec-badge {
  position: absolute; top: -12px; left: var(--sp-5);
  background: var(--lime); color: var(--lime-text);
  font-size: var(--text-xs); font-weight: 700;
  padding: 3px 12px; border-radius: var(--r-pill);
}
.rec-tier.budget    { color: var(--text-tertiary); }
.rec-tier.recommend { color: var(--lime-text); }
.rec-tier.premium   { color: #92400E; }
```

## 4.8 — Toast Notifications

```css
.toast-stack {
  position: fixed; top: var(--sp-5); right: var(--sp-5);
  z-index: var(--z-toast); display: flex; flex-direction: column; gap: var(--sp-2);
  pointer-events: none; min-width: 320px; max-width: 420px;
}
.toast {
  background: var(--text-primary); color: white;
  border-radius: var(--r-xl); padding: var(--sp-4) var(--sp-5);
  display: flex; align-items: center; gap: var(--sp-3);
  box-shadow: var(--shadow-float); pointer-events: all;
  animation: toastIn 220ms ease forwards;
}
@keyframes toastIn { from{opacity:0;transform:translateY(-8px) translateX(8px)} to{opacity:1;transform:none} }
.toast.purple  { background: var(--purple); }
.toast.success { background: var(--success); }
.toast.warning { background: var(--warning); }
.toast.danger  { background: var(--danger); }
```

---

# PART 5 — BOUNCE PERSONA UI

## 5.1 — Avatar System

```css
.bounce-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--purple); color: var(--lime);
  font-family: var(--font-logo); font-weight: 800; font-size: 18px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; user-select: none;
}
.bounce-avatar-sm { width: 30px; height: 30px; font-size: 13px; }
.bounce-avatar-lg { width: 64px; height: 64px; font-size: 28px; box-shadow: var(--shadow-bounce); }

.member-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  font-family: var(--font-sans); font-weight: 700; font-size: 15px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  /* bg and color set via MEMBER_COLOURS array — see Part 1.3 */
}
```

## 5.2 — Bounce FAB

```css
.bounce-fab {
  position: fixed; bottom: var(--sp-8); right: var(--sp-8);
  width: 60px; height: 60px; border-radius: 50%;
  background: var(--purple); box-shadow: var(--shadow-bounce);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; z-index: var(--z-chat);
  transition: transform var(--t-fast);
}
.bounce-fab:hover  { transform: scale(1.06); }
.bounce-fab:active { transform: scale(0.94); }
.bounce-fab .fab-icon { color: var(--lime); font-size: 26px; }

.bounce-fab.has-alert::before {
  content: ''; position: absolute; inset: -6px;
  border-radius: 50%; border: 2px solid var(--lime);
  animation: pulse-ring 1.8s ease infinite;
}
@keyframes pulse-ring {
  0%  { transform: scale(0.9); opacity: 0.8; }
  70% { transform: scale(1.3); opacity: 0; }
}
```

## 5.3 — Bounce Chat Panel

Desktop: slides in from the right as a sidebar panel. Not bottom sheet.

```css
.bounce-backdrop {
  position: fixed; inset: 0;
  background: rgba(26,10,107,0.3);
  z-index: calc(var(--z-chat) - 1); opacity: 0;
  pointer-events: none; transition: opacity var(--t-normal);
}
.bounce-backdrop.open { opacity: 1; pointer-events: all; }

.bounce-panel {
  position: fixed; right: 0; top: 0; bottom: 0;
  width: 420px; background: var(--bg-card);
  box-shadow: var(--shadow-float);
  z-index: var(--z-chat);
  display: flex; flex-direction: column;
  transform: translateX(100%);
  transition: transform var(--t-slow);
}
.bounce-panel.open { transform: translateX(0); }

.bounce-panel-header {
  padding: var(--sp-5) var(--sp-6);
  border-bottom: 1px solid var(--border-light);
  display: flex; align-items: center; gap: var(--sp-3);
}
```

## 5.4 — Message Bubbles

```css
.msg { display: flex; gap: var(--sp-3); align-items: flex-end; margin-bottom: var(--sp-3); }
.msg-bounce { flex-direction: row; }
.msg-user   { flex-direction: row-reverse; }

.msg-bubble {
  max-width: 75%; padding: 12px 16px;
  font-size: var(--text-sm); line-height: var(--leading-relaxed);
}
.msg-bounce .msg-bubble {
  background: #F7F7F2; color: var(--text-primary);
  border-radius: 4px var(--r-xl) var(--r-xl) var(--r-xl);
}
.msg-user .msg-bubble {
  background: var(--purple-mid); color: white;
  border-radius: var(--r-xl) 4px var(--r-xl) var(--r-xl);
}
```

## 5.5 — Progressive Loading Messages

When Bounce runs a multi-step operation (itinerary generation: 20–30s). Each step appears after the previous completes.

- `"Mapping [destination] venues..."`
- `"Checking everyone's dietary needs..."`
- `"Building Day 1 around your arrivals..."`
- `"Finding places your group will love..."`
- `"Reviewing energy and pacing..."`

## 5.6 — Bounce Contextual Inline Message

```css
.bounce-say {
  display: flex; align-items: flex-start; gap: var(--sp-3);
  padding: var(--sp-4) var(--sp-5);
  background: var(--lime-tint); border-left: 3px solid var(--lime-dark);
  border-radius: 0 var(--r-lg) var(--r-lg) 0;
  margin-bottom: var(--sp-4);
}
.bounce-say p { font-size: var(--text-sm); color: var(--purple); line-height: var(--leading-relaxed); }

.bounce-say.danger { background: var(--danger-tint); border-left-color: var(--danger); }
.bounce-say.danger p { color: var(--danger-text); }
```

---

# PART 6 — VISUAL LANGUAGE

## 6.1 — Gradient Orbs

Decorative circular blobs. Never place interactive content over orbs.

```css
.orb { border-radius: 50%; flex-shrink: 0; pointer-events: none; user-select: none; }
.orb-1 { width: 200px; height: 200px; background: var(--orb-1); }
.orb-2 { width: 180px; height: 180px; background: var(--orb-2); }
.orb-3 { width: 220px; height: 220px; background: var(--orb-3); }
.orb-4 { width: 180px; height: 180px; background: var(--orb-4); }

.orb-row {
  display: flex; align-items: center; justify-content: center;
  gap: var(--sp-5); padding: var(--sp-10) 0; overflow: hidden;
}
```

## 6.2 — Full-Bleed Section Backgrounds

| Section | Background |
|---|---|
| Hero | `radial-gradient(ellipse 70% 60% at 50% 40%, #F5FFB0 0%, #FAFFD4 40%, #FFFFFF 100%)` |
| Problem | `#1A0A6B` solid — white + lime-yellow text |
| Feature list | `linear-gradient(135deg, #7DC832 0%, #8DC63F 30%, #AADC3A 65%, #C8E64A 100%)` |
| CTA arc | `radial-gradient(circle at 50% 35%, #FF9A3C 0%, #F47B20 35%, #FBBF24 80%)` |

## 6.3 — Activity Category Colour System

Each activity type has a dedicated colour from the brand palette. Used for left-border accent, icon background, and category tag.

| Category | Token | Hex | Tabler icon |
|---|---|---|---|
| Food & cafes | `--cat-food` | `#F47B20` | `ti-tools-kitchen-2` |
| Culture & museums | `--cat-culture` | `#7C3AED` | `ti-building-arch` |
| Nature & outdoors | `--cat-nature` | `#16A34A` | `ti-trees` |
| Transport & transit | `--cat-transport` | `#1A0A6B` | `ti-train` |
| Shopping | `--cat-shopping` | `#EC4899` | `ti-shopping-bag` |
| Accommodation | `--cat-hotel` | `#C8E64A` | `ti-building` |
| Nightlife | `--cat-nightlife` | `#4A2FC4` | `ti-moon-stars` |
| Wellness & spa | `--cat-wellness` | `#0D9488` | `ti-spa` |

---

# PART 7 — MAP DESIGN SPECIFICATION

## 7.1 — Custom Venue Pins

| Colour | Use |
|---|---|
| `--purple` `#1A0A6B` | Standard venues — numbered circle 32px, white border |
| `--lime` `#C8E64A`, purple border | Accommodation — 38px, larger |
| Teal `#0D9488` | Current activity — pulses with `map-pin-pulse` animation |

## 7.2 — Route Line

`strokeColor: #1A0A6B` (purple), opacity 0.7, weight 3, directional arrows at 50% offset repeating every 120px.

## 7.3 — Venue Callout Card

220px · `r-xl` · `shadow-raised` · appears above pin on tap. Contains: venue name, time, Navigate button (purple), Swap button (ghost). Animate with `calloutAppear` (fade + translateY 4px).

## 7.4 — Transport Mode Selector

Vertical pill column, top-right of map overlay. 36px square buttons. Active state: `bg-purple`, `color-lime`.

---

# PART 8 — SCREEN SPECIFICATIONS

> **CUT — do not build:** Travel DNA · Receipt scanning · Packing list · Trip narrative · Multi-language · Cultural briefing · GPS/live location · Screen 12 (merged into Screen 11)

---

## Screen 0 — Auth / Name Entry

Full-height deep purple background. Bounce logo (64px) + wordmark centered top third. White card bottom half, rounded top corners.

> **Bounce says:** "I'm Bounce — your AI travel companion. Before we go anywhere, what's your name?"

- Large name input — centered, underline style, 30px Nunito ExtraBold
- Placeholder: `"Alex, Priya, Marcus..."`
- CTA: `"Let's go →"` — `.btn-primary`, full width
- Privacy note — `.t-caption`, `text-tertiary`, centered

---

## Screen 1 — Entry Conversation

> **Bounce says:** "Tell me about your trip. I'll figure out the rest."

- Top bar — wordmark + scrollable group type chips (Friends | Family | Office)
- White card — Bounce contextual + `.pill-input-bar` + send button
- Quick-select chips: Beach | City | Mountains | Culture | Adventure | International | Domestic
- Group size stepper: — N + people
- Bounce typing indicator → response bubble

---

## Screen 1b — Member Join Flow

Opens from invite link.

> **Bounce says:** "Hey! [Name] is planning a trip to [Destination]. I need a few things from you first."

- Purple hero — trip name, organiser, destination chip, member avatar row
- White card — Bounce intro + `"Join the trip →"` CTA (`.btn-primary`, full width)
- After join: full-screen lime-tint card, teal check, "You're in!", group status + progress bar, member avatars

---

## Screen 2 — Group Setup (Organiser View)

- Invite card — lime-tint bg, share link, copy button, join status + `.progress-wrap` component
- Co-leader assignment — member list with Assign toggles (max 2)
- Member cards — avatar + name + origin + role badge + status badge
- Bounce contextual (admins only) — preference insights + visa flags
- CTA: `"Begin planning →"` — active only when all members joined

---

## Screen 3 — Profile Completion

Bounce pre-fills from conversation. User sees only genuine gaps. 3-step flow with progress bar.

- **Step 1 — Dietary:** chip grid with strictness toggle if halal/kosher/vegan selected
- **Step 2 — Interests:** History | Art | Food | Nightlife | Nature | Shopping | Music | Sport | Wellness
- **Step 3 — Observance:** prayer times toggle, mobility toggle, emergency contact toggle

**Compliance view** (private, international trips only): amber banner, visa status tag, processing time, apply-by date, fee estimate, official embassy link only.

---

## Screen 4 — Itinerary View (Duolingo-inspired)

The most important screen. Visual hierarchy is critical. Rounded, colourful, icon-forward. Each activity type is immediately visually distinct.

### Layout (desktop, 3-column)

```
[ Day selector — 280px ] [ Day timeline — 1fr ] [ Budget + map — 300px ]
```

### Day Selector (left column)

```css
.day-tab {
  display: flex; align-items: center; gap: var(--sp-3);
  padding: var(--sp-3) var(--sp-4); border-radius: var(--r-xl);
  cursor: pointer; transition: all var(--t-fast);
  margin-bottom: var(--sp-1);
}
.day-tab:hover  { background: var(--bg-raised); }
.day-tab.active { background: var(--purple-mid); color: white; }
.day-tab .day-number  { font-family: var(--font-display); font-weight: 800; font-size: var(--text-lg); }
.day-tab .day-date    { font-size: var(--text-xs); opacity: 0.7; }
.day-tab .day-weather { font-size: 18px; }
```

### Accommodation Strip (always first in day)

```css
.accom-strip {
  display: flex; align-items: center; gap: var(--sp-4);
  padding: var(--sp-4) var(--sp-5);
  background: var(--lime-tint); border-radius: var(--r-xl);
  border-left: 4px solid var(--lime-dark);
  margin-bottom: var(--sp-5);
}
.accom-icon { font-size: 24px; color: var(--lime-text); }
.accom-name { font-weight: 700; font-size: var(--text-md); }
.accom-meta { font-size: var(--text-sm); color: var(--text-secondary); }
```

### Activity Card (Duolingo-inspired)

```css
.activity-card {
  display: flex; align-items: flex-start; gap: var(--sp-4);
  padding: var(--sp-4) var(--sp-5); background: var(--bg-card);
  border-radius: var(--r-xl); border: 2px solid var(--border-light);
  border-left: 5px solid var(--cat-color);   /* set via inline style */
  margin-bottom: var(--sp-3);
  transition: box-shadow var(--t-fast), transform var(--t-fast);
}
.activity-card:hover { box-shadow: var(--shadow-raised); transform: translateY(-1px); }

.activity-icon-wrap {
  width: 48px; height: 48px; border-radius: var(--r-lg); flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: var(--cat-tint);   /* rgba(cat-hex, 0.12) */
}
.activity-icon   { font-size: 22px; color: var(--cat-color); }
.activity-time   { font-size: var(--text-xs); font-weight: 700; color: var(--text-tertiary);
                   text-transform: uppercase; letter-spacing: 0.07em; }
.activity-name   { font-family: var(--font-display); font-weight: 800;
                   font-size: var(--text-md); color: var(--text-primary); margin-bottom: 2px; }
.activity-reason { font-size: var(--text-sm); color: var(--text-secondary);
                   font-style: italic; line-height: var(--leading-normal); }
.activity-tags   { display: flex; gap: var(--sp-2); margin-top: var(--sp-2); flex-wrap: wrap; }
.activity-footer { display: flex; justify-content: space-between; align-items: center;
                   margin-top: var(--sp-3); padding-top: var(--sp-3);
                   border-top: 1px solid var(--border-light); }
```

**HTML usage — inline style to inject category colour:**
```html
<div class="activity-card" style="--cat-color: var(--cat-food); --cat-tint: rgba(244,123,32,0.12)">
  <div class="activity-icon-wrap">
    <i class="ti ti-tools-kitchen-2 activity-icon"></i>
  </div>
  <div>
    <div class="activity-time">9:00 AM — 10:30 AM</div>
    <div class="activity-name">Tsukiji Outer Market</div>
    <div class="activity-reason">I've put breakfast here — freshest sushi in Tokyo at this hour.</div>
    <div class="activity-tags">
      <span class="tag tag-orange">Food</span>
      <span class="tag tag-purple">Booking not required</span>
    </div>
  </div>
</div>
```

### Transit Connector

```css
.transit-connector {
  display: flex; align-items: center; gap: var(--sp-3);
  padding: var(--sp-2) var(--sp-5);
  color: var(--text-tertiary); font-size: var(--text-sm);
}
.transit-connector::before,
.transit-connector::after { content: ''; flex: 1; height: 1px; background: var(--border-light); }
```

### Right Column — Day Budget Card

```css
.day-budget-card {
  background: var(--bg-card); border-radius: var(--r-xl);
  border: 1px solid var(--border-light); padding: var(--sp-5);
  margin-bottom: var(--sp-4);
}
.budget-amount {
  font-family: var(--font-display); font-weight: 800;
  font-size: var(--text-2xl); color: var(--text-primary);
}
```

Use `.progress-wrap` from Part 4.2 for the budget bar.

> **Visual hierarchy rule:** Every activity card must show: (1) coloured icon — instant category recognition, (2) bold name — most important text, (3) italic reason — why Bounce picked it, (4) time label top-left. Mirrors Duolingo's lesson card: icon → title → subtitle.

> **Colour rule:** Every card must have a colour. Never use a default grey card for activities. Set `--cat-color` and `--cat-tint` via inline style on every `.activity-card`.

---

## Screen 5 — FlockMode Creation

> **Bounce says:** "Split your group into smaller flocks for parallel adventures. They'll reconvene at a time and place you set."

Desktop: centred modal, max-width 640px.

```css
.flock-dropzone {
  min-height: 80px; border: 2px dashed var(--border-medium);
  border-radius: var(--r-xl); padding: var(--sp-3);
  display: flex; flex-wrap: wrap; gap: var(--sp-2);
  transition: border-color var(--t-fast), background var(--t-fast);
}
.flock-dropzone.has-members { border-color: var(--purple-mid); background: var(--purple-tint); }
```

- Unassigned members pool — chip grid
- Flock boxes (3 default, max 5) — dashed drop zone, tap to rename
- Reconvene section — time picker + location input
- CTA: `"Start FlockMode →"` — `.btn-lime`, disabled until all members assigned

---

## Screen 6 — FlockMode Active (Member View)

- Purple header — flock name + `ti-feather` icon + member chips
- Reconvene countdown card — large timer (`.t-display`) + venue + transit estimate
- Flock-specific timeline — same `.activity-card` component, venues for this flock only
- Per-flock map embed
- Thread tab in Bounce panel — flock thread active

---

## Screen 7 — Active Trip Daily View

- Flight status banner — `.toast.success` (on time) | `.toast.warning` (delayed) | `.toast.danger` (cancelled)
- Current activity card — purple border, lime NOW pulse badge
- Today's remaining schedule — condensed `.activity-card` timeline
- Map embed — day venues pinned (not live GPS)
- Ask Bounce button — lime-tint bg
- Budget tracker + quick expense add button

---

## Screen 8 — Disruption Response Flow

Pub/Sub event → Firebase update → danger toast → Bounce FAB pulses → disruption sheet (desktop: centred modal).

> **Bounce says:** "Heads up — [venue] is showing as closed today. I've already found 3 alternatives nearby. Want to see them?"

```css
.disruption-overlay { position: fixed; inset: 0; background: rgba(26,10,107,0.5);
  z-index: var(--z-overlay); display: flex; align-items: center; justify-content: center; }
.disruption-sheet {
  width: 100%; max-width: 640px; background: var(--bg-card);
  border-radius: var(--r-2xl); padding: var(--sp-8);
  max-height: 90vh; overflow-y: auto;
  animation: sheetUp var(--t-slow) forwards;
}
@keyframes sheetUp { from { transform: translateY(20px); opacity: 0; } to { transform: none; opacity: 1; } }
```

- 3-option rec-set — same component, transit + cost + duration per card
- After selection — confirmation, member avatars all green, Firebase already broadcast
- Return to today view — itinerary reflects new venue, success toast fires

---

## Screen 9 — Suggestion Review Panel (Admin)

Lime-tint card at top of itinerary. Purple count badge. Suggestion items (white card inside). Supporter count. Accept / Modify / Decline actions.

```css
.suggestion-panel {
  background: var(--lime-tint); border: 1px solid var(--lime-dark);
  border-radius: var(--r-xl); padding: var(--sp-5); margin-bottom: var(--sp-4);
}
.suggestion-count-badge {
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--purple); color: var(--lime);
  font-size: 13px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
```

---

## Screen 10 — Split Bill

- Tab row: Everyone | Specific people | My Flock | Just me
- Large amount input — `.t-display`, number keyboard, currency chip
- Description input: `"What was this for?"`
- Category chips — Food | Transport | Activity | Shopping | Other
- Member chip grid — all selected by default for "Specific people"
- Running balance bar — per-person mini card: name | spent | balance (colour-coded)

---

## Screen 11 — Settlement + Spending Summary

Screen 12 merged here. No Travel DNA.

### Top: Spending Summary

- Trip header card — `.card-purple`, trip name, destination, dates, group avatar row
- Total spend: `.t-display` amount vs budget, `.progress-wrap` (success/danger state)
- Category breakdown: horizontal bar per category (Food | Transport | Activities | Shopping | Other)
- Bounce insight: 1 sentence only. e.g. `"You overspent on food by 12%. Worth it."`

### Bottom: Settlement (who pays who)

> **Bounce says:** "I've calculated the simplest way to settle — minimum transactions for everyone."

```css
.transaction-card {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--sp-4) var(--sp-5); background: var(--bg-card);
  border-radius: var(--r-xl); border: 1px solid var(--border-light);
  margin-bottom: var(--sp-3);
}
.transaction-amount {
  font-family: var(--font-display); font-weight: 800;
  font-size: var(--text-xl); color: var(--text-primary);
}
```

- Transaction cards — payer → receiver + amount + Copy details / Message [name] buttons
- Per-person balance cards — total paid | total owed | net (green if owed money, red if owes)
- Bounce note: `"These figures are based on expenses logged in Bounce. Settle anything outside the app separately."`

---

## Screen 13 — Judge Test Mode UI

Only visible at `?mode=judge`. Lime trigger pill bottom-left.

```css
.judge-trigger {
  background: var(--lime); color: var(--purple);
  padding: 6px 14px; border-radius: var(--r-pill);
  font-weight: 700; font-size: var(--text-xs); cursor: pointer;
}
```

4 actions: Reset demo | Load Reunion trip | Trigger disruption | Judge instructions

---

# PART 9 — UX FLOWS

## 9.1 — 3-Minute Demo Path

| Time | Action |
|---|---|
| 0:00–0:05 | Auth screen — name "Alex" → "Let's go" |
| 0:05–0:20 | Screen 1: Entry — Reunion message → Bounce responds |
| 0:20–0:35 | Screen 3: Profile completion (pre-filled, brief) |
| 0:35–0:50 | Group status (7 joined, 3 pending) → "Begin planning" |
| 0:50–1:05 | Progressive loading — 5 Bounce steps animate in |
| 1:05–1:15 | Screen 4: Itinerary Day 1 — colour-coded cards, icons |
| 1:15–1:25 | Flight selection — ANA NH106 rec-card (Low risk, 84/100) |
| 1:25–1:35 | Day 5 tab — Bounce suggests FlockMode |
| 1:35–1:50 | Screen 5: FlockMode creation — 3 Flocks built |
| 1:50–2:00 | Screen 6: FlockMode active — reconvene countdown |
| 2:00–2:05 | Judge panel: tap "Trigger disruption" |
| 2:05–2:30 | Screen 8: Disruption → Mori Art Museum → Firebase update |
| 2:30–2:40 | Screen 10: Split bill — 4-mode UI |
| 2:40–2:55 | Screen 11: Spending summary + settlement |
| 2:55–3:00 | Bounce logo hold |

## 9.2 — Booking Handoff Flow

Tap booking link → warning modal → "Leaving Bounce to book" → external site → return → Bounce asks for confirmation number → status updates to "Booked ✓".

## 9.3 — Chat-to-Form Sync

User speaks in Bounce panel while form screen is visible. Agent returns structured intent. Frontend applies `.bounce-updated` animation to the affected field/chip.

```javascript
// Agent response structure:
{ intent: 'update_profile', field: 'dietary', value: 'vegetarian' }
```

---

# PART 10 — STATES

## 10.1 — Loading States

```css
.skeleton {
  background: linear-gradient(90deg,
    var(--border-light) 0%, var(--bg-raised) 50%, var(--border-light) 100%);
  background-size: 200% 100%; border-radius: var(--r-sm);
  animation: shimmer 1.5s ease infinite;
}
@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }
```

For loads > 5s: use progressive loading messages from Part 5.5.

## 10.2 — Empty States Per Screen

| Screen | Icon | Bounce message |
|---|---|---|
| Group (no members) | `ti-user-plus` | "Share the invite link — I'll ping you when people start joining." |
| Itinerary (no days) | `ti-map` | "Tell me about your trip and I'll build the plan." |
| Split bill | `ti-receipt-2` | "Log your first expense when you get there — I'll handle the maths." |
| Flocks (not created) | `ti-feather` | "Day 5 looks like a good one for FlockMode. Tap to split up." |
| Flight status | `ti-plane` | "Once you've picked your flights, I'll keep an eye on them." |

## 10.3 — Error States

```css
.error-inline {
  display: flex; align-items: flex-start; gap: var(--sp-2);
  padding: var(--sp-3) var(--sp-5); background: var(--danger-tint);
  border-left: 3px solid var(--danger); border-radius: 0 var(--r-lg) var(--r-lg) 0;
}
```

---

# PART 11 — ANIMATION & MOTION

```css
/* Page enter */
.page-enter { animation: fadeUp 220ms ease both; }
@keyframes fadeUp { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }

/* Staggered card appear */
.stagger > * { animation: fadeUp 200ms ease both; }
.stagger > *:nth-child(1){animation-delay:0ms}
.stagger > *:nth-child(2){animation-delay:50ms}
.stagger > *:nth-child(3){animation-delay:100ms}
.stagger > *:nth-child(4){animation-delay:150ms}
.stagger > *:nth-child(5){animation-delay:200ms}

/* Disruption shake */
.shake { animation: shake 400ms ease; }
@keyframes shake { 0%,100%{transform:translateX(0)} 20%{transform:translateX(-6px)} 40%{transform:translateX(6px)} 60%{transform:translateX(-4px)} 80%{transform:translateX(4px)} }

/* Firebase update flash */
.firebase-update { animation: flashUpdate 800ms ease; }
@keyframes flashUpdate { 0%,100%{background:inherit} 30%,70%{background:var(--lime-tint)} }

/* Flight status flash */
.status-change { animation: statusFlash 600ms ease; }
@keyframes statusFlash { 0%,100%{background:inherit} 50%{background:var(--orange-tint)} }

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

| Class | Effect |
|---|---|
| `.page-enter` | fadeUp 220ms |
| `.stagger > *` | fadeUp 200ms, 50ms stagger per child |
| `.shake` | Horizontal shake ±6px (disruption trigger) |
| `.firebase-update` | Flashes lime-tint (item changed by another member) |
| `.status-change` | Flashes orange-tint (flight status changed) |
| `.bounce-updated` | Field flashes lime-dark/lime-tint (chat-to-form sync) |
| `.activity-card:hover` | translateY(-1px) + shadow-raised |

---

# PART 12 — MICRO-COPY GUIDE

See Part 17 for full brand voice rules. Tables below are the applied output.

## 12.1 — Button Labels

| Generic (wrong) | Specific (correct) |
|---|---|
| Submit / Continue | Plan my trip · Start planning · Lock it in · Add my details |
| Save / Confirm | Done · Got it · Looks right · That's the one |
| Select (flight) | Fly this one · Choose |
| Apply (disruption) | Go here instead |
| Back / Close | Change something · Go back · Done |
| Join / Share | Join the trip → · Invite my group |
| Book | Go to [airline] → |
| Log expense | Add expense |

## 12.2 — Bounce Voice

**When something takes time:**
- `"Let me pull this together — it'll be worth the wait."`
- `"Working on your 10-day itinerary... this takes a moment."`

**When something goes right:**
- `"Done! [specific result]."` — never just "Done!"
- `"Your trip is locked in. See you in Tokyo."`
- `"All 10 members are in. Let's build this trip."`

**When something goes wrong:**
- `"Couldn't pull live flights right now — give it a moment."`
- `"Something went sideways. Try that again?"`

**When data is an estimate:**
- `"These prices are estimates — confirm when you book."`
- `"Visa info is current as of today — always verify with the embassy."`

**Never say:**
- "I have processed your request"
- "Certainly!" / "Of course!" / "An error has occurred"
- "Please find below" / "I understand that..."

## 12.3 — Empty State Messages

| Screen | Message |
|---|---|
| No members | "Share the link with your group. I'll keep you posted as people join." |
| Waiting for planning | "Just waiting for [Name] to kick things off. Once they start planning, you'll see the trip here." |
| No expenses | "First expense? Log it here — I'll handle the maths and keep everyone updated." |
| FlockMode not created | "When your group wants to split up for a few hours, use FlockMode. Each Flock gets its own plan." |
| No flight status | "I'll track your flights once you've confirmed them. Check back closer to departure." |

---

# PART 13 — ACCESSIBILITY

```css
*:focus-visible {
  outline: 2.5px solid var(--purple-mid);
  outline-offset: 2px;
  border-radius: 4px;
}
```

## 13.1 — Contrast Ratios (WCAG AA)

| Combination | Result |
|---|---|
| `--purple` on white | ✓ Passes — use for headings, icons |
| White on `--purple` | ✓ Passes — nav, avatar, CTAs |
| `--lime-text` (#3A5200) on `--lime` | 5.1:1 ✓ — always use `--lime-text` on lime surfaces |
| `--purple-mid` on white | ✓ Passes for interactive elements |
| `--text-secondary` on white | 4.8:1 ✓ |
| `--lime` on `--purple` | ✓ High contrast — logo accent, FAB icon |

## 13.2 — Required ARIA Labels

| Component | ARIA |
|---|---|
| Bounce chat panel | `role="dialog" aria-label="Bounce assistant" aria-modal="true"` |
| Map | `role="application" aria-label="Trip map showing venue locations"` |
| Flight risk meter | `role="meter" aria-valuemin="0" aria-valuemax="100"` |
| Toggle switch | `role="switch" aria-checked="false"` |
| Loading state | `aria-live="polite" aria-label="Bounce is building your itinerary"` |

---

# PART 14 — PRD SYNC CHECKLIST

| PRD Feature | Design Element | Screen | Status |
|---|---|---|---|
| Bounce persona | Avatar, FAB, chat panel, messages | All | ✓ |
| Conversational entry | Entry screen + quick-select chips | Screen 1 | ✓ |
| Group invite + join | Group setup, member join flow | Screens 2, 1b | ✓ |
| Co-leader assignment | Member card + toggle | Screen 2 | ✓ |
| Per-member visa compliance | Private compliance card | Screen 3 | ✓ |
| 3-option recommendations | Unified rec-set component | All planning | ✓ |
| Itinerary + Maps | Duolingo-style day view + map | Screen 4 | ✓ v3.0 |
| Flight risk scoring | Risk bar + score on flight card | Screen 4 | ✓ |
| FlockMode creation | Full screen spec | Screen 5 | ✓ |
| FlockMode active | Flock view, countdown, thread | Screen 6 | ✓ |
| Disruption mitigation | Disruption sheet, 3-option alts | Screen 8 | ✓ |
| Firebase live sync | `.firebase-update` animation | All group screens | ✓ |
| Split bill 4 modes | Tab row in split bill | Screen 10 | ✓ |
| Settlement + spending | Merged Screen 11 | Screen 11 | ✓ v3.0 |
| Travel DNA | **REMOVED** | — | ✗ CUT |
| Receipt scanning | **REMOVED** | — | ✗ CUT |
| Packing list | **REMOVED** | — | ✗ CUT |
| Trip narrative | **REMOVED** | — | ✗ CUT |
| Multi-language UI | **REMOVED** | — | ✗ CUT |
| Cultural briefing | **REMOVED** | — | ✗ CUT |
| GPS / live location | **REMOVED** | — | ✗ CUT |
| Dark mode | **REMOVED** — light only | — | ✗ CUT |
| Rate limit (5 msg/10s) | No UI — CS backend only | — | CS owned |

---

# PART 15 — OWNERSHIP & BUILD ORDER

## Biz 1 Owns

| Days | Task |
|---|---|
| Day 1 | Auth screen (Screen 0) + Entry screen (Screen 1) — first thing judges see |
| Day 3–5 | Profile completion (Screen 3) + Compliance card |
| Day 6–8 | Flight selection UI (5 origin groups × 3 rec-cards) |
| Day 9–11 | FlockMode creation (Screen 5) — key demo moment |
| Day 12–13 | Split bill (Screen 10) |
| Day 14–15 | Bounce loading animations, toast system, empty states |

## Biz 2 Owns

| Days | Task |
|---|---|
| Day 2 | Member join flow (Screen 1b) + Group setup (Screen 2) |
| Day 3–5 | Itinerary view — Duolingo layout + Maps (Screen 4) |
| Day 6–8 | Active trip daily view (Screen 7) + FlockMode active (Screen 6) |
| Day 9–11 | Disruption sheet (Screen 8) + Suggestion panel (Screen 9) |
| Day 12–13 | Settlement + spending summary (Screen 11) |
| Day 14–15 | Judge mode UI (Screen 13) + demo video recording |

## CS Engineer Connects

| Scope | Task |
|---|---|
| All screens | Firebase real-time listeners → `.firebase-update` animation on changed nodes |
| Screen 1 | Bounce textarea → Agent Builder streaming API |
| Screen 4 | Maps SDK init + custom marker creation (Part 7) |
| Screen 3 | Agent intent → form field `.bounce-updated` animation (Part 9.3) |
| Screen 7 | Pub/Sub flight event → toast → disruption sheet open |
| Screen 8 | Alternative selection → `save_itinerary` → Firebase broadcast |
| Sidebar | Phase transitions (`data-phase` on `.sidebar`, Part 3.3) |
| Screen 13 | Judge endpoints wired to UI actions |

---

# PART 16 — ICON REFERENCE

CDN — add to `<head>`:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css" />
```

| Feature | Icon | Feature | Icon |
|---|---|---|---|
| Home | `ti-home` | Itinerary | `ti-map-2` |
| Today | `ti-calendar-today` | Bounce / Chat | `ti-message-circle-2` |
| Split bill | `ti-receipt-2` | Profile | `ti-user` |
| Visa | `ti-id` | Alerts | `ti-bell` |
| Flight | `ti-plane` | Hotel | `ti-building` |
| Restaurant | `ti-tools-kitchen-2` | Transit | `ti-train` |
| Walk | `ti-walk` | Drive | `ti-car` |
| Ferry | `ti-sailboat` | FlockMode | `ti-feather` |
| Disruption | `ti-alert-triangle` | Flight status | `ti-radar` |
| Risk low | `ti-shield-check` | Risk high | `ti-shield-x` |
| Budget | `ti-wallet` | Expense | `ti-coin` |
| Map pin | `ti-map-pin` | Group | `ti-users-group` |
| Co-leader | `ti-crown` | Flock leader | `ti-star` |
| Reconvene | `ti-arrows-join` | Copy link | `ti-copy` |
| Share | `ti-share-2` | Swap venue | `ti-refresh` |
| Confirmed | `ti-circle-check` | External link | `ti-external-link` |
| Back | `ti-arrow-left` | Close | `ti-x` |
| Settings | `ti-settings` | Privacy | `ti-lock` |
| Judge mode | `ti-bolt` | Culture | `ti-building-arch` |
| Nature | `ti-trees` | Shopping | `ti-shopping-bag` |
| Nightlife | `ti-moon-stars` | Wellness | `ti-spa` |

---

# PART 17 — BRAND VOICE & COPY GUIDELINES

> **Bounce should feel like:** *"The friend who somehow keeps the whole trip together."*
>
> Not about optimising travel. About making group trip planning feel exciting, easy, and socially enjoyable again.

## 17.1 — Brand Personality

| | |
|---|---|
| **Bounce IS** | Warm · Socially intelligent · Clear · Optimistic · Collaborative · Playful (restrained) · Emotionally relieving · Modern |
| **Bounce is NOT** | Corporate · Technical · Productivity-sounding · Robotic · Overly Gen Z or meme-heavy · Trying too hard |

## 17.2 — Writing Principles

**1. Clarity over cleverness** — users must instantly understand what Bounce does.

| | |
|---|---|
| Good | "Plan trips together, without the chaos." |
| Bad | "Reinvent collaborative travel orchestration." |

**2. Write emotionally, not technically** — focus on how planning feels. Not backend complexity.

**3. Keep copy short and airy** — short paragraphs, minimal UI copy, let the UI explain.

**4. Avoid overusing "AI"** — Bounce should feel magical, not technical.

**5. Make it feel collaborative** — groups, friends, together. Not solo.

## 17.3 — Core Messaging Pillars

| Pillar | Description |
|---|---|
| Group travel is chaotic | Group chats, spreadsheets, TikToks, opinions become overwhelming. Bounce organises the chaos. |
| Planning should feel exciting | The planning stage is part of the experience. Bounce makes it energising. |
| Bounce keeps everyone aligned | Stay synced, collaborate live, adapt together, travel more smoothly. |
| Real trips are messy | Trips change. Bounce adapts through delays, split schedules, budget differences. |

## 17.4 — UX Writing

**Placeholders — natural, realistic:**

| | |
|---|---|
| Good | "We're 6 friends going to Seoul in November. Cafes, nightlife, shopping, and good food." |
| Avoid | Robotic / over-formatted prompts |

**Loading states — alive, reassuring:**

| | |
|---|---|
| Good | "Organizing everyone's ideas..." · "Finding places your group will love..." |
| Avoid | "Processing request..." · technical language |

**Empty states — optimistic:**

| | |
|---|---|
| Good | "Your trip starts with an idea." · "Invite your friends to start planning together." |
| Avoid | Dead-end copy · error-sounding language |

---

> **Brand feeling — every screen must reinforce:**
>
> *"Planning trips with friends should feel fun again."*

---

*Bounce Design System v3.0 — May 2026*
*Desktop-first · Light mode only · Google Cloud Rapid Agent Hackathon 2026*
