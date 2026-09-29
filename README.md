# SentinelOps AI

**Runtime Control Plane for AI Agents**

> Know what your agents can do. Control what they actually do.

SentinelOps AI is a security and governance gateway for AI agents. It sits between AI agents and enterprise tools, authenticates agents, validates permissions, evaluates runtime risk, applies policies, manages human approvals, and records auditable execution evidence.

## Architecture

`AI Agent → SentinelOps Gateway → Authentication + Permission Graph → Risk Engine → Policy Engine → Approval → Tool Adapter → Enterprise Tool`

## Core Capabilities

* FastAPI backend with PostgreSQL
* JWT authentication and role-based access control
* Agent registry with configurable autonomy levels
* Agent-scoped API keys
* Tool registry and agent/tool permission binding
* Runtime action authorization
* Context-aware and trajectory-aware risk scoring
* Policy-based ALLOW / APPROVAL / BLOCK decisions
* Automatic blocking of destructive production actions
* Human approval workflow
* Approval execution tracking
* Security alerts and runtime audit events
* Server-side credential isolation
* Pluggable tool adapter architecture
* Simulated, environment, and HTTP adapters
* Secure HTTP adapter restrictions
* Python SDK support
* React + TypeScript security dashboard
* Docker Compose local deployment
* Alembic database migrations
* Automated backend test suite

## Runtime Decision Model

Every protected action passes through the SentinelOps authorization flow before execution.

```text
AI Agent
   |
   v
Authentication
   |
   v
Agent + Tool Permission Check
   |
   v
Risk Evaluation
   |
   v
Policy Evaluation
   |
   +---- BLOCK --------> Audit Event
   |
   +---- APPROVAL -----> Human Approval
   |                         |
   |                         v
   |                    Controlled Execute
   |
   +---- ALLOW --------> Tool Adapter
                              |
                              v
                         Audit Evidence
```

## Security Controls

SentinelOps AI is designed around a server-side security boundary.

### Agent Isolation

Agents authenticate independently and can be restricted to explicitly permitted tools.

### Credential Isolation

Credentials are resolved server-side and are not returned to the AI agent.

### Production Protection

Destructive production actions are blocked by default by the policy engine.

### Risk-Based Approval

High-risk actions can require human approval before execution.

Risk evaluation can consider factors including:

* Tool sensitivity
* Financial amount
* External destinations
* Agent autonomy
* Previous actions in the session
* Sensitive-data workflows

### HTTP Adapter Protection

HTTP tool execution requires HTTPS and rejects private, loopback, and link-local destinations. Redirects are not followed.

## Demonstrated Runtime Flows

The production demo validates three core authorization paths:

### ALLOW

A permitted low-risk action is authorized and routed through the configured tool adapter.

### BLOCK

A destructive production action is blocked automatically before execution.

### APPROVAL

A high-risk financial action can enter the human approval queue, be approved, and then execute through the controlled gateway.

The current demonstration environment uses a simulated adapter for safe execution testing. Real enterprise integrations should be configured with appropriate production credentials, endpoint policies, and operational controls.

## Dashboard

The React/TypeScript dashboard provides visibility into:

* Agents
* Tools
* Policies
* Runtime events
* Security status
* Approval queue
* Execution evidence

Production frontend:

`https://sentinelopsai.pages.dev/`

Production API:

`https://sentinelopsai.fastapicloud.dev`

API documentation:

`https://sentinelopsai.fastapicloud.dev/docs`

## Local Development

### Start the full stack

```powershell
docker compose up --build
```

Backend:

`http://localhost:8000`

API documentation:

`http://localhost:8000/docs`

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Frontend development server:

`http://localhost:5173`

## Database Migration

After the database is available:

```powershell
cd backend
alembic upgrade head
```

## Testing

Run the backend test suite from the repository root:

```powershell
$env:DATABASE_URL="postgresql+psycopg://sentinelops:sentinelops@localhost:5433/sentinelops"; pytest .\backend\tests -q --tb=short
```

The current verified test suite passes all automated backend tests.

## Project Structure

```text
SentinelOpsAI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── db/
│   │   └── main.py
│   └── tests/
├── frontend/
│   └── src/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Production Considerations

SentinelOps AI provides the control-plane architecture and security boundaries required for governed AI-agent execution.

Before connecting real enterprise systems, production operators should:

* Configure credentials through a secure secret manager.
* Review and restrict tool endpoints.
* Define policies appropriate to the organization.
* Configure appropriate approval requirements.
* Review audit events and security alerts.
* Validate adapter behavior against the target enterprise systems.
* Apply organization-specific authentication, networking, monitoring, and compliance controls.

## Product Positioning

SentinelOps AI is designed for organizations that need controlled execution of AI agents across business systems.

It provides a centralized layer for:

**Identity → Permissions → Risk → Policy → Human Approval → Controlled Execution → Audit Evidence**

This architecture allows AI agents to remain productive while keeping sensitive tool execution behind an explicit governance boundary.

## License

See the repository license and deployment terms for the applicable usage conditions.
