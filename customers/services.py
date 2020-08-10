from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import get_object_or_404

from users.models import Customer, Businessman, BusinessmanCustomer


class CustomerService:

    def customer_exists(self, user: Businessman, phone: str) -> bool:
        return Customer.objects.filter(businessmans=user, phone=phone).exists()

    def customer_exists_by_id(self, user: Businessman, customer_id: int) -> bool:
        return Customer.objects.filter(businessman=user, id=customer_id).exists()

    def get_customer(self, user: Businessman, phone: str) -> Customer:
        return Customer.objects.get(businessman=user, phone=phone)

    def get_customer_by_id(self, customer_id: int) -> Customer:
        return Customer.objects.get(id=customer_id)

    def get_businessman_customer_by_id(self, user: Businessman, customer_id: int):
        return user.customers.get(id=customer_id)

    def get_customer_by_id_or_404(self, user: Businessman, customer_id: int):
        return get_object_or_404(Customer, businessmans=user, id=customer_id)

    def get_businessman_customers(self, user: Businessman):
        return Customer.objects.filter(businessmans=user).all()

    def get_bsuinessman_customers_by_ids(self, user: Businessman, customer_ids: [int]):
        return Customer.objects.filter(businessmans=user, id__in=customer_ids).all()

    def get_customer_by_phone(self, phone: str) -> Customer:
        return Customer.objects.get(phone=phone)

    def get_customer_by_businessman_and_phone(self, businessman: Businessman, phone: str) -> Customer:
        return businessman.customers.get(phone=phone)

    def add_customer(self, businessman: Businessman, phone: str, full_name='') -> Customer:
        # c = Customer.objects.create(phone=phone, full_name=full_name)
        try:
            c = Customer.objects.get(phone=phone)
            BusinessmanCustomer.objects.create(customer=c, businessman=businessman)
            return c
        except ObjectDoesNotExist:
            c = Customer.objects.create(phone=phone, full_name=full_name)
            BusinessmanCustomer.objects.create(customer=c, businessman=businessman)
            return c

    def get_date_joined(self, customer: Customer, businessman=Businessman):
        return BusinessmanCustomer.objects.get(customer=customer, businessman=businessman).create_date

    def is_phone_number_unique_for_register(self, businessman: Businessman, phone: str) -> bool:
        return not businessman.customers.filter(phone=phone).exists()

    def is_phone_number_unique_for_update(self, businessman: Businessman, customer: Customer, phone: str) -> bool:
        return not businessman.customers.filter(phone=phone).exclude(id=customer.id).exists()

    def delete_customer_for_businessman(self, businessman: Businessman, customer_id):
        BusinessmanCustomer.objects.filter(businessman=businessman, customer__id=customer_id).delete()


customer_service = CustomerService()
