import datetime

import pandas as pd
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class DayOfWeek(models.Model):
    day = models.CharField(max_length=10)
    index = models.IntegerField(verbose_name='Index')

    def __str__(self):
        return str(self.day)[:3]

    def create(self):
        pass


class RecordingTime(models.Model):
    time = models.TimeField(verbose_name='Recording Time')

    def __str__(self):
        return str(self.time)[:5]


class Service(models.Model):
    name = models.CharField(max_length=200, verbose_name='Name')
    address = models.CharField(max_length=200, verbose_name='Address')
    website = models.URLField(verbose_name='URL')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True)
    email = models.EmailField(verbose_name='Email')
    working_days = models.ManyToManyField(DayOfWeek, blank=True)
    recording_time = models.ManyToManyField(RecordingTime, blank=True)
    opening_time = models.TimeField(max_length=5, verbose_name='Opening Time')
    closing_time = models.TimeField(max_length=5, verbose_name='Closing Time')
    phone_number = models.CharField(max_length=20, validators=[
        RegexValidator(
            regex=r"^\+?375?\(?\d{2}\)\d{7}$",
            message="Phone number must be entered in the format: '+375(29)1234567",
        )
    ])

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def get_absolute_url(self):
        return "/service/%i/" % self.pk

    def __str__(self):
        return self.name


class Date(models.Model):
    day = models.IntegerField(verbose_name='Date')
    service = models.ForeignKey('Service', on_delete=models.PROTECT, blank=True)

    @property
    def date_for_profile(self):
        return str(datetime.date(datetime.datetime.today().year, datetime.datetime.today().month, self.day).strftime(
            '%A, %d %B'))

    def __str__(self):
        return str(self.day)

    def create(self, service_id, working_days):
        for day in working_days:
            Date.objects.create(day=day, service_id=service_id)

    def get_absolute_url(self):
        return "/date/%i/" % self.pk

    class Meta:
        ordering = ['pk']
        verbose_name = 'Date'
        verbose_name_plural = 'Dates'


class Time(models.Model):
    time = models.TimeField(verbose_name='Time')
    day = models.ForeignKey(Date, on_delete=models.CASCADE, blank=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, blank=True, null=True)
    service = models.ForeignKey('Service', on_delete=models.PROTECT, blank=True)

    def __str__(self) -> str:
        return str(self.time)[:5]

    def add(self, service, day, recording_time):
        if str(recording_time) == '00:30':
            freq = '0.5H'
        elif str(recording_time) == '01:00':
            freq = '1H'
        time_list = pd.timedelta_range(start=str(service.opening_time), end=str(service.closing_time),
                                       freq=freq).tolist()
        for i in time_list:
            Time.objects.create(time=str(i)[7:12], day_id=day.id, service_id=service.id)

    class Meta:
        ordering = ['pk']
        verbose_name = 'Time'
        verbose_name_plural = 'Times'


class Customer(models.Model):
    surname = models.CharField(max_length=50, verbose_name='Surname')
    name = models.CharField(max_length=50, verbose_name='Name')
    patronymic = models.CharField(max_length=50, verbose_name='Patronymic')
    car = models.CharField(max_length=50, verbose_name='Car')
    phone_number = models.CharField(max_length=20, validators=[
        RegexValidator(
            regex=r"^\+?375?\(?\d{2}\)\d{7}$",
            message="Phone number must be entered in the format: '+375(29)1234567",
        )
    ])
    email = models.EmailField(verbose_name='Email')

    def __str__(self) -> str:
        return f'customer{self.pk}'
