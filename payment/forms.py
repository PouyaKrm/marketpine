from django.core.exceptions import ValidationError
from django.forms.models import ModelForm

from payment.models import PanelActivationPlans


class PanelActivationForm(ModelForm):

    class Meta:
        model = PanelActivationPlans
        exclude = [
            'duration'
        ]

    def clean_price_in_toman(self):
        val = self.cleaned_data.get('price_in_toman')
        if val < 10000:
            raise ValidationError('price must be bigger than 10000')
        return val

