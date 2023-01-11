from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


# class User(AbstractUser):
#     tariff plan
class Service(models.Model):
    name = models.CharField(max_length=50, verbose_name='Name')
    address = models.CharField(max_length=50, verbose_name='Address')
    website = models.URLField(max_length=200, verbose_name='URL')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True)
    email = models.EmailField(verbose_name='Email')
    working_hours = models.DurationField(verbose_name='Working Hours')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,12}$',
                                 message="Phone number must be entered in the format: '+375(29)12-12-123'. Up to 12 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=13, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'


class Date(models.Model):
    day = models.IntegerField(verbose_name='Date')
    service = models.ForeignKey('Service', on_delete=models.PROTECT, blank=True, null=True)

    def get_absolute_url(self):
        return "/date/%i/" % self.id

    class Meta:
        verbose_name = 'Date'
        verbose_name_plural = 'Dates'


class Time(models.Model):
    time = models.TimeField(verbose_name='Time')
    day = models.ForeignKey(Date, on_delete=models.CASCADE, blank=True, null=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self) -> str:
        return str(self.time)[:5]

    class Meta:
        verbose_name = 'Time'
        verbose_name_plural = 'Times'


class Customer(models.Model):
    surname = models.CharField(max_length=20, verbose_name='Surname')
    name = models.CharField(max_length=20, verbose_name='Name')
    patronymic = models.CharField(max_length=20, verbose_name='Patronymic')
    car = models.CharField(max_length=40, verbose_name='Car')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,12}$',
                                 message="Phone number must be entered in the format: '+375(29)12-12-123'. Up to 12 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=13, blank=True)
    email = models.EmailField(verbose_name='Email')
