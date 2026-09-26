import React, { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  Bot,
  Check,
  CheckCircle2,
  ChevronRight,
  CircleDot,
  Clock3,
  Database,
  FileCheck2,
  Fingerprint,
  Gauge,
  KeyRound,
  LayoutDashboard,
  LogOut,
  Network,
  Play,
  Plus,
  RefreshCw,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Terminal,
  Wrench,
  X,
  XCircle,
} from 'lucide-react';
import './styles.css';

const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

type Event = {
  id: string;
  agent_id?: string;
  tool_id?: string;
  action: string;
  resource: string;
  decision: string;
  risk_score: number;
  reasons?: string[];
  metadata_json?: Record<string, unknown>;
  created_at: string;
};

type Agent = {
  id: string;
  name: string;
  description?: string;
  autonomy?: string;
  is_active?: boolean;
};

type Tool = {
  id: string;
  name: string;
  description?: string;
  sensitivity?: number;
  adapter?: string;
  endpoint?: string;
  is_active?: boolean;
};

type Policy = {
  id: string;
  name: string;
  action_pattern: string;
  min_risk_score?: number;
  max_financial_impact?: number | null;
  require_approval?: boolean;
  effect?: string;
};

type JwtPayload = {
  sub?: string;
  email?: string;
  role?: string;
  exp?: number;
};

type Tone = 'success' | 'warning' | 'danger';

function decodeToken(token: string): JwtPayload {
  try {
    return JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
  } catch {
    return {};
  }
}

function decisionTone(decision: string): Tone {
  const value = decision.toLowerCase();
  if (value === 'allow') return 'success';
  if (value === 'approval') return 'warning';
  return 'danger';
}

function riskTone(score: number): Tone {
  if (score >= 70) return 'danger';
  if (score >= 40) return 'warning';
  return 'success';
}

async function apiJson(path: string, token: string, options?: RequestInit) {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...(options?.headers || {}),
    },
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }

  if (response.status === 204) return null;
  return response.json();
}

