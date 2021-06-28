import calendar
import random
from datetime import datetime
from typing import List, Tuple
from unittest.mock import patch, Mock

from django.utils import timezone

from base_app.error_codes import ApplicationErrorException, ApplicationErrorCodes
from base_app.tests import BaseTestClass
from panelprofile.models import SMSPanelInfo
from payment.models import Payment, Billing
from payment.services import payment_service, wallet_billing_service
# Create your tests here.
from users.models import BusinessmanCustomer


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


class BaseWalletBillingTestClass(BaseTestClass):
    def setUp(self) -> None:
        super().setUp()
        self.businessman = self.create_businessman()

    def _create_bulk_billing(self, seed: int = 2, joined_by=BusinessmanCustomer.JOINED_BY_PANEL) -> Tuple[
        List[Billing], int]:
        billings = [
            Billing.objects.create(
                businessman=self.businessman,
                amount=10,
                customer_added=self.create_customer_return_businessmancustomer(self.businessman, joined_by))
            for _ in range(seed)
        ]

        sum_amount = sum(b.amount for b in billings)
        return billings, sum_amount

    def _create_billing_with_create_date(self, create_date, joined_by=BusinessmanCustomer.JOINED_BY_PANEL) -> Billing:
        b = Billing.objects.create(amount=10,
                                   businessman=self.businessman,
                                   customer_added=self.create_customer_return_businessmancustomer(
                                       self.businessman,
                                       joined_by
                                   ),
                                   )
        b.create_date = create_date
        b.save()
        return b

    def _create_billing_for_other_businessman(self, joined_by=BusinessmanCustomer.JOINED_BY_CUSTOMER_APP):
        return Billing.objects.create(
            businessman=self.create_businessman(),
            customer_added=self.create_customer_return_businessmancustomer(
                self.businessman,
                joined_by
            ),
            amount=10
        )


