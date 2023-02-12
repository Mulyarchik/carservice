import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from ...factories import (
    RecordingTimeFactory, DayOfWeekFactory, ServiceOwnerFactory, ServiceFactory)
from ...models import RecordingTime, DayOfWeek, Service, Date
from ...views import create_working_days


NUM_DAYS = 7
NUM_RECORDING_TIMES = 2

NUM_SERVICES = 7
NUM_SERVICE_ONWERS = 7

SERVICE_DAY_MAX = 7
SERVICE_REC_TIME_MAX = 1

User = get_user_model()

class Command(BaseCommand):
    help = "Generates test data"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old data...")
        models = [RecordingTime, DayOfWeek, Date, Service, User]
        for m in models:
            m.objects.all().delete()

        self.stdout.write("Creating new data...")

        days = []
        for x in range(NUM_DAYS):
            day = DayOfWeekFactory()
            days.append(day)

        recording_times = []
        for _ in range(NUM_RECORDING_TIMES):
            rec_time = RecordingTimeFactory()
            recording_times.append(rec_time)

        service_onwers = []
        for _ in range(NUM_SERVICE_ONWERS):
            owner = ServiceOwnerFactory()
            service_onwers.append(owner)

        opening_times = ["08:00", "09:00", "10:00", "11:00"]
        closing_times = ["17:00", "18:00", "19:00", "20:00"]
        for _ in range(NUM_SERVICES):
            owner = random.choice(service_onwers)
            opening_time = random.choice(opening_times)
            closing_time = random.choice(closing_times)
            service = ServiceFactory(opening_time=opening_time, closing_time=closing_time, owner=owner)

            recording_time = random.choice(recording_times)
            service.recording_time.add(recording_time)

            working_days = random.choices(
                days,
                k=SERVICE_DAY_MAX
            )
            working_days = set(working_days)

            list_working_days = []
            for i in working_days:
                list_working_days.append(i.pk)
            service.working_days.add(*working_days)

            Date().create(service.id, create_working_days(list_working_days))

        self.stdout.write("New data successfully сreated")
