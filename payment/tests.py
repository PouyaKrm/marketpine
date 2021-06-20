from unittest.mock import patch, Mock

from base_app.error_codes import ApplicationErrorException
from base_app.tests import BaseTestClass
from payment.models import Payment
from payment.services import payment_service


# Create your tests here.


class PaymentServiceBaseTestClass(BaseTestClass):
    pass


class CreateSMSPanelCreditPaymentTest(PaymentServiceBaseTestClass):

    def setUp(self) -> None:
        super().setUp()
        self.mocked_request = Mock('Http Request')
        self.mocked_request.build_absolute_uri = Mock(return_value="fake url")

    @patch("payment.services.Client")
    def test_client_returns_100(self, mocked_client):
        pay_request_mock_result = Mock(name='pay_request_mock_result', Status=100, Authority='fake')
        pay_request_mock = Mock(name='pay_request_mock',
                                **{'service.PaymentRequest.return_value': pay_request_mock_result})
        mocked_client.return_value = pay_request_mock
        b = self.create_businessman()
        p = payment_service.create_payment_for_smspanel_credit(self.mocked_request, b, 10)
        self.assertEqual(p.create_status, 100)
        self.assertEqual(p.payment_type, Payment.TYPE_SMS)

    @patch("payment.services.Client")
    def test_client_returns_non_100_status_code(self, mocked_client):
        pay_request_mock_result = Mock(name='pay_request_mock_result', Status=200)
        pay_request_mock = Mock(name='pay_request_mock',
                                **{'service.PaymentRequest.return_value': pay_request_mock_result})
        mocked_client.return_value = pay_request_mock
        b = self.create_businessman()
        self.assertRaises(ApplicationErrorException, payment_service.create_payment_for_smspanel_credit,
                          self.mocked_request, b, 10)
        count = Payment.objects.count()
        self.assertEqual(count, 1)

    @patch("payment.services.Client")
    def test_client_raises_exception(self, mocked_client):
        pay_request_mock = Mock(
            name='pay_request_mock',
            **{'service.PaymentRequest.side_effect': Exception("fake")}
        )
        mocked_client.return_value = pay_request_mock
        b = self.create_businessman()
        self.assertRaises(
            ApplicationErrorException,
            payment_service.create_payment_for_smspanel_credit,
            self.mocked_request, b, 10)
        count = Payment.objects.count()
        self.assertEqual(count, 0)
