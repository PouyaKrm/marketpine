from django.template.exceptions import TemplateSyntaxError
from rest_framework import serializers
from .models import PanelSetting
from common.util.custom_templates import render_template, get_fake_context


class PanelSettingSerializer(serializers.ModelSerializer):

    class Meta:

        model = PanelSetting
        fields = [
            'welcome_message'
        ]

    def validate_welcome_message(self, value):

        user = self.context['user']

        try:
            render_template(value, get_fake_context(user))

        except TemplateSyntaxError:
            raise serializers.ValidationError("invalid template")

        return value
