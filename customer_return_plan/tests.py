import uuid
from abc import ABC
from random import randint
# Create your tests here.
from typing import Tuple

from django.utils import timezone

from base_app.error_codes import ApplicationErrorException, ApplicationErrorCodes
from base_app.tests import BaseTestClass
from customer_return_plan.festivals.models import Festival
from customer_return_plan.invitation.models import FriendInvitation
from customer_return_plan.loyalty.models import CustomerExclusiveDiscount, CustomerLoyaltyDiscountSettings, \
    CustomerLoyaltySettings, CustomerPoints
from customer_return_plan.models import Discount, PurchaseDiscount, BaseDiscountSettings
from customer_return_plan.services import discount_service, customer_discount_service
from customerpurchase.models import CustomerPurchase
from users.models import Businessman, Customer, BusinessmanCustomer


class BaseDiscountServiceTestClass(BaseTestClass, ABC):

    def setUp(self) -> None:
        bc = self.create_customer_and_businessman_with_relation()
        b = bc[0]
        self.businessman = b
        invited = self.create_customer_with_businessman(b)
        self.invitation = self._create_friend_invitation(b, bc[1], invited)

    def create_customer_and_businessman_with_relation(self) -> Tuple[Businessman, BusinessmanCustomer]:
        b = self.create_businessman()
        c = self.create_customer_with_businessman(b)
        return b, c

    def create_customer_with_businessman(self, businessman: Businessman) -> BusinessmanCustomer:
        c = super().create_customer_with_businessman(businessman)
        return BusinessmanCustomer.objects.get(businessman=businessman, customer=c)

    def _create_friend_invitation(self, businessman: Businessman, inviter: BusinessmanCustomer,
                                  invited: BusinessmanCustomer) -> FriendInvitation:
        # inviter = BusinessmanCustomer.objects.get(businessman=businessman, customer=inviter)
        # invited = BusinessmanCustomer.objects.get(businessman=businessman, customer=invited)
        inviter_discount = self._create_discount(businessman, Discount.USED_FOR_INVITATION)
        invited_discount = self._create_discount(businessman, Discount.USED_FOR_INVITATION)
        return FriendInvitation.objects.create(businessman=businessman,
                                               inviter=inviter, invited=invited,
                                               inviter_discount=inviter_discount,
                                               invited_discount=invited_discount
                                               )

    def _create_discount(self, businessman: Businessman, used_for: str = Discount.USED_FOR_NONE) -> Discount:
        d = Discount()
        d.set_discount_data(randint(0, 10000).__str__(), Discount.DISCOUNT_TYPE_FLAT_RATE, 0, 1000)
        d.used_for = used_for
        d.businessman = businessman
        d.save()
        return d

    # def _create_friend_invitation(self, businessman: Businessman, inviter: Customer,
    #                               invited: Customer) -> FriendInvitation:
    #     inviter_discount = self._create_discount(businessman, Discount.USED_FOR_INVITATION)
    #     invited_discount = self._create_discount(businessman, Discount.USED_FOR_INVITATION)
    #     invitation = FriendInvitation()
    #     invitation.businessman = businessman
    #     invitation.inviter = inviter
    #     invitation.invited = invited
    #     invitation.inviter_discount = inviter_discount
    #     invitation.invited_discount = invited_discount
    #     invitation.save()
    #     return invitation

    def _create_purchase(self, businessman: Businessman, customer: Customer) -> CustomerPurchase:
        p = CustomerPurchase.objects.create(amount=10, customer=customer,
                                            businessman=businessman)
        return p

    def _create_festival(self, businessman: Businessman, discount: Discount) -> Festival:
        past = self.create_time_in_past()
        return Festival.objects.create(businessman=businessman,
                                       discount=discount,
                                       start_date=past,
                                       end_date=timezone.now()
                                       )

    def add_customer_to_businessman(self, businessman: Businessman, customer: Customer) -> BusinessmanCustomer:
        c = super().add_customer_to_businessman(businessman, customer)
        return BusinessmanCustomer.objects.get(businessman=businessman, customer=customer)

    def _create_loyalty_discount(self, bc: BusinessmanCustomer) -> Discount:
        d = self._create_discount(bc.businessman, Discount.USED_FOR_LOYALTY)
        CustomerExclusiveDiscount.objects.create(discount=d, businessman_customer=bc)
        return d

    def _create_loyalty_settings(self, businessman: Businessman, is_active=False):
        return CustomerLoyaltySettings.objects.create(businessman=businessman, is_active=is_active)

    def _create_loyalty_discount_setting(self, businessman: Businessman,
                                         is_active: bool) -> CustomerLoyaltyDiscountSettings:
        setting = self._create_loyalty_settings(businessman, is_active)
        return CustomerLoyaltyDiscountSettings.objects.create(loyalty_settings=setting,
                                                              point=10,
                                                              discount_code='code',
                                                              percent_off=0, flat_rate_off=0,
                                                              discount_type=BaseDiscountSettings.DISCOUNT_TYPE_FLAT_RATE,
                                                              )

    def _create_customer_point(self, businessman: Businessman, customer: Customer, point: int):
        return CustomerPoints.objects.create(businessman=businessman,
                                             customer=customer,
                                             point=point
                                             )


