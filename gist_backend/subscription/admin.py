from django.contrib import admin
from subscription.models import Subscription, Plan

# Register your models here.

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Форма для создания универа
        form.base_fields["plan"].label = "План подписки"
        form.base_fields['duration'].label = "Длительность подписки (в месяцах)"        
        form.base_fields['start_date'].label = "Дата начала подписки"        
        form.base_fields['end_date'].label = "Дата окончания подписки"        
        
        return form

    # Кортеж столбцов, отображаемых в списке универов
    list_display = ('name_display', 'duration_display')

    # Поля для добавления нового универа
    fields = ('plan', 'duration', 'start_date', 'end_date')



@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
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