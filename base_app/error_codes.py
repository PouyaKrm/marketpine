from typing import Union


class ApplicationErrorException(Exception):

    def __init__(self, error_code_message: Union[dict, str], original_exception: Exception = None):
        if type(error_code_message) == dict:
            self.http_message = error_code_message
        elif type(error_code_message) == str:
            self.http_message = {'message': error_code_message}
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
    INVALID_PASSWORD = _get_code_message_dict.__func__(1008, 'کلمه عبور اشتباه')
    CUSTOMER_ALREADY_ADDED = _get_code_message_dict.__func__(1009, 'مشتری قبلا اضافه شده')
    PAYMENT_CREATION_FAILED = _get_code_message_dict.__func__(1010, 'پرداخت با خظا مواجه شد')
    PAYMENT_ALREADY_VERIFIED = _get_code_message_dict.__func__(1011, 'پرداخت قبلا انجام شده')
    PAYMENT_WAS_NOT_SUCCESSFUL = _get_code_message_dict.__func__(1012, 'پرداخت موفقیت آمیز نبود')
    PAYMENT_VERIFICATION_FAILED = _get_code_message_dict.__func__(1013,
                                                                  'بررسی پرداخت با خطا مواجه شد با پشتیبانی تماس بگیرید')
    PAYMENT_INFORMATION_INCORRECT = _get_code_message_dict.__func__(2000, 'اطلاعات پرداخت اشتباه است')
    SMS_PANEL_INCREASE_DECREASE_CREDIT_FAILED = _get_code_message_dict.__func__(1014,
                                                                                'تغییر اعتبار پنل پیامک با خطا مواجه شد')

    USERNAME_IS_NOT_UNIQUE = _get_code_message_dict.__func__(1015, 'نام کاربری یکتا نیست')
    EMAIL_IS_NOT_UNIQUE = _get_code_message_dict.__func__(1016, 'ایمیل یکتا نیست')
    NOT_ENOUGH_WALLET_CREDIT = _get_code_message_dict.__func__(1017, 'اعتبار کیف پول کافی نیست')
    MINIMUM_WALLET_CREDIT_INCREASE = _get_code_message_dict.__func__(1018, 'مقدار افزایش اعتبار کم است')

    @staticmethod
    def get_exception(code: dict, original_exception: Exception = None) -> ApplicationErrorException:
        return ApplicationErrorException(code, original_exception)

    @staticmethod
    def get_field_error(field_name, error_code: dict,
                        original_exception: Exception = None) -> ApplicationErrorException:
        message = {field_name: error_code['message']}
        return ApplicationErrorException(message, original_exception)
