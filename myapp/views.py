from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login, logout, get_user_model, authenticate
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
import logging
from .forms import CustomUserCreationForm, PasswordResetCodeForm
from django.utils import timezone
from datetime import timedelta
import random
from .models import MyUser, PasswordResetCode

MyUser = get_user_model()
logger = logging.getLogger(__name__)

SERVICES = {
    "home_services": [
        "Air Conditioning",
        "Babysitting/Nanny Services",
        "Construction & Remodeling",
        "Electrician",
        "Gardening",
        "House & Airbnb Cleaning",
        "Interior Design",
        "Landscaping",
        "Painting",
        "Pest Control",
        "Plumbing",
        "Roofing",
        "Security Systems",
        "Solar Panel Installation",
        "Swimming Pool Maintenance",
    ],
    "car_and_vehicle_services": [
        "Car Towing Services",
        "Car Wash and Detailing",
        "Mechanics",
    ],
    "pet_services": [
        "Pet boarding",
        "Pet grooming",
        "Pet training",
    ],
    "moving_services": [
        "Local Moving",
        "Long Distance Moving",
        "Storage Solutions",
    ],
    "professional_services": [
        "Accounting",
        "Legal Services",
        "Consulting",
    ],
    "events_services": [
        "Event Planning",
        "Catering",
        "Entertainment",
    ],
}

def home(request):
    return render(request, "myapp/home.html")

def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data["email"]
            user.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("home")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = CustomUserCreationForm()
    return render(request, "myapp/accounts/signup.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid login credentials. Please try again.")
    return render(request, "myapp/accounts/login.html")

def logout_view(request):
    logout(request)
    return redirect("home")

@login_required
def delete_account(request):
    if request.method == "POST":
        request.user.delete()
        return redirect("home")
    return render(request, "myapp/accounts/delete_account.html")

def home_services(request):
    services = SERVICES["home_services"]
    services.sort()
    return render(request, "myapp/services/home_services.html", {"services": services})

def car_and_vehicle_services(request):
    services = SERVICES["car_and_vehicle_services"]
    services.sort()
    return render(request, "myapp/services/car_and_vehicle_services.html", {"services": services})

def pet_services(request):
    services = SERVICES["pet_services"]
    services.sort()
    return render(request, "myapp/services/pet_services.html", {"services": services})

def moving_services(request):
    services = SERVICES["moving_services"]
    services.sort()
    return render(request, "myapp/services/moving_services.html", {"services": services})

def professional_services(request):
    services = SERVICES["professional_services"]
    services.sort()
    return render(request, "myapp/services/professional_services.html", {"services": services})

def events_services(request):
    services = SERVICES["events_services"]
    services.sort()
    return render(request, "myapp/services/events_services.html", {"services": services})

def search_services(request):
    query = request.GET.get('q')
    if query:
        filtered_services = {
            category: [service for service in services if query.lower() in service.lower()]
            for category, services in SERVICES.items()
        }
    else:
        filtered_services = {}

    return render(request, "myapp/search_results.html", {"query": query, "filtered_services": filtered_services})

def generate_code():
    return "".join(random.choices("0123456789", k=6))

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            associated_users = MyUser.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    code = generate_code()
                    PasswordResetCode.objects.create(user=user, code=code)
                    subject = "Password Reset Requested"
                    message = f"Use this code to reset your password: {code}"
                    try:
                        send_mail(
                            subject,
                            message,
                            settings.DEFAULT_FROM_EMAIL,
                            [user.email],
                            fail_silently=False,
                        )
                        logger.info(f"Password reset code sent to {user.email}")
                        messages.success(
                            request, f"A password reset code has been sent to {email}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to send password reset code to {user.email}. Error: {str(e)}"
                        )
            else:
                messages.error(
                    request, "No account found with the provided email address."
                )

            return redirect("password_reset_code")
    else:
        form = PasswordResetForm()
    return render(request, "myapp/accounts/password_reset.html", {"form": form})

def password_reset_code(request):
    if request.method == "POST":
        form = PasswordResetCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            try:
                reset_code = PasswordResetCode.objects.get(
                    code=code, created_at__gte=timezone.now() - timedelta(minutes=3)
                )
                return redirect(
                    "password_reset_confirm",
                    uidb64=urlsafe_base64_encode(force_bytes(reset_code.user.pk)),
                    token=default_token_generator.make_token(reset_code.user),
                )
            except PasswordResetCode.DoesNotExist:
                messages.error(request, "Invalid or expired code. Please try again.")
                return redirect("password_reset_code")
    else:
        form = PasswordResetCodeForm()
    return render(request, "myapp/accounts/password_reset_code.html", {"form": form})

def password_reset_confirm(request, uidb64=None, token=None):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = MyUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                new_password1 = form.cleaned_data.get("new_password1")
                if user.check_password(new_password1):
                    messages.error(request, "The old and new password are the same.")
                else:
                    if any(
                        item in new_password1.lower()
                        for item in [
                            user.first_name.lower(),
                            user.last_name.lower(),
                            user.username.lower(),
                        ]
                    ):
                        messages.error(
                            request,
                            "The password should not contain your first name, last name, or username.",
                        )
                    else:
                        form.save()
                        messages.success(
                            request,
                            "Your password has been set. You can now log in.",
                            extra_tags="password_set_success",
                        )
                        return redirect("login")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
        else:
            form = SetPasswordForm(user)
        return render(
            request,
            "myapp/accounts/password_reset_confirm.html",
            {
                "form": form,
                "uidb64": uidb64,
                "token": token,
                "user": user,
            },
        )
    else:
        messages.error(request, "The reset link is no longer valid.")
        return redirect("password_reset")

def password_reset_complete(request):
    messages.success(request, "Your password has been reset successfully.")
    return redirect("login")
