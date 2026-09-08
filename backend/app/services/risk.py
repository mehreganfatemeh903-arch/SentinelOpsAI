from app.schemas.action import ActionRequest

def calculate_risk(request:ActionRequest, autonomy_level:str='assist'):
    score=0; reasons=[]
    if request.sensitivity>=70: score+=30; reasons.append('Sensitive data access')
    elif request.sensitivity>=40: score+=15; reasons.append('Moderate data sensitivity')
    if request.financial_amount>=1000: score+=35; reasons.append('High-value financial action')
    elif request.financial_amount>0: score+=15; reasons.append('Financial action')
    if request.external_destination: score+=20; reasons.append('External destination')
    if len(request.session_actions)>=3: score+=15; reasons.append('Complex action trajectory')
    if autonomy_level in {'autonomous','critical'}: score+=10; reasons.append('High autonomy level')
    # Sequence-aware rule: individually plausible actions can become risky together.
    seq=set(request.session_actions+[request.action])
    if {'read_customer','read_financial','create_refund'}.issubset(seq): score+=20; reasons.append('Financial trajectory combines customer, financial and refund actions')
    if {'read_sensitive','export_data'}.issubset(seq) and request.external_destination: score+=25; reasons.append('Sensitive-data export trajectory')
    return min(score,100), reasons
