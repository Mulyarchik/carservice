from django.conf.urls.static import static
from django.urls import path

from .views import *

app_name = 'vlads_app'

urlpatterns = [
                  path('', home, name='home'),
                  path('register/', user_signup, name='user_signup'),
                  path('login/', user_login, name='user_login'),
                  path('logout/', user_logout, name='logout'),
                  path('services/', services, name='services'),
                  # path('registration/', backends, name='backends'),
                  path('date/<int:day_id>/time/', choose_time, name='choose_time'),
                  path('date/<int:day_id>/time/<int:time_id>/', profile, name='profile'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
              + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
