# Bounce Judge Instructions

Status: copy-ready judge instructions for README and Devpost.

## Live links

- Live app: https://bounce-api-4dynllwdeq-as.a.run.app/
- Health check: https://bounce-api-4dynllwdeq-as.a.run.app/health
- Judge instructions endpoint: https://bounce-api-4dynllwdeq-as.a.run.app/judge/instructions
- Source code: https://github.com/Farizff/FF_googleCloudHackathon

## Suggested judge path

1. Open the live app.
2. Confirm the API badge says `API online: Bounce v0` or open `/health`.
3. Review the planning screen:
   - natural-language trip prompt,
   - quick profile details,
   - Day 1 itinerary with group-ready reasoning,
   - budget estimate,
   - map preview,
   - 3 flight options per origin.
4. Review group planning:
   - joined/pending member status,
   - organiser suggestion review,
   - FlockMode creation,
   - Flock active schedule and reconvene details.
5. Review active-trip support:
   - today schedule,
   - flight status card,
   - split-bill UI and balances.
6. Use the judge panel:
   - `Seed demo trip`,
   - `Trigger disruption`,
   - optionally reset the demo.

## Direct endpoint checks

```bash
BASE="https://bounce-api-4dynllwdeq-as.a.run.app"

curl "$BASE/health"
curl "$BASE/judge/instructions"
curl -X POST "$BASE/judge/seed-demo-trip"
curl -X POST "$BASE/judge/trigger-disruption"
curl -X POST "$BASE/judge/reset"
```

## Expected behavior

- `/health` returns HTTP 200 and `{"status":"ok","app":"Bounce","version":"v0"}`.
- `/judge/instructions` returns a plain-text guide.
- Judge POST endpoints return HTTP 200 on the deployed service.
- The app remains usable without judge setup because the frontend includes the seeded Tokyo Reunion demo path.

## Scope notes

- Real production authentication is intentionally not implemented for the hackathon demo.
- Secrets are not stored in the repository.
- Cut features remain out of scope unless explicitly reopened: receipt scanning, multi-language UI, in-app GPS tracking, generated packing list, generated trip narrative, cultural briefing screen, and Travel DNA read-back on later trips.
