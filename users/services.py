from users.models import Businessman


class BusinessmanService:

    def is_page_id_unique(self, user: Businessman, page_id) -> bool:
        return not Businessman.objects.filter(page_id=page_id).exclude(id=user.id).exists()

    def get_businessman_by_page_id(self, page_id) -> Businessman:
        return Businessman.objects.get(page_id=page_id)


businessman_service = BusinessmanService()
