from base_app.error_codes import ApplicationErrorCodes


class BaseService:

    def throw_exception(self, error_code: dict, field_name: str = None, original_exception: Exception = None):
        if field_name is None:
            raise ApplicationErrorCodes.get_exception(error_code, original_exception)
        else:
            raise ApplicationErrorCodes.get_field_error(field_name, error_code, original_exception)

    def throw_field_exception(self, field_name: str, error_code: dict, original_exception: Exception = None):
        raise ApplicationErrorCodes.get_field_error(field_name, error_code, original_exception)


def throw_exception(*args, error_code: dict, field_name: str = None, original_exception: Exception = None):
    if field_name is None:
        raise ApplicationErrorCodes.get_exception(error_code, original_exception)
    else:
        raise ApplicationErrorCodes.get_field_error(field_name, error_code, original_exception)


def throw_field_exception(self, field_name: str, error_code: dict, original_exception: Exception = None):
    raise ApplicationErrorCodes.get_field_error(field_name, error_code, original_exception)
