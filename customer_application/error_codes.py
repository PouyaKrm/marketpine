class CustomerAppErrors:

    CODE_PHONE_DOES_NOT_EXIST = '0'
    PASSWORD_SEND_FAILED = '1'
    INVALID_PASSWORD = '2'
    ONE_TIME_PASSWORD_ALREADY_SENT = '3'
    LOGIN_TOKEN_DOES_NOT_EXIST = '4'
    BUSINESSMAN_NOT_FOUND = '5'
    FRIEND_ALREADY_INVITED = '6'
    FRIEND_INVITATION_DISABLED = '7'
    USER_SHOULD_LOGIN = '8'
    PHONE_NUMBER_ALREADY_TAKEN = '9'
    FULL_NAME_MUST_BE_SET = '10'
    RECORD_NOT_FOUND = '11'

    @staticmethod
    def error_dict(code, error: dict = None):
        return {'code': code, 'errors': error}
