from django.utils import timezone

CUSTOMER_ONE_TIME_PASSWORD_EXPIRE_DELTA = timezone.timedelta(minutes=10)

CUSTOMER_APP_PAGINATION_SETTINGS = {
    'DEFAULT_PAGE_SIZE': 8,
    'MAX_PAGE_SIZE': 20,
    'PAGE_SIZE_QUERY_PARAM': 'page_size'
}

BUSINESSMAN_PAGE_URL = 'https://moshtarino.com/{}'
VIDEO_PAGE_URL = 'https://moshtarino.com/v/{}'

CUSTOMER_APP_FRONTEND_PATHS = [
    'login',
    'profile',
    'markets',
    'discounts',
    'get-discount'
]
