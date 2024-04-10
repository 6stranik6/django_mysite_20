from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

from myauth.models import Profile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', 'bio')
