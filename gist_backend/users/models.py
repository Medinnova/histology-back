from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from users.managers import CustomUserManager
from university.models import University
from subscription.models import Subscription
import string
import random

from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.core.mail import send_mail
from gist_backend.settings import EMAIL_HOST_USER

from rolepermissions.roles import assign_role

class User(AbstractUser):
    # Имя
    first_name = models.CharField(max_length=25, default='')
    # Фамилия
    last_name = models.CharField(max_length=25, default='')
    # Отчество
    surname = models.CharField(max_length=30, default='')
    # ID Тарифа
    tariff_id = models.IntegerField(default=0)
    # Phone Number
    phone_number = models.CharField(max_length=20, default='')
    # Univerisity
    university = models.ForeignKey(University, on_delete=models.CASCADE, blank=True, null=True)
    # Подписка
    subscription = models.OneToOneField(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    
    objects = CustomUserManager()

    # def save(self, *args, **kwargs):
    #     """Хэширует пароль и сохраняет его в базе данных"""
    #     self.is_active = True
    #     if self.username:
    #         self.email = self.username
    #     if self.password:
    #         self.password = make_password(self.password)
    #         print("set_password")
    #     super().save(*args, **kwargs)

    # def set_password(self, new_password):
    #     self.password = make_password(new_password)
    #     self.save()

    @admin.display(description='Логин')
    def username_display(self):
        return self.username

    @admin.display(description='Почта')
    def email_display(self):
        return self.email

    @admin.display(description='Дата регистрации')
    def date_joined_display(self):
        return self.date_joined

    @admin.display(boolean=True, description='Редактор')
    def is_staff_display(self):
        return self.is_staff

    @admin.display(boolean=True, description='Администратор')
    def is_superuser_display(self):
        return self.is_superuser

    @admin.display(description='Идентификатор')
    def id_display(self):
        return f'ID:{self.id}'  

    @admin.display(description='Университет')
    def university_display(self):
        return self.university

    def __str__(self):
        return self.username


# Подверждение кода по почте
class Confirmation(models.Model):
    email = models.CharField(max_length=100, default='')
    code = models.CharField(max_length=6, default='')

    def save(self, *args, **kwargs):
        """Генерируем код"""
        if not self.code:
            for confirmation in Confirmation.objects.filter(email=self.email):
                confirmation.delete()

            letters = string.digits
            code_length = 6
            random_str = ''.join(random.choice(letters) for i in range(code_length))
            self.code = random_str
            try:
                html_message = render_to_string('confirm_code.html', {'code': random_str})
                plain_message = strip_tags(html_message)
                send_mail(
                    "Подтверждение почты",
                    plain_message,
                    EMAIL_HOST_USER,
                    [self.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                # email = EmailMessage('Подтверждение почты', "Для подтверждения вашей почты введите этот код: <h2>{0}</h2>".format(random_str), to=[self.email])
                # email.send()
            except Exception as e:
                print("ОШИБКА ПРИ ОТПРАВКЕ EMAIL: ", e)

        super().save(*args, **kwargs)
    
    @admin.display(description='Почта')
    def email_display(self):
        return self.email
    
    @admin.display(description='Код подтверждения')
    def code_display(self):
        return self.code