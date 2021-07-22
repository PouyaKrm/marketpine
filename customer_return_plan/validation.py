from typing import Optional

from django.core.exceptions import ValidationError

from customer_return_plan.models import BaseDiscountSettings


def create_error(for_admin: bool, key: str, error_message: str) -> ValidationError:
    if for_admin:
        return ValidationError(error_message)
    else:
        return ValidationError({key: error_message})


def validate_discount_value_by_discount_type(for_admin: bool, discount_type: str, percent_off: Optional[int] = None,
                                             flat_rate_off: Optional[int] = None):
    percent_off_err = create_error(for_admin, 'percent_off', 'مقدار تخفیف درصدی باید بشتر از 0 باشد')
    flat_off_err = create_error(for_admin, 'flat_rate_off', 'مقدار تخفیف پولی باید بیشتر از 0 باشد')

    if discount_type == BaseDiscountSettings.DISCOUNT_TYPE_PERCENT and percent_off is not None and percent_off <= 0:
        raise percent_off_err
    elif discount_type == BaseDiscountSettings.DISCOUNT_TYPE_FLAT_RATE and flat_rate_off is not None and flat_rate_off <= 0:
        raise flat_off_err
