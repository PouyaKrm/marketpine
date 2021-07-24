import math
from typing import Dict

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from customer_return_plan.models import Discount
from customer_return_plan.services import discount_service
from customerpurchase.services import purchase_service
from users.models import Businessman, Customer
from .models import (CustomerLoyaltyDiscountSettings, CustomerPurchaseAmountDiscountSettings,
                     CustomerPurchaseNumberDiscountSettings, CustomerPoints, CustomerLoyaltySettings)

# if sys.version_info[0] == 3 and sys.version_info[1] >= 8:
#     from typing import TypedDict
# else:
#     from typing_extensions import TypedDict

max_settings_per_businessman = settings.LOYALTY_SETTINGS['MAX_SETTINGS_NUMBER_PER_BUSINESSMAN']
purchase_for_1_point = settings.LOYALTY_SETTINGS['PURCHASE_AMOUNT_FOR_1']


class LoyaltyService:
    _instance = None

    @staticmethod
    def get_instance():
        if LoyaltyService._instance is None:
            LoyaltyService._instance = LoyaltyService()
        return LoyaltyService._instance

    def __can_customer_have_new_amount_discount(self, businessman: Businessman, customer: Customer,
                                                amount_setting: CustomerPurchaseAmountDiscountSettings) -> bool:
        amount = amount_setting.purchase_amount
        disc_nums = discount_service.get_customer_loyalty_amount_discounts(businessman, customer).count()
        all_purchase_amounts = purchase_service.get_customer_all_purchase_amounts(businessman, customer)
        return all_purchase_amounts >= (disc_nums + 1) * amount

    def __can_customer_have_new_number_discount(self, businessman: Businessman, customer: Customer,
                                                number_setting: CustomerPurchaseNumberDiscountSettings) -> bool:

        number = number_setting.purchase_number
        disc_nums = discount_service.get_customer_loyalty_number_discounts(businessman, customer)
        all_purchases_counts = purchase_service.get_customer_all_purchases(businessman, customer).count()
        return all_purchases_counts >= (disc_nums + 1) * number

    def try_create_loyalty_setting_for_businessman(self, businessman: Businessman) -> CustomerLoyaltyDiscountSettings:

        try:
            return CustomerLoyaltyDiscountSettings.objects.get(businessman=businessman)
        except ObjectDoesNotExist:
            pass
        number_setting = CustomerPurchaseNumberDiscountSettings.objects.create()
        amount_setting = CustomerPurchaseAmountDiscountSettings.objects.create()
        s = CustomerLoyaltyDiscountSettings(businessman=businessman, purchase_amount_settings=amount_setting,
                                            purchase_number_settings=number_setting, disabled=True)
        s.save()
        return s

    def get_businessman_loyalty_settings(self, user: Businessman) -> CustomerLoyaltySettings:
        try:
            return CustomerLoyaltySettings.objects.get(businessman=user)
        except ObjectDoesNotExist:
            return CustomerLoyaltySettings.objects.create(businessman=user)

    def update_businessman_loyalty_settings(self, user: Businessman, loyalty_settings: Dict):
        settings = self.get_businessman_loyalty_settings(user)
        settings.is_active = loyalty_settings.get('is_active')
        settings.save()
        CustomerLoyaltyDiscountSettings.objects.filter(loyalty_settings=settings).delete()
        cs = [
            CustomerLoyaltyDiscountSettings(
                loyalty_settings=settings,
                point=st['point'],
                discount_type=st['discount_type'],
                discount_code=st['discount_code'],
                percent_off=st['percent_off'],
                flat_rate_off=st['flat_rate_off']
            ) for st in loyalty_settings.get('discount_settings')
        ]
        CustomerLoyaltyDiscountSettings.objects.bulk_create(cs)
        return settings

    def increase_customer_points_by_purchase_amount(self, businessman: Businessman, customer: Customer,
                                                    purchase_amount: int) -> CustomerPoints:
        points = self.get_customer_points(businessman, customer)
        added_points = math.floor(purchase_amount / purchase_for_1_point)
        points.point = points.point + added_points
        points.save()
        return points

    def get_customer_points(self, businessman: Businessman, customer: Customer) -> CustomerPoints:
        try:
            return CustomerPoints.objects.get(businessman=businessman, customer=customer)
        except ObjectDoesNotExist:
            return CustomerPoints.objects.create(businessman=businessman, customer=customer, point=0)

    def create_discount_for_loyalty(self, businessman: Businessman, customer: Customer) -> bool:
        try:
            setting = CustomerLoyaltyDiscountSettings.objects.get(businessman=businessman)
        except ObjectDoesNotExist:
            return False

        amount_setting = setting.purchase_amount_settings
        number_setting = setting.purchase_number_settings
        can_have_amount_discount = self.__can_customer_have_new_amount_discount(businessman, customer, amount_setting)
        can_have_number_discount = self.__can_customer_have_new_number_discount(businessman, customer, number_setting)

        if setting.is_discount_for_purchase_amount() and can_have_amount_discount:
            self.__create_amount_discount(businessman, customer, amount_setting)
            return True
        if setting.is_discount_for_purchase_number() and can_have_number_discount:
            self.__create_number_discount(businessman, customer, number_setting)
            return True
        if setting.is_discount_for_both():
            if can_have_amount_discount:
                self.__create_amount_discount(businessman, customer, amount_setting)
            if can_have_number_discount:
                self.__create_number_discount(businessman, customer, number_setting)
            return True

    def re_evaluate_discounts_after_purchase_update_or_delete(self, businessman: Businessman,
                                                              customer: Customer) -> Discount:

        num_setting = businessman.customerloyaltydiscountsettings.purchase_number_settings
        amount_setting = businessman.customerloyaltydiscountsettings.purchase_amount_settings
        discounts_num = discount_service.get_customer_loyalty_number_discounts().count()

        if discounts_num * num_setting.purchase_number > purchase_service.get_customer_all_purchases(businessman,
                                                                                                     customer).count():
            discount_service.delete_last_loyalty_number_discount(businessman, customer)

        if discounts_num * amount_setting.purchase_amount > purchase_service.get_customer_all_purchase_amounts(
                businessman, customer):
            discount_service.delete_last_loyalty_amount_discount(businessman, customer)


LoyaltyService.get_instance()
loyalty_service = LoyaltyService()
