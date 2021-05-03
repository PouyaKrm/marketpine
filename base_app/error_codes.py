class ApplicationErrorException(Exception):

    def __init__(self, error_code: dict):
        self.http_message = error_code


class ApplicationErrorCodes:

    RECORD_NOT_FOUND = {'code': '900', 'message': 'رکورد موردنظر پیدا نشد'}
    NOT_ENOUGH_SMS_CREDIT = {'code': '1000', 'message': 'اعتبار کافی برای ارسال پیامک ندارید'}
    VERIFICATION_CODE_SEND_ERROR = {'code': '1001', 'message': 'خطا در ارسال کد احراز هویت'}
    VERIFICATION_DOES_NOT_EXIST_OR_EXPIRED = {'code': '1001', 'message': 'کد وجود ندارد یا منقضی شده'}
    VERIFICATION_CODE_ALREADY_SENT = {'code': '1002', 'message': 'کد تایید قبلا ارسال شده'}
    PHONE_NUMBER_IS_NOT_UNIQUE = {'code': '1003', 'message': 'شماره تلفن یکتا نیست'}

    @staticmethod
    def get_exception(code: dict) -> ApplicationErrorException:
        return ApplicationErrorException(code)
