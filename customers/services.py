from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import QuerySet

from base_app.error_codes import ApplicationErrorCodes
from base_app.services import BaseService
from smspanel.services import sms_message_service
from users.models import Customer, Businessman, BusinessmanCustomer


class CustomerService(BaseService):

    def customer_exists_by_phone(self, user: Businessman, phone: str) -> bool:
        return BusinessmanCustomer.objects.filter(customer=user, customer__phone=phone, is_deleted=False).exists()

    def customer_exists(self, user: Businessman, customer: Customer) -> bool:
        return BusinessmanCustomer.objects.filter(businessman=user, customer=customer, is_deleted=False).exists()

    def customer_exists_by_id(self, user: Businessman, customer_id: int) -> bool:
        return BusinessmanCustomer.objects.filter(businessman=user, customer__id=customer_id, is_deleted=False).exists()

    def get_customer(self, user: Businessman, phone: str) -> Customer:
        return Customer.objects.get(businessman=user, phone=phone, connected_businessmans__is_deleted=False)

    def get_customer_by_id(self, customer_id: int) -> Customer:
        return Customer.objects.get(id=customer_id)

    def get_businessman_customer_by_id(self, user: Businessman, customer_id: int, field_name: str = None) -> Customer:
        try:
            bc = BusinessmanCustomer.objects.get(businessman=user, customer_id=customer_id, is_deleted=False)
            return bc.customer
        except ObjectDoesNotExist as ex:
            self.throw_exception(ApplicationErrorCodes.RECORD_NOT_FOUND, field_name, ex)

    def get_businessman_customers(self, user: Businessman):
        return Customer.objects.filter(businessmans=user, connected_businessmans__is_deleted=False).order_by(
            '-date_joined').all()

    def get_last_customer_ordered_by_id(self, user: Businessman) -> Customer:
        return Customer.objects.filter(businessmans=user).order_by('id').last()

    def get_businessmancustomer(self, user: Businessman, customer: Customer) -> BusinessmanCustomer:
        return BusinessmanCustomer.objects.get(businessman=user, customer=customer, is_deleted=False)

    def get_bsuinessman_customers_by_ids(self, user: Businessman, customer_ids: [int]):
        return Customer.objects.filter(businessmans=user, id__in=customer_ids,
                                       connected_businessmans__is_deleted=False).all()

    def get_customer_by_phone(self, phone: str) -> Customer:
        return Customer.objects.get(phone=phone)

    def get_customer_by_businessman_and_phone(self, businessman: Businessman, phone: str) -> Customer:
        try:
            bc = BusinessmanCustomer.objects.get(businessman=businessman, customer__phone=phone, is_deleted=False)
            return bc.customer
        except ObjectDoesNotExist as ex:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.RECORD_NOT_FOUND, ex)

    def add_customer(self, businessman: Businessman, phone: str, full_name='', groups: list = None,
                     joined_by=BusinessmanCustomer.JOINED_BY_PANEL,
                     low_credit_error_code: dict = None, purchase_price=None) -> Customer:
        from customerpurchase.services import purchase_service
        self._check_is_phone_number_unique_for_register(businessman, phone)
        c = None
        try:
            c = Customer.objects.get(phone=phone)
            bc = self._get_businessman_customer_relation(businessman, c)
            if bc is not None and bc.is_deleted:
                bc.is_deleted = False
                bc.save()
            else:
                c = self._join_customer_to_businessman(businessman, c, joined_by, groups, low_credit_error_code)
        except ObjectDoesNotExist:
            c = self._create_customer_join_to_businessman(businessman, joined_by, phone, full_name, groups,
                                                          low_credit_error_code)

        if purchase_price is not None:
            purchase_service.add_customer_purchase(
                user=businessman, customer=c,
                amount=purchase_price
            )
        return c

    def _join_customer_to_businessman(self, businessman: Businessman, customer: Customer, joined_by,
                                      groups: list, low_credit_error_code: dict = None) -> Customer:
        from payment.services import wallet_billing_service
        with transaction.atomic():
            bc = BusinessmanCustomer.objects.create(customer=customer, businessman=businessman, joined_by=joined_by)
            wallet_billing_service.payment_for_customer_added(bc, low_credit_error_code)
            self._reset_customer_group_send_welcome_message(businessman, customer, groups)
            return customer

    def _create_customer_join_to_businessman(self, businessman: Businessman, joined_by, phone: str,
                                             full_name: str = None, groups: list = None,
                                             low_credit_error_code: dict = None) -> Customer:
        from payment.services import wallet_billing_service
        with transaction.atomic():
            c = Customer.objects.create(phone=phone, full_name=full_name)
            bc = BusinessmanCustomer.objects.create(customer=c, businessman=businessman, joined_by=joined_by)
            wallet_billing_service.payment_for_customer_added(bc, low_credit_error_code)
            self._reset_customer_group_send_welcome_message(businessman, c, groups)
            return c

    def _reset_customer_group_send_welcome_message(self, businessman: Businessman, customer: Customer,
                                                   groups: list = None):
        sms_message_service.send_welcome_message(businessman, customer)
        if groups is not None:
            self.reset_customer_groups(businessman, customer, groups)
        return customer

    def customer_registered_in_date(self, businessman: Businessman, date):
        return self.get_businessman_customers(businessman).filter(connected_businessmans__create_date__year=date.year,
                                                                  connected_businessmans__create_date__month=date.month,
                                                                  connected_businessmans__create_date__day=date.day)

    def get_date_joined(self, customer: Customer, businessman=Businessman):
        return BusinessmanCustomer.objects.get(customer=customer, businessman=businessman).create_date

    def is_phone_number_unique_for_register(self, businessman: Businessman, phone: str) -> bool:
        return not businessman.customers.filter(phone=phone, connected_businessmans__is_deleted=False).exists()

    def is_phone_number_unique(self, phone: str) -> bool:
        return Customer.objects.filter(phone=phone).exists()

    def delete_customer_for_businessman(self, businessman: Businessman, customer_id) -> Customer:
        try:
            bc = BusinessmanCustomer.objects.get(businessman=businessman, customer__id=customer_id, is_deleted=False)
            bc.is_deleted = True
            bc.save()
            return bc.customer
        except ObjectDoesNotExist:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.RECORD_NOT_FOUND)

    def get_businessmancustomer_delete_check(self, businessman: Businessman, customer: Customer) -> BusinessmanCustomer:
        try:
            return BusinessmanCustomer.objects.get(businessman=businessman, customer=customer, is_deleted=False)
        except ObjectDoesNotExist as ex:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.RECORD_NOT_FOUND, ex)

    def get_businessmans_of_customer(self, c: Customer) -> QuerySet:
        return c.businessmans.filter(connected_customers__is_deleted=False).all()

    def can_edit_phone(self, user: Businessman, c: Customer, phone: str) -> bool:
        can_edit_phone = self._can_edit_phone_number_value(user, c, phone)
        can_change = self._can_edit_phone_number_by_change_customer(user, c, phone)
        return not c.is_phone_confirmed and (can_edit_phone or can_change)

    def edit_customer_phone(self, user: Businessman, c: Customer, phone: str) -> Customer:
        if phone is None or not customer_service.can_edit_phone(user, c, phone):
            return c

        if c.is_phone_confirmed:
            return c

        can_edit_phone = self._can_edit_phone_number_value(user, c, phone)
        if can_edit_phone:
            c.phone = phone
            c.save()
            return c

        can_change = self._can_edit_phone_number_by_change_customer(user, c, phone)
        if can_change:
            new_c = self.get_customer_by_phone(phone)
            self.delete_customer_for_businessman(user, c.id)
            BusinessmanCustomer.objects.create(businessman=user, customer=new_c)
            return new_c

        return c

    def edit_full_name(self, user: Businessman, c: Customer, full_name) -> Customer:
        can_edit = self.can_edit_full_name(user, c)
        if not can_edit:
            return c
        c.full_name = full_name
        c.save()
        return c

    def edit_customer_phone_full_name(self, user: Businessman, customer_id: int, phone: str = None,
                                      full_name: str = None, purchase_price=None) -> Customer:
        customer = self.get_businessman_customer_by_id(user, customer_id)
        self.edit_customer_phone(user, customer, phone)
        self.edit_full_name(user, customer, full_name)
        if purchase_price is not None:
            from customerpurchase import services
            services.purchase_service.add_customer_purchase(
                user=user,
                customer=customer,
                amount=purchase_price
            )

        return customer

    def _can_edit_phone_number_value(self, user: Businessman, c: Customer, phone: str) -> bool:
        is_unique = self.is_phone_number_unique_for_update(user, c.id, phone)
        businessmans = self.get_businessmans_of_customer(c)
        if is_unique:
            return businessmans.exclude(id=user.id).count() == 0

    def is_phone_number_unique_for_update(self, user: Businessman, customer_id: int, phone: str) -> bool:
        return not user.customers.filter(phone=phone).exclude(id=customer_id,
                                                              connected_businessmans__is_deleted=False).exists()

    def _can_edit_phone_number_by_change_customer(self, user: Businessman, c: Customer, phone: str):
        return Customer.objects.filter(phone=phone).exclude(connected_businessmans__businessman=user).exclude(
            id=c.id).exists()

    def can_edit_full_name(self, user: Businessman, c: Customer) -> bool:
        return not BusinessmanCustomer.objects.exclude(businessman=user).filter(customer=c).exists()

    def _can_edit_phone_number_value(self, user: Businessman, c: Customer, phone: str) -> bool:
        is_unique = self.is_phone_number_unique_for_update(user, c.id, phone)
        businessmans = self.get_businessmans_of_customer(c)
        if is_unique:
            return businessmans.exclude(id=user.id).count() == 0

    def _can_edit_phone_number_by_change_customer(self, user: Businessman, c: Customer, phone: str):
        return Customer.objects.filter(phone=phone).exclude(connected_businessmans__businessman=user).exclude(
            id=c.id).exists()

    def is_phone_number_unique_for_update(self, user: Businessman, customer_id: int, phone: str) -> bool:
        return not user.customers.filter(phone=phone).exclude(id=customer_id,
                                                              connected_businessmans__is_deleted=False).exists()

    def _update_customer_phone_full_name(self, c: Customer, phone: str, full_name: str) -> Customer:
        c.phone = phone
        c.full_name = full_name
        c.save()
        return c

    def reset_customer_groups(self, user: Businessman, customer: Customer, groups: list):
        from groups.models import BusinessmanGroups
        if groups is None:
            return customer
        # for g in groups:
        #     g.add_member(customer)
        BusinessmanGroups.reset_customer_groups(user, customer, groups)
        return customer

    def get_customer_by_phone_or_create(self, phone) -> Customer:
        try:
            return customer_service.get_customer_by_phone(phone)
        except ObjectDoesNotExist:
            return Customer.objects.create(phone=phone)

    def _check_is_phone_number_unique_for_register(self, user: Businessman, phone: str):
        is_unique = self.is_phone_number_unique_for_register(user, phone)
        if not is_unique:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.PHONE_NUMBER_IS_NOT_UNIQUE)

    def _get_businessman_customer_relation(self, user: Businessman, customer: Customer) -> BusinessmanCustomer:
        try:
            return BusinessmanCustomer.objects.get(businessman=user, customer=customer)
        except ObjectDoesNotExist:
            return None


customer_service = CustomerService()
