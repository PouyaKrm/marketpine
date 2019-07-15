from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import Businessman
from .models import Festival


def validate_festival_name(value: str, user: Businessman):

    if user.festival_set.filter(name=value).exists():
        raise serializers.ValidationError('name of the festival must be unique')

    return value




class FestivalCreationSerializer(serializers.ModelSerializer):

    discount_code = serializers.CharField(min_length=8, max_length=12)

    class Meta:
        model = Festival
        fields = [
            'id',
            'name',
            'start_date',
            'end_date',
            'is_general',
            'discount_code',
            'percent_off',
            'flat_rate_off'
        ]


    def validate_name(self, value):

        return validate_festival_name(value, self.context['user'])




    def validate_start_date(self, value):

        if value < timezone.now().date():
            raise serializers.ValidationError('start date must be in present or future time')

        return value




    def validate_end_date(self, value):
        if value <= timezone.now().date():
            raise serializers.ValidationError('end date must be in future time')

        return value




    def validate(self, attrs):

        if attrs.get('start_date') >= attrs.get('end_date'):
            raise serializers.ValidationError({'end_date': ['end_date must be bigger than start_date']})

        return attrs



    def validate_percent_off(self, value):

        if not ((value > 0) and (value <= 100)):
            raise serializers.ValidationError('invalid value')

        return value



    def validate_discount_code(self, value):

        user = self.context['user']


        if user.festival_set.filter(end_date__gte=timezone.now(), discount_code=value).exists():
            raise serializers.ValidationError('discount code must be unique')

        return value


    def create(self, validated_data):

        return Festival.objects.create(businessman=self.context['user'], **validated_data)


class FestivalListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Festival
        fields = [
            'id',
            'name',
        ]





class RetrieveFestivalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Festival
        fields = [

            'id',
            'name',
            'start_date',
            'end_date',
            'is_general',
            'discount_code',
            'percent_off',
            'flat_rate_off'

        ]


    def validate_name(self, value):

        return validate_festival_name(value, self.context['user'])



    def update(self, instance: Festival, validated_data):

        instance.name = validated_data.get('name')

        instance.save()

        return instance
