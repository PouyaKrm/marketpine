"""
Django settings for CRM project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
import datetime
import logging.config
import multiprocessing
import os

from corsheaders.defaults import default_headers
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.conf import settings
from django.utils import timezone
from django.utils.log import DEFAULT_LOGGING

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_UPLOAD_PERMISSIONS = 0o644

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9$%^gnqdq7$k@1x0ayin=axndczmrqy5uu!n3qw&0gqcy*dzog'

REFRESH_KEY_PR = """-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCXEzZ21MDkEzEKx4bax4J7EiiEfWqVUYC5H7m48PLFYCgmAO+/
IIEuBv5PJv/XNA3veqHgTHQ8Y0pg7TBIFOUxJrGnuS+bpsFJ8c/KKLnk2fVs4iGt
Y/fPCRFeoVppqiFWs2gV390suMI16RoKDHoKuR1ChcrTQYQs+QvhU9QitwIDAQAB
AoGAPQG8L7Zwgmmhl0nFklmYvlwx0nbW8J9uDNPb6uwaDUxsShR8vEDDCbQ3Q/1q
uRvDON7bubkGA1DRO1zs717IwjRdGZ3XqJLOaW0YFXGSfAiUneKPx22zvXpt3Ivh
qPlmfpzpuv3u+TYWre80ZUWd+MeWUQGiZ4boUfMe1A4AvlECQQDojpIYqgbDJeZM
055W4Rcdt0u7CYKspe7lF9qjbrKl4CQxzFbXrtn1AboRGgTD+ygcwO6B0P5Shk+m
yXByk72ZAkEApk3l5nc4/Vjus2mWs6NpYqm6qfc62KRnt8IAaRP05SuY1aot8pTF
MBKqqbX6S1tGRJNrtJ+Alx9JYrJFQ+j0zwJAFlhEj1we5DdLBoy6xQxBpVhMTX9f
b+lNp/N/zX5AahG8SJCis3yYcqMk1qnSVWZXd1POVujW1uUS2Cq4xDmP2QJASSUv
/groJP4tlvnVD9PK8VtHv6P+3PSKrdcFSTI+32EqiqecJ/rpM/ix2Y0xtl1B7b2N
fNc+vrlDFMbmEjVvHwJBALNX4AJshJnjq1bPNL0qMoB02ikGsQk+yxHJTGOYEvbI
cghiamAIjLImWkN9HP1gvc/V4PThUXh7GOyMWh+hl/E=
-----END RSA PRIVATE KEY-----"""

REFRESH_KEY_PU = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCXEzZ21MDkEzEKx4bax4J7EiiE
fWqVUYC5H7m48PLFYCgmAO+/IIEuBv5PJv/XNA3veqHgTHQ8Y0pg7TBIFOUxJrGn
uS+bpsFJ8c/KKLnk2fVs4iGtY/fPCRFeoVppqiFWs2gV390suMI16RoKDHoKuR1C
hcrTQYQs+QvhU9QitwIDAQAB
-----END PUBLIC KEY-----"""

REFRESH_TOKEN_EXP_DELTA = timezone.timedelta(days=1)

PAGINATION_PAGE_NUM = 25

FRONTEND_URL = "https://panel.foroshgahino.com"

ACTIVATION_ALLOW_REFRESH_DAYS_BEFORE_EXPIRE = timezone.timedelta(days=2)
ACTIVATION_COST_IN_TOMANS = 1000
ALLOWED_CUSTOMER_REGISTER_FREE = 20

ADMIN_PHONE = '09212617107'

SMS_PANEL = {
    'CUSTOMER_LINE': '10004000030003',
    'SYSTEM_LINE': '10004000020002',
    'VERIFICATION_TEMPLATE_NAME': 'BusinessmanVerify',
    'BUSINESSMAN_NEW_PASSWORD_FORGET_TEMPLATE_NAME': 'BusinessmanForgetPasswordChange',
    'CUSTOMER_ONE_TIME_PASSWORD_TEMPLATE_NAME': 'CustomerOneTimePassword',
    'CUSTOMER_PHONE_CHANGE_TEMPLATE_NAME': 'CustomerPhoneChange',
    'BUSINESSMAN_PHONE_CHANGE_TEMPLATE_NAME': 'BusinessmanPhoneChange',
    'INIT_CREDIT': 150000,
    'API_KEY': '4D4C324E43416D726C65446D7258566A4F59697153444355734E4F4D6B382B57',
    'CUSTOMER_US_PREFIX': 'bp',
    'PID': 1422,
    'MIN_CREDIT': 100000,  # minimum credit that each user must have for sending message
    "MIN_CREDIT_CHARGE": 1000,  # min amount that user can increase their credit in Tomans
    "MAX_CREDIT_CHARGE": 30000,  # max amount that user can increase their credit in Tomans
    "MAX_ALLOWED_CREDIT": 30000,  # max credit that user can have in Tomans
    "SYSTEM_MIN_CREDIT": 300000,  # system min credit in rials
    'MAX_MESSAGE_COST': 600,  # this is used for credit validation before sending message. must be in rials
    'ENGLISH_MAX_CHARS': 612,
    'PERSIAN_MAX_CHARS': 268,
    'TEMPLATE_MIN_CHARS': 10,
    'TEMPLATE_MAX_CHARS': 160,
    # note: Don 't change this value. If you really want, change in SMSTemplate -> content -> max_length too
    'SEND_THREADS_NUMBER': multiprocessing.cpu_count(),
    'MAX_SEND_FAIL_ATTEMPTS': 3,
    'SEND_TEMPLATE_PAGE_SIZE': 150,
    "SEND_PLAIN_CUSTOMERS_MAX_NUMBER": 3,  # allowed number of customer in selecting specific customer for plain send
    "SEND_PLAIN_CUSTOMERS_PAGE_SIZE": 2,
    'SEND_TEMPLATE_MAX_CUSTOMERS': 5,  # allowed number of customer in selecting specific customer for template send
    'MAX_ALLOWED_DEFINED_TEMPLATES': 7,  # defines how many sms templates that user can define
    'MAX_ALLOWED_DEFINED_GROUPS': 20  # defines how many customer groups user can have
}

