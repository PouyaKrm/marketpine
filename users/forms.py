from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Salesman, Customer
from django import forms

class SalesCreationFrom(UserCreationForm):

    class Meta(UserCreationForm):
        model = Salesman
        fields = '__all__'

class SalesmanChangeForm(UserChangeForm):

    class Meta:
        model = Salesman
        exclude = 'password'


class CustomerCreationForm(UserCreationForm):

    class Meta:

        model = Customer

        fields = ['phone', 'email', 'first_name', 'last_name']


class CustomerChangeForm(UserChangeForm):

    class Meta:
        model = Customer
        fields = ['phone', 'email', 'first_name', 'last_name']


