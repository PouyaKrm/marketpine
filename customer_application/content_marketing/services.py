from django.core.exceptions import ObjectDoesNotExist

from content_marketing.models import Post, Comment
from content_marketing.services import content_marketing_service
from customer_application.exceptions import CustomerServiceException
from customer_application.services import customer_data_service
from users.models import Customer


class CustomerAppContentMarketingService:

    def get_all_posts(self, businessman_id_page_id: str):

        if businessman_id_page_id is not None:
            b = customer_data_service.get_businessman_by_id_or_page_id(businessman_id_page_id)
            q = content_marketing_service.get_businessman_all_posts(b)
        else:
            q = content_marketing_service.get_all_posts()
        return q.filter(confirmation_status=Post.CONFIRM_STATUS_ACCEPTED)

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

    def get_post_comments(self, post_id: int):
        try:
            p = self._get_post(post_id)
            return p.comments.order_by('-create_date')
        except ObjectDoesNotExist:
            CustomerServiceException.for_record_not_found()

    def add_comment(self, customer: Customer, post_id: int, body: str) -> Comment:
        try:
            return content_marketing_service.add_comment(customer, post_id, body)
        except ObjectDoesNotExist:
            CustomerServiceException.for_record_not_found()

    def _set_views_for_post(self, post: Post, customer: Customer):
        post.increase_views()
        if not customer.is_anonymous:
            content_marketing_service.set_post_viewed_by_customer(post, customer)

    def _get_post(self, post_id: int) -> Post:
        try:
            return content_marketing_service.get_accepted_post_by_post_id(post_id)
        except ObjectDoesNotExist:
            CustomerServiceException.for_record_not_found()


customer_content_service = CustomerAppContentMarketingService()
