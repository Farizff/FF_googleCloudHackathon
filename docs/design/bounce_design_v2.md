# Bounce — Design System v2.1 (synchronized)
## Gold-standard frontend implementation guide · Google Cloud Rapid Agent Hackathon 2026

> **For Biz 1, Biz 2, and CS engineers.**
> Build every screen from this document. Every gap from v1 is addressed here.
> Paste the token block first. Build screens in Part 8 order. Follow the demo path in Part 9.
>
> **For all tool contracts, schemas, algorithms, and demo scenario member assignments, see `bounce_prd_v2.md` (the PRD is the source of truth for those).**
> **This design document is the source of truth for all UI styling, screens, flows, and component specs.**

---

# PART 0 — VISUAL IDENTITY

## 0.1 — The Bounce logomark

The Bounce mark is a rounded square (app-icon geometry) in Yale Blue. A bold lowercase **b** sits left-center in Lemon Chiffon. A small filled circle in Lemon Chiffon sits upper-right, connected to the b by a faint dashed arc — the trajectory of a bounce. Simple, legible at 16px, distinctive.

**SVG logomark** — save as `public/logo.svg`. Use at all sizes:

```svg
<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Bounce">
  <rect width="40" height="40" rx="9" fill="#0D3B66"/>
  <text x="9" y="29" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif"
        font-weight="800" font-size="24" fill="#FAF0CA" letter-spacing="-0.5">b</text>
  <circle cx="29" cy="10" r="4" fill="#FAF0CA"/>
  <path d="M22 22 Q26 14 27 12" stroke="#FAF0CA" stroke-width="1.5"
        fill="none" stroke-dasharray="2 3" stroke-linecap="round" opacity="0.55"/>
</svg>
```

**Wordmark** (logo + name, used in nav header):

```html
<div class="bounce-wordmark">
  <img src="/logo.svg" width="28" height="28" alt="Bounce" />
  <span>Bounce</span>
</div>
```

```css
.bounce-wordmark {
  display: flex; align-items: center; gap: 8px;
}
.bounce-wordmark span {
  font-size: 20px; font-weight: 800; color: white;
  letter-spacing: -0.5px;
}
.bounce-wordmark span::first-letter { color: var(--lemon); }
```

## 0.2 — Brand mark sizes

| Context | Size | File | Notes |
|---|---|---|---|
| Browser favicon | 16×16, 32×32 | `favicon.ico` / `favicon.svg` | Use the SVG logomark |
| PWA icon | 192×192, 512×512 | `icon-192.png`, `icon-512.png` | Export logomark at these sizes |
| App header (nav) | 28×28 | inline SVG or img | With wordmark beside it |
| Bounce avatar (chat) | 36×36 | Rendered CSS, no image | Use `.bounce-avatar` component |
| Entry hero | 56×56 | Rendered CSS | Use `.bounce-avatar-lg` |

## 0.3 — Bounce persona

Bounce is not a robot. Bounce is a competent, energetic travel-obsessed friend who happens to know everything. The persona shows in four ways:

**Voice:** Short sentences. Occasional exclamation marks on wins. No corporate language. Always explains why, not just what. Example: "I've kept Day 1 light — you're crossing 16 time zones and trust me, you'll thank me later."

