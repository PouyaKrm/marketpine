from django import forms
from django.core.exceptions import ValidationError

from mobile_app_conf.models import MobileAppPageConf
from mobile_app_conf.services import mobile_page_conf_service


class MobileAppPageConfForm(forms.ModelForm):

    class Meta:
        model = MobileAppPageConf
        fields = '__all__'

    def clean_working_time_to(self):
        working_from = self.cleaned_data.get('working_time_from')
        working_to = self.cleaned_data.get('working_time_to')

        if working_from is not None and working_to is not None and working_to <= working_from:
            raise ValidationError('ساعت پایان کار وارد شده اشتباه و باید بزرگتر از ساعت شروع به کار باشد')
        return self.cleaned_data

    def clean_page_id(self):
        page_id = self.cleaned_data.get('page_id')
        user = self.cleaned_data.get('businessman')
        if not mobile_page_conf_service.is_page_id_pattern_valid(page_id):
            raise ValidationError('فرمت اشتباه')
        elif not mobile_page_conf_service.is_page_id_unique(user, page_id):
            raise ValidationError('این آیدی صفحه قبلا استفاده شده')
        elif mobile_page_conf_service.is_page_id_predefined(page_id):
            raise ValidationError('آیدی غیر مجاز')
        return page_id

    def clean_instagram_page_url(self):
        url = self.cleaned_data.get('instagram_page_url')
        mobile_page_conf_service.check_instagram_page_url_is_valid(url)
        return url

