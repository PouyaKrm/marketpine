def calculate_total_sms_cost(sent_messages: list):

    cost = 0
    for m in sent_messages:
        cost += m['cost']
    
    return cost


def message_id_and_receptor_from_sms_result(result: list) -> list:
    data = []
    for r in result:
        data.append({'message_id': str(r['messageid']), 'receptor': r['receptor']})

    # return [{'message_id': str(r['messageid']), 'receptor': r['receptor']} for r in result]
    return data
