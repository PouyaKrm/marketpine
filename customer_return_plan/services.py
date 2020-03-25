from django.utils import timezone
from strgen import StringGenerator
from customer_return_plan.invitation.models import FriendInvitation
from customer_return_plan.models import Discount
from users.models import Businessman, Customer


class DiscountService:

    def __generate_discount_code(self) -> str:
        return StringGenerator("[A-Za-z0-9]{8}").render()

    def is_discount_code_unique(self, user: Businessman, code: str) -> bool:
        exists = Discount.objects.filter(businessman=user, discount_code=code, expires=False).exists()
        if exists:
            return False
        exists = Discount.objects.filter(businessman=user, discount_code=code, expires=True,
                                         expire_date__gt=timezone.now()).exists()
        return not exists

    def generate_unique_code(self, user: Businessman):
        code = self.__generate_discount_code()
        while not self.is_discount_code_unique(user, code):
            code = self.__generate_discount_code()
        return code

    def create_discount(self, user: Businessman, expires: bool, discount_type: str,
                        auto_discount_code: bool, percent_off: float, flat_rate_off: int, discount_code=None,
                        expire_date=None) -> Discount:

        discount = Discount()
        discount.businessman = user
        if auto_discount_code:
            discount_code = self.generate_unique_code(user)
        discount.set_expire_date_if_expires(expires, expire_date)
        discount.set_discount_data(discount_code, discount_type, percent_off, flat_rate_off)
        discount.save()
        return discount

    def create_festival_discount(self, user: Businessman, expires: bool, discount_type: str,
                                 auto_discount_code: bool, percent_off: float, flat_rate_off: int, discount_code=None,
                                 expire_date=None) -> Discount:

        discount = self.create_discount(user, expires, discount_type, auto_discount_code, percent_off,
                                        flat_rate_off, discount_code, expire_date)
        discount.used_for = Discount.USED_FOR_FESTIVAL
        discount.save()
        return discount

    def create_invitation_discount(self, user: Businessman, expires: bool, discount_type: str,
                                   auto_discount_code: bool, percent_off: float, flat_rate_off: int, discount_code=None,
                                   expire_date=None) -> Discount:

        discount = self.create_discount(user, expires, discount_type, auto_discount_code, percent_off,
                                        flat_rate_off, discount_code, expire_date)
        discount.used_for = Discount.USED_FOR_INVITATION
        discount.save()
        return discount

    def update_discount(self, discount: Discount, user: Businessman, expires: bool,
                        discount_type: str, auto_discount_code: bool, percent_off: float, flat_rate_off: int,
                        discount_code=None, expire_date=None):
        discount.businessman = user
        if auto_discount_code:
            discount_code = self.generate_unique_code(user)
        discount.set_expire_date_if_expires(expires, expire_date)
        discount.set_discount_data(discount_code, discount_type, percent_off, flat_rate_off)
        discount.save()
        return discount

    def has_customer_any_discount(self, businessman: Businessman, customer: Customer) -> bool:

        has_discount = Discount.objects.filter(businessman=businessman,
                                               used_for=Discount.USED_FOR_FESTIVAL,
                                               expire_date__gt=timezone.now()).exclude(
            customers_used__id=customer.id).exists()
        if has_discount:
            return True

        has_discount = FriendInvitation.objects.filter(businessman=businessman, invited=customer, ) \
            .exclude(
            invited_discount__customers_used__id=customer.id
        ).exists()

        if has_discount:
            return True
        has_discount = FriendInvitation.objects.filter(businessman=businessman, inviter=customer) \
            .exclude(inviter_discount__customers_used__id=customer.id).exists()
        return has_discount

