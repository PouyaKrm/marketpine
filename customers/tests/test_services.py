import pytest
from django.core.exceptions import ObjectDoesNotExist

from base_app.error_codes import ApplicationErrorException
from customers.services import add_customer, get_customer_by_phone_or_create, _join_customer_to_businessman, \
    _create_customer_join_to_businessman, _reset_customer_group_send_welcome_message, customer_registered_in_date, \
    delete_customer_for_businessman, can_edit_phone, edit_customer_phone, edit_full_name, edit_customer_phone_full_name, \
    can_edit_full_name
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


def mock___can_edit_phone_number_value(mocker, return_value: bool):
    return mocker.patch('customers.services._can_edit_phone_number_value', return_value=return_value)


def mock___can_edit_phone_number_by_change_customer(mocker, return_value: bool):
    return mocker.patch('customers.services._can_edit_phone_number_by_change_customer', return_value=return_value)


def mock__can_edit_full_name(mocker, return_value: bool):
    return mocker.patch('customers.services.can_edit_full_name', return_value=return_value)


def mock__get_businessman_customer_by_id(mocker, customer: Customer):
    return mocker.patch('customers.services.get_businessman_customer_by_id', return_value=customer)


@pytest.fixture
def mocked_phone_number_unique_for_register(mocker):
    mocker.patch('customers.services._check_is_phone_number_unique_for_register', return_value=None)


@pytest.fixture
def mocked_wallet_payment_for_customer_added(mocker):
    return mocker.patch('payment.services.wallet_billing_service.payment_for_customer_added', return_value=None)


@pytest.fixture
def mocked__reset_customer_group_send_welcome_message(mocker):
    return mocker.patch('customers.services._reset_customer_group_send_welcome_message', return_value=None)


@pytest.fixture
def mocked_send_welcome_message(mocker):
    return mocker.patch('customers.services.send_welcome_message')


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


def test___join_customer_to_businessman__transaction(mocked__reset_customer_group_send_welcome_message,
                                                     mocked_wallet_payment_for_customer_added,
                                                     businessman_1,
                                                     customer_1):
    mocked_wallet_payment_for_customer_added.side_effect = Exception('fake')
    with pytest.raises(Exception):
        _join_customer_to_businessman(businessman=businessman_1,
                                      customer=customer_1,
                                      joined_by=BusinessmanCustomer.JOINED_BY_PANEL,
                                      groups=[],
                                      low_credit_error_code=None)

    exists = BusinessmanCustomer.objects.filter(
        businessman=businessman_1,
        customer=customer_1,
        joined_by=BusinessmanCustomer.JOINED_BY_PANEL
    ).exists()

    assert not exists


def test___join_customer_to_businessman__success(customer_1, businessman_1,
                                                 mocked__reset_customer_group_send_welcome_message,
                                                 mocked_wallet_payment_for_customer_added
                                                 ):
    joined_by = BusinessmanCustomer.JOINED_BY_PANEL
    groups = []
    low_credit_error_code = None

    _join_customer_to_businessman(
        businessman=businessman_1,
        customer=customer_1,
        joined_by=joined_by,
        groups=groups,
        low_credit_error_code=low_credit_error_code
    )

    q = BusinessmanCustomer.objects.filter(
        businessman=businessman_1,
        customer=customer_1,
        joined_by=BusinessmanCustomer.JOINED_BY_PANEL
    )
    assert q.exists()
    mocked_wallet_payment_for_customer_added.assert_called_once_with(q.first(), low_credit_error_code)
    mocked__reset_customer_group_send_welcome_message.assert_called_once_with(
        businessman=businessman_1,
        customer=customer_1,
        groups=groups
    )


def test___create_customer_join_to_businessman__transaction(
        mocked_wallet_payment_for_customer_added,
        mocked__reset_customer_group_send_welcome_message,
        businessman_1, customer_1):
    mocked_wallet_payment_for_customer_added.side_effect = Exception('fast')
    phone = 'fake'
    with pytest.raises(Exception):
        _create_customer_join_to_businessman(
            businessman=businessman_1,
            joined_by=BusinessmanCustomer.JOINED_BY_CUSTOMER_APP,
            phone=phone
        )

    q = BusinessmanCustomer.objects.filter(
        businessman=businessman_1,
        businessman__phone=phone
    )

    assert not q.exists()