DOWNLOAD_SETTINGS = {
    'NGINX_LOCATION': 'downloads',
    'NGINX_REDIRECT_HEADER': 'X-Accel-Redirect',
    'ATTACHEMENT_HEADER': 'Content-disposition'
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost']
DOMAIN = "localhost:8000"

# Application definition

INSTALLED_APPS = [
    'base_app',
    'content_marketing',
    'device',
    'payment',
    'rest_framework',
    'users',
    'panelmodulus',
    'customers',
    'corsheaders',
    'groups',
    'smspanel',
    'customer_return_plan',
    'customer_return_plan.festivals',
    'customer_return_plan.invitation',
    'dashboard',
    'customerpurchase',
    'panelprofile',
    'customer_return_plan.loyalty',
    'online_menu',
    'mobile_app_conf',
    'customer_application',
    'background_task',
    'rest_framework_swagger',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'download',
    'download.profiledownload',
    'django_cleanup.apps.CleanupConfig',
    'educations'

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'CRM.middlewares.AppExceptionMiddleware',
]

ROOT_URLCONF = 'CRM.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'CRM.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
LOG_DIR = os.path.join(BASE_DIR, '..', 'logs')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': u'{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'console': {
            'format': u'%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
    },

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },

        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, '..', 'logs/application.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'UTF-8',
        },

        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {

        'django': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            # required to avoid double logging with root logger
        }
    },
}

MAX_LOGO_SIZE = 10000000
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'uploaded_media/')

AUTH_DOC = {
    'MAX_FORM_SIZE': 10000000,
    'MAX_CARD_SIZE': 10000000,
    'MAX_CERTIFICATE_SIZE': 10000000,
}

AUTH_USER_MODEL = 'users.Businessman'

REST_FRAMEWORK = {

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': PAGINATION_PAGE_NUM,

    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',

    ),

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),

    'EXCEPTION_HANDLER': 'CRM.app_exception_handling.custom_exception_handler'

}

JWT_AUTH = {
    'JWT_ENCODE_HANDLER':
        'rest_framework_jwt.utils.jwt_encode_handler',

    'JWT_DECODE_HANDLER':
        'rest_framework_jwt.utils.jwt_decode_handler',

    'JWT_PAYLOAD_HANDLER':
        'rest_framework_jwt.utils.jwt_payload_handler',

    'JWT_PAYLOAD_GET_USER_ID_HANDLER':
        'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',

    'JWT_RESPONSE_PAYLOAD_HANDLER':
        'rest_framework_jwt.utils.jwt_response_payload_handler',

    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_GET_USER_SECRET_KEY': None,
    'JWT_PUBLIC_KEY': None,
    'JWT_PRIVATE_KEY': None,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(minutes=10),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,

    'JWT_ALLOW_REFRESH': False,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),

    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_AUTH_COOKIE': None,

}

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    'x-api-key',
    'x-device-key'
]
CORS_EXPOSE_HEADERS = [
    'authorization',
    'content-type',
]

PUBLIC_FILE_BASE_PATH = os.path.join(BASE_DIR, '..', 'public/')

PRIVATE_FILE_BASE_PATH = os.path.join(BASE_DIR, '..', 'private/')

CONTENT_MARKETING = {
    'MAX_SIZE_VIDEO': '50000000',
    'ALLOWED_TYPES_VIDEO': ['.mp4'],
    'SUB_DIR': 'videos/',
    'VIDEO_CONFIRM_MESSAGE': 'ویدیو بارگزاری شده شما تایید شد',
    'VIDEO_REJECT_MESSAGE': 'ویدیو بارگزاری شده شما رد شد',
    'VIDEO_PAGINATION_PAGE_SIZE': 5,
    'BASE_URL': "/content/video/",
    'THUMBNAIL_MAX_NAME_CHARS': 200,
    'THUMBNAIL_MAX_SIZE': 10000000,
    'NOTIF_TEMPLATE_MAX_CHARS': 100
}

ONLINE_MENU = {
    'SUB_DIR': 'menus/',
    'BASE_URL': '/menu/',
    'MAX_FILE_SIZE': 10000000,
    'MAX_ALLOWED_IMAGES': 30
}

MOBILE_APP_PAGE_CONF = {
    'SUB_DIR': 'mobile_app/',
    'BASE_URL': '/mobile-app/',
    'MAX_HEADER_IMAGE_SIZE': 5000000,
    'MAX_ALLOWED_HEADERS': 4
}

EDUCATIONS = {
    'SUB_DIR': 'educations/',
    'BASE_URL': '/educations/'
}

DEFAULT_BUSINESS_CATEGORY = [
    'سایر',
    'رستوران',
    'کافی شاپ',
]

try:
    from .local_settings import *
except ImportError:
    pass

from .customer_app_settings import *

from .payment_settings import *

from .return_plan_settings import *
