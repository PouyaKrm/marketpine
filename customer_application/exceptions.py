from customer_application.error_codes import CustomerAppErrors


class CustomerServiceException(Exception):

    def __init__(self, http_message):
        self.http_message = http_message

    @staticmethod
    def for_customer_by_phone_does_not_exist():
        raise CustomerServiceException(CustomerAppErrors.error_dict(CustomerAppErrors.CODE_PHONE_DOES_NOT_EXIST))

    @staticmethod
    def for_password_send_failed():
        raise CustomerServiceException(CustomerAppErrors.error_dict(CustomerAppErrors.PASSWORD_SEND_FAILED))

    @staticmethod
    def for_invalid_password():
        raise CustomerServiceException(CustomerAppErrors.error_dict(CustomerAppErrors.INVALID_PASSWORD))

    @staticmethod
    def for_one_time_password_already_sent():
        raise CustomerServiceException(CustomerAppErrors.error_dict(CustomerAppErrors.ONE_TIME_PASSWORD_ALREADY_SENT))

    @staticmethod
    def for_login_token_does_not_exist():
        raise CustomerServiceException(CustomerAppErrors.error_dict(CustomerAppErrors.LOGIN_TOKEN_DOES_NOT_EXIST))

    @staticmethod
    def for_businessman_not_found():
        raise CustomerServiceException(CustomerAppErrors.error_dict(CustomerAppErrors.BUSINESSMAN_NOT_FOUND))