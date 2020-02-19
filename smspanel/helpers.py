
from users.models import Businessman
from common.util.sms_panel.message import ClientBulkToCustomerSMSMessage, ClientBulkToAllToCustomerSMSMessage, \
    ClientSMSMessage, ClientToAllCustomersSMSMessage, BulkMessageWithAdditionalContext
from common.util.sms_panel.exceptions import SendSMSException
from common.util.sms_panel.helpers import calculate_total_sms_cost
from common.util.kavenegar_local import APIException
from .models import UnsentTemplateSMS, SentSMS, UnsentPlainSMS, SMSMessage
from django.db.models import QuerySet

from groups.models import BusinessmanGroups

def send_template_sms_message_to_all(user: Businessman, template: str):

    """
    Because send to all by template does not have any serailizer, this helper method is created.
    This method send sms message to all customers and saves the record of them in the database.
    """

    client_sms =ClientBulkToAllToCustomerSMSMessage(user, template)

    try:
        sent_messages = client_sms.send_bulk()
    except SendSMSException as e:
        UnsentTemplateSMS(businessman=user, template=template, resend_start=e.failed_on.id)
        raise APIException(e.status, e.message)

    while sent_messages is not None:
        user.smspanelinfo.reduce_credit(calculate_total_sms_cost(sent_messages))
        SentSMS.objects.bulk_create([SentSMS(businessman=user, message_id=m['messageid'], receptor=m['receptor']) for m in sent_messages])
        try:
            sent_messages = client_sms.send_bulk()
        except SendSMSException as e:
            UnsentTemplateSMS(businessman=user, template=template, resend_start=e.failed_on.id)
            raise APIException(e.status, e.message)


