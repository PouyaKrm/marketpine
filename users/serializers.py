from django.core.validators import RegexValidator
from rest_framework import serializers, validators

from users.message import SMSMessage
from .models import Salesman, VerificationCodes
import re, secrets, datetime

PhonenumberValidator = RegexValidator(regex=r'^\+?1?\d{11, 12}$',
                                      message="Phone number must be entered in the format: '+999999999'."
                                              " Up to 15 digits allowed.")


def phone_validator(value):

    result = re.match("^(\\+98|0)9\\d{9}$", value)

    if result is None:
        raise serializers.ValidationError("phone number is invalid")


class SalespersonRegisterSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(min_length=8, max_length=16, style={'input_type': 'password', 'write_only': True})
    password = serializers.CharField(min_length=8, max_length=16, style={'input_type': 'password', 'write_only': True})
    email = serializers.EmailField(validators=[
        validators.UniqueValidator(queryset=Salesman.objects.all(), message="this email address is already taken")])
    phone = serializers.CharField(max_length=15, validators=[phone_validator, validators.UniqueValidator(queryset=Salesman.objects.all(), message="phone number must be unique")])

    class Meta:
        model = Salesman
        fields = [

            'username',
            'password',
            'password2',
            'first_name',
            'last_name',
            'address',
            'phone',
            'email',
            'business_name'
        ]

    def validate(self, attrs):

        password2 = attrs.get('password2')
        del attrs['password2']
        password = attrs.get('password')

        if password != password2:

            raise serializers.ValidationError({'password2': ['passwords must match']})

        return attrs

    def create(self, validated_data):

        user = Salesman(**validated_data)
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

        expire_time = datetime.datetime.now() + datetime.timedelta(seconds=30)

        VerificationCodes.objects.create(businessman=user, code=code, expiration_time=expire_time)

        SMSMessage().send_verification_code(receptor=user.phone, code=code)

        return user


class SalesmanPasswordResetSerializer(serializers.ModelSerializer):

    old_password = serializers.CharField(min_length=8, max_length=16,
                                         style={'input_type': 'password', 'write_only': True})

    new_password = serializers.CharField(min_length=8, max_length=16,
                                         style={'input_type': 'password', 'write_only': True})

    new_password2 = serializers.CharField(min_length=8, max_length=16,
                                         style={'input_type': 'password', 'write_only': True})

    class Meta:

        model = Salesman
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



class SalesmanSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(max_length=15, validators=[phone_validator])

    class Meta:

        model = Salesman
        fields = [
            'username',
            'first_name',
            'last_name',
            'address',
            'phone',
            'email',
            'business_name',
            'bot_access',
            'instagram_access'
        ]

        extra_kwargs = {'username': {'read_only': True}, 'bot_access': {'read_only': True},
                        'instagram_access': {'read_only': True}}

    def validate_phone(self, value):

        logged_in_user = self.context['request'].user

        users_num = Salesman.objects.all().filter(phone=value).exclude(id=logged_in_user.id).count()

        if users_num is not 0:
            raise serializers.ValidationError('this phone number is already taken')

        return value

    # def validate_email(self, value):

    def validate_email(self, value):

        logged_in_user = self.context['request'].user

        users_num = Salesman.objects.all().filter(email=value).exclude(id=logged_in_user.id).count()

        if users_num is not 0:
            raise serializers.ValidationError('this email address is already taken')

        return value

    def update(self, instance, validated_data):

        phone = validated_data.pop('phone')

        for key, value in validated_data.items():

            setattr(instance, key, value)

        instance.save()

        return instance



