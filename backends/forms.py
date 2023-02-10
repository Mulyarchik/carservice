from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from django.db import transaction
from django.forms import TextInput

from .models import Customer, Service

my_validator = RegexValidator("^\+?1?\d{9,12}$",
                              "Phone number must be entered in the format: '+375(29)12-12-123'. Up to 12 digits allowed.")

User = get_user_model()


class UserForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(required=True, label='First Name')
    last_name = forms.CharField(required=True, label='Last Name')

    first_name = forms.CharField(
        label=("Name"),
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'type': 'text',
                                          'required': 'true',
                                          }))

    last_name = forms.CharField(
        label=("Surname"),
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'type': 'text',
                                          'required': 'true',
                                          }))
    username = forms.RegexField(
        label=("Username"), max_length=15, regex=r"^[\w.@+-]+$",
        help_text=("Required. 15 characters or fewer. Letters, digits and "
                   "@/./+/-/_ only."),
        error_messages={
            'invalid': ("This value may contain only letters, numbers and "
                        "@/./+/-/_ characters.")},
        widget=TextInput(attrs={'class': 'form-control',
                                'required': 'true',
                                })
    )

    email = forms.CharField(
        label=("Email"),
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'type': 'text',
                                          'required': 'true',
                                          'placeholder': 'for_example@mail.ru'
                                          }))
    password1 = forms.CharField(
        label=("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'required': 'true',
                                          })
    )

    password2 = forms.CharField(
        label=("Password confirmation"),
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'required': 'true',
                                          })
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "password1", "password2")


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(
        label=("Username or Email"),
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'type': 'text',
                                      'required': 'true',
                                      }))
    password = forms.CharField(
        label=("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'type': 'password',
                                          'required': 'true',
                                          }))


class ServiceForm(forms.ModelForm):
    name = forms.CharField(
        label=("Name"),
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'type': 'text',
                                      'required': 'true',
                                      }))

    address = forms.CharField(
        label=("Address"),
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'type': 'text',
                                      'required': 'true',
                                      }))

    website = forms.CharField(
        label=("URL"),
        widget=forms.URLInput(attrs={'class': 'form-control',
                                     'type': 'text',
                                     'required': 'true',
                                     'placeholder': 'URL'
                                     }))

    email = forms.CharField(
        label=("Email"),
        widget=forms.EmailInput(attrs={'class': 'form-control',
                                       'type': 'text',
                                       'required': 'true',
                                       'placeholder': 'for_example@mail.ru'
                                       }))

    working_days = forms.CharField(
        label=("Working Days"),
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'type': 'text',
                                      'required': 'true',
                                      }))

    opening_time = forms.TimeField(input_formats=['%H:%M'],
                                   label=("Opening Time"),
                                   widget=forms.TimeInput(attrs={'class': 'form-control', }))

    closing_time = forms.TimeField(input_formats=['%H:%M'],
                                   label=("Closing Time"),
                                   widget=forms.TimeInput(attrs={'class': 'form-control', }))

    phone_number = forms.RegexField(
        label=("Phone number"),
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'type': 'text',
                                      'required': 'true',
                                      }),
        regex=r'^\+?1?\d{9,15}$')

    class Meta:
        model = Service
        fields = (
            'name', 'address', 'website', 'email', 'working_days', 'opening_time', 'closing_time',
            'phone_number')

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user')
        self._recording_time = kwargs.pop('recording_time')
        self._working_days = kwargs.pop('working_days')
        super(ServiceForm, self).__init__(*args, **kwargs)

    @transaction.atomic
    def save(self, commit=True):
        service = super(ServiceForm, self).save(commit=False)
        service.owner = self._user

        if commit:
            service.save()
            self.save_m2m()

        service.recording_time.add(self._recording_time)
        for day in self._working_days:
            service.working_days.add(day)
        return service.id


class CustomerForm(forms.ModelForm):
    surname = forms.CharField(
        label=("Surname"),
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'type': 'text',
                                      'required': 'true',
                                      }))

    name = forms.CharField(
        label=("Name"),
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'type': 'text',
                                      'required': 'true',
                                      }))

    patronymic = forms.CharField(
        label=("Patronymic"),
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'type': 'text',
                                      'required': 'true',
                                      }))

    car = forms.CharField(
        label=("Car"),
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'type': 'text',
                                      'required': 'true',
                                      }))

    phone_number = forms.RegexField(
        label=("Phone number"),
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'type': 'text',
                                      'required': 'true',
                                      }),
        regex=r'^\+?1?\d{9,15}$')

    email = forms.EmailField(
        label=("Email"),
        widget=forms.EmailInput(attrs={'class': 'form-control',
                                       'type': 'text',
                                       'required': 'true',
                                       }))

    class Meta:
        model = Customer
        fields = ('surname', 'name', 'patronymic', 'car', 'phone_number', 'email')


class CreateDay(forms.Form):
    recording_time = forms.TimeField(input_formats=['%H:%M'],
                                     label=("Opening Time"),
                                     widget=forms.TimeInput(attrs={'class': 'form-control', }))

    opening_time = forms.TimeField(input_formats=['%H:%M'],
                                   label=("Opening Time"),
                                   widget=forms.TimeInput(attrs={'class': 'form-control', }))

    closing_time = forms.TimeField(input_formats=['%H:%M'],
                                   label=("Closing Time"),
                                   widget=forms.TimeInput(attrs={'class': 'form-control', }))
