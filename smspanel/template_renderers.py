from django.core.exceptions import ObjectDoesNotExist

from content_marketing.models import Post
from festivals.models import Festival
from invitation.models import FriendInvitation
from smspanel.models import SMSMessage, SMSMessageReceivers
import re

from users.models import Customer, Businessman


class BaseTemplateRenderer:

    def __init__(self, sms_message: SMSMessage):
        self._sms_message = sms_message
        self._businessman = sms_message.businessman

    def _customer_key_value(self, customer: Customer) -> dict:
        return {'customer_phone': customer.phone, 'full_name': customer.full_name}

    def _businessman_key_value(self) -> dict:
        return {'business_name': self._businessman.business_name}

    def _all_key_values(self, customer: Customer) -> dict:
        return {
            **self._businessman_key_value(),
            **self._customer_key_value(customer)
        }

    def _render(self, template: str, tag_key_value: dict):

        def replace(match):
            g = match.group(1)
            if not tag_key_value.keys().__contains__(g):
                return ''
            return tag_key_value.get(g)
        return re.sub('#([A-Za-z0-9_]+)', replace, template)

    def render(self, receiver: SMSMessageReceivers):
        return self._render(self._sms_message.message, {**self._businessman_key_value(),
                                                         **self._customer_key_value(receiver.customer)
                                                         })


class ContentMarketingTemplateRenderer(BaseTemplateRenderer):

    def __init__(self, sms_message: SMSMessage):

        super().__init__(sms_message)
        try:
            self.__post = Post.objects.get(notif_sms=sms_message)
        except ObjectDoesNotExist:
            raise ValueError('no record with provided sms message found')

    def render(self, receiver: SMSMessageReceivers):

        return self._render(self._sms_message.message,
                            {'video_link': self.__post.video_url,
                             **self._businessman_key_value(),
                             **self._customer_key_value(receiver.customer)
                             })


class FestivalTemplateRenderer(BaseTemplateRenderer):

    def __init__(self, sms_message: SMSMessage):
        super().__init__(sms_message)
        try:
            self.__festival = Festival.objects.get(sms_message=sms_message)
        except ObjectDoesNotExist:
            raise ValueError('no festival with provided sms_message found')

    def render(self, receiver: SMSMessageReceivers):

        festival_context = {
            'name': self.__festival.name,
            'start_date': self.__festival.start_date,
            'end_date': self.__festival.end_date,
            'discount_code': self.__festival.discount_code
        }

        return self._render(self._sms_message.message,
                            {**festival_context,
                             **self._all_key_values(receiver.customer)
                             })


class FriendInvitationTemplateRenderer(BaseTemplateRenderer):

    def __init__(self, sms_message: SMSMessage):
        super().__init__(sms_message)
        try:
            self.invitation = FriendInvitation.objects.get(sms_message=sms_message)
        except ObjectDoesNotExist:
            raise ValueError('no record exist on invitation with provided sms message')

    def render(self, receiver: SMSMessageReceivers):
        invite_context = {
            'inviter_phone': self.invitation.inviter.phone,
            'invited_phone': self.invitation.invited.phone,
            'invited_code': self.invitation.invited_discount_code,
            'invite_date': self.invitation.invitation_date
        }

        if self.invitation.is_percent_discount():
            invite_context = {**invite_context, 'percent_off': self.invitation.percent_off}
        else:
            invite_context = {**invite_context, 'flat_rate_off': self.invitation.flat_rate_off}

        return self._render(self._sms_message.message, {
            **invite_context,
            **self._all_key_values(receiver.customer)}
                            )


def get_renderer_object_based_on_sms_message_used(sms_message: SMSMessage) -> BaseTemplateRenderer:

    if sms_message.used_for == SMSMessage.USED_FOR_CONTENT_MARKETING:
        return ContentMarketingTemplateRenderer(sms_message)
    elif sms_message.used_for == SMSMessage.USED_FOR_FESTIVAL:
        return FestivalTemplateRenderer(sms_message)
    elif sms_message.used_for == SMSMessage.USED_FOR_FRIEND_INVITATION:
        return FriendInvitationTemplateRenderer(sms_message)
    else:
        return BaseTemplateRenderer(sms_message)

