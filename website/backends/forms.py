from django import forms
from django.core.validators import RegexValidator

from .models import Customer

my_validator = RegexValidator("^\+?1?\d{9,12}$",
                              "Phone number must be entered in the format: '+375(29)12-12-123'. Up to 12 digits allowed.")


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
        #regex=r'^\+?1?\d{9,15}$')
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
