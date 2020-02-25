from django.core.exceptions import ObjectDoesNotExist

from content_marketing.models import Post
from smspanel.models import SMSMessage, SMSMessageReceivers
import re

from users.models import Customer, Businessman


class BaseTemplateRenderer:

    def _customer_key_value(self, customer: Customer) -> dict:
        return {'customer_phone': customer.phone, 'full_name': customer.full_name}

    def _businessman_key_value(self, businessman: Businessman) -> dict:
        return {'business_name': businessman.business_name}

    def _render(self, template: str, tag_key_value: dict):

        def replace(match):
            g = match.group(1)
            if not tag_key_value.keys().__contains__(g):
                return ''
            return tag_key_value.get(g)
        return re.sub('#([A-Za-z0-9_]+)', replace, template)

    def render(self, sms_message: SMSMessage, receiver: SMSMessageReceivers):
        raise NotImplemented('render function must be implemented')


class ContentMarketingTemplateRenderer(BaseTemplateRenderer):

    def render(self, sms_message: SMSMessage, receiver: SMSMessageReceivers):
        try:
            post = Post.objects.get(customer_sms_message=sms_message)
        except ObjectDoesNotExist:
            raise ValueError('no record with provided sms message found')
        return self._render(sms_message.message,
                            {'video_link': post.video_url,
                             **self._businessman_key_value(sms_message.businessman),
                             **self._customer_key_value(receiver.customer)
                             })


def get_renderer_object_based_on_sms_message_used(used_for: str) -> BaseTemplateRenderer:
    return ContentMarketingTemplateRenderer()
