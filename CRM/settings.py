"""
Django settings for CRM project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
import datetime
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost']


# Application definition

INSTALLED_APPS = [
    'rest_framework',
    'users',
    'panelmodulus',
    'customers',
    'corsheaders',
    'groups',
    'smspanel',
    'festivals',
    'invitation',
    'dashboard',
    'customerpurchase',
    'rest_framework_swagger',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

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

MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'uploaded_media')

MAX_LOGO_SIZE = 800000

AUTH_USER_MODEL = 'users.Businessman'


REST_FRAMEWORK = {

    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 10,

    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',

    ),

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),

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
CORS_EXPOSE_HEADERS = [
    'authorization',
    'content-type',
]

try:
    from .local_settings import *
except ImportError:
    pass

