from django.db.models import Model
from rest_framework import serializers

from users.models import Customer
from .models import BusinessmanGroups


class BusinessmanGroupsCreateListSerializer(serializers.ModelSerializer):

    customers_total = serializers.SerializerMethodField(read_only=True)

    class Meta:

        model = BusinessmanGroups
        fields = [
            'id',
            'title',
            'create_date',
            'customers_total',
        ]

    def get_customers_total(self, obj):
        return obj.customers.count()

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title')
        instance.save()
        return instance

    def create(self, validated_data):
        return BusinessmanGroups.objects.create(businessman=self.context['user'], **validated_data)



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


class BusinessmanGroupsRetrieveSerializer(serializers.ModelSerializer):


    class Meta:

        model = BusinessmanGroups
        fields = [
            'id',
            'title',
            'customers',
        ]
        extra_kwargs = {'title': {'read_only': True}}

    def validate_customers(self, value):

        user = self.context['user']

        result = all(el in user.customers.all() for el in value)

        if result:
            return value

        raise serializers.ValidationError('invalid customer entered')

    def update(self, instance: Model, validated_data):

        customers = validated_data.get('customers')

        for i in customers:
            instance.customers.add(i)
        instance.save()

        return instance

