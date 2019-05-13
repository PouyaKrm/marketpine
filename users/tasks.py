from .models import VerificationCodes
import datetime
from background_task import background
from django.utils import timezone

@background(schedule=5)
def delete_expired_codes():

    for i in VerificationCodes.objects.filter(expiration_time__lt=timezone.datetime.now()).all():

        i.businessman.delete()

    print("hello world")
