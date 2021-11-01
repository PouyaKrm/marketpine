import pytest

from customers.services import add_customer
from users.models import Customer, BusinessmanCustomer
from customers.tests.test_conf import *

pytestmark = pytest.mark.unit


def mock__get_businessman_customer_relation(mocker, bc: BusinessmanCustomer):
    return mocker.patch('customers.services._get_businessman_customer_relation', return_value=bc)


def mock__join_customer_to_businessman(mocker, customer: Customer):
    return mocker.patch('customers.services._join_customer_to_businessman', return_value=customer)


def mock__create_customer_join_to_businessman(mocker):
    return mocker.patch('customers.services._create_customer_join_to_businessman', return_value=Customer(phone='phone'))


@pytest.fixture
def mocked_phone_number_unique_for_register(mocker):
    mocker.patch('customers.services._check_is_phone_number_unique_for_register', return_value=None)


def test__add_customer__customer_already_deleted(mocker, mocked_customer_deleted,
                                                 mocked_phone_number_unique_for_register):
    relation_mock = mock__get_businessman_customer_relation(mocker, mocked_customer_deleted.businessman_customer)
    join_mock = mock__join_customer_to_businessman(mocker, mocked_customer_deleted.customer)
    create_customer_mock = mock__create_customer_join_to_businessman(mocker)

    result = add_customer(businessman=mocked_customer_deleted.businessman, phone=mocked_customer_deleted.customer.phone)

    relation_mock.assert_called_once_with(businessman=mocked_customer_deleted.businessman,
                                          customer=mocked_customer_deleted.customer)
    join_mock.assert_not_called()
    create_customer_mock.assert_not_called()
    assert not mocked_customer_deleted.businessman_customer.is_deleted
    assert result == mocked_customer_deleted.customer


def test__add_customer__customer_is_created(mocker, mocked_customer_deleted, mocked_businessman,
                                            mocked_phone_number_unique_for_register):
    b = mocked_businessman.first()
    phone = 'fake'
    full_name = ''
    relation_mock = mock__get_businessman_customer_relation(mocker, None)
    join_mock = mock__join_customer_to_businessman(mocker, None)
    create_customer_mock = mock__create_customer_join_to_businessman(mocker)

    result = add_customer(businessman=b, phone=phone, full_name=full_name)

    relation_mock.assert_not_called()
    join_mock.assert_not_called()
    create_customer_mock.assert_called_once_with(
        businessman=b,
        joined_by=BusinessmanCustomer.JOINED_BY_PANEL,
        phone=phone,
        full_name=full_name,
        groups=None,
        low_credit_error_code=None
    )
    assert result == create_customer_mock.return_value