function App() {
  const [token, setToken] = useState(() => localStorage.getItem('sentinelops_token') || '');
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

  const payload = useMemo(() => decodeToken(token), [token]);
  const isManager = payload.role === 'manager' || payload.role === 'admin';

  async function load() {
    if (!token) return;

    setLoading(true);
    setError('');

    try {
      const [agentsData, toolsData, policiesData, eventsData, alertsData] = await Promise.all([
        apiJson('/agents', token),
        apiJson('/tools', token),
        apiJson('/policies', token),
        apiJson('/events?limit=50', token),
        apiJson('/alerts?limit=20', token),
      ]);

      setAgents(Array.isArray(agentsData) ? agentsData : agentsData.items || []);
      setTools(Array.isArray(toolsData) ? toolsData : toolsData.items || []);
      setPolicies(Array.isArray(policiesData) ? policiesData : policiesData.items || []);
      setEvents(Array.isArray(eventsData) ? eventsData : eventsData.items || []);
      setAlerts(Array.isArray(alertsData) ? alertsData : alertsData.items || []);

      if (isManager) {
        const approvalData = await apiJson('/approvals?status=all', token);
        const items = Array.isArray(approvalData) ? approvalData : approvalData.items || [];

        setApprovals(items.filter((item: any) => item.status === 'pending'));
        setApprovedApprovals(
          items.filter(
            (item: any) =>
              item.status === 'approved' &&
              item.executed !== true &&
              item.status !== 'executed',
          ),
        );
        setExecutedApprovals(
          items.filter(
            (item: any) =>
              item.status === 'executed' ||
              item.executed === true,
          ),
        );
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load dashboard');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (token) {
      localStorage.setItem('sentinelops_token', token);
      load();
    }
  }, [token]);

  function signOut() {
    localStorage.removeItem('sentinelops_token');
    setToken('');
  }

  if (!token) {
    return <Login onLogin={setToken} />;
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'agents', label: 'Agents', icon: Bot },
    { id: 'tools', label: 'Tools', icon: Wrench },
    { id: 'policies', label: 'Policies', icon: ShieldCheck },
    { id: 'security', label: 'Security', icon: ShieldAlert, count: alerts.length },
    ...(isManager
      ? [{ id: 'approvals', label: 'Approvals', icon: FileCheck2, count: approvals.length }]
      : []),
  ];

  return (
    <div className="shell">
      <header>
        <div>
          <span className="eyebrow">SENTINELOPS AI · RUNTIME CONTROL PLANE</span>
          <h1>Control what AI agents actually do.</h1>
          <p>
            Identity, tools, policy, risk, approval, execution and evidence in one
            operational control plane.
          </p>
        </div>

        <button className="ghost" onClick={load} disabled={loading}>
          <RefreshCw size={15} className={loading ? 'spin' : ''} />
          Refresh
        </button>
      </header>

      <nav className="tabs">
        <div className="tabsWrap">
          {tabs.map(({ id, label, icon: Icon, count }) => (
            <button
              key={id}
              className={tab === id ? 'active' : ''}
              onClick={() => setTab(id)}
            >
              <Icon size={15} />
              {label}
              {typeof count === 'number' && count > 0 && <span>{count}</span>}
            </button>
          ))}
        </div>

        <button className="logout" onClick={signOut}>
          <LogOut size={14} />
          Sign out
        </button>
      </nav>

      {error && (
        <div className="error">
          <strong>Request error</strong>
          <div>{error}</div>
        </div>
      )}

      {tab === 'overview' && (
        <>
          <section className="grid">
            <article className="card">
              <div className="cardHead">
                <span className="cardIcon"><Bot /></span>
                <strong>Active Agents</strong>
              </div>
              <b>{agents.filter((agent) => agent.is_active !== false).length}</b>
              <small>{agents.length} registered agents</small>
            </article>

            <article className="card">
              <div className="cardHead">
                <span className="cardIcon"><Wrench /></span>
                <strong>Active Tools</strong>
              </div>
              <b>{tools.filter((tool) => tool.is_active !== false).length}</b>
              <small>{tools.length} registered tools</small>
            </article>

            <article className="card">
              <div className="cardHead">
                <span className="cardIcon"><ShieldCheck /></span>
                <strong>Policies</strong>
              </div>
              <b>{policies.length}</b>
              <small>Runtime enforcement rules</small>
            </article>

            <article className="card">
              <div className="cardHead">
                <span className="cardIcon"><Activity /></span>
                <strong>Runtime Events</strong>
              </div>
              <b>{events.length}</b>
              <small>Recent recorded decisions</small>
            </article>
          </section>

          <section className="two">
            <div className="panel">
              <div className="panelHead">
                <div>
                  <h2>Runtime Activity</h2>
                  <span>Latest authorization decisions</span>
                </div>
                <span>{events.length} events</span>
              </div>

              <div className="events">
                {events.length === 0 ? (
                  <div className="empty">
                    <Activity />
                    <p>No runtime events recorded yet.</p>
                  </div>
                ) : (
                  events.slice(0, 20).map((event) => (
                    <EventRow key={event.id} event={event} />
                  ))
                )}
              </div>
            </div>

            <div className="panel">
              <h2>Enforcement Flow</h2>

              <div className="flow">
                <span>Identity</span>
                <i>→</i>
                <span>Tool</span>
                <i>→</i>
                <span>Policy</span>
                <i>→</i>
                <span>Risk</span>
                <i>→</i>
                <strong>Decision</strong>
                <i>→</i>
                <span>Evidence</span>
              </div>

              <div className="principle">
                <ShieldCheck />
                <div>
                  <strong>AI actions stay inside policy.</strong>
                  <p>
                    Every tool execution is evaluated before reaching the adapter,
                    with approval and runtime evidence when required.
                  </p>
                </div>
              </div>
            </div>
          </section>
        </>
      )}

      {tab === 'agents' && (
        <div className="panel">
          <div className="panelHead">
            <div>
              <h2>Agents</h2>
              <span>Registered AI identities</span>
            </div>
            <span>{agents.length} agents</span>
          </div>

          <div className="agentGrid">
            {agents.length === 0 ? (
              <div className="empty">
                <Bot />
                <p>No agents registered.</p>
              </div>
            ) : (
              agents.map((agent) => (
                <article className="agent" key={agent.id}>
                  <div className="agentIcon">
                    <Bot size={19} />
                  </div>

                  <div>
                    <h3>{agent.name}</h3>
                    <p>{agent.description || 'No description provided.'}</p>

                    <div className="badges">
                      <span>{agent.autonomy || 'Not specified'}</span>
                      <span className={agent.is_active === false ? 'danger' : 'ok'}>
                        {agent.is_active === false ? 'Suspended' : 'Active'}
                      </span>
                    </div>
                  </div>
                </article>
              ))
            )}
          </div>
        </div>
      )}

      {tab === 'tools' && (
        <ToolsPanel
          token={token}
          agents={agents}
          tools={tools}
          reload={load}
          setError={setError}
        />
      )}

      {tab === 'policies' && (
        <PoliciesPanel
          token={token}
          policies={policies}
          reload={load}
          setError={setError}
        />
      )}

      {tab === 'security' && (
        <div className="panel">
          <div className="panelHead">
            <div>
              <h2>Security</h2>
              <span>Risk signals and security events</span>
            </div>
            <span>{alerts.length} alerts</span>
          </div>

          <div className="events">
            {alerts.length === 0 ? (
              <div className="empty">
                <ShieldCheck />
                <p>No active security alerts.</p>
              </div>
            ) : (
              alerts.map((event) => (
                <EventRow key={event.id} event={event} />
              ))
            )}
          </div>
        </div>
      )}

      {tab === 'approvals' && isManager && (
        <ApprovalsPanel
          token={token}
          approvals={approvals}
          approvedApprovals={approvedApprovals}
          executedApprovals={executedApprovals}
          reload={load}
          setError={setError}
        />
      )}

      <footer>
        <Fingerprint />
        <span>SentinelOps AI · Runtime authorization and evidence layer</span>
      </footer>
    </div>
  );
}

