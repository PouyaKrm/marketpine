from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Businessman, Customer
from django import forms


class BusinessmanCreationFrom(UserCreationForm):

    class Meta(UserCreationForm):
        model = Businessman
        # fields = ['username', 'password', 'phone',
        #           'business_name', 'address', 'is_verified',
        #           'bot_access', 'instagram_access','bot_access_expire', 'instagram_access_expire' ]

        fields = '__all__'

class BusinessmanChangeForm(UserChangeForm):

    class Meta:
        model = Businessman
        fields = ['username', 'phone',
                  'business_name', 'address', 'is_verified',
                  'bot_access', 'instagram_access', 'bot_access_expire', 'instagram_access_expire']


class CustomerCreationForm(UserCreationForm):

    class Meta:

        model = Customer

        fields = ['phone', 'email', 'first_name', 'last_name']


class CustomerChangeForm(UserChangeForm):

    class Meta:
        model = Customer
        fields = ['phone', 'email', 'first_name', 'last_name']


