from rest_framework import serializers
from .models import BusinessmanModulus

class BusinessmanModulusSerializer(serializers.ModelSerializer):

    module = serializers.StringRelatedField()

    class Meta:

        model = BusinessmanModulus
        fields = [
            'purchase_date',
            'expire_at',
            'module'
        ]
