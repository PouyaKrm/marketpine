
from kavenegar import KavenegarAPI, APIException, HTTPException


class Message:

    key = '4D4C324E43416D726C65446D7258566A4F59697153444355734E4F4D6B382B57'
    api = KavenegarAPI(key)

    def send(self, **params):

        try:

            self.api.sms_send(params)
        except APIException as e:
            return e
        except HTTPException as e:
            return e

        return None

    def send_message(self, receptor, message, sender=''):

        params = {
            'sender': f'{sender}',
            'receptor': f'{receptor}',
            'message': f'{message}'
        }

        try:

            self.api.sms_send(params)
        except APIException as e:
            return e
        except HTTPException as e:
            return e

        return None

    def send_verification_code(self, receptor, code, sender=''):

        return self.send_message(receptor, message=f'your verification code is: {code}')
