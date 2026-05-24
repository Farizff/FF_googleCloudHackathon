# BNC-016 — Cloud/GCP Project Readiness

Date: 2026-05-24

## Result

BNC-016 is verified complete for the current Bounce Google Cloud project.

## Project and CLI context

- Active gcloud account: `febiantofariz@gmail.com`
- Active project: `project-411e0419-48bd-4b5b-97f`
- Active Cloud Run region: `asia-southeast1`
- Bounce API service: `bounce-api`
- Bounce API URL: `https://bounce-api-4dynllwdeq-as.a.run.app`

Note: the original PRD example project ID is `bounce-hackathon-2026`, but the live project currently used by the repo/deployment is `project-411e0419-48bd-4b5b-97f`.

## Billing

Billing check passed.

- Billing enabled: `true`
- Billing account linked: yes

No billing account secret details are stored here beyond the fact that billing is linked.

## Required APIs

All BNC-016/PRD-required project APIs are enabled:

- `run.googleapis.com`
- `aiplatform.googleapis.com`
- `dialogflow.googleapis.com`
- `pubsub.googleapis.com`
- `cloudscheduler.googleapis.com`
- `translate.googleapis.com`
- `maps-backend.googleapis.com`
- `places-backend.googleapis.com`
- `firebasedatabase.googleapis.com`
- `secretmanager.googleapis.com`
- `cloudbuild.googleapis.com`
- `artifactregistry.googleapis.com`
- `cloudbilling.googleapis.com` — enabled to allow billing verification

## Cloud Run readiness

`bounce-api` is deployed in `asia-southeast1`.

Observed settings:

- URL: `https://bounce-api-4dynllwdeq-as.a.run.app`
- Min instances: `1`
- Max instances: `3`
- CPU limit: `1000m`
- Memory limit: `512Mi`
- Service account: default Compute service account

Health check:

```json
{"status":"ok","app":"Bounce","version":"v0"}
```

## Secret Manager

Secret Manager API is enabled.

Current secret list returned no secret names during this audit. This means the API is ready, but later cards that need real credentials must still create/populate the needed secrets, for example MongoDB, Firebase, Amadeus, Maps, RapidAPI, SendGrid, and exchange-rate credentials.

## Changes made during BNC-016

- Set local `gcloud run/region` to `asia-southeast1`.
- Enabled missing PRD-required APIs:
  - `dialogflow.googleapis.com`
  - `cloudscheduler.googleapis.com`
  - `translate.googleapis.com`
  - `maps-backend.googleapis.com`
  - `places-backend.googleapis.com`
  - `firebasedatabase.googleapis.com`
- Enabled `cloudbilling.googleapis.com` so billing status could be verified.

## Next recommended card

`BNC-017 — MongoDB Atlas and MCP live setup`
