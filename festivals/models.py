from django.db import models
from users.models import Businessman, Customer


# Create your models here.


class Festival(models.Model):

    name = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    discount_code = models.CharField(max_length=12)
    percent_off = models.PositiveIntegerField(default=0)
    flat_rate_off = models.PositiveIntegerField(default=0)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    customers = models.ManyToManyField(Customer)

    class Meta:

        unique_together = [['businessman', 'name'], ['businessman', 'discount_code']]


# class CustomerFestival(models.Model):
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
#     festival = models.ForeignKey(Festival, on_delete=models.CASCADE)
#
#     class Meta:
#         unique_together = ['customer', 'festival']
