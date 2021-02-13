from django.shortcuts import get_object_or_404
from rest_framework.request import Request

from common.util import create_link
from content_marketing.models import Post, PostConfirmationStatus
from customers.services import customer_service
from smspanel.services import sms_message_service
from users.models import Customer, Businessman


class ContentMarketingService:

    def create_post(self, request: Request, post_data: dict) -> Post:
        send_sms = post_data.get('send_sms')
        send_pwa = post_data.get('send_pwa')
        template = None
        if send_sms:
            template = post_data.pop('notif_sms_template')

        post = Post.objects.create(businessman=request.user, **post_data)

        if send_sms:
            post.notif_sms = sms_message_service.content_marketing_message_status_cancel(user=request.user,
                                                                                         template=template)
        if send_pwa:
            self.send_post_pwa_notif(post)

        post.video_url = create_link(post.videofile.url, request)
        post.save()
        return post

    def get_businessman_all_posts(self, user: Businessman):
        return Post.objects.filter(businessman=user).all()

    def has_businessman_any_pending_post(self, user: Businessman) -> bool:
        return Post.objects.filter(businessman=user, confirmation_status=Post.CONFIRM_STATUS_PENDING).exists()

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

    def send_post_pwa_notif(self, post: Post):
        return
        post.send_pwa = True
        c = customer_service.get_businessman_customers(request.user)
        post.remaining_pwa_notif_customers.set(c)

content_marketing_service = ContentMarketingService()
