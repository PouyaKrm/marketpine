from django.core.exceptions import ValidationError
from django.forms.models import ModelForm

from customer_return_plan.models import Discount
from customer_return_plan.services import discount_service


class BaseReturnPlanForm(ModelForm):

    def _check_discount_used_any_where_else(self, discount: Discount):
        used = discount_service.is_discount_used_anywhere_else(discount)
        if used:
            raise ValidationError(
                'این تخفیف قبلا برای جای دیگری استفاده شده',
                code='invalid'
            )
