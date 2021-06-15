from django.core.exceptions import ValidationError

from customer_return_plan.forms import BaseReturnPlanForm
from customer_return_plan.invitation.models import FriendInvitation
from customer_return_plan.models import Discount


class CreateChangeInvitationForm(BaseReturnPlanForm):
    class Meta:
        model = FriendInvitation
        fields = '__all__'

    def clean_inviter(self):
        inviter = self.cleaned_data.get('inviter')
        businessman = self.cleaned_data.get('businessman')
        if inviter.businessman != businessman:
            raise ValidationError(
                'فرد معرف  باید عضو بیزینس منی باشید که صاحب این معرفی دوست است',
                code='invalid'
            )
        return inviter

    def clean_invited(self):
        invited = self.cleaned_data.get('invited')
        businessman = self.cleaned_data.get('businessman')
        if invited.businessman != businessman:
            raise ValidationError(
                'فرد معرفی شده باید عضو بیزینس منی باشید که صاحب این معرفی دوست است',
                code='invalid'
            )
        return invited

    def clean_inviter_discount(self):
        d = self.cleaned_data.get('inviter_discount')
        businessman = self.cleaned_data.get('businessman')
        self._check_discount_used_any_where_else(d)
        if d.used_for != Discount.USED_FOR_INVITATION:
            raise ValidationError(
                'نوع تخفیف باید معرفی دوست باشد',
                code='invalid'
            )

        if d.businessman != businessman:
            raise ValidationError(
                'بیزینس من صاحب تخیفیف با بیزینس من دازنده این معرفی دوست باید یکسان باشد',
                code='invalid'
            )
        return d

    def validate_invited_discount(self):

        d = self.cleaned_data.get('invited_discount')
        self._check_discount_used_any_where_else(d)
        businessman = self.cleaned_data.get('businessman')

        if d.used_for != Discount.USED_FOR_INVITATION:
            raise ValidationError(
                'نوع تخفیف باید معرفی دوست باشد',
                code='invalid'
            )

        if d.businessman != businessman:
            raise ValidationError(
                'بیزینس من صاحب تخیفیف با بیزینس من دازنده این معرفی دوست باید یکسان باشد',
                code='invalid'
            )
        return d

    def clean(self):
        inviter = self.cleaned_data.get('inviter')
        invited = self.cleaned_data.get('invited')
        inviter_discount = self.cleaned_data.get('inviter_discount')
        invited_discount = self.cleaned_data.get('invited_discount')

        if invited == inviter:
            raise ValidationError('معرف و معرفی کننده نباید یک شخص باشند')

        if inviter_discount == invited_discount:
            raise ValidationError('تخفیف معرف و معرفی کننده نباید یکسان باشند')

        return self.cleaned_data
