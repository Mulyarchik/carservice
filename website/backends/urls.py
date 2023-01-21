from django.urls import path

from .views import *

app_name = 'vlads_app'

urlpatterns = [
    path('', home, name='home'),
    path('accounts/register/', user_signup, name='user_signup'),
    path('accounts/login/', user_login, name='user_login'),
    path('accounts/logout/', user_logout, name='logout'),
    path('services/', service_selection, name='service_selection'),
    path('service/add/', add_service, name='add_service'),
    path('service/<int:service_id>/', day_selection, name='day_selection'),
    path('service/<int:service_id>/day/<int:day_id>/', time_selection, name='time_selection'),
    path('service/<int:service_id>/day/<int:day_id>/add', day_add, name='day_add'),
    path('service/<int:service_id>/day/<int:day_id>/update', day_update, name='day_update'),
    path('service/<int:service_id>/day/<int:day_id>/delete', day_delete, name='day_delete'),
    path('service/<int:service_id>/day/<int:day_id>/time/<int:time_id>/add_customer/', add_customer,
         name='add_customer'),
    path('profile/<int:user_id>/', profile, name='profile'),

]

# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