**Visual:** Yale Blue avatar with Lemon Chiffon letter. The Lemon Chiffon represents warmth and energy against the authoritative Yale Blue. Bounce messages always appear in the off-white (#F7F7F2) bubble, never white, so they feel warm not clinical.

**Behaviour:** Bounce speaks before the user asks. Bounce notices things. Bounce admits when it does not know. Bounce celebrates with the user.

**Avatar mark:** Never use a generic user avatar icon for Bounce. Always use the `.bounce-avatar` CSS component (letter "B" in Lemon Chiffon on Yale Blue). This distinguishes Bounce from all human members visually at a glance.

## 0.4 — Favicon and PWA config

```html
<!-- index.html head -->
<link rel="icon" type="image/svg+xml" href="/logo.svg" />
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png" />
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
<link rel="manifest" href="/manifest.json" />
<meta name="theme-color" content="#0D3B66" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
<meta name="apple-mobile-web-app-title" content="Bounce" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
```

---

# PART 1 — DESIGN TOKENS

Paste this entire block at the top of `style.css` before any other styles. Reference only these variables everywhere — never use raw hex values in component CSS.

```css
/* ════════════════════════════════════════
   BOUNCE DESIGN TOKENS — LIGHT MODE
   ════════════════════════════════════════ */
:root {
  /* ── Brand ── */
  --yale:           #0D3B66;
  --yale-light:     #1A6DC8;
  --yale-tint:      #E8F0F8;
  --lemon:          #FAF0CA;
  --lemon-dark:     #F0DB6A;
  --lemon-text:     #7A6010;  /* text ON lemon background — passes WCAG AA */

  /* ── Semantic ── */
  --teal:           #0D9488;
  --teal-light:     #14B8A6;
  --teal-tint:      #E6F7F5;
  --teal-text:      #0F5550;
  --amber:          #D97706;
  --amber-tint:     #FFF7ED;
  --amber-text:     #7C3B00;
  --danger:         #DC2626;
  --danger-tint:    #FEF2F2;
  --danger-text:    #7F1D1D;
  --success:        #16A34A;
  --success-tint:   #F0FDF4;

  /* ── Neutral ── */
  --bg-page:        #F7F7F2;
  --bg-card:        #FFFFFF;
  --bg-raised:      #FAFAFA;
  --bg-overlay:     rgba(13,59,102,0.04);

  /* ── Text ── */
  --text-primary:   #1A1A2E;
  --text-secondary: #6B7280;
  --text-tertiary:  #9CA3AF;
  --text-inverse:   #FFFFFF;
  --text-lemon:     #7A6010;  /* text ON lemon bg */
  --text-yale:      #FFFFFF;  /* text ON yale bg */

  /* ── Borders ── */
  --border-light:   #E5E7EB;
  --border-medium:  #D1D5DB;
  --border-strong:  #9CA3AF;
  --border-yale:    #1A6DC8;
  --border-lemon:   #F0DB6A;

  /* ── Typography ── */
  --font-sans:  -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  --font-mono:  'SF Mono', 'Fira Code', 'Cascadia Code', monospace;

  /* ── Type scale ── */
  --text-xs:    11px;  /* labels, tags, timestamps */
  --text-sm:    13px;  /* captions, secondary info, chip text */
  --text-base:  15px;  /* body text, default */
  --text-md:    17px;  /* subheadings, card titles */
  --text-lg:    20px;  /* section headings */
  --text-xl:    24px;  /* screen titles */
  --text-2xl:   30px;  /* hero numbers, expense amounts */
  --text-3xl:   40px;  /* large numeric display */

  /* ── Leading ── */
  --leading-tight:   1.25;
  --leading-normal:  1.5;
  --leading-relaxed: 1.7;

  /* ── Spacing scale (use these, never raw px in components) ── */
  --sp-1:  4px;
  --sp-2:  8px;
  --sp-3:  12px;
  --sp-4:  16px;
  --sp-5:  20px;
  --sp-6:  24px;
  --sp-8:  32px;
  --sp-10: 40px;
  --sp-12: 48px;
  --sp-16: 64px;

  /* ── Border radius ── */
  --r-xs:   4px;
  --r-sm:   8px;
  --r-md:   12px;
  --r-lg:   16px;
  --r-xl:   20px;
  --r-2xl:  24px;
  --r-pill: 99px;

  /* ── Shadows ── */
  --shadow-xs:     0 1px 2px rgba(0,0,0,0.04);
  --shadow-card:   0 1px 4px rgba(0,0,0,0.06), 0 0 0 0.5px rgba(0,0,0,0.05);
  --shadow-raised: 0 4px 12px rgba(0,0,0,0.08), 0 0 0 0.5px rgba(0,0,0,0.05);
  --shadow-float:  0 8px 24px rgba(13,59,102,0.12), 0 0 0 0.5px rgba(13,59,102,0.06);
  --shadow-bounce: 0 4px 20px rgba(13,59,102,0.25);

  /* ── Z-index ── */
  --z-base:    1;
  --z-card:    10;
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

/* ════════════════════════════════════════
   DARK MODE TOKEN OVERRIDES
   ════════════════════════════════════════ */
@media (prefers-color-scheme: dark) {
  :root {
    --bg-page:        #0F1629;
    --bg-card:        #1A2436;
    --bg-raised:      #212E44;
    --bg-overlay:     rgba(255,255,255,0.03);

    --text-primary:   #EEF2FF;
    --text-secondary: #8899B4;
    --text-tertiary:  #4E6080;
    --text-lemon:     #F0DB6A;  /* brighter on dark for readability */

    --border-light:   rgba(255,255,255,0.07);
    --border-medium:  rgba(255,255,255,0.13);
    --border-strong:  rgba(255,255,255,0.22);
    --border-yale:    #4A90D9;
    --border-lemon:   #C8A800;

    --yale-tint:      rgba(26,109,200,0.18);
    --teal-tint:      rgba(13,148,136,0.18);
    --amber-tint:     rgba(217,119,6,0.18);
    --danger-tint:    rgba(220,38,38,0.18);
    --success-tint:   rgba(22,163,74,0.18);
    --lemon:          #FAF0CA;  /* lemon stays — reads well on dark */

    --shadow-card:    0 1px 4px rgba(0,0,0,0.3), 0 0 0 0.5px rgba(255,255,255,0.05);
    --shadow-raised:  0 4px 16px rgba(0,0,0,0.4);
    --shadow-float:   0 8px 32px rgba(0,0,0,0.5), 0 0 0 0.5px rgba(255,255,255,0.07);
    --shadow-bounce:  0 4px 20px rgba(13,59,102,0.5);
  }
}
```

## 1.1 — Token usage rules

| Token | When to use | Never use for |
|---|---|---|
| `--yale` | Primary CTAs, active states, Bounce avatar bg, nav header bg | Body text on white |
| `--yale-light` | Links, interactive elements, focus rings | Headers or heavy text |
| `--lemon` | Celebration, Bounce contextual messages, "recommended" badge | Error states |
| `--teal` | Success, confirmed states, low-risk indicators | Primary actions |
| `--amber` | Warnings, "simplified" tags, pending states, moderate risk | Errors or success |
| `--danger` | Disruption, cancellation, high risk, errors | Standard warnings |
| `--bg-page` | Page background only | Card backgrounds |
| `--bg-card` | Card surfaces, input backgrounds | Page backgrounds |

---

# PART 2 — TYPOGRAPHY

```css
/* ── Reset ── */
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  color: var(--text-primary);
  background: var(--bg-page);
  line-height: var(--leading-normal);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ── Type utilities ── */
.t-label   { font-size: var(--text-xs);  font-weight: 600; letter-spacing: 0.07em; text-transform: uppercase; color: var(--text-tertiary); }
.t-caption { font-size: var(--text-sm);  color: var(--text-secondary); line-height: var(--leading-normal); }
.t-body    { font-size: var(--text-base); color: var(--text-primary);   line-height: var(--leading-relaxed); }
.t-sub     { font-size: var(--text-base); font-weight: 500; color: var(--text-primary); }
.t-title   { font-size: var(--text-md);  font-weight: 600; color: var(--text-primary); line-height: var(--leading-tight); }
.t-heading { font-size: var(--text-lg);  font-weight: 700; color: var(--text-primary); line-height: var(--leading-tight); letter-spacing: -0.2px; }
.t-hero    { font-size: var(--text-xl);  font-weight: 700; color: var(--text-primary); line-height: var(--leading-tight); letter-spacing: -0.5px; }
.t-display { font-size: var(--text-3xl); font-weight: 800; color: var(--text-primary); line-height: 1.1; letter-spacing: -1px; }
.t-mono    { font-family: var(--font-mono); font-size: var(--text-sm); }

/* ── Colour modifiers ── */
.t-yale    { color: var(--yale); }
.t-lemon   { color: var(--text-lemon); }
.t-teal    { color: var(--teal); }
.t-amber   { color: var(--amber); }
.t-danger  { color: var(--danger); }
.t-muted   { color: var(--text-secondary); }
.t-inverse { color: var(--text-inverse); }
```

**Usage guide for Biz engineers:**

| Screen context | Class to use |
|---|---|
| Screen page title | `.t-hero` |
| Section heading | `.t-heading` |
| Card title | `.t-title` |
| Body paragraph | `.t-body` |
| Secondary/supporting text | `.t-caption` |
| Tags, timestamps, labels | `.t-label` |
| Money amounts (large display) | `.t-display` |
| Bounce messages | `.t-body` (Bounce) or `.t-caption` (contextual) |

---

# PART 3 — LAYOUT AND NAVIGATION

## 3.1 — Page shell

```css
.page-shell {
  max-width: 640px;
  margin: 0 auto;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  background: var(--bg-page);
  position: relative;
  overflow-x: hidden;
}

.page-header {
  position: sticky; top: 0; z-index: var(--z-nav);
  background: var(--bg-card);
  border-bottom: 0.5px solid var(--border-light);
  padding: var(--sp-3) var(--sp-4);
  display: flex; align-items: center; gap: var(--sp-3);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.page-header-yale {
  background: var(--yale); border-bottom: none;
}
.page-header-title { flex: 1; font-size: var(--text-md); font-weight: 600; color: var(--text-primary); }
.page-header-yale .page-header-title { color: white; }
.page-header-back { padding: var(--sp-1); cursor: pointer; color: var(--text-secondary); }
.page-header-yale .page-header-back { color: rgba(255,255,255,0.7); }

.page-content {
  flex: 1;
  padding: var(--sp-4);
  padding-bottom: calc(80px + var(--sp-6) + env(safe-area-inset-bottom));
}
/* When Bounce FAB is visible, bottom padding already covers it */
```

## 3.2 — Phase-adaptive bottom navigation

The bottom nav has three states based on trip phase. CS engineer sets `data-phase` on `.bottom-nav`.

```css
.bottom-nav {
  position: fixed; bottom: 0;
  left: 50%; transform: translateX(-50%);
  width: 100%; max-width: 640px; height: 64px;
  background: var(--bg-card);
  border-top: 0.5px solid var(--border-light);
  display: flex; align-items: center;
  z-index: var(--z-nav);
  padding-bottom: env(safe-area-inset-bottom);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.nav-tab {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; gap: 3px; padding: var(--sp-2) var(--sp-1);
  cursor: pointer; text-decoration: none;
  transition: background var(--t-fast);
  border-radius: var(--r-sm);
  margin: var(--sp-1);
}
.nav-icon  { font-size: 22px; color: var(--text-tertiary); transition: color var(--t-fast); }
.nav-label { font-size: 10px; font-weight: 500; color: var(--text-tertiary); transition: color var(--t-fast); white-space: nowrap; }
.nav-tab.active            { background: var(--lemon); }
.nav-tab.active .nav-icon  { color: var(--yale); }
.nav-tab.active .nav-label { color: var(--yale); font-weight: 700; }

/* ── Phase: Planning ── */
/* Tabs: Home | Group | Chat | Visa | Profile */
[data-phase="planning"] .nav-split { display: none; }
[data-phase="planning"] .nav-map   { display: none; }
[data-phase="planning"] .nav-today { display: none; }

/* ── Phase: Active Trip ── */
/* Tabs: Today | Map | Chat | Split | Alerts */
[data-phase="active"] .nav-home  { display: none; }
[data-phase="active"] .nav-group { display: none; }
[data-phase="active"] .nav-visa  { display: none; }

/* ── Phase: Post-trip ── */
/* Tabs: Home | Summary | Split | DNA | Profile */
[data-phase="post"] .nav-map   { display: none; }
[data-phase="post"] .nav-today { display: none; }
[data-phase="post"] .nav-group { display: none; }
```

Nav tab HTML template — CS engineer shows/hides per phase:

```html
<nav class="bottom-nav" data-phase="planning">
  <a class="nav-tab nav-home active" href="/home">
    <i class="ti ti-home nav-icon" aria-hidden="true"></i>
    <span class="nav-label">Home</span>
  </a>
  <a class="nav-tab nav-group" href="/group">
    <i class="ti ti-users-group nav-icon" aria-hidden="true"></i>
    <span class="nav-label">Group</span>
  </a>
  <a class="nav-tab nav-today" href="/today">
    <i class="ti ti-calendar-today nav-icon" aria-hidden="true"></i>
    <span class="nav-label">Today</span>
  </a>
  <a class="nav-tab nav-map" href="/map">
    <i class="ti ti-map-2 nav-icon" aria-hidden="true"></i>
    <span class="nav-label">Map</span>
  </a>
  <a class="nav-tab nav-split" href="/split">
    <i class="ti ti-receipt-2 nav-icon" aria-hidden="true"></i>
    <span class="nav-label">Split</span>
  </a>
  <a class="nav-tab nav-visa" href="/visa">
    <i class="ti ti-id nav-icon" aria-hidden="true"></i>
    <span class="nav-label">Visa</span>
  </a>
  <a class="nav-tab" href="/chat">
    <i class="ti ti-message-circle-2 nav-icon" aria-hidden="true"></i>
    <span class="nav-label">Bounce</span>
  </a>
  <a class="nav-tab" href="/profile">
    <i class="ti ti-user nav-icon" aria-hidden="true"></i>
    <span class="nav-label">Profile</span>
  </a>
</nav>
```

---

# PART 4 — CORE COMPONENTS

## 4.1 — Cards

```css
.card {
  background: var(--bg-card);
  border-radius: var(--r-lg);
  border: 0.5px solid var(--border-light);
  box-shadow: var(--shadow-card);
  padding: var(--sp-4) var(--sp-5);
  margin-bottom: var(--sp-3);
}
.card-primary  { border-color: var(--yale);        border-width: 1.5px; }
.card-lemon    { background: var(--lemon);          border-color: var(--border-lemon); }
.card-teal     { background: var(--teal-tint);      border-color: var(--teal); }
.card-amber    { background: var(--amber-tint);     border-color: var(--amber); }
.card-danger   { background: var(--danger-tint);    border-color: var(--danger); border-width: 1.5px; }
.card-yale     { background: var(--yale);           border: none; color: white; }
.card-elevated { box-shadow: var(--shadow-raised); }
```

## 4.2 — Unified 3-option recommendation component

This is the most repeated pattern in the app. Flights, accommodation, transport, disruption alternatives, venue swaps. All use this component with context-specific content slots.

```css
.rec-set { display: flex; flex-direction: column; gap: var(--sp-2); margin-bottom: var(--sp-4); }
.rec-set-label {
  font-size: var(--text-xs); font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.07em; color: var(--text-tertiary); margin-bottom: var(--sp-1);
}

.rec-card {
  background: var(--bg-card); border-radius: var(--r-lg);
  border: 1.5px solid var(--border-light);
  padding: var(--sp-4); cursor: pointer;
  transition: border-color var(--t-fast), box-shadow var(--t-fast);
  position: relative;
}
.rec-card:hover     { border-color: var(--border-yale); box-shadow: var(--shadow-raised); }
.rec-card.selected  { border-color: var(--yale); background: var(--yale-tint); box-shadow: var(--shadow-raised); }

/* Recommended — visually elevated */
.rec-card.recommended {
  border-color: var(--yale); border-width: 2px;
  box-shadow: var(--shadow-raised);
}

/* Badge sits at top of recommended card */
.rec-badge {
  position: absolute; top: -10px; left: var(--sp-4);
  background: var(--yale); color: var(--lemon);
  font-size: var(--text-xs); font-weight: 700;
  padding: 3px 10px; border-radius: var(--r-pill);
  letter-spacing: 0.04em;
}

/* Tier label inside card */
.rec-tier {
  font-size: var(--text-xs); font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.07em;
  margin-bottom: var(--sp-2);
}
.rec-tier.budget    { color: var(--text-tertiary); }
.rec-tier.recommend { color: var(--yale); }
.rec-tier.premium   { color: #8B6914; }  /* warm gold */

.rec-title   { font-size: var(--text-md); font-weight: 600; color: var(--text-primary); margin-bottom: var(--sp-1); }
.rec-details { font-size: var(--text-sm); color: var(--text-secondary); line-height: var(--leading-normal); }
.rec-meta    { display: flex; justify-content: space-between; align-items: center; margin-top: var(--sp-3); padding-top: var(--sp-3); border-top: 0.5px solid var(--border-light); }
.rec-price   { font-size: var(--text-md); font-weight: 700; color: var(--text-primary); }
.rec-price small { font-size: var(--text-xs); color: var(--text-tertiary); display: block; font-weight: 400; }
.rec-select-btn {
  padding: 7px 16px; border-radius: var(--r-pill);
  background: var(--yale); color: white;
  font-size: var(--text-sm); font-weight: 600;
  border: none; cursor: pointer;
  transition: background var(--t-fast);
}
.rec-select-btn:hover { background: #0a2f52; }
.rec-card.selected .rec-select-btn { background: var(--teal); }
```

Usage template (works for flights, accommodation, transport, alternatives):

```html
<div class="rec-set">
  <p class="rec-set-label">Choose your flight</p>

  <div class="rec-card">
    <div class="rec-tier budget">Budget</div>
    <div class="rec-title">United UA838 · 14h 20m</div>
    <div class="rec-details">1 stop · SFO → IAH → NRT · Departs 10:30am</div>
    <div class="rec-meta">
      <div class="rec-price">$680 <small>per person · est.</small></div>
      <button class="rec-select-btn">Select</button>
    </div>
  </div>

  <div class="rec-card recommended">
    <div class="rec-badge">Bounce's pick</div>
    <div class="rec-tier recommend">Recommended</div>
    <div class="rec-title">ANA NH106 · 11h 45m</div>
    <div class="rec-details">Direct · SFO → NRT · Departs 11:55am · Low risk</div>
    <div class="rec-meta">
      <div class="rec-price">$890 <small>per person · est.</small></div>
      <button class="rec-select-btn">Select</button>
    </div>
  </div>

  <div class="rec-card">
    <div class="rec-tier premium">Premium</div>
    <div class="rec-title">ANA NH106 Business · 11h 45m</div>
    <div class="rec-details">Direct · SFO → NRT · Departs 11:55am · Lie-flat seats</div>
    <div class="rec-meta">
      <div class="rec-price">$2,840 <small>per person · est.</small></div>
      <button class="rec-select-btn">Select</button>
    </div>
  </div>
</div>
```

## 4.3 — Chips and tags

```css
/* Selectable chip */
.chip {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 7px 14px; border-radius: var(--r-pill);
  font-size: var(--text-sm); font-weight: 500;
  border: 1.5px solid var(--border-light);
  background: var(--bg-card); color: var(--text-secondary);
  cursor: pointer; transition: all var(--t-fast); user-select: none;
}
.chip:hover    { border-color: var(--yale-light); color: var(--yale); }
.chip.selected { border-color: var(--yale); background: var(--yale-tint); color: var(--yale); font-weight: 600; }
.chip.selected::before { content: '✓ '; font-size: 11px; }

/* Status tag */
.tag {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 9px; border-radius: var(--r-pill);
  font-size: var(--text-xs); font-weight: 600;
  border: 0.5px solid; white-space: nowrap;
}
.tag-yale    { background: var(--yale-tint);   color: var(--yale);         border-color: var(--yale-light); }
.tag-teal    { background: var(--teal-tint);   color: var(--teal-text);    border-color: var(--teal); }
.tag-lemon   { background: var(--lemon);       color: var(--text-lemon);   border-color: var(--border-lemon); }
.tag-amber   { background: var(--amber-tint);  color: var(--amber-text);   border-color: var(--amber); }
.tag-danger  { background: var(--danger-tint); color: var(--danger-text);  border-color: var(--danger); }
.tag-muted   { background: var(--bg-page);     color: var(--text-tertiary);border-color: var(--border-light); }
```

## 4.4 — Buttons

```css
.btn {
  display: inline-flex; align-items: center; justify-content: center;
  gap: var(--sp-2); padding: 12px 24px; border-radius: var(--r-md);
  font-size: var(--text-base); font-weight: 600;
  cursor: pointer; transition: all var(--t-fast);
  border: none; text-decoration: none; white-space: nowrap;
  -webkit-tap-highlight-color: transparent;
}
.btn-primary   { background: var(--yale); color: white; }
.btn-primary:hover   { background: #0a2f52; }
.btn-primary:active  { transform: scale(0.98); }
.btn-secondary { background: transparent; color: var(--yale); border: 1.5px solid var(--yale); }
.btn-secondary:hover { background: var(--yale-tint); }
.btn-lemon     { background: var(--lemon); color: var(--yale); border: 1px solid var(--border-lemon); }
.btn-lemon:hover     { background: var(--lemon-dark); }
.btn-teal      { background: var(--teal); color: white; }
.btn-danger    { background: var(--danger); color: white; }
.btn-ghost     { background: transparent; color: var(--text-secondary); border: 1.5px solid var(--border-light); }
.btn-ghost:hover     { border-color: var(--border-medium); color: var(--text-primary); }
.btn-full   { width: 100%; }
.btn-sm     { padding: 8px 16px; font-size: var(--text-sm); border-radius: var(--r-sm); }
.btn-lg     { padding: 16px 32px; font-size: var(--text-md); border-radius: var(--r-lg); }
```

## 4.5 — Inputs and form elements

```css
.input-group  { display: flex; flex-direction: column; gap: var(--sp-2); margin-bottom: var(--sp-4); }
.input-label  { font-size: var(--text-sm); font-weight: 500; color: var(--text-primary); }
.input-hint   { font-size: var(--text-xs); color: var(--text-tertiary); margin-top: var(--sp-1); }

.input {
  width: 100%; padding: 12px 16px;
  border-radius: var(--r-md); border: 1.5px solid var(--border-light);
  background: var(--bg-card); font-size: var(--text-base);
  font-family: var(--font-sans); color: var(--text-primary);
  outline: none; transition: border-color var(--t-fast);
}
.input:focus         { border-color: var(--yale-light); }
.input::placeholder  { color: var(--text-tertiary); }
.input:disabled      { background: var(--bg-page); color: var(--text-tertiary); cursor: not-allowed; }
.input.error         { border-color: var(--danger); }

/* Animated chat-synced form state */
.input.bounce-updated {
  animation: bounceFieldUpdate 600ms ease;
}
@keyframes bounceFieldUpdate {
  0%,100% { border-color: var(--border-light); }
  30%,70% { border-color: var(--yale-light); background: var(--yale-tint); }
}

/* Toggle */
.toggle-row    { display: flex; align-items: center; justify-content: space-between; padding: var(--sp-3) 0; border-bottom: 0.5px solid var(--border-light); }
.toggle-row:last-child { border-bottom: none; }
.toggle-info   { flex: 1; padding-right: var(--sp-4); }
.toggle-title  { font-size: var(--text-base); font-weight: 500; color: var(--text-primary); }
.toggle-desc   { font-size: var(--text-sm); color: var(--text-secondary); margin-top: 2px; }
.toggle-switch {
  width: 44px; height: 26px; border-radius: 13px;
  background: var(--border-medium); position: relative;
  cursor: pointer; transition: background var(--t-normal); flex-shrink: 0;
}
.toggle-switch.on { background: var(--yale); }
.toggle-switch::after {
  content: ''; width: 20px; height: 20px; border-radius: 50%;
  background: white; position: absolute; top: 3px; left: 3px;
  transition: transform var(--t-normal);
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
.toggle-switch.on::after { transform: translateX(18px); }
```

---

# PART 5 — BOUNCE PERSONA UI

## 5.1 — Avatar system

```css
.bounce-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--yale); display: flex; align-items: center;
  justify-content: center; color: var(--lemon);
  font-weight: 800; font-size: 15px; flex-shrink: 0;
  user-select: none;
}
.bounce-avatar-sm { width: 28px; height: 28px; font-size: 12px; }
.bounce-avatar-lg { width: 56px; height: 56px; font-size: 22px; box-shadow: var(--shadow-bounce); }
/* Human member avatar */
.member-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--yale-tint); color: var(--yale);
  font-weight: 700; font-size: 13px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
```

## 5.2 — Bounce floating action button

```css
.bounce-fab {
  position: fixed; bottom: calc(72px + env(safe-area-inset-bottom));
  right: var(--sp-5); width: 56px; height: 56px;
  border-radius: 50%; background: var(--yale);
  display: flex; align-items: center; justify-content: center;
  box-shadow: var(--shadow-bounce); cursor: pointer;
  z-index: var(--z-chat); transition: transform var(--t-fast);
}
.bounce-fab:hover  { transform: scale(1.06); }
.bounce-fab:active { transform: scale(0.94); }
.bounce-fab .fab-icon { color: var(--lemon); font-size: 24px; }

/* Unread badge */
.bounce-fab-badge {
  position: absolute; top: 0; right: 0;
  width: 18px; height: 18px; border-radius: 50%;
  background: var(--danger); color: white;
  font-size: 10px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  border: 2px solid var(--bg-page);
}

/* Proactive pulse */
.bounce-fab.has-alert::before {
  content: ''; position: absolute; inset: -5px;
  border-radius: 50%; border: 2px solid var(--yale-light);
  animation: pulse-ring 1.8s ease infinite;
}
@keyframes pulse-ring {
  0%   { transform: scale(0.9); opacity: 0.8; }
  70%  { transform: scale(1.2); opacity: 0; }
  100% { transform: scale(1.2); opacity: 0; }
}
```

## 5.3 — Bounce slide-up chat panel

Panel has two thread tabs: Main Trip and (if in FlockMode) My Flock.

```css
/* Overlay backdrop */
.bounce-backdrop {
  position: fixed; inset: 0; background: rgba(15,22,41,0.5);
  z-index: calc(var(--z-chat) - 1); opacity: 0;
  pointer-events: none; transition: opacity var(--t-normal);
}
.bounce-backdrop.open { opacity: 1; pointer-events: all; }

/* Panel */
.bounce-panel {
  position: fixed; bottom: 0;
  left: 50%; transform: translateX(-50%) translateY(100%);
  width: 100%; max-width: 640px; height: 82dvh;
  background: var(--bg-card);
  border-radius: var(--r-2xl) var(--r-2xl) 0 0;
  z-index: var(--z-chat); display: flex; flex-direction: column;
  box-shadow: var(--shadow-float);
  transition: transform var(--t-slow);
}
.bounce-panel.open { transform: translateX(-50%) translateY(0); }

/* Drag handle */
.panel-handle {
  width: 36px; height: 4px; border-radius: 2px;
  background: var(--border-medium); margin: var(--sp-3) auto var(--sp-2);
  flex-shrink: 0;
}

/* Thread tabs — only shown when FlockMode is active */
.thread-tabs {
  display: flex; gap: 0; padding: 0 var(--sp-4) var(--sp-2);
  border-bottom: 0.5px solid var(--border-light); flex-shrink: 0;
}
.thread-tab {
  flex: 1; padding: var(--sp-2) var(--sp-3); text-align: center;
  font-size: var(--text-sm); font-weight: 500; color: var(--text-secondary);
  border-bottom: 2px solid transparent; cursor: pointer;
  transition: all var(--t-fast);
}
.thread-tab.active {
  color: var(--yale); font-weight: 600;
  border-bottom-color: var(--yale);
}

/* Messages area */
.bounce-messages {
  flex: 1; overflow-y: auto; padding: var(--sp-4) var(--sp-4) var(--sp-2);
  display: flex; flex-direction: column; gap: var(--sp-3);
  scroll-behavior: smooth;
}

/* Message bubbles */
.msg { display: flex; gap: var(--sp-2); align-items: flex-end; }
.msg-bounce { flex-direction: row; }
.msg-user   { flex-direction: row-reverse; }

.msg-bubble {
  max-width: 78%; padding: 10px 14px;
  border-radius: var(--r-lg); font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
}
.msg-bounce .msg-bubble {
  background: var(--bg-page); color: var(--text-primary);
  border-radius: 4px var(--r-lg) var(--r-lg) var(--r-lg);
}
.msg-user .msg-bubble {
  background: var(--yale); color: white;
  border-radius: var(--r-lg) 4px var(--r-lg) var(--r-lg);
}
.msg-time { font-size: 10px; color: var(--text-tertiary); margin-top: 3px; padding: 0 var(--sp-1); }

/* Suggestion indicator on member messages */
.msg-suggestion-tag {
  display: inline-flex; align-items: center; gap: 4px;
  background: var(--amber-tint); color: var(--amber-text);
  font-size: 10px; font-weight: 600; padding: 2px 8px;
  border-radius: var(--r-pill); margin-top: var(--sp-1);
}

/* Typing indicator */
.bounce-typing { display: flex; gap: 4px; align-items: center; padding: 12px 14px; }
.bounce-typing span {
  width: 7px; height: 7px; border-radius: 50%; background: var(--text-tertiary);
  animation: typing-dot 1.2s ease infinite;
}
.bounce-typing span:nth-child(2) { animation-delay: 0.2s; }
.bounce-typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing-dot { 0%,80%,100%{transform:scale(0.7);opacity:0.3} 40%{transform:scale(1);opacity:1} }

/* Input bar */
.bounce-input-bar {
  display: flex; gap: var(--sp-2); align-items: flex-end;
  padding: var(--sp-3) var(--sp-4);
  padding-bottom: max(var(--sp-4), env(safe-area-inset-bottom));
  border-top: 0.5px solid var(--border-light);
  flex-shrink: 0;
}
.bounce-textarea {
  flex: 1; min-height: 40px; max-height: 120px;
  padding: 10px 14px; border-radius: 20px;
  border: 1.5px solid var(--border-light);
  background: var(--bg-page); resize: none;
  font-size: var(--text-base); font-family: var(--font-sans);
  color: var(--text-primary); outline: none;
  transition: border-color var(--t-fast);
}
.bounce-textarea:focus { border-color: var(--yale-light); }
.bounce-send {
  width: 40px; height: 40px; border-radius: 50%; border: none;
  background: var(--yale); cursor: pointer; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  transition: all var(--t-fast);
}
.bounce-send:hover { background: #0a2f52; transform: scale(1.05); }
.bounce-send:disabled { background: var(--border-light); cursor: not-allowed; transform: none; }
```

## 5.4 — Progressive loading messages

When Bounce is running a multi-step operation (itinerary generation: 20–30s), show streaming intermediate messages instead of a skeleton. Each line appears after the previous one completes.

```css
.bounce-loading-panel {
  background: var(--bg-card); border-radius: var(--r-lg);
  border: 0.5px solid var(--border-light); padding: var(--sp-5);
  margin-bottom: var(--sp-3);
}
.bounce-loading-header {
  display: flex; align-items: center; gap: var(--sp-3); margin-bottom: var(--sp-4);
}
.bounce-loading-title { font-size: var(--text-base); font-weight: 500; color: var(--yale); }

.loading-step {
  display: flex; align-items: center; gap: var(--sp-3);
  padding: var(--sp-2) 0; opacity: 0;
  animation: stepAppear 300ms ease forwards;
}
.loading-step:nth-child(1) { animation-delay: 0ms; }
.loading-step:nth-child(2) { animation-delay: 1800ms; }
.loading-step:nth-child(3) { animation-delay: 4200ms; }
.loading-step:nth-child(4) { animation-delay: 7000ms; }
.loading-step:nth-child(5) { animation-delay: 10500ms; }

@keyframes stepAppear {
  from { opacity: 0; transform: translateX(-8px); }
  to   { opacity: 1; transform: translateX(0); }
}

.step-icon {
  width: 20px; height: 20px; border-radius: 50%;
  background: var(--yale-tint); color: var(--yale);
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; flex-shrink: 0;
}
.step-text { font-size: var(--text-sm); color: var(--text-secondary); }
.step-text.done { color: var(--text-tertiary); }
.step-check { font-size: 14px; color: var(--teal); margin-left: auto; }
```

Usage in JS: append steps progressively as tool responses stream in:
```javascript
const steps = [
  "Mapping Tokyo venues...",
  "Checking everyone's dietary needs...",
  "Building Day 1 around your arrivals...",
  "Optimising routes across 10 days...",
  "Reviewing energy and pacing..."
];
// Append each step when the corresponding agent tool responds
```

## 5.5 — Bounce contextual messages (inline, not chat)

```css
.bounce-say {
  display: flex; align-items: flex-start; gap: var(--sp-3);
  padding: var(--sp-3) var(--sp-4);
  background: var(--lemon); border-left: 3px solid var(--border-lemon);
  border-radius: 0 var(--r-md) var(--r-md) 0;
  margin-bottom: var(--sp-3);
}
.bounce-say p { font-size: var(--text-sm); color: var(--yale); line-height: var(--leading-relaxed); }
.bounce-say strong { font-weight: 600; }

/* Critical/disruption variant */
.bounce-say.danger {
  background: var(--danger-tint); border-left-color: var(--danger);
}
.bounce-say.danger p { color: var(--danger-text); }
```

---

# PART 6 — USER JOURNEY MAP

## 6.1 — Full journey (text flow diagram)

```
LANDING
  └── Auth/name entry screen
       ├── [New user] → Entry conversation with Bounce
       └── [Returning user] → Dashboard (last trip state)

ENTRY CONVERSATION
  └── Bounce extracts: destination, type (friends/family/office),
      mode (international/domestic), size, budget, occasion
       ├── [Solo] → Profile completion → Planning
       └── [Group] → Group setup

GROUP SETUP (organiser)
  └── Invite link generated → organiser shares
       ├── [Members open link] → Member join flow
       └── [All joined] → Preference synthesis shown to admins
           └── Organiser confirms → Profile completion (all)

MEMBER JOIN FLOW (separate entry point)
  └── Bounce welcome (trip context shown) → member's profile entry
       └── Profile complete → "You're in" confirmation
           └── Waits in group status view until organiser starts planning

PROFILE COMPLETION
  └── Gap-fill only what Bounce doesn't know
       ├── [International] → Visa compliance surfaced privately per member
       └── All done → Planning

PLANNING
  ├── Itinerary + accommodation + map generated together (progressive loading)
  ├── Transport planning (multi-modal options)
  ├── Flight selection (3 options per origin city)
  └── Trip confirmed → sharing + emergency card

PRE-DEPARTURE
  └── Per-member departure brief → reminders fire from Cloud Scheduler

ACTIVE TRIP (phase changes nav)
  ├── Daily companion view (today's schedule + map)
  ├── FlockMode (organiser-initiated) → Flock active views → reconvene → end
  ├── Disruption (Pub/Sub fires) → disruption sheet → alternative selected → back to today
  ├── Split bill (ongoing)
  └── Flight status tracking (AeroDataBox polling)

RETURN JOURNEY
  └── Last-day logistics view → members depart

POST-TRIP
  └── Spending summary → settlement → Travel DNA cards → next trip seeds
```

## 6.2 — Navigation state transitions

CS engineer fires these transitions when trip phase changes:

```javascript
function setPhase(phase) {
  // 'planning' | 'active' | 'post'
  document.querySelector('.bottom-nav').dataset.phase = phase;
  // Also update FAB visibility, page header style
}

// Triggered events:
// 'planning' → entry conversation complete
// 'active'   → departure date reached (or organiser taps "Start trip")
// 'post'     → return date reached (or organiser taps "Trip complete")
```

---

# PART 7 — MAP DESIGN SPECIFICATION

## 7.1 — Custom venue pin

Replace default Google Maps teardrops with numbered circle markers.

```javascript
// In Maps JS API
function createVenueMarker(map, position, number, isAccom, isCurrent) {
  const color = isCurrent ? '#0D9488'    // teal for current activity
              : isAccom   ? '#FAF0CA'    // lemon for accommodation
              :             '#0D3B66';   // yale for venues

  const textColor = isAccom ? '#0D3B66' : '#FFFFFF';

  const marker = new google.maps.marker.AdvancedMarkerElement({
    position,
    map,
    content: buildPinElement(number, color, textColor, isCurrent),
  });
  return marker;
}

function buildPinElement(number, bg, fg, pulse) {
  const div = document.createElement('div');
  div.className = `map-pin ${pulse ? 'map-pin-current' : ''}`;
  div.style.cssText = `
    width:32px; height:32px; border-radius:50%;
    background:${bg}; color:${fg};
    display:flex; align-items:center; justify-content:center;
    font-size:13px; font-weight:700; font-family:sans-serif;
    border:2.5px solid white; box-shadow:0 2px 8px rgba(0,0,0,0.25);
    cursor:pointer;
  `;
  div.textContent = number;
  return div;
}
```

```css
/* Current activity pin pulses */
.map-pin-current { animation: map-pin-pulse 2s ease infinite; }
@keyframes map-pin-pulse {
  0%,100% { box-shadow: 0 2px 8px rgba(13,148,136,0.3); }
  50%      { box-shadow: 0 2px 16px rgba(13,148,136,0.7), 0 0 0 6px rgba(13,148,136,0.15); }
}

/* Accommodation pin — larger, house icon */
.map-pin-accom {
  width: 38px; height: 38px;
  background: var(--lemon);
  border: 2.5px solid var(--yale);
}
```

## 7.2 — Route line

```javascript
// Recommended route between stops
const routePath = new google.maps.Polyline({
  path: coordinates,
  geodesic: false,
  strokeColor: '#0D3B66',      // yale
  strokeOpacity: 0.7,
  strokeWeight: 3,
  icons: [{
    icon: {
      path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
      scale: 3, strokeColor: '#0D3B66', strokeWeight: 1.5
    },
    offset: '50%',
    repeat: '120px'
  }]
});
```

## 7.3 — Venue callout card

Appears above the pin when tapped. Close on map tap elsewhere.

```css
.map-callout {
  position: absolute; bottom: calc(100% + 10px);
  left: 50%; transform: translateX(-50%);
  width: 220px; background: var(--bg-card);
  border-radius: var(--r-lg); box-shadow: var(--shadow-raised);
  border: 0.5px solid var(--border-light); padding: var(--sp-3);
  z-index: 10; animation: calloutAppear 150ms ease forwards;
}
.map-callout::after {
  content: ''; position: absolute; bottom: -7px; left: 50%;
  transform: translateX(-50%);
  border-left: 7px solid transparent; border-right: 7px solid transparent;
  border-top: 7px solid var(--bg-card);
}
@keyframes calloutAppear {
  from { opacity: 0; transform: translateX(-50%) translateY(4px); }
  to   { opacity: 1; transform: translateX(-50%) translateY(0); }
}
.callout-name   { font-size: var(--text-sm); font-weight: 600; color: var(--text-primary); margin-bottom: 3px; }
.callout-time   { font-size: var(--text-xs); color: var(--text-tertiary); margin-bottom: var(--sp-2); }
.callout-actions { display: flex; gap: var(--sp-2); }
.callout-nav-btn {
  flex: 1; padding: 6px; border-radius: var(--r-sm);
  background: var(--yale); color: white;
  font-size: var(--text-xs); font-weight: 600;
  border: none; cursor: pointer; text-align: center;
}
.callout-swap-btn {
  flex: 1; padding: 6px; border-radius: var(--r-sm);
  background: var(--bg-page); color: var(--yale);
  font-size: var(--text-xs); font-weight: 600;
  border: 1px solid var(--border-light); cursor: pointer; text-align: center;
}
```

## 7.4 — Transport mode selector (map overlay)

```css
.map-mode-selector {
  position: absolute; top: var(--sp-3); right: var(--sp-3);
  display: flex; flex-direction: column; gap: var(--sp-1);
  z-index: 5;
}
.map-mode-btn {
  width: 36px; height: 36px; border-radius: var(--r-sm);
  background: var(--bg-card); border: 0.5px solid var(--border-light);
  box-shadow: var(--shadow-card); display: flex; align-items: center;
  justify-content: center; cursor: pointer; font-size: 18px;
  color: var(--text-secondary); transition: all var(--t-fast);
}
.map-mode-btn.active { background: var(--yale); color: var(--lemon); border-color: var(--yale); }
.map-mode-btn:hover  { border-color: var(--yale-light); color: var(--yale); }
```

---

# PART 8 — SCREEN SPECIFICATIONS

## Screen 0 — Auth / Name entry

First screen ever. Simple. Bounce introduces itself. User enters name only — no password for hackathon.

```
[Full-height Yale Blue background]
  [Bounce logo 56px centered, top third]
  [Wordmark "Bounce" below logo]
  [Tagline: "Your group travel genius" — white, 60% opacity]

[White card, bottom half, rounded corners top-only]
  [Bounce says:] "I'm Bounce — your AI travel companion.
   Before we go anywhere, what's your name?"

  [Name input — large, centered]
  [Placeholder: "Alex, Priya, Marcus..."]

  [CTA button — full width: "Let's go →"]

[Small print below button]
  "Bounce stores your travel preferences to personalise your trips.
   We don't sell your data or share it outside your travel group."
```

```css
.auth-screen {
  min-height: 100dvh; background: var(--yale);
  display: flex; flex-direction: column; align-items: center;
  padding: var(--sp-12) var(--sp-6) 0;
}
.auth-logo-wrap { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.auth-wordmark  { font-size: 36px; font-weight: 800; color: white; letter-spacing: -1px; margin-top: var(--sp-4); }
.auth-wordmark span { color: var(--lemon); }
.auth-tagline   { font-size: 15px; color: rgba(255,255,255,0.6); margin-top: var(--sp-2); }
.auth-card {
  width: 100%; background: var(--bg-card);
  border-radius: var(--r-2xl) var(--r-2xl) 0 0;
  padding: var(--sp-6) var(--sp-5) var(--sp-8);
  box-shadow: var(--shadow-float);
}
.auth-name-input {
  width: 100%; border: none; border-bottom: 2px solid var(--border-light);
  background: transparent; font-size: var(--text-2xl); font-weight: 700;
  color: var(--text-primary); outline: none; padding: var(--sp-3) 0;
  text-align: center; transition: border-color var(--t-fast);
}
.auth-name-input:focus    { border-bottom-color: var(--yale); }
.auth-name-input::placeholder { color: var(--border-medium); font-weight: 400; font-size: var(--text-lg); }
.auth-privacy { font-size: var(--text-xs); color: var(--text-tertiary); text-align: center; margin-top: var(--sp-3); line-height: var(--leading-relaxed); }
```

---

## Screen 1 — Entry conversation

Primary action: type naturally. Bounce responds. Quick-select chips for common inputs.

```
[Yale Blue header]
  [Bounce wordmark + wordmark]
  [Group type chips: Friends | Family | Office] (scrollable row)

[White card pulled up, overlapping header]
  [Bounce contextual message: "Tell me about your trip. I'll figure out the rest."]
  [Large textarea — min 3 lines]
  [Send button — Yale Blue pill, right-aligned]

[Quick-select chips below input]
  Row 1: [Beach] [City] [Mountains] [Culture] [Adventure]
  Row 2: [International] [Domestic]
  [Group size stepper: — 8 +  "people"]

[Bounce typing indicator while processing]
[Bounce response bubble appears below]
```

---

## Screen 1b — Member join flow (opens from invite link)

```
[Yale Blue hero — same as auth but different content]
  [Bounce logo]
  [Trip name: "The Tokyo Reunion"]
  [Organiser name: "Alex invited you"]
  [Destination + dates chip]
  [Members already in: [avatar chips: Alex, Priya, Marcus...]]

[White card below]
  [Bounce says:] "Hey! Alex is planning a trip to Tokyo.
   I need a few things from you before I can add you to the group."

  [CTA: "Join the trip →"] — full width, Yale Blue
```

After tapping Join: run same conversational entry as Screen 1, then profile completion. On completion, show:

```
[Full-screen lemon card]
  [Large ✓ icon — teal]
  [Heading: "You're in!"]
  [Bounce says: "Welcome to the group. As soon as everyone
   joins, I'll start building the trip."]
  [Group status: "7 of 10 members joined — waiting for Carlos, Liam, Rania"]
  [Member avatar row]
```

---

## Screen 2 — Group setup (organiser view)

```
[Page header: "Your group" — Yale]

[Invite card — lemon background]
  "Share this with your group"
  [Link field + copy button]
  [Status: "7 of 10 joined"]
  [Progress bar: 70% — teal fill]

[Admin controls card]
  "Co-leaders (up to 2)"
  [Member list with "Assign" toggles]
  [Priya Patel — toggle ON — Co-leader badge]

[Member list]
  [One member card per person]
  [Member card: avatar + name + origin + role badge + status badge]
  [Admin-only: amber dot if compliance action needed]

[Bounce contextual] 
  "High food/culture alignment across the group. 
   3 members need visa applications before you travel."
  [This shows only to organiser/co-leaders]

[CTA: "Begin planning →"] — active when all members joined
```

---

## Screen 3 — Profile completion

Bounce pre-fills from conversation. User sees only genuine gaps.

```
[Page header: "Quick details — Alex" with progress steps]
[Step indicator: 1 of 3 steps]

Step 1 — Dietary
  [Bounce says: "I caught that you eat halal. Anything else?"]
  [Chip grid: Vegetarian | Vegan | Gluten-free | Kosher | No pork | No beef | No alcohol | None]
  [Strictness toggle if halal/kosher/vegan selected]

Step 2 — Interests (for itinerary matching)
  [Chip grid: History | Art | Food | Nightlife | Nature | Shopping | Music | Architecture | Sport | Wellness]

Step 3 — Observance & optional
  [Toggle: "I have daily schedule needs (prayer times, etc.)"]
  [Toggle: "I have mobility considerations"]
  [Toggle: "Notify someone when I travel"]
  [→ each toggle reveals a form when ON]

[CTA: "Save my details →"] — saves and returns to planning or group join
```

**Compliance view (private — auto-shown after profile for international trips):**

```
[Private amber banner at top]
  "Just for you — this won't be shared with the group"

[Compliance card]
  [Country flag — India]
  [Heading: "Japan entry requirements for Indian passport holders"]
  [Status: VISA REQUIRED — amber tag]

  [Detail rows:]
  Visa type:      Consulate tourist visa
  Processing:     10–14 business days
  Apply by:       [auto-calculated date]
  Official link:  [Japan Embassy India]
  Fee estimate:   $25

  [CTA: "Go to embassy website ↗"] — validated external link only
  [Small print: "Verify with the embassy — requirements may change."]
```

---

## Screen 4 — Itinerary view (planning phase)

```
[Sticky day tab strip]
  Day 1 | Day 2 | Day 3 ... | Day 10
  [Tab shows date + weather icon + flock bird if FlockMode day]

[Accommodation strip — always top of day]
  [Hotel icon] [Name] [3-star tag] [¥XX,XXX est./night]
  [Tap to see 3-option accommodation rec-set]

[Weather bar]
  [Condition icon] [28°C / 19°C] [20% rain]

[Timeline — see Part 4 for CSS]
  Each venue card shows:
    - Time range (destination timezone — always note "Tokyo time")
    - Venue name + category tag
    - Reasoning in italic muted text (1 line)
    - Customs chip if temple/religious (tap to expand)
    - Booking badge if advance booking required
    - Swap link → opens 3-option rec-set inline

[Google Maps embed section]
  [Mode buttons: transit icon | walk icon | car icon]
  [Map with numbered pins]
  [Route line — yale blue, directional arrows]
  ["Open in Google Maps ↗" button below map]

[Budget bar]
  Day X budget: $XXX used of $XXX
  [Progress bar — teal under 60%, amber 60-80%, danger 80%+]

[Sticky bottom bar (inside page content, above nav)]
  [← Previous day] [Day X of 10] [Next day →]
```

---

## Screen 5 — FlockMode creation

Organiser taps "Split into Flocks" on any planning day.

```
[Sheet slides up — full height]
  [Header: "Create Flocks for Day 5"]
  [Bounce says: "Split your group into smaller flocks for parallel adventures.
   They'll reconvene at a time and place you set."]

  [Unassigned members pool — chip grid]
    [Alex] [Priya] [Marcus] [Sofia] [Jake] [Aditya] [Emma] [Carlos] [Liam] [Rania]

  [3 Flock boxes below (+ button to add more, max 5)]
  ┌─────────────────────────────┐
  │ Flock 1                     │ ← tap to rename inline
  │ [Drop zone — dashed border] │
  │ [Member chips added here]   │
  └─────────────────────────────┘
  [+ Add another Flock]

  [Reconvene section]
  Time: [time picker — 6:30 PM]
  Where: [text input — "Shinjuku Station East Exit"]

  [CTA: "Start FlockMode →"] — disabled until all members assigned
```

```css
.flock-dropzone {
  min-height: 60px; border: 2px dashed var(--border-medium);
  border-radius: var(--r-md); padding: var(--sp-3);
  display: flex; flex-wrap: wrap; gap: var(--sp-1);
  align-items: flex-start; align-content: flex-start;
  transition: border-color var(--t-fast), background var(--t-fast);
}
.flock-dropzone.has-members { border-color: var(--yale); background: var(--yale-tint); }
.flock-name-input {
  border: none; background: transparent; font-size: var(--text-base);
  font-weight: 600; color: var(--text-primary); width: 100%;
  outline: none; padding: var(--sp-2) 0;
}
```

---

## Screen 6 — FlockMode active (member view)

Each member sees their own Flock's schedule, not others'.

```
[Yale Blue header with flock bird icon]
  "The Explorers" (Flock 1)
  [Member chips: Alex, Priya, Aditya, Emma]

[Reconvene countdown card]
  "Meet at Shinjuku Station East Exit"
  [Large countdown timer: 3h 42m]
  [Transit estimate: "~18 min by Yamanote Line from teamLab"]

[Today's Flock schedule — same timeline component as main itinerary]
  [Venues relevant to THIS Flock only]

[Per-Flock map — venues pinned for Flock 1 only]

[Thread tab in Bounce panel: "The Explorers" thread active]

[Budget: "Flock 1 spend: $XXX today"]
```

---

## Screen 7 — Active trip daily view (non-FlockMode)

```
[Flight status banner if any member in transit]
  [Scheduled: teal | Delayed: amber | Cancelled: danger]
  "NH106 SFO → NRT · On time · Lands 4:50pm"

[Current activity card — Yale Blue border, teal "NOW" pulse badge]
  NOW ●  [Venue name]  [Time range]
  [Transit to next: 15 min by metro →]

[Today's remaining schedule — condensed timeline]

[In-app map — current position area, next 2 venues pinned]
  ["Open in Google Maps ↗"]

[Ask Bounce button — lemon background, prominent]
  "Ask Bounce anything about today →"
  [Examples rotate: "Is tap water safe?", "Best halal dinner nearby?"]

[Budget tracker — per person]
[Quick expense add button]
```

---

## Screen 8 — Disruption response flow

**Step 1: Disruption arrives** — Pub/Sub event triggers Firebase update.
Toast fires at top of screen (danger style). Bounce FAB pulses.

**Step 2: User taps toast or FAB.** Bounce panel opens automatically on disruption thread. Bounce message reads:

"Heads up — teamLab Borderless is showing as closed today for a private event. I've already found 3 alternatives nearby. Want to see them?"

**Step 3: Disruption sheet slides up.**

```
[Disruption sheet]
  [Danger icon wrap + title + description]
  "teamLab Borderless · Unexpected closure"

  [Bounce explains]
  "You have about 4 hours before your next commitment.
   Here are 3 alternatives within 20 minutes of your location."

  [3-option rec-set — disruption context]
    Budget: Ueno Park · 5 min walk · Free · 2–3 hrs
    Recommended: Mori Art Museum · 18 min by metro · ¥2,000 · 2 hrs · Great views
    Premium: teamLab Planets Toyosu · 22 min by metro · ¥3,200 · 2 hrs · Similar experience

  [Each card shows: transit time, cost, duration, reason Bounce picked it]
  [CTA per card: "Go here →"]

  [After selection: confirmation screen]
  "Mori Art Museum added to Day 7. Everyone in the group has been updated."
  [Firebase has already broadcast. Show member avatar row — all green.]
```

**Step 4: Return to today view.** Itinerary reflects new venue. Success toast fires.

```css
.disruption-overlay { position: fixed; inset: 0; background: rgba(15,22,41,0.6); z-index: var(--z-overlay); display: flex; align-items: flex-end; }
.disruption-sheet {
  width: 100%; max-width: 640px; margin: 0 auto;
  background: var(--bg-card);
  border-radius: var(--r-2xl) var(--r-2xl) 0 0;
  padding: var(--sp-6) var(--sp-5);
  padding-bottom: max(var(--sp-8), env(safe-area-inset-bottom));
  max-height: 92dvh; overflow-y: auto;
  animation: sheetUp var(--t-slow) forwards;
}
@keyframes sheetUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
```

---

## Screen 9 — Suggestion review panel (admin view)

Appears as a card at top of itinerary or as a Bounce notification in the admin's chat.

```css
.suggestion-panel {
  background: var(--lemon); border: 1px solid var(--border-lemon);
  border-radius: var(--r-lg); padding: var(--sp-4); margin-bottom: var(--sp-3);
}
.suggestion-panel-header {
  display: flex; align-items: center; gap: var(--sp-3); margin-bottom: var(--sp-3);
}
.suggestion-count-badge {
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--yale); color: var(--lemon);
  font-size: 13px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.suggestion-title { font-size: var(--text-base); font-weight: 600; color: var(--yale); }
.suggestion-item { background: var(--bg-card); border-radius: var(--r-md); padding: var(--sp-3); margin-bottom: var(--sp-2); }
.suggestion-text { font-size: var(--text-sm); color: var(--text-primary); margin-bottom: var(--sp-2); line-height: var(--leading-normal); }
.suggestion-supporters { font-size: var(--text-xs); color: var(--text-secondary); margin-bottom: var(--sp-3); }
.suggestion-actions { display: flex; gap: var(--sp-2); }
.sug-btn { padding: 6px 14px; border-radius: var(--r-pill); font-size: var(--text-sm); font-weight: 600; border: none; cursor: pointer; }
.sug-accept  { background: var(--teal); color: white; }
.sug-modify  { background: var(--amber-tint); color: var(--amber-text); border: 1px solid var(--amber); }
.sug-decline { background: var(--bg-page); color: var(--text-secondary); border: 1px solid var(--border-light); }
```

---

## Screen 10 — Split bill

```
[Tab row: Everyone | Specific people | My Flock | Just me]

[Large amount input]
  $  [0.00 — large text, number keyboard]
  [Currency selector chip: USD ▾]

[Description input]
  "What was this for?" — single line

[Category chips: 🍜 Food | 🚇 Transport | 🎟 Activity | 🛍 Shopping | 📦 Other]

[Members section — only shown for "Specific people" tab]
  [Member chip grid — all selected by default, tap to deselect]
  "Split between: Alex, Priya, Carlos (+4 more)"

[Log expense button — full width, Yale Blue]

[Running balance bar]
  [Per-person mini card: name | amount spent | balance]
  [Green = owed money | red = owes | gray = balanced]
```

---

## Screen 11 — Settlement summary (post-trip)

```
[Header: "Who pays who"]
[Bounce contextual: "I've calculated the simplest way to settle — minimum transactions for everyone."]

[Transaction cards]
  ┌─────────────────────────────────────────┐
  │ 💸  Carlos  →  Alex                     │
  │     $127.40                             │
  │ [Copy details] [Message Alex]           │
  └─────────────────────────────────────────┘

[Each person's final balance card]
  Name | Total paid | Total owed | Net (green/red)

[Bounce note at bottom]
  "These figures are based on expenses logged in Bounce.
   If you paid anything outside the app, settle that separately."
```

---

## Screen 12 — Post-trip wrap (Travel DNA)

```
[Yale Blue hero card — full width]
  [Animated ✈→🏠 graphic or just large emoji]
  "The Tokyo Reunion · 10 days"
  [Trip dates]
  [Group avatar row]

[Spending card]
  Total: $X,XXX of $3,500 budget
  [Category breakdown bars — horizontal]
  Food 34% | Transport 22% | Activities 28% | Shopping 16%
  [Bounce insight: "You overspent on food by 12%. No regrets."]

[Travel DNA cards — one per member (own card only)]
  [Personality traits — horizontal bars]
  "Food-forward · Cultural · Early riser"
  [Generated by Vertex AI from trip behaviour]

[Next trip seeds]
  [3 destination rec-cards: Kyoto | Seoul | Taipei]
  [Bounce reasoning per card]
```

---

## Screen 13 — Judge test mode UI

Only visible when URL contains `?mode=judge`. Do not show to regular users.

```css
.judge-panel {
  position: fixed; bottom: calc(72px + env(safe-area-inset-bottom));
  left: var(--sp-4); z-index: var(--z-judge);
}
.judge-trigger {
  background: var(--amber); color: white;
  padding: 6px 12px; border-radius: var(--r-pill);
  font-size: var(--text-xs); font-weight: 700;
  cursor: pointer; box-shadow: var(--shadow-float);
  display: flex; align-items: center; gap: var(--sp-1);
}
.judge-trigger::before { content: '⚡'; font-size: 11px; }
.judge-menu {
  position: absolute; bottom: calc(100% + var(--sp-2)); left: 0;
  background: var(--bg-card); border-radius: var(--r-lg);
  border: 1.5px solid var(--amber); box-shadow: var(--shadow-float);
  padding: var(--sp-3); min-width: 200px;
  display: none;
}
.judge-menu.open { display: block; animation: fadeUp 150ms ease; }
.judge-menu-title { font-size: var(--text-xs); font-weight: 700; color: var(--amber); text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: var(--sp-3); padding-bottom: var(--sp-2); border-bottom: 0.5px solid var(--border-lemon); }
.judge-action {
  display: flex; align-items: center; gap: var(--sp-2);
  padding: var(--sp-2) var(--sp-3); border-radius: var(--r-sm);
  font-size: var(--text-sm); font-weight: 500; color: var(--text-primary);
  cursor: pointer; transition: background var(--t-fast); text-decoration: none;
  width: 100%; background: none; border: none; text-align: left;
}
.judge-action:hover { background: var(--bg-page); }
.judge-action.danger { color: var(--danger); }
.judge-action-icon  { font-size: 16px; }
```

HTML:
```html
<div class="judge-panel" id="judgePanel" style="display:none">
  <button class="judge-trigger" onclick="toggleJudgeMenu()">Judge Mode</button>
  <div class="judge-menu" id="judgeMenu">
    <div class="judge-menu-title">⚡ Judge controls</div>
    <button class="judge-action" onclick="judgeReset()">
      <i class="ti ti-refresh judge-action-icon"></i> Reset demo
    </button>
    <button class="judge-action" onclick="judgeSeedReunion()">
      <i class="ti ti-users judge-action-icon"></i> Load Reunion trip
    </button>
    <button class="judge-action danger" onclick="judgeTriggerDisruption()">
      <i class="ti ti-alert-triangle judge-action-icon"></i> Trigger disruption
    </button>
    <a class="judge-action" href="/judge/instructions" target="_blank">
      <i class="ti ti-help-circle judge-action-icon"></i> Judge instructions ↗
    </a>
  </div>
</div>
<script>
  if (new URLSearchParams(location.search).get('mode') === 'judge') {
    document.getElementById('judgePanel').style.display = 'block';
  }
  function toggleJudgeMenu() {
    document.getElementById('judgeMenu').classList.toggle('open');
  }
</script>
```

---

# PART 9 — UX FLOWS

## 9.1 — Demo path (3 minutes mapped to screens)

Every screen transition during the 3-minute demo video:

```
0:00-0:05  Auth screen — name "Alex" entered → tap "Let's go"
0:05-0:20  Screen 1: Entry — Alex types The Reunion message → Bounce responds
0:20-0:35  Profile completion Screen 3 (briefly shown, pre-filled)
0:35-0:50  Group status card (7 joined, 3 pending) → "Begin planning" CTA
0:50-1:05  Progressive loading panel — 5 Bounce steps animate in
1:05-1:15  Screen 4: Itinerary Day 1 — note the "group ready" logic callout
1:15-1:25  Screen 4: Flight selection — ANA NH106 risk card (Low, 84/100)
1:25-1:35  Day 5 tab — Bounce suggests FlockMode
1:35-1:50  Screen 5: FlockMode creation — 3 Flocks built
1:50-2:00  Screen 6: FlockMode active — reconvene countdown shown
2:00-2:05  Judge panel: tap "Trigger disruption"
2:05-2:30  Screen 8: Disruption sheet → Mori Art Museum selected → Firebase update
2:30-2:40  Screen 10: Split bill — 4-mode UI shown, expense logged
2:40-2:55  Screen 12: Travel DNA + next trip seeds
2:55-3:00  Bounce logo hold
```

## 9.2 — Booking handoff flow

When user taps any booking link (flight, hotel):

```
User taps "Book this flight" →
  [Warning sheet — amber, not danger]
  "Leaving Bounce to book"
  "You're heading to united.com to complete this booking.
   Come back here to confirm your flight and I'll update your itinerary."
  [Cancel — ghost] [Continue to airline ↗ — primary]
  
→ External site opens in new tab
→ User returns to Bounce
→ Bounce shows: "Did you book it? Add your confirmation number so I can track the flight."
→ [Input: confirmation number] [Save]
→ Itinerary booking status updates to "Booked ✓"
```

## 9.3 — Chat-to-form sync flow

When Bounce updates a form field via chat (e.g., user says "I'm vegetarian" during profile chip screen):

```
User in profile screen, dietary chips visible
User types in Bounce chat: "Actually I'm vegetarian, not vegan"
→ Bounce responds: "Got it — switching you to vegetarian."
→ Frontend receives intent update from agent
→ "Vegan" chip deselects (with .bounce-updated animation)
→ "Vegetarian" chip selects
→ User sees the form update without touching it
```

CS implementation: Agent returns `{intent: "update_profile", field: "dietary", value: "vegetarian"}` in a structured response field. Frontend listens and applies.

---

# PART 10 — STATES

## 10.1 — Loading states

```css
/* Skeleton shimmer — use for quick loads (<5s) */
.skeleton { background: linear-gradient(90deg, var(--border-light) 0%, var(--bg-raised) 50%, var(--border-light) 100%); background-size: 200% 100%; border-radius: var(--r-xs); animation: shimmer 1.5s ease infinite; }
@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }
.skeleton-text  { height: 14px; margin-bottom: var(--sp-2); border-radius: var(--r-xs); }
.skeleton-title { height: 22px; width: 55%; margin-bottom: var(--sp-3); border-radius: var(--r-xs); }
.skeleton-card  { height: 100px; border-radius: var(--r-lg); margin-bottom: var(--sp-3); }
/* For long loads (>5s): use progressive loading panel from Part 5.4 */
```

## 10.2 — Error states

```css
.error-inline {
  display: flex; align-items: flex-start; gap: var(--sp-2);
  padding: var(--sp-3) var(--sp-4); background: var(--danger-tint);
  border-left: 3px solid var(--danger); border-radius: 0 var(--r-md) var(--r-md) 0;
  margin-bottom: var(--sp-3);
}
.error-inline p { font-size: var(--text-sm); color: var(--danger-text); line-height: var(--leading-normal); }
```

## 10.3 — Empty states (per screen)

```css
.empty { display: flex; flex-direction: column; align-items: center; padding: var(--sp-10) var(--sp-6); text-align: center; }
.empty-icon    { font-size: 48px; margin-bottom: var(--sp-4); }
.empty-title   { font-size: var(--text-md); font-weight: 600; color: var(--text-primary); margin-bottom: var(--sp-2); }
.empty-caption { font-size: var(--text-base); color: var(--text-secondary); line-height: var(--leading-relaxed); max-width: 280px; }
```

| Screen | Empty icon | Bounce message |
|---|---|---|
| Group (no members) | ti-user-plus | "Share the invite link — I'll ping you when people start joining." |
| Itinerary (no days yet) | ti-map | "Tell me about your trip and I'll build the plan." |
| Split bill (no expenses) | ti-receipt-2 | "Log your first expense when you get there — I'll handle the maths." |
| Flocks (not created) | ti-feather | "Day 5 looks like a good one for FlockMode. Tap to split up." |
| Flight status (no flights) | ti-plane | "Once you've picked your flights, I'll keep an eye on them." |

## 10.4 — Toast notifications

```css
.toast-stack { position: fixed; top: var(--sp-4); left: 50%; transform: translateX(-50%); width: calc(100% - var(--sp-8)); max-width: 560px; z-index: var(--z-toast); display: flex; flex-direction: column; gap: var(--sp-2); pointer-events: none; }
.toast {
  background: var(--text-primary); color: white;
  border-radius: var(--r-md); padding: var(--sp-3) var(--sp-4);
  display: flex; align-items: center; gap: var(--sp-3);
  box-shadow: var(--shadow-float); pointer-events: all;
  animation: toastIn 220ms ease forwards;
}
@keyframes toastIn { from{opacity:0;transform:translateY(-10px)} to{opacity:1;transform:translateY(0)} }
.toast-icon { font-size: 18px; flex-shrink: 0; }
.toast-body { flex: 1; }
.toast-title { font-size: var(--text-sm); font-weight: 600; margin-bottom: 1px; }
.toast-sub   { font-size: var(--text-xs); opacity: 0.8; }
.toast-close { font-size: 18px; opacity: 0.6; cursor: pointer; padding: var(--sp-1); }
.toast.yale    { background: var(--yale); }
.toast.teal    { background: var(--teal); }
.toast.amber   { background: var(--amber); }
.toast.danger  { background: var(--danger); }
```

---

# PART 11 — ANIMATION AND MOTION

```css
/* Page enter */
.page-enter { animation: fadeUp 220ms ease both; }
@keyframes fadeUp { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }

/* Staggered card appear */
.stagger > *:nth-child(1){animation-delay:0ms}
.stagger > *:nth-child(2){animation-delay:50ms}
.stagger > *:nth-child(3){animation-delay:100ms}
.stagger > *:nth-child(4){animation-delay:150ms}
.stagger > *:nth-child(5){animation-delay:200ms}
.stagger > * { animation: fadeUp 200ms ease both; }

/* Disruption shake */
.shake { animation: shake 400ms ease; }
@keyframes shake { 0%,100%{transform:translateX(0)} 20%{transform:translateX(-6px)} 40%{transform:translateX(6px)} 60%{transform:translateX(-4px)} 80%{transform:translateX(4px)} }

/* Firebase update flash (itinerary item changed by another member) */
.firebase-update { animation: flashUpdate 800ms ease; }
@keyframes flashUpdate { 0%,100%{background:inherit} 30%,70%{background:var(--teal-tint)} }

/* Status update (flight status changed) */
.status-change { animation: statusFlash 600ms ease; }
@keyframes statusFlash { 0%,100%{background:inherit} 50%{background:var(--lemon)} }

/* Respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

# PART 12 — MICRO-COPY GUIDE

Every button, CTA, and Bounce message in the demo path.

## 12.1 — Button labels (never use generic verbs)

| Generic (wrong) | Specific (correct) |
|---|---|
| Submit | Plan my trip · Start planning · Lock it in |
| Continue | Set up my group · Add my details · Next: flights |
| Save | Done · Got it · Saved |
| Confirm | Looks right · Confirm trip · That's the one |
| Select (flight) | Fly this one · Choose |
| Apply (disruption alt) | Go here instead |
| Back | Change something · Go back |
| Close | Done · Got it |
| Join | Join the trip → |
| Share | Invite my group |
| Log expense | Add expense |
| Book | Go to [airline] → |

## 12.2 — Bounce voice guide

**When something takes time:**
"Let me pull this together — it'll be worth the wait."
"Working on your 10-day itinerary... this takes a moment."

**When something goes right:**
"Done! [specific result]." — never just "Done!"
"Your trip is locked in. See you in Tokyo."
"All 10 members are in. Let's build this trip."

**When something goes wrong:**
"Couldn't pull live flights right now — give it a moment, or tell me which airline you prefer."
"Something went sideways. Try that again?"
"I can't verify that right now — check [specific source] directly."

**When data is an estimate:**
"These prices are estimates — confirm when you book."
"Crowd times are based on typical patterns, not live sensors."
"Visa info is current as of today — always verify with the embassy."

**Never say:**
- "I have processed your request"
- "Please find below"
- "An error has occurred"
- "I understand that..."
- "Certainly!"
- "Of course!"

## 12.3 — Empty state Bounce messages (full text)

```
No members joined yet:
"Share the link with your group. I'll keep you posted as people join."

Waiting for planning to start:
"Just waiting for Alex to kick things off.
 Once they start planning, you'll see the trip here."

No expenses logged:
"First expense? Log it here — I'll handle the maths and keep everyone updated."

FlockMode not yet created:
"When your group wants to split up for a few hours, use FlockMode.
 Each Flock gets its own plan while you explore independently."

No flight status:
"I'll track your flights once you've confirmed them. Check back closer to departure."
```

---

# PART 13 — ACCESSIBILITY

Minimum accessibility standards for demo quality:

```css
/* Focus rings — visible, on-brand */
*:focus-visible {
  outline: 2.5px solid var(--yale-light);
  outline-offset: 2px;
  border-radius: 4px;
}

/* Skip link for keyboard nav */
.skip-link {
  position: absolute; top: -100%; left: var(--sp-4);
  background: var(--yale); color: white;
  padding: var(--sp-2) var(--sp-4); border-radius: var(--r-md);
  font-size: var(--text-sm); font-weight: 600; z-index: 9999;
  transition: top var(--t-fast);
}
.skip-link:focus { top: var(--sp-4); }
```

ARIA requirements for key components:

```html
<!-- Bounce chat panel -->
<div class="bounce-panel" role="dialog" aria-label="Bounce assistant" aria-modal="true">

<!-- Map -->
<div id="bounce-map" role="application" aria-label="Trip map showing venue locations">

<!-- Flight risk score -->
<div class="risk-bar" role="meter" aria-valuemin="0" aria-valuemax="100" aria-valuenow="84" aria-label="Flight risk score: 84 out of 100, Low risk">

<!-- Toggle switch -->
<button class="toggle-switch" role="switch" aria-checked="false" aria-label="Enable morning schedule observance">

<!-- Loading state -->
<div aria-live="polite" aria-label="Bounce is building your itinerary">
```

Contrast ratios (all passing WCAG AA):
- Yale Blue (#0D3B66) on white: 12.6:1 ✓
- White on Yale Blue: 12.6:1 ✓
- Yale Blue text on Lemon Chiffon: 10.8:1 ✓
- #7A6010 on Lemon Chiffon: 5.2:1 ✓ (use `--text-lemon`)
- Teal (#0D9488) on white: 4.6:1 ✓
- Amber (#D97706) on white: 3.0:1 — use for decorative only, not primary text

---

# PART 14 — PRD SYNC CHECKLIST

| PRD feature | Design element | Screen | Status |
|---|---|---|---|
| Bounce persona | Avatar, FAB, chat panel, contextual messages | All screens | ✓ Designed |
| Conversational entry | Entry screen with quick-select | Screen 1 | ✓ |
| Group invite + join | Group setup, member join flow | Screens 2, 1b | ✓ |
| Co-leader assignment | Member card + toggle | Screen 2 | ✓ |
| Per-member compliance | Private compliance card, nav-visa tab | Screen 3 + tab | ✓ |
| 3-option recommendations | Unified rec-set component | All planning screens | ✓ |
| Itinerary + Maps | Day view, timeline, Maps section | Screen 4 | ✓ |
| Custom map pins | Part 7 spec | Screen 4 | ✓ |
| Flight risk scoring | Risk bar + score label on flight rec-card | Screen 4 (flights) | ✓ |
| Staggered arrivals (Day 1) | Day 1 shows "group ready" callout | Screen 4 Day 1 | Note in reasoning line |
| Jet lag mitigation | Bounce contextual on Day 1/2 | Screen 4 | Note in Bounce message |
| FlockMode creation | Full screen spec | Screen 5 | ✓ |
| FlockMode active | Flock view, countdown, private thread tab | Screen 6 | ✓ |
| Disruption mitigation | Disruption sheet, 3-option alternatives | Screen 8 | ✓ |
| Firebase live sync | `.firebase-update` animation on changed items | All group screens | ✓ |
| Flight status tracking | Status banner in active trip | Screen 7 | ✓ |
| Split bill 4 modes | Tab row in split bill screen | Screen 10 | ✓ |
| Settlement algorithm | Settlement summary screen | Screen 11 | ✓ |
| Suggestion review | Suggestion panel CSS + screen | Screen 9 | ✓ |
| Progressive loading | Part 5.4 Bounce streaming messages | During generation | ✓ |
| Booking handoff | Warning sheet flow | Part 9.2 | ✓ |
| Chat-to-form sync | `.bounce-updated` animation + flow | Part 9.3 | ✓ |
| Judge test mode | Amber judge panel, 4 actions | Screen 13 | ✓ |
| Dark mode | Full token overrides | All screens | ✓ |
| Error states | Inline error + toast variants | Part 10.2 | ✓ |
| Empty states per screen | Table in Part 10.3 | All screens | ✓ |
| Rate limit (5 msg/10s) | No UI — CS backend only | — | CS owned |
| PII detection | No UI — CS backend; Bounce message handles | Bounce voice | ✓ |

---

# PART 15 — OWNERSHIP AND BUILD ORDER

## Biz 1 owns

Day 1: Auth screen (Screen 0) + Entry screen (Screen 1) — the first thing judges see
Day 3-5: Profile completion (Screen 3) + Compliance card
Day 6-8: Flight selection UI (5 origin groups × 3 rec-cards)
Day 9-11: FlockMode creation screen (Screen 5) — key demo moment
Day 12-13: Split bill (Screen 10)
Day 14-15: Bounce loading animations, toast system, empty states

## Biz 2 owns

Day 2: Member join flow (Screen 1b) + Group setup (Screen 2)
Day 3-5: Itinerary timeline view + Maps embed (Screen 4)
Day 6-8: Active trip daily view (Screen 7) + FlockMode active (Screen 6)
Day 9-11: Disruption sheet (Screen 8) + Suggestion panel (Screen 9)
Day 12-13: Post-trip wrap + Settlement summary (Screens 11, 12)
Day 14-15: Judge mode UI (Screen 13) + demo video recording

## CS engineer connects

All screens: Firebase real-time listeners → `.firebase-update` animation on changed nodes
Screen 1: Bounce textarea → Agent Builder streaming API
Screen 4: Maps SDK init + custom marker creation (Part 7)
Screen 3: Agent intent response → form field `.bounce-updated` animation (Part 9.3)
Screen 7: Pub/Sub flight event → toast → disruption sheet open
Screen 8: Alternative selection → save_itinerary → Firebase broadcast
Nav: Phase transitions (`data-phase` on bottom-nav, Part 3.2)
Screen 13: Judge endpoints wired to UI actions

---

# PART 16 — ICON REFERENCE

CDN link (place in `<head>`):
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css" />
```

| Feature | Icon |
|---|---|
| Home | ti-home |
| Itinerary | ti-map-2 |
| Today | ti-calendar-today |
| Bounce / Chat | ti-message-circle-2 |
| Split bill | ti-receipt-2 |
| Profile | ti-user |
| Visa | ti-id |
| Alerts | ti-bell |
| Flight | ti-plane |
| Hotel | ti-building |
| Restaurant | ti-tools-kitchen-2 |
| Transit | ti-train |
| Walk | ti-walk |
| Drive | ti-car |
| Ferry | ti-sailboat |
| FlockMode | ti-feather |
| Disruption | ti-alert-triangle |
| Flight status | ti-radar |
| Risk low | ti-shield-check |
| Risk high | ti-shield-x |
| Budget | ti-wallet |
| Expense | ti-coin |
| Map pin | ti-map-pin |
| Group | ti-users-group |
| Co-leader | ti-crown |
| Flock leader | ti-star |
| Customs | ti-book |
| Reconvene | ti-arrows-join |
| Copy link | ti-copy |
| Share | ti-share-2 |
| Swap venue | ti-refresh |
| Confirmed | ti-circle-check |
| External link | ti-external-link |
| Back | ti-arrow-left |
| Close | ti-x |
| Settings | ti-settings |
| Privacy | ti-lock |
| Q&A | ti-help-circle |
| Judge mode | ti-bolt |

---

*Bounce Design System v2.0 — May 2026*
*Gold standard implementation guide for Google Cloud Rapid Agent Hackathon 2026*