function EventRow({ event }: { event: Event }) {
  const tone = decisionTone(event.decision);
  const risk = riskTone(event.risk_score);

  return (
    <div className="event">
      <div className={`decision ${event.decision.toLowerCase()}`}>
        {event.decision.toLowerCase() === 'allow' && <CheckCircle2 size={17} />}
        {event.decision.toLowerCase() === 'block' && <XCircle size={17} />}
        {event.decision.toLowerCase() === 'approval' && <Clock3 size={17} />}
      </div>

      <div className="eventBody">
        <strong className="mono">{event.action}</strong>
        <small>{event.resource}</small>
      </div>

      <span className={`badge tone-${tone}`}>
        {event.decision}
      </span>

      <div className="meterRow">
        <span className="riskbar">
          <span
            className={`riskfill tone-${risk}`}
            style={{ width: `${Math.min(100, Math.max(0, event.risk_score))}%` }}
          />
        </span>
        <span className="riskvalue">{event.risk_score} risk</span>
      </div>
    </div>
  );
}

function ToolsPanel({
  token,
  agents,
  tools,
  reload,
  setError,
}: {
  token: string;
  agents: Agent[];
  tools: Tool[];
  reload: () => Promise<void>;
  setError: (value: string) => void;
}) {
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [sensitivity, setSensitivity] = useState('1');
  const [adapter, setAdapter] = useState('simulated');
  const [endpoint, setEndpoint] = useState('');
  const [selectedTool, setSelectedTool] = useState('');
  const [selectedAgent, setSelectedAgent] = useState('');
  const [saving, setSaving] = useState(false);

  async function addTool(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError('');

    try {
      await apiJson('/tools', token, {
        method: 'POST',
        body: JSON.stringify({
          name,
          description,
          sensitivity: Number(sensitivity),
          adapter,
          endpoint: endpoint || null,
        }),
      });

      setName('');
      setDescription('');
      setSensitivity('1');
      setAdapter('simulated');
      setEndpoint('');
      setShowForm(false);
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create tool');
    } finally {
      setSaving(false);
    }
  }

  async function bindTool() {
    if (!selectedTool || !selectedAgent) return;

    setSaving(true);
    setError('');

    try {
      await apiJson(`/tools/${selectedTool}/bind/${selectedAgent}`, token, {
        method: 'POST',
      });
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to bind tool');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="panel">
      <div className="panelHead">
        <div>
          <h2>Tools</h2>
          <span>Capabilities available to AI agents</span>
        </div>
        <button
          className="secondary smallButton"
          onClick={() => setShowForm((value) => !value)}
        >
          <Plus size={15} />
          Add tool
        </button>
      </div>

      {showForm && (
        <form className="resourceForm" onSubmit={addTool}>
          <div className="formGrid">
            <div className="field">
              <label>Name</label>
              <input value={name} onChange={(e) => setName(e.target.value)} required />
            </div>

            <div className="field">
              <label>Description</label>
              <input value={description} onChange={(e) => setDescription(e.target.value)} />
            </div>

            <div className="field">
              <label>Sensitivity</label>
              <select value={sensitivity} onChange={(e) => setSensitivity(e.target.value)}>
                <option value="1">1 · Low</option>
                <option value="2">2 · Medium</option>
                <option value="3">3 · High</option>
                <option value="4">4 · Critical</option>
                <option value="5">5 · Critical+</option>
              </select>
            </div>

            <div className="field">
              <label>Adapter</label>
              <input value={adapter} onChange={(e) => setAdapter(e.target.value)} required />
            </div>

            <div className="field">
              <label>Endpoint</label>
              <input value={endpoint} onChange={(e) => setEndpoint(e.target.value)} />
            </div>
          </div>

          <div className="formActions">
            <button className="primary smallButton" type="submit" disabled={saving}>
              {saving ? 'Creating...' : 'Create tool'}
            </button>
          </div>
        </form>
      )}

      <div className="bindingBox">
        <div>
          <strong>Bind tool to agent</strong>
          <small>Control which AI identity can use a capability.</small>
        </div>

        <div className="bindingControls">
          <select value={selectedTool} onChange={(e) => setSelectedTool(e.target.value)}>
            <option value="">Select tool</option>
            {tools.map((tool) => (
              <option key={tool.id} value={tool.id}>{tool.name}</option>
            ))}
          </select>

          <select value={selectedAgent} onChange={(e) => setSelectedAgent(e.target.value)}>
            <option value="">Select agent</option>
            {agents.map((agent) => (
              <option key={agent.id} value={agent.id}>{agent.name}</option>
            ))}
          </select>

          <button className="secondary" onClick={bindTool} disabled={saving}>
            <Network size={15} />
            Bind
          </button>
        </div>
      </div>

      <div className="resourceGrid">
        {tools.length === 0 ? (
          <div className="empty">
            <Wrench />
            <p>No tools registered.</p>
          </div>
        ) : (
          tools.map((tool) => {
            const level = Math.min(5, Math.max(0, tool.sensitivity || 0));

            return (
              <article className="resourceCard" key={tool.id}>
                <div className="resourceIcon">
                  <Wrench size={18} />
                </div>

                <div className="resourceBody">
                  <div className="resourceTitle">
                    <h3>{tool.name}</h3>
                    <span className={tool.is_active === false ? 'danger' : 'ok'}>
                      {tool.is_active === false ? 'Inactive' : 'Active'}
                    </span>
                  </div>

                  <p>{tool.description || 'No description provided.'}</p>

                  <div className="meterRow">
                    <span>Sensitivity</span>
                    <span className="meter">
                      <span
                        className={`meterFill tone-${level >= 4 ? 'danger' : level >= 3 ? 'warning' : 'success'}`}
                        style={{ width: `${level * 20}%` }}
                      />
                    </span>
                    <span className="riskvalue">{level}/5</span>
                  </div>

                  <div className="resourceMeta">
                    <span className="mono">{tool.adapter || 'Not specified'}</span>
                    {tool.endpoint && <span className="endpoint">{tool.endpoint}</span>}
                  </div>
                </div>
              </article>
            );
          })
        )}
      </div>
    </div>
  );
}

function PoliciesPanel({
  token,
  policies,
  reload,
  setError,
}: {
  token: string;
  policies: Policy[];
  reload: () => Promise<void>;
  setError: (value: string) => void;
}) {
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [actionPattern, setActionPattern] = useState('');
  const [minRisk, setMinRisk] = useState('0');
  const [maxFinancial, setMaxFinancial] = useState('');
  const [requireApproval, setRequireApproval] = useState(false);
  const [effect, setEffect] = useState('allow');
  const [saving, setSaving] = useState(false);

  async function addPolicy(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError('');

    try {
      await apiJson('/policies', token, {
        method: 'POST',
        body: JSON.stringify({
          name,
          action_pattern: actionPattern,
          min_risk_score: Number(minRisk),
          max_financial_impact: maxFinancial === '' ? null : Number(maxFinancial),
          require_approval: requireApproval,
          effect,
        }),
      });

      setName('');
      setActionPattern('');
      setMinRisk('0');
      setMaxFinancial('');
      setRequireApproval(false);
      setEffect('allow');
      setShowForm(false);
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create policy');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="panel">
      <div className="panelHead">
        <div>
          <h2>Policies</h2>
          <span>Rules governing runtime authorization</span>
        </div>
        <button
          className="secondary smallButton"
          onClick={() => setShowForm((value) => !value)}
        >
          <Plus size={15} />
          Add policy
        </button>
      </div>

      {showForm && (
        <form className="resourceForm" onSubmit={addPolicy}>
          <div className="formGrid">
            <div className="field">
              <label>Name</label>
              <input value={name} onChange={(e) => setName(e.target.value)} required />
            </div>

            <div className="field">
              <label>Action pattern</label>
              <input
                className="mono"
                value={actionPattern}
                onChange={(e) => setActionPattern(e.target.value)}
                placeholder="security.*"
                required
              />
            </div>

            <div className="field">
              <label>Minimum risk</label>
              <input
                type="number"
                min="0"
                max="100"
                value={minRisk}
                onChange={(e) => setMinRisk(e.target.value)}
              />
            </div>

            <div className="field">
              <label>Max financial impact</label>
              <input
                type="number"
                min="0"
                value={maxFinancial}
                onChange={(e) => setMaxFinancial(e.target.value)}
              />
            </div>

            <div className="field">
              <label>Effect</label>
              <select value={effect} onChange={(e) => setEffect(e.target.value)}>
                <option value="allow">Allow</option>
                <option value="block">Block</option>
              </select>
            </div>

            <label className="checkField">
              <input
                type="checkbox"
                checked={requireApproval}
                onChange={(e) => setRequireApproval(e.target.checked)}
              />
              <span>
                <strong>Require human approval</strong>
                <small>Pause execution until a reviewer approves it.</small>
              </span>
            </label>
          </div>

          <div className="formActions">
            <button className="primary smallButton" type="submit" disabled={saving}>
              {saving ? 'Creating...' : 'Create policy'}
            </button>
          </div>
        </form>
      )}

      <div className="resourceGrid">
        {policies.length === 0 ? (
          <div className="empty">
            <Shield />
            <p>No policies configured.</p>
          </div>
        ) : (
          policies.map((policy) => {
            const effectValue = (policy.effect || 'allow').toLowerCase();
            const tone =
              effectValue === 'block'
                ? 'danger'
                : policy.require_approval
                  ? 'warning'
                  : 'success';

            return (
              <article className="resourceCard" key={policy.id}>
                <div className="resourceIcon">
                  {effectValue === 'block' ? (
                    <ShieldAlert size={18} />
                  ) : policy.require_approval ? (
                    <Clock3 size={18} />
                  ) : (
                    <ShieldCheck size={18} />
                  )}
                </div>

                <div className="resourceBody">
                  <div className="resourceTitle">
                    <h3>{policy.name}</h3>
                    <span className={tone === 'danger' ? 'danger' : 'ok'}>
                      {effectValue === 'block'
                        ? 'Block'
                        : policy.require_approval
                          ? 'Approval'
                          : 'Allow'}
                    </span>
                  </div>

                  <span className="policyPattern">{policy.action_pattern}</span>

                  <p>
                    Minimum risk: {policy.min_risk_score ?? 0}
                    {policy.max_financial_impact != null
                      ? ` · Max financial impact: ${policy.max_financial_impact}`
                      : ''}
                  </p>

                  <div className="policyFooter">
                    <small>
                      {policy.require_approval
                        ? 'Human approval required'
                        : 'Automatic enforcement'}
                    </small>

                    <span className={`badge tone-${tone}`}>
                      {policy.require_approval ? 'Review gate' : effectValue}
                    </span>
                  </div>
                </div>
              </article>
            );
          })
        )}
      </div>
    </div>
  );
}

function ApprovalsPanel({
  token,
  approvals,
  approvedApprovals,
  executedApprovals,
  reload,
  setError,
}: {
  token: string;
  approvals: any[];
  approvedApprovals: any[];
  executedApprovals: any[];
  reload: () => Promise<void>;
  setError: (value: string) => void;
}) {
  async function decide(id: string, decision: 'approve' | 'reject') {
    setError('');

    try {
      await apiJson(`/approvals/${id}/decision`, token, {
        method: 'POST',
        body: JSON.stringify({ decision }),
      });
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to update approval');
    }
  }

  async function execute(id: string) {
    setError('');

    try {
      await apiJson(`/approvals/${id}/execute`, token, {
        method: 'POST',
      });
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to execute approval');
    }
  }

  return (
    <div className="panel">
      <div className="panelHead">
        <div>
          <h2>Approval Queue</h2>
          <span>Human review before sensitive execution</span>
        </div>
        <span>{approvals.length} pending</span>
      </div>

      <h3 className="sectionTitle">Pending review</h3>

      <div className="approvalList">
        {approvals.length === 0 ? (
          <div className="empty">
            <CheckCircle2 />
            <p>No approvals waiting for review.</p>
          </div>
        ) : (
          approvals.map((approval) => (
            <article className="approval" key={approval.id}>
              <div>
                <strong className="mono">
                  {approval.action || approval.event?.action}
                </strong>
                <small>
                  {approval.resource || approval.event?.resource} · Risk {approval.risk ?? approval.risk_score ?? 0}
                </small>
                <p>
                  {Array.isArray(approval.reasons)
                    ? approval.reasons.join(' · ')
                    : 'Human review required by policy.'}
                </p>
              </div>

              <div className="approvalActions">
                <button onClick={() => decide(approval.id, 'approve')}>
                  <Check size={14} />
                  Approve
                </button>
                <button onClick={() => decide(approval.id, 'reject')}>
                  <X size={14} />
                  Reject
                </button>
              </div>
            </article>
          ))
        )}
      </div>

      <h3 className="sectionTitle">Approved · Ready to execute</h3>

      <div className="approvalList">
        {approvedApprovals.length === 0 ? (
          <div className="empty">
            <Clock3 />
            <p>No approved actions are waiting for execution.</p>
          </div>
        ) : (
          approvedApprovals.map((approval) => (
            <article className="approval" key={approval.id}>
              <div>
                <strong className="mono">
                  {approval.action || approval.event?.action}
                </strong>
                <small>
                  {approval.resource || approval.event?.resource} · Risk {approval.risk ?? approval.risk_score ?? 0}
                </small>
                <p>Approved by a human reviewer and ready for controlled execution.</p>
              </div>

              <div className="approvalActions">
                <button onClick={() => execute(approval.id)}>
                  <Play size={14} />
                  Execute
                </button>
              </div>
            </article>
          ))
        )}
      </div>

      <h3 className="sectionTitle">Recently executed</h3>

      <div className="approvalList">
        {executedApprovals.length === 0 ? (
          <div className="empty">
            <Database />
            <p>No executed approvals yet.</p>
          </div>
        ) : (
          executedApprovals.slice(0, 10).map((approval) => (
            <article className="approval executed" key={approval.id}>
              <div>
                <strong className="mono">
                  {approval.action || approval.event?.action}
                </strong>
                <small>
                  {approval.resource || approval.event?.resource} · Risk {approval.risk ?? approval.risk_score ?? 0}
                </small>
                <p>Execution completed and retained in the runtime evidence trail.</p>
              </div>

              <span className="badge tone-success">
                <CheckCircle2 size={13} />
                Executed
              </span>
            </article>
          ))
        )}
      </div>
    </div>
  );
}

function Login({ onLogin }: { onLogin: (token: string) => void }) {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const path = mode === 'login' ? '/auth/login' : '/auth/register';
      const body =
        mode === 'login'
          ? { email, password }
          : { email, password, name };

      const response = await fetch(`${API}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || 'Authentication failed');
      }

      const data = await response.json();
      const nextToken = data.access_token || data.token;

      if (!nextToken) {
        throw new Error('Authentication response did not contain an access token.');
      }

      onLogin(nextToken);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth">
      <div className="authCard">
        <div className="logo">
          <ShieldCheck />
        </div>

        <span className="eyebrow">SENTINELOPS AI</span>
        <h1>Runtime Control Plane</h1>
        <p className="authSubtitle">
          Govern AI agent actions before they reach real-world tools.
        </p>

        {error && <div className="error">{error}</div>}

        <form onSubmit={submit}>
          {mode === 'register' && (
            <div className="field">
              <label>Name</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                required
              />
            </div>
          )}

          <div className="field">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>

          <div className="field">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <button className="primary" type="submit" disabled={loading}>
            {loading
              ? 'Please wait...'
              : mode === 'login'
                ? 'Sign in'
                : 'Create account'}
          </button>
        </form>

        <button
          className="link"
          onClick={() => {
            setMode(mode === 'login' ? 'register' : 'login');
            setError('');
          }}
        >
          {mode === 'login'
            ? 'Need an account? Register'
            : 'Already have an account? Sign in'}
        </button>
      </div>
    </div>
  );
}

React.createElement(React.StrictMode, null, null);

import { createRoot } from 'react-dom/client';

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);