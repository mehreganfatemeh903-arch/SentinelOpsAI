# SentinelOps AI — Customer Demo Guide

## Purpose

This guide demonstrates how SentinelOps AI governs AI-agent actions before they reach enterprise tools.

The demonstration covers three runtime decisions:

1. ALLOW
2. BLOCK
3. APPROVAL → EXECUTE

---

## Production Demo

Frontend:

`https://sentinelopsai.pages.dev/`

API:

`https://sentinelopsai.fastapicloud.dev`

API documentation:

`https://sentinelopsai.fastapicloud.dev/docs`

Health check:

`https://sentinelopsai.fastapicloud.dev/health`

---

## Demo Flow

### 1. Dashboard Overview

Open the production dashboard.

Show:

* Agents
* Tools
* Policies
* Runtime Events
* Security status
* Approval Queue

Explain:

> SentinelOps AI acts as a control plane between an AI agent and the tools it is allowed to use.

---

## 2. ALLOW — Normal Action

Demonstrate a low-risk permitted action.

Example:

```text
Action: demo.execute
Risk: 0
Decision: ALLOW
```

Explain:

> The agent is authenticated, the tool is permitted, the action satisfies policy, and the gateway allows execution.

Show the corresponding runtime event in the dashboard.

---

## 3. BLOCK — Destructive Production Action

Demonstrate:

```text
Action: delete.production.data
Environment: production
Decision: BLOCK
```

The gateway blocks the action before tool execution.

Explain:

> Destructive production actions are blocked by default. The agent cannot bypass this boundary by directly requesting the enterprise tool.

Show the resulting runtime event.

---

## 4. APPROVAL — High-Risk Financial Action

Demonstrate:

```text
Action: process.customer.payment
Sensitivity: 70
Financial amount: 1000
External destination: true
Risk score: 85
Decision: APPROVAL
```

The action enters the human approval queue.

Explain:

> High-risk actions can require explicit human authorization before execution.

Open the Approval Queue.

Approve the request.

Then execute the approved action.

Expected result:

```text
Decision: ALLOW
Executed: true
```

Show the resulting runtime event and execution evidence.

---

## 5. Security Boundary

Explain the main security controls:

* Agent-scoped authentication
* Agent/tool permission binding
* Server-side credential isolation
* Policy enforcement
* Runtime risk evaluation
* Human approval
* Production destructive-action protection
* Audit events
* Secure HTTP adapter restrictions

Important:

> Credentials are resolved server-side and are not returned to the AI agent.

---

## 6. Architecture

```text
AI Agent
   |
   v
Authentication
   |
   v
Permission Graph
   |
   v
Risk Engine
   |
   v
Policy Engine
   |
   +---- BLOCK
   |
   +---- APPROVAL → Human Decision → Execute
   |
   +---- ALLOW
   |
   v
Tool Adapter
   |
   v
Enterprise Tool
   |
   v
Audit Evidence
```

---

## 7. Technical Demonstration

The Python SDK provides a lightweight integration point:

```python
from sdk.sentinelops import SentinelOpsClient

client = SentinelOpsClient(
    base_url,
    agent_api_key,
)

result = client.authorize(
    agent_id,
    action,
    resource,
)
```

For controlled execution:

```python
result = client.execute(
    agent_id,
    action,
    resource,
)
```

The agent keeps its business logic while SentinelOps owns authorization, risk, policy, approval, and audit decisions.

---

## 8. Demo Adapter

The current customer demonstration uses the simulated adapter for safe execution testing.

This allows the complete authorization and approval lifecycle to be demonstrated without performing real financial or destructive operations.

Real enterprise integrations can use configured adapters with organization-specific credentials, endpoints, policies, and operational controls.

---

## 9. Customer Value

SentinelOps AI provides a centralized governance layer for AI-agent execution:

```text
Identity
   ↓
Permissions
   ↓
Risk
   ↓
Policy
   ↓
Human Approval
   ↓
Controlled Execution
   ↓
Audit Evidence
```

The objective is to allow organizations to deploy AI agents while maintaining explicit control over consequential actions.
