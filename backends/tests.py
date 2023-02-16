from django.contrib.auth.models import User
from django.test import TestCase

from .models import Service, RecordingTime, DayOfWeek


class ServiceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        rec_time = RecordingTime.objects.create(time='00:30:00')
        day_of_week = DayOfWeek.objects.create(day='Monday', index=1)
        owner = User.objects.create_user(username='john',
                                         email='john_doe@email.com',
                                         password='vovka432')

        service = Service.objects.create(name="Diagnostic station No.254 Autocenter 'Audi'",
                                         address='Grodno st. Obukhova 15',
                                         website='https://stackoverflow.com',
                                         email='example@mail.com',
                                         opening_time='08:00',
                                         closing_time='20:00',
                                         phone_number='+375(29)1234567',
                                         owner=owner)

    def test_get_absolute_url(self):
        question = Service.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEquals(question.get_absolute_url(), "/service/1/")
