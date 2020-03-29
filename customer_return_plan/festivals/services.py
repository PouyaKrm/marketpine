from django.core.exceptions import ObjectDoesNotExist

from customer_return_plan.festivals.models import Festival
from users.models import Businessman


class FestivalService:

    def delete_festival(self, businessman: Businessman, festival_id: int) -> (bool, Festival):
        try:
            festival = Festival.objects.get(businessman=businessman, id=festival_id)
        except ObjectDoesNotExist:
            return False, None
        festival.delete()
        festival.discount.delete()
        return True, festival

    def festival_by_name_exists(self, businessman: Businessman, festival_name: str) -> bool:

        return Festival.objects.filter(businessman=businessman, name=festival_name).exists()
