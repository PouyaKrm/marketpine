import requests

from users.models import Businessman

from common.util.kavenegar_local import KavenegarAPI, APIException, HTTPException
from common.util.sms_panel.exceptions import SendSMSException

from django.conf import settings
from django.db.models import QuerySet

sms_settings = settings.SMS_PANEL
api_key = sms_settings['API_KEY']
min_credit = sms_settings['MIN_CREDIT']
init_credit = sms_settings['INIT_CREDIT']
pid = sms_settings['PID']
username_prefix = sms_settings['CUSTOMER_US_PREFIX']
customer_line = sms_settings['CUSTOMER_LINE']
send_plain_all_page_num = sms_settings['SEND_PLAIN_ALL_CUSTOMERS_PAGE_NUMBER']

class SystemSMSMessage:

    def __init__(self):

        self.api = KavenegarAPI(api_key)
        self._line = sms_settings['SYSTEM_LINE']

    def send(self, **params):

        return self.api.sms_send(params)

    def send_message(self, receptor, message):

        params = {
            'sender': self._line,
            'receptor': f'{receptor}',
            'message': f'{message}'
        }

        return self.api.sms_send(params)


    def send_verification_code(self, receptor, code, sender=''):

        return self.send_message(receptor, message=f'your verification code is: {code}')

    def send_new_password(self, receptor, new_password):

        return self.send_message(receptor, f'your new password is:\n{new_password}')



class ClientSMSMessage(SystemSMSMessage):

    """
    sends one same message to specific number of customers
    """

    def __init__(self, sms_panel_info):

        super().__init__()

        self._api = KavenegarAPI(sms_panel_info.api_key)
        self._line = customer_line

    def send_message(self, receptor, message):

        """
        sends message by taking receptors as string that contains comma seperated phone numbers.
        :returns list of details of sent message to each receptor
        """

        params = {
            'sender': self._line,
            'receptor': receptor,
            'message': message
        }

        return self._api.sms_send(params)

    def send_plain(self, customers: QuerySet, message: str):

        """
        A helper method to send message to customers.
        :customers retrived customers from database
        :returns list of details of sent message to each customer
        """

        phones = ""

        for c in customers.all():
            phones += c.phone + ","

        try:
            return self.send_message(phones, message)
        
        except APIException as e:
            raise SendSMSException(e.status, e.message, customers.first(), customers.last())


    def send_verification_code(self, receptor, code, sender=''):
        pass

    def send_friend_invitation_welcome_message(self, business_name: str, invited_phone: str, discount_code: str,
                                               bot_link: str = None):

        if bot_link is None:
            message = f'مشتری عزیز شما به {business_name} دعوت شدید. با استفاده از کد تخفیف {discount_code} در اولین خرید از تخفیف بهرمند شوید'

        else:
            message = f'مشتری عزیز شما به {business_name} دعوت شدید. با استفاده از کد تخفیف {discount_code} در اولین خرید از تخفیف بهرمند شوید. با استفاده از لینک زیر در بات تلگرام ما عضو شوید. {bot_link}'

        return self.send_message(invited_phone, message)
        


class ClientToAllCustomersSMSMessage(ClientSMSMessage):

    """
    a helper class for sending one message to all custmers of a businessman
    """

    def __init__(self, businessman: Businessman, message: str):

        super().__init__(businessman.smspanelinfo)

        self._businessman = businessman
        self._index = 0
        self._receptors_count = businessman.customers.count()
        self._remained_count = self._receptors_count
        self._message = message


    def _get_next_receptors(self):

        """
        prepares phone numbers of customers based on "SEND_PLAIN_ALL_CUSTOMERS_PAGE_NUMBER"
        in sms panel settings.
        :returns string with number of "SEND_PLAIN_ALL_CUSTOMERS_PAGE_NUMBER" phone numbers.
        """
        
        if self._remained_count == 0:
            return None

        phones = ""
        
        if self._remained_count <= send_plain_all_page_num:
            # for c in self._businessman.customers.all()[self._index:]:
            #     phones += c.phone + ","
            customers = self._businessman.customers.all()[self._index:]
            self._remained_count = 0
            self._index = self._receptors_count
            return customers
        

        # for c in self._businessman.customers.all()[self._index : self._index + send_plain_all_page_num]:
        #     phones += c.phone + ","
        
        customers = self._businessman.customers.all()[self._index : self._index + send_plain_all_page_num]

        self._index += send_plain_all_page_num

        self._remained_count -= send_plain_all_page_num
      
        return customers


    def send_plain_next(self):

        """
        on each invoke, sends same message to specific number of customers.
        to send to all customers, this method must be invoke until it returns None
        :returns: List of data of sent messages that is recieved as response from kavenegar api
        """

        customers = self._get_next_receptors()

        if customers is None:
            return None

        current_customer = customers[0]

        phones = ""

        for c in customers:
            phones += c.phone + ","
        try:
            return self.send_message(phones, self._message)
        except APIException as e:
            raise SendSMSException(e.status, e.message, current_customer)
        


class FestivalMessageBulkSystem(SystemSMSMessage):

    def __init__(self, receptors: list, messages: list, senders=None):

        """
        Note: length of message list and receptors list and senders must be equal
        :raises ValueError: If length of receptors list and messages list are not equal, this exception will be raised
        :param receptors: list of string phone numbers
        :param messages: list of string messages
        :param senders:  list of senders phone number. if this value is nit provided default phone numbers will be used
        """

        super().__init__()
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


