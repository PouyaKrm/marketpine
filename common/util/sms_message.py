
from kavenegar import KavenegarAPI, APIException, HTTPException


class SMSMessage:

    key = '4D4C324E43416D726C65446D7258566A4F59697153444355734E4F4D6B382B57'
    api = KavenegarAPI(key)

    def send(self, **params):

        try:

            return self.api.sms_send(params)
        except APIException as e:
            return e
        except HTTPException as e:
            return e



    def send_message(self, receptor, message, sender=''):

        params = {
            'sender': f'{sender}',
            'receptor': f'{receptor}',
            'message': f'{message}'
        }

        # try:

        return self.api.sms_send(params)
        # except APIException as e:
        #     return e
        # except HTTPException as e:
        #     return e


    def send_verification_code(self, receptor, code, sender=''):

        return self.send_message(receptor, message=f'your verification code is: {code}')

    def send_new_password(self, receptor, new_password):

        return self.send_message(receptor, f'your new password is:\n{new_password}')