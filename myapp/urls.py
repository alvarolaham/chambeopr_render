from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.generic.base import TemplateView
from myapp.views import (
    become_a_pro,
    car_and_vehicle_services,
    dashboard,
    delete_account,
    delete_pro_account,
    events_services,
    get_rates_and_services,
    get_services,
    home_services,
    index,
    login_view,
    logout_view,
    moving_services,
    onboarding,
    password_reset_code,
    password_reset_complete,
    password_reset_confirm,
    password_reset_request,
    pet_services,
    professional_services,
    save_rates,
    search_services,
    signup,
    update_availability,
    update_services,
    upload_profile_picture,
    delete_profile_picture,
    get_user_profile_pic,
    upload_profile_picture_dashboard,
)

urlpatterns = [
    path("", index, name="index"),
    path("signup/", signup, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path(
        "upload_profile_picture/",
        upload_profile_picture,
        name="upload_profile_picture",
    ),
    path(
        "upload_profile_picture_dashboard/",
        upload_profile_picture_dashboard,
        name="upload_profile_picture_dashboard",
    ),
    path(
        "delete_profile_picture/",
        delete_profile_picture,
        name="delete_profile_picture",
    ),
    path(
        "get_user_profile_pic/",
        get_user_profile_pic,
        name="get_user_profile_pic",
    ),
    path("delete_account/", delete_account, name="delete_account"),
    path("delete-pro-account/", delete_pro_account, name="delete_pro_account"),
    path("home_services/", home_services, name="home_services"),
    path(
        "car_and_vehicle_services/",
        car_and_vehicle_services,
        name="car_and_vehicle_services",
    ),
    path("pet_services/", pet_services, name="pet_services"),
    path("moving_services/", moving_services, name="moving_services"),
    path(
        "professional_services/",
        professional_services,
        name="professional_services",
    ),
    path("events_services/", events_services, name="events_services"),
    path("become-a-pro/", become_a_pro, name="become_a_pro"),
    path("onboarding/", onboarding, name="onboarding"),
    path("password_reset/", password_reset_request, name="password_reset"),
    path(
        "password_reset/code/", password_reset_code, name="password_reset_code"
    ),
    path(
        "password_reset/confirm/<uidb64>/<token>/",
        password_reset_confirm,
        name="password_reset_confirm",
    ),
    path(
        "password_reset/done/",
        TemplateView.as_view(
            template_name="myapp/accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/done/", password_reset_complete, name="password_reset_complete"
    ),
    path("search/", search_services, name="search_services"),
    path("api/get-services/", get_services, name="get_services"),
    path("api/save-rates/", save_rates, name="save_rates"),
    path("dashboard/", dashboard, name="dashboard"),
    path(
        "api/get-rates-and-services/",
        get_rates_and_services,
        name="get_rates_and_services",
    ),
    path(
        "api/update-availability/",
        update_availability,
        name="update_availability",
    ),
    path("api/update-services/", update_services, name="update_services"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
