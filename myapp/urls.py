from django.urls import path
from myapp.views import (
    home, signup, login_view, logout_view, delete_account,
    home_services, car_and_vehicle_services, pet_services,
    moving_services, professional_services, events_services,
    password_reset_request, password_reset_code, password_reset_confirm, password_reset_complete,
    search_services
)
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('delete_account/', delete_account, name='delete_account'),
    path('home_services/', home_services, name='home_services'),
    path('car_and_vehicle_services/', car_and_vehicle_services, name='car_and_vehicle_services'),
    path('pet_services/', pet_services, name='pet_services'),
    path('moving_services/', moving_services, name='moving_services'),
    path('professional_services/', professional_services, name='professional_services'),
    path('events_services/', events_services, name='events_services'),
    path('password_reset/', password_reset_request, name='password_reset'),
    path('password_reset/code/', password_reset_code, name='password_reset_code'),
    path('password_reset/confirm/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('password_reset/done/', TemplateView.as_view(template_name="myapp/accounts/password_reset_done.html"), name='password_reset_done'),
    path('reset/done/', password_reset_complete, name='password_reset_complete'),
    path('search/', search_services, name='search_services'),  # Added search URL pattern
]
