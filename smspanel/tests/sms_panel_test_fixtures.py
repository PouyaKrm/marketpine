from base_app.tests import *
from smspanel.models import SMSMessage, SMSMessageReceivers, WelcomeMessage, SentSMS, SMSTemplate


@pytest.fixture
def create_sms_message(db, businessman_with_customer_tuple):
    def create_sms(status: str, failed_attempts: int = 0) -> SMSMessage:
        return SMSMessage.objects.create(
            businessman=businessman_with_customer_tuple[0],
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
def sent_sms_list_1(db, create_sms_message, businessman_with_customer_tuple) -> List[SentSMS]:
    sms = create_sms_message(status=SMSMessage.STATUS_DONE)

    SentSMS.objects.bulk_create(
        [SentSMS(sms_message=sms, message='fake', receptor=c) for c in businessman_with_customer_tuple[1]]
    )

    return list(SentSMS.objects.all())


@pytest.fixture
def sms_template_1(db, businessman_1) -> SMSTemplate:
    return SMSTemplate.objects.create(businessman=businessman_1, content='content', title='title')
