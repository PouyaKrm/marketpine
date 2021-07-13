import random
from datetime import datetime
from typing import List, Tuple
from unittest.mock import patch, Mock

import jdatetime
import pytz
from django.conf import settings

from base_app.error_codes import ApplicationErrorException, ApplicationErrorCodes
from base_app.tests import BaseTestClass
from panelprofile.models import SMSPanelInfo
from payment.models import Payment, Billing
from payment.services import payment_service, wallet_billing_service
# Create your tests here.
from users.models import BusinessmanCustomer, Businessman

wallet_minimum_credit_increase = settings.WALLET['MINIMUM_ALLOWED_CREDIT_INCREASE']


class PaymentServiceBaseTestClass(BaseTestClass):

    def setUp(self) -> None:
        super().setUp()

    def _create_payment(self, **kwargs) -> Payment:
        b = self.create_businessman()
        return Payment.objects.create(businessman=b, amount=0, authority=random.randint(0, 200).__str__(), **kwargs)


class CreatePaymentTest(PaymentServiceBaseTestClass):

    def setUp(self) -> None:
        super().setUp()
        self.mocked_request = Mock('Http Request')
        self.mocked_request.build_absolute_uri = Mock(return_value="fake url")
        b = self.create_businessman()
        self.call_params = {
            'request': self.mocked_request,
            'user': b,
            'amount_toman': 10,
            'description': 'fake_desc',
            'payment_type': Payment.TYPE_SMS
        }

    @patch("payment.services.Client")
    def test_client_returns_100(self, mocked_client):
        pay_request_mock_result = Mock(name='pay_request_mock_result', Status=100, Authority='fake')
        pay_request_mock = Mock(name='pay_request_mock',
                                **{'service.PaymentRequest.return_value': pay_request_mock_result})
        mocked_client.return_value = pay_request_mock
        p = payment_service.create_payment(**self.call_params)
        self._assert_created_payment(p, 100)

    @patch("payment.services.Client")
    def test_client_returns_non_100_status_code(self, mocked_client):
        status = 200
        pay_request_mock_result = Mock(name='pay_request_mock_result', Status=status)
        pay_request_mock = Mock(name='pay_request_mock',
                                **{'service.PaymentRequest.return_value': pay_request_mock_result})
        mocked_client.return_value = pay_request_mock
        with self.assertRaises(ApplicationErrorException) as cx:
            payment_service.create_payment(**self.call_params)
        ex = cx.exception
        self.assertEqual(ex.http_message, ApplicationErrorCodes.PAYMENT_CREATION_FAILED)
        count = Payment.objects.count()
        self.assertEqual(count, 1)
        p = Payment.objects.first()
        self._assert_created_payment(p, status)

    @patch("payment.services.Client")
    def test_client_raises_exception(self, mocked_client):
        pay_request_mock = Mock(
            name='pay_request_mock',
            **{'service.PaymentRequest.side_effect': Exception("fake")}
        )
        mocked_client.return_value = pay_request_mock
        with self.assertRaises(ApplicationErrorException) as cx:
            payment_service.create_payment(**self.call_params)
        ex = cx.exception
        self.assertEqual(ex.http_message, ApplicationErrorCodes.PAYMENT_CREATION_FAILED)
        count = Payment.objects.count()
        self.assertEqual(count, 0)

    def _assert_created_payment(self, p: Payment, create_status: int):
        self.assertEqual(p.create_status, create_status)
        self.assertEqual(p.payment_type, self.call_params['payment_type'])
        self.assertEqual(p.businessman, self.call_params['user'])
        self.assertEqual(p.amount, self.call_params['amount_toman'])
        self.assertEqual(p.description, self.call_params['description'])
        self.assertEqual(p.payment_type, self.call_params['payment_type'])


