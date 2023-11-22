from django.db import models
import uuid
from django.contrib import admin
from users.models import User
# Create your models here.

class Category(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, default='') # Имя отображается на фронте
    code_name = models.CharField(max_length=150, default='', blank=True, null=True) # Кодовое имя используется для поиска в бэке
    parent = models.ForeignKey('Category', on_delete=models.CASCADE, blank=True, null=True)
    owners = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    # parent = models.ForeignKey("Category", on_delete=models.CASCADE, blank=True, null=True)

    @admin.display(description='Уникальный ID')
    def uuid_display(self):
        return f"{self.uuid}"

    @admin.display(description='Название раздела')
    def name_display(self):
        return f'{self.name}'

    @admin.display(description='UUID Гл.Раздела')
    def parent_id_display(self):
        if not self.parent_id: 
            return 'None'
        return self.parent_id

    @admin.display(description='Владелец')
    def owners_display(self):
        owners = ""
        for owner in self.owners.all():
            owners += owner.username + ", "
        return owners

    @admin.display(description='Идентификатор')
    def id_display(self):
        return f'{self.id}'        

    def __str__(self):
        return f'Секция "{self.name}" у пользователей "{self.owners_display()}"'