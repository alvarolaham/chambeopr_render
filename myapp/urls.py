from django.urls import path, include
from myapp.views import home, signup, login_view, logout_view, delete_account, home_services

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('delete_account/', delete_account, name='delete_account'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('home_services/', home_services, name="home_services"),
]
