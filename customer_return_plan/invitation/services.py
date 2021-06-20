from django.core.exceptions import ObjectDoesNotExist
from django.db.models.aggregates import Sum
from django.db.models.query_utils import Q

from customer_return_plan.invitation.models import FriendInvitationSettings, FriendInvitation
from customer_return_plan.models import Discount
from customer_return_plan.services import discount_service
from customers.services import customer_service
from smspanel.models import SMSMessage
from smspanel.services import sms_message_service
from users.models import Businessman, Customer


class FriendInvitationService:

    def try_create_invitation_setting(self, businessman: Businessman) -> (bool, FriendInvitationSettings):
        if not hasattr(businessman, 'friendinvitationsettings'):
            s = FriendInvitationSettings(businessman=businessman, percent_off=0, flat_rate_off=0, disabled=True,
                                         discount_type=FriendInvitationSettings.DISCOUNT_TYPE_PERCENT)
            s.save()
            return True, s

        return False, None

    def is_invitation_enabled(self, businessman: Businessman) -> bool:
        return not self.get_businessman_invitation_setting_or_create(businessman).disabled

    def is_friend_already_invited(self, businessman: Businessman, friend_phone: str) -> bool:
        return customer_service.customer_exists_by_phone(businessman, friend_phone)

    def create_invitation(self, businessman: Businessman, inviter: Customer, invited: Customer) -> Discount:
        inviter_bc = customer_service.get_businessmancustomer(businessman, inviter)
        invited_bc = customer_service.get_businessmancustomer(businessman, invited)
        invitation = FriendInvitation()
        settings = self.get_businessman_invitation_setting_or_create(businessman)
        inviter_discount = self._create_invitation_discount(settings, businessman)
        invited_discount = self._create_invitation_discount(settings, businessman)
        invitation.businessman = businessman
        invitation.inviter = inviter_bc
        invitation.invited = invited_bc
        invitation.inviter_discount = inviter_discount
        invitation.invited_discount = invited_discount
        invitation.sms_message = self._send_invitation_message(businessman, settings, invited)
        invitation.save()
        return inviter_discount

    def get_businessman_invitation_setting_or_create(self, businessman: Businessman):
        try:
            return FriendInvitationSettings.objects.get(businessman=businessman)
        except ObjectDoesNotExist:
            s = FriendInvitationSettings(businessman=businessman, percent_off=0, flat_rate_off=0, disabled=True,
                                         discount_type=FriendInvitationSettings.DISCOUNT_TYPE_PERCENT)
            s.save()
            return s

    def invitations_added_in_month(self, businessman: Businessman, date):
        return FriendInvitation.objects.filter(businessman=businessman,
                                               create_date__year=date.year,
                                               create_date__month=date.month,
                                               create_date__day=date.day)

    def get_businessman_all_invitations(self, businessman: Businessman, inviter_customer_id: int = None):
        query = FriendInvitation.objects.filter(businessman=businessman)
        if inviter_customer_id is not None:
            query = query.filter(inviter__customer__id=inviter_customer_id)
        return query.order_by('-create_date')

    def customer_all_invited_friend_purchases_sum(self, user: Businessman, inviter: Customer) -> int:
        result = FriendInvitation.objects.filter(businessman=user, inviter__customer=inviter) \
            .aggregate(
            purchase_sum=Sum(
                'invited__customer__purchases__amount',
                filter=Q(
                    invited__customer__purchases__businessman=user
                )
            )
        ).get(
            'purchase_sum'
        )
        if result is None:
            return 0
        return result

    def customer_total_invitations_count(self, customer: Customer):
        return FriendInvitation.objects.filter(inviter__customer=customer).count()

    def _create_invitation_discount(self, invite_settings: FriendInvitationSettings,
                                    businessman: Businessman) -> Discount:

        return discount_service.create_invitation_discount(businessman, False, invite_settings.discount_type, True,
                                                           percent_off=invite_settings.percent_off,
                                                           flat_rate_off=invite_settings.flat_rate_off
                                                           )

    def _send_invitation_message(self, businessman: Businessman, invitation_settings: FriendInvitationSettings,
                                 invited: Customer) -> SMSMessage:
        sms = sms_message_service.friend_invitation_message(businessman, invitation_settings.sms_template, invited)
        return sms

    def filter_invitation_by_discount(self, discount: Discount):
        return FriendInvitation.objects.filter(
            Q(inviter_discount=discount) | Q(invited_discount=discount)
        )


invitation_service = FriendInvitationService()
