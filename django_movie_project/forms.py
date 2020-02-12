from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=20)
    first_name = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = ('username', 'last_name', 'first_name', 'password1', 'password2',)
