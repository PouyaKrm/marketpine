from django.core.validators import RegexValidator
from rest_framework import serializers, validators
from django.contrib.auth.base_user import BaseUserManager
from common.util.sms_panel.message import SystemSMSMessage
from .models import Businessman, VerificationCodes, BusinessCategory
import secrets, datetime
from django.conf import settings
import os
from common.util.custom_validators import validate_logo_size, password_validator, phone_validator

PhonenumberValidator = RegexValidator(regex=r'^\+?1?\d{11, 12}$',
                                      message="Phone number must be entered in the format: '+999999999'."
                                              " Up to 15 digits allowed.")


class BusinessmanRegisterSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(min_length=8, max_length=16, style={'input_type': 'password', 'write_only': True})
    password = serializers.CharField(min_length=8, max_length=16, style={'input_type': 'password', 'write_only': True},
                                     validators=[password_validator])
    email = serializers.EmailField(validators=[
        validators.UniqueValidator(queryset=Businessman.objects.all(), message="this email address is already taken")])
    phone = serializers.CharField(max_length=15, validators=[validators.UniqueValidator(queryset=Businessman.objects.all(), message="phone number must be unique")])
    business_category = serializers.PrimaryKeyRelatedField(required=True, queryset=BusinessCategory.objects.all())

    class Meta:
        model = Businessman
        fields = [

            'username',
            'password',
            'password2',
            'first_name',
            'last_name',
            'phone',
            'email',
            'business_name',
            'business_category'
        ]

    def validate(self, attrs):

        password2 = attrs.get('password2')
        del attrs['password2']
        password = attrs.get('password')

        if password != password2:

            raise serializers.ValidationError({'password2': ['passwords must match']})

        return attrs

    def create(self, validated_data):

        user = Businessman(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = True
        user.save()

        code = secrets.randbelow(10000)

        if code < 10000:
            code += 10000

        while VerificationCodes.objects.filter(code=code).count() > 0:

            code = secrets.randbelow(10000)

            if code < 10000:
                code += 10000

        expire_time = datetime.datetime.now() + datetime.timedelta(hours=24)

        VerificationCodes.objects.create(businessman=user, code=code, expiration_time=expire_time)

        SystemSMSMessage().send_verification_code(receptor=user.phone, code=code)

        return user
        

class BusinessmanPasswordResetSerializer(serializers.ModelSerializer):

    old_password = serializers.CharField(min_length=8, max_length=16,
                                         style={'input_type': 'password', 'write_only': True})

    new_password = serializers.CharField(min_length=8, max_length=16,
                                         style={'input_type': 'password', 'write_only': True}, validators=[password_validator])

    new_password2 = serializers.CharField(min_length=8, max_length=16,
                                         style={'input_type': 'password', 'write_only': True})

    class Meta:

        model = Businessman
        fields = [
            'old_password',
            'new_password',
            'new_password2'
        ]

    def validate(self, validated_data):

        new_pass = validated_data.get('new_password')
        new_pass2 = validated_data.pop('new_password2')

        if new_pass != new_pass2:
            raise serializers.ValidationError({'new_password2': ['passwords must match']})

        return validated_data

    def update(self, instance, validated_data):

        instance.set_password(validated_data.get('new_password'))

        instance.save()

        return instance


class BusinessmanForgetPasswordSerializer(serializers.ModelSerializer):

    # phone = serializers.CharField(max_length=15, validators=[phone_validator])

    username = serializers.CharField(max_length=150)

    class Meta:

        model = Businessman
        fields = [
            'username',
            'phone'
        ]



    def update(self, instance, validated_data):

        new_password = BaseUserManager().make_random_password(length=8)

        SystemSMSMessage().send_new_password(instance.phone, new_password)

        instance.set_password(new_password)

        instance.save()

        return instance


class BusinessmanLoginSerializer(serializers.ModelSerializer):

    username = serializers.CharField(max_length=40)

    class Meta:

        model = Businessman

        fields = [
            'username',
            'password'
        ]

        extra_kwargs = {'password': {'write_only': True}}


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessCategory
        fields = [
            'name',
            'id'
        ]
