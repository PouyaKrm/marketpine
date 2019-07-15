from .models import VerificationCodes, Businessman
from django.utils import timezone
from faker import Faker


def delete_unverified_businessmans():
    Businessman.objects.raw("DELETE FROM user  WHERE id IN "
                            "(SELECT id FROM user join users_verificationcodes uv on user.id = uv.businessman_id where uv.expiration_time < %s)", timezone.now())
    print('task ran at' + timezone.now().time())


def generate_fake_businessman():
    fake_username=['reza', 'pouya', 'jack', 'dan']

    if Businessman.objects.count() <= 1:
        faker = Faker("fa_IR")
        for i in range(4):
            user = Businessman(username=fake_username[i], is_verified=True, date_joined=timezone.now(), phone=faker.msisdn(),
                        business_name=faker.company(), address=faker.address())
            user.set_password("12345678")
            user.save()
