from django.shortcuts import get_object_or_404

from content_marketing.models import Post, PostConfirmationStatus
from users.models import Customer, Businessman


class ContentMarketingService:

    def get_oldest_post_for_notification(self, customer: Customer) -> Post:
        p = Post.objects.filter(confirmation_status=PostConfirmationStatus.ACCEPTED,
                                   send_pwa=True,
                                   remaining_pwa_notif_customers=customer).order_by('creation_date').first()

        if p is not None:
            p.remaining_pwa_notif_customers.remove(customer)
        return p

    def get_post_by_id_or_404(self, user: Businessman, post_id: int):
        return get_object_or_404(Post, pk=post_id, businessman=user)

    def get_post_comments_by_post_id_or_404(self, user: Businessman, post_id: int):
        post = self.get_post_by_id_or_404(user, post_id)
        return post.comments.order_by('-create_date')


content_marketing_service = ContentMarketingService()
