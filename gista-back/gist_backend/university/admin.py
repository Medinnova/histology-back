from django.contrib import admin
from .models import University, Request, UniversityCode


# Register your models here.

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Форма для создания универа
        form.base_fields["name"].label = "Имя университета"
        form.base_fields['address'].label = "Адрес университета"        
        
        return form

    # Кортеж столбцов, отображаемых в списке универов
    list_display = ('name_display', 'address_display')

    # Настройка фильтра для поиска по полям
    search_fields = ('name__icontains', 'address__icontains')

    # Поля для добавления нового универа
    fields = ('name', 'address')


admin.site.register(Request)
admin.site.register(UniversityCode)