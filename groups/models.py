from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from users.models import Customer, BusinessmanManyToOneBaseModel, BaseModel


# Create your models here.


class BusinessmanGroups(BusinessmanManyToOneBaseModel):

    TYPE_NORMAL = '0'
    TYPE_TOP_PURCHASE = '1'

    type_choices = [
        (TYPE_NORMAL, 'NORMAL'),
        (TYPE_TOP_PURCHASE, 'TOP_PURCHASE')
    ]

    title = models.CharField(max_length=40)
    type = models.CharField(max_length=2, choices=type_choices, default=TYPE_NORMAL)
    customers = models.ManyToManyField(Customer, related_name='connected_groups', related_query_name='connected_groups',
                                       through='Membership')

    def __str__(self):
        return f"{self.title} - {self.businessman.username}"

    class Meta:

        db_table = 'businessman_groups'

    def reset_customers(self, customers):
        self.customers.set(customers)

    def get_all_customers(self):
        return self.customers.order_by('-membership__create_date').all()


    def customers_total(self):
        return self.customers.count()

    def set_title_customers(self, title, customers):

        """
        updates the title of the group.
        members are updated if group is not special.
        Args:
            title: new title of the group
            customers: new members for the group

        Returns: None

        """

        if not self.is_special_group():
            self.reset_customers(customers)
        self.title = title
        self.save()

    @staticmethod
    def get_all_businessman_groups(user):
        return BusinessmanGroups.objects.filter(businessman=user).all()

    @staticmethod
    def get_all_businessman_normal_groups(user):
        return BusinessmanGroups.get_all_businessman_groups(user).filter(
            type=BusinessmanGroups.TYPE_NORMAL).all()

    @staticmethod
    def get_group_by_id_or_404(user, group_id: int):
        return get_object_or_404(BusinessmanGroups, id=group_id, businessman=user)

    @staticmethod
    def create_group(user, title: str, customers=None):
        group = BusinessmanGroups.objects.create(businessman=user, title=title)
        if customers is not None:
            group.customers.set(customers)
        group.save()
        return group

    @staticmethod
    def is_title_unique(user, title: str) -> bool:
        return not BusinessmanGroups.objects.filter(businessman=user, title=title).exists()

    @staticmethod
    def set_members_for_purchase_top(user, customers):
        try:
            g = BusinessmanGroups.objects.get(businessman=user, type=BusinessmanGroups.TYPE_TOP_PURCHASE)
        except ObjectDoesNotExist:
            g = BusinessmanGroups.objects.create(title=f'top purchase-{user.username}', businessman=user, type=BusinessmanGroups.TYPE_TOP_PURCHASE)
        g.reset_customers(customers)
        return g

    @staticmethod
    def get_group_by_id(user, group_id):
        return BusinessmanGroups.objects.get(businessman=user, id=group_id)

    @staticmethod
    def reset_customer_groups(user, customer: Customer, groups: list):
        g = BusinessmanGroups.objects.filter(businessman=user)
        g_ids = [g.id for g in groups]
        new_groups = g.filter(id__in=g_ids)
        removed_groups = g.exclude(id__in=g_ids)
        for g in new_groups.all():
            g.add_member(customer)

        for g in removed_groups.all():
            g.remove_member(customer)

        return customer


    def add_member(self, customer: Customer) -> Customer:
        exist = self.customers.filter(id=customer.id).exists()
        if not exist:
            Membership.objects.create(group=self, customer=customer)
        return customer

    def remove_member(self, customer: Customer):
        try:
            Membership.objects.get(group=self, customer=customer).delete()
        except ObjectDoesNotExist:
            pass

    def is_special_group(self) -> bool:
        """
        All groups are special except Normal Group witch are created by the user
        Returns: True is group is not Normal else, False

        """
        return self.type != BusinessmanGroups.TYPE_NORMAL

    @staticmethod
    def is_member_of_group(user, customer: Customer, group_id):
        return BusinessmanGroups.objects.filter(businessman=user, customers=customer, id=group_id).exists()


class Membership(BaseModel):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_query_name='membership')
    group = models.ForeignKey(BusinessmanGroups, on_delete=models.CASCADE, related_query_name='membership')

