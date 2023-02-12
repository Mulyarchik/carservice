import factory.fuzzy
from django.conf import settings
from factory.django import DjangoModelFactory
from faker import Faker

from .models import DayOfWeek, RecordingTime, Service

faker = Faker()

names = [faker.unique.first_name() for i in range(200)]

days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
index_of_days = [1, 2, 3, 4, 5, 6, 7]
recording_times = ['00:30', '01:00']


class DayOfWeekFactory(DjangoModelFactory):
    class Meta:
        model = DayOfWeek

    day = factory.Iterator(days_of_week)
    index = factory.Iterator(index_of_days)


class RecordingTimeFactory(DjangoModelFactory):
    class Meta:
        model = RecordingTime

    time = factory.Iterator(recording_times)


class ServiceOwnerFactory(DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Iterator(names)
    email = factory.LazyAttribute(lambda obj: '%s@example.com' % obj.username)
    password = factory.PostGenerationMethodCall('set_password', 'adm1n')

    is_superuser = False
    is_staff = False
    is_active = False


class ServiceFactory(DjangoModelFactory):
    class Meta:
        model = Service

    name = factory.Sequence(lambda n: "Diagnostic station No. {}".format(n))
    address = factory.Faker("street_address")
    website = factory.Faker("url")
    email = factory.Faker("email")
    working_days = factory.RelatedFactory(DayOfWeekFactory)
    recording_time = factory.RelatedFactory(RecordingTimeFactory)
    phone_number = '+375291234567'
