from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import ModelForm

from payment.models import SubscriptionPlan, Wallet


class PanelActivationForm(ModelForm):

    class Meta:
        model = SubscriptionPlan
        exclude = [
            'duration'
        ]

    def clean_price_in_toman(self):
        val = self.cleaned_data.get('price_in_toman')
        if val < 1000:
            raise ValidationError('price must be bigger than 10000')
        return val


class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = '__all__'

    def clean_subscription_start(self):
        has = self.cleaned_data.get('has_subscription')
        start = self.cleaned_data.get('subscription_start')

        if has and start is None:
            raise ValidationError("تاریخ شروع باید مقدار داشته باشد")
        return start

    def clean_subscription_end(self):
        has = self.cleaned_data.get('has_subscription')
        start = self.cleaned_data.get('subscription_start')
        end = self.cleaned_data.get('subscription_end')

        if has and end is None:
            raise ValidationError("تاریخ پایان باید مقدار داشته باشد")

        if end <= start:
            raise ValidationError("تاریخ پایان باید بزرگتر از تاریخ شروع باشد")

        return end