class SendSMSMessage():

    def create_unsent_plain_sms(self, ex: SendSMSException, content: str, user: Businessman, receptors: QuerySet):

        remained_recoptors = receptors.order_by('id').filter(id__gte=ex.failed_on.id).all()
        obj = UnsentPlainSMS.objects.create(businessman=user, message=content)
        obj.customers.add(*remained_recoptors)
        obj.save()

      

    def create_unsent_template_sms(self, ex: SendSMSException, template: str, businessman: Businessman, receptors: QuerySet):

        remained_receptors = receptors.order_by('id').filter(id__gte=ex.failed_on.id).all()
        obj = UnsentTemplateSMS.objects.create(businessman=businessman, template=template)
        obj.customers.add(*remained_receptors)
        obj.save()
       

    def send_plain_sms(self, customers: QuerySet, user: Businessman, message: str):

        # client_sms = ClientSMSMessage(user.smspanelinfo, customers.all(), message)
        # try:
        #     sent_messages = client_sms.send_plain_next()
        # except SendSMSException as e:
        #     self.create_unsent_plain_sms(e, message, user, customers)
        #     raise APIException(e.status, e.message)
         
        # while sent_messages is not None:
         
        #     user.smspanelinfo.reduce_credit(calculate_total_sms_cost(sent_messages))
        #     SentSMS.objects.bulk_create([SentSMS(businessman=user, message_id=m['messageid'], receptor=m['receptor']) for m in sent_messages])
        #     try:
        #         sent_messages = client_sms.send_plain_next()
        #     except SendSMSException as e:
        #         self.create_unsent_plain_sms(e, message, user, customers)
        #         raise APIException(e.status, e.message)
        sms = SMSMessage.objects.create(message=message, businessman=user, message_type=SMSMessage.PLAIN, status=SMSMessage.PENDING)
        sms.receptors.set(customers)
        sms.save()

        

    def send_plain_sms_to_all(self, user: Businessman, message: str):

        # client_sms = ClientToAllCustomersSMSMessage(user, message)

        # try:
        #     sent_messages = client_sms.send_plain_next()
        # except SendSMSException as e:
        #     self.create_unsent_plain_sms(e, message, user, user.customers.all())
        #     raise APIException(e.status, e.message)

        # while sent_messages is not None:
            
        #     user.smspanelinfo.reduce_credit(calculate_total_sms_cost(sent_messages))
        #     SentSMS.objects.bulk_create([SentSMS(businessman=user, message_id=m['messageid'], receptor=m['receptor']) for m in sent_messages])
        #     try:
        #         sent_messages = client_sms.send_plain_next()
        #     except SendSMSException as e:
        #         self.create_unsent_plain_sms(e, message, user, user.customers.all())
        #         raise APIException(e.status, e.message)

        sms = SMSMessage.objects.create(message=message, businessman=user, message_type=SMSMessage.PLAIN)
        sms.receptors.set(user.customers.all())
        sms.save()


    def send_by_template(self, user: Businessman, receiver_customers: QuerySet, message_template: str):

        message_by_template = ClientBulkToCustomerSMSMessage(user.smspanelinfo, receiver_customers, message_template)


        try:
            sent_messages = message_by_template.send_bulk()
        except SendSMSException as e:
            self.create_unsent_template_sms(e, template, user, receiver_customers)
            raise APIException(e.status, e.message)

        while sent_messages is not None:
            user.smspanelinfo.reduce_credit(calculate_total_sms_cost(sent_messages))
            SentSMS.objects.bulk_create([SentSMS(businessman=user, message_id=m['messageid'], receptor=m['receptor']) for m in sent_messages])
            try:
                sent_messages = message_by_template.send_bulk()
            except SendSMSException as e:
                self.create_unsent_template_sms(e, template, user, receiver_customers)
                raise APIException(e.status, e.message)


    def send_by_template_to_all(self, user: Businessman, template: str):

        client_sms =ClientBulkToAllToCustomerSMSMessage(user, template)

        try:
            sent_messages = client_sms.send_bulk()
        except SendSMSException as e:
            self.create_unsent_template_sms(e, template, user, user.customers.all())
            raise APIException(e.status, e.message)
        
        while sent_messages is not None:
            user.smspanelinfo.reduce_credit(calculate_total_sms_cost(sent_messages))
            SentSMS.objects.bulk_create([SentSMS(businessman=user, message_id=m['messageid'], receptor=m['receptor']) for m in sent_messages])
            try:
                sent_messages = client_sms.send_bulk()
            except SendSMSException as e:
                self.create_unsent_template_sms(e, template, user, user.customers.all())
                raise APIException(e.status, e.message)


    def resend_unsent_plain_sms(self, user: Businessman, unsent_sms: UnsentPlainSMS):

        """
        deletes the unsent_plain_sms record the sends.
        this, prevents from multiple records for same message exist 
        in database. if any error occur during send message,
        new unsent_plain_sms will be created for the message again.
        "records must be updated in the client side when this method is called to prevent request for
        deleted record.
        """

        customers = unsent_sms.customers.all()
        UnsentPlainSMS.objects.filter(id=unsent_sms.id).delete()

        try:
            self.send_plain_sms(customers, user, unsent_sms.message)
        except APIException as e:
            raise e


    def resend_unsent_template_sms(self, user: Businessman, unsent_sms: UnsentTemplateSMS):

        """

        """

        customers = unsent_sms.customers.all()
        UnsentTemplateSMS.objects.filter(id=unsent_sms.id).delete()
        try:
            self.send_by_template(user, customers, unsent_sms.template)
        except APIException as e:
            raise e


    def send_video_upload_message(self, template: str, user: Businessman, **additional_context):

        client_sms = BulkMessageWithAdditionalContext(user, template, additional_context)

        try:
            sent_messages = client_sms.send_bulk()
        except SendSMSException as e:
            self.create_unsent_template_sms(e, template, user, user.customers.all())
            raise APIException(e.status, e.message)

        while sent_messages is not None:
            user.smspanelinfo.reduce_credit(calculate_total_sms_cost(sent_messages))
            SentSMS.objects.bulk_create(
                [SentSMS(businessman=user, message_id=m['messageid'], receptor=m['receptor']) for m in sent_messages])
            try:
                sent_messages = client_sms.send_bulk()
            except SendSMSException as e:
                self.create_unsent_template_sms(e, template, user, user.customers.all())
                raise APIException(e.status, e.message)
