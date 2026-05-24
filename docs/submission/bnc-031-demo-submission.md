# BNC-031 — Demo / Submission Package

Status: **prepared; blocked on final human-owned upload/submission actions**.

Prepared at: 2026-05-24T16:07:14Z

## Source requirements

BNC-031 acceptance from the fixed Kanban contract:

- 3-minute demo video.
- Devpost form.
- Screenshots.
- Public repo verification.
- Judge instructions.
- All Devpost checklist items complete before the submission buffer ends.

## Prepared artifacts

- `docs/submission/demo-video-script.md` — 3-minute recording script and screen timeline.
- `docs/submission/devpost-draft.md` — copy-ready Devpost draft.
- `docs/submission/judge-instructions.md` — copy-ready judge instructions.
- `docs/submission/screenshots/bounce-live-app-full-page.png` — live app screenshot evidence.
- `docs/submission/screenshots/bounce-judge-panel.png` — judge panel screenshot evidence.

## Live links

- Live app/API: https://bounce-api-4dynllwdeq-as.a.run.app/
- Health check: https://bounce-api-4dynllwdeq-as.a.run.app/health
- Judge instructions: https://bounce-api-4dynllwdeq-as.a.run.app/judge/instructions
- Source repo: https://github.com/Farizff/FF_googleCloudHackathon

## Verification performed

```text
GET /health -> HTTP 200
GET /judge/instructions -> HTTP 200
```

Prior production smoke evidence also confirms:

```text
POST /judge/seed-demo-trip -> HTTP 200
POST /judge/trigger-disruption -> HTTP 200
POST /judge/reset -> HTTP 200
```

## Public repo readiness

- GitHub remote: `https://github.com/Farizff/FF_googleCloudHackathon.git`
- License file exists: `LICENSE`
- README now includes live demo and judge-mode instructions.
- Secrets are not committed.

## Final human-owned checklist

These actions cannot be truthfully completed from the repo alone:

- [ ] Record final 3-minute demo video using `docs/submission/demo-video-script.md`.
- [ ] Upload the video and paste the video URL into Devpost.
- [ ] Copy `docs/submission/devpost-draft.md` into the Devpost form.
- [ ] Upload/select screenshots from `docs/submission/screenshots/`.
- [ ] Submit the Devpost entry.

## Recommended final video order

1. Hook: Bounce value proposition.
2. Conversational planning and profile gap-fill.
3. Itinerary, map, budget, and flight-risk cards.
4. Group dashboard and FlockMode.
5. Judge mode disruption path.
6. Split bill and closing logo.
