from django.contrib import admin
from subscription.models import Subscription, Plan

# Register your models here.

@admin.register(Subscription)
class UniversityAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Форма для создания универа
        form.base_fields["plan"].label = "План подписки"
        form.base_fields['duration'].label = "Длительность подписки (в месяцах)"        
        
        return form

    # Кортеж столбцов, отображаемых в списке универов
    list_display = ('name_display', 'duration_display')

    # Поля для добавления нового универа
    fields = ('plan', 'duration')



@admin.register(Plan)
class UniversityAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Форма для создания универа
        form.base_fields["name"].label = "План подписки"
        form.base_fields['price_month'].label = "Цена за месяц"        
        form.base_fields['price_half_year'].label = "Цена за полгода"
        form.base_fields['price_year'].label = "Цена за год"
        return form

    # Кортеж столбцов, отображаемых в списке универов
    list_display = ('name_display', 'price_month_display', 'price_half_year_display', 'price_year_display')

    # Поля для добавления нового универа
    fields = ('name', 'price_month', 'price_half_year', 'price_year')