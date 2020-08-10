class CustomerAppErrors:

    CODE_PHONE_DOES_NOT_EXIST = '0'
    PASSWORD_SEND_FAILED = '1'
    INVALID_PASSWORD = '2'
    ONE_TIME_PASSWORD_ALREADY_SENT = '3'
    LOGIN_TOKEN_DOES_NOT_EXIST = '4'
    BUSINESSMAN_NOT_FOUND = '5'

    @staticmethod
    def error_dict(code, error: dict = None):
        return {'code': code, 'errors': error}
