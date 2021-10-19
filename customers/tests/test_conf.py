import pytest
from django_mock_queries.query import MockModel, MockSet


class BusinessmanCustomerMockResult:
    def __init__(self, businessman, customer, qs, mock):
        self.businessman = businessman
        self.customer = customer
        self.qs = qs
        self.mock = mock


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
        mock_bc = MockModel(mock_name='businessman customer 1', is_deleted=is_deleted)
        b = MockModel(mock_name='businessman 1')
        c = MockModel(mock_name='customer 1', phone='123', connected_businessmans=mock_bc, businessman=b, id=1)
        qs = MockSet(c)
        mock = mocker.patch('users.models.Customer.objects', qs)
        return BusinessmanCustomerMockResult(b, c, qs, mock)

    return create_mock


@pytest.fixture
def mocked_customer_deleted(create_mocked_customer):
    return create_mocked_customer(True)


@pytest.fixture
def mocked_customer(create_mocked_customer):
    return create_mocked_customer(False)
