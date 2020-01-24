class PaymentCreationFailedException(Exception):

    def __init__(self, status: int):
        self.returned_status = status


class PaymentVerificationFailedException(Exception):

    def __init__(self, status: int):
        self.returned_status = status
