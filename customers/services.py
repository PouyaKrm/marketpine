from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from rest_framework.generics import get_object_or_404


from users.models import Customer, Businessman, BusinessmanCustomer


class CustomerService:

    def customer_exists(self, user: Businessman, phone: str) -> bool:
        return Customer.objects.filter(businessmans=user, phone=phone).exists()

    def customer_exists_by_id(self, user: Businessman, customer_id: int) -> bool:
        return Customer.objects.filter(businessman=user, id=customer_id).exists()

    def get_customer(self, user: Businessman, phone: str) -> Customer:
        return Customer.objects.get(businessman=user, phone=phone)

    def get_customer_by_id(self, customer_id: int) -> Customer:
        return Customer.objects.get(id=customer_id)

    def get_businessman_customer_by_id(self, user: Businessman, customer_id: int):
        return user.customers.get(id=customer_id)

    def get_customer_by_id_or_404(self, user: Businessman, customer_id: int):
        return get_object_or_404(Customer, businessmans=user, id=customer_id)

    def get_businessman_customers(self, user: Businessman):
        return Customer.objects.filter(businessmans=user).order_by('-date_joined').all()

    def get_bsuinessman_customers_by_ids(self, user: Businessman, customer_ids: [int]):
        return Customer.objects.filter(businessmans=user, id__in=customer_ids).all()

    def get_customer_by_phone(self, phone: str) -> Customer:
        return Customer.objects.get(phone=phone)

    def get_customer_by_businessman_and_phone(self, businessman: Businessman, phone: str) -> Customer:
        return businessman.customers.get(phone=phone)

    def add_customer(self, businessman: Businessman, phone: str, full_name='', groups: list = None) -> Customer:
        c = None
        try:
            c = Customer.objects.get(phone=phone)
            BusinessmanCustomer.objects.create(customer=c, businessman=businessman)
        except ObjectDoesNotExist:
            c = Customer.objects.create(phone=phone, full_name=full_name)
            BusinessmanCustomer.objects.create(customer=c, businessman=businessman)
        finally:
            if groups is not None:
                self.reset_customer_groups(c, groups)
            return c

    def get_date_joined(self, customer: Customer, businessman=Businessman):
        return BusinessmanCustomer.objects.get(customer=customer, businessman=businessman).create_date

    def is_phone_number_unique_for_register(self, businessman: Businessman, phone: str) -> bool:
        return not businessman.customers.filter(phone=phone).exists()

    def is_phone_number_unique(self, phone: str) -> bool:
        return Customer.objects.filter(phone=phone).exists()

    def delete_customer_for_businessman(self, businessman: Businessman, customer_id):
        BusinessmanCustomer.objects.filter(businessman=businessman, customer__id=customer_id).delete()

    def get_businessmans_of_customer(self, c: Customer) -> QuerySet:
        return c.businessmans.all()

    def can_edit_phone(self, user: Businessman, c: Customer, phone: str) -> bool:
        can_edit_phone = self._can_edit_phone_number_value(user, c, phone)
        can_change = self._can_edit_phone_number_by_change_customer(user, c, phone)
        return not c.is_phone_confirmed and (can_edit_phone or can_change)

    def edit_customer_phone(self, user: Businessman, c: Customer, phone: str) -> Customer:

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

    def can_edit_full_name(self, user: Businessman, c: Customer) -> bool:
        return not BusinessmanCustomer.objects.exclude(businessman=user).filter(customer=c).exists()

    def _can_edit_phone_number_value(self, user: Businessman, c: Customer, phone: str) -> bool:
        is_unique = self._is_phone_number_unique_for_update(c, phone)
        businessmans = self.get_businessmans_of_customer(c)
        if is_unique:
            return businessmans.exclude(id=user.id).count() == 0

    def _can_edit_phone_number_by_change_customer(self, user: Businessman, c: Customer, phone: str):
        return Customer.objects.filter(phone=phone).exclude(connected_businessmans__businessman=user).exclude(id=c.id).exists()

    def _is_phone_number_unique_for_update(self, customer: object, phone: object) -> object:
        return not Customer.objects.filter(phone=phone).exclude(id=customer.id).exists()

    def _update_customer_phone_full_name(self, c: Customer, phone: str, full_name: str) -> Customer:
        c.phone = phone
        c.full_name = full_name
        c.save()
        return c

    def reset_customer_groups(self, customer: Customer, groups: list):
        from groups.models import BusinessmanGroups
        if groups is None:
            return customer
        # for g in groups:
        #     g.add_member(customer)
        BusinessmanGroups.reset_customer_groups(groups, customer)
        return customer


customer_service = CustomerService()
