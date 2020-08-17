from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.conf import settings
from django.utils import timezone

from common.util.kavenegar_local import APIException

categories = settings.DEFAULT_BUSINESS_CATEGORY


class AuthStatus:
    AUTHORIZED = '2'
    PENDING = '1'
    UNAUTHORIZED = '0'


class BaseModel(models.Model):
    create_date = models.DateTimeField(auto_now_add=True, null=True)
    update_date = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class BusinessCategory(BaseModel):
    name = models.CharField(max_length=40)

    @staticmethod
    def create_default_categories():
        if BusinessCategory.objects.count() != 0:
            return
        BusinessCategory.objects.bulk_create([BusinessCategory(name=n) for n in categories])

    @staticmethod
    def get_top5_category(name: str = None):
        if name is None or name == '':
            return BusinessCategory.objects.all()[:5]
        return BusinessCategory.objects.filter(name__startswith=name).all()[:5]

    def __str__(self):
        return self.name


class Businessman(AbstractUser):

    def get_upload_path(self, filename):
        return f"{self.id}/logo/{filename}"

    phone = models.CharField(max_length=15)
    address = models.TextField(max_length=500, blank=True, null=True)
    business_name = models.CharField(max_length=1000)
    logo = models.ImageField(upload_to=get_upload_path, null=True, blank=True, max_length=254)
    telegram_id = models.CharField(max_length=20, blank=True, null=True)
    instagram_id = models.CharField(max_length=20, blank=True, null=True)
    business_category = models.ForeignKey(BusinessCategory, on_delete=models.PROTECT, null=True)
    is_verified = models.BooleanField(default=False)
    AUTHORIZE_CHOICES = [('0', 'UNAUTHORIZED'), ('1', 'PENDING'), ('2', 'AUTHORIZED')]
    authorized = models.CharField(max_length=1, choices=AUTHORIZE_CHOICES, default='0')
    has_sms_panel = models.BooleanField(default=False)
    panel_activation_date = models.DateTimeField(null=True)
    panel_expiration_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.username

    def username_phone_email_exists(self, username: str, email: str, phone: str) -> (bool, bool, bool):
        result1 = False
        result2 = False
        result3 = False
        if username is not None and username != '':
            result1 = Businessman.objects.filter(username=username).exists()
        if email is not None and email != '':
            result2 = Businessman.objects.filter(email=email).exists()
        if phone is not None and phone != '':
            result3 = Businessman.objects.filter(phone=phone).exists()

        return result1, result2, result3


class BusinessmanOneToOneBaseModel(BaseModel):
    businessman = models.OneToOneField(Businessman, on_delete=models.PROTECT)

    class Meta(BaseModel.Meta):
        abstract = True


class BusinessmanManyToOneBaseModel(BaseModel):
    businessman = models.ForeignKey(Businessman, on_delete=models.PROTECT)

    class Meta(BaseModel.Meta):
        abstract = True


@receiver(post_save, sender=Businessman)
def businessman_post_save(sender, instance: Businessman, created: bool, **kwargs):
    from customer_return_plan.invitation.services import FriendInvitationService
    FriendInvitationService().try_create_invitation_setting(instance)
    from customer_return_plan.loyalty.services import loyalty_service
    loyalty_service.try_create_loyalty_setting_for_businessman(instance)
    from panelsetting.models import PanelSetting
    PanelSetting.try_create_panel_setting_for_businessman(instance)


class VerificationCodes(BusinessmanManyToOneBaseModel):
    expiration_time = models.DateTimeField()
    num_requested = models.IntegerField(default=1)
    code = models.CharField(max_length=8, unique=True)

    def __str__(self):
        return self.code

    def try_resend_verification_code(self, user_id: int) -> (bool, bool, bool):
        from common.util.sms_panel.message import SystemSMSMessage

        try:
            user = Businessman.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return False, False, False
        vcode = VerificationCodes.objects.filter(businessman=user, expiration_time__gt=timezone.now(),
                                                 num_requested__lt=2,
                                                 update_date__lte=timezone.now() - timezone.timedelta(
                                                     minutes=1)).first()
        if vcode is None:
            return True, False, False
        try:
            SystemSMSMessage().send_verification_code(vcode.businessman.phone, vcode.code)
        except APIException as e:
            return True, True, False
        vcode.num_requested += 1
        vcode.save()
        return True, True, True


class CustomerManager(BaseUserManager):

    def create_user(self, phone, email=None, **extra_fields):

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
    phone = models.CharField(max_length=15, unique=True)
    register_date = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=40, null=True, blank=True)
    telegram_id = models.CharField(max_length=40, null=True, blank=True)
    instagram_id = models.CharField(max_length=40, null=True, blank=True)
    businessmans = models.ManyToManyField(Businessman, related_name="customers", related_query_name='customers',
                                          through='BusinessmanCustomer')
    email = models.EmailField(blank=True, null=True, unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(null=True, auto_now_add=True)
    update_date = models.DateTimeField(null=True, auto_now=True)

    USERNAME_FIELD = 'phone'

    REQUIRED_FIELDS = ['is_active']

    objects = CustomerManager()

    class Meta:
        db_table = 'customers'

        # unique_together = ('businessman', 'phone')

    def __str__(self):
        return self.phone

    def register(self, businessman: Businessman, phone: str, full_name: str):
        obj = Customer.objects.create(businessman=businessman, phone=phone, full_name=full_name)
        from smspanel.services import SendSMSMessage
        if businessman.panelsetting.send_welcome_message:
            SendSMSMessage().welcome_message(businessman.panelsetting.welcome_message, businessman, obj)
        return obj


class BusinessmanRefreshTokens(models.Model):
    generate_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField()
    ip = models.GenericIPAddressField()
    username = models.CharField(max_length=40)


class BusinessmanCustomer(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='connected_businessmans',
                                 related_query_name='connected_businessmans')
    businessman = models.ForeignKey(Businessman, on_delete=models.PROTECT, related_name='connected_customers',
                                    related_query_name='connected_customers')

    class Meta:
        unique_together = ['businessman', 'customer']
