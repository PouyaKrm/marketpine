import re

from django.conf import settings
from users.models import Businessman

customer_frontend_paths = settings.CUSTOMER_APP_FRONTEND_PATHS

class BusinessmanService:

    def is_page_id_unique(self, user: Businessman, page_id: str) -> bool:
        return not Businessman.objects.filter(page_id=page_id.lower()).exclude(id=user.id).exists()

    def get_businessman_by_page_id(self, page_id: str) -> Businessman:
        return Businessman.objects.get(page_id=page_id.lower())

    def is_page_id_predefined(self, page_id: str) -> bool:
        return page_id in customer_frontend_paths

    def is_page_id_pattern_valid(self, page_id) -> bool:
        match = re.search(r'^\d*[a-zA-Z_-]+[a-zA-Z0-9_-]*$', page_id)
        return match is not None


businessman_service = BusinessmanService()
