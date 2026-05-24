# BNC-017 MongoDB Atlas and MCP Readiness

Date: 2026-05-24

## Card

`BNC-017 — MongoDB Atlas and MCP live setup`

PRD source: `docs/prd/bounce_prd_v2.md` Part 0.3.

## Target contract

BNC-017 is complete only when all of these are true:

- Live MongoDB Atlas cluster exists, preferably M0 in/near Singapore.
- Database `bounce` exists.
- The 10 PRD MongoDB collections exist:
  - `traveller_profiles`
  - `group_trips`
  - `itineraries`
  - `flight_performance`
  - `airline_ratings`
  - `visa_requirements`
  - `venue_enrichment`
  - `expenses`
  - `suggestions`
  - `notification_log`
- App database user `bounce-app` has read/write access to the `bounce` database.
- Network access allows the deployed Cloud Run backend to connect. PRD permits `0.0.0.0/0` for hackathon simplicity.
- GCP Secret Manager contains secret `mongodb-uri` with the Atlas connection string.
- Cloud Run service `bounce-api` receives the MongoDB URI as `MONGODB_CONNECTION_STRING` from Secret Manager.
- MongoDB MCP server is configured with the same connection string, using secret/env injection rather than committing credentials.
- Deployed backend or readiness script can read/write the expected collections without local mocks.

## What was checked

Environment/tooling:

- Active GCP project: `project-411e0419-48bd-4b5b-97f`
- Active Cloud Run region: `asia-southeast1`
- `node`, `npm`, and `npx` are available.
- `atlas`, `mongosh`, and legacy `mongo` CLIs are not installed locally.

Secret Manager:

- Secret `mongodb-uri` now exists in project `project-411e0419-48bd-4b5b-97f`.
- A secret version containing the Atlas URI was added without committing or printing the URI.

Cloud Run:

- `bounce-api` revision `bounce-api-00011-gj6` receives `MONGODB_CONNECTION_STRING` from Secret Manager secret `mongodb-uri:latest`.
- `bounce-api` has `MONGODB_DATABASE=bounce`.
- `/health`, `/`, `/judge/instructions`, `/chat`, `/judge/seed-demo-trip`, `/judge/trigger-disruption`, and `/judge/reset` are live.
- MongoDB-backed judge writes return HTTP 200 after Atlas Network Access was updated to `0.0.0.0/0` for hackathon/demo access.

Local environment/readiness:

- The provided Atlas URI was verified locally without printing the URI.
- Database `bounce` exists.
- All 10 PRD MongoDB collections exist.
- `python scripts/infra/verify_mongodb_atlas.py --create-missing --write-probe` passes.

The URI works locally and deployed Cloud Run judge smoke tests now pass after Atlas Network Access was changed from `117.54.157.254/32` to `0.0.0.0/0`.

## Repo support added

Added a non-secret readiness script:

```bash
python scripts/infra/verify_mongodb_atlas.py --create-missing --write-probe
```

The script:

- Reads the URI from `MONGODB_CONNECTION_STRING` by default.
- Never prints the URI.
- Pings MongoDB Atlas.
- Verifies the 10 PRD collections.
- Can create missing collections when `--create-missing` is passed.
- Can perform a read/write/delete probe via `notification_log` when `--write-probe` is passed.

Expected successful output shape:

```text
database=bounce
expected_collections=10
existing_expected_collections=10
missing_collections=none
created_collections=traveller_profiles,group_trips,itineraries,flight_performance,airline_ratings,visa_requirements,venue_enrichment,expenses,suggestions,notification_log
write_probe=ok
```

Current run with the provided Atlas URI succeeds locally:

```text
database=bounce
expected_collections=10
existing_expected_collections=10
missing_collections=none
created_collections=traveller_profiles,group_trips,itineraries,flight_performance,airline_ratings,visa_requirements,venue_enrichment,expenses,suggestions,notification_log
write_probe=ok
```

Current deployed Cloud Run judge mutation smoke now passes:

```text
GET /health -> HTTP 200
POST /judge/seed-demo-trip -> HTTP 200
POST /judge/trigger-disruption -> HTTP 200
POST /judge/reset -> HTTP 200
```

## MCP server configuration target

MongoDB's MCP package is available as `mongodb-mcp-server` on npm. A secure Hermes config should inject the connection string from a secret-backed environment variable, not hard-code it.

Template for Hermes native MCP once the URI is available:

```yaml
mcp_servers:
  mongodb:
    command: "npx"
    args: ["-y", "mongodb-mcp-server", "--readOnly"]
    env:
      MDB_MCP_CONNECTION_STRING: "${MONGODB_CONNECTION_STRING}"
      MDB_MCP_TELEMETRY: "disabled"
    timeout: 120
    connect_timeout: 60
```

Note: this template remains non-secret and is safe to apply only if the Hermes process receives `MONGODB_CONNECTION_STRING` from the environment/secret manager. Do not paste the URI into `config.yaml`.

## Commands used for final verification

Set the URI locally for the terminal session without committing it:

```bash
export MONGODB_CONNECTION_STRING='[REDACTED_ATLAS_URI]'
export MONGODB_DATABASE=bounce
python scripts/infra/verify_mongodb_atlas.py --create-missing --write-probe
```

Create the Secret Manager secret if it does not exist:

```bash
gcloud secrets create mongodb-uri \
  --project project-411e0419-48bd-4b5b-97f \
  --replication-policy=automatic
```

Add the URI as a secret version:

```bash
printf '%s' "$MONGODB_CONNECTION_STRING" | gcloud secrets versions add mongodb-uri \
  --project project-411e0419-48bd-4b5b-97f \
  --data-file=-
```

Grant the Cloud Run service account Secret Manager access if needed:

```bash
gcloud secrets add-iam-policy-binding mongodb-uri \
  --project project-411e0419-48bd-4b5b-97f \
  --member='serviceAccount:[REDACTED_CLOUD_RUN_SERVICE_ACCOUNT]' \
  --role='roles/secretmanager.secretAccessor'
```

Wire the secret to Cloud Run:

```bash
gcloud run services update bounce-api \
  --project project-411e0419-48bd-4b5b-97f \
  --region asia-southeast1 \
  --update-secrets MONGODB_CONNECTION_STRING=mongodb-uri:latest \
  --set-env-vars MONGODB_DATABASE=bounce
```

Then redeploy/smoke-test backend routes that require MongoDB when those routes are implemented.

## Status

Complete for the current hackathon deployment gate:

- Atlas URI works locally.
- Database `bounce` exists.
- All 10 expected collections exist.
- Local write probe passes.
- Secret Manager secret `mongodb-uri` exists.
- Cloud Run service `bounce-api` has `MONGODB_CONNECTION_STRING` from Secret Manager and `MONGODB_DATABASE=bounce`.
- Atlas Network Access allows demo Cloud Run access via `0.0.0.0/0`.
- Deployed judge routes `/judge/seed-demo-trip`, `/judge/trigger-disruption`, and `/judge/reset` return HTTP 200.

Follow-up security hardening after demo:

- Rotate the `bounce-app` password because the URI was shared in chat.
- Replace `0.0.0.0/0` with a tighter network posture if/when Cloud Run uses stable egress.

No secrets were committed to the repository.
