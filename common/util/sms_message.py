
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

    def send_friend_invitation_welcome_message(self, business_name: str, invited_phone: str, discount_code: str,
                                               bot_link: str = None):

        if bot_link is None:
            message = f'مشتری عزیز شما به {business_name} دعوت شدید. با استفاده از کد تخفیف {discount_code} در اولین خرید از تخفیف بهرمند شوید'

        else:
            message = f'مشتری عزیز شما به {business_name} دعوت شدید. با استفاده از کد تخفیف {discount_code} در اولین خرید از تخفیف بهرمند شوید. با استفاده از لینک زیر در بات تلگرام ما عضو شوید. {bot_link}'

        return self.send_message(invited_phone, message)





class FestivalMessageBulk(SMSMessage):

    def __init__(self, receptors: list, messages: list, senders=None):

        self.receptors = receptors
        self.messages = messages
        self.senders = senders
        self.start=0
        self.end=0

    def validate_bulk_input(self):

        """
        :raise if length of receptors and messages are not equal ValueError exception will be raised
        :return:
        """

        if len(self.receptors) != len(self.messages):
            raise ValueError('messages length and receptors length must be same in bulk messages')



    def give_message_params(self):

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
        Note: length of message list and receptors list and senders must be equal
        :param receptors: list of phone numbers
        :param messages: list of messages
        :param sender: if messages are going to be sent by multiple sender's, phone number
        of those senders must be represented as a list other wise it will be sent by default phone number
        :return: status of the sent messages
        """

        self.validate_bulk_input()

        if self.senders is None:
            self.senders = ['0013658000175', '10004346', '30004681', '2000004346']
        params = self.give_message_params()
        length = len(self.senders)

        for i in range(0, len(self.receptors)):

            self.api.sms_sendarray(params)
            params = self.give_message_params()
            if params is None:
                break

