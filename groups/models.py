from django.db import models
from users.models import Businessman, Customer

# Create your models here.


class BusinessmanCustomersGroups(models.Model):

    title = models.CharField(max_length=40)
    create_date = models.DateTimeField(auto_now_add=True)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    customer = models.ManyToManyField(Customer)

    def __str__(self):
        return f"{self.title} - {self.businessman.username}"

    class Meta:

        db_table = 'businessman_customers_groups'