def test___create_customer_join_to_businessman(businessman_1,
                                               mocked_wallet_payment_for_customer_added,
                                               mocked__reset_customer_group_send_welcome_message
                                               ):
    phone = 'fake'
    joined_by = 'joined_by'
    full_name = 'full name'
    groups = None
    low_error_code = None

    result = _create_customer_join_to_businessman(businessman=businessman_1,
                                                  joined_by=joined_by,
                                                  phone=phone,
                                                  full_name=full_name,
                                                  groups=groups,
                                                  low_credit_error_code=low_error_code
                                                  )

    cq = Customer.objects.filter(phone=phone, full_name=full_name)
    bcq = BusinessmanCustomer.objects.filter(businessman=businessman_1, customer=cq.first(), joined_by=joined_by)
    assert cq.exists()
    assert result == cq.first()
    assert bcq.exists()
    mocked_wallet_payment_for_customer_added.assert_called_once_with(bcq.first(), low_error_code)
    mocked__reset_customer_group_send_welcome_message.assert_called_once_with(businessman=businessman_1,
                                                                              customer=cq.first(),
                                                                              groups=groups)


def test___reset_customer_group_send_welcome_message__groups_is_none(mocker, businessman_1, customer_1,
                                                                     mocked_send_welcome_message):
    reset_mock = mocker.patch('customers.services.reset_customer_groups')

    result = _reset_customer_group_send_welcome_message(businessman=businessman_1,
                                                        customer=customer_1)

    mocked_send_welcome_message.assert_called_once_with(businessman=businessman_1, customer=customer_1)
    reset_mock.assert_not_called()
    assert result == customer_1


def test___reset_customer_group_send_welcome_message__groups_is_not_none(mocker,
                                                                         businessman_1,
                                                                         customer_1,
                                                                         mocked_send_welcome_message):
    reset_mock = mocker.patch('customers.services.reset_customer_groups')
    groups = [1]

    result = _reset_customer_group_send_welcome_message(businessman=businessman_1, customer=customer_1, groups=groups)

    mocked_send_welcome_message.assert_called_once_with(businessman=businessman_1, customer=customer_1)
    reset_mock.assert_called_once_with(businessman=businessman_1, customer=customer_1, groups=groups)
    assert result == customer_1


def test__customer_registered_in_date(businessman_1_with_customer_tuple):
    d = businessman_1_with_customer_tuple[2][0].create_date

    result = customer_registered_in_date(businessman=businessman_1_with_customer_tuple[0], create_date=d)

    result = list(result)
    t = TestCase()
    t.assertCountEqual(list(result), businessman_1_with_customer_tuple[1])


def test__delete_customer_for_businessman__businessmmancustomer_not_found(businessman_1_with_customer_tuple):
    with pytest.raises(ApplicationErrorException):
        delete_customer_for_businessman(
            businessman=businessman_1_with_customer_tuple[0],
            customer_id=1000
        )


def test__delete_customer_for_businessman__success(businessman_1_with_customer_tuple):
    b = businessman_1_with_customer_tuple[0]
    c = businessman_1_with_customer_tuple[1][0]

    result = delete_customer_for_businessman(businessman=b, customer_id=c.id)

    assert result == c
    bc = BusinessmanCustomer.objects.get(businessman=b, customer=c)
    assert bc.is_deleted


def test__can_edit_phone(mocker, businessman_1_with_customer_tuple):
    mocked_can_edit_phone = mock___can_edit_phone_number_value(mocker, True)
    mocked_change_customer = mock___can_edit_phone_number_by_change_customer(mocker, True)
    c = businessman_1_with_customer_tuple[1][0]
    call_params = {
        'businessman': businessman_1_with_customer_tuple[0],
        'customer': businessman_1_with_customer_tuple[1][0],
        'phone': 'fake'
    }

    result = can_edit_phone(**call_params)

    assert result == (not c.is_phone_confirmed)
    mocked_can_edit_phone.assert_called_once_with(**call_params)
    mocked_change_customer.assert_called_once_with(**call_params)


def mock__can_edit_phone(mocker, return_value=True):
    return mocker.patch('customers.services.can_edit_phone', return_value=return_value)


def test__edit_customer_phone__phone_is_none(mocker, businessman_1_with_customer_tuple):
    mocked_can_edit = mock__can_edit_phone(mocker, True)
    c = businessman_1_with_customer_tuple[1][0]
    call_params = {
        'businessman': businessman_1_with_customer_tuple[0],
        'customer': c,
        'phone': None
    }

    result = edit_customer_phone(**call_params)

    assert result == c
    mocked_can_edit.assert_not_called()


def test__edit_customer_phone__phone_is_confirmed(mocker, businessman_1_with_customer_tuple):
    mocked_can_edit = mock__can_edit_phone(mocker, True)
    c = businessman_1_with_customer_tuple[1][0]
    c.is_phone_confirmed = True
    c.save()
    call_params = {
        'businessman': businessman_1_with_customer_tuple[0],
        'customer': c,
        'phone': 'fake'
    }

    result = edit_customer_phone(**call_params)

    assert result == c
    mocked_can_edit.assert_called_once_with(**call_params)


