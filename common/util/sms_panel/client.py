from users.models import Businessman
from django.conf import settings
import requests

from common.util.kavenegar_local import APIException

sms_settings = settings.SMS_PANEL
api_key = sms_settings['API_KEY']
min_credit = sms_settings['MIN_CREDIT']
init_credit = sms_settings['INIT_CREDIT']
pid = sms_settings['PID']
username_prefix = sms_settings['CUSTOMER_US_PREFIX']
customer_line = sms_settings['CUSTOMER_LINE']

class ClientManagement:

    """
    Handles user creation, update on kavenegar sms panel
    """

    def __init__(self):
        self.api_key = api_key


    def add(self, data: dict):

        resp = requests.post(f'http://api.kavenegar.com/v1/{self.api_key}/client/add.json', data)

        resp_data = resp.json()

        if resp.status_code != 200:
            raise APIException(resp.status_code, resp_data['return']['message'])

        return resp_data['entries']

    def fetch_by_local_id(self, local_id):

        """
        fetches users data by local id and return dictionary of response data
        :param local_id: id of the businessman in local database
        :return: dictionary of the response data
        """

        resp = requests.post(f'http://api.kavenegar.com/v1/{self.api_key}/client/fetchbylocalid.json', {'localid': local_id})

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

    def add_user(self, user: Businessman, password: str):

        from panelprofile.models import SMSPanelInfo

        """
        Provides simpler method to add a user to kavenegar.
        :param user: businessman
        :return: SMSPanelInfo that businessman property is not set to user and is not saved to database
        """

        data = {'username': username_prefix + user.username, 'password': password, 'localid': user.id,
                'mininumallowedcredit': min_credit, 'credit': init_credit,
                'fullname': user.first_name + " " + user.last_name, 'planid': pid,
                'mobile': user.phone, 'lines': customer_line, 'status': 0}

        result = self.add(data)

        info = SMSPanelInfo()
        info.api_key = result['apikey']
        info.status = '0'
        info.credit = result['remaincredit']
        info.sms_farsi_cost = result['smsfarsicost']
        info.sms_english_cost = result['smsenglishcost']
        info.username = result['username']

        return info

    def fetch_user(self, user):

        """
        providing simpler function to fetch user data from kavenegar
        :param user: Businessman object
        :return: SMSPanelInfo info that businessman property is not set and is not saved in database
        """

        from panelprofile.models import SMSPanelInfo
        result = self.fetch_by_local_id(user.id)

        info = SMSPanelInfo()
        info.api_key = result['apikey']
        info.status = '0'
        info.credit = result['remaincredit']
        info.sms_farsi_cost = result['smsfarsicost']
        info.sms_english_cost = result['smsenglishcost']
        info.username = result['username']

        return info

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


    def change_credit(self, amount: int, businessman_api_key: str, description: str):

        """
        This method increase or decrease amount of credit of businessman in kavenegar
        :param amount: To increase, use a positive number. To decrease, use a negative number
        :param businessman_api_key: api_key of the businessman we are going to change his credit
        :param description: description of this transaction that will be shown ti businessman in kavenegar panel
        :return: Status code of the request
        :raises APIException if transaction failed
        :raises ValueError if amount < 1000 or amount > -1000
        """

        if (amount > 0 and amount < 1000) or (amount < 0 and amount > -1000):
            raise ValueError("amount must be bigger that 1000 or smaller that -1000")

        data = {'Apikey': businessman_api_key, 'Credit': amount, 'Desc': description}
        resp = requests.post(f"http://api.kavenegar.com/v1/{api_key}/client/chargecredit.json", data)
        resp_data = resp.json()

        if resp.status_code != 200:
            raise APIException(resp_data.status_code, resp_data['return']['message'])
        return resp.status_code

    def fetch_credit_by_local_id(self, id: int):
        return self.fetch_by_local_id(id)['remaincredit']
