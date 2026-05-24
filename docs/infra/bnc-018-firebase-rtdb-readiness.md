# BNC-018 Firebase Realtime Database Readiness

Date: 2026-05-24

## Card

`BNC-018 — Firebase Realtime Database live setup`

PRD source: `docs/prd/bounce_prd_v2.md` Part 0.4 and Part 7.4.

## Target contract

BNC-018 is complete only when all of these are true:

- The live GCP project is added to Firebase.
- Firebase Realtime Database exists for the Bounce project.
- Initial hackathon demo rules are configured.
- Backend configuration points at the live database URL.
- A readiness check confirms the live database instance exists.
- Later integration code can broadcast itinerary/group state updates to PRD paths.

## PRD rule baseline

The PRD explicitly chooses open demo rules for the hackathon and says to acknowledge that real auth is not implemented:

```json
{
  "rules": {
    ".read": "auth != null || true",
    ".write": "auth != null || true"
  }
}
```

These rules are intentionally **not production-safe**. They are committed only because BNC-018 follows the PRD hackathon demo contract. They must be tightened before any real-user launch.

## What was checked

Environment/tooling:

- Node.js: available (`v24.15.0`).
- npm: available (`11.13.0`).
- Firebase CLI via `npx -y firebase-tools@latest`: available (`15.18.0`).
- Firebase Agent Skills: installed locally for this workspace during the readiness pass.

Firebase CLI auth:

- `npx -y firebase-tools@latest use --json` failed because Firebase CLI login is not present.
- This means normal Firebase CLI project/database setup cannot proceed without an interactive Firebase login.

Google Cloud/Firebase API status:

- Active GCP project: `project-411e0419-48bd-4b5b-97f`.
- `firebasedatabase.googleapis.com` was already enabled during BNC-016.
- `firebase.googleapis.com` was enabled during this BNC-018 pass.

Firebase project status:

- REST check with current `gcloud` auth and quota project shows the GCP project has **not** been added to Firebase yet.
- Attempting `projects/project-411e0419-48bd-4b5b-97f:addFirebase` returned `PERMISSION_DENIED` for the current caller.
- Realtime Database instance check reports no instances because the project is not yet a Firebase project.

Current readiness script output:

```text
project=project-411e0419-48bd-4b5b-97f
firebase_project_exists=no
database_instances=none
```

Exit code: `2` (`firebase_project_exists=no`).

## Repo support added

Added Firebase config files:

- `firebase.json`
- `database.rules.json`

Added a non-secret readiness script:

```bash
python scripts/infra/verify_firebase_rtdb.py --project project-411e0419-48bd-4b5b-97f
```

The script:

- Uses the current `gcloud auth print-access-token` token.
- Sends `x-goog-user-project` to avoid ADC quota-project errors.
- Checks whether the GCP project is a Firebase project.
- Checks whether Realtime Database instances exist.
- Never prints credentials.

## Commands to finish BNC-018 once Firebase access is available

Login to Firebase CLI if using CLI setup:

```bash
npx -y firebase-tools@latest login
```

Add/use the live project:

```bash
npx -y firebase-tools@latest use --add project-411e0419-48bd-4b5b-97f
```

Initialize/deploy Realtime Database rules from this repo:

```bash
npx -y firebase-tools@latest init database --project project-411e0419-48bd-4b5b-97f
npx -y firebase-tools@latest deploy --only database --project project-411e0419-48bd-4b5b-97f
```

Then verify:

```bash
python scripts/infra/verify_firebase_rtdb.py --project project-411e0419-48bd-4b5b-97f
```

A successful BNC-018 verification should report:

```text
firebase_project_exists=yes
database_instances=<at least one instance>
```

## Status

Blocked on Firebase project permission/login:

- Current Firebase CLI is not logged in.
- Current Google caller cannot add Firebase to the existing GCP project (`PERMISSION_DENIED`).
- No live Realtime Database instance exists yet.

No secrets were committed to the repository.
