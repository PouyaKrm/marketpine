from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework.request import Request

from base_app.error_codes import ApplicationErrorCodes
from common.util import create_link
from content_marketing.models import Post, ViewedPost, Like, Comment
from customers.services import customer_service
from panelprofile.services import sms_panel_info_service
from smspanel.models import SMSMessage
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
            post.notif_sms = self._send_notif_sms(post, template)
        if send_pwa:
            self._send_post_pwa_notif(post)

        post.video_url = create_link(post.videofile.url, request)
        post.save()
        return post

    def get_businessman_all_posts(self, user: Businessman):
        return Post.objects.filter(businessman=user).order_by('-create_date').all()

    def has_businessman_any_pending_post(self, user: Businessman) -> bool:
        return Post.objects.filter(businessman=user, confirmation_status=Post.CONFIRM_STATUS_PENDING).exists()

    def get_oldest_post_for_notification(self, customer: Customer) -> Post:
        p = Post.objects.filter(confirmation_status=Post.CONFIRM_STATUS_ACCEPTED,
                                send_pwa=True,
                                remaining_pwa_notif_customers=customer).order_by('create_date').first()

        if p is not None:
            p.remaining_pwa_notif_customers.remove(customer)
        return p

    def get_post_by_id_or_404(self, user: Businessman, post_id: int):
        return get_object_or_404(Post, pk=post_id, businessman=user)

    def get_post_comments_by_post_id_or_404(self, user: Businessman, post_id: int):
        post = self.get_post_by_id_or_404(user, post_id)
        return post.comments.order_by('-create_date')

    def get_post_comments_by_post_id(self, post_id: int):
        post = self.get_post_by_post_id(post_id)
        return post.comments.order_by('-create_date')

    def add_comment(self, customer: Customer, post_id, body: str) -> Comment:
        p = self.get_post_by_post_id(post_id)
        return Comment.objects.create(customer=customer, post=p, body=body)

    def _send_post_pwa_notif(self, post: Post):
        return
        post.send_pwa = True
        c = customer_service.get_businessman_customers(request.user)
        post.remaining_pwa_notif_customers.set(c)

    def _send_notif_sms(self, post: Post, template: str) -> SMSMessage:
        has_credit = sms_panel_info_service.has_valid_credit_to_send_to_all(post.businessman)
        if not has_credit:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.NOT_ENOUGH_SMS_CREDIT)
        sms = sms_message_service.content_marketing_message_status_cancel(user=post.businessman,
                                                                          template=template)
        return sms

    def get_all_posts(self):
        return Post.objects.order_by('-create_date').order_by('-customers_viewed__create_date')

    def get_post_by_post_id(self, post_id: int):
        return Post.objects.get(id=post_id)

    def get_accepted_post_by_post_id(self, post_id):
        return Post.objects.get(id=post_id, confirmation_status=Post.CONFIRM_STATUS_ACCEPTED)

    def set_post_viewed_by_customer(self, post: Post, customer: Customer):
        exist = ViewedPost.objects.filter(customer=customer, post=post).exists()
        if exist:
            return
        ViewedPost.objects.create(post=post, customer=customer)

    def toggle_like(self, post: Post, customer: Customer) -> Like:
        try:
            like = Like.objects.get(post=post, customer=customer)
            like.delete()
            return like
        except ObjectDoesNotExist:
            return Like.objects.create(post=post, customer=customer)

    def is_post_liked_by_customer(self, post: Post, customer: Customer) -> bool:
        return Like.objects.filter(post=post, customer=customer).exists()


content_marketing_service = ContentMarketingService()
