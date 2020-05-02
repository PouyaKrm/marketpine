from django.db.models import Model
from rest_framework import serializers

from customers.serializers import CustomerReadIdListRepresentRelatedField
from users.models import Customer
from .models import BusinessmanGroups


class BusinessmanGroupsCreateListSerializer(serializers.ModelSerializer):
    customers = CustomerReadIdListRepresentRelatedField(many=True, required=False, write_only=True)

    class Meta:
        model = BusinessmanGroups
        fields = [
            'id',
            'title',
            'create_date',
            'customers_total',
            'customers'
        ]

    def validate_title(self, value):
        if not BusinessmanGroups.is_title_unique(value):
            raise serializers.ValidationError("عنوان یکتا نیست")
        return value

    def update(self, instance: BusinessmanGroups, validated_data):
        instance.set_title_customers(validated_data.get('title'), validated_data.get('customers'))
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
            'customers',
            'customers_total'
        ]

    def validate_title(self, value):
        if self.instance.title == value:
            return value
        return super().validate_title(value)

    def update(self, instance: BusinessmanGroups, validated_data):
        instance.set_title_customers(validated_data.get('title'), validated_data.get('customers'))
        return instance

    def create(self, validated_data):
        pass
