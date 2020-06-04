from rest_framework.generics import get_object_or_404

from users.models import Customer, Businessman


class CustomerService:

    def customer_exists(self, user: Businessman, phone: str) -> bool:
        return Customer.objects.filter(businessman=user, phone=phone).exists()

    def customer_exists_by_id(self, user: Businessman, customer_id: int) -> bool:
        return Customer.objects.filter(businessman=user, id=customer_id).exists()

    def get_customer(self, user: Businessman, phone: str) -> Customer:
        return Customer.objects.get(businessman=user, phone=phone)

    def get_customer_by_id(self, customer_id: int) -> Customer:
        return Customer.objects.get(id=customer_id)

    def get_customer_by_id(self, user: Businessman, customer_id: int):
        return Customer.objects.get(businessman=user, id=customer_id)

    def get_customer_by_id_or_404(self, user: Businessman, customer_id: int):
        return get_object_or_404(Customer, businessman=user, id=customer_id)

    def get_businessman_customers(self, user: Businessman):
        return Customer.objects.filter(businessman=user).all()

customer_service = CustomerService()