from django.template import TemplateSyntaxError
from rest_framework import serializers

from base_app.serializers import BaseModelSerializerWithRequestObj
from common.util.custom_validators import sms_not_contains_link
from customers.serializers import CustomerReadIdListRepresentRelatedField
from .models import SMSTemplate, SentSMS, UnsentPlainSMS, UnsentTemplateSMS, SMSMessage, WelcomeMessage
from common.util.custom_templates import render_template, get_fake_context, render_template_with_customer_data
from .services import SMSMessageService
from django.conf import settings

persian_max_chars = settings.SMS_PANEL['PERSIAN_MAX_CHARS']
send_plain_max_customers = settings.SMS_PANEL['SEND_PLAIN_CUSTOMERS_MAX_NUMBER']
template_max_chars = settings.SMS_PANEL['TEMPLATE_MAX_CHARS']
template_min_chars = settings.SMS_PANEL['TEMPLATE_MIN_CHARS']
send_template_max_customers = settings.SMS_PANEL['SEND_TEMPLATE_MAX_CUSTOMERS']


class SMSTemplateSerializer(serializers.ModelSerializer):

    content = serializers.CharField(min_length=template_min_chars, max_length=template_max_chars, validators=[sms_not_contains_link])

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

    content = serializers.CharField(required=True, validators=[sms_not_contains_link])
    customers = serializers.ListField(child=serializers.IntegerField(min_value=1), required=True, min_length=1)

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

        customers = validated_data.get('customers')

        customers = user.customers.filter(id__in=customers).all()

        content = validated_data.get('content')

        messainger = SMSMessageService()

        messainger.send_plain_sms(customers, user, content)

        return validated_data


class SendPlainSMSToAllSerializer(serializers.Serializer):

    """
    a serializer to send same message to all customers of a businessman and saving the recieved 
    information from kavehnegar api
    """

    content = serializers.CharField(required=True, validators=[sms_not_contains_link])

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
        pass


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

        messanger = SMSMessageService()

        messanger.send_by_template(user, customers, template.content)
        
        return validated_data



class SentSMSSerializer(serializers.ModelSerializer):

    class Meta:
        model = SentSMS
        fields = [
            'message_id',
            'receptor',
            'cost',
            'date',
            'message'
        ]

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





class SendPlainToGroup(serializers.Serializer):

    content = serializers.CharField(required=True)

    def validate_content(self, value):

        if len(value) > persian_max_chars:
            raise serializers.ValidationError('طول متن پیام بیش از حد مجاز است')
        
        return value

    def create(self, validate_data: dict):

        user = self.context['user']
        group = self.context['group']
        message = validate_data.get('content')

        messanger = SMSMessageService()
        messanger.send_plain_sms(group.customers.all(), user, message)

        return validate_data


class SMSMessageListSerializer(serializers.ModelSerializer):

    class Meta:
        model = SMSMessage
        fields = [
            'id',
            'message',
            'create_date',
            'message_type',
            'status',
            'used_for'
        ]


class UnsentPlainSMSListSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnsentPlainSMS
        fields = [
            'id',
            'message',
            'create_date',
        ]


class UnsentTemplateSMSListSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnsentTemplateSMS
        fields = [
            'id',
            'template',
            'create_date',
        ]


class WelcomeMessageSerializer(BaseModelSerializerWithRequestObj):

    class Meta:

        model = WelcomeMessage
        fields = [
            'message',
            'send_message'
        ]

        extra_kwargs = {
            'message': {'required': True},
            'send_message': {'required': True}
        }
