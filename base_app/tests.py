import random
from abc import ABC
from datetime import datetime
from typing import Tuple, List

import pytest
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

    def create_businessman_with_businessmancustomer(self, customer: Customer) -> BusinessmanCustomer:
        b = self.create_businessman()
        return BusinessmanCustomer.objects.create(businessman=b, customer=customer)


def random_mobile_phone() -> str:
    base = '09'
    base23 = random.randint(1, 10).__str__() + random.randint(0, 10).__str__()
    result = base + base23
    for i in range(7):
        r = random.randint(0, 10).__str__()
        result = result + r

    return result


@pytest.fixture
def create_businessman(db):
    profile = fake.profile()
    fake_email = fake.email()

    def create_user(
            username=profile['username'],
            email=fake_email,
            is_active=True,
            business_name=fake.name()
    ) -> Businessman:
        return Businessman.objects.create(
            username=username, email=email,
            is_active=is_active,
            business_name=business_name,
            phone=random_mobile_phone()
        )

    return create_user


@pytest.fixture
def businessman_1(db, create_businessman) -> Businessman:
    return create_businessman()


@pytest.fixture
def businessman_2(db, create_businessman) -> Businessman:
    return create_businessman()


@pytest.fixture
def create_customer(db):
    def createc(
            phone=random_mobile_phone(),
            full_name=fake.name()
    ) -> Customer:
        return Customer.objects.create(phone=phone, full_name=full_name)

    return createc


@pytest.fixture
def customer_1(db, create_customer) -> Customer:
    return create_customer(phone=random_mobile_phone())


@pytest.fixture
def customer_2(db, create_customer) -> Customer:
    return create_customer(phone=random_mobile_phone())


#
# @pytest.fixture
# def customers_list_1(db, create_customer) -> List[Customer]:
#     result = []
#     for i in range(10):
#         result.append(create_customer(phone=random_mobile_phone()))
#     return result


@pytest.fixture
def create_businessman_new_customer(db, create_customer):
    def create_bc(
            businessman: Businessman,
            is_deleted=False
    ) -> BusinessmanCustomer:
        c = create_customer(phone=random_mobile_phone())
        return BusinessmanCustomer.objects.create(businessman=businessman, customer=c, is_deleted=is_deleted)

    return create_bc


@pytest.fixture
def create_new_businessman_new_customer(db, create_businessman_new_customer, create_businessman):
    def create_bc(
            is_deleted=False
    ) -> BusinessmanCustomer:
        b = create_businessman()
        return create_businessman_new_customer(b, is_deleted)

    return create_bc


@pytest.fixture
def create_businessman_with_customers(db, create_businessman_new_customer, create_businessman):
    def create_bcs(
            seed=5,
            is_deleted=False
    ) -> List[BusinessmanCustomer]:
        b = create_businessman()
        result = []
        for i in range(seed):
            bc = create_businessman_new_customer(b, is_deleted)
            result.append(bc)
        return result

    return create_bcs


@pytest.fixture
def businessman_with_customer(db, create_businessman_with_customers) -> List[BusinessmanCustomer]:
    return create_businessman_with_customers()


@pytest.fixture
def businessman_with_customer_tuple(db, create_businessman_with_customers) -> Tuple[Businessman, List[Customer]]:
    bcs = create_businessman_with_customers()
    customers = list(map(lambda e: e.customer, bcs))
    return bcs[0].businessman, customers


@pytest.fixture
def businessman_with_single_customer_tuple(db, create_businessman, create_businessman_new_customer):
    b = create_businessman()
    bc = create_businessman_new_customer(b)
    return b, bc.customer
