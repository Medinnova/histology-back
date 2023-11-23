from django.contrib import admin
from .models import Category


# Register your models here.
@admin.register(Category)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name_display', 'uuid_display', 'parent_id_display', 'owners_display', 'id_display', 'created_at')
