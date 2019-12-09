from django.core.exceptions import ValidationError
from django.db.models.base import Model
from django.template import TemplateSyntaxError
from rest_framework import serializers

from common.util.custom_validators import validate_sms_message_length
from .models import SMSTemplate, SentSMS, UnsentPlainSMS, UnsentTemplateSMS
from common.util.custom_templates import render_template, get_fake_context, render_template_with_customer_data
from common.util.sms_panel.message import SystemSMSMessage, ClientSMSMessage, ClientToAllCustomersSMSMessage, ClientBulkSMSMessage
from common.util.sms_panel.client import ClientManagement
from common.util.sms_panel.exceptions import SendSMSException
from common.util.kavenegar_local import APIException

from users.models import Businessman

from django.conf import settings

persian_max_chars = settings.SMS_PANEL['PERSIAN_MAX_CHARS']
send_plain_max_customers = settings.SMS_PANEL['SEND_PLAIN_CUSTOMERS_MAX_NUMBER']
template_max_chars = settings.SMS_PANEL['TEMPLATE_MAX_CHARS']
send_template_max_customers = settings.SMS_PANEL['SEND_TEMPLATE_MAX_CUSTOMERS']

def create_unsent_plain_sms(ex: SendSMSException, content: str, user: Businessman):
    resend_start = ex.failed_on
    resend_end = ex.resend_last

    if resend_start is not None and resend_end is not None:
        UnsentPlainSMS.objects.create(businessman=user, message=content, resend_start=resend_start.id, resend_stop=resend_end.id)
    elif resend_start is not None:
        UnsentPlainSMS.objects.create(businessman=user, message=content, resend_start=resend_start.id)


class SMSTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = SMSTemplate
        fields = [
            'id',
            'title',
            'create_date',
            'content'
        ]

    def validate_content(self, value):

        if len(value) > template_max_chars:
            raise serializers.ValidationError('طول قالب بیش از حد مجاز است')

        try:
            render_template(value, get_fake_context(self.context['user']))

        except TemplateSyntaxError:
            raise serializers.ValidationError('invalid template')

        return value

    def create(self, validated_data: dict):

        return SMSTemplate.objects.create(businessman=self.context['user'], **validated_data)


class SendSMSSerializer(serializers.ModelSerializer):

    content = serializers.CharField(required=True)

    customers = serializers.ListField(child=serializers.IntegerField(min_value=1), required=True, min_length=1)

    def send_plain(self, customers, content):

        user = self.context['user']

        receptors = ''

        for c in customers:
            receptors += c.phone + ", "

        sms = ClientSMSMessage(user.smspanelinfo)

        return sms.send_message(receptor=receptors, message=content)

    def send_by_template(self, template, customers):

        message_ids = []
        user = self.context['user']
        sms = ClientSMSMessage(user.smspanelinfo)

        for c in customers:
            message = render_template_with_customer_data(template, c)
            try:
                validate_sms_message_length(message)
                message_ids.append(sms.send_message(receptor=c.phone, message=message))
            except ValidationError:
                pass

        return message_ids


    class Meta:

        model = SentSMS
        fields = [
            'content',
            'customers'
        ]

    def validate_customers(self, value):

        if len(value) > send_plain_max_customers:
            raise serializers.ValidationError("تعداد دریافت کنندگان بیش از حد مجاز است")

        return value

    def validate_content(self, value):
        if(len(value) > persian_max_chars):
            raise serializers.ValidationError("طول پیام بیش از حئ مجاز است")
        return value


    def create(self, validated_data: dict):

        user = self.context['user']

        customers = validated_data.pop('customers')

        client_message = ClientSMSMessage(user.smspanelinfo)

        customers = user.customers.filter(id__in=customers).all()

        content = validated_data.get('content')

        try:
            sent_messages = client_message.send_plain(customers, content)
        except SendSMSException as e:
            
            create_unsent_plain_sms(e, content, user)
            raise APIException(e.status, e.message)


        obj = SentSMS.objects.bulk_create([SentSMS(businessman=user, message_id=m['messageid'], receptor=m['receptor']) for m in sent_messages])

        return obj


