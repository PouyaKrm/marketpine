from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager


class Businessman(AbstractUser):

    phone = models.CharField(max_length=15)
    address = models.TextField(max_length=500, blank=True, null=True)
    business_name = models.CharField(max_length=1000)
    bot_access = models.BooleanField(default=False)
    bot_access_expire = models.DateTimeField(blank=True, null=True)
    instagram_access = models.BooleanField(default=False)
    instagram_access_expire = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)


    class Meta:

        db_table="user"

    def __str__(self):
        return self.username

    # def get_customers(self):
    #     return "\n".join(list(self.customer_set.all()))


class VerificationCodes(models.Model):
    businessman = models.OneToOneField(Businessman, on_delete=models.CASCADE)
    expiration_time = models.DateTimeField()
    num_requested = models.IntegerField(default=1)
    code = models.CharField(max_length=8, unique=True)

    def __str__(self):
        return self.code

class CustomerManager(BaseUserManager):

    def create_user(self, phone,  email=None, **extra_fields):

        customer = Customer(phone=phone)

        customer.set_unusable_password()

        if not phone:
            raise ValueError(_('The phone number must be set'))

        if email:
            email = self.normalize_email(email)
            customer.email = email

        customer.save(**extra_fields)

        return customer

    def create_superuser(self, phone, email=None):
        pass



class Customer(AbstractBaseUser):

    password = None
    phone = models.CharField(max_length=15)
    register_date = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=40, blank=True, null=True)
    last_name = models.CharField(max_length=40, blank=True, null=True)
    telegram_id = models.CharField(max_length=40, null=True, blank=True)
    instagram_id = models.CharField(max_length=40, null=True, blank=True)
    businessman = models.ForeignKey(Businessman,  related_name="customers",
                                    on_delete=models.CASCADE, related_query_name='businessman')
    email = models.EmailField(blank=True, null=True, unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone'

    REQUIRED_FIELDS = ['is_active']

    objects = CustomerManager()

    def get_full_name(self):

        return self.first_name + " " + self.last_name

    class Meta:

        db_table = 'customers'

        unique_together = ('businessman', 'phone')

    def __str__(self):

        return self.phone


# class SalesmenCustomer(models.Model):
#
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE
#                                    )
#     salesman = models.ForeignKey(Businessman, on_delete=models.CASCADE)
#     register_date = models.DateTimeField(auto_now_add=True)
#     is_active = models.BooleanField(default=False)
#
#     class Meta:
#
#         db_table = 'salesman_customer'
#         unique_together = ('customer', 'salesman')
#
#     def __str__(self):
#
#         return f"{self.salesman.username}-{self.customer.phone}"