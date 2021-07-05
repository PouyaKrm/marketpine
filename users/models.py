from django.conf import settings
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.utils import timezone

from base_app.models import PanelDurationBaseModel, PublicFileStorage
from common.util.kavenegar_local import APIException

categories = settings.DEFAULT_BUSINESS_CATEGORY
days_before_expire = settings.ACTIVATION_ALLOW_REFRESH_DAYS_BEFORE_EXPIRE
st = PublicFileStorage(subdir='logos', base_url='logo')


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
        return BusinessCategory.objects.filter(name__icontains=name).all()[:5]

    def __str__(self):
        return self.name


class Businessman(AbstractUser, PanelDurationBaseModel):

    def get_upload_path(self, filename):
        from common.util import generate_url_safe_base64_file_name
        return f"{self.id}/{generate_url_safe_base64_file_name(filename)}"

    AUTHORIZATION_UNAUTHORIZED = '0'
    AUTHORIZATION_PENDING = '1'
    AUTHORIZATION_AUTHORIZED = '2'

    phone = models.CharField(max_length=15)
    business_name = models.CharField(max_length=1000)
    logo = models.ImageField(storage=st, upload_to=get_upload_path, null=True, blank=True, max_length=254)
    telegram_id = models.CharField(max_length=20, blank=True, null=True)
    instagram_id = models.CharField(max_length=20, blank=True, null=True)
    page_id = models.CharField(max_length=40, unique=True, blank=True, null=True)
    business_category = models.ForeignKey(BusinessCategory, on_delete=models.PROTECT, null=True)
    is_phone_verified = models.BooleanField(default=False)
    viewed_intro = models.BooleanField(default=False)
    AUTHORIZE_CHOICES = [(AUTHORIZATION_UNAUTHORIZED, 'UNAUTHORIZED'),
                         (AUTHORIZATION_PENDING, 'PENDING'),
                         (AUTHORIZATION_AUTHORIZED, 'AUTHORIZED')]
    authorized = models.CharField(max_length=1, choices=AUTHORIZE_CHOICES, default='0')
    has_sms_panel: bool = models.BooleanField(default=False)
    panel_activation_date = models.DateTimeField(null=True)
    panel_expiration_date = models.DateTimeField(null=True, blank=True)

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

    def can_activate_panel(self) -> bool:
        if self.is_duration_permanent():
            return False

        if self.is_duration_permanent():
            return False

        if self.panel_expiration_date is None:
            return True

        now = timezone.now()

        return self.panel_expiration_date <= now or self.panel_expiration_date - now <= days_before_expire

    def clean(self):
        super().clean()
        duration_type = self.duration_type
        panel_expire_date = self.panel_expiration_date

        if duration_type != Businessman.DURATION_PERMANENT and panel_expire_date is None:
            raise ValidationError("if duration is not permanent panel expiration date must be set")
        elif duration_type == Businessman.DURATION_PERMANENT and panel_expire_date is not None:
            self.panel_expiration_date = None

        if self.__is_activation_date_bigger_than_expire_date():
            raise ValidationError("expire date should be bigger than activate date")

    def __is_activation_date_bigger_than_expire_date(self) -> bool:
        act = self.panel_activation_date
        exp = self.panel_expiration_date
        return exp is not None and act >= exp

    def is_page_id_set(self):
        return self.page_id is not None and len(self.page_id.strip()) != 0

    def is_panel_active(self) -> bool:
        return self.is_duration_permanent() or (
                self.panel_expiration_date is not None and self.panel_expiration_date > timezone.now())

    def is_authorized(self) -> bool:
        return self.authorized == Businessman.AUTHORIZATION_AUTHORIZED


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


class VerificationCodes(BusinessmanManyToOneBaseModel):
    USED_FOR_PHONE_VERIFICATION = '0'
    USED_FOR_PHONE_CHANGE = '2'

    used_for_choices = [
        (USED_FOR_PHONE_VERIFICATION, 'Phone verification'),
        (USED_FOR_PHONE_CHANGE, 'Phone change')
    ]

    expiration_time = models.DateTimeField()
    num_requested = models.IntegerField(default=1)
    code = models.CharField(max_length=8, unique=True)
    used_for = models.CharField(choices=used_for_choices, default=USED_FOR_PHONE_VERIFICATION, max_length=2)

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


class PhoneChangeVerification(BusinessmanManyToOneBaseModel):
    previous_phone_verification = models.ForeignKey(VerificationCodes,
                                                    on_delete=models.CASCADE,
                                                    related_query_name='phone_change_previous',
                                                    related_name='phone_change_previous')
    new_phone_verification = models.ForeignKey(VerificationCodes,
                                               on_delete=models.CASCADE,
                                               related_name='phone_change_new',
                                               related_query_name='phone_change_new')
    new_phone = models.CharField(max_length=20)


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
    is_phone_confirmed = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone'

    REQUIRED_FIELDS = ['is_active']

    objects = CustomerManager()

    class Meta:
        db_table = 'customers'

        # unique_together = ('businessman', 'phone')

    def __str__(self):
        return self.phone

    def is_full_name_set(self) -> bool:
        return self.full_name is not None and len(self.full_name) > 0


class BusinessmanRefreshTokens(models.Model):
    generate_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField()
    ip = models.GenericIPAddressField()
    username = models.CharField(max_length=40)


class BusinessmanCustomer(BaseModel):
    JOINED_BY_PANEL = '0'
    JOINED_BY_CUSTOMER_APP = '1'
    JOINED_BY_INVITATION = '2'
    joined_by_choices = [
        (JOINED_BY_PANEL, 'By Panel'),
        (JOINED_BY_CUSTOMER_APP, 'Customer App'),
        (JOINED_BY_INVITATION, 'Joined by invitation')
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='connected_businessmans',
                                 related_query_name='connected_businessmans')
    businessman = models.ForeignKey(Businessman, on_delete=models.PROTECT, related_name='connected_customers',
                                    related_query_name='connected_customers')
    joined_by = models.CharField(max_length=2, default=JOINED_BY_PANEL, choices=joined_by_choices)

    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = ['businessman', 'customer']
