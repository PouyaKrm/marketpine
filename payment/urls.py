from django.urls import path
from .views import *

app_name = "payment"

urlpatterns = [
    path('verify/', verify , name='verify'),
    path('pay/',pay,name="pay")
]
