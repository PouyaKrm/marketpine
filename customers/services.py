from users.models import Customer, Businessman


class CustomerService:

    def customer_exists(self, user: Businessman, phone: str) -> bool:
        return Customer.objects.filter(businessman=user, phone=phone).exists()

    def get_customer(self, user: Businessman, phone: str) -> Customer:
        return Customer.objects.get(businessman=user, phone=phone)
