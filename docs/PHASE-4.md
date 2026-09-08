# SentinelOps AI — Phase 4

## Runtime Gateway + Permission Graph

Phase 4 turns the authorization API into an enforceable control path for tool execution.

### Added
- Agent-to-tool permission bindings.
- Tool validation during runtime authorization.
- Dependency-free SDK with structured HTTP errors.
- `execute` gateway endpoint that refuses non-ALLOW decisions.
- Human approval queue with action context.
- Alembic migration for agent/tool bindings.
- End-to-end Finance Agent demo.

### Runtime path

`Agent API Key → Agent status → Tool binding → Risk → Policy → Decision → Execute/Stop → Audit`

### Important production boundary

The demo executor is intentionally simulated. A production adapter should call a real tool only after SentinelOps returns `allow`, and should keep the external tool credentials outside the agent process.
