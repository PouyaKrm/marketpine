from django.core.exceptions import ObjectDoesNotExist

from content_marketing.models import Post
from content_marketing.services import content_marketing_service
from customer_application.exceptions import CustomerServiceException
from users.models import Customer


class CustomerAppContentMarketingService:

    def retrieve_post_for_view(self, post_id: int, customer: Customer):

        try:
            p = self._get_post(post_id)
            self._set_views_for_post(p, customer)
            return p
        except ObjectDoesNotExist:
            CustomerServiceException.for_record_not_found()

    def toggle_post_like(self, post_id: int, customer: Customer) -> Post:

        p = self._get_post(post_id)
        content_marketing_service.toggle_like(p, customer)
        return p

    def _set_views_for_post(self, post: Post, customer: Customer):
        post.increase_views()
        if not customer.is_anonymous:
            content_marketing_service.set_post_viewed_by_customer(post, customer)

    def _get_post(self, post_id: int) -> Post:
        try:
            return content_marketing_service.retrieve_post(post_id)
        except ObjectDoesNotExist:
            CustomerServiceException.for_record_not_found()


customer_content_service = CustomerAppContentMarketingService()