class BusinessmanDiscountTest(BaseDiscountServiceTestClass):

    def test_is_discount_code_unique_false(self):
        d = self.invitation.invited_discount
        result = discount_service.is_discount_code_unique(self.businessman, d.discount_code)
        self.assertFalse(result)

    def test_is_discount_code_unique_true(self):
        code = uuid.uuid4()
        result = discount_service.is_discount_code_unique(self.businessman, code)
        self.assertTrue(result)

    def test_create_loyalty_discounts(self):
        setting = self._create_loyalty_discount_setting(self.businessman, True)
        bc = self.create_customer_with_businessman(self.businessman)
        d = discount_service.create_loyalty_discount(setting, bc.customer, {})
        self.assertEqual(d.used_for, Discount.USED_FOR_LOYALTY)
        self.assertEqual(d.percent_off, d.percent_off)
        self.assertEqual(d.flat_rate_off, setting.flat_rate_off)
        self.assertEqual(d.discount_type, setting.discount_type)
        self.assertEqual(d.discount_code, setting.discount_code)
        self.assertEqual(d.exclusive_customers.count(), 1)
        ec = d.exclusive_customers.first()
        self.assertEqual(ec.businessman_customer, bc)

    def test_create_loyalty_discounts_setting_is_disabled(self):
        setting = self._create_loyalty_discount_setting(self.businessman, False)
        bc = self.create_customer_with_businessman(self.businessman)
        with self.assertRaises(ApplicationErrorException) as cx:
            discount_service.create_loyalty_discount(setting, bc.customer, {})
        ex = cx.exception
        self.assertEqual(ex.http_message, ApplicationErrorCodes.OPTION_IS_DISABLED)

    def test_create_loyalty_discounts_raises_exception_not_enough_points(self):
        bc = self.create_customer_with_businessman(self.businessman)
        setting = self._create_loyalty_discount_setting(self.businessman, True)
        point = self._create_customer_point(self.businessman, bc.customer, setting.point - 1)
        with self.assertRaises(ApplicationErrorException) as cx:
            discount_service.create_loyalty_discount(setting, bc.customer, {})
        ex = cx.exception
        self.assertEqual(ex.http_message, ApplicationErrorCodes.NOT_ENOUGH_POINT_FOR_DISCOUNT)

    def test_create_loyalty_discounts_raises_exception_already_discount_exist(self):
        bc = self.create_customer_with_businessman(self.businessman)
        self._create_loyalty_discount(bc)
        setting = self._create_loyalty_discount_setting(self.businessman, True)
        error_dict = {}
        with self.assertRaises(ApplicationErrorException) as cx:
            discount_service.create_loyalty_discount(setting, bc.customer, error_dict)

        ex = cx.exception
        self.assertEqual(ex.http_message, error_dict)

    def test_inviter_discount_with_invited_has_no_purchase(self):
        discounts = discount_service.get_customer_discounts_for_businessman(self.invitation.businessman,
                                                                            self.invitation.inviter.customer)
        self.assertFalse(discounts.filter(used_for=Discount.USED_FOR_INVITATION).exists())

    def test_inviter_has_discount_with_invited_has_purchase(self):
        self._create_purchase(self.businessman, self.invitation.invited.customer)
        discounts = discount_service.get_customer_discounts_for_businessman(self.invitation.businessman,
                                                                            self.invitation.inviter.customer)
        self.assertTrue(discounts.filter(used_for=Discount.USED_FOR_INVITATION).exists())
        self.assertEqual(discounts.first().inviter_discount.inviter, self.invitation.inviter)

    def test_inviter_has_no_discount_when_is_deleted(self):
        self._create_purchase(self.businessman, self.invitation.invited.customer)
        self.delete_customer_for_businessman(self.invitation.businessman, self.invitation.inviter.customer)
        discounts = discount_service.get_customer_discounts_for_businessman(self.invitation.businessman,
                                                                            self.invitation.inviter.customer)
        self.assertFalse(discounts.count(), 0)

    def test_inviter_has_no_discount_when_invitation_blongs_to_another_businessman(self):
        b2 = self.create_businessman()
        # invited = self.create_customer_with_businessman(b2)
        invited = self.invitation.invited
        invited_new = self.add_customer_to_businessman(b2, self.invitation.invited.customer)
        inviter_new = self.add_customer_to_businessman(b2, self.invitation.inviter.customer)
        self._create_friend_invitation(b2, inviter_new, invited_new)
        CustomerPurchase.objects.create(amount=10, customer=invited.customer,
                                        businessman=b2)

        discounts = discount_service.get_customer_discounts_for_businessman(self.invitation.businessman,
                                                                            self.invitation.inviter.customer)

        self.assertFalse(discounts.filter(used_for=Discount.USED_FOR_INVITATION,
                                          inviter_discount__inviter=self.invitation.inviter).exists())

    def test_invited_discount(self):
        discounts = discount_service.get_customer_discounts_for_businessman(
            self.invitation.businessman,
            self.invitation.invited.customer)
        all_match = all(
            d.used_for == Discount.USED_FOR_INVITATION and d.invited_discount.invited == self.invitation.invited for d
            in discounts)
        self.assertTrue(all_match)

    def test_has_invited_discount_and_inviter_discount(self):
        invited_c = self.create_customer_with_businessman(self.invitation.businessman)
        self._create_friend_invitation(self.invitation.businessman, self.invitation.invited, invited_c)
        CustomerPurchase.objects.create(businessman=self.invitation.businessman, customer=invited_c.customer, amount=10)
        discounts = discount_service.get_customer_discounts_for_businessman(
            self.invitation.businessman,
            self.invitation.invited.customer)
        count = discounts.count()
        inviter_discount_count = discounts.filter(inviter_discount__inviter=self.invitation.invited).count()
        invited_discount_count = discounts.filter(invited_discount__invited=self.invitation.invited).count()
        self.assertEqual(count, 2)
        self.assertEqual(inviter_discount_count, 1)
        self.assertEqual(invited_discount_count, 1)

    def test_festival_discount(self):
        d = self._create_discount(self.businessman, Discount.USED_FOR_FESTIVAL)
        discounts = discount_service.get_customer_discounts_for_businessman(self.businessman,
                                                                            self.invitation.inviter.customer)
        fd = discounts.get(used_for=Discount.USED_FOR_FESTIVAL)
        self.assertEqual(fd, d)

    def test_festival_inviter_invited_discount(self):
        self._create_discount(self.businessman, Discount.USED_FOR_FESTIVAL)
        invited_c = self.create_customer_with_businessman(self.invitation.businessman)
        self._create_friend_invitation(self.invitation.businessman, self.invitation.invited, invited_c)
        CustomerPurchase.objects.create(businessman=self.invitation.businessman, customer=invited_c.customer, amount=10)
        discounts = discount_service.get_customer_discounts_for_businessman(self.invitation.businessman,
                                                                            self.invitation.invited.customer)
        count = discounts.count()
        inviter_discount_count = discounts.filter(inviter_discount__inviter=self.invitation.invited).count()
        invited_discount_count = discounts.filter(invited_discount__invited=self.invitation.invited).count()
        festival_discount_count = discounts.filter(used_for=Discount.USED_FOR_FESTIVAL).count()
        self.assertEqual(count, 3)
        self.assertEqual(inviter_discount_count, 1)
        self.assertEqual(invited_discount_count, 1)
        self.assertEqual(festival_discount_count, 1)

    def test_customer_unused_discount_for_businessman(self):
        p = self._create_purchase(self.businessman, self.invitation.invited.customer)
        PurchaseDiscount.objects.create(discount=self.invitation.invited_discount, purchase=p)
        discount = discount_service.get_customer_unused_discounts_for_businessman(self.businessman,
                                                                                  self.invitation.invited.customer)
        self.assertEqual(discount.count(), 0)

    def test_customer_available_discount_for_businessman_discount_expired(self):
        d = self.invitation.invited_discount
        d.expires = True
        d.expire_date = self.create_time_in_past()
        d.save()
        discounts = discount_service.get_customer_available_discounts_for_businessman(self.businessman,
                                                                                      self.invitation.invited.customer)
        self.assertEqual(discounts.count(), 0)

    def test_customer_available_discount_for_businessman_festival_deleted(self):
        past = self.create_time_in_past()
        d = self._create_discount(businessman=self.businessman, used_for=Discount.USED_FOR_FESTIVAL)
        f = Festival.objects.create(businessman=self.businessman, marked_as_deleted_for_businessman=True,
                                    start_date=past, end_date=timezone.now())
        f.discount = d
        f.save()
        discounts = discount_service.get_customer_available_discounts_for_businessman(self.businessman,
                                                                                      self.invitation.invited.customer)
        self.assertFalse(discounts.filter(used_for=Discount.USED_FOR_FESTIVAL).exists())

    def test_customer_available_discount_for_businessman_discount_used(self):
        p = self._create_purchase(self.businessman, self.invitation.invited.customer)
        PurchaseDiscount.objects.create(discount=self.invitation.invited_discount, purchase=p)
        discount = discount_service.get_customer_available_discounts_for_businessman(self.businessman,
                                                                                     self.invitation.invited.customer)
        self.assertEqual(discount.count(), 0)

    def test_can_customer_use_discount(self):
        can_use = discount_service.can_customer_use_discount(self.businessman,
                                                             self.invitation.inviter_discount,
                                                             self.invitation.inviter.customer
                                                             )
        self.assertFalse(can_use)

    def test_has_customer_any_discount(self):
        has_discount = discount_service.has_customer_any_discount(self.businessman,
                                                                  self.invitation.inviter.customer)
        self.assertFalse(has_discount)

    def test_get_customer_used_discounts_for_businessman(self):
        c = self.invitation.invited
        p = self._create_purchase(self.businessman, self.invitation.invited.customer)
        PurchaseDiscount.objects.create(discount=self.invitation.invited_discount, purchase=p)
        discounts = discount_service.get_customer_used_discounts_for_businessman(self.businessman,
                                                                                 c.customer)
        exist = discounts.filter(invited_discount__invited=c).exists()
        self.assertTrue(exist)
        self.assertEqual(discounts.count(), 1)

    def test_delete_customer_from_discount_invalid_discount_id(self):
        c = self.invitation.invited
        result = discount_service.delete_customer_from_discount(self.businessman, -1, c.id)
        self.assertFalse(result[0])

    def test_delete_customer_from_discount_invalid_customer_id(self):
        c = self.invitation.invited
        d = self.invitation.invited_discount
        p = self._create_purchase(self.businessman, c.customer)
        PurchaseDiscount.objects.create(discount=d, purchase=p)
        result = discount_service.delete_customer_from_discount(self.businessman,
                                                                d.id,
                                                                -1)
        self.assertTrue(result[0])
        self.assertFalse(result[1])

    def test_delete_customer_from_discount(self):
        c = self.invitation.invited
        d = self.invitation.invited_discount
        p = self._create_purchase(self.businessman, c.customer)
        PurchaseDiscount.objects.create(discount=d, purchase=p)
        result = discount_service.delete_customer_from_discount(self.businessman,
                                                                d.id,
                                                                c.customer.id)
        self.assertTrue(result[0])
        self.assertTrue(result[1])
        self.assertEqual(result[2], d)
        self.assertEqual(result[3], p)

    def test_get_used_festival_discounts_in_month(self):
        d = self._create_discount(self.businessman, Discount.USED_FOR_FESTIVAL)
        c = self.invitation.invited
        p = self._create_purchase(self.businessman, c.customer)
        PurchaseDiscount.objects.create(discount=d, purchase=p)
        PurchaseDiscount.objects.create(discount=self.invitation.invited_discount, purchase=p)
        discounts = discount_service.get_used_festival_discounts_in_month(self.businessman, timezone.now())
        self.assertEqual(discounts.count(), 1)
        first = discounts.first()
        self.assertEqual(first.used_for, Discount.USED_FOR_FESTIVAL)

    def test_get_used_invitation_discounts_in_month(self):
        d = self._create_discount(self.businessman, Discount.USED_FOR_FESTIVAL)
        c = self.invitation.invited
        p = self._create_purchase(self.businessman, c.customer)
        PurchaseDiscount.objects.create(discount=d, purchase=p)
        PurchaseDiscount.objects.create(discount=self.invitation.invited_discount, purchase=p)
        discounts = discount_service.get_used_invitation_discounts_in_month(self.businessman, timezone.now())
        self.assertEqual(discounts.count(), 1)
        first = discounts.first()
        self.assertEqual(first.used_for, Discount.USED_FOR_INVITATION)

    def test_loyalty_discount(self):
        bc = self.create_customer_with_businessman(self.businessman)
        d = self._create_loyalty_discount(bc)
        discounts = discount_service.get_customer_discounts_for_businessman(self.businessman, bc.customer)
        self._assert_loyalty_discount_result(discounts, bc)

    def test_loyalty_other_customer_have_discount(self):
        bc = self.create_customer_with_businessman(self.businessman)
        bc2 = self.create_customer_with_businessman(self.businessman)
        d = self._create_loyalty_discount(bc)
        d2 = self._create_loyalty_discount(bc2)
        discounts = discount_service.get_customer_discounts_for_businessman(self.businessman, bc.customer)
        self._assert_loyalty_discount_result(discounts, bc)

    def test_other_businessman_have_loyalty_discount_for_same_customer(self):
        bc = self.create_customer_with_businessman(self.businessman)
        bc2 = self.create_businessman_with_businessmancustomer(bc.customer)
        d = self._create_loyalty_discount(bc)
        self._create_loyalty_discount(bc2)
        discounts = discount_service.get_customer_discounts_for_businessman(bc.businessman, bc.customer)
        self._assert_loyalty_discount_result(discounts, bc)
        self.assertEqual(discounts[0], d)

    def test_loyalty_discount_customer_is_deleted(self):
        bc = self.create_customer_with_businessman(self.businessman)
        bc2 = self.create_businessman_with_businessmancustomer(bc.customer)
        d = self._create_loyalty_discount(bc)
        self._create_loyalty_discount(bc2)
        self.delete_customer_for_businessman(bc.businessman, bc.customer)
        discounts = discount_service.get_customer_discounts_for_businessman(bc.businessman, bc.customer)
        self.assertEqual(discounts.count(), 0)

    def _assert_loyalty_discount_result(self, discounts, bc: BusinessmanCustomer):
        self.assertEqual(len(discounts), 1)
        d = discounts.first()
        self.assertEqual(d.used_for, Discount.USED_FOR_LOYALTY)
        exclusives = list(d.exclusive_customers.all())
        self.assertEqual(len(exclusives), 1)
        self.assertEqual(exclusives[0].businessman_customer, bc)
        self.assertEqual(exclusives[0].discount, d)


