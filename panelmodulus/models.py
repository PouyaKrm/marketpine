from django.db import models

# Create your models here.
from users.models import Businessman


class PanelModulus(models.Model):

    name = models.CharField(max_length=20)
    cost = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    businessman = models.ManyToManyField(Businessman, through='BusinessmanModulus')

    class Meta:
        db_table = 'panel_modulus'
        verbose_name = 'Panel Modulus'

    def __str__(self):
        return self.name


class BusinessmanModulus(models.Model):

    businessman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
    module = models.ForeignKey(PanelModulus, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField()

    class Meta:

        db_table = 'businessman_modulus'
        verbose_name = 'Businessman Modulus'
