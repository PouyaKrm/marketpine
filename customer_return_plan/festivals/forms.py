from django.core.exceptions import ValidationError

from panelprofile.services import sms_panel_info_service
from .models import Festival
from ..forms import BaseReturnPlanForm
from ..models import Discount


class FestivalForm(BaseReturnPlanForm):
    class Meta:
        model = Festival
        fields = '__all__'

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        businessman = self.cleaned_data.get('businessman')
        self._check_discount_used_for_is_used_anywhere_belongs_to_businessman(
            discount,
            businessman,
            Discount.USED_FOR_FESTIVAL
        )
        return discount

    def clean(self):
        super().clean()
        businessman = self.cleaned_data.get('businessman')
        has_sms_panel = sms_panel_info_service.has_sms_panel(businessman)
        if not has_sms_panel:
            raise ValidationError('بیزینس من پنل اسمس ندارد')
        panel = sms_panel_info_service.get_buinessman_sms_panel(businessman)
        if panel.is_status_disabled():
            raise ValidationError('پنل اسمس بیزینس من فعال نیست')
        return self.cleaned_data
