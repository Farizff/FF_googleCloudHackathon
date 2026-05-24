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

- Secret `mongodb-uri` does **not** currently exist in project `project-411e0419-48bd-4b5b-97f`.

Cloud Run:

- `bounce-api` currently has no MongoDB-related env var or Secret Manager reference configured.

Local environment:

- `MONGODB_CONNECTION_STRING` is unset.
- `MONGODB_DATABASE` is unset.
- Atlas API credential env vars are unset.

Because no MongoDB URI or Atlas API credentials are available in the environment, I could not create/verify the live Atlas cluster, create live collections, save the real URI secret, or validate deployed read/write access.

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
created_collections=none
write_probe=ok
```

Current run without credentials fails correctly:

```text
MongoDB readiness check failed: MongoDB URI is required; set MONGODB_CONNECTION_STRING or pass --uri-env.
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

Note: this is intentionally not applied to global Hermes config yet because the required MongoDB connection string is not available.

## Commands to finish BNC-017 once Atlas URI is available

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

Blocked on external credential/setup input:

- Need an Atlas cluster or permission/API credentials to create one.
- Need the Atlas connection string for user `bounce-app`.
- Need the Cloud Run service account identity when granting secret access.

No secrets were committed to the repository.
