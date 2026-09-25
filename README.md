# SentinelOps AI

**Runtime Control Plane for AI Agents**

> Know what your agents can do. Control what they actually do.

SentinelOps sits between an AI agent and enterprise tools. It authenticates the agent, validates its permitted tools, evaluates contextual and trajectory risk, applies policy, records evidence, and returns **ALLOW / APPROVAL / BLOCK** before execution.

## Architecture

`AI Agent → SentinelOps Gateway → Policy + Risk + Permission Graph → Enterprise Tool`

## Phase 5.1

The project now includes:
- FastAPI backend + PostgreSQL
- JWT dashboard authentication + RBAC
- Agent registry and autonomy levels
- Agent-scoped API keys
- Tool registry and agent/tool permission graph
- Runtime action authorization
- Trajectory-aware risk scoring
- Human approval queue
- Security alerts and audit events
- SDK for Python agents
- Finance Agent end-to-end demo
- Alembic migration structure
- Docker Compose
- React/TypeScript security dashboard

## Run locally

```powershell
docker compose up --build
```

Backend: `http://localhost:8000`
Docs: `http://localhost:8000/docs`

For frontend:

```powershell
cd frontend
npm install
npm run dev
```

## Migration

After the database is available:

```powershell
cd backend
alembic upgrade head
```

## Important

The gateway now routes approved and allowed actions through configured tool adapters. HTTP tools require HTTPS and reject private or local endpoints. Credentials are resolved server-side and are never returned to the agent. Production deployments should configure real credentials through a secure secret manager and review adapter endpoint policies.
