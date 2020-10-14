import ast

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model
from django.conf import settings
from rest_framework import serializers

from customers.serializers import CustomerReadIdListRepresentRelatedField
from users.models import Customer
from .models import BusinessmanGroups

page_size = settings.PAGINATION_PAGE_NUM

class BusinessmanGroupsCreateListSerializer(serializers.ModelSerializer):
    customers = CustomerReadIdListRepresentRelatedField(many=True, required=False, write_only=True)

    class Meta:
        model = BusinessmanGroups
        fields = [
            'id',
            'title',
            'create_date',
            'customers_total',
            'customers',
            'type',
        ]

        extra_kwargs = {'type': {'read_only': True}}

    def validate_title(self, value):
        user = self.context['user']
        if not BusinessmanGroups.is_title_unique(user, value):
            raise serializers.ValidationError("عنوان یکتا نیست")
        return value

    def update(self, instance: BusinessmanGroups, validated_data):
        instance.set_title(validated_data.get('title'), validated_data.get('customers'))
        return instance

    def create(self, validated_data):
        return BusinessmanGroups.create_group(self.context['user'], validated_data.get('title'),
                                              validated_data.get('customers'))


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'id',
            'phone',
            'full_name',
            'telegram_id',
            'instagram_id'
        ]


class BusinessmanGroupsRetrieveSerializer(BusinessmanGroupsCreateListSerializer):
    customers = CustomerReadIdListRepresentRelatedField(many=True, required=False)

    class Meta:
        model = BusinessmanGroups
        fields = [
            'id',
            'title',
            'customers_total',
            'type'
        ]

        extra_kwargs = {'type': {'read_only': True}}

    def validate_title(self, value):
        if self.instance.title == value:
            return value
        return super().validate_title(value)

    def update(self, instance: BusinessmanGroups, validated_data):
        instance.set_title(validated_data.get('title'))
        return instance

    def create(self, validated_data):
        pass


class BusinessmanGroupAddDeleteMemberSerializer(serializers.Serializer):

    customers = CustomerReadIdListRepresentRelatedField(required=True, many=True)

    class Meta:
        fields = [
            'customer'
        ]

    def validate_customers(self, value):
        if len(value) > page_size:
            raise serializers.ValidationError('max customers length is {}'.format(page_size))
        return value


