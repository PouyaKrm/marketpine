class CustomerAppErrors:

    CODE_PHONE_DOES_NOT_EXIST = '0'
    PASSWORD_SEND_FAILED = '1'

    @staticmethod
    def error_dict(code, error: dict = None):
        return {'code': code, 'errors': error}
