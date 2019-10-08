from rest_framework import serializers
from .models import SMSPanelInfo, BusinessmanAuthDocs
from django.conf import settings
from common.util.custom_validators import pdf_file_validator
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


class AuthFormSerializer(serializers.ModelSerializer):

    form = serializers.FileField(max_length=40, validators=[pdf_file_validator])
    class Meta:
        model = BusinessmanAuthDocs
        fields = [
            'form'
        ]

    def update(self, instance: BusinessmanAuthDocs, validated_data: dict):

        """
        deletes previous file form if exist and saves new one
        :param instance: BusinessmanAuthDocs
        :param validated_data: contains new form
        :return:
        """
        if instance.form.name is not None:
            instance.form.delete()

        instance.form = validated_data.get('form')
        instance.save()
        return instance


class AuthNationalCardSerializer(serializers.ModelSerializer):

    national_card = serializers.ImageField(max_length=40)
    class Meta:
        model = BusinessmanAuthDocs
        fields = [
            'national_card'
        ]

    def update(self, instance: BusinessmanAuthDocs, validated_data: dict):

        if instance.national_card.name is not None:
            instance.form.delete()

        instance.national_card = validated_data.get('national_card')
        instance.save()
        return instance


class AuthBirthCertificateSerializer(serializers.ModelSerializer):

    birth_certificate = serializers.ImageField(max_length=40)

    class Meta:
        model = BusinessmanAuthDocs
        fields = [
            'birth_certificate'
        ]

    def update(self, instance: BusinessmanAuthDocs, validated_data):

        # if instance.birth_certificate.name is not None:
        #     instance.birth_certificate.delete()
        #

        if instance.birth_certificate.name is not None:
            instance.delete()
        instance.birth_certificate = validated_data.get('birth_certificate')

        instance.save()

        return instance

class SMSPanelInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = SMSPanelInfo
        read_only_fields = [
            'status',
            'minimum_allowed_credit',
            'credit'
        ]

