from django.db.models.base import Model
from django.template import TemplateSyntaxError
from rest_framework import serializers
from .models import SMSTemplate
from common.util import render_template


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
            render_template(value, {'name': 'test name'})

        except TemplateSyntaxError:
            raise serializers.ValidationError('invalid template')

        return value

    def create(self, validated_data: dict):

        return SMSTemplate.objects.create(businessman=self.context['user'], **validated_data)


