from django.urls import path

from .views import *

app_name = 'vlads_app'

urlpatterns = [
    path('', home, name='home'),
    path('register/', user_signup, name='user_signup'),
    path('login/', user_login, name='user_login'),
    path('logout/', user_logout, name='logout'),
    path('services/', services, name='services'),
    path('list_of_services/', list_of_services, name='list_of_services'),
    path('services2/<int:service_id>/', services2, name='services2'),
    path('services2/<int:service_id>/day/<int:day_id>/', services2_time, name='services2_time'),
    path('services2/<int:service_id>/day/<int:day_id>/time/<int:time_id>/add_customer/', profile2, name='profile2'),
    path('profile/<int:user_id>/', view_profile, name='profile'),

]

# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
