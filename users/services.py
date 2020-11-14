from users.models import Businessman


class BusinessmanService:

    def is_page_id_unique(self, user: Businessman, page_id) -> bool:
        return not Businessman.objects.filter(page_id=page_id).exclude(id=user.id).exists()


businessman_service = BusinessmanService()
