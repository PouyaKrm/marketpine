import random

import pytest
from django.utils import timezone
from django_mock_queries.query import MockModel, MockSet
from faker import Faker

from users.models import BusinessmanCustomer


class BusinessmanCustomerMockResult:
    def __init__(self, *args, businessman, customer, businessman_customer, qs, mock):
        self.businessman = businessman
        self.customer = customer
        self.businessman_customer = businessman_customer
        self.qs = qs
        self.mock = mock


@pytest.fixture
def mocked_businessman(mocker) -> MockSet:
    fake = Faker()
    b = MockModel(mock_name="businessman_1", id=random.randint(1, 1000), businesss_name='fake_business name',
                  username=fake.profile()['username'])
    qs = MockSet(b)
    mocker.patch('users.models.Businessman.objects', qs)
    return qs


@pytest.fixture
def create_mocked_businessman_customer(mocker):
    def create_mock(is_deleted):
        b = MockModel(mock_name='businessman')
        c1 = MockModel(mock_name='customer1', phone='123', id=1)
        qs = MockSet(
            MockModel(mock_name="c1", businessman=b, is_deleted=is_deleted, customer=c1)
        )
        mock = mocker.patch('users.models.BusinessmanCustomer.objects', qs)
        return BusinessmanCustomerMockResult(b, c1, qs, mock)

    return create_mock


@pytest.fixture
def mocked_businessmancustomer(create_mocked_businessman_customer) -> BusinessmanCustomerMockResult:
    return create_mocked_businessman_customer(False)


@pytest.fixture
def mocked_businessmancustomer_deleted(create_mocked_businessman_customer) -> BusinessmanCustomerMockResult:
    return create_mocked_businessman_customer(True)


@pytest.fixture
def create_mocked_customer(mocker):
    def create_mock(is_deleted) -> BusinessmanCustomerMockResult:
        mock_bc = MockModel(mock_name='businessman customer 1', is_deleted=is_deleted, businessman=None, customer=None,
                            joined_by=BusinessmanCustomer.JOINED_BY_PANEL, create_date=timezone.now())
        b = MockModel(mock_name='businessman 1', customers=None)
        c = MockModel(mock_name='customer 1', phone='123', connected_businessmans=mock_bc, businessman=b, id=1)
        qs = MockSet(c)
        mock_bc.businessman = b
        mock_bc.customer = c
        mock_bc.save()
        mocker.patch('users.models.BusinessmanCustomer.objects', MockSet(mock_bc))
        mock = mocker.patch('users.models.Customer.objects', qs)
        return BusinessmanCustomerMockResult(businessman=b, customer=c, businessman_customer=mock_bc, qs=qs, mock=mock)

    return create_mock


@pytest.fixture
def mocked_customer_deleted(create_mocked_customer):
    return create_mocked_customer(True)


@pytest.fixture
def mocked_customer(create_mocked_customer):
    return create_mocked_customer(False)
