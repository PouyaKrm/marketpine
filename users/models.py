from enum import Enum

from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager
from django.db.models.signals import pre_save, post_save
from django.dispatch.dispatcher import receiver
from django.utils import timezone




class AuthStatus:

    AUTHORIZED = '2'
    PENDING = '1'
    UNAUTHORIZED = '0'


class Businessman(AbstractUser):

    def get_upload_path(self, filename):
        return f"{self.id}/logo/{filename}"

    phone = models.CharField(max_length=15)
    address = models.TextField(max_length=500, blank=True, null=True)
    business_name = models.CharField(max_length=1000)
    logo = models.ImageField(upload_to=get_upload_path, null=True, blank=True, max_length=254)
    telegram_id = models.CharField(max_length=20, blank=True, null=True)
    instagram_id = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    AUTHORIZE_CHOICES = [('0', 'UNAUTHORIZED'), ('1', 'PENDING'), ('2', 'AUTHORIZED')]
    authorized = models.CharField(max_length=1, choices=AUTHORIZE_CHOICES, default='0')
    has_sms_panel = models.BooleanField(default=False)
    panel_activation_date = models.DateTimeField(null=True)
    panel_expiration_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.username


class BaseModel(models.Model):

    create_date = models.DateTimeField(auto_now=True, null=True)
    update_date = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        abstract = True


class BusinessmanOneToOneBaseModel(BaseModel):

    businessman = models.OneToOneField(Businessman, on_delete=models.PROTECT)

    class Meta(BaseModel.Meta):
        abstract = True


@receiver(post_save, sender=Businessman)
def businessman_post_save(sender, instance: Businessman, created: bool, **kwargs):
    from invitation.models import FriendInvitationSettings
    if created or not hasattr(instance, 'friendinvitationsettings'):
        FriendInvitationSettings.objects.create(businessman=instance, disabled=True)


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
    full_name = models.CharField(max_length=40, null=True, blank=True)
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


    class Meta:

        db_table = 'customers'

        unique_together = ('businessman', 'phone')

    def __str__(self):

        return self.phone


class BusinessmanRefreshTokens(models.Model):

    generate_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField()
    ip = models.GenericIPAddressField()
    username = models.CharField(max_length=40)


