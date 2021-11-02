from django.core.exceptions import ObjectDoesNotExist
from django_mock_queries.query import MockSet, MockModel

from base_app.error_codes import ApplicationErrorException
from base_app.tests import *
from customers.tests.test_conf import *
from customers.selectors import customer_exists_by_phone, customer_exists, customer_exists_by_id, get_customer, \
    get_customer_by_id, get_customer_by_businessman_and_phone, get_date_joined, is_phone_number_unique_for_register, \
    is_phone_number_unique, get_businessmancustomer_delete_check, get_businessmans_of_customer, \
    _get_businessman_customer_relation

pytestmark = pytest.mark.unit


def test__customer_exists_by_phone__returns_false(mocker, businessman_1_with_customer_tuple, businessman_2):
    result = customer_exists_by_phone(
        businessman=businessman_2,
        phone=businessman_1_with_customer_tuple[1][0].phone
    )

    assert not result


def test__customer_exists_by_phone__success(mocker, businessman_1_with_customer_tuple):
    result = customer_exists_by_phone(
        businessman=businessman_1_with_customer_tuple[0],
        phone=businessman_1_with_customer_tuple[1][0].phone
    )

    assert result


def test__customer_exists__returns_false(mocker, businessman_1_with_deleted_customer_tuple):
    result = customer_exists(
        businessman=businessman_1_with_deleted_customer_tuple[0],
        customer=businessman_1_with_deleted_customer_tuple[1][0]
    )

    assert not result


def test__customer_exists__success(mocker, businessman_1_with_customer_tuple):
    result = customer_exists(businessman=businessman_1_with_customer_tuple[0],
                             customer=businessman_1_with_customer_tuple[1][0])

    assert result


def test__test__customer_exists_by_id__returns_false(businessman_1_with_deleted_customer_tuple):
    result = customer_exists_by_id(businessman=businessman_1_with_deleted_customer_tuple[0],
                                   customer_id=businessman_1_with_deleted_customer_tuple[1][0].id
                                   )

    assert not result


def test__customer_exists_by_id__success(businessman_1_with_customer_tuple):
    result = customer_exists_by_id(
        businessman=businessman_1_with_customer_tuple[0],
        customer_id=businessman_1_with_customer_tuple[1][0].id
    )

    assert result


def test__get_customer__success__raises_error(businessman_1_with_deleted_customer_tuple):
    with pytest.raises(ApplicationErrorException):
        get_customer(
            businessman=businessman_1_with_deleted_customer_tuple[0],
            phone=businessman_1_with_deleted_customer_tuple[1][0].phone
        )


def test__get_customer__success(businessman_1_with_customer_tuple):
    customer = businessman_1_with_customer_tuple[1][0]
    result = get_customer(
        businessman=businessman_1_with_customer_tuple[0],
        phone=customer.phone
    )

    assert result == customer


def test__get_customer_by_id__success(businessman_1_with_customer_tuple):
    customer = businessman_1_with_customer_tuple[1][0]

    result = get_customer_by_id(customer_id=customer.id)

    assert result == customer


def test__get_customer_by_businessman_and_phone__raises_error(businessman_1_with_deleted_customer_tuple):
    with pytest.raises(ApplicationErrorException):
        get_customer_by_businessman_and_phone(businessman=businessman_1_with_deleted_customer_tuple[0],
                                              phone=businessman_1_with_deleted_customer_tuple[1][0].phone)


def test__get_customer_by_businessman_and_phone__success(businessman_1_with_customer_tuple):
    customer = businessman_1_with_customer_tuple[1][0]
    result = get_customer_by_businessman_and_phone(
        businessman=businessman_1_with_customer_tuple[0],
        phone=customer.phone
    )

    assert result == customer


def test__get_date_joined__raises_error(businessman_1, customer_1):
    with pytest.raises(ApplicationErrorException):
        get_date_joined(
            businessman=businessman_1,
            customer=customer_1
        )


def test__get_date_joined__success(businessman_1_with_customer_tuple):
    customer = businessman_1_with_customer_tuple[1][0]
    bc = businessman_1_with_customer_tuple[2][0]

    result = get_date_joined(businessman=businessman_1_with_customer_tuple[0], customer=customer)

    assert result == bc.create_date


def test__is_phone_number_unique_for_register__returns_false(businessman_1_with_customer_tuple):
    result = is_phone_number_unique_for_register(
        businessman=businessman_1_with_customer_tuple[0],
        phone=businessman_1_with_customer_tuple[1][0].phone
    )

    assert not result


def test__test__is_phone_number_unique_for_register__returns_true(businessman_1_with_deleted_customer_tuple):
    result = is_phone_number_unique_for_register(
        businessman=businessman_1_with_deleted_customer_tuple[0],
        phone=businessman_1_with_deleted_customer_tuple[1][0].phone
    )

    assert result


def test__is_phone_number_unique__returns_false(customer_1):
    result = is_phone_number_unique(phone=customer_1.phone)

    assert not result


def test__is_phone_number_unique__returns_true(db):
    result = is_phone_number_unique(phone=random_mobile_phone())

    assert result


def test__get_businessmancustomer_delete_check__raises__error(businessman_1_with_deleted_customer_tuple):
    with pytest.raises(ApplicationErrorException):
        get_businessmancustomer_delete_check(
            businessman=businessman_1_with_deleted_customer_tuple[0],
            customer=businessman_1_with_deleted_customer_tuple[1][0]
        )


def test__get_businessmancustomer_delete_check__success(businessman_1_with_customer_tuple):
    bc = businessman_1_with_customer_tuple[2][0]
    businessman = businessman_1_with_customer_tuple[0]
    customer = businessman_1_with_customer_tuple[1][0]
    result = get_businessmancustomer_delete_check(
        businessman=businessman,
        customer=customer
    )

    assert result == bc


def test__get_businessmans_of_customer__success(businessman_1_with_customer_tuple):
    businessman = businessman_1_with_customer_tuple[0]
    customer = businessman_1_with_customer_tuple[1][0]

    result = get_businessmans_of_customer(customer=customer)

    assert result.count() == 1
    assert result.first() == businessman


def test___get_businessman_customer_relation__returns_None(businessman_1, customer_1):
    result = _get_businessman_customer_relation(
        businessman=businessman_1,
        customer=customer_1
    )

    assert result is None


def test__test___get_businessman_customer_relation__returns_businesmsancustomer(businessman_1_with_customer_tuple):
    businessman = businessman_1_with_customer_tuple[0]
    customer = businessman_1_with_customer_tuple[1][0]
    bc = businessman_1_with_customer_tuple[2][0]
    result = _get_businessman_customer_relation(
        businessman=businessman,
        customer=customer
    )

    assert result == bc
