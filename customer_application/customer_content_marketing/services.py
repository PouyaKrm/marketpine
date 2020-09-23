from content_marketing.models import Post
from content_marketing.services import content_marketing_service
from users.models import Customer


class CustomerAppContentMarketingService:

    def get_post_for_notif(self, customer: Customer) -> Post:
        return content_marketing_service.get_oldest_post_for_notification(customer)

customer_app_content_marketing_service = CustomerAppContentMarketingService()
