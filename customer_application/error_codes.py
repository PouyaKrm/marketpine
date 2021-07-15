class CustomerAppErrors:
    CODE_PHONE_DOES_NOT_EXIST = {'code': '0', 'message': 'کد یا شماره تلفن وجود ندارد'}
    PASSWORD_SEND_FAILED = {'code': '1', 'message': 'ارسال کد ورود با خطا مواجه شد'}
    INVALID_PASSWORD = {'code': '2', 'message': 'کلمه عبور اشتباه'}
    ONE_TIME_PASSWORD_ALREADY_SENT = {'code': '3', 'message': 'کد یکبار مصرف قبلا ارسال شده'}
    LOGIN_TOKEN_DOES_NOT_EXIST = {'code': '4', 'message': 'کلید ورود وجود ندارد'}
    BUSINESSMAN_NOT_FOUND = {'code': '5', 'message': 'فروشگاه وجود ندارد'}
    FRIEND_ALREADY_INVITED = {'code': '6', 'message': 'دوست قبلا معرفی شده'}
    FRIEND_INVITATION_DISABLED = {'code': '7', 'message': 'امکان معرفی دوست به این فروشگاه نیست'}
    USER_SHOULD_LOGIN = {'code': '8', 'message': 'کاربر باید وارد شود'}
    PHONE_NUMBER_ALREADY_TAKEN = {'code': '9', 'message': 'این شماره تلفن توسط فرد دیگری استفاده شده'}
    FULL_NAME_MUST_BE_SET = {'code': '10', 'message': 'نام باید ست شود'}
    RECORD_NOT_FOUND = {'code': '11', 'message': 'رکورد موردنظر پیدا نشد'}
    CAN_NOT_JOIN_BUSINESSMAN_THAT_DELETED_CUSTOMER_BEFORE = {'code': '12',
                                                             'message': 'امکان عضویت به فروشگاهی که قبلا شما را از لیست مشتریان خود حذف کرده نیست'}
    USER_NOT_JOINED_BUSINESSMAN = {'code': '13', 'message': 'عضو بیزینس من نیستید'}
    CAN_NOT_JOIN_BUSINESSMAN = {'code': '14', 'message': 'امکان عضویت به این بیزینس من نیست'}

    @staticmethod
    def error_dict(code, error: dict = None):
        return {'code': code, 'errors': error}
