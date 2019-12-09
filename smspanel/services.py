
from users.models import Businessman
from common.util.sms_panel.message import ClientBulkToAllSMSMessage
from common.util.sms_panel.exceptions import SendSMSException
from common.util.kavenegar_local import APIException
from .models import UnsentTemplateSMS, SentSMS

def send_template_sms_message_to_all(user: Businessman, template: str):

    """
    Because send to all by template does not have any serailizer, this helper method is created.
    This method send sms message to all customers and saves the record of them in the database.
    """

    client_sms =ClientBulkToAllSMSMessage(user, template)

    try:
        sent_messages = client_sms.send_bulk()
    except SendSMSException as e:
        UnsentTemplateSMS(businessman=user, template=template, resend_start=e.failed_on.id)
        raise APIException(e.status, e.message)

    while sent_messages is not None:

        SentSMS.objects.bulk_create([SentSMS(businessman=user, message_id=m['messageid'], receptor=m['receptor']) for m in sent_messages])
        try:
            sent_messages = client_sms.send_bulk()
        except SendSMSException as e:
            UnsentTemplateSMS(businessman=user, template=template, resend_start=e.failed_on.id)
            raise APIException(e.status, e.message)
