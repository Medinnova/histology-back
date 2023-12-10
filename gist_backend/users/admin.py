from django import forms
from django.contrib import admin
from .models import User, Confirmation
from users.forms import CustomUserChangeForm, UserAdminForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from rolepermissions.roles import get_user_roles, assign_role, clear_roles, AbstractUserRole
from users.roles import *

# admin.site.register(User, UserAdmin)
@admin.register(User)
class SectionAdmin(BaseUserAdmin):
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)

    #     form.base_fields['role'] = forms.ChoiceField(
    #         choices=[(role.get_name(), role.get_name()) for role in AbstractUserRole.__subclasses__()],
    #         required=False
    #     )

    #     if obj:  # Проверка, что это не новый объект
    #         user_roles = get_user_roles(obj)
    #         if user_roles:
    #             form.base_fields['role'].initial = user_roles[0].get_name()

    #     return form
    form = CustomUserChangeForm

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Обновление роли пользователя, если поле 'role' присутствует в форме
        if 'role' in form.cleaned_data and form.cleaned_data['role']:
            clear_roles(obj)
            assign_role(obj, form.cleaned_data['role'])

    fieldsets = (
        ('Личные данные', {'fields': ('username', 'password', 'first_name', 'last_name', 'surname', 'email')}),
        ('Права доступа', {'fields': ('is_staff', 'is_superuser', 'role')}),
        ('Дополнительная информация', {'fields': ('phone_number', 'university', 'subscription', 'date_joined')}),
    )

    # Кортеж столбцов, отображаемых в списке пользователей
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'date_joined')

    # Настройка фильтра для поиска
    search_fields = ('username__startswith',)

    # Фильтры
    list_filter = ('is_staff', 'is_superuser', 'is_active')


@admin.register(Confirmation)
class SectionConfirmation(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Форма для создания пользователя
        form.base_fields["email"].label = "Почта"
        return form

    # Кортеж столбцов, отображаемых в списке
    list_display = ('email_display', 'code_display')

    # Настройка фильтра для поиска
    search_fields = ('email__icontains',)

    # Поля для добавления нового подтверждения
    fields = ('email',)