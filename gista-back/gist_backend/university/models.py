from django.db import models
from django.contrib import admin
import uuid
import random
import string

class UniversityCode(models.Model):
    code = models.CharField(max_length=200, default='')
    university = models.ForeignKey("University", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        """Генерируем 10 значный код"""
        if not self.code:
            letters = string.digits + string.ascii_lowercase
            code_length = 10
            random_str = ''.join(random.choice(letters) for i in range(code_length))
            self.code = random_str
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.university.name

class University(models.Model):
    name = models.CharField(max_length=200, default='')
    address = models.CharField(max_length=200, default='')

    def generate_codes(self, count):        
        i = 0
        while i < count:
            code = UniversityCode.objects.create(university=self)
            code.save()
            i+=1


    @admin.display(description='Имя университета')
    def name_display(self):
        return self.name

    @admin.display(description='Адрес университета')
    def address_display(self):
        return self.address

    def __str__(self):
        return f'{self.name}'


class Request(models.Model):
    university_name = models.CharField(max_length=200, default='')

    def __str__(self):
        return self.university_name



