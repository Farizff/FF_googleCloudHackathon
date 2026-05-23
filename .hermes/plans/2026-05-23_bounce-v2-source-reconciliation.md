# Bounce v2.1 Source-of-Truth Reconciliation

Date: 2026-05-23

## What changed

The project source documents are now synchronized v2.1 docs:

- PRD: `docs/prd/bounce_prd_v2.md`
- Design system: `docs/design/bounce_design_v2.md`

## Authority boundaries

- PRD is the source of truth for tool contracts, schemas, algorithms, demo scenario data, cloud setup, and build order.
- Design system is the source of truth for UI styling, screens, flows, components, microcopy, and visual identity.
- When implementation touches both, follow PRD for data/logic and Design for presentation.

## Reconciled decisions replacing the old v1 plan

- Region is `asia-southeast1` (Singapore), not `asia-southeast2` and not Jakarta.
- Demo member data should follow PRD v2.1 exactly: Alex, Priya, Marcus, Sofia, Jake, Aditya, Emma, Carlos, Liam, Rania with the listed nationalities and FlockMode assignments.
- Cloud Vision receipt scanning is explicitly out of scope. Manual expense entry only.
- Frontend typography follows Design v2.1 tokens: system sans stack (`--font-sans`) unless the design system is later changed. The older Geometri amendment is superseded by the synchronized design system.
- Chat messages live in Firebase Realtime Database, not MongoDB.
- Required MongoDB collections are the 10 listed in PRD Part 0.3; `chat_threads` is Firebase-only.

## Immediate execution batch

1. Store the synchronized docs in repo.
2. Update README and `.env.example` to v2.1 region/project defaults.
3. Add MIT license.
4. Create the PRD directory skeleton.
5. Add minimal backend dependencies.
6. Add FastAPI `/health` endpoint and test.
7. Verify with pytest and git diff/status.
