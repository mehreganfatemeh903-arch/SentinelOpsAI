from dataclasses import dataclass
import json
import urllib.error
import urllib.request

@dataclass
class AuthorizationResult:
    decision: str
    risk_score: int
    reasons: list[str]
    approval_required: bool
    event_id: str
    @property
    def allowed(self): return self.decision == 'allow'

@dataclass
class ExecutionResult(AuthorizationResult):
    executed: bool
    output: dict | None = None

class SentinelOpsError(RuntimeError): pass

class SentinelOpsClient:
    """Small dependency-free SDK for placing SentinelOps between an agent and its tools."""
    def __init__(self, base_url: str, api_key: str, timeout: float = 10.0):
        self.base_url=base_url.rstrip('/'); self.api_key=api_key; self.timeout=timeout
    def _post(self,path,body):
        req=urllib.request.Request(self.base_url+path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-Sentinel-Key':self.api_key},method='POST')
        try:
            with urllib.request.urlopen(req,timeout=self.timeout) as response: return json.loads(response.read().decode())
        except urllib.error.HTTPError as exc:
            detail=exc.read().decode(errors='replace')
            raise SentinelOpsError(f'SentinelOps HTTP {exc.code}: {detail}') from exc
        except urllib.error.URLError as exc:
            raise SentinelOpsError(f'SentinelOps unavailable: {exc.reason}') from exc
    def authorize(self, agent_id: str, action: str, resource: str, **kwargs) -> AuthorizationResult:
        return AuthorizationResult(**self._post('/api/v1/actions/agent-authorize',{'agent_id':agent_id,'action':action,'resource':resource,**kwargs}))
    def check_and_raise(self,*args,**kwargs):
        result=self.authorize(*args,**kwargs)
        if not result.allowed: raise PermissionError(f'SentinelOps decision={result.decision}: {"; ".join(result.reasons)}')
        return result
    def execute(self,agent_id: str,action: str,resource: str,**kwargs)->ExecutionResult:
        return ExecutionResult(**self._post('/api/v1/actions/execute',{'agent_id':agent_id,'action':action,'resource':resource,**kwargs}))
