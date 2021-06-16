from django.core.exceptions import ValidationError
from django.forms.models import ModelForm

from customer_return_plan.festivals.models import Festival
from customer_return_plan.invitation.models import FriendInvitation
from customer_return_plan.models import Discount
from customer_return_plan.services import discount_service
from users.models import Businessman


class BaseReturnPlanForm(ModelForm):

    def _check_discount_used_any_where_else(self, discount: Discount, exclude_invitation: FriendInvitation = None,
                                            exclude_festival: Festival = None):

        used = discount_service.is_discount_used_anywhere_else(discount, exclude_festival, exclude_invitation)
        if used:
            raise ValidationError(
                'این تخفیف قبلا برای جای دیگری استفاده شده',
                code='invalid'
            )

    def _check_discount_blongs_to_businessman(self, discount: Discount, user: Businessman):
        if discount.businessman != user:
            raise ValidationError('تخفیف متعلق به بیزینس من دیگری است')

    def _check_discount_used_for(self, discount: Discount, used_for: str):

        if used_for == Discount.USED_FOR_FESTIVAL:
            err_message = 'کد تخفیف برای استفاده در جشنواره ثبت نشده'
        elif used_for == Discount.USED_FOR_INVITATION:
            err_message = 'کد تخفیف برای استفاده در معرفی دوست ثبت نشده'
        else:
            raise ValueError('invalid value for used_for field')

        if discount.used_for != used_for:
            raise ValidationError(err_message, code='invalid')

    def _check_discount_used_for_is_used_anywhere_belongs_to_businessman(self, discount: Discount, user: Businessman,
                                                                         used_for: str,
                                                                         exclude_festival: Festival = None,
                                                                         exclude_invitation: FriendInvitation = None):
        self._check_discount_used_for(discount, used_for)
        self._check_discount_used_any_where_else(discount, exclude_invitation, exclude_festival)
        self._check_discount_blongs_to_businessman(discount, user)
