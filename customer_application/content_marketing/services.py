from django.core.exceptions import ObjectDoesNotExist

from content_marketing.services import content_marketing_service
from customer_application.exceptions import CustomerServiceException
from users.models import Customer


class CustomerAppContentMarketingService:

    def get_post(self, post_id: int, customer: Customer):

        try:
            return content_marketing_service.retrieve_post_for_customer(post_id, customer)
        except ObjectDoesNotExist:
            CustomerServiceException.for_record_not_found()


customer_content_service = CustomerAppContentMarketingService()
