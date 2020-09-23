from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from customer_return_plan.festivals.models import Festival
from smspanel.services import SendSMSMessage
from users.models import Businessman, Customer


class FestivalService:

    def delete_festival_by_festival_id(self, businessman: Businessman, festival_id: int) -> (bool, Festival):
        try:
            festival = Festival.objects.get(businessman=businessman, id=festival_id)
        except ObjectDoesNotExist:
            return False, None
        if not festival.is_expired() and festival.message_sent:
            return False, None
        if festival.has_any_one_used_festival():
            festival.mark_as_deleted()
        else:
            festival.delete()
            festival.discount.delete()
        return True, festival

    def festival_by_name_exists(self, businessman: Businessman, festival_name: str) -> bool:

        return Festival.objects.filter(businessman=businessman, name=festival_name) \
            .exclude(marked_as_deleted_for_businessman=True).exists()

    def get_businessman_all_undeleted_festivals(self, businessman: Businessman):
        return Festival.objects.filter(businessman=businessman, marked_as_deleted_for_businessman=False) \
            .order_by('-create_date').all()

    def get_businessman_festivals_filtered_by_discount_code(self, businessman: Businessman, discount_code: str):
        return Festival.objects.filter(businessman=businessman, discount__discount_code__contains=discount_code) \
            .order_by('-create_date')

    def send_festival_message_by_festival_id_if_festival_is_not_deleted_expired_message_sent(self,
                                                                                             businessman: Businessman,
                                                                                             festival_id: int) -> (
    bool, bool):
        try:
            festival = Festival.objects.get(businessman=businessman, id=festival_id)
        except ObjectDoesNotExist:
            return False, False

        if festival.message_sent or festival.is_expired():
            return True, False

        SendSMSMessage().set_message_to_pending(festival.sms_message)
        festival.message_sent = True
        festival.save()

        return True, True

    def get_oldest_active_festival(self, businessman: Businessman) -> Festival:
        return Festival.objects.filter(businessman=businessman).order_by('create_date').first()

    def get_customer_latest_festival_for_notif(self, customer: Customer) -> Festival:
        f = Festival.objects.filter(send_pwa_notif=True,
                                    marked_as_deleted_for_businessman=False,
                                    start_date__lte=timezone.now(),
                                    end_date__gt=timezone.now(),
                                    remaining_pwa_notif_customers=customer).order_by('create_date').first()
        if f is not None:
            f.remaining_pwa_notif_customers.remove(customer)
        return f


festival_service = FestivalService()
