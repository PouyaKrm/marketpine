from common.util.sms_panel.message import BaseSMSMessage, customer_line


class ClientSMSMessage(BaseSMSMessage):

    def __init__(self, api_key: str):

        super().__init__(api_key, customer_line)

    def send_plain(self, phones: list, message: str, local_ids: list = None):

        receptors = ''

        # for phone in phones:
        #     receptors += phone + ', '
        receptors = ','.join(phones)

        if local_ids is not None:
            # for message_id in local_ids:
            #     ids += str(message_id) + ','
            ids = ','.join(str(message_id) for message_id in local_ids)
            return self.send_message(receptors, message, ids)
        return self.send_message(receptors, message)

    def send_array(self, phones: list, messages: list):

        if len(messages) != len(phones):
            raise ValueError('phones and messages lists length must be equal')
        sender = []
        for _ in range(len(phones)):
            sender.append(customer_line)

        params = {'sender': f'{sender}', 'receptor': f'{phones}', 'message': f'{messages}'}
        return self._api.sms_sendarray(params)