class TestCreatePaymentSmspanelCredit(PaymentServiceBaseTestClass):

    def setUp(self) -> None:
        super().setUp()
        mocked_request = Mock()
        b = self.create_businessman()
        self.call_params = {
            'request': mocked_request,
            'user': b,
            'amount_toman': 10,
        }

    @patch('payment.services.payment_service.create_payment')
    def test_payment_creation(self, mocked):
        p = Payment()
        mocked.return_value = p
        result = payment_service.create_payment_for_smspanel_credit(**self.call_params)
        self.assertEqual(result, p)


class TestCreatePaymentWallet(PaymentServiceBaseTestClass):

    def setUp(self) -> None:
        super().setUp()

    def test_low_minimum_credit(self):
        with self.assertRaises(ApplicationErrorException) as cx:
            payment_service.create_payment_for_wallet_credit(Mock(), self.create_businessman(),
                                                             wallet_minimum_credit_increase - 100)
        ex = cx.exception
        self.assertEqual(ex.http_message, ApplicationErrorCodes.MINIMUM_WALLET_CREDIT_INCREASE)

    @patch('payment.services.payment_service.create_payment')
    def test_create_payment(self, mocked):
        p = Payment()
        request = Mock()
        b = self.create_businessman()
        amount = wallet_minimum_credit_increase + 100
        mocked.return_value = p
        result = payment_service.create_payment_for_wallet_credit(request, b, amount)
        self.assertEqual(result, p)
        mocked.assert_called_once()


class TestVerifyPayment(PaymentServiceBaseTestClass):

    def setUp(self) -> None:
        super().setUp()
        self.p = self._create_payment()

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
        self.p = self._create_payment()
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

    def _create_billing_with_create_date(self, jcreate_date, joined_by=BusinessmanCustomer.JOINED_BY_PANEL) -> Billing:
        b = Billing.objects.create(
            amount=10,
            businessman=self.businessman,
            customer_added=self.create_customer_return_businessmancustomer(
                self.businessman,
                joined_by
            ),
        )
        b.jcreate_date = jcreate_date
        tz = pytz.timezone('Asia/Tehran')
        d = datetime.now()
        localized = tz.localize(b.jcreate_date.togregorian())
        utc_date = localized.astimezone(pytz.utc)
        b.create_date = utc_date
        b.save()
        return b

    def _create_bulk_billing_in_different_month(self, month: int, day: int, seed: int,
                                                joined_by=BusinessmanCustomer.JOINED_BY_PANEL,
                                                businessman: Businessman = None) -> Tuple[
        List[Billing], int, datetime]:
        now = jdatetime.datetime.now()
        d = now.replace(month=month, day=day)
        fakes = []
        for _ in range(seed):
            f = self._create_billing_with_create_date(d, joined_by)
            if businessman is not None:
                f.businessman = businessman
                f.save()
            fakes.append(f)
        a_sum = sum([b.amount for b in fakes])
        return fakes, a_sum, d

    def _create_billing_for_other_businessman(self, joined_by=BusinessmanCustomer.JOINED_BY_CUSTOMER_APP):
        return Billing.objects.create(
            businessman=self.create_businessman(),
            customer_added=self.create_customer_return_businessmancustomer(
                self.businessman,
                joined_by
            ),
            amount=10
        )


