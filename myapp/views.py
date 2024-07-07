from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
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
from django.db import models

UserModel = get_user_model()
logger = logging.getLogger(__name__)

class PasswordResetCode(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

def home(request):
    return render(request, 'myapp/home.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data['email']
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
        else:
            messages.error(request, "Error creating account. Please try again.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'myapp/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
        else:
            messages.error(request, "Invalid login credentials. Please try again.")
    else:
        form = AuthenticationForm()
    return render(request, 'myapp/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('home')
    return render(request, 'myapp/delete_account.html')

def home_services(request):
    services = [
        "Air Conditioning", "Babysitting/Nanny Services", "Construction & Remodeling", "Electrician", 
        "Gardening", "House & Airbnb Cleaning", "Interior Design", "Landscaping", "Painting", "Pest Control", 
        "Plumbing", "Roofing", "Security Systems", "Solar Panel Installation", "Swimming Pool Maintenance"
    ]
    services.sort()  # Ensure services are in alphabetical order
    return render(request, "myapp/home_services.html", {"services": services})

def generate_code():
    return ''.join(random.choices('0123456789', k=6))

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            associated_users = UserModel.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    code = generate_code()
                    PasswordResetCode.objects.create(user=user, code=code)
                    subject = "Password Reset Requested"
                    message = f"Use this code to reset your password: {code}"
                    try:
                        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                        logger.info(f"Password reset code sent to {user.email}")
                    except Exception as e:
                        logger.error(f"Failed to send password reset code to {user.email}. Error: {str(e)}")
            else:
                logger.info(f"Password reset attempted for non-existent email: {email}")
                subject = "Password Reset Requested"
                message = "A password reset was requested for this email, but no account exists."
                try:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
                    logger.info(f"Dummy password reset email sent to non-existent user: {email}")
                except Exception as e:
                    logger.error(f"Failed to send dummy password reset email to {email}. Error: {str(e)}")

            messages.success(request, 'If an account with this email exists, a password reset code has been sent.')
            return redirect('password_reset_code')
    else:
        form = PasswordResetForm()
    return render(request, 'myapp/password_reset.html', {'form': form})

def password_reset_code(request):
    if request.method == "POST":
        form = PasswordResetCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            try:
                reset_code = PasswordResetCode.objects.get(code=code, created_at__gte=timezone.now() - timedelta(minutes=3))
                return redirect('password_reset_confirm', uidb64=urlsafe_base64_encode(force_bytes(reset_code.user.pk)), token=default_token_generator.make_token(reset_code.user))
            except PasswordResetCode.DoesNotExist:
                messages.error(request, 'Invalid or expired code. Please try again.')
                return redirect('password_reset_code')
    else:
        form = PasswordResetCodeForm()
    return render(request, 'myapp/password_reset_code.html', {'form': form})

def password_reset_confirm(request, uidb64=None, token=None):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been set. You can now log in.')
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'myapp/password_reset_confirm.html', {'form': form, 'uidb64': uidb64, 'token': token})
    else:
        messages.error(request, 'The reset link is no longer valid.')
        return redirect('password_reset')

def password_reset_complete(request):
    messages.success(request, 'Your password has been reset successfully.')
    return redirect('login')