class CustomerDiscountServiceTestClass(BaseDiscountServiceTestClass):

    def test_return_is_not_none(self):
        result = customer_discount_service.get_customer_discounts(self.invitation.invited.customer)
        self.assertTrue(result is not None)

    def test_invited_discount(self):
        c = self.invitation.invited
        discounts = customer_discount_service.get_customer_discounts(c.customer)
        count = discounts.count()
        exist = discounts.filter(used_for=Discount.USED_FOR_INVITATION, invited_discount__invited=c)
        self.assertEqual(count, 1)
        self.assertTrue(exist)

    def test_invited_discount_on_invited_is_deleted(self):
        c = self.invitation.invited
        self.delete_customer_for_businessman(self.businessman, c.customer)
        b = self.create_businessman()
        invited_new = self.add_customer_to_businessman(b, c.customer)
        c2 = self.create_customer_with_businessman(b)
        fi = self._create_friend_invitation(b, c2, invited_new)
        discounts = customer_discount_service.get_customer_discounts(c.customer)
        exist = discounts.filter(used_for=Discount.USED_FOR_INVITATION,
                                 invited_discount__invited__customer=c.customer,
                                 businessman=self.businessman
                                 ).exists()

        self.assertFalse(exist)
        self.assertEqual(discounts.count(), 1)

    def test_inviter_discount(self):
        c = self.invitation.inviter
        discount = customer_discount_service.get_customer_discounts(c.customer)
        self.assertEqual(discount.count(), 1)
        exist = discount.filter(used_for=Discount.USED_FOR_INVITATION, inviter_discount__inviter=c).exists()
        self.assertTrue(exist)

    def test_inviter_discount_inviter_deleted(self):
        c = self.invitation.inviter
        self.delete_customer_for_businessman(self.businessman, c.customer)
        b = self.create_businessman()
        inviter_new = self.add_customer_to_businessman(b, c.customer)
        invited_new = self.add_customer_to_businessman(b, self.invitation.invited.customer)
        self._create_friend_invitation(b, inviter_new, invited_new)
        discounts = customer_discount_service.get_customer_discounts(c.customer)
        exist = discounts.filter(used_for=Discount.USED_FOR_INVITATION,
                                 inviter_discount__inviter=c,
                                 businessman=self.businessman
                                 ).exists()
        self.assertFalse(exist)
        self.assertEqual(discounts.count(), 1)

    def test_festival_discount(self):
        d = self._create_discount(self.businessman, Discount.USED_FOR_FESTIVAL)
        self._create_festival(self.businessman, d)
        b = self.create_businessman()
        d2 = self._create_discount(b, Discount.USED_FOR_FESTIVAL)
        self._create_festival(b, d2)
        self.add_customer_to_businessman(b, self.invitation.inviter.customer)
        self.delete_customer_for_businessman(b, self.invitation.inviter.customer)
        discounts = customer_discount_service.get_customer_discounts(self.invitation.inviter.customer)
        count = discounts.filter(businessman=self.businessman, used_for=Discount.USED_FOR_FESTIVAL).count()
        self.assertEqual(count, 1)

    def test_get_customer_available_discount_expired(self):
        c = self.invitation.inviter.customer
        d = self._create_discount(self.businessman, used_for=Discount.USED_FOR_FESTIVAL)
        past = self.create_time_in_past()
        d.expires = True
        d.expire_date = past
        d.save()
        discounts = customer_discount_service.get_customer_available_discount(c)
        exist = discounts.filter(id=d.id).exists()
        self.assertFalse(exist)

    def test_get_customer_available_discount_festival_deleted(self):
        d = self._create_discount(self.businessman, Discount.USED_FOR_FESTIVAL)
        f = self._create_festival(self.businessman, d)
        f.marked_as_deleted_for_businessman = True
        f.save()
        c = self.invitation.inviter.customer
        discounts = customer_discount_service.get_customer_available_discount(c)
        exist = discounts.filter(id=d.id).exists()
        self.assertFalse(exist)

    def test_get_customer_available_discount_purchase_added(self):
        c = self.invitation.inviter.customer
        p = self._create_purchase(self.businessman, c)
        d = self._create_discount(self.businessman, Discount.USED_FOR_FESTIVAL)
        self._create_festival(self.businessman, d)
        PurchaseDiscount.objects.create(discount=d, purchase=p)
        discounts = customer_discount_service.get_customer_available_discount(c)
        exist = discounts.filter(id=d.id).exists()
        self.assertFalse(exist)

    def test_inviter_discount_invited_has_purchase_for_another_businessman(self):
        b = self.create_businessman()
        invited = self.invitation.invited.customer
        self.add_customer_to_businessman(b, invited)
        self._create_purchase(b, invited)
        d = customer_discount_service.get_customer_discounts(self.invitation.inviter.customer)
        self.assertEqual(d.count(), 1)

    def test_is_invitation_discount_invited_has_purchase_not_invitation_discount(self):
        d = self._create_discount(self.businessman, Discount.USED_FOR_FESTIVAL)
        inviter_c = self.invitation.inviter.customer
        result = customer_discount_service.is_invitation_inviter_discount_and_invited_has_purchase(d, inviter_c)
        self.assertFalse(result[0])
        self.assertFalse(result[1])
        self.assertFalse(result[2])

    def test_is_invitation_discount_invited_has_purchase_customer_is_not_inviter(self):
        d = self.invitation.inviter_discount
        invited_c = self.invitation.invited.customer
        result = customer_discount_service.is_invitation_inviter_discount_and_invited_has_purchase(d, invited_c)
        self.assertTrue(result[0])
        self.assertFalse(result[1])
        self.assertFalse(result[2])

    def test_is_invitation_discount_invited_has_purchase_invited_has_0_purchase(self):
        d = self.invitation.inviter_discount
        inviter_c = self.invitation.inviter.customer
        result = customer_discount_service.is_invitation_inviter_discount_and_invited_has_purchase(d, inviter_c)
        self.assertTrue(result[0])
        self.assertTrue(result[1])
        self.assertFalse(result[2])

    def test_is_invitation_discount_invited_has_purchase_and_invited_has_purchase(self):
        invited_c = self.invitation.invited.customer
        inviter_c = self.invitation.inviter.customer
        d = self.invitation.inviter_discount
        CustomerPurchase.objects.create(businessman=self.invitation.businessman, customer=invited_c,
                                        amount=10)
        result = customer_discount_service.is_invitation_inviter_discount_and_invited_has_purchase(d,
                                                                                                   inviter_c)
        self.assertTrue(result[0])
        self.assertTrue(result[1])
        self.assertTrue(result[2])

    def test_loyalty_discount(self):
        bc = self.create_customer_with_businessman(self.businessman)
        d = self._create_loyalty_discount(bc)
        discounts = customer_discount_service.get_customer_discounts(bc.customer)
        self.assertEqual(discounts.count(), 1)
        self._assert_loyalty_discount_result(discounts, bc)

    def test_loyalty_discount_customer_is_deleted(self):
        bc = self.create_customer_with_businessman(self.businessman)
        bc2 = self.create_businessman_with_businessmancustomer(bc.customer)
        self._create_loyalty_discount(bc)
        self._create_loyalty_discount(bc2)
        self.delete_customer_for_businessman(bc.businessman, bc.customer)
        discounts = customer_discount_service.get_customer_discounts(bc.customer)
        self.assertEqual(discounts.count(), 1)
        self._assert_loyalty_discount_result(discounts, bc2)

    def test_loyalty_discount_other_businessman_discount_for_same_customer(self):
        bc = self.create_customer_with_businessman(self.businessman)
        bc2 = self.create_businessman_with_businessmancustomer(bc.customer)
        self._create_loyalty_discount(bc)
        self._create_loyalty_discount(bc2)
        discounts = customer_discount_service.get_customer_discounts(bc.customer)
        self.assertEqual(discounts.count(), 2)
        self._assert_loyalty_discount_result(discounts, bc)
        self._assert_loyalty_discount_result(discounts, bc2)

    def _assert_loyalty_discount_result(self, discounts, bc: BusinessmanCustomer):
        filtered = discounts.filter(exclusive_customers__businessman_customer=bc)
        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered[0].used_for, Discount.USED_FOR_LOYALTY)
        c = filtered.first().exclusive_customers
        self.assertEqual(c.count(), 1)
        self.assertEqual(c.first().businessman_customer, bc)
