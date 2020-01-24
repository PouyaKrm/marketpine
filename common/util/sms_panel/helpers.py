def calculate_total_sms_cost(sent_messages: list):

    cost = 0
    for m in sent_messages:
        cost += m['cost']
    
    return cost
