from django.db import models
from users.models import Businessman

# Create your models here.


class Festival(models.Model):

    name = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    is_general = models.BooleanField()
    discount_code = models.CharField(max_length=12)
    percent_off = models.PositiveIntegerField(default=0)
    flat_rate_off = models.PositiveIntegerField(default=0)
    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
