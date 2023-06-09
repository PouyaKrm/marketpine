from typing import Tuple

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.aggregates import Sum
from django.db.models.query_utils import Q
from django.utils import timezone
from strgen import StringGenerator

from base_app.error_codes import ApplicationErrorException, ApplicationErrorCodes
from customer_return_plan.festivals.models import Festival
from customer_return_plan.festivals.services import festival_service
from customer_return_plan.loyalty.models import CustomerLoyaltyDiscountSettings, CustomerExclusiveDiscount
from customer_return_plan.models import Discount, PurchaseDiscount
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
        ).exclude(festival__marked_as_deleted_for_businessman=True).exists()

        return exists

    def get_businessman_all_discounts(self, user: Businessman):
        return Discount.objects.filter(businessman=user).all()

    def get_businessman_discount_or_none(self, user: Businessman, discount_id: int) -> Discount:
        try:
            return Discount.objects.get(businessman=user, id=discount_id)
        except ObjectDoesNotExist:
            return None

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

    def create_loyalty_discount(self, discount_settings: CustomerLoyaltyDiscountSettings, customer: Customer,
                                has_loyalty_discount_error_code: dict) -> Discount:

        from .loyalty.services import LoyaltyService

        if not discount_settings.loyalty_settings.is_active:
            raise ApplicationErrorException(ApplicationErrorCodes.OPTION_IS_DISABLED)

        has_loyalty = self.has_customer_loyalty_discounts(discount_settings.loyalty_settings.businessman, customer)
        if has_loyalty:
            raise ApplicationErrorException(has_loyalty_discount_error_code)

        points = LoyaltyService.get_instance().get_customer_points(discount_settings.loyalty_settings.businessman,
                                                                   customer)

        if points.point < discount_settings.point:
            raise ApplicationErrorException(ApplicationErrorCodes.NOT_ENOUGH_POINT_FOR_DISCOUNT)

        d = self.create_discount(discount_settings.loyalty_settings.businessman, False,
                                 discount_settings.discount_type, False,
                                 discount_settings.percent_off, discount_settings.flat_rate_off,
                                 discount_settings.discount_code)
        d.used_for = Discount.USED_FOR_LOYALTY
        d.save()
        bc = customer_service.get_businessmancustomer(discount_settings.loyalty_settings.businessman, customer)
        CustomerExclusiveDiscount.objects.create(discount=d, businessman_customer=bc)
        points.decrease_point(discount_settings.point)
        return d

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

    def try_apply_discounts(self, businessman: Businessman, discounts: [Discount],
                            purchase: CustomerPurchase):
        """
        tries to add customer to customer_used field in discount
        :param businessman: businessman who's discounts and customer belongs to
        :param discount_ids: ids of the discounts
        :param customer_id: id of the customer
        :return: if any discount exists by provided ids returns True else False
        """
        # customer = customer_service.get_customer_by_id(businessman, customer_id)
        # discounts = self.get_customer_unused_discounts(businessman, purchase.customer.id).filter(id__in=discount_ids)
        if len(discounts) == 0:
            return False
        for discount in discounts:
            discount.connected_purchases.add(purchase)
            discount.save()
        return True

    def get_customer_discounts_for_businessman(self, user: Businessman, customer: Customer):

        exist = customer_service.customer_exists(user, customer)

        if not exist:
            return Discount.objects.none()

        inviter_discount = Discount.objects.filter(
            businessman=user,
            used_for=Discount.USED_FOR_INVITATION,
            inviter_discount__inviter__customer=customer,
            inviter_discount__inviter__businessman=user,
        ).annotate(
            purchase_sum_of_invited=Sum('inviter_discount__invited__customer__purchases__amount',
                                        filter=Q(
                                            inviter_discount__inviter__customer=customer,
                                            inviter_discount__invited__customer__purchases__businessman=user
                                        )
                                        )
        ).filter(
            purchase_sum_of_invited__gt=0
        )

        invited_discount = Discount.objects.filter(
            businessman=user,
            invited_discount__invited__businessman=user,
            invited_discount__invited__customer=customer,
        )

        festival_discount = Discount.objects.filter(businessman=user, used_for=Discount.USED_FOR_FESTIVAL)

        loyalty_discount = Discount.objects.filter(
            businessman=user,
            used_for=Discount.USED_FOR_LOYALTY
        ).filter(
            exclusive_customers__businessman_customer__customer=customer,
            exclusive_customers__businessman_customer__is_deleted=False
        )

        discounts = inviter_discount | invited_discount | festival_discount | loyalty_discount
        return discounts.order_by('-create_date')

    def get_customer_unused_discounts_for_businessman(self, user: Businessman, customer: Customer):
        return self.get_customer_discounts_for_businessman(user, customer) \
            .exclude(
            connected_purchases__customer=customer)

    def get_customer_available_discounts_for_businessman(self, user: Businessman, customer: Customer):
        return self.get_customer_discounts_for_businessman(user, customer) \
            .exclude(expires=True, expire_date__lt=timezone.now()) \
            .exclude(festival__marked_as_deleted_for_businessman=True) \
            .exclude(
            connected_purchases__customer=customer)

    def can_customer_use_discount(self, businessman: Businessman, discount: Discount, customer: Customer) -> bool:

        return self.get_customer_available_discounts_for_businessman(businessman, customer).filter(
            id=discount.id).exists()

    def has_customer_any_discount(self, businessman: Businessman, customer: Customer) -> bool:

        return self.get_customer_available_discounts_for_businessman(businessman, customer).exists()

    def get_customer_used_discounts_for_businessman(self, user: Businessman, customer: Customer):
        return self.get_customer_discounts_for_businessman(user, customer) \
            .filter(connected_purchases__customer=customer).order_by('-purchase_discount__create_date')

    def get_customer_loyalty_amount_discounts(self, user: Businessman, customer: Customer):
        return self.get_customer_discounts_for_businessman(user, customer).filter(
            used_for=Discount.USED_FOR_LOYALTY_AMOUNT)

    def get_customer_loyalty_number_discounts(self, user: Businessman, customer: Customer):
        return self.get_customer_discounts_for_businessman(user, customer).filter(
            used_for=Discount.USED_FOR_LOYALTY_NUMBER)

    def get_customer_used_discounts_sum_amount(self, user: Businessman, customer: Customer):
        val = 0
        for d in self.get_customer_used_discounts_for_businessman(user, customer).all():
            val += d.amount_of_discount_for_customer(customer)
        return val

    def has_customer_used_discount(self, discount: Discount, customer: Customer) -> (bool, bool, Discount, Customer):
        return discount.connected_purchases.filter(customer=customer).exists()

    def has_customer_loyalty_discounts(self, businessman: Businessman, customer: Customer) -> bool:
        discounts = self.get_customer_available_discounts_for_businessman(businessman, customer)
        return discounts.filter(used_for=Discount.USED_FOR_LOYALTY).exists()

    def get_discount_date_used(self, user: Businessman, discount: Discount, customer: Customer):
        query = PurchaseDiscount.objects.filter(discount=discount, discount__businessman=user).filter(
            purchase__businessman=user,
            purchase__customer=customer)
        if not query.exists():
            return None
        return query.first().create_date

    def get_num_of_customers_used_discount(self, discount: Discount) -> int:
        return discount.connected_purchases.count()

    def delete_customer_from_discount(self, user: Businessman, discount_id: int, customer_id: int):

        try:
            discount = Discount.objects.get(businessman=user, id=discount_id)
        except ObjectDoesNotExist:
            return False, False, None, None
        try:
            purchase = discount.connected_purchases.get(customer_id=customer_id)
        except ObjectDoesNotExist:
            return True, False, None, None

        PurchaseDiscount.objects.filter(discount__id=discount_id, purchase=purchase).delete()
        # discount.save()
        return True, True, discount, purchase

    def oldest_unused_discounts_by_ids(self, businessman: Businessman, customer: Customer, discount_ids: list):
        """
        retrieve list of unused discount by discounts_ids for specific customer
        :param businessman: businessman that discounts belongs to
        :param discount_ids: ids of the discounts
        :return: list of tuples in order of (discount_type, percent_off, flat_rate_off)
        """
        return self.get_customer_unused_discounts_for_businessman(businessman, customer).filter(
            id__in=discount_ids).order_by(
            'create_date')

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

    def get_used_festival_discounts_in_month(self, businessman: Businessman, date):
        return Discount.objects.filter(businessman=businessman,
                                       used_for=Discount.USED_FOR_FESTIVAL,
                                       purchase_discount__create_date__year=date.year,
                                       purchase_discount__create_date__month=date.month)

    def get_used_invitation_discounts_in_month(self, businessman: Businessman, date):
        return Discount.objects.filter(businessman=businessman,
                                       used_for=Discount.USED_FOR_INVITATION,
                                       purchase_discount__create_date__year=date.year,
                                       purchase_discount__create_date__month=date.month
                                       )

    def is_discount_used_anywhere_else(self, discount: Discount, exclude_festival: Festival = None,
                                       exclude_invitation=None) -> bool:
        from .invitation.services import invitation_service
        festival_exist_q = festival_service.filter_festival_by_discount(discount)
        if exclude_festival is not None:
            festival_exist_q = festival_exist_q.exclude(id=exclude_festival.id)
        invitation_exist_q = invitation_service.filter_invitation_by_discount(discount)
        if exclude_invitation is not None:
            invitation_exist_q = invitation_exist_q.exclude(id=exclude_invitation.id)
        return festival_exist_q.exists() or invitation_exist_q.exists()


