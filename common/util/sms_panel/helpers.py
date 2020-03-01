def calculate_total_sms_cost(sent_messages: list):

    cost = 0
    for m in sent_messages:
        cost += m['cost']
    
    return cost


def message_id_receptor_cost_sms(result: list) -> list:
    data = []
    for r in result:
        data.append({'message_id': str(r['messageid']), 'receptor': r['receptor'], 'cost': r['cost']})

    # return [{'message_id': str(r['messageid']), 'receptor': r['receptor']} for r in result]
    return data
