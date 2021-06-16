from base_app.error_codes import ApplicationErrorException


class CustomerServiceException(ApplicationErrorException):

    def __init__(self, http_message, original_exception: Exception = None):
        super().__init__(http_message, original_exception)