class CustomerDiscountService:

    def get_customer_discounts(self, customer: Customer):

        inviter_discount = Discount.objects.filter(
            used_for=Discount.USED_FOR_INVITATION
        ).filter(
            inviter_discount__inviter__customer=customer,
            inviter_discount__inviter__is_deleted=False
        )

        invited_discount = Discount.objects.filter(
            used_for=Discount.USED_FOR_INVITATION,
        ).filter(
            invited_discount__invited__customer=customer,
            invited_discount__invited__is_deleted=False
        )

        joined_businessmans = Businessman.objects.filter(
            connected_customers__customer=customer,
            connected_customers__is_deleted=False
        )

        festival_discount = Discount.objects.filter(
            used_for=Discount.USED_FOR_FESTIVAL,
            festival__businessman__in=joined_businessmans
        )

        loyalty_discounts = Discount.objects.filter(
            used_for=Discount.USED_FOR_LOYALTY
        ).filter(
            exclusive_customers__businessman_customer__customer=customer,
            exclusive_customers__businessman_customer__is_deleted=False
        )

        return invited_discount | inviter_discount | festival_discount | loyalty_discounts

    def get_customer_available_discount(self, customer: Customer):
        return self.get_customer_discounts(customer) \
            .exclude(expires=True, expire_date__lt=timezone.now()) \
            .exclude(festival__marked_as_deleted_for_businessman=True) \
            .exclude(
            connected_purchases__customer=customer)

    def is_invitation_inviter_discount_and_invited_has_purchase(self, discount: Discount, customer: Customer) -> Tuple[
        bool, bool, bool]:

        """
        :param discount: discount to be used to check against
        :param customer: customer to check if  discount is related to this customer and customer has it as inviter in frient invitation
        :returns:
             -x (:py:class:`bool`) - is discount used_for == USED_FOR_INVITATION
             -y (:py:class:`bool`) - is customer is has discount as inviter
             -z (:py:class:`bool`) - is invited customer has any purchase
        """

        if not discount.is_invitation_discount():
            return False, False, False

        if discount.inviter_discount.inviter.customer != customer:
            return True, False, False

        p_sum = CustomerPurchase.objects.filter(
            businessman=discount.businessman,
            customer=discount.inviter_discount.invited.customer
        ).aggregate(
            purchase_amount_sum=Sum('amount')
        )

        if p_sum is not None and p_sum['purchase_amount_sum'] is not None and p_sum['purchase_amount_sum'] > 0:
            return True, True, True

        return True, True, False

    def get_customer_used_discounts(self, customer: Customer):
        return self.get_customer_discounts(customer) \
            .filter(connected_purchases__customer=customer).order_by('-purchase_discount__create_date')


discount_service = DiscountService()
customer_discount_service = CustomerDiscountService()
