import requests

from users.models import Businessman

from common.util.kavenegar_local import KavenegarAPI, APIException, HTTPException
from common.util.sms_panel.exceptions import SendSMSException
from common.util.custom_templates import render_template_with_customer_data

from django.conf import settings
from django.db.models import QuerySet
from django.template import Template

sms_settings = settings.SMS_PANEL
api_key = sms_settings['API_KEY']
system_line = sms_settings['SYSTEM_LINE']
verification_template_name = sms_settings['VERIFICATION_TEMPLATE_NAME']
new_password_forget_template_name = sms_settings['BUSINESSMAN_NEW_PASSWORD_FORGET_TEMPLATE_NAME']
one_time_password_template_name = sms_settings['CUSTOMER_ONE_TIME_PASSWORD_TEMPLATE_NAME']
phone_change_template_name = sms_settings['CUSTOMER_PHONE_CHANGE_TEMPLATE_NAME']
min_credit = sms_settings['MIN_CREDIT']
init_credit = sms_settings['INIT_CREDIT']
pid = sms_settings['PID']
username_prefix = sms_settings['CUSTOMER_US_PREFIX']
customer_line = sms_settings['CUSTOMER_LINE']
send_plain_page_size = sms_settings['SEND_PLAIN_CUSTOMERS_PAGE_SIZE']
send_template_page_size = sms_settings['SEND_TEMPLATE_PAGE_SIZE']
admin_phone = settings.ADMIN_PHONE


class BaseSMSMessage():

    def __init__(self, api_key: str, line: str):
        self._api = KavenegarAPI(api_key)
        self._line = line

    def send(self, **params):
        return self._api.sms_send(params)

    def send_message(self, receptor, message, local_ids=None):
        params = {
            'sender': self._line,
            'receptor': f'{receptor}',
            'message': f'{message}'
        }

        if local_ids is not None:
            params['localid'] = local_ids

        return self._api.sms_send(params)


class SystemSMSMessage(BaseSMSMessage):

    def __init__(self):
        super().__init__(api_key, system_line)

    def send_verification_code(self, receptor, code, sender=''):
        return self._api.verify_lookup({'receptor': receptor, 'token': code, 'template': verification_template_name})

    def send_new_password(self, receptor, new_password):
        return self._api.verify_lookup({
            'receptor': receptor,
            'token': new_password,
            'template': new_password_forget_template_name
        })

    def send_customer_one_time_password(self, receptor, code):
        return self._api.verify_lookup(
            {'receptor': receptor, 'token': code, 'template': one_time_password_template_name})

    def send_customer_phone_change_code(self, receptor: str, code: str):
        return self._api.verify_lookup({'receptor': receptor, 'token': code, 'template': phone_change_template_name})

    def send_admin_low_system_credit_message(self):
        return self.send_message(admin_phone, 'اعتبار پنل پیامک سیستم مشترینو کم است و تعدادی از مشتریان موفق به شارژ پنل نشده اند')


system_sms_message = SystemSMSMessage()


