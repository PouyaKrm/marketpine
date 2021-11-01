from django.core.exceptions import ObjectDoesNotExist
from django_mock_queries.query import MockSet, MockModel

from base_app.error_codes import ApplicationErrorException
from base_app.tests import *
from customers.tests.test_conf import *
from customers.selectors import customer_exists_by_phone, customer_exists, customer_exists_by_id, get_customer, \
    get_customer_by_id, get_customer_by_businessman_and_phone, get_date_joined, is_phone_number_unique_for_register, \
    is_phone_number_unique, get_businessmancustomer_delete_check, get_businessmans_of_customer

pytestmark = pytest.mark.unit


def test__customer_exists_by_phone__returns_false(mocker, mocked_businessmancustomer_deleted):
    result = customer_exists_by_phone(
        businessman=mocked_businessmancustomer_deleted.businessman,
        phone=mocked_businessmancustomer_deleted.customer.phone
    )

    assert not result


def test__customer_exists_by_phone__success(mocker, mocked_businessmancustomer):
    result = customer_exists_by_phone(
        businessman=mocked_businessmancustomer.businessman,
        phone=mocked_businessmancustomer.customer.phone
    )

    assert result


def test__customer_exists__returns_false(mocker, mocked_businessmancustomer_deleted):
    result = customer_exists(businessman=mocked_businessmancustomer_deleted.businessman,
                             customer=mocked_businessmancustomer_deleted.customer)

    assert not result


def test__customer_exists__success(mocker, mocked_businessmancustomer):
    result = customer_exists(businessman=mocked_businessmancustomer.businessman,
                             customer=mocked_businessmancustomer.customer)

    assert result


def test__test__customer_exists_by_id__returns_false(mocked_businessmancustomer_deleted):
    result = customer_exists_by_id(businessman=mocked_businessmancustomer_deleted.businessman,
                                   customer_id=mocked_businessmancustomer_deleted.customer.id
                                   )

    assert not result


def test__customer_exists_by_id__success(mocked_businessmancustomer):
    result = customer_exists_by_id(
        businessman=mocked_businessmancustomer.businessman,
        customer_id=mocked_businessmancustomer.customer.id
    )

    assert result


def test__get_customer__raises_error(mocked_customer_deleted):
    with pytest.raises(ObjectDoesNotExist):
        get_customer(businessman=mocked_customer_deleted.businessman, phone=mocked_customer_deleted.customer.phone)


def test__get_customer__success(mocked_customer):
    result = get_customer(businessman=mocked_customer.businessman, phone=mocked_customer.customer.phone)

    assert result == mocked_customer.customer


def test__get_customer_by_id__success(mocked_customer):
    result = get_customer_by_id(customer_id=mocked_customer.customer.id)

    assert result == mocked_customer.customer


def test__get_customer_by_businessman_and_phone__raises_error(mocked_customer, mocked_businessman):
    with pytest.raises(ApplicationErrorException):
        get_customer_by_businessman_and_phone(businessman=mocked_businessman.first(),
                                              phone=mocked_customer.customer.phone)


def test__get_customer_by_businessman_and_phone__success(mocked_customer):
    result = get_customer_by_businessman_and_phone(businessman=mocked_customer.businessman,
                                                   phone=mocked_customer.customer.phone)

    assert result == mocked_customer.customer


def test__get_date_joined__raises_error(mocked_customer, mocked_businessman):
    with pytest.raises(ApplicationErrorException):
        get_date_joined(businessman=mocked_businessman.first(), customer=mocked_customer.customer)


def test__get_date_joined__success(mocked_customer):
    result = get_date_joined(businessman=mocked_customer.businessman, customer=mocked_customer.customer)

    assert result == mocked_customer.businessman_customer.create_date


def test__is_phone_number_unique_for_register__returns_false(mocked_customer):
    result = is_phone_number_unique_for_register(businessman=mocked_customer.businessman,
                                                 phone=mocked_customer.customer.phone)

    assert not result


def test__test__is_phone_number_unique_for_register__returns_true(mocked_customer, mocked_businessman):
    result = is_phone_number_unique_for_register(businessman=mocked_businessman.first(),
                                                 phone=mocked_customer.customer.phone)

    assert result


def test__is_phone_number_unique__returns_false(mocked_customer):
    result = is_phone_number_unique(phone=mocked_customer.customer.phone)

    assert not result


def test__is_phone_number_unique__returns_true(mocked_customer):
    result = is_phone_number_unique(phone=random_mobile_phone())

    assert result


def test__get_businessmancustomer_delete_check__raises__error(mocked_customer, mocked_businessman):
    with pytest.raises(ApplicationErrorException):
        get_businessmancustomer_delete_check(businessman=mocked_businessman.first(), customer=mocked_customer.customer)


def test__get_businessmancustomer_delete_check__success(mocked_customer):
    result = get_businessmancustomer_delete_check(businessman=mocked_customer.businessman,
                                                  customer=mocked_customer.customer)

    assert result == mocked_customer.businessman_customer


def test__get_businessmans_of_customer__success(mocked_customer):
    result = get_businessmans_of_customer(customer=mocked_customer.customer)

    assert result.count() == 1
    assert result.first() == mocked_customer.businessman
