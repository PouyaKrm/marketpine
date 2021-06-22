import random
from unittest.mock import patch, Mock

from base_app.error_codes import ApplicationErrorException, ApplicationErrorCodes
from base_app.tests import BaseTestClass
from panelprofile.models import SMSPanelInfo
from payment.models import Payment
from payment.services import payment_service


# Create your tests here.


class PaymentServiceBaseTestClass(BaseTestClass):

    def setUp(self) -> None:
        super().setUp()
        self.p = self._create_payment()

    def _create_payment(self, **kwargs) -> Payment:
        b = self.create_businessman()
        return Payment.objects.create(businessman=b, amount=0, authority=random.randint(0, 200).__str__(), **kwargs)


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


class TestVerifyPayment(PaymentServiceBaseTestClass):

    @patch("payment.services.Client")
    def test_payment_verified_before(self, mocked_client):
        p = self._create_payment(refid='fake id')
        with self.assertRaises(ApplicationErrorException) as cx:
            payment_service.verify_payment(p)

        ex = cx.exception
        self.assertEqual(ex.http_message, ApplicationErrorCodes.PAYMENT_ALREADY_VERIFIED)
        mocked_client.assert_not_called()

    @patch("payment.services.Client")
    def test_client_throws_exception(self, mocked_client):
        mocked_client.return_value = Mock(**{'service.PaymentVerification.side_effect': ValueError('fake')})
        with self.assertRaises(ApplicationErrorException) as cx:
            payment_service.verify_payment(self.p)

        ex = cx.exception
        self.assertEqual(ex.http_message, ApplicationErrorCodes.PAYMENT_VERIFICATION_FAILED)
        mocked_client.assert_called_once()
        assert isinstance(ex.originalException, ValueError)

    @patch("payment.services.Client")
    def test_client_returns_non_100_status(self, mocked_client):
        status = 200
        mocked_client.return_value = Mock(**{'service.PaymentVerification.return_value': Mock(Status=status)})
        with self.assertRaises(ApplicationErrorException) as cx:
            payment_service.verify_payment(self.p)
        ex = cx.exception
        self.assertEqual(ex.http_message, ApplicationErrorCodes.PAYMENT_WAS_NOT_SUCCESSFUL)
        self.assertEqual(self.p.verification_status, status)

    @patch("payment.services.Client")
    def test_client_returns_100_status(self, mocked_client):
        status = 100
        refid = 'fake'
        mocked_client.return_value = Mock(
            **{'service.PaymentVerification.return_value': Mock(Status=status, RefID=refid)})
        payment_service.verify_payment(self.p)
        self.assertEqual(self.p.verification_status, status)
        self.assertEqual(self.p.refid, refid)


class TestVerifyPaymentByAuthority(PaymentServiceBaseTestClass):

    def setUp(self) -> None:
        super().setUp()
        self.callback_status = "OK"

    def test_throws_exception_on_invalid_callback_status(self):
        self.assertRaises(ValueError, payment_service.verify_payment_by_authority, 'auth', 'fake')

    def test_invalid_authority(self):
        with self.assertRaises(ApplicationErrorException) as cx:
            payment_service.verify_payment_by_authority('auth', self.callback_status)
        ex = cx.exception
        self.assertEqual(ex.http_message, ApplicationErrorCodes.RECORD_NOT_FOUND)

    def test_payment_verified_before(self):
        self.p.refid = 'fake'
        self.p.save()

        with self.assertRaises(ApplicationErrorException) as cx:
            payment_service.verify_payment_by_authority(self.p.authority, self.callback_status)
        ex = cx.exception
        self.assertEqual(ex.http_message, ApplicationErrorCodes.PAYMENT_ALREADY_VERIFIED)

    @patch('payment.services.sms_panel_info_service.get_panel_increase_credit_in_tomans')
    @patch("payment.services.payment_service.verify_payment")
    def test_sms_payment_increase_sms_panel_credit_failed(self, verify_payment_mock, increase_credit_mock):
        self.p.payment_type = Payment.TYPE_SMS
        self.p.save()
        ex = ApplicationErrorException(ApplicationErrorCodes.PAYMENT_ALREADY_VERIFIED)
        increase_credit_mock.side_effect = ex
        with self.assertRaises(ApplicationErrorException) as cx:
            payment_service.verify_payment_by_authority(self.p.authority, self.callback_status)
        excep = cx.exception
        self.assertEqual(excep, ex)
        increase_credit_mock.assert_called_once()
        verify_payment_mock.assert_called_once()

    @patch('payment.services.sms_panel_info_service.get_panel_increase_credit_in_tomans')
    @patch("payment.services.payment_service.verify_payment")
    @patch("payment.services.sms_panel_info_service.get_panel_decrease_credit_in_tomans")
    def test_sms_payment_verify_payment_throws_exception(self, decrease_credit_mock, verify_payment_mock,
                                                         increase_credit_mock):
        info = SMSPanelInfo()
        increase_credit_mock.return_value = info
        ex = ValueError('fake')
        verify_payment_mock.side_effect = ex
        p = self._create_payment(payment_type=Payment.TYPE_SMS)
        with self.assertRaises(ApplicationErrorException) as cx:
            payment_service.verify_payment_by_authority(p.authority, self.callback_status)
        exception = cx.exception
        self.assertEqual(exception.originalException, ex)
        verify_payment_mock.assert_called_once()
        decrease_credit_mock.assert_not_called()
        increase_credit_mock.assert_not_called()

    @patch('payment.services.sms_panel_info_service.get_panel_increase_credit_in_tomans')
    @patch("payment.services.payment_service.verify_payment")
    @patch("payment.services.sms_panel_info_service.get_panel_decrease_credit_in_tomans")
    @patch("payment.services.sms_panel_info_service.get_buinessman_sms_panel")
    def test_success_execution(self, get_businessman_sms, panel_decrease, verify_payment, panel_increase):
        info = SMSPanelInfo()
        get_businessman_sms.return_value = info
        p = self._create_payment(payment_type=Payment.TYPE_SMS)
        result = payment_service.verify_payment_by_authority(p.authority, self.callback_status)
        self.assertEqual(result[0], p)
        self.assertEqual(result[1], info)
        get_businessman_sms.assert_called_once()
        panel_increase.assert_called_once()
        verify_payment.assert_called_once()
        panel_decrease.assert_not_called()
