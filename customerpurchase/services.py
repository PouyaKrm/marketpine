from django.core.exceptions import ObjectDoesNotExist
from django.db.models.aggregates import Sum


from customer_return_plan.models import Discount
from customer_return_plan.services import DiscountService
from customerpurchase.models import CustomerPurchase
from customers.services import customer_service
from groups.models import BusinessmanGroups
from users.models import Businessman, Customer

discount_service = DiscountService()


class PurchaseService:

    def re_evaluate_purchase_top_group(self, user: Businessman):
        p = CustomerPurchase.objects.filter(businessman=user).values('customer').annotate(purchase_sum=Sum('amount')).filter(
            purchase_sum__gt=0).order_by('-purchase_sum')[:5]
        customer_ids = []
        for c in p.all():
            customer_ids.append(c['customer'])
        customers = customer_service.get_bsuinessman_customers_by_ids(user, customer_ids)
        BusinessmanGroups.set_members_for_purchase_top(user, customers)

    def get_businessman_all_purchases(self, user: Businessman):
        return CustomerPurchase.objects.filter(businessman=user).order_by('-create_date').all()

    def validate_calculate_discount_amount_for_purchase(self, discounts: [Discount], purchase_amount: int, ) -> (bool, bool, int):
        # discounts = discount_service.oldest_unused_discounts_by_ids(businessman=businessman, customer=customer,
        #                                                             discount_ids=discount_ids)
        if len(discounts) == 0:
            return False, False, -1

        discount_amounts = 0
        for discount in discounts:
            if discount.is_flat_discount():
                discount_amounts += discount.flat_rate_off
            elif discount.is_percent_discount():
                discount_amounts += discount.percent_off / 100 * purchase_amount

        if discount_amounts > purchase_amount:
            return True, False, -1
        return True, True, discount_amounts

    def submit_purchase_with_discounts(self, businessman: Businessman, customer: Customer, amount: int,
                                       discount_ids: [int] = None) -> CustomerPurchase:

        from payment.services import wallet_billing_service
        from customer_return_plan.loyalty.services import LoyaltyService
        purchase = CustomerPurchase(businessman=businessman, amount=amount, customer=customer)
        bc = customer_service.get_businessmancustomer_delete_check(businessman, customer)
        wallet_billing_service.add_payment_if_customer_invited(bc)
        purchase.save()
        if (discount_ids is not None) and len(discount_ids) != 0:
            discount_service.try_apply_discounts(businessman, discount_ids, purchase)
        LoyaltyService.get_instance().increase_customer_points_by_purchase_amount(businessman, customer,
                                                                                  purchase.amount)
        return purchase

    def get_customer_all_purchases(self, businessman: Businessman, customer: Customer):
        return CustomerPurchase.objects.filter(businessman=businessman, customer=customer)

    def get_customer_all_purchase_amounts(self, businessman: Businessman, customer: Customer) -> int:
        return 0
        # return self.get_customer_all_purchases(businessman, customer).aggregate(Sum('amount')).get(
        #     'sum_amount')

    def add_customer_purchase(self, user: Businessman, customer: Customer, amount: int) -> CustomerPurchase:
        from payment.services import wallet_billing_service
        from customer_return_plan.loyalty.services import LoyaltyService
        purchase = CustomerPurchase.objects.create(businessman=user, customer=customer, amount=amount)
        bc = customer_service.get_businessmancustomer_delete_check(user, customer)
        wallet_billing_service.add_payment_if_customer_invited(bc)
        self.re_evaluate_purchase_top_group(user)
        LoyaltyService.get_instance().increase_customer_points_by_purchase_amount(user, customer, purchase.amount)
        return purchase

    def delete_purchase_by_purchase_id(self, user: Businessman, purchase_id: int) -> (bool, CustomerPurchase):
        try:
            purchase = CustomerPurchase.objects.get(businessman=user, id=purchase_id)
        except ObjectDoesNotExist:
            return False, None
        purchase.delete()
        self.re_evaluate_purchase_top_group(user)
        return True, purchase

    def get_customer_purchase_sum(self, user: Businessman, customer: Customer):
        result = CustomerPurchase.objects.filter(businessman=user, customer=customer).aggregate(purchase_sum=Sum('amount'))['purchase_sum']
        if result is None:
            return 0
        return result

    def get_all_businessman_purchases_by_dsicount(self, businessman: Businessman):
        return CustomerPurchase.objects.filter(businessman=businessman, connected_purchases__businessman=businessman)


purchase_service = PurchaseService()
