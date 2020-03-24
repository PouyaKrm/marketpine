from django.utils import timezone
from strgen import StringGenerator

from customer_return_plan.models import Discount
from users.models import Businessman


class DiscountService:

    def __generate_discount_code(self)-> str:
        return StringGenerator("[A-Za-z0-9]{8}").render()

    def is_discount_code_unique(self, user: Businessman, code: str) -> bool:
        exists = Discount.objects.filter(businessman=user, discount_code=code, expires=False).exists()
        if not exists:
            return True
        exists = Discount.objects.filter(businessman=user, discount_code=code, expires=True, expire_date__gt=timezone.now()).exists()
        return not exists


    def generate_unique_code(self, user: Businessman):
        code = self.__generate_discount_code()
        while not self.is_discount_code_unique(user, code):
            code = self.__generate_discount_code()
        return code

    def create_discount_auto_code(self, user: Businessman, is_percent_discount: bool,
                                  percent_off: float, flat_rate_off: int, expires: bool, expire_date=None) -> Discount:
        discount = Discount()
        discount.businessman = user
        discount.discount_code = self.generate_unique_code(user)
        discount.set_expire_date_if_expires(expires, expire_date)
        discount.set_discount_data(is_percent_discount, percent_off, flat_rate_off)
        discount.save()
        return discount
