from abc import ABC
from datetime import datetime
from typing import Tuple

from django.test import TestCase
from django.utils import timezone
from faker import Faker

# Create your tests here.
from users.models import Businessman, Customer, BusinessmanCustomer

fake = Faker('fa_IR')


class BaseTestClass(TestCase, ABC):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = fake

    def create_businessman(self) -> Businessman:
        return Businessman.objects.create(username=fake.profile()['username'])

    def create_customer(self) -> Customer:
        return Customer.objects.create(phone=fake.phone_number())

    def create_customer_with_businessman(self, businessman: Businessman) -> Customer:
        c = self.create_customer()
        BusinessmanCustomer.objects.create(businessman=businessman, customer=c)
        return c

    def create_customer_and_businessman_with_relation(self) -> Tuple[Businessman, Customer]:
        b = self.create_businessman()
        c = self.create_customer_with_businessman(b)
        return b, c

    def add_customer_to_businessman(self, businessman: Businessman, customer: Customer):
        BusinessmanCustomer.objects.create(businessman=businessman, customer=customer)

    def delete_customer_for_businessman(self, businessman: Businessman, customer: Customer):
        bc = BusinessmanCustomer.objects.get(customer=customer, businessman=businessman)
        bc.is_deleted = True
        bc.save()

    def create_time_in_past(self) -> datetime:
        return timezone.now() - timezone.timedelta(days=30)

    def create_customer_return_businessmancustomer(self, b: Businessman,
                                                   joined_by=BusinessmanCustomer.JOINED_BY_PANEL) -> BusinessmanCustomer:
        c = self.create_customer()
        return BusinessmanCustomer.objects.create(businessman=b, customer=c, joined_by=joined_by)