class TestGetMonthBillings(BaseWalletBillingTestClass):

    def _create_billing_with_random_colck(self, create_date, seed=1, joined_by=BusinessmanCustomer.JOINED_BY_PANEL) -> \
            Tuple[
                List[Billing], int
            ]:
        new_date = create_date.replace(hour=random.randint(0, 23), minute=random.randint(0, 59),
                                       second=random.randint(0, 59))
        result = []
        amount_sum = 0
        for i in range(seed):
            r = self._create_billing_with_create_date(new_date, joined_by)
            amount_sum = amount_sum + r.amount
            result.append(r)
        return result, amount_sum

    def test_billings_for_present_month(self):
        panel_billings = []
        app_billings = []
        invitation_billings = []
        now = jdatetime.datetime.now()
        count = 30

        for i in range(count):
            date = now.replace(day=i + 1)
            b = self._create_billing_with_random_colck(date, random.randint(1, 20), BusinessmanCustomer.JOINED_BY_PANEL)
            panel_billings.append(b)
            p = self._create_billing_with_random_colck(date, random.randint(1, 20),
                                                       BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
            app_billings.append(p)
            i = self._create_billing_with_random_colck(date, random.randint(1, 20),
                                                       BusinessmanCustomer.JOINED_BY_INVITATION)
            invitation_billings.append(i)

        result = wallet_billing_service.get_month_billings(self.businessman, now)
        self.assertEqual(len(result), count * 3)

        panels = list(filter(lambda x: x.joined_by == BusinessmanCustomer.JOINED_BY_PANEL, result))
        apps = list(filter(lambda x: x.joined_by == BusinessmanCustomer.JOINED_BY_CUSTOMER_APP, result))
        invitations = list(filter(lambda x: x.joined_by == BusinessmanCustomer.JOINED_BY_INVITATION, result))

        for i in range(count):
            r = panels[i]
            p = panel_billings[i]
            self.assertEqual(r.amount,
                             p[1])
            self.assertEqual(r.create_date, p[0][0].jcreate_date.date())
            self.assertEqual(r.joined_by, p[0][0].customer_added.joined_by)

            r = apps[i]
            a = app_billings[i]
            self.assertEqual(r.amount,
                             a[1])
            self.assertEqual(r.create_date, a[0][0].jcreate_date.date())
            self.assertEqual(r.joined_by, a[0][0].customer_added.joined_by)

            r = invitations[i]
            n = invitation_billings[i]

            self.assertEqual(r.amount,
                             n[1])
            self.assertEqual(r.create_date, n[0][0].jcreate_date.date())
            self.assertEqual(r.joined_by, n[0][0].customer_added.joined_by)

    def test_billings_in_different_months(self):
        now = jdatetime.datetime.now()
        if now.month < 12:
            other = now.replace(month=now.month + 1)
        else:
            other = now.replace(month=now.month - 1)

        present_count = 3
        next_count = 10
        panel_billing = []
        app_billing = []

        for i in range(present_count):
            date = now.replace(day=i + 1)
            self._create_billing_with_random_colck(date)

        for i in range(next_count):
            date = other.replace(day=i + 1)
            b = self._create_billing_with_random_colck(date, random.randint(1, 30))
            panel_billing.append(b)
            p = self._create_billing_with_random_colck(date, random.randint(1, 5),
                                                       BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
            app_billing.append(p)

        result = wallet_billing_service.get_month_billings(self.businessman, other)
        self.assertEqual(len(result), next_count * 2)

        panels = list(filter(lambda x: x.joined_by == BusinessmanCustomer.JOINED_BY_PANEL, result))
        apps = list(filter(lambda x: x.joined_by == BusinessmanCustomer.JOINED_BY_CUSTOMER_APP, result))
        invitations = list(filter(lambda x: x.joined_by == BusinessmanCustomer.JOINED_BY_INVITATION, result))

        for i in range(next_count):
            r = panels[i]
            p = panel_billing[i]
            self.assertEqual(r.amount, p[1])
            self.assertEqual(r.create_date, p[0][0].jcreate_date.date())
            self.assertEqual(r.joined_by, p[0][0].customer_added.joined_by)

            r = apps[i]
            a = app_billing[i]
            self.assertEqual(r.amount, a[1])
            self.assertEqual(r.create_date, a[0][0].jcreate_date.date())
            self.assertEqual(r.joined_by, a[0][0].customer_added.joined_by)

        self.assertEqual(len(invitations), 0)


class TestGetDayBillingsGroupByDayAndCustomerJoinedByType(BaseWalletBillingTestClass):

    def setUp(self) -> None:
        super().setUp()
        self.fakes_panel = self._create_bulk_billing_in_different_month(1, 2, 5, BusinessmanCustomer.JOINED_BY_PANEL)
        self.fakes_app = self._create_bulk_billing_in_different_month(1, 2, 20,
                                                                      BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        self.fakes_invitation = self._create_bulk_billing_in_different_month(1, 2, 30,
                                                                             BusinessmanCustomer.JOINED_BY_INVITATION)

    def test_billing(self):
        result = wallet_billing_service.get_day_billings_group_by_day_and_customer_joined_by_type(
            self.businessman,
            self.fakes_panel[2]
        )

        self._assert_call_result(result)

    def test_billings_other_businessman_have_billing(self):
        b = self.create_businessman()

        self._create_bulk_billing_in_different_month(1, 2, 60, BusinessmanCustomer.JOINED_BY_PANEL, b)
        self._create_bulk_billing_in_different_month(1, 2, 70, BusinessmanCustomer.JOINED_BY_CUSTOMER_APP, b)
        self._create_bulk_billing_in_different_month(1, 2, 80, BusinessmanCustomer.JOINED_BY_INVITATION, b)

        result = wallet_billing_service.get_day_billings_group_by_day_and_customer_joined_by_type(
            self.businessman,
            self.fakes_panel[2]
        )

        self._assert_call_result(result)

    def test_billings_exist_in_other_day(self):
        self._create_bulk_billing_in_different_month(1, 3, 4, BusinessmanCustomer.JOINED_BY_PANEL)
        self._create_bulk_billing_in_different_month(1, 3, 6, BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        self._create_bulk_billing_in_different_month(1, 3, 8, BusinessmanCustomer.JOINED_BY_INVITATION)

        result = wallet_billing_service.get_day_billings_group_by_day_and_customer_joined_by_type(
            self.businessman,
            self.fakes_panel[2]
        )

        self._assert_call_result(result)

    def _assert_call_result(self, result):
        self.assertEqual(len(result), 3)
        r_p = list(filter(lambda x: x.joined_by == BusinessmanCustomer.JOINED_BY_PANEL, result))
        self.assertEqual(len(r_p), 1)
        self.assertEqual(r_p[0].amount, self.fakes_panel[1])
        self.assertIsNone(r_p[0].create_date)

        r_a = list(filter(lambda x: x.joined_by == BusinessmanCustomer.JOINED_BY_CUSTOMER_APP, result))
        self.assertEqual(len(r_a), 1)
        self.assertEqual(r_a[0].amount, self.fakes_app[1])
        self.assertIsNone(r_a[0].create_date)

        r_i = list(filter(lambda x: x.joined_by == BusinessmanCustomer.JOINED_BY_INVITATION, result))
        self.assertEqual(len(r_i), 1)
        self.assertEqual(r_i[0].amount, self.fakes_invitation[1])
        self.assertIsNone(r_i[0].create_date)


class TestPresentYearBillings(BaseWalletBillingTestClass):

    def setUp(self) -> None:
        super().setUp()
        self.fakes_panel_month = 5
        self.fakes_app_month = 2
        self.fakes_invitation_month = 12
        self.fakes_panel1 = self._create_bulk_billing_in_different_month(
            self.fakes_panel_month, 2, 5,
            BusinessmanCustomer.JOINED_BY_PANEL
        )

        self.fakes_panel2 = self._create_bulk_billing_in_different_month(
            self.fakes_panel_month, 3, 6,
            BusinessmanCustomer.JOINED_BY_PANEL
        )

        self.fakes_app1 = self._create_bulk_billing_in_different_month(
            self.fakes_app_month, 6, 20,
            BusinessmanCustomer.JOINED_BY_CUSTOMER_APP
        )

        self.fakes_app2 = self._create_bulk_billing_in_different_month(
            self.fakes_app_month, 8, 5,
            BusinessmanCustomer.JOINED_BY_CUSTOMER_APP
        )

        self.fakes_invitation1 = self._create_bulk_billing_in_different_month(
            self.fakes_invitation_month, 8, 30,
            BusinessmanCustomer.JOINED_BY_INVITATION
        )

        self.fakes_invitation2 = self._create_bulk_billing_in_different_month(
            self.fakes_invitation_month, 9, 5,
            BusinessmanCustomer.JOINED_BY_INVITATION
        )

    def _create_bulk_billing_in_different_year(self, year: int, month: int, day: int, seed: int,
                                               joined_by=BusinessmanCustomer.JOINED_BY_PANEL,
                                               businessman: Businessman = None) -> Tuple[
        List[Billing], int, datetime]:
        now = jdatetime.datetime.now()
        future = now.replace(year=year)
        fakes = self._create_bulk_billing_in_different_month(month, day, seed, joined_by, businessman)
        for i in fakes[0]:
            i.jcreate_date = future
            i.create_date = future.utcnow().togregorian()
            i.save()

        return fakes

    def test_billings(self):
        result = wallet_billing_service.get_present_year_billings(self.businessman)

        self._assert_call_result(result)

    def test_billing_in_different_year(self):
        now = jdatetime.datetime.now()
        year = now.replace(year=now.year + 1).year
        self._create_bulk_billing_in_different_year(year, self.fakes_panel_month, 2, 5,
                                                    BusinessmanCustomer.JOINED_BY_PANEL)
        self._create_bulk_billing_in_different_year(year, self.fakes_app_month, 6, 20,
                                                    BusinessmanCustomer.JOINED_BY_CUSTOMER_APP)
        self._create_bulk_billing_in_different_year(year, self.fakes_invitation_month, 8, 30,
                                                    BusinessmanCustomer.JOINED_BY_INVITATION)

        result = wallet_billing_service.get_present_year_billings(self.businessman)

        self._assert_call_result(result)

    def test_billing_for_other_businessman(self):
        b = self.create_businessman()
        self._create_bulk_billing_in_different_month(self.fakes_panel_month, 2, 5,
                                                     BusinessmanCustomer.JOINED_BY_PANEL,
                                                     b
                                                     )
        self._create_bulk_billing_in_different_month(self.fakes_app_month, 6, 20,
                                                     BusinessmanCustomer.JOINED_BY_CUSTOMER_APP,
                                                     b)
        self._create_bulk_billing_in_different_month(self.fakes_invitation_month, 8, 30,
                                                     BusinessmanCustomer.JOINED_BY_INVITATION,
                                                     b)

        result = wallet_billing_service.get_present_year_billings(self.businessman)

        self._assert_call_result(result)

    def _assert_call_result(self, result):
        self.assertEqual(len(result), 3)

        panels = list(filter(lambda x: x.joined_by == BusinessmanCustomer.JOINED_BY_PANEL, result))
        apps = list(filter(lambda x: x.joined_by == BusinessmanCustomer.JOINED_BY_CUSTOMER_APP, result))
        invitations = list(filter(lambda x: x.joined_by == BusinessmanCustomer.JOINED_BY_INVITATION, result))

        self.assertEqual(len(panels), 1)
        self.assertEqual(panels[0].amount, self.fakes_panel1[1] + self.fakes_panel2[1])
        self.assertEqual(panels[0].create_date.year, self.fakes_panel1[2].date().year)
        self.assertEqual(panels[0].create_date.month, self.fakes_panel1[2].date().month)

        self.assertEqual(len(apps), 1)
        self.assertEqual(apps[0].amount, self.fakes_app1[1] + self.fakes_app2[1])
        self.assertEqual(apps[0].create_date.year, self.fakes_app1[2].date().year)
        self.assertEqual(apps[0].create_date.month, self.fakes_app1[2].date().month)

        self.assertEqual(len(invitations), 1)
        self.assertEqual(invitations[0].amount, self.fakes_invitation1[1] + self.fakes_invitation2[1])
        self.assertEqual(invitations[0].create_date.year, self.fakes_invitation1[2].date().year)
        self.assertEqual(invitations[0].create_date.month, self.fakes_invitation1[2].date().month)
