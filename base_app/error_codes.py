class ApplicationErrorException(Exception):

    def __init__(self, error_code: dict, original_exception: Exception = None):
        self.http_message = error_code
        self.originalException = original_exception


class ApplicationErrorCodes:

    @staticmethod
    def _get_code_message_dict(code: int, message: str) -> dict:
        return {'code': code.__str__(), 'message': message}

    RECORD_NOT_FOUND = {'code': '900', 'message': 'رکورد موردنظر پیدا نشد'}
    NOT_ENOUGH_SMS_CREDIT = {'code': '1000', 'message': 'اعتبار کافی برای ارسال پیامک ندارید'}
    VERIFICATION_CODE_SEND_ERROR = {'code': '1001', 'message': 'خطا در ارسال کد احراز هویت'}
    VERIFICATION_DOES_NOT_EXIST_OR_EXPIRED = {'code': '1002', 'message': 'کد وجود ندارد یا منقضی شده'}
    VERIFICATION_CODE_ALREADY_SENT = {'code': '1003', 'message': 'کد تایید قبلا ارسال شده'}
    PHONE_NUMBER_IS_NOT_UNIQUE = {'code': '1004', 'message': 'شماره تلفن یکتا نیست'}
    BUSINESSMAN_HAS_NO_SMS_PANEL = _get_code_message_dict.__func__(1005, 'پنل پیامکی برای کاربر ثبت نشده')
    KAVENEGAR_CLIENT_MANAGEMENT_ERROR = _get_code_message_dict.__func__(1006, 'خطای مدیریت مشتری از سوی کاونگار')
    BUSINESSMAN_HAS_NO_AUTH_DOCS = _get_code_message_dict.__func__(1007, 'کاربر هیچ مدارک احراز هویتی در سیستم ندارد')

    @staticmethod
    def get_exception(code: dict, original_exception: Exception = None) -> ApplicationErrorException:
        return ApplicationErrorException(code, original_exception)
