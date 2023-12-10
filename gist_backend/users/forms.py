from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from rolepermissions.roles import get_user_roles, assign_role, clear_roles
from rolepermissions.roles import AbstractUserRole
from django.contrib.auth.forms import UserChangeForm
from users.roles import *

class UserAdminForm(forms.ModelForm):
    role = forms.ChoiceField(choices=[(role.get_name(), role.get_name()) for role in AbstractUserRole.__subclasses__()], required=False)

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            user_roles = get_user_roles(self.instance)
            if user_roles:
                self.fields['role'].initial = user_roles[0].get_name()

    def save(self, commit=True):
        user = super(UserAdminForm, self).save(commit=commit)
        if commit and self.cleaned_data['role']:
            clear_roles(user)
            assign_role(user, self.cleaned_data['role'])
        return user

class CustomUserChangeForm(UserChangeForm):
    role = forms.ChoiceField(
        choices=[(role.get_name(), role.get_name()) for role in AbstractUserRole.__subclasses__()],
        required=False
    )

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            user_roles = get_user_roles(self.instance)
            if user_roles:
                self.fields['role'].initial = user_roles[0].get_name()
