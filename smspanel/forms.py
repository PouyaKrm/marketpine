from django import forms

from panelprofile.models import SMSPanelStatus
from panelprofile.services import sms_panel_info_service
from .models import SMSMessage


class SMSMessageForm(forms.ModelForm):

    class Meta:
        model = SMSMessage
        fields = '__all__'

    def clean(self):
        super().clean()
        businessman = self.cleaned_data.get('businessman')
        has_panel_and_is_active = sms_panel_info_service.fetch_panel_and_check_is_active(businessman)
        if not has_panel_and_is_active:
            raise forms.ValidationError('کاربر پنل پیامک ندارد یا پنل پیامکش غیر فعال است', code='error')

