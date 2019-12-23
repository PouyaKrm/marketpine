from common.util.kavenegar_local import APIException

from users.models import Customer

class SendSMSException(APIException):

    def __init__(self, status, message: str, failed_on: Customer, resend_last: Customer=None):

        super().__init__(status, message)

        self.failed_on = failed_on
        self.resend_last = resend_last
