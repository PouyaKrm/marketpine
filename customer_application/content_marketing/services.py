from django.core.exceptions import ObjectDoesNotExist

from content_marketing.services import content_marketing_service
from customer_application.exceptions import CustomerServiceException
from users.models import Customer


class CustomerAppContentMarketingService:

    def retrieve_post_for_view(self, post_id: int, customer: Customer):

        try:
            p = content_marketing_service.retrieve_post(post_id)
            p.increase_views()
            return p
        except ObjectDoesNotExist:
            CustomerServiceException.for_record_not_found()


customer_content_service = CustomerAppContentMarketingService()
