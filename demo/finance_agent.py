"""End-to-end Finance Agent demo: every consequential action passes SentinelOps first."""
import os
from sdk.sentinelops import SentinelOpsClient, SentinelOpsError
BASE_URL=os.getenv('SENTINELOPS_URL','http://localhost:8000')
AGENT_ID=os.environ['SENTINEL_AGENT_ID']; API_KEY=os.environ['SENTINEL_AGENT_KEY']
client=SentinelOpsClient(BASE_URL,API_KEY)

def refund(order_id:str,amount:float):
    try:
        result=client.execute(AGENT_ID,'create_refund',f'customer:4821/order:{order_id}',tool_id=os.getenv('SENTINEL_TOOL_ID'),sensitivity=55,financial_amount=amount,external_destination=False,session_actions=['read_customer','read_financial'],context={'reason':'customer requested refund','currency':'EUR'})
    except SentinelOpsError as exc:
        print(exc); return
    print(f'decision={result.decision} risk={result.risk_score} approval={result.approval_required} executed={result.executed}')
    for reason in result.reasons: print('-',reason)
    if result.executed: print('Gateway output:',result.output)

if __name__=='__main__': refund('ORD-9021',250)
