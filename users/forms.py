from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Businessman, Customer
from django import forms

class SalesCreationFrom(UserCreationForm):

    class Meta(UserCreationForm):
        model = Businessman
        fields = '__all__'

class SalesmanChangeForm(UserChangeForm):

    class Meta:
        model = Businessman
        exclude = 'password'


class CustomerCreationForm(UserCreationForm):

    class Meta:

        model = Customer

        fields = ['phone', 'email', 'first_name', 'last_name']


class CustomerChangeForm(UserChangeForm):

    class Meta:
        model = Customer
        fields = ['phone', 'email', 'first_name', 'last_name']


