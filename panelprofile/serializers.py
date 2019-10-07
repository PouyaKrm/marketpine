from rest_framework import serializers
from .models import SMSPanelInfo
from django.conf import settings
from common.util.sms_panel import ClientManagement


class SMSPanelCreateSerializer(serializers.Serializer):

    password = serializers.CharField(min_length=8, max_length=16)

    def businessman(self, user):
        self.context['user'] = user

    def create(self, validated_data):

        user = self.context['user']

        data = {'username': 'bpe' + user.username, 'password': validated_data.get('password'), 'localid': user.id,
                'mininumallowedcredit': settings.MIN_CREDIT, 'credit': settings.INIT_CREDIT,
                'fullname': user.first_name + " " + user.last_name, 'planid': settings.SMS_PID,
                'mobile': user.phone, 'status': 0}

        client_manage = ClientManagement()

        result = client_manage.add(data)

        info = SMSPanelInfo()
        info.api_key = result['apikey']
        info.businessman = user
        info.status = '0'
        info.credit = result['remaincredit']
        info.sms_farsi_cost = result['smsfarsicost']
        info.sms_english_cost = result['smsenglishcost']
        info.username = result['username']

        info.save()

        return validated_data.get('password')


class SMSPanelInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = SMSPanelInfo
        read_only_fields = [
            'status',
            'minimum_allowed_credit',
            'credit'
        ]

