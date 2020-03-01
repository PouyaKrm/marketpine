from django import forms

from panelprofile.models import SMSPanelStatus
from .models import SMSMessage


class SMSMessageForm(forms.ModelForm):

    class Meta:
        model = SMSMessage
        fields = '__all__'

    def clean(self):
        super().clean()
        businessman = self.cleaned_data.get('businessman')
        if businessman is None or not businessman.has_sms_panel or businessman.smspanelinfo.status == SMSPanelStatus.INACTIVE:
            raise forms.ValidationError('businessman has no sms panel or sms panel is inactive', code='error')

