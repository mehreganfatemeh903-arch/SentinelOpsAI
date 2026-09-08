from app.models import Decision, Policy
from app.schemas.action import ActionRequest

def matches(pattern:str, action:str)->bool:
    return pattern=='*' or pattern==action or (pattern.endswith('*') and action.startswith(pattern[:-1]))

def evaluate_policies(request:ActionRequest, risk_score:int, policies:list[Policy]):
    reasons=[]; approval=False; decision=Decision.ALLOW
    for p in policies:
        if not p.enabled or not matches(p.action_pattern,request.action): continue
        if risk_score < p.min_risk: continue
        if p.max_financial_amount is not None and request.financial_amount>p.max_financial_amount: continue
        reasons.append(f'Policy matched: {p.name} v{p.version}')
        if p.effect==Decision.BLOCK: return Decision.BLOCK,False,reasons
        if p.require_approval or p.effect==Decision.APPROVAL: approval=True; decision=Decision.APPROVAL
    if risk_score>=90: return Decision.BLOCK,False,reasons+['Critical runtime risk threshold reached']
    if risk_score>=70 and decision==Decision.ALLOW: return Decision.APPROVAL,True,reasons+['High runtime risk requires human approval']
    return decision,approval,reasons
