from django.template.exceptions import TemplateSyntaxError
from rest_framework import serializers
from .models import PanelSetting
from common.util.custom_templates import render_template, get_fake_context, CustomerTemplate


class PanelSettingSerializer(serializers.ModelSerializer):

    class Meta:

        model = PanelSetting
        fields = [
            'welcome_message',
            'send_welcome_message'
        ]

        extra_kwargs = {
            'send_welcome_message': {'required': True}
        }

    def validate_welcome_message(self, value):

        user = self.context['user']

        template = CustomerTemplate(user, value)

        try:
            template.validate_welcome_template()

        except TemplateSyntaxError:
            raise serializers.ValidationError("invalid template")

        return value

