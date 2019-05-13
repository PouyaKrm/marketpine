import os, sys
import django
from CRM.settings import BASE_DIR
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CRM.settings")

django.setup()
