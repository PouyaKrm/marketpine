class PaymentCreationFailedException(Exception):

    def __init__(self, status: int):
        self.returned_status = status


class PaymentVerificationFailedException(Exception):

    def __init__(self, status: int):
        self.returned_status = status


class PaymentAlreadyVerifiedException(Exception):
    pass


class PaymentOperationFailedException(Exception):

    def __init__(self, payment_type: str, original_exception):
        self.payment_type = payment_type
        self.original_exception = original_exception
