from django.db import models

# Create your models here.
from users.models import BusinessmanManyToOneBaseModel, Customer


class BaseInvitationDiscountSettings(models.Model):
    DISCOUNT_TYPE_PERCENT = '0'
    DISCOUNT_TYPE_FLAT_RATE = '1'

    discount_type_choices = [
        (DISCOUNT_TYPE_PERCENT, 'Percent'),
        (DISCOUNT_TYPE_FLAT_RATE, 'Flat rate')
    ]
    discount_type = models.CharField(max_length=2, null=True, choices=discount_type_choices,
                                     default=DISCOUNT_TYPE_PERCENT)
    percent_off = models.FloatField(default=0)
    flat_rate_off = models.PositiveIntegerField(default=0)

    def is_percent_discount(self) -> bool:
        return self.discount_type == self.DISCOUNT_TYPE_PERCENT

    class Meta:
        abstract = True


class Discount(BusinessmanManyToOneBaseModel, BaseInvitationDiscountSettings):

    discount_code = models.CharField(max_length=20)
    expires = models.BooleanField(default=False)
    expire_date = models.DateTimeField(null=True, blank=True)
    customers_used = models.ManyToManyField(Customer, related_name="customers_used")

    def set_discount_data(self, is_percent_discount: bool, percent_off: float, flat_rate_off: int):
        if is_percent_discount:
            self.discount_type = Discount.DISCOUNT_TYPE_PERCENT
        else:
            self.discount_type = Discount.DISCOUNT_TYPE_FLAT_RATE

        self.percent_off = percent_off
        self.flat_rate_off = flat_rate_off

    def set_expire_date_if_expires(self, expire: bool, expire_date):
        if expire:
            self.expire_date = expire_date
        else:
            self.expire_date = None