def test__edit_customer_phone__can_edit_phone_number_value(mocker, businessman_1_with_customer_tuple):
    mocked_can_edit_phone = mock__can_edit_phone(mocker, True)
    mocked_can_edit_value = mock___can_edit_phone_number_value(mocker, True)
    mocked_can_change = mock___can_edit_phone_number_by_change_customer(mocker, True)
    c = businessman_1_with_customer_tuple[1][0]
    c.is_phone_confirmed = False
    c.save()
    call_params = {
        'businessman': businessman_1_with_customer_tuple[0],
        'customer': c,
        'phone': 'fake'
    }

    result = edit_customer_phone(**call_params)

    assert result.id == c.id
    mocked_can_edit_phone.assert_called_once_with(**call_params)
    mocked_can_edit_value.assert_called_once_with(**call_params)
    mocked_can_change.assert_not_called()
    assert result.phone == call_params['phone']


def test__test__edit_customer_phone__customer_change(mocker, businessman_1_with_customer_tuple, customer_2):
    mocked_can_edit = mock__can_edit_phone(mocker, True)
    mocked_can_edit_value = mock___can_edit_phone_number_value(mocker, False)
    mocked_can_change = mock___can_edit_phone_number_by_change_customer(mocker, True)
    mocked_get_customer = mocker.patch('customers.services.get_customer_by_phone', return_value=customer_2)
    mocked_delete_customer = mocker.patch('customers.services.delete_customer_for_businessman')
    b = businessman_1_with_customer_tuple[0]
    c = businessman_1_with_customer_tuple[1][0]
    c.is_phone_confirmed = False
    c.save()
    call_params = {
        'businessman': b,
        'customer': c,
        'phone': 'fake'
    }

    result = edit_customer_phone(**call_params)

    assert result == customer_2
    exist = BusinessmanCustomer.objects.filter(businessman=b, customer=customer_2, is_deleted=False).exists()
    assert exist
    mocked_can_edit.assert_called_once_with(**call_params)
    mocked_can_edit_value.assert_called_once_with(**call_params)
    mocked_can_change.assert_called_once_with(**call_params)
    mocked_get_customer.assert_called_once_with(phone=call_params['phone'])
    mocked_delete_customer.assert_called_once_with(businessman=b, customer_id=c.id)


def test__edit_full_name__can_not_edit_full_name(mocker, businessman_1_with_customer_tuple):
    mocked_can_edit = mock__can_edit_full_name(mocker, False)
    b = businessman_1_with_customer_tuple[0]
    c = businessman_1_with_customer_tuple[1][0]

    result = edit_full_name(businessman=b, customer=c, full_name='name')

    assert result == c
    mocked_can_edit.assert_called_once_with(businessman=b, customer=c)


def test__edit_full_name(mocker, businessman_1_with_customer_tuple):
    b = businessman_1_with_customer_tuple[0]
    c = businessman_1_with_customer_tuple[1][0]
    full_name = 'fake'
    mocked_can_edit = mock__can_edit_full_name(mocker, True)

    result = edit_full_name(businessman=b, customer=c, full_name=full_name)

    q = Customer.objects.filter(id=c.id, full_name=full_name)
    assert q.exists()
    assert result == q.first()
    mocked_can_edit.assert_called_once_with(businessman=b, customer=c)


def test__edit_customer_phone_full_name(mocker, businessman_1_with_customer_tuple):
    b = businessman_1_with_customer_tuple[0]
    c = businessman_1_with_customer_tuple[1][1]
    phone = 'fake'
    full_name = 'fake'
    mocked_get_by_id = mock__get_businessman_customer_by_id(mocker, c)
    mocked_edit_phone = mocker.patch('customers.services.edit_customer_phone')
    mocked_edit_full_name = mocker.patch('customers.services.edit_full_name')

    result = edit_customer_phone_full_name(businessman=b, customer_id=c.id, phone=phone, full_name=full_name)

    assert result == c
    mocked_get_by_id.assert_called_once_with(businessman=b, customer_id=c.id)
    mocked_edit_phone.assert_called_once_with(businessman=b, customer=c, phone=phone)
    mocked_edit_full_name.assert_called_once_with(businessman=b, customer=c, full_name=full_name)


def test__can_edit_full_name__returns_false(businessman_1_with_customer_tuple, businessman_2,
                                            create_businessmancustomer):
    b = businessman_1_with_customer_tuple[0]
    c = businessman_1_with_customer_tuple[1][0]
    create_businessmancustomer(businessman=businessman_2, customer=c)

    result = can_edit_full_name(businessman=b, customer=c)

    assert not result


def test__can_edit_full_name__returns_true(businessman_1_with_customer_tuple):
    b = businessman_1_with_customer_tuple[0]
    c = businessman_1_with_customer_tuple[1][0]

    result = can_edit_full_name(businessman=b, customer=c)

    assert result
