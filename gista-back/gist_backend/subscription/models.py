from django.db import models
from django.contrib import admin
import uuid
import random
import string
from subscription.enums import SUBSCRIPTION_TYPE, TRANSACTION_TYPE
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.core.validators import MaxValueValidator, MinValueValidator


class Plan(models.Model):
    name = models.CharField(max_length=255)
    price_month = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_half_year = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_year = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @admin.display(description='Имя подписки')
    def name_display(self):
        return self.name

    @admin.display(description='Цена за месяц')
    def price_month_display(self):
        return str(self.price_month)

    @admin.display(description='Цена за полгода')
    def price_half_year_display(self):
        return str(self.price_half_year)
    
    @admin.display(description='Цена за год')
    def price_year_display(self):
        return str(self.price_year)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)    
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=datetime.now)
    end_date = models.DateTimeField()
    duration = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(12)])
    is_auto_renew = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.end_date = self.start_date+relativedelta(months=self.duration)
        super(Subscription, self).save(*args, **kwargs)

    def renew_subscription(self):
        #TODO 
        # написать функицю для оплаты

        # if success
        self.start_date = self.end_date
        self.end_date = self.end_date + relativedelta(months=self.duration)

    @admin.display(description='Имя подписки')
    def name_display(self):
        return self.plan

    @admin.display(description='Длительность подписки (в месяцах)')
    def duration_display(self):
        return self.duration

    @admin.display(description='Дата начала')
    def start_date_display(self):
        return str(self.start_date)

    @admin.display(description='Дата окончания')
    def end_date_display(self):
        return str(self.end_date)

    def __str__(self):
        return f'<Subscrition obj> UUID:{self.uuid}'
