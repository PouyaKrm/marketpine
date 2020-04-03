from customer_return_plan.invitation.models import FriendInvitationSettings
from users.models import Businessman


class FriendInvitationService:

    def try_create_invitation_setting(self, businessman: Businessman) -> (bool, FriendInvitationSettings):
        if not hasattr(businessman, 'friendinvitationsettings'):
            s = FriendInvitationSettings(businessman=businessman, percent_off=0, flat_rate_off=0, disabled=True,
                                         discount_type=FriendInvitationSettings.DISCOUNT_TYPE_PERCENT)
            s.save()
            return True, s

        return False, None
