from django import forms
from django.contrib import admin
from .models import User, Confirmation
from users.forms import UserAdminForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from rolepermissions.roles import get_user_roles, assign_role, clear_roles, AbstractUserRole
from users.roles import *

# admin.site.register(User, UserAdmin)
@admin.register(User)
class SectionAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Форма для создания пользователя
        form.base_fields["username"].label = "Имя пользователя"
        form.base_fields['password'].label = "Пароль"
        form.base_fields['is_staff'].label = "Редактор [Поставить галочку]"
        form.base_fields['date_joined'].label = "Зарегистрирован"
        form.base_fields['is_superuser'].label = 'Суперпользователь'
        form.base_fields['email'].label = 'Почта'
        form.base_fields['first_name'].label = 'Имя'
        form.base_fields['last_name'].label = 'Фамилия'
        form.base_fields['surname'].label = 'Отчество'
        form.base_fields['phone_number'].label = 'Номер телефона'
        # Необязательные поля
        form.base_fields['email'].required = False
        form.base_fields['first_name'].required = False
        form.base_fields['last_name'].required = False
        form.base_fields['surname'].required = False
        form.base_fields['phone_number'].required = False
        form.base_fields['university'].required = False
        form.base_fields['subscription'].required = False

        form.base_fields['role'] = forms.ChoiceField(
            choices=[(role.get_name(), role.get_name()) for role in AbstractUserRole.__subclasses__()],
            required=False
        )
        if obj:  # Проверка, что это не новый объект
            user_roles = get_user_roles(obj)
            print("ROLES : ", user_roles)
            if user_roles:
                form.base_fields['role'].initial = user_roles[0].get_name()

        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Обновление роли пользователя, если поле 'role' присутствует в форме
        if 'role' in form.cleaned_data and form.cleaned_data['role']:
            clear_roles(obj)
            assign_role(obj, form.cleaned_data['role'])

    # Кортеж столбцов, отображаемых в списке пользователей
    list_display = ('username_display', 'email_display', 'is_staff_display',
                    'is_superuser_display', 'date_joined_display', 'id_display', 'university_display', 'subscription_display')

    # Настройка фильтра для поиска по полю username
    search_fields = ('username__startswith',)

    # Поля для добавления нового пользователя
    fields = ('username', 'password', 'is_staff', 'date_joined', 'is_superuser', 'email', 'first_name', 'last_name',
              'surname', 'phone_number', 'university', 'subscription')

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