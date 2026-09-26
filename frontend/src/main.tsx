
import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  ShieldCheck,
  Bot,
  AlertTriangle,
  Activity,
  LockKeyhole,
  CheckCircle2,
  XCircle,
  RefreshCw,
  KeyRound,
  Clock3,
  Wrench,
  FileCheck2,
  Plus,
  Link2,
  Server,
} from 'lucide-react';
import './styles.css';

const API =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

type Event = {
  id: string;
  action: string;
  resource: string;
  decision: string;
  risk_score: number;
  created_at: string;
  reasons: string[];
};

type Agent = {
  id: string;
  name: string;
  owner: string;
  autonomy_level: string;
  active: boolean;
  description?: string;
};

type Tool = {
  id: string;
  name: string;
  description?: string | null;
  sensitivity: number;
  adapter_name: string;
  credential_ref?: string | null;
  endpoint?: string | null;
  active: boolean;
};

type Policy = {
  id: string;
  name: string;
  action_pattern: string;
  min_risk: number;
  max_financial_amount?: number | null;
  require_approval: boolean;
  effect: string;
  enabled: boolean;
  version: number;
};

type JwtPayload = {
  role?: string;
  sub?: string;
  exp?: number;
};

function decodeToken(token: string): JwtPayload {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch {
    return {};
  }
}

async function apiJson<T>(
  path: string,
  token: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set('Authorization', `Bearer ${token}`);

  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API}${path}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = Array.isArray(data?.detail)
      ? data.detail.map((item: any) => item.msg).join(', ')
      : data?.detail;

    throw new Error(detail || `Request failed (${response.status})`);
  }

  return data as T;
}

function App() {
  const [token, setToken] = useState(
    localStorage.getItem('sentinel_token') || '',
  );
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tools, setTools] = useState<Tool[]>([]);
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [alerts, setAlerts] = useState<Event[]>([]);
  const [approvals, setApprovals] = useState<any[]>([]);
  const [approvedApprovals, setApprovedApprovals] = useState<any[]>([]);
  const [executedApprovals, setExecutedApprovals] = useState<any[]>([]);
  const [tab, setTab] = useState('overview');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const role = decodeToken(token).role || 'viewer';
  const canManage = role === 'admin' || role === 'operator';

  async function load() {
    if (!token) return;

    setLoading(true);

    try {
      const requests = await Promise.all([
        apiJson<Agent[]>('/agents', token),
        apiJson<Tool[]>('/tools', token),
        apiJson<Policy[]>('/policies', token),
        apiJson<Event[]>('/events?limit=50', token),
        apiJson<Event[]>('/alerts?limit=20', token),
      ]);

      setAgents(requests[0]);
      setTools(requests[1]);
      setPolicies(requests[2]);
      setEvents(requests[3]);
      setAlerts(requests[4]);

      if (canManage) {
        const approvalRows = await apiJson<any[]>('/approvals?status=all', token);
        setApprovals(approvalRows.filter((approval) => approval.status === 'pending'));
        setApprovedApprovals(approvalRows.filter((approval) => approval.status === 'approved' && approval.executed !== true));
        setExecutedApprovals(approvalRows.filter((approval) => approval.executed === true));
      } else {
        setApprovals([]);

        if (tab === 'approvals') {
          setTab('overview');
        }
      }

      setError('');
    } catch (err: any) {
      setError(err?.message || 'Unable to load SentinelOps AI data.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [token]);

  if (!token) {
    return (
      <Login
        onLogin={(newToken) => {
          localStorage.setItem('sentinel_token', newToken);
          setToken(newToken);
        }}
      />
    );
  }

  const blocked = events.filter((event) => event.decision === 'block').length;
  const approvalEvents = events.filter(
    (event) => event.decision === 'approval',
  ).length;
  const allowed = events.filter((event) => event.decision === 'allow').length;

  return (
    <main className="shell">
      <header>
        <div>
          <span className="eyebrow">
            SENTINELOPS AI · RUNTIME CONTROL PLANE
          </span>

          <h1>Control what AI agents actually do.</h1>

          <p>
            Identity, policy, contextual risk, human approval and
            evidence—inline with every consequential action.
          </p>
        </div>

        <button className="ghost" onClick={load} disabled={loading}>
          <RefreshCw size={16} className={loading ? 'spin' : ''} />
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </header>

      <nav className="tabs">
        <button
          className={tab === 'overview' ? 'active' : ''}
          onClick={() => setTab('overview')}
        >
          Overview
        </button>

        <button
          className={tab === 'agents' ? 'active' : ''}
          onClick={() => setTab('agents')}
        >
          Agents
        </button>

        <button
          className={tab === 'tools' ? 'active' : ''}
          onClick={() => setTab('tools')}
        >
          Tools
        </button>

        <button
          className={tab === 'policies' ? 'active' : ''}
          onClick={() => setTab('policies')}
        >
          Policies
        </button>

        <button
          className={tab === 'security' ? 'active' : ''}
          onClick={() => setTab('security')}
        >
          Security <span>{alerts.length}</span>
        </button>

        {canManage && (
          <button
            className={tab === 'approvals' ? 'active' : ''}
            onClick={() => setTab('approvals')}
          >
            Approvals <span>{approvals.length}</span>
          </button>
        )}

        <button
          className="logout"
          onClick={() => {
            localStorage.removeItem('sentinel_token');
            setToken('');
            setTab('overview');
          }}
        >
          Sign out
        </button>
      </nav>

      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}

      {tab === 'overview' && (
        <>
          <section className="grid">
            <Card
              icon={<Bot />}
              title="Agents"
              value={agents.length}
              text="Registered identities"
            />

            <Card
              icon={<CheckCircle2 />}
              title="Allowed"
              value={allowed}
              text="Recent actions"
            />

            <Card
              icon={<Clock3 />}
              title="Approval"
              value={approvalEvents + approvals.length}
              text="Escalated actions"
            />

            <Card
              icon={<AlertTriangle />}
              title="Blocked"
              value={blocked}
              text="Denied actions"
            />
          </section>

          <section className="two">
            <Panel title="Runtime Activity">
              <div className="events">
                {events.length === 0 ? (
                  <Empty />
                ) : (
                  events.map((event) => (
                    <EventRow key={event.id} event={event} />
                  ))
                )}
              </div>
            </Panel>

            <Panel title="Enforcement path">
              <div className="flow">
                <span>Agent</span>
                <i>→</i>
                <span>Identity</span>
                <i>→</i>
                <span>Policy</span>
                <i>→</i>
                <span>Risk</span>
                <i>→</i>
                <strong>ALLOW / APPROVAL / BLOCK</strong>
              </div>

              <div className="principle">
                <ShieldCheck />

                <div>
                  <strong>Trajectory-aware decisions</strong>

                  <p>
                    SentinelOps evaluates the current action together with
                    recent session actions, data sensitivity, financial value,
                    destination and autonomy.
                  </p>
                </div>
              </div>
            </Panel>
          </section>
        </>
      )}

      {tab === 'agents' && (
        <AgentPanel agents={agents} />
      )}

      {tab === 'tools' && (
        <ToolsPanel
          tools={tools}
          agents={agents}
          token={token}
          canManage={canManage}
          reload={load}
          setError={setError}
        />
      )}

      {tab === 'policies' && (
        <PoliciesPanel
          policies={policies}
          token={token}
          canManage={canManage}
          reload={load}
          setError={setError}
        />
      )}

      {tab === 'security' && (
        <SecurityPanel alerts={alerts} />
      )}

      {tab === 'approvals' && canManage && (
        <ApprovalPanel
          approvals={approvals}
          approvedApprovals={approvedApprovals}
          executedApprovals={executedApprovals}
          reload={load}
          token={token}
          setError={setError}
        />
      )}

      <footer>
        <KeyRound />
        Agent API keys are scoped to one agent and are intended for runtime
        traffic—not dashboard login.
      </footer>
    </main>
  );
}

function AgentPanel({ agents }: { agents: Agent[] }) {
  return (
    <section className="panel">
      <div className="panelHead">
        <div>
          <h2>Agent Registry</h2>
          <span>Non-human identities and autonomy posture</span>
        </div>

        <span>{agents.length} registered</span>
      </div>

      <div className="agentGrid">
        {agents.map((agent) => (
          <article className="agent" key={agent.id}>
            <div className="agentIcon">
              <Bot />
            </div>

            <div>
              <h3>{agent.name}</h3>

              <p>
                {agent.description || 'Runtime-controlled AI agent'}
              </p>

              <div className="badges">
                <span>{agent.autonomy_level}</span>

                <span className={agent.active ? 'ok' : 'danger'}>
                  {agent.active ? 'ACTIVE' : 'SUSPENDED'}
                </span>
              </div>
            </div>
          </article>
        ))}
      </div>

      {agents.length === 0 && <Empty />}
    </section>
  );
}

function ToolsPanel({
  tools,
  agents,
  token,
  canManage,
  reload,
  setError,
}: {
  tools: Tool[];
  agents: Agent[];
  token: string;
  canManage: boolean;
  reload: () => void;
  setError: (message: string) => void;
}) {
  const [showForm, setShowForm] = useState(false);
  const [selectedTool, setSelectedTool] = useState('');
  const [selectedAgent, setSelectedAgent] = useState('');
  const [binding, setBinding] = useState(false);

  async function bindTool() {
    if (!selectedTool || !selectedAgent) {
      setError('Select both a tool and an agent.');
      return;
    }

    setBinding(true);

    try {
      await apiJson(
        `/tools/${selectedTool}/bind/${selectedAgent}`,
        token,
        {
          method: 'POST',
          body: JSON.stringify({ enabled: true }),
        },
      );

      setError('');
      setSelectedTool('');
      setSelectedAgent('');
      reload();
    } catch (err: any) {
      setError(err?.message || 'Unable to bind tool.');
    } finally {
      setBinding(false);
    }
  }

  return (
    <section className="panel">
      <div className="panelHead">
        <div>
          <h2>Tool Registry</h2>
          <span>
            Runtime capabilities available to controlled agents
          </span>
        </div>

        {canManage && (
          <button
            className="primary smallButton"
            onClick={() => setShowForm(!showForm)}
          >
            <Plus size={16} />
            {showForm ? 'Close' : 'Add Tool'}
          </button>
        )}
      </div>

      {canManage && showForm && (
        <ToolForm
          token={token}
          reload={() => {
            setShowForm(false);
            reload();
          }}
          setError={setError}
        />
      )}

      {canManage && tools.length > 0 && agents.length > 0 && (
        <div className="bindingBox">
          <div>
            <strong>Bind tool to agent</strong>
            <small>
              Grant an enabled tool capability to a specific agent.
            </small>
          </div>

          <div className="bindingControls">
            <select
              value={selectedTool}
              onChange={(event) => setSelectedTool(event.target.value)}
            >
              <option value="">Select tool</option>

              {tools
                .filter((tool) => tool.active)
                .map((tool) => (
                  <option value={tool.id} key={tool.id}>
                    {tool.name}
                  </option>
                ))}
            </select>

            <select
              value={selectedAgent}
              onChange={(event) => setSelectedAgent(event.target.value)}
            >
              <option value="">Select agent</option>

              {agents
                .filter((agent) => agent.active)
                .map((agent) => (
                  <option value={agent.id} key={agent.id}>
                    {agent.name}
                  </option>
                ))}
            </select>

            <button
              className="secondary"
              onClick={bindTool}
              disabled={binding}
            >
              <Link2 size={16} />
              {binding ? 'Binding...' : 'Bind'}
            </button>
          </div>
        </div>
      )}

      <div className="resourceGrid">
        {tools.map((tool) => (
          <article className="resourceCard" key={tool.id}>
            <div className="resourceIcon">
              <Wrench />
            </div>

            <div className="resourceBody">
              <div className="resourceTitle">
                <h3>{tool.name}</h3>

                <span className={tool.active ? 'ok' : 'danger'}>
                  {tool.active ? 'ACTIVE' : 'INACTIVE'}
                </span>
              </div>

              <p>
                {tool.description || 'Runtime integration capability'}
              </p>

              <div className="resourceMeta">
                <span>Sensitivity {tool.sensitivity}/100</span>
                <span>Adapter {tool.adapter_name}</span>
              </div>

              {tool.endpoint && (
                <small className="endpoint">
                  {tool.endpoint}
                </small>
              )}
            </div>
          </article>
        ))}
      </div>

      {tools.length === 0 && (
        <Empty
          text={
            canManage
              ? 'No tools registered yet. Add the first runtime capability.'
              : 'No tools are registered for this workspace.'
          }
        />
      )}
    </section>
  );
}

function ToolForm({
  token,
  reload,
  setError,
}: {
  token: string;
  reload: () => void;
  setError: (message: string) => void;
}) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [sensitivity, setSensitivity] = useState('20');
  const [adapterName, setAdapterName] = useState('simulated');
  const [credentialRef, setCredentialRef] = useState('');
  const [endpoint, setEndpoint] = useState('');
  const [saving, setSaving] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();

    if (!name.trim()) {
      setError('Tool name is required.');
      return;
    }

    setSaving(true);

    try {
      await apiJson<Tool>('/tools', token, {
        method: 'POST',
        body: JSON.stringify({
          name: name.trim(),
          description: description.trim() || null,
          sensitivity: Number(sensitivity),
          adapter_name: adapterName.trim() || 'simulated',
          credential_ref: credentialRef.trim() || null,
          endpoint: endpoint.trim() || null,
        }),
      });

      setError('');
      reload();
    } catch (err: any) {
      setError(err?.message || 'Unable to create tool.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="resourceForm" onSubmit={submit}>
      <div className="formGrid">
        <Field
          label="Tool name"
          value={name}
          onChange={setName}
          placeholder="Finance API"
          required
        />

        <Field
          label="Adapter"
          value={adapterName}
          onChange={setAdapterName}
          placeholder="simulated"
          required
        />

        <Field
          label="Sensitivity (0–100)"
          value={sensitivity}
          onChange={setSensitivity}
          type="number"
          min="0"
          max="100"
        />

        <Field
          label="Credential reference"
          value={credentialRef}
          onChange={setCredentialRef}
          placeholder="finance-prod"
        />

        <Field
          label="Endpoint"
          value={endpoint}
          onChange={setEndpoint}
          placeholder="https://api.example.com"
        />

        <Field
          label="Description"
          value={description}
          onChange={setDescription}
          placeholder="What this tool can do"
        />
      </div>

      <div className="formActions">
        <button
          type="submit"
          className="primary"
          disabled={saving}
        >
          <Plus size={16} />
          {saving ? 'Creating...' : 'Create Tool'}
        </button>
      </div>
    </form>
  );
}

function PoliciesPanel({
  policies,
  token,
  canManage,
  reload,
  setError,
}: {
  policies: Policy[];
  token: string;
  canManage: boolean;
  reload: () => void;
  setError: (message: string) => void;
}) {
  const [showForm, setShowForm] = useState(false);

  return (
    <section className="panel">
      <div className="panelHead">
        <div>
          <h2>Policy Engine</h2>
          <span>
            Runtime rules governing risk, approval and enforcement
          </span>
        </div>

        {canManage && (
          <button
            className="primary smallButton"
            onClick={() => setShowForm(!showForm)}
          >
            <Plus size={16} />
            {showForm ? 'Close' : 'Add Policy'}
          </button>
        )}
      </div>

      {canManage && showForm && (
        <PolicyForm
          token={token}
          reload={() => {
            setShowForm(false);
            reload();
          }}
          setError={setError}
        />
      )}

      <div className="resourceGrid">
        {policies.map((policy) => (
          <article className="resourceCard" key={policy.id}>
            <div className="resourceIcon">
              <FileCheck2 />
            </div>

            <div className="resourceBody">
              <div className="resourceTitle">
                <h3>{policy.name}</h3>

                <span className={policy.enabled ? 'ok' : 'danger'}>
                  {policy.enabled ? 'ENABLED' : 'DISABLED'}
                </span>
              </div>

              <div className="policyPattern">
                {policy.action_pattern}
              </div>

              <div className="resourceMeta">
                <span>Min risk {policy.min_risk}</span>

                <span>
                  Max value{' '}
                  {policy.max_financial_amount == null
                    ? 'Unlimited'
                    : policy.max_financial_amount}
                </span>

                <span>
                  {policy.require_approval
                    ? 'Human approval'
                    : 'No approval'}
                </span>
              </div>

              <div className="policyFooter">
                <strong>
                  {policy.effect.toUpperCase()}
                </strong>

                <small>Version {policy.version}</small>
              </div>
            </div>
          </article>
        ))}
      </div>

      {policies.length === 0 && (
        <Empty
          text={
            canManage
              ? 'No policies registered yet. Add the first enforcement rule.'
              : 'No policies are registered for this workspace.'
          }
        />
      )}
    </section>
  );
}

function PolicyForm({
  token,
  reload,
  setError,
}: {
  token: string;
  reload: () => void;
  setError: (message: string) => void;
}) {
  const [name, setName] = useState('');
  const [actionPattern, setActionPattern] = useState('*');
  const [minRisk, setMinRisk] = useState('0');
  const [maxFinancialAmount, setMaxFinancialAmount] = useState('');
  const [requireApproval, setRequireApproval] = useState(false);
  const [effect, setEffect] = useState('allow');
  const [saving, setSaving] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();

    if (!name.trim()) {
      setError('Policy name is required.');
      return;
    }

    setSaving(true);

    try {
      await apiJson<Policy>('/policies', token, {
        method: 'POST',
        body: JSON.stringify({
          name: name.trim(),
          action_pattern: actionPattern.trim() || '*',
          min_risk: Number(minRisk),
          max_financial_amount:
            maxFinancialAmount.trim() === ''
              ? null
              : Number(maxFinancialAmount),
          require_approval: requireApproval,
          effect,
        }),
      });

      setError('');
      reload();
    } catch (err: any) {
      setError(err?.message || 'Unable to create policy.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="resourceForm" onSubmit={submit}>
      <div className="formGrid">
        <Field
          label="Policy name"
          value={name}
          onChange={setName}
          placeholder="High value approval"
          required
        />

        <Field
          label="Action pattern"
          value={actionPattern}
          onChange={setActionPattern}
          placeholder="transfer_*"
        />

        <Field
          label="Minimum risk"
          value={minRisk}
          onChange={setMinRisk}
          type="number"
          min="0"
          max="100"
        />

        <Field
          label="Maximum financial amount"
          value={maxFinancialAmount}
          onChange={setMaxFinancialAmount}
          type="number"
          min="0"
          placeholder="Optional"
        />

        <div className="field">
          <label htmlFor="effect">Effect</label>

          <select
            id="effect"
            value={effect}
            onChange={(event) => setEffect(event.target.value)}
          >
            <option value="allow">Allow</option>
            <option value="approval">Approval</option>
            <option value="block">Block</option>
          </select>
        </div>

        <label className="checkField">
          <input
            type="checkbox"
            checked={requireApproval}
            onChange={(event) =>
              setRequireApproval(event.target.checked)
            }
          />

          <span>
            <strong>Require human approval</strong>
            <small>
              Pause matched consequential actions for an operator.
            </small>
          </span>
        </label>
      </div>

      <div className="formActions">
        <button
          type="submit"
          className="primary"
          disabled={saving}
        >
          <FileCheck2 size={16} />
          {saving ? 'Creating...' : 'Create Policy'}
        </button>
      </div>
    </form>
  );
}

function SecurityPanel({ alerts }: { alerts: Event[] }) {
  return (
    <section className="panel">
      <div className="panelHead">
        <div>
          <h2>Security Alerts</h2>
          <span>
            Runtime decisions classified as security events
          </span>
        </div>

        <span>{alerts.length} recent</span>
      </div>

      {alerts.length === 0 ? (
        <Empty text="No security alerts detected." />
      ) : (
        <div className="events">
          {alerts.map((event) => (
            <EventRow key={event.id} event={event} security />
          ))}
        </div>
      )}
    </section>
  );
}


function ApprovalPanel({
  approvals,
  approvedApprovals,
  executedApprovals,
  reload,
  token,
  setError,
}: {
  approvals: any[];
  approvedApprovals: any[];
  executedApprovals: any[];
  reload: () => void;
  token: string;
  setError: (message: string) => void;
}) {
  const [busyId, setBusyId] = useState<string | null>(null);

  async function decide(id: string, approve: boolean) {
    setBusyId(id);

    try {
      await apiJson(
        `/approvals/${id}/decision?approve=${approve}`,
        token,
        { method: 'POST' },
      );

      setError('');
      reload();
    } catch (err: any) {
      setError(err?.message || 'Approval action failed.');
    } finally {
      setBusyId(null);
    }
  }

  async function execute(id: string) {
    setBusyId(id);

    try {
      await apiJson(
        `/approvals/${id}/execute`,
        token,
        { method: 'POST' },
      );

      setError('');
      reload();
    } catch (err: any) {
      setError(err?.message || 'Execution failed.');
    } finally {
      setBusyId(null);
    }
  }

  return (
    <section className="panel">
      <div className="panelHead">
        <div>
          <h2>Human Approval Queue</h2>
          <span>
            Consequential actions paused before execution
          </span>
        </div>

        <span>{approvals.length} pending</span>
      </div>

      {approvals.length === 0 ? (
        <Empty text="No actions are currently waiting for approval." />
      ) : (
        <div className="approvalList">
          {approvals.map((approval) => (
            <article className="approval" key={approval.id}>
              <div>
                <strong>{approval.action}</strong>

                <small>
                  {approval.resource} · risk {approval.risk_score}/100
                </small>

                <p>
                  {(approval.reasons || []).join(' · ')}
                </p>
              </div>

              <div className="approvalActions">
                <button
                  onClick={() => decide(approval.id, true)}
                  disabled={busyId === approval.id}
                >
                  Approve
                </button>

                <button
                  onClick={() => decide(approval.id, false)}
                  disabled={busyId === approval.id}
                >
                  Reject
                </button>

                {approval.status === 'approved' && (
                  <button
                    className="primary"
                    onClick={() => execute(approval.id)}
                    disabled={busyId === approval.id}
                  >
                    Execute
                  </button>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
      
      <h3>Approved - Ready to Execute</h3>
      {approvedApprovals.length === 0 ? (
        <Empty text="No approved actions are waiting for execution." />
      ) : (
        <div className="approvalList">
          {approvedApprovals.map((approval) => (
            <article className="approval" key={approval.id}>
              <div>
                <strong>{approval.action}</strong>
                <small>{approval.resource} � risk {approval.risk_score}/100</small>
                <p>{(approval.reasons || []).join(' � ')}</p>
              </div>
              <div className="approvalActions">
                <button
                  className="primary"
                  onClick={() => execute(approval.id)}
                  disabled={busyId === approval.id}
                >
                  Execute
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      <h3>Recently Executed</h3>
      {executedApprovals.length === 0 ? (
        <Empty text="No executed approvals yet." />
      ) : (
        <div className="approvalList">
          {executedApprovals.slice(0, 10).map((approval) => (
            <article className="approval" key={approval.id}>
              <div>
                <strong>{approval.action}</strong>
                <small>{approval.resource} � risk {approval.risk_score}/100</small>
                <p>{(approval.reasons || []).join(' � ')}</p>
              </div>
              <div className="approvalActions">
                <span>Executed</span>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}


function EventRow({
  event,
  security = false,
}: {
  event: Event;
  security?: boolean;
}) {
  return (
    <div className="event">
      <div className={`decision ${event.decision}`}>
        {event.decision === 'allow' ? (
          <CheckCircle2 />
        ) : event.decision === 'block' ? (
          <XCircle />
        ) : (
          <Clock3 />
        )}
      </div>

      <div>
        <strong>{event.action}</strong>

        <small>
          {event.resource} · risk {event.risk_score}/100
          {security ? ' · security' : ''}
        </small>
      </div>

      <b>{event.decision.toUpperCase()}</b>
    </div>
  );
}

function Card({
  icon,
  title,
  value,
  text,
}: {
  icon: React.ReactNode;
  title: string;
  value: number;
  text: string;
}) {
  return (
    <article className="card">
      {icon}
      <strong>{title}</strong>
      <b>{value}</b>
      <small>{text}</small>
    </article>
  );
}

function Panel({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="panel">
      <h2>{title}</h2>
      {children}
    </div>
  );
}

function Empty({
  text = 'No runtime events yet. Connect the Finance Agent SDK to create the first decision.',
}: {
  text?: string;
}) {
  return (
    <div className="empty">
      <Activity />
      <p>{text}</p>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  type = 'text',
  min,
  max,
  required = false,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: string;
  min?: string;
  max?: string;
  required?: boolean;
}) {
  return (
    <div className="field">
      <label>{label}</label>

      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        type={type}
        min={min}
        max={max}
        required={required}
      />
    </div>
  );
}

function Login({
  onLogin,
}: {
  onLogin: (token: string) => void;
}) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError('');

    if (mode === 'register' && !name.trim()) {
      setError('Please enter your full name.');
      return;
    }

    if (!email.trim() || !password) {
      setError('Please enter your email and password.');
      return;
    }

    setLoading(true);

    try {
      const path = mode === 'login' ? 'login' : 'register';

      const body =
        mode === 'login'
          ? { email, password }
          : {
              email,
              password,
              name: name.trim(),
            };

      const response = await fetch(`${API}/auth/${path}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item: any) => item.msg).join(', ')
          : data.detail;

        setError(detail || 'Request failed.');
        return;
      }

      if (!data.access_token) {
        setError(
          'Authentication succeeded but no access token was returned.',
        );
        return;
      }

      onLogin(data.access_token);
    } catch (err: any) {
      setError(
        err?.message ||
          'Unable to connect to the SentinelOps AI API.',
      );
    } finally {
      setLoading(false);
    }
  }

  function switchMode() {
    setError('');
    setMode(mode === 'login' ? 'register' : 'login');
  }

  return (
    <main className="auth">
      <form onSubmit={submit} className="authCard">
        <div className="logo">
          <ShieldCheck />
        </div>

        <span className="eyebrow">SENTINELOPS AI</span>

        <h1>
          {mode === 'login'
            ? 'Secure control plane'
            : 'Create workspace owner'}
        </h1>

        <p className="authSubtitle">
          {mode === 'login'
            ? 'Sign in to manage your AI runtime control plane.'
            : 'Create the first administrator account for this workspace.'}
        </p>

        {mode === 'register' && (
          <div className="field">
            <label htmlFor="name">Full name</label>

            <input
              id="name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Your full name"
              autoComplete="name"
            />
          </div>
        )}

        <div className="field">
          <label htmlFor="email">Email</label>

          <input
            id="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@example.com"
            type="email"
            autoComplete="email"
          />
        </div>

        <div className="field">
          <label htmlFor="password">Password</label>

          <input
            id="password"
            value={password}
            onChange={(event) =>
              setPassword(event.target.value)
            }
            placeholder="Enter your password"
            type="password"
            autoComplete={
              mode === 'login'
                ? 'current-password'
                : 'new-password'
            }
          />
        </div>

        {error && (
          <div className="error" role="alert">
            {error}
          </div>
        )}

        <button
          type="submit"
          className="primary"
          disabled={loading}
        >
          {loading
            ? 'Please wait...'
            : mode === 'login'
              ? 'Sign in'
              : 'Create account'}
        </button>

        <button
          type="button"
          className="link"
          onClick={switchMode}
          disabled={loading}
        >
          {mode === 'login'
            ? 'Create the first workspace account'
            : 'Back to sign in'}
        </button>
      </form>
    </main>
  );
}

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);





