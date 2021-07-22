from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from customer_return_plan.loyalty.models import CustomerLoyaltyDiscountSettings
from customer_return_plan.loyalty.services import LoyaltyService
from customer_return_plan.validation import validate_discount_value_by_discount_type

max_settings_per_businessman = settings.LOYALTY_SETTINGS['MAX_SETTINGS_NUMBER_PER_BUSINESSMAN']


class CustomerLoyaltyAdminForm(forms.ModelForm):
    class Meta:
        model = CustomerLoyaltyDiscountSettings
        fields = '__all__'

    def clean_point(self):
        businessman = self.cleaned_data.get('businessman')
        point = self.cleaned_data.get('point')
        points = LoyaltyService.get_instance().get_businessman_loyalty_settings(businessman)
        if self.instance is not None:
            points = points.exclude(id=self.instance.id)
        exist = points.filter(point=point).exists()
        if exist:
            raise ValidationError('تنظیمات دیگری با این امتیاز ثبت شده')
        return point

    def clean_percent_off(self):
        discount_type = self.cleaned_data.get('discount_type')
        percent_off = self.cleaned_data.get('percent_off')
        validate_discount_value_by_discount_type(True, discount_type, percent_off)
        return percent_off

    def clean_flat_rate_off(self):
        discount_type = self.cleaned_data.get('discount_type')
        flat_rate_off = self.cleaned_data.get('flat_rate_off')
        validate_discount_value_by_discount_type(True, discount_type, None, flat_rate_off)
        return flat_rate_off

    def clean(self):
        super().clean()
        businessman = self.cleaned_data.get('businessman')
        settings = LoyaltyService.get_instance().get_businessman_loyalty_settings(businessman)
        if self.instance is None and settings.count() >= max_settings_per_businessman:
            raise ValidationError('حد اکثر تعداد تنطیمات تخفیف {} است'.format(max_settings_per_businessman))
        return self.cleaned_data
