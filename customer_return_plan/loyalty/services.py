from typing import List, Dict

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet

from customer_return_plan.models import Discount
from customer_return_plan.services import discount_service
from customerpurchase.services import purchase_service
from users.models import Businessman, Customer
from .models import (CustomerLoyaltyDiscountSettings, CustomerPurchaseAmountDiscountSettings,
                     CustomerPurchaseNumberDiscountSettings)

# if sys.version_info[0] == 3 and sys.version_info[1] >= 8:
#     from typing import TypedDict
# else:
#     from typing_extensions import TypedDict

max_settings_per_businessman = settings.LOYALTY_SETTINGS['MAX_SETTINGS_NUMBER_PER_BUSINESSMAN']


# class LoyaltySetting(TypedDict):
#     point: int
#     discount_code: str
#     discount_type: str
#     discount_off: int
#     percent_off: int
#     flat_rate_off: int
#

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

    def get_businessman_loyalty_settings(self, businessman: Businessman) -> QuerySet:
        return CustomerLoyaltyDiscountSettings.objects.filter(businessman=businessman).order_by('point')

    def update_businessman_loyalty_settings(self, user: Businessman, loyalty_settings: List[Dict]):

        length = len(loyalty_settings)
        db_settings_count = self.get_businessman_loyalty_settings(user).count()

        if db_settings_count >= length:
            result = self._update_when_new_settings_count_smaller(user, loyalty_settings)

        else:
            result = self._update_when_old_settings_are_smaller(user, loyalty_settings)

        return result

    def _update_when_new_settings_count_smaller(self, user: Businessman, loyalty_settings: List[Dict]):
        length = len(loyalty_settings)
        db_settings = self.get_businessman_loyalty_settings(user).order_by('point')[:length]
        ids = list(map(lambda e: e.id, db_settings))

        for old_st, new_st in zip(db_settings, loyalty_settings):
            self._update_settings(old_st, new_st)

        CustomerLoyaltyDiscountSettings.objects.filter(businessman=user).exclude(
            id__in=ids
        ).delete()

        return db_settings

    def _update_when_old_settings_are_smaller(self, user: Businessman, loyalty_settings: List[Dict]):

        db_settings_count = self.get_businessman_loyalty_settings(user).count()
        db_settings = self.get_businessman_loyalty_settings(user).order_by('point')[:db_settings_count]
        for old_st, new_st in zip(db_settings, loyalty_settings):
            self._update_settings(old_st, new_st)

        for new_st in loyalty_settings[db_settings_count:]:
            CustomerLoyaltyDiscountSettings.objects.create(businessman=user,
                                                           point=new_st['point'],
                                                           discount_type=new_st['discount_type'],
                                                           discount_code=new_st['discount_code'],
                                                           percent_off=new_st['percent_off'],
                                                           flat_rate_off=new_st['flat_rate_off']
                                                           )
        return self.get_businessman_loyalty_settings(user)

    def _update_settings(self, old_settings: CustomerLoyaltyDiscountSettings, new_settings: dict):
        old_settings.point = new_settings['point']
        old_settings.discount_code = new_settings['discount_code']
        old_settings.discount_type = new_settings['discount_type']
        old_settings.percent_off = new_settings['percent_off']
        old_settings.flat_rate_off = new_settings['flat_rate_off']
        old_settings.save()

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
