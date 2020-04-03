from customer_return_plan.services import DiscountService
from customerpurchase.models import CustomerPurchase
from users.models import Businessman

discount_service = DiscountService()


class PurchaseService:

    def validate_calculate_discount_amount_for_purchase(self, businessman: Businessman, customer_id: int, discount_ids: [int],
                                                 purchase_amount: int, ) -> (bool, bool, int):
        discounts = discount_service.oldest_unused_discounts_by_ids(businessman=businessman, customer_id=customer_id,
                                                                    discount_ids=discount_ids)
        if discounts.count() == 0:
            return False, False, -1

        discount_amounts = 0
        for discount in discounts.all():
            if discount.is_flat_discount():
                discount_amounts += discount.flat_rate_off
            elif discount.is_percent_discount():
                discount_amounts += discount.percent_off / 100 * purchase_amount

        if discount_amounts > purchase_amount:
            return True, False, -1
        return True, True, discount_amounts

    def submit_purchase_with_discounts(self, businessman: Businessman, customer_id: int, amount: int,
                                       discount_ids: [int]=None) -> (bool, bool, CustomerPurchase):

        purchase = CustomerPurchase(businessman=businessman, amount=amount, customer_id=customer_id)
        if (discount_ids is not None) and len(discount_ids) != 0:
            discount_service.try_apply_discount_by_discount_ids(businessman, discount_ids, customer_id)
        purchase.save()
        return True, True, purchase
