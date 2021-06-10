from random import randint

# Create your tests here.
from django.utils import timezone

from base_app.tests import BaseTestClass
from customer_return_plan.festivals.models import Festival
from customer_return_plan.invitation.models import FriendInvitation
from customer_return_plan.models import Discount, PurchaseDiscount
from customer_return_plan.services import discount_service
from customerpurchase.models import CustomerPurchase
from users.models import Businessman, Customer


class BusinessmanDiscountTest(BaseTestClass):

    def setUp(self) -> None:
        bc = self.create_customer_and_businessman_with_relation()
        b = bc[0]
        self.businessman = b
        invited = self.create_customer_with_businessman(b)
        self.invitation = self._create_friend_invitation(b, bc[1], invited)

    def _create_discount(self, businessman: Businessman, used_for: str = Discount.USED_FOR_NONE) -> Discount:
        d = Discount()
        d.set_discount_data(randint(0, 10000).__str__(), Discount.DISCOUNT_TYPE_FLAT_RATE, 0, 1000)
        d.used_for = used_for
        d.businessman = businessman
        d.save()
        return d

    def _create_friend_invitation(self, businessman: Businessman, inviter: Customer,
                                  invited: Customer) -> FriendInvitation:
        inviter_discount = self._create_discount(businessman, Discount.USED_FOR_INVITATION)
        invited_discount = self._create_discount(businessman, Discount.USED_FOR_INVITATION)
        invitation = FriendInvitation()
        invitation.businessman = businessman
        invitation.inviter = inviter
        invitation.invited = invited
        invitation.inviter_discount = inviter_discount
        invitation.invited_discount = invited_discount
        invitation.save()
        return invitation

    def _create_purchase(self, businessman: Businessman, customer: Customer) -> CustomerPurchase:
        p = CustomerPurchase.objects.create(amount=10, customer=self.invitation.invited,
                                            businessman=self.invitation.businessman)
        return p

    def test_inviter_discount_with_invited_has_no_purchase(self):
        discounts = discount_service.get_customer_discounts_for_businessman(self.invitation.businessman,
                                                                            self.invitation.inviter)
        self.assertFalse(discounts.filter(used_for=Discount.USED_FOR_INVITATION).exists())

    def test_inviter_has_discount_with_invited_has_purchase(self):
        self._create_purchase(self.businessman, self.invitation.invited)
        discounts = discount_service.get_customer_discounts_for_businessman(self.invitation.businessman,
                                                                            self.invitation.inviter)
        self.assertTrue(discounts.filter(used_for=Discount.USED_FOR_INVITATION).exists())
        self.assertEqual(discounts.first().inviter_discount.inviter, self.invitation.inviter)

    def test_inviter_has_no_discount_when_is_deleted(self):
        self._create_purchase(self.businessman, self.invitation.invited)
        self.delete_customer_for_businessman(self.invitation.businessman, self.invitation.inviter)
        discounts = discount_service.get_customer_discounts_for_businessman(self.invitation.businessman,
                                                                            self.invitation.inviter)
        self.assertFalse(discounts.count(), 0)

    def test_inviter_has_no_discount_when_invitation_blongs_to_another_businessman(self):
        b2 = self.create_businessman()
        # invited = self.create_customer_with_businessman(b2)
        invited = self.invitation.invited
        self._create_friend_invitation(b2, self.invitation.inviter, invited)
        CustomerPurchase.objects.create(amount=10, customer=invited,
                                        businessman=b2)

        discounts = discount_service.get_customer_discounts_for_businessman(self.invitation.businessman,
                                                                            self.invitation.inviter)

        self.assertFalse(discounts.filter(used_for=Discount.USED_FOR_INVITATION,
                                          inviter_discount__inviter=self.invitation.inviter).exists())

    def test_invited_discount(self):
        discounts = discount_service.get_customer_discounts_for_businessman(self.invitation.businessman,
                                                                            self.invitation.invited)
        all_match = all(
            d.used_for == Discount.USED_FOR_INVITATION and d.invited_discount.invited == self.invitation.invited for d
            in discounts)
        self.assertTrue(all_match)

    def test_has_invited_discount_and_inviter_discount(self):
        invited_c = self.create_customer_with_businessman(self.invitation.businessman)
        self._create_friend_invitation(self.invitation.businessman, self.invitation.invited, invited_c)
        CustomerPurchase.objects.create(businessman=self.invitation.businessman, customer=invited_c, amount=10)
        discounts = discount_service.get_customer_discounts_for_businessman(self.invitation.businessman,
                                                                            self.invitation.invited)
        count = discounts.count()
        inviter_discount_count = discounts.filter(inviter_discount__inviter=self.invitation.invited).count()
        invited_discount_count = discounts.filter(invited_discount__invited=self.invitation.invited).count()
        self.assertEqual(count, 2)
        self.assertEqual(inviter_discount_count, 1)
        self.assertEqual(invited_discount_count, 1)

    def test_festival_discount(self):
        d = self._create_discount(self.businessman, Discount.USED_FOR_FESTIVAL)
        discounts = discount_service.get_customer_discounts_for_businessman(self.businessman, self.invitation.inviter)
        fd = discounts.get(used_for=Discount.USED_FOR_FESTIVAL)
        self.assertEqual(fd, d)

    def test_festival_inviter_invited_discount(self):
        self._create_discount(self.businessman, Discount.USED_FOR_FESTIVAL)
        invited_c = self.create_customer_with_businessman(self.invitation.businessman)
        self._create_friend_invitation(self.invitation.businessman, self.invitation.invited, invited_c)
        CustomerPurchase.objects.create(businessman=self.invitation.businessman, customer=invited_c, amount=10)
        discounts = discount_service.get_customer_discounts_for_businessman(self.invitation.businessman,
                                                                            self.invitation.invited)
        count = discounts.count()
        inviter_discount_count = discounts.filter(inviter_discount__inviter=self.invitation.invited).count()
        invited_discount_count = discounts.filter(invited_discount__invited=self.invitation.invited).count()
        festival_discount_count = discounts.filter(used_for=Discount.USED_FOR_FESTIVAL).count()
        self.assertEqual(count, 3)
        self.assertEqual(inviter_discount_count, 1)
        self.assertEqual(invited_discount_count, 1)
        self.assertEqual(festival_discount_count, 1)

    def test_customer_unused_discount_for_businessman(self):
        p = self._create_purchase(self.businessman, self.invitation.invited)
        PurchaseDiscount.objects.create(discount=self.invitation.invited_discount, purchase=p)
        discount = discount_service.get_customer_unused_discounts_for_businessman(self.businessman,
                                                                                  self.invitation.invited)
        self.assertEqual(discount.count(), 0)

    def test_customer_available_discount_for_businessman_discount_expired(self):
        d = self.invitation.invited_discount
        d.expires = True
        d.expire_date = self.create_time_in_past()
        d.save()
        discounts = discount_service.get_customer_available_discounts_for_businessman(self.businessman,
                                                                                      self.invitation.invited)
        self.assertEqual(discounts.count(), 0)

    def test_customer_available_discount_for_businessman_festival_deleted(self):
        past = self.create_time_in_past()
        d = self._create_discount(businessman=self.businessman, used_for=Discount.USED_FOR_FESTIVAL)
        f = Festival.objects.create(businessman=self.businessman, marked_as_deleted_for_businessman=True,
                                    start_date=past, end_date=timezone.now())
        f.discount = d
        f.save()
        discounts = discount_service.get_customer_available_discounts_for_businessman(self.businessman,
                                                                                      self.invitation.invited)
        self.assertFalse(discounts.filter(used_for=Discount.USED_FOR_FESTIVAL).exists())

    def test_customer_available_discount_for_businessman_discount_used(self):
        p = self._create_purchase(self.businessman, self.invitation.invited)
        PurchaseDiscount.objects.create(discount=self.invitation.invited_discount, purchase=p)
        discount = discount_service.get_customer_available_discounts_for_businessman(self.businessman,
                                                                                     self.invitation.invited)
        self.assertEqual(discount.count(), 0)

    def test_can_customer_use_discount(self):
        can_use = discount_service.can_customer_use_discount(self.businessman,
                                                             self.invitation.inviter_discount,
                                                             self.invitation.inviter
                                                             )
        self.assertFalse(can_use)

    def test_has_customer_any_discount(self):
        has_discount = discount_service.has_customer_any_discount(self.businessman,
                                                                  self.invitation.inviter)
        self.assertFalse(has_discount)

    def test_get_customer_used_discounts_for_businessman(self):
        c = self.invitation.invited
        p = self._create_purchase(self.businessman, self.invitation.invited)
        PurchaseDiscount.objects.create(discount=self.invitation.invited_discount, purchase=p)
        discounts = discount_service.get_customer_used_discounts_for_businessman(self.businessman,
                                                                                 c)
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
        p = self._create_purchase(self.businessman, c)
        PurchaseDiscount.objects.create(discount=d, purchase=p)
        result = discount_service.delete_customer_from_discount(self.businessman,
                                                                d.id,
                                                                -1)
        self.assertTrue(result[0])
        self.assertFalse(result[1])

    def test_delete_customer_from_discount(self):
        c = self.invitation.invited
        d = self.invitation.invited_discount
        p = self._create_purchase(self.businessman, c)
        PurchaseDiscount.objects.create(discount=d, purchase=p)
        result = discount_service.delete_customer_from_discount(self.businessman,
                                                                d.id,
                                                                c.id)
        self.assertTrue(result[0])
        self.assertTrue(result[1])
        self.assertEqual(result[2], d)
        self.assertEqual(result[3], p)