class ClientSMSMessage(BaseSMSMessage):
    """
    sends one same message to specific number of customers
    """

    def __init__(self, sms_panel_info, customers: QuerySet, message: str):

        super().__init__(sms_panel_info.api_key, customer_line)
        self._customers = customers
        self._index = 0
        self._receptors_count = customers.count()
        self._remained_count = self._receptors_count
        self._message = message
        self._last_customer = self._customers.last()

    def _get_next_receptors(self):
        if self._remained_count == 0:
            return None

        phones = ""

        if self._remained_count <= send_plain_page_size:
            customers = self._customers.all()[self._index:]
            self._remained_count = 0
            self._index = self._receptors_count
            return customers

        customers = self._customers.all()[self._index: self._index + send_plain_page_size]

        self._index += send_plain_page_size

        self._remained_count -= send_plain_page_size

        return customers

    def send_plain_next(self):

        """
        A helper method to send message to customers.
        This mehtod uses a page size to send message to customers.
        Call this method until it returns None to send message to all customers.
        :customers retrived customers from database
        :returns list of details of sent message to each customer
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
            raise SendSMSException(e.status, e.message, current_customer, self._last_customer)

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

        super().__init__(businessman.smspanelinfo, businessman.customers.all(), message)

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


class ClientBulkToCustomerSMSMessage(ClientSMSMessage):
    """
    A class to send several different messages to different recievers.
    """

    def __init__(self, sms_panel_info, customers: QuerySet, template: str):
        super().__init__(sms_panel_info, customers, template)
        self._template = template
        self._receptors = customers
        self._receptors_num = self._receptors.count()
        self._remained_receptors = self._receptors_num
        self._senders_length = send_template_page_size
        self._last_customer = self._receptors.last()

        self._senders = []
        for _ in range(0, self._senders_length):
            self._senders.append(self._line)

        self._start = 0
        self._end = 0

    def _render_messages(self, customers: list):

        return [render_template_with_customer_data(self._template, c) for c in customers]

    def _get_phones(self, customers: list):

        return [c.phone for c in customers]

    def _get_next_message_params(self):

        """
        Generates message parameters that is needed for sms_sendarray method of
        kavenegar api, plus first receiver in the current queue.
        :return: None if the no receiver is remained,
        else, dictionary of data that is needed for sms_sendarray method and first receiver
        in the current queue
        """

        if self._remained_receptors <= 0:
            return None

        if self._senders_length >= self._remained_receptors:

            recievers = self._receptors.all()[self._start:]

            params = {"sender": f"{self._senders[:self._remained_receptors]}",
                      "receptor": f"{self._get_phones(recievers)}",
                      "message": f"{self._render_messages(recievers)}", 'first_reciever': recievers[0]}
            self._start += len(recievers)
            self._end = self._start

        else:

            self._end += self._senders_length
            recievers = self._receptors[:self._end]
            params = {"sender": f"{self._senders}", "receptor": f"{self._get_phones(recievers)}",
                      "message": f"{self._render_messages(recievers)}", 'first_reciever': recievers[0]}

            self._start = self._end

        self._remained_receptors -= len(recievers)

        return params

    def send_bulk(self):

        """
        The actual send in handled by this method. 
        to send to all recievers, this method must be called repeatedly until it returns None
        :return: List of sent messages that is retrived from kavenegar api if any receptor is remained.
        else, returns None
        :raise: SendSMSException if any error occur during sending message with resend_last parameter is set.
        """

        message_params = self._get_next_message_params()

        if message_params is None:
            return None

        first_receiver = message_params.pop('first_reciever')
        last_reciever = self._receptors.last()

        try:
            return self._api.sms_sendarray(message_params)
        except APIException as e:
            raise SendSMSException(e.status, e.message, first_receiver, self._last_customer)


class ClientBulkToAllToCustomerSMSMessage(ClientBulkToCustomerSMSMessage):
    """
    A class to send several different messages to different recievers.
    Use this class only when you want to send message to all customers of 
    a businessman
    """

    def __init__(self, businessman: Businessman, template: str):

        super().__init__(businessman.smspanelinfo, businessman.customers.all(), template)

    def send_bulk(self):

        """
        The actual send in handled by this method. 
        to send to all recievers this method must be called repeatedly until it returns None
        :return: List of sent messages that is retrived from kavenegar api, if any receptor is remained.
        else, returns None
        :raise: SendSMSException if any error occur during sending message with resend_last parameter set to None
        """

        message_parameters = self._get_next_message_params()

        if message_parameters is None:
            return None

        first_receiver = message_parameters.pop('first_reciever')

        try:
            return self._api.sms_sendarray(message_parameters)
        except APIException as e:
            raise SendSMSException(e.status, e.message, first_receiver)


def retrive_sent_messages(api_key: str, messageids: list):
    api = KavenegarAPI(api_key)

    param_value = ""

    for m in messageids:
        param_value += m + ","

    return api.sms_select({'messageid': param_value})


class ClientBulkTemplateSMSMessage(ClientSMSMessage):

    def __init__(self, sms_panel_info):

        """
        Note: length of message list and receptors list and senders must be equal
        :raises ValueError: If length of receptors list and messages list are not equal, this exception will be raised
        :param receptors: list of string phone numbers
        :param messages: list of string messages
        :param senders:  list of senders phone number. if this value is nit provided default phone numbers will be used
        """

        super().__init__(sms_panel_info)

        self._bulk_lines = customer_bulk_lines
        self._bulk_lines_num = len(self._bulk_lines)

        self._sender_string = ""

        for line in self._bulk_lines:
            self._sender_string += line + ","

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


class BulkMessageWithAdditionalContext(ClientBulkToAllToCustomerSMSMessage):

    def __init__(self, businessman, template, additional_context: dict):
        super().__init__(businessman, template)
        self.__additional_context = additional_context

    def _render_messages(self, customers: list):
        return [render_template_with_customer_data(self._template, c, **self.__additional_context) for c in customers]
