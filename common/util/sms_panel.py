import requests

from users.models import Businessman
from .kavenegar_local import KavenegarAPI, APIException, HTTPException
from django.conf import settings

class SMSMessage:

    key = settings.SMS_API_KEY
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

    def send_friend_invitation_welcome_message(self, business_name: str, invited_phone: str, discount_code: str,
                                               bot_link: str = None):

        if bot_link is None:
            message = f'مشتری عزیز شما به {business_name} دعوت شدید. با استفاده از کد تخفیف {discount_code} در اولین خرید از تخفیف بهرمند شوید'

        else:
            message = f'مشتری عزیز شما به {business_name} دعوت شدید. با استفاده از کد تخفیف {discount_code} در اولین خرید از تخفیف بهرمند شوید. با استفاده از لینک زیر در بات تلگرام ما عضو شوید. {bot_link}'

        return self.send_message(invited_phone, message)




class FestivalMessageBulk(SMSMessage):

    def __init__(self, receptors: list, messages: list, senders=None):

        """
        Note: length of message list and receptors list and senders must be equal
        :raises ValueError: If length of receptors list and messages list are not equal, this exception will be raised
        :param receptors: list of string phone numbers
        :param messages: list of string messages
        :param senders:  list of senders phone number. if this value is nit provided default phone numbers will be used
        """

        if len(receptors) != len(messages):
            raise ValueError('messages length and receptors length must be same in bulk messages')

        self.receptors = receptors
        self.messages = messages
        self.senders = senders
        self.start = 0
        self.end = 0


    def give_message_params(self):

        """
        Provides SMS message parameters in order that is specified by kavehnegar api.
        :return: Dictionary that contains 'sender', 'receptor' and 'message' keys and values
        """

        if self.start == len(self.receptors):
            return None

        recep_len = len(self.receptors[self.start:])
        sender_len = len(self.senders)

        if sender_len > recep_len:
            params = {"sender": f"{self.senders[:recep_len]}", "receptor": f"{self.receptors[self.start:]}",
                      "message": f"{self.messages[self.start:]}"}
            self.start += recep_len
            self.end = self.start

        else:
            self.end += sender_len
            params = {"sender": f"{self.senders}", "receptor": f"{self.receptors[self.start:self.end]}",
                      "message": f"{self.messages[self.start:self.end]}"}

            self.start = self.end

        return params

    def send_bulk(self):

        """
        sends bulk messages means that many messages to many receptors.
        this function is specific for sending multiple messages
        of those senders must be represented as a list other wise it will be sent by default phone number
        :return:
        """

        if self.senders is None:
            self.senders = ['0013658000175', '10004346', '30004681', '2000004346']
        params = self.give_message_params()

        while params is not None:

            self.api.sms_sendarray(params)
            params = self.give_message_params()


class ClientManagement:

    def __init__(self):
        self.api_key = settings.SMS_API_KEY

    def add(self, data: dict):

        resp = requests.post(f'http://api.kavenegar.com/v1/{self.api_key}/client/add.json', data)

        resp_data = resp.json()

        if resp.status_code != 200:
            raise APIException(resp.status_code, resp_data['return']['message'])

        return resp_data['entries']


    def update(self, businessman_api_key, data: dict):

        """
        updates client info on kavenegar
        :param businessman_api_key: api key of client
        :param data: data that needs to be updated
        :raises APIException if kavenegar api  send error response
        :return:
        """
        resp = requests.post(f'http://api.kavenegar.com/v1/{self.api_key}/client/update.json',
                             {'apikey': businessman_api_key,
                              **data})
        resp_data = resp.json()
        if resp.status_code != 200:
            raise APIException(resp.status_code, resp_data['return']['message'])

        return resp.status_code

    def activate_sms_panel(self, businessman_api_key):
        """
        activates sms panel of the client om kavenegar
        :param businessman_api_key: api key of the client
        :return: result of update method
        """
        return self.update(businessman_api_key, {'status': '1'})

    def deactivate_sms_panel(self, businessman_api_key):
        """
        deactivates sms panel of the client on kavenegar
        :param businessman_api_key: api key of the client
        :return: result of update method
        """
        return self.update(businessman_api_key, {'status': '0'})
