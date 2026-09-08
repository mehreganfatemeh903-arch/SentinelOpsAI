# SentinelOps Python SDK

Use an agent-scoped API key and call `SentinelOpsClient.authorize(...)` immediately before a consequential tool action.

The SDK intentionally stays small: the control plane owns policy, risk, audit, approval, and kill-switch decisions while the agent keeps its own business logic.
