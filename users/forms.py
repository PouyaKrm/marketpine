from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Salesman

class SalesCreationFrom(UserCreationForm):

    class Meta(UserCreationForm):
        model = Salesman
        fields = ['username', 'phone', 'address']

class SalesmanChangeForm(UserChangeForm):

    class Meta:
        model = Salesman
        fields = ['username', 'phone', 'email']
