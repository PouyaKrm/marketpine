from django.core.exceptions import ValidationError
from django.db.models.base import Model
from django.template import TemplateSyntaxError
from rest_framework import serializers

from common.util.custom_validators import validate_sms_message_length
from .models import SMSTemplate, SentSMS
from common.util.custom_templates import render_template, get_fake_context, render_template_with_customer_data
from common.util.sms_panel import SystemSMSMessage, ClientSMSMessage


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

        try:
            render_template(value, get_fake_context(self.context['user']))

        except TemplateSyntaxError:
            raise serializers.ValidationError('invalid template')

        validate_sms_message_length(value)

        return value

    def create(self, validated_data: dict):

        return SMSTemplate.objects.create(businessman=self.context['user'], **validated_data)


class SentSMSSerializer(serializers.ModelSerializer):

    content = serializers.CharField(validators=[validate_sms_message_length])

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

        user = self.context['user']

        result = all(el in user.customers.all() for el in value)

        if result:
            return value

        raise serializers.ValidationError('invalid customers')

    def create(self, validated_data: dict):

        user = self.context['user']
        is_plain = self.context['is_plain']

        customers = validated_data.pop('customers')

        if is_plain is True:
            self.send_plain(customers, validated_data.get('content'))

        else:
            self.send_by_template(validated_data.get('content'), customers)

        obj = SentSMS.objects.create(businessman=user **validated_data)


        for c in customers:
            obj.customers.add(c)

        obj.save()

        return obj


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
            'content',
            'is_plain_sms',
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
