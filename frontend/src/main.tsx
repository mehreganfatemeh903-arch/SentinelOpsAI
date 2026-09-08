import React,{useEffect,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {ShieldCheck,Bot,AlertTriangle,Activity,LockKeyhole,CheckCircle2,XCircle,RefreshCw,KeyRound,Clock3} from 'lucide-react';
import './styles.css';
const API=import.meta.env.VITE_API_BASE_URL||'http://localhost:8000/api/v1';
type Event={
 id:string;
 action:string;
 resource:string;
 decision:string;
 risk_score:number;
 created_at:string;
 reasons:string[];
};
type Agent={
 id:string;
 name:string;
 owner:string;
 autonomy_level:string;
 active:boolean;
 description?:string;
};
function App(){
 const [token,setToken]=useState(localStorage.getItem('sentinel_token')||'');
 const [agents,setAgents]=useState<Agent[]>([]);
 const [events,setEvents]=useState<Event[]>([]);
 const [alerts,setAlerts]=useState<Event[]>([]);
 const [approvals,setApprovals]=useState<any[]>([]);
 const [tab,setTab]=useState('overview');
 const [error,setError]=useState('');
 async function load(){
  if(!token)return;
  const h={Authorization:`Bearer ${token}`};
  try{
   const payload=JSON.parse(atob(token.split('.')[1]));
   const role=payload.role||'viewer';
   const [a,e,s]=await Promise.all([
    fetch(`${API}/agents`,{headers:h}),
    fetch(`${API}/events?limit=50`,{headers:h}),
    fetch(`${API}/alerts?limit=20`,{headers:h})
   ]);
   if(!a.ok||!e.ok||!s.ok)throw Error('API access failed');
   setAgents(await a.json());
   setEvents(await e.json());
   setAlerts(await s.json());
   if(role==='admin'||role==='operator'){
    const p=await fetch(`${API}/approvals`,{headers:h});
    if(!p.ok)throw Error('Approval API access failed');
    setApprovals(await p.json());
   }else{
    setApprovals([]);
    if(tab==='approvals'){
     setTab('overview');
    }
   }
   setError('');
  }catch(e:any){
   setError(e.message);
  }
 }
 useEffect(()=>{load()},[token]);
 if(!token)
  return <Login onLogin={t=>{
   localStorage.setItem('sentinel_token',t);
   setToken(t);
  }}/>;
 const payload=JSON.parse(atob(token.split('.')[1]));
 const role=payload.role||'viewer';
 const canManageApprovals=role==='admin'||role==='operator';
 const blocked=events.filter(e=>e.decision==='block').length;
 const approvalEvents=events.filter(e=>e.decision==='approval').length;
 const allowed=events.filter(e=>e.decision==='allow').length;
 return <main className="shell">
  <header>
   <div>
    <span className="eyebrow">SENTINELOPS AI · RUNTIME CONTROL PLANE</span>
    <h1>Control what AI agents actually do.</h1>
    <p>Identity, policy, contextual risk, human approval and evidence—inline with every consequential action.</p>
   </div>
   <button className="ghost" onClick={load}>
    <RefreshCw size={16}/> Refresh
   </button>
  </header>
  <nav className="tabs">
   <button
    className={tab==='overview'?'active':''}
    onClick={()=>setTab('overview')}
   >
    Overview
   </button>
   <button
    className={tab==='agents'?'active':''}
    onClick={()=>setTab('agents')}
   >
    Agents
   </button>
   <button
    className={tab==='security'?'active':''}
    onClick={()=>setTab('security')}
   >
    Security <span>{alerts.length}</span>
   </button>
   {canManageApprovals&&
    <button
     className={tab==='approvals'?'active':''}
     onClick={()=>setTab('approvals')}
    >
     Approvals <span>{approvals.length}</span>
    </button>
   }
   <button
    className="logout"
    onClick={()=>{
     localStorage.removeItem('sentinel_token');
     setToken('');
     setTab('overview');
    }}
   >
    Sign out
   </button>
  </nav>
  {error&&<div className="error">{error}</div>}
  {tab==='overview'&&
   <>
    <section className="grid">
     <Card
      icon={<Bot/>}
      title="Agents"
      value={agents.length}
      text="Registered identities"
     />
     <Card
      icon={<CheckCircle2/>}
      title="Allowed"
      value={allowed}
      text="Recent actions"
     />
     <Card
      icon={<LockKeyhole/>}
      title="Approval"
      value={approvals.length}
      text="Awaiting / escalated"
     />
     <Card
      icon={<AlertTriangle/>}
      title="Blocked"
      value={blocked}
      text="Denied actions"
     />
    </section>
    <section className="two">
     <Panel title="Runtime Activity">
      <div className="events">
       {events.length===0
        ?<Empty/>
        :events.map(e=><EventRow key={e.id} e={e}/>)
       }
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
       <ShieldCheck/>
       <div>
        <strong>Trajectory-aware decisions</strong>
        <p>
         SentinelOps evaluates the current action together with recent session actions,
         data sensitivity, financial value, destination and autonomy.
        </p>
       </div>
      </div>
     </Panel>
    </section>
   </>
  }
  {tab==='agents'&&
   <section className="panel">
    <div className="panelHead">
     <div>
      <h2>Agent Registry</h2>
      <span>Non-human identities and autonomy posture</span>
     </div>
     <span>{agents.length} registered</span>
    </div>
    <div className="agentGrid">
     {agents.map(a=>
      <article className="agent" key={a.id}>
       <div className="agentIcon"><Bot/></div>
       <div>
        <h3>{a.name}</h3>
        <p>{a.description||'Runtime-controlled AI agent'}</p>
        <div className="badges">
         <span>{a.autonomy_level}</span>
         <span className={a.active?'ok':'danger'}>
          {a.active?'ACTIVE':'SUSPENDED'}
         </span>
        </div>
       </div>
      </article>
     )}
    </div>
    {agents.length===0&&<Empty/>}
   </section>
  }
  {tab==='security'&&
   <section className="panel">
    <div className="panelHead">
     <div>
      <h2>Security Alerts</h2>
      <span>Runtime decisions classified as security events</span>
     </div>
     <span>{alerts.length} recent</span>
    </div>
    {alerts.length===0
     ?<Empty/>
     :<div className="events">
       {alerts.map(e=>
        <EventRow key={e.id} e={e} security/>
       )}
      </div>
    }
   </section>
  }
  {tab==='approvals'&&canManageApprovals&&
   <ApprovalPanel
    approvals={approvals}
    reload={load}
    token={token}
    setError={setError}
   />
  }
  <footer>
   <KeyRound/>
   Agent API keys are scoped to one agent and are intended for runtime traffic—not dashboard login.
  </footer>
 </main>
}
function ApprovalPanel({
 approvals,
 reload,
 token,
 setError
}:{
 approvals:any[];
 reload:()=>void;
 token:string;
 setError:(message:string)=>void
}){
 async function decide(id:string,approve:boolean){
  const r=await fetch(
   `${API}/approvals/${id}/decision?approve=${approve}`,
   {
    method:'POST',
    headers:{Authorization:`Bearer ${token}`}
   }
  );
  if(!r.ok){
   setError('Approval action failed');
   return;
  }
  reload();
 }
 return <section className="panel">
  <div className="panelHead">
   <div>
    <h2>Human Approval Queue</h2>
    <span>Consequential actions paused before execution</span>
   </div>
   <span>{approvals.length} pending</span>
  </div>
  {approvals.length===0
   ?<Empty/>
   :<div className="approvalList">
     {approvals.map(a=>
      <article className="approval" key={a.id}>
       <div>
        <strong>{a.action}</strong>
        <small>
         {a.resource} · risk {a.risk_score}/100
        </small>
        <p>
         {(a.reasons||[]).join(' · ')}
        </p>
       </div>
       <div className="approvalActions">
        <button onClick={()=>decide(a.id,true)}>
         Approve
        </button>
        <button onClick={()=>decide(a.id,false)}>
         Reject
        </button>
       </div>
      </article>
     )}
    </div>
  }
 </section>
}
function EventRow({
 e,
 security=false
}:{
 e:Event;
 security?:boolean
}){
 return <div className="event">
  <div className={`decision ${e.decision}`}>
   {e.decision==='allow'
    ?<CheckCircle2/>
    :e.decision==='block'
     ?<XCircle/>
     :<Clock3/>
   }
  </div>
  <div>
   <strong>{e.action}</strong>
   <small>
    {e.resource} · risk {e.risk_score}/100 {security?'· security':''}
   </small>
  </div>
  <b>{e.decision.toUpperCase()}</b>
 </div>
}
function Card(p:any){
 return <article className="card">
  {p.icon}
  <strong>{p.title}</strong>
  <b>{p.value}</b>
  <small>{p.text}</small>
 </article>
}
function Panel({
 title,
 children
}:{
 title:string;
 children:any
}){
 return <div className="panel">
  <h2>{title}</h2>
  {children}
 </div>
}
function Empty(){
 return <div className="empty">
  <Activity/>
  <p>
   No runtime events yet. Connect the Finance Agent SDK to create the first decision.
  </p>
 </div>
}
function Login({onLogin}:{onLogin:(t:string)=>void}){
 const [email,setEmail]=useState('');
 const [password,setPassword]=useState('');
 const [mode,setMode]=useState<'login'|'register'>('login');
 const [name,setName]=useState('');
 const [error,setError]=useState('');
 const [loading,setLoading]=useState(false);
 async function submit(e:any){
  e.preventDefault();
  setError('');
  if(mode==='register'&&!name.trim()){
   setError('Please enter your full name.');
   return;
  }
  if(!email.trim()||!password){
   setError('Please enter your email and password.');
   return;
  }
  setLoading(true);
  try{
   const path=mode==='login'?'login':'register';
   const body=mode==='login'
    ?{email,password}
    :{email,password,name:name.trim()};
   const url=API+'/auth/'+path;
   const r=await fetch(url,{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(body)
   });
   const d=await r.json().catch(()=>({}));
   if(!r.ok){
    const detail=Array.isArray(d.detail)
     ?d.detail.map((x:any)=>x.msg).join(', ')
     :d.detail;
    setError(detail||'Request failed.');
    return;
   }
   if(!d.access_token){
    setError('Authentication succeeded but no access token was returned.');
    return;
   }
   onLogin(d.access_token);
  }catch(err:any){
   setError(
    err?.message||
    'Unable to connect to the SentinelOps AI API.'
   );
  }finally{
   setLoading(false);
  }
 }
 function switchMode(){
  setError('');
  setMode(mode==='login'?'register':'login');
 }
 return <main className='auth'>
  <form onSubmit={submit} className='authCard'>
   <div className='logo'>
    <ShieldCheck/>
   </div>
   <span className='eyebrow'>SENTINELOPS AI</span>
   <h1>
    {mode==='login'
     ?'Secure control plane'
     :'Create workspace owner'
    }
   </h1>
   <p className='authSubtitle'>
    {mode==='login'
     ?'Sign in to manage your AI runtime control plane.'
     :'Create the first administrator account for this workspace.'
    }
   </p>
   {mode==='register'&&
    <div className='field'>
     <label htmlFor='name'>Full name</label>
     <input
      id='name'
      value={name}
      onChange={e=>setName(e.target.value)}
      placeholder='Your full name'
      autoComplete='name'
     />
    </div>
   }
   <div className='field'>
    <label htmlFor='email'>Email</label>
    <input
     id='email'
     value={email}
     onChange={e=>setEmail(e.target.value)}
     placeholder='you@example.com'
     type='email'
     autoComplete='email'
    />
   </div>
   <div className='field'>
    <label htmlFor='password'>Password</label>
    <input
     id='password'
     value={password}
     onChange={e=>setPassword(e.target.value)}
     placeholder='Enter your password'
     type='password'
     autoComplete={
      mode==='login'
       ?'current-password'
       :'new-password'
     }
    />
   </div>
   {error&&
    <div className='error' role='alert'>
     {error}
    </div>
   }
   <button
    type='submit'
    className='primary'
    disabled={loading}
   >
    {loading
     ?'Please wait...'
     :mode==='login'
      ?'Sign in'
      :'Create account'
    }
   </button>
   <button
    type='button'
    className='link'
    onClick={switchMode}
    disabled={loading}
   >
    {mode==='login'
     ?'Create the first workspace account'
     :'Back to sign in'
    }
   </button>
  </form>
 </main>
}
createRoot(document.getElementById('root')!).render(
 <React.StrictMode>
  <App/>
 </React.StrictMode>
);
