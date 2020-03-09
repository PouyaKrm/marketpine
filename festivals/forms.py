from django import forms
from django.core.exceptions import ValidationError

from panelprofile.models import SMSPanelStatus
from .models import Festival


class FestivalForm(forms.ModelForm):
    class Meta:
        model = Festival
        fields = '__all__'

    def clean(self):
        super().clean()
        businessman = self.cleaned_data.get('businessman')
        if businessman is not None and (not businessman.has_sms_panel or
                                        businessman.smspanelinfo.status != SMSPanelStatus.ACTIVE):
            raise ValidationError('businessman does not have active sms panel')
