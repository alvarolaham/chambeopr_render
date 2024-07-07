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

UserModel = get_user_model()
logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'myapp/home.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
        else:
            messages.error(request, "Error creating account. Please try again.")
    else:
        form = UserCreationForm()
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
        "Landscaping", "Gardening", "Painting", "House & Airbnb Cleaning",
        "Pest Control", "Roofing", "Interior Design", "Security Systems",
        "Solar Panel Installation", "Swimming Pool Maintenance", "Babysitting/Nanny Services",
        "Air Conditioning", "Construction & Remodeling", "Electrician", "Plumbing"
    ]
    return render(request, "myapp/home_services.html", {"services": services})

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            associated_users = UserModel.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "myapp/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': request.META['HTTP_HOST'],
                        'site_name': 'ChambeoPR',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email_content = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email_content, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                        logger.info(f"Password reset email sent to {user.email}")
                    except Exception as e:
                        logger.error(f"Failed to send password reset email to {user.email}. Error: {str(e)}")
            else:
                # Send a dummy email for non-existent users
                logger.info(f"Password reset attempted for non-existent email: {email}")
                subject = "Password Reset Requested"
                email_content = "A password reset was requested for this email, but no account exists."
                try:
                    send_mail(subject, email_content, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
                    logger.info(f"Dummy password reset email sent to non-existent user: {email}")
                except Exception as e:
                    logger.error(f"Failed to send dummy password reset email to {email}. Error: {str(e)}")
            
            messages.success(request, 'If an account with this email exists, a password reset link has been sent.')
            return redirect('password_reset_done')
    else:
        form = PasswordResetForm()
    return render(request, 'myapp/password_reset.html', {'form': form})

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
    else:
        messages.error(request, 'The reset link is no longer valid.')
        return redirect('password_reset')

    return render(request, 'myapp/password_reset_confirm.html', {'form': form})

def password_reset_complete(request):
    messages.success(request, 'Your password has been reset successfully.')
    return redirect('login')