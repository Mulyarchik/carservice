from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import RecordingTime

User._meta.get_field('email')._unique = True
User._meta.get_field('email').blank = False
User._meta.get_field('email').null = False
User._meta.get_field('email').required = True


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = UserCreationForm.Meta.model
        fields = '__all__'
        field_classes = UserCreationForm.Meta.field_classes


class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {'fields': ('email', 'username', 'password1', 'password2')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Important fields'), {'fields': ('email',)}),
    )


# class DateAdmin(admin.ModelAdmin):
#     list_display = ('date1',)
#     #list_editable = ('date',)
#
@admin.register(RecordingTime)
class RecordingTimeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'time', ]
    list_editable = ['time', ]
    list_display_links = None

    def __str__(self):
        return self.time


admin.site.unregister(RecordingTime)
admin.site.register(RecordingTime, RecordingTimeAdmin)