class SendPlainSMSToAllSerializer(serializers.Serializer):

    """
    a serializer to send same message to all customers of a businessman and saving the recieved 
    information from kavehnegar api
    """

    content = serializers.CharField(required=True)

    class Meta:
        fields = [
            'content'
        ]

    def validate_content(self, value):

        """
        Validates that length of the content is valid or not.
        :raises ValidationError if length is too big
        :retuns contents
        """

        if len(value) > persian_max_chars:
            raise serializers.ValidationError("طول پیام بیش از حد مجاز است")

        return value

    def create(self, validated_data: dict):

        """
        send message to customers and saves message_id that is retrieved from kavehnegar api
        :raises APIException if kavehnegar api does not accept the send of the message
        :raises HTTPException if an error occur during http request
        :returns content
        """

        user = self.context['user']
        content = validated_data.get('content')
        client_sms = ClientToAllCustomersSMSMessage(user, content)

        try:
            sent_messages = client_sms.send_plain_next()
        except SendSMSException as e:
            create_unsent_plain_sms(e, content, user)
            raise APIException(e.status, e.message)

        while sent_messages is not None:

            SentSMS.objects.bulk_create([SentSMS(businessman=user, message_id=m['messageid'], receptor=m['receptor']) for m in sent_messages])
            try:
                sent_messages = client_sms.send_plain_next()
            except SendSMSException as e:
                create_unsent_plain_sms(e, content, user)
                raise APIException(e.status, e.message)
        
        return content


def create_unsent_template_sms(e: SendSMSException, template: str, businessman: Businessman):

    resend_stop = e.resend_last
    resend_start = e.failed_on

    if resend_stop is not None:
        UnsentTemplateSMS.objects.create(businessman=businessman, resend_start=e.failed_on.id,
        resend_stop=resend_stop.id, template=template)
    else:
        UnsentTemplateSMS.objects.create(businessman=businessman, resend_start=e.failed_on.id,
        template=template)


class SendByTemplateSerializer(serializers.Serializer):

    """
    sends sms message to specific number ofcustomers and creates their records in the database.
    """

    customers = serializers.ListField(child=serializers.IntegerField(min_value=1), min_length=1, required=True)

    class Meta:
        fields = [
            'customers'
        ]

    def validate_customers(self, value):

        if len(value) > send_template_max_customers:
            raise serializers.ValidationError("طول گیرنده ها بیش از حد مجاز است")

        return value
    
    def create(self, validated_data: dict):

        """
        sends sms message by a template and creates records of sent messages in the database.
        :raises APIException if kavehnegar api does not accept the send of the message
        :raises HTTPException if an error occur during http request
        :return: customers
        """

        user = self.context['user']
        customers = user.customers.filter(id__in=validated_data.get('customers')).all()
        template = self.context['template']

        message_by_template = ClientBulkSMSMessage(user.smspanelinfo, customers, template.content)

        try:
            sent_messages = message_by_template.send_bulk()
        except SendSMSException as e:
            create_unsent_template_sms(e, template.content, user)
            raise APIException(e.status, e.message)

        while sent_messages is not None:

            SentSMS.objects.bulk_create([SentSMS(businessman=user, message_id=m['messageid'], receptor=m['receptor']) for m in sent_messages])
            try:
                sent_messages = message_by_template.send_bulk()
            except SendSMSException as e:
                create_unsent_template_sms(e, template.content, user)
                raise APIException(e.status, e.message)
        
        return validated_data




class SentSMSRetrieveForCustomer(serializers.ModelSerializer):

    rendered_content = serializers.SerializerMethodField(read_only=True)

    def get_rendered_content(self, obj: SentSMS):

        if not obj.is_plain_sms:

            return render_template_with_customer_data(obj.content, self.context['customer'])

        return None

    class Meta:

        model = SentSMS
        fields = [
            'id',
            'rendered_content',
        ]










#
# class CustomerSentSMSSerializer(serializers.ModelSerializer):
#
#     class Meta:
#
#         model = CustomerSentSMS
#         fields = [
#             'customer',
#             'sent_date'
#         ]
#
#     def create(self, validated_data: dict):
#
#         businessman = self.context['businessman']
#         sms = SentSMS.objects.create(businessman=businessman, **validated_data)
