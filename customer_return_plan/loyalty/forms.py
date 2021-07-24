from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from customer_return_plan.loyalty.models import CustomerLoyaltyDiscountSettings, CustomerLoyaltySettings
from customer_return_plan.validation import validate_discount_value_by_discount_type

max_settings_per_businessman = settings.LOYALTY_SETTINGS['MAX_SETTINGS_NUMBER_PER_BUSINESSMAN']


class CustomerLoyaltySettingsForm(forms.ModelForm):
    class Meta:
        model = CustomerLoyaltySettings
        fields = '__all__'

    def clean_is_active(self):
        is_active = self.cleaned_data.get('is_active')
        if (is_active and self.instance is None) or (is_active and self.instance.discount_settings.count() == 0):
            raise ValidationError('برای فعال کردن حداقل یک تخفیف را اول نتظیم کنید')

        return is_active


class CustomerLoyaltyDiscountSettingsAdminForm(forms.ModelForm):
    point = forms.IntegerField(min_value=1)

    class Meta:
        model = CustomerLoyaltyDiscountSettings
        fields = [
            'loyalty_settings',
            'point',
            'discount_type',
            'discount_code',
            'flat_rate_off',
            'percent_off'
        ]

    def clean_point(self):
        loyalty_settings = self.cleaned_data.get('loyalty_settings')
        point = self.cleaned_data.get('point')
        discount_settings = loyalty_settings.discount_settings
        if self.instance is not None:
            discount_settings = discount_settings.exclude(id=self.instance.id)
        exist = discount_settings.filter(point=point).exists()
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
        loyalty_settings = self.cleaned_data.get('loyalty_settings')
        discount_settings = loyalty_settings.discount_settings
        if self.instance is None and discount_settings.count() >= max_settings_per_businessman:
            raise ValidationError('حد اکثر تعداد تنطیمات تخفیف {} است'.format(max_settings_per_businessman))
        return self.cleaned_data
