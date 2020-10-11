from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import QuerySet

from users.models import Customer, BusinessmanManyToOneBaseModel


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
    customers = models.ManyToManyField(Customer)

    def __str__(self):
        return f"{self.title} - {self.businessman.username}"

    class Meta:

        db_table = 'businessman_groups'

    def reset_customers(self, customers):
        # self.customers.exclude(customers__in=list(customers)).delete()
        #
        # for c in customers:
        #     self.customers.add(c)
        # self.save()
        self.customers.set(customers)
        self.save()

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
    def get_all_businessman_normal_groups(user):
        return BusinessmanGroups.objects.filter(businessman=user, type=BusinessmanGroups.TYPE_NORMAL).all()

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

    def add_member(self, customer: Customer) -> Customer:
        exist = self.customers.filter(id=customer.id).exists()
        if not exist:
            self.customers.add(customer)
        return customer

    def is_special_group(self) -> bool:
        """
        All groups are special except Normal Group witch are created by the user
        Returns: True is group is not Normal else, False

        """
        return self.type != BusinessmanGroups.TYPE_NORMAL
