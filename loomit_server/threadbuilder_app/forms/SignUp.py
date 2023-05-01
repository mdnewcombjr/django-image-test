from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext, gettext_lazy as _


class SignUpForm(UserCreationForm):
    given_name = forms.CharField(max_length=30, required=False, help_text='Optional.', label=_("First name"))
    surname = forms.CharField(max_length=30, required=False, help_text='Optional.', label = _("Last name"))
    email = forms.EmailField(max_length=128, help_text='Required.', label = _("Email address"))

    class Meta:
        model = User
        fields = ('username', 'given_name', 'surname', 'email', 'password1', 'password2', )