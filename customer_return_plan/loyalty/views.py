from django.conf import settings
# Create your views here.
from rest_framework.request import Request
from rest_framework.views import APIView

from base_app.error_codes import ApplicationErrorException
from common.util.http_helpers import ok, bad_request
from .serializers import LoyaltySettingsSerializer
from .services import LoyaltyService

max_settings_per_businessman = settings.LOYALTY_SETTINGS['MAX_SETTINGS_NUMBER_PER_BUSINESSMAN']


class LoyaltySettingsRetrieveUpdateAPIVIew(APIView):

    def get(self, request: Request):
        obj = LoyaltyService.get_instance().get_businessman_loyalty_settings(request.user)
        serializer = LoyaltySettingsSerializer(obj)
        return ok(serializer.data)

    def put(self, request: Request):
        try:
            serializer = LoyaltySettingsSerializer(data=request.data)
            if not serializer.is_valid():
                return bad_request(serializer.errors)
            self._validate_loyality_settings_list(serializer)
            updated = LoyaltyService.get_instance().update_businessman_loyalty_settings(request.user,
                                                                                        serializer.validated_data)
            serializer = LoyaltySettingsSerializer(updated)
            return ok(serializer.data)
        except ApplicationErrorException as ex:
            return bad_request(ex.http_message)

    def _validate_loyality_settings_list(self, sr: LoyaltySettingsSerializer):

        discount_settings = sr.validated_data.get('discount_settings')
        is_active = sr.validated_data.get('is_active')

        if is_active and len(discount_settings) == 0:
            raise ApplicationErrorException("برای فعال کردن آپشن حداقل یک تخفیف را تنظیم کنید")

        if len(discount_settings) > max_settings_per_businessman:
            raise ApplicationErrorException('حداکثر تعداد تنظیمات تخفیف {} است'.format(max_settings_per_businessman))

        mapped_point = list(map(lambda e: e['point'], sr.validated_data.get('discount_settings')))
        point_set = set(mapped_point)
        if len(mapped_point) != len(point_set):
            raise ApplicationErrorException('امتیاز ها نباید تکراری باشد')
