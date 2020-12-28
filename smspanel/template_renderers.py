from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from common.util import gregorian_to_jalali_str
from content_marketing.models import Post
from customer_return_plan.festivals.models import Festival
from customer_return_plan.invitation.models import FriendInvitation
from smspanel.models import SMSMessage, SMSMessageReceivers
import re
import jdatetime

page_url = settings.BUSINESSMAN_PAGE_URL

from users.models import Customer


class BaseTemplateRenderer:

    def __init__(self, sms_message: SMSMessage):
        self._sms_message = sms_message
        self._businessman = sms_message.businessman

    def _customer_key_value(self, customer: Customer) -> dict:
        return {'customer_phone': customer.phone, 'full_name': customer.full_name}

    def _businessman_key_value(self) -> dict:
        if self._businessman.is_page_id_set():
            p_id = self._businessman.page_id
        else:
            p_id = self._businessman.id
        return {
            'business_name': self._businessman.business_name,
            'page_url': page_url.format(p_id)
        }

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

        return re.sub('#([A-Za-z0-9_]+)', replace, template).replace(u'\xa0', u' ')

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
        start_date_j = gregorian_to_jalali_str(self.__festival.start_date)
        end_date_j = gregorian_to_jalali_str(self.__festival.end_date)
        festival_context = {
            'festival_name': self.__festival.name,
            'start_date': start_date_j,
            'end_date': end_date_j,
            'percent_off': self.__festival.discount.percent_off.__str__(),
            'flat_rate_off': self.__festival.discount.flat_rate_off.__str__(),
            'discount_code': self.__festival.discount.discount_code
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
        invited_discount = self.invitation.invited_discount
        invite_date = gregorian_to_jalali_str(self.invitation.create_date)
        if invited_discount.is_percent_discount():
            discount_amount = invited_discount.percent_off
        else:
            discount_amount = invited_discount.flat_rate_off
        invite_context = {
            'inviter_phone': self.invitation.inviter.phone,
            'invited_phone': self.invitation.invited.phone,
            'invited_full_name': self.invitation.invited.full_name,
            'inviter_full_name': self.invitation.inviter.full_name,
            'invited_discount_code': self.invitation.inviter_discount.discount_code,
            'invited_discount_amount': discount_amount.__str__(),
            'invite_date': invite_date
        }

        if self.invitation.invited_discount.is_percent_discount():
            invite_context = {**invite_context, 'percent_off': self.invitation.invited_discount.percent_off.__str__()}
        else:
            invite_context = {**invite_context, 'flat_rate_off': self.invitation.inviter_discount.flat_rate_off.__str__()}

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