class WalletBillingGetTodayBillingUntilNowTest(BaseWalletBillingTestClass):

    def test_billings_added_by_panel(self):
        fakes = self._create_bulk_billing(3)
        self._create_billing_with_create_date(timezone.now() + timezone.timedelta(minutes=1))
        self._create_billing_for_other_businessman()
        result = wallet_billing_service.get_today_billings_until_now(self.businessman)
        count = result.query.filter(businessman=self.businessman).filter(
            customer_added__joined_by=BusinessmanCustomer.JOINED_BY_PANEL
        ).count()
        all_count = result.query.count()
        self.assertEqual(count, all_count)
        self.assertEqual(count, len(fakes[0]))
        self.assertEqual(result.added_by_panel_cost, fakes[1])
        self.assertEqual(result.added_by_app_cost, 0)
        self.assertEqual(result.invitation_cost, 0)

    def test_billings_added_by_app(self):
        fakes = self._create_bulk_billing(3, BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        future = timezone.now() + timezone.timedelta(minutes=1)
        self._create_billing_with_create_date(future, BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        self._create_billing_for_other_businessman(BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        result = wallet_billing_service.get_today_billings_until_now(self.businessman)
        count = result.query.filter(businessman=self.businessman).filter(
            customer_added__joined_by=BusinessmanCustomer.JOINED_BY_CUSTOMER_APP).count()
        all_count = result.query.count()
        self.assertEqual(count, all_count)
        self.assertEqual(count, len(fakes[0]))
        self.assertEqual(result.added_by_panel_cost, 0)
        self.assertEqual(result.added_by_app_cost, fakes[1])
        self.assertEqual(result.invitation_cost, 0)

    def test_billings_invitation(self):
        fakes = self._create_bulk_billing(5, BusinessmanCustomer.JOINED_BY_INVITATION)
        future = timezone.now() + timezone.timedelta(minutes=1)
        self._create_billing_with_create_date(future, BusinessmanCustomer.JOINED_BY_INVITATION)
        self._create_billing_for_other_businessman(BusinessmanCustomer.JOINED_BY_INVITATION)
        result = wallet_billing_service.get_today_billings_until_now(self.businessman)
        count = result.query.filter(businessman=self.businessman).filter(
            customer_added__joined_by=BusinessmanCustomer.JOINED_BY_INVITATION
        ).count()
        all_count = result.query.count()
        self.assertEqual(count, all_count)
        self.assertEqual(count, len(fakes[0]))
        self.assertEqual(result.added_by_panel_cost, 0)
        self.assertEqual(result.added_by_app_cost, 0)
        self.assertEqual(result.invitation_cost, fakes[1])

    def test_billings(self):
        fakes_panel = self._create_bulk_billing(5, BusinessmanCustomer.JOINED_BY_PANEL)
        fakes_app = self._create_bulk_billing(2, BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        fakes_invitation = self._create_bulk_billing(7, BusinessmanCustomer.JOINED_BY_INVITATION)
        future = timezone.now() + timezone.timedelta(minutes=1)
        self._create_billing_with_create_date(future, BusinessmanCustomer.JOINED_BY_PANEL)
        self._create_billing_with_create_date(future, BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        self._create_billing_with_create_date(future, BusinessmanCustomer.JOINED_BY_INVITATION)
        self._create_billing_for_other_businessman(BusinessmanCustomer.JOINED_BY_PANEL)
        self._create_billing_for_other_businessman(BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        self._create_billing_for_other_businessman(BusinessmanCustomer.JOINED_BY_INVITATION)

        result = wallet_billing_service.get_today_billings_until_now(self.businessman)
        count = result.query.filter(businessman=self.businessman).count()
        all_count = result.query.count()
        fakes_count = len(fakes_panel[0]) + len(fakes_app[0]) + len(fakes_invitation[0])
        self.assertEqual(count, all_count)
        self.assertEqual(count, fakes_count)
        self.assertEqual(result.added_by_panel_cost, fakes_panel[1])
        self.assertEqual(result.added_by_app_cost, fakes_app[1])
        self.assertEqual(result.invitation_cost, fakes_invitation[1])


class WalletBillingGetMonthBillingsUntilNowTest(BaseWalletBillingTestClass):

    def _create_billing_with_previous_month_date(self, joined_by=BusinessmanCustomer.JOINED_BY_PANEL) -> Billing:
        first = timezone.now().replace(day=1)
        pr = first - timezone.timedelta(days=1)
        return self._create_billing_with_create_date(pr, joined_by)

    def _create_billing_with_next_month_date(self, joined_by=BusinessmanCustomer.JOINED_BY_PANEL) -> Billing:
        now = timezone.now()
        last_day_of_month = calendar.monthrange(now.year, now.month)[1]
        nx = timezone.datetime(now.year, now.month, last_day_of_month) + timezone.timedelta(days=1)
        return self._create_billing_with_create_date(nx, joined_by)

    def _create_billing_in_next_day_date(self, joined_by=BusinessmanCustomer.JOINED_BY_PANEL):
        day = timezone.now() + timezone.timedelta(days=1)
        return self._create_billing_with_create_date(day, joined_by)

    def test_billings_added_by_panel(self):
        fakes = self._create_bulk_billing(2)
        self._create_billing_with_previous_month_date()
        self._create_billing_with_next_month_date()
        self._create_billing_in_next_day_date()
        self._create_billing_for_other_businessman()
        result = wallet_billing_service.get_month_billings_until_now(self.businessman)
        count = result.query.filter(businessman=self.businessman).filter(
            customer_added__joined_by=BusinessmanCustomer.JOINED_BY_PANEL).count()
        all_count = result.query.count()
        self.assertEqual(count, all_count)
        self.assertEqual(count, len(fakes[0]))
        self.assertEqual(result.added_by_panel_cost, fakes[1])
        self.assertEqual(result.added_by_app_cost, 0)
        self.assertEqual(result.invitation_cost, 0)

    def test_billings_added_by_app(self):
        fakes = self._create_bulk_billing(2, BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        self._create_billing_with_previous_month_date(BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        self._create_billing_with_next_month_date(BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        self._create_billing_in_next_day_date(BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        self._create_billing_for_other_businessman(BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        result = wallet_billing_service.get_month_billings_until_now(self.businessman)
        count = result.query.filter(businessman=self.businessman).filter(
            customer_added__joined_by=BusinessmanCustomer.JOINED_BY_CUSTOMER_APP).count()
        all_count = result.query.count()
        self.assertEqual(count, all_count)
        self.assertEqual(count, len(fakes[0]))
        self.assertEqual(result.added_by_panel_cost, 0)
        self.assertEqual(result.added_by_app_cost, fakes[1])
        self.assertEqual(result.invitation_cost, 0)

    def test_billings_invitation(self):
        fakes = self._create_bulk_billing(10, BusinessmanCustomer.JOINED_BY_INVITATION)
        self._create_billing_with_previous_month_date(BusinessmanCustomer.JOINED_BY_INVITATION)
        self._create_billing_with_next_month_date(BusinessmanCustomer.JOINED_BY_INVITATION)
        self._create_billing_in_next_day_date(BusinessmanCustomer.JOINED_BY_INVITATION)
        self._create_billing_for_other_businessman(BusinessmanCustomer.JOINED_BY_INVITATION)
        result = wallet_billing_service.get_month_billings_until_now(self.businessman)
        count = result.query.filter(businessman=self.businessman).filter(
            customer_added__joined_by=BusinessmanCustomer.JOINED_BY_INVITATION).count()
        all_count = result.query.count()
        self.assertEqual(count, all_count)
        self.assertEqual(count, len(fakes[0]))
        self.assertEqual(result.added_by_panel_cost, 0)
        self.assertEqual(result.added_by_app_cost, 0)
        self.assertEqual(result.invitation_cost, fakes[1])

    def test_billings(self):
        panel_fakes = self._create_bulk_billing(3, BusinessmanCustomer.JOINED_BY_PANEL)
        app_fakes = self._create_bulk_billing(5, BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        invitation_fakes = self._create_bulk_billing(6, BusinessmanCustomer.JOINED_BY_INVITATION)

        self._create_billing_with_previous_month_date(BusinessmanCustomer.JOINED_BY_PANEL)
        self._create_billing_with_next_month_date(BusinessmanCustomer.JOINED_BY_PANEL)
        self._create_billing_in_next_day_date(BusinessmanCustomer.JOINED_BY_PANEL)
        self._create_billing_for_other_businessman(BusinessmanCustomer.JOINED_BY_PANEL)

        self._create_billing_with_previous_month_date(BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        self._create_billing_with_next_month_date(BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        self._create_billing_in_next_day_date(BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        self._create_billing_for_other_businessman(BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)

        self._create_billing_with_previous_month_date(BusinessmanCustomer.JOINED_BY_INVITATION)
        self._create_billing_with_next_month_date(BusinessmanCustomer.JOINED_BY_INVITATION)
        self._create_billing_in_next_day_date(BusinessmanCustomer.JOINED_BY_INVITATION)
        self._create_billing_for_other_businessman(BusinessmanCustomer.JOINED_BY_INVITATION)

        result = wallet_billing_service.get_month_billings_until_now(self.businessman)
        panel_counts = result.query.filter(businessman=self.businessman).filter(
            customer_added__joined_by=BusinessmanCustomer.JOINED_BY_PANEL).count()
        app_count = result.query.filter(businessman=self.businessman).filter(
            customer_added__joined_by=BusinessmanCustomer.JOINED_BY_CUSTOMER_APP).count()
        invitation_count = result.query.filter(businessman=self.businessman).filter(
            customer_added__joined_by=BusinessmanCustomer.JOINED_BY_INVITATION).count()
        all_count = result.query.count()
        fake_count = len(panel_fakes[0]) + len(app_fakes[0]) + len(invitation_fakes[0])
        self.assertEqual(all_count, fake_count)
        self.assertEqual(panel_counts, len(panel_fakes[0]))
        self.assertEqual(app_count, len(app_fakes[0]))
        self.assertEqual(invitation_count, len(invitation_fakes[0]))
        self.assertEqual(result.added_by_panel_cost, panel_fakes[1])
        self.assertEqual(result.added_by_app_cost, app_fakes[1])
        self.assertEqual(result.invitation_cost, invitation_fakes[1])


class TestGetMonthBillingsGroupByDay(BaseWalletBillingTestClass):

    def _create_bulk_billing_in_different_month(self, month: int, day: int, seed: int,
                                                joined_by=BusinessmanCustomer.JOINED_BY_PANEL) -> Tuple[
        List[Billing], datetime]:
        now = timezone.now()
        d = now.replace(month=month, day=day)
        fakes = []
        for _ in range(seed):
            f = self._create_billing_with_create_date(d, joined_by)
            fakes.append(f)
        return fakes, d

    def test_billings_for_present_month(self):
        t = timezone.now()
        if t.day < 30:
            tomorrow_past = t + timezone.timedelta(days=1)
        else:
            tomorrow_past = t - timezone.timedelta(days=1)
        tomorrow_past_fake = self._create_billing_with_create_date(tomorrow_past)
        fakes = self._create_bulk_billing(5)
        p = self.create_time_in_past()
        self._create_billing_with_create_date(p)
        self._create_billing_for_other_businessman()
        result = wallet_billing_service.get_month_billings_group_by_day(self.businessman, timezone.now())

        self.assertEqual(len(result), 2)
        today_billing_result = filter(lambda x: x.amount == fakes[1], result)
        today_billing_result = list(today_billing_result)
        self.assertEqual(len(today_billing_result), 1)
        self.assertEqual(today_billing_result[0].create_date, fakes[0][0].create_date.date())
        tomorrow_past_billing = filter(lambda x: x.amount == tomorrow_past_fake.amount, result)
        tomorrow_past_billing = list(tomorrow_past_billing)
        self.assertEqual(len(tomorrow_past_billing), 1)
        self.assertEqual(tomorrow_past_billing[0].create_date, tomorrow_past_fake.create_date.date())

    def test_billing_for_other_month(self):
        fakes_panel_month1 = self._create_bulk_billing_in_different_month(1, 5, 2)
        fakes_customer_month1 = self._create_bulk_billing_in_different_month(1, 10, 3,
                                                                             BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)

        fakes_other_month = self._create_bulk_billing_in_different_month(2, 10, 5)

        result = wallet_billing_service.get_month_billings_group_by_day(self.businessman, fakes_panel_month1[1])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].create_date, fakes_panel_month1[1].date())
        self.assertEqual(result[1].create_date, fakes_customer_month1[1].date())
        panel_sum_amount = sum([b.amount for b in fakes_panel_month1[0]])
        self.assertEqual(result[0].amount, panel_sum_amount)
        customer_sum_amount = sum([b.amount for b in fakes_customer_month1[0]])
        self.assertEqual(result[1].amount, customer_sum_amount)
