import pytest
from django.core.exceptions import ObjectDoesNotExist

from customers.services import add_customer, get_customer_by_phone_or_create
from users.models import Customer, BusinessmanCustomer
from customers.tests.test_conf import *
from base_app.tests import *

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


def test__add_customer__customer_already_deleted(mocker,
                                                 businessman_1_with_deleted_customer_tuple,
                                                 mocked_phone_number_unique_for_register):
    businessman = businessman_1_with_deleted_customer_tuple[0]
    customer = businessman_1_with_deleted_customer_tuple[1][0]
    bc = businessman_1_with_deleted_customer_tuple[2][0]
    relation_mock = mock__get_businessman_customer_relation(mocker, bc)
    join_mock = mock__join_customer_to_businessman(mocker, customer)
    create_customer_mock = mock__create_customer_join_to_businessman(mocker)

    result = add_customer(businessman=businessman, phone=customer.phone)

    relation_mock.assert_called_once_with(
        businessman=businessman,
        customer=customer
    )
    join_mock.assert_not_called()
    create_customer_mock.assert_not_called()
    assert not bc.is_deleted
    assert result == customer


def test__add_customer__customer_is_created(mocker, businessman_1,
                                            mocked_phone_number_unique_for_register):
    b = businessman_1
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


def test__get_customer_by_phone_or_create__return_already_created_customer(mocker, customer_1):
    mock = mocker.patch('customers.services.get_customer_by_phone', return_value=customer_1)

    result = get_customer_by_phone_or_create(phone=customer_1.phone)

    mock.assert_called_once_with(phone=customer_1.phone)
    assert result == customer_1


def test__get_customer_by_phone_or_create__creates_new_customer(db, mocker):
    phone = 'fake'
    mock = mocker.patch('customers.services.get_customer_by_phone', side_effect=ObjectDoesNotExist())

    result = get_customer_by_phone_or_create(phone=phone)

    mock.assert_called_once_with(phone=phone)
    obj = Customer.objects.get(phone=phone)
    assert result == obj
