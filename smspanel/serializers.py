from django.db.models.base import Model
from django.template import TemplateSyntaxError
from rest_framework import serializers
from .models import SMSTemplate, SentSMS
from common.util import render_template, AVAILABLE_TEMPLATE_CONTEXT
from common.util.message import SMSMessage


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
            render_template(value, AVAILABLE_TEMPLATE_CONTEXT)

        except TemplateSyntaxError:
            raise serializers.ValidationError('invalid template')

        return value

    def create(self, validated_data: dict):

        return SMSTemplate.objects.create(businessman=self.context['user'], **validated_data)


class SentSMSSerializer(serializers.ModelSerializer):

    def send_plain(self, customers, content):

        receptors = ''

        for c in customers:
            receptors += c.phone + ", "

        sms = SMSMessage()

        return sms.send_message(receptor=receptors, message=content)

    def send_by_template(self, template, customers):
        context = AVAILABLE_TEMPLATE_CONTEXT
        context.update(business_name=self.context['user'].business_name)

        sms = SMSMessage()

        for c in customers:
            context.update(phone=c.phone, telegram_id=c.telegram_id, instagram_id=c.instagram_id)
            message = render_template(template, context)
            sms.send_message(receptor=c.phone, message=message)

        print(AVAILABLE_TEMPLATE_CONTEXT)

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

        obj = SentSMS.objects.create(businessman=user, is_plain_sms=is_plain, **validated_data)

        for c in customers:
            obj.customers.add(c)

        obj.save()

        return obj







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