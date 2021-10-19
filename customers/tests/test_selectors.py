from django.core.exceptions import ObjectDoesNotExist
from django_mock_queries.query import MockSet, MockModel

from base_app.tests import *
from customers.tests.test_conf import *
from customers.selectors import customer_exists_by_phone, customer_exists, customer_exists_by_id, get_customer, \
    get_customer_by_id

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
