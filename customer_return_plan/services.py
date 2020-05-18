from django.core.exceptions import ObjectDoesNotExist
from django.db.models.aggregates import Sum
from django.db.models.query_utils import Q
from django.utils import timezone
from strgen import StringGenerator

from customer_return_plan.festivals.models import Festival
from customer_return_plan.invitation.models import FriendInvitation
from customer_return_plan.models import Discount
from customerpurchase.models import CustomerPurchase
from customers.services import CustomerService
from users.models import Businessman, Customer

customer_service = CustomerService()


class DiscountService:

    def __init__(self):
        self.customer_service = CustomerService()

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

    def discount_exists_by_discount_code(self, businessman: Businessman, discount_code: str) -> bool:
        exists = Discount.objects.filter(
            Q(businessman=businessman, expires=False, discount_code=discount_code)
            | Q(businessman=businessman, expires=True, expire_date__gt=timezone.now(), discount_code=discount_code)
        ).exists()

        return exists

    def can_customer_use_discount(self, businessman: Businessman, discount_code: str, customer: Customer) -> bool:

        discount = Discount.objects.get(discount_code=discount_code)

        if discount.purchases.filter(customer=customer).exists():
            return False

        # if discount.used_for == Discount.USED_FOR_FESTIVAL and \
        #         discount.customers_used.filter(phone=customer.phone).exists():
        #     return False

        discount_for_invited_query = FriendInvitation.objects.filter(businessman=businessman, invited=customer, ) \
            .filter(
            invited_discount=discount,
        )

        if discount_for_invited_query.exists():
            return not discount_for_invited_query.filter(
                invited_discount__customers_used__id=customer.id).exists()  # checks customer used discount before

        inviter_discount_query = FriendInvitation.objects.filter(businessman=businessman, inviter=customer) \
            .filter(
            inviter_discount=discount,
        )

        if inviter_discount_query.exists():
            return not inviter_discount_query.filter(
                inviter_discount__customers_used__id=customer.id).exists()  # check customer used discount

        return False

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

    def discount_for_loyalty_amount(self, user: Businessman, customer: Customer, expires: bool, discount_type: str,
                                    percent_off: float, flat_rate_off: int,
                                    expire_date=None) -> Discount:

        # discount = self.create_discount(user, False, discount_type, True, percent_off, flat_rate_off)
        # discount.used_for = Discount.USED_FOR_LOYALTY_AMOUNT
        # discount.reserved_for = customer
        # discount.save()
        # return discount
        return None

    def discount_for_loyalty_number(self, user: Businessman, customer: Customer, expires: bool, discount_type: str,
                                    percent_off: float, flat_rate_off: int,
                                    expire_date=None) -> Discount:

        return None

        # discount = self.create_discount(user, False, discount_type, True, percent_off, flat_rate_off)
        # discount.used_for = Discount.USED_FOR_LOYALTY_NUMBER
        # discount.reserved_for = customer
        # discount.save()
        # return discount

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
            purchases__customer=customer).exists()
        if has_discount:
            return True

        has_discount = FriendInvitation.objects.filter(businessman=businessman, invited=customer, ) \
            .exclude(
            invited_discount__purchases__customer=customer
        ).exists()

        if has_discount:
            return True
        has_discount = FriendInvitation.objects.filter(businessman=businessman, inviter=customer) \
            .exclude(inviter_discount__purchases__customer=customer.id).exists()
        return has_discount

    def apply_discount(self, businessman: Businessman, discount_code: str, phone: str) -> (bool, Discount):

        """
        applies discount for customer by discount code
        :param businessman: Businessman that discount code belongs to.
        :param discount_code: discount code of discount record
        :param phone: phone number of the customer that discount is going to be used for
        :return: tuple (bool, Discount). first parameter indicates that customer could use discount, if true
        second parameter is the discount record that applied for the customer. if false, second parameter is None
        """

        if not self.discount_exists_by_discount_code(businessman=businessman, discount_code=discount_code):
            raise ValueError('discount code is not valid')

        customer = self.customer_service.get_customer(businessman, phone)
        can_use = self.can_customer_use_discount(businessman, discount_code, customer)

        if not can_use:
            return False, None

        discount = Discount.objects.get(businessman=businessman, discount_code=discount_code)

        discount.customers_used.add(customer)
        discount.save()

        return True, discount

        # if discount.discount_type == Discount.DISCOUNT_TYPE_PERCENT:

    def try_apply_discount_by_discount_ids(self, businessman: Businessman, discount_ids: [int],
                                           purchase: CustomerPurchase):
        """
        tries to add customer to customer_used field in discount
        :param businessman: businessman who's discounts and customer belongs to
        :param discount_ids: ids of the discounts
        :param customer_id: id of the customer
        :return: if any discount exists by provided ids returns True else False
        """
        # customer = customer_service.get_customer_by_id(businessman, customer_id)
        discounts = self.get_customer_unused_discounts(businessman, purchase.customer.id).filter(id__in=discount_ids)
        if discounts.count() == 0:
            return False
        for discount in discounts.all():
            discount.purchases.add(purchase)
            discount.save()
        return True

    def get_customer_discounts_by_customer_id(self, user: Businessman, customer_id: int):

        customer = customer_service.get_customer_by_id(user, customer_id)

        festival_discounts = Discount.objects.filter(businessman=user).filter(
            Q(expires=True, expire_date__gt=timezone.now()) | Q(expires=False)) \
            .filter(Q(used_for=Discount.USED_FOR_FESTIVAL)
                    | Q(used_for=Discount.USED_FOR_INVITATION,
                        inviter_discount__inviter=customer)
                    | Q(used_for=Discount.USED_FOR_INVITATION,
                        inviter_discount__invited=customer)).all()

        return festival_discounts

    def get_customer_unused_discounts(self, user: Businessman, customer_id: int):
        return self.get_customer_discounts_by_customer_id(user, customer_id).exclude(
            purchases__customer__id=customer_id)

    def get_customer_used_discounts(self, user: Businessman, customer_id: int):
        return self.get_customer_discounts_by_customer_id(user, customer_id).filter(purchases__customer__id=customer_id)

    def get_customer_loyalty_amount_discounts(self, user: Businessman, customer: Customer):
        return self.get_customer_discounts_by_customer_id(user, customer.id).filter(
            used_for=Discount.USED_FOR_LOYALTY_AMOUNT)

    def get_customer_loyalty_number_discounts(self, user: Businessman, customer: Customer):
        return self.get_customer_discounts_by_customer_id(user, customer.id).filter(
            used_for=Discount.USED_FOR_LOYALTY_NUMBER)

    def get_customer_used_discounts_sum_amount(self, user: Businessman, customer_id):
        val = 0
        for d in self.get_customer_used_discounts(user, customer_id).all():
            val += d.purchase_amount_for_customer(customer_id)
        return val

    def has_customer_used_discount(self, discount: Discount, customer_id: int) -> (bool, bool, Discount, Customer):
        return discount.purchases.filter(customer__id=customer_id).exists()

    def get_discount_date_used(self, user: Businessman, discount: Discount, customer_id: int):
        used_discounts = self.get_customer_used_discounts(user, customer_id)
        if not used_discounts.filter(id=discount.id).exists():
            return None
        return used_discounts.get(id=discount.id).purchases.first().create_date

    def get_num_of_customers_used_discount(self, discount: Discount) -> int:
        return discount.purchases.count()

    def delete_customer_from_discount(self, user: Businessman, discount_id: int, customer_id: int):

        try:
            discount = Discount.objects.get(businessman=user, id=discount_id)
        except ObjectDoesNotExist:
            return False, False, None, None
        try:
            customer = discount.customers_used.get(id=customer_id)
        except ObjectDoesNotExist:
            return True, False, None, None

        discount.customers_used.remove(customer)
        discount.save()
        return True, True, discount, customer

    def oldest_unused_discounts_by_ids(self, businessman: Businessman, customer_id: int, discount_ids: list):
        """
        retrieve list of unused discount by discounts_ids for specific customer
        :param businessman: businessman that discounts belongs to
        :param discount_ids: ids of the discounts
        :return: list of tuples in order of (discount_type, percent_off, flat_rate_off)
        """
        return self.get_customer_unused_discounts(businessman, customer_id).filter(id__in=discount_ids).order_by(
            'create_date')

    def delete_discount(self, user: Businessman, discount_id: int) -> (bool, Discount):

        try:
            discount = Discount.objects.get(businessman=user, id=discount_id)
        except ObjectDoesNotExist:
            return False, None
        discount.delete()
        return True, discount

    def delete_last_loyalty_number_discount(self, user: Businessman, customer: Customer) -> Discount:
        if self.get_customer_loyalty_number_discounts(user, customer).count() > 0:
            d = self.get_customer_loyalty_number_discounts(user, customer).order_by('-create_date').first()
            d.delete()
            return d
        return None

    def delete_last_loyalty_amount_discount(self, user: Businessman, customer: Customer) -> Discount:
        if self.get_customer_loyalty_amount_discounts(user, customer).count() > 0:
            d = self.get_customer_loyalty_amount_discounts(user, customer).order_by('-create_date').first()
            d.delete()
            return d
        return None

    def get_total_customers_used_festival_discount(self, festival: Festival) -> int:
        return self.get_num_of_customers_used_discount(festival.discount)


discount_service = DiscountService()
