from random import randint

# Create your tests here.
from base_app.tests import BaseTestClass
from customer_return_plan.invitation.models import FriendInvitation
from customer_return_plan.models import Discount
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

    def test_inviter_discount_with_invited_has_no_purchase(self):
        discounts = discount_service.get_customer_discounts_for_businessman(self.invitation.businessman,
                                                                            self.invitation.inviter)
        self.assertFalse(discounts.filter(used_for=Discount.USED_FOR_INVITATION).exists())

    def test_inviter_has_discount_with_invited_has_purchase(self):
        CustomerPurchase.objects.create(amount=10, customer=self.invitation.invited,
                                        businessman=self.invitation.businessman)
        discounts = discount_service.get_customer_discounts_for_businessman(self.invitation.businessman,
                                                                            self.invitation.inviter)
        self.assertTrue(discounts.filter(used_for=Discount.USED_FOR_INVITATION).exists())
        self.assertEqual(discounts.first().inviter_discount.inviter, self.invitation.inviter)

    def test_inviter_has_no_discount_when_is_deleted(self):
        CustomerPurchase.objects.create(amount=10, customer=self.invitation.invited,
                                        businessman=self.invitation.businessman)
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
