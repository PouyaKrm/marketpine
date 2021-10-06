from django.conf import settings

from base_app.tests import *
from panelprofile.models import SMSPanelInfo
from smspanel.models import SMSMessage, SMSMessageReceivers, WelcomeMessage, SentSMS, SMSTemplate

min_credit = settings.SMS_PANEL['MIN_CREDIT']
max_message_const = settings.SMS_PANEL['MAX_MESSAGE_COST']


@pytest.fixture
def create_sms_message(db, businessman_1_with_customer_tuple):
    def create_sms(status: str, failed_attempts: int = 0) -> SMSMessage:
        return SMSMessage.objects.create(
            businessman=businessman_1_with_customer_tuple[0],
            status=status,
            send_fail_attempts=failed_attempts,
            reserved_credit=10
        )

    return create_sms


@pytest.fixture
def sms_message_pending_1(db, create_sms_message) -> SMSMessage:
    return create_sms_message(status=SMSMessage.STATUS_PENDING)


@pytest.fixture
def sms_message_pending_list_1(db, create_sms_message) -> List[SMSMessage]:
    result = []
    for _ in range(10):
        result.append(create_sms_message(SMSMessage.STATUS_PENDING))
    return result


@pytest.fixture
def sms_message_failed_1(db, create_sms_message) -> SMSMessage:
    return create_sms_message(status=SMSMessage.STATUS_FAILED, failed_attempts=10)


@pytest.fixture
def sms_message_failed_list_1(db, create_sms_message) -> List[SMSMessage]:
    result = []
    for i in range(10):
        result.append(create_sms_message(SMSMessage.STATUS_FAILED))
    return result


@pytest.fixture
def sms_message_with_receivers(db, sms_message_pending_1, businessman_with_customer_tuple) -> Tuple[
    SMSMessage, List[SMSMessageReceivers]]:
    result = []
    for i in businessman_with_customer_tuple[1]:
        s = SMSMessageReceivers.objects.create(sms_message=sms_message_pending_1, customer=i, is_sent=False)
        result.append(s)

    return sms_message_pending_1, result


@pytest.fixture
def welcome_message_1(db, businessman_1: Businessman) -> WelcomeMessage:
    return WelcomeMessage.objects.create(businessman=businessman_1, message='fake', send_message=True)


@pytest.fixture
def sent_sms_list_1(db, create_sms_message, businessman_1_with_customer_tuple) -> List[SentSMS]:
    sms = create_sms_message(status=SMSMessage.STATUS_DONE)

    SentSMS.objects.bulk_create(
        [SentSMS(sms_message=sms, message='fake', receptor=c) for c in businessman_1_with_customer_tuple[1]]
    )

    return list(SentSMS.objects.all())


def create_sms_template(businessman: Businessman) -> SMSTemplate:
    name = fake.text()[:20]
    text = fake.text()[:40]
    return SMSTemplate.objects.create(businessman=businessman, content=text, title=name)


@pytest.fixture
def sms_template_1(db, businessman_1) -> SMSTemplate:
    return create_sms_template(businessman_1)


@pytest.fixture
def sms_template_list(db, businessman_1) -> List[SMSTemplate]:
    result = []
    for _ in range(10):
        result.append(create_sms_template(businessman_1))
    return result


def get_sms_panel_info_object() -> SMSPanelInfo:
    return SMSPanelInfo(status=SMSPanelInfo.STATUS_ACTIVE_LOGIN,
                        credit=min_credit + 1000,
                        sms_farsi_cost=100,
                        sms_english_cost=max_message_const
                        )


@pytest.fixture
def active_sms_panel_info_1(db, businessman_1) -> SMSPanelInfo:
    sms = get_sms_panel_info_object()
    sms.businessman = businessman_1
    sms.save()
    return sms
