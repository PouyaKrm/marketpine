class ApplicationErrorException(Exception):

    def __init__(self, error_code: dict):
        self.http_message = error_code


class ApplicationErrorCodes:

    NOT_ENOUGH_SMS_CREDIT = {'code': '1000', 'message': 'اعتبار کافی برای ارسال پیامک ندارید'}

    @staticmethod
    def get_exception(code: dict) -> ApplicationErrorException:
        return ApplicationErrorException(code)
