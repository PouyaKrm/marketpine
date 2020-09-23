from content_marketing.models import Post, PostConfirmationStatus
from users.models import Customer


class ContentMarketingService:

    def get_oldest_post_for_notification(self, customer: Customer) -> Post:
        p = Post.objects.filter(confirmation_status=PostConfirmationStatus.ACCEPTED,
                                   send_pwa=True,
                                   remaining_pwa_notif_customers=customer).order_by('creation_date').first()

        if p is not None:
            p.remaining_pwa_notif_customers.remove(customer)
        return p


content_marketing_service = ContentMarketingService()
