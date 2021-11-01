from typing import Optional

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet

from base_app.error_codes import ApplicationErrorCodes
from base_app.services import throw_exception
from users.models import Businessman, Customer, BusinessmanCustomer


def customer_exists_by_phone(*args, businessman: Businessman, phone: str) -> bool:
    return BusinessmanCustomer.objects.filter(businessman=businessman, customer__phone=phone, is_deleted=False).exists()


def customer_exists(*args, businessman: Businessman, customer: Customer) -> bool:
    return BusinessmanCustomer.objects.filter(businessman=businessman, customer=customer, is_deleted=False).exists()


def customer_exists_by_id(*args, businessman: Businessman, customer_id: int) -> bool:
    return BusinessmanCustomer.objects.filter(businessman=businessman,
                                              customer__id=customer_id,
                                              is_deleted=False
                                              ).exists()


def get_customer(*args, businessman: Businessman, phone: str) -> Customer:
    try:
        return Customer.objects.get(connected_businessmans__businessman=businessman,
                                    phone=phone,
                                    connected_businessmans__is_deleted=False
                                    )
    except ObjectDoesNotExist as ex:
        throw_exception(error_code=ApplicationErrorCodes.RECORD_NOT_FOUND, original_exception=ex)


def get_customer_by_id(*args, customer_id: int) -> Customer:
    return Customer.objects.get(id=customer_id)


def get_businessman_customer_by_id(*args, businessman: Businessman, customer_id: int,
                                   field_name: str = None) -> Customer:
    try:
        bc = BusinessmanCustomer.objects.get(businessman=businessman,
                                             customer_id=customer_id,
                                             is_deleted=False
                                             )
        return bc.customer
    except ObjectDoesNotExist as ex:
        throw_exception(error_code=ApplicationErrorCodes.RECORD_NOT_FOUND, field_name=field_name, original_exception=ex)


def get_businessman_customers(*args, businessman: Businessman):
    return Customer.objects.filter(businessmans=businessman, connected_businessmans__is_deleted=False).order_by(
        '-date_joined').all()


def get_last_customer_ordered_by_id(*args, businessman: Businessman) -> Customer:
    return Customer.objects.filter(businessmans=businessman).order_by('id').last()


def get_businessmancustomer(*args, businessman: Businessman, customer: Customer) -> BusinessmanCustomer:
    return BusinessmanCustomer.objects.get(businessman=businessman, customer=customer, is_deleted=False)


def get_bsuinessman_customers_by_ids(*args, businessman: Businessman, customer_ids: [int]):
    return Customer.objects.filter(businessmans=businessman,
                                   id__in=customer_ids,
                                   connected_businessmans__is_deleted=False
                                   ).all()


def get_customer_by_phone(*args, phone: str) -> Customer:
    return Customer.objects.get(phone=phone)


def get_customer_by_businessman_and_phone(*args, businessman: Businessman, phone: str) -> Customer:
    try:
        bc = BusinessmanCustomer.objects.get(businessman=businessman,
                                             customer__phone=phone,
                                             is_deleted=False
                                             )
        return bc.customer
    except ObjectDoesNotExist as ex:
        throw_exception(error_code=ApplicationErrorCodes.RECORD_NOT_FOUND, original_exception=ex)


def get_date_joined(*args, businessman: Businessman, customer: Customer):
    try:
        return BusinessmanCustomer.objects.get(customer=customer, businessman=businessman).create_date
    except ObjectDoesNotExist as ex:
        throw_exception(error_code=ApplicationErrorCodes.RECORD_NOT_FOUND, original_exception=ex)


def is_phone_number_unique_for_register(*args, businessman: Businessman, phone: str) -> bool:
    return not BusinessmanCustomer.objects.filter(businessman=businessman, customer__phone=phone,
                                                  is_deleted=False).exists()
    # return not businessman.customers.filter(phone=phone, connected_businessmans__is_deleted=False).exists()


def is_phone_number_unique(*args, phone: str) -> bool:
    return not Customer.objects.filter(phone=phone).exists()


def get_businessmancustomer_delete_check(*args, businessman: Businessman, customer: Customer) -> BusinessmanCustomer:
    try:
        return BusinessmanCustomer.objects.get(businessman=businessman, customer=customer, is_deleted=False)
    except ObjectDoesNotExist as ex:
        raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.RECORD_NOT_FOUND, ex)


def get_businessmans_of_customer(*args, customer: Customer) -> QuerySet:
    return customer.businessmans.filter(connected_customers__is_deleted=False).all()


def _get_businessman_customer_relation(*args, businessman: Businessman, customer: Customer) -> Optional[
    BusinessmanCustomer]:
    try:
        return BusinessmanCustomer.objects.get(businessman=businessman, customer=customer)
    except ObjectDoesNotExist:
        return None
