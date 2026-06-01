# BV5-016 Cloud Run deployment smoke

Date: 2026-06-01

## Approved deployment path

- Option: Option 2 — deploy v5 prototype to a new Cloud Run service.
- Google Cloud project: `project-411e0419-48bd-4b5b-97f`
- Region: `asia-southeast1`
- Service: `bounce-v5-prototype`
- Existing service intentionally untouched: `bounce-api`
- Existing service check: `https://bounce-api-4dynllwdeq-as.a.run.app/health` returned HTTP 200 from revision `bounce-api-00017-hmz`.

## Deployment source

- Source directory: `cloudrun/bounce-v5-prototype/`
- Runtime: Python stdlib HTTP server in `app.py`
- Prototype payload: `cloudrun/bounce-v5-prototype/index.html`, copied from `frontend/bounce_v5_prototype.html`
- Health endpoint: `/health`

## Cloud Run result

- Public URL: `https://bounce-v5-prototype-4dynllwdeq-as.a.run.app`
- Latest ready revision: `bounce-v5-prototype-00001-cpt`
- Traffic: 100% to `bounce-v5-prototype-00001-cpt`

## Smoke evidence

Command result:

```text
SERVICE_URL=https://bounce-v5-prototype-4dynllwdeq-as.a.run.app
REVISION=bounce-v5-prototype-00001-cpt
ROOT_STATUS=200
HEALTH_STATUS=200
ROOT_CONTAINS={'Bounce': True, 'Your trip starts here': True, 'bytes': 65150}
HEALTH_BODY={"status": "ok","app": "Bounce","service": "bounce-v5-prototype","version": "v5-l1"}
```

Browser smoke:

```text
URL=https://bounce-v5-prototype-4dynllwdeq-as.a.run.app/
title=Bounce v5 L1 prototype
hasCta=True
jsErrors=[]
```

## Acceptance mapping

- Fariz-approved deployment target is recorded: yes, Option 2 / new Cloud Run service.
- Hosted URL loads the v5 prototype: yes, `/` returned HTTP 200 and browser smoke found the v5 CTA.
- `/health` remains healthy: yes, `/health` returned HTTP 200 with `status: ok`.
- Smoke evidence records exact URL, status codes, and revision/version identifier: yes.
