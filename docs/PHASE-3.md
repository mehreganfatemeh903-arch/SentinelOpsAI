# SentinelOps AI — Phase 3

## What was added
- Agent-scoped API keys with SHA-256 hashes at rest, rotation/revocation via API.
- Dedicated runtime endpoint `POST /api/v1/actions/agent-authorize` using `X-Sentinel-Key`.
- Python SDK under `sdk/sentinelops`.
- Deterministic Finance Agent demo under `demo/finance_agent.py`.
- Security alert endpoint and dashboard Security tab.
- Agent resume/kill-switch controls.
- Alembic structure for production migrations.
- Frontend API base URL via `VITE_API_BASE_URL`.

## Runtime contract
Agent -> X-Sentinel-Key -> SentinelOps -> identity -> policy -> trajectory risk -> ALLOW / APPROVAL / BLOCK -> audit.

The API key is shown only when created. Store it in a secret manager or environment variable.
