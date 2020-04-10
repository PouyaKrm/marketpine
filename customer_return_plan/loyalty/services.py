from django.core.exceptions import ObjectDoesNotExist

from customer_return_plan.models import Discount
from users.models import Businessman, Customer
from .models import (CustomerLoyaltyDiscountSettings, CustomerPurchaseAmountDiscountSettings,
                     CustomerPurchaseNumberDiscountSettings)

from customer_return_plan.services import discount_service
from customerpurchase.services import purchase_service


class LoyaltyService:

    def __create_amount_discount(self, businessman: Businessman, customer: Customer,
                                 amount_setting: CustomerPurchaseAmountDiscountSettings) -> Discount:

        discount = discount_service.discount_for_loyalty_amount(businessman, customer, False,
                                                                amount_setting.discount_type,
                                                                amount_setting.percent_off,
                                                                amount_setting.flat_rate_off)
        return discount

    def __create_number_discount(self, businessman: Businessman, customer: Customer,
                                 number_setting: CustomerPurchaseNumberDiscountSettings) -> Discount:

        discount = discount_service.discount_for_loyalty_number(businessman, customer, False,
                                                                number_setting.discount_type,
                                                                number_setting.percent_off,
                                                                number_setting.flat_rate_off)
        return discount

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

    def get_businessman_loyalty_settings(self, businessman: Businessman) -> CustomerLoyaltyDiscountSettings:

        try:
            return CustomerLoyaltyDiscountSettings.objects.get(businessman=businessman)
        except ObjectDoesNotExist:
            return None

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

    def re_evaluate_discounts_after_purchase_update_or_delete(self, businessman: Businessman, customer: Customer) -> Discount:

        num_setting = businessman.customerloyaltydiscountsettings.purchase_number_settings
        amount_setting = businessman.customerloyaltydiscountsettings.purchase_amount_settings
        discounts_num = discount_service.get_customer_loyalty_number_discounts().count()

        if discounts_num * num_setting.purchase_number > purchase_service.get_customer_all_purchases(businessman, customer).count():
            discount_service.delete_last_loyalty_number_discount(businessman, customer)

        if discounts_num * amount_setting.purchase_amount > purchase_service.get_customer_all_purchase_amounts(businessman, customer):
            discount_service.delete_last_loyalty_amount_discount(businessman, customer)


loyalty_service = LoyaltyService()
