"""
This module manages user accounts with these functions:

1. Sign up - Create a new account
2. Log in - Access your account
3. Log out - Exit your account
4. Request password reset - Start the process to change a forgotten password
5. Enter reset code - Verify your identity for password reset
6. Set new password - Complete the password reset process
7. Finish password reset - Confirm your password has been changed
8. Delete account - Permanently remove your entire account
9. Delete pro account - Remove your pro status while keeping your basic account

These functions help users manage their accounts easily and securely.
"""

import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils import timezone
from django.views.decorators.http import require_POST

from myapp.forms import CustomUserCreationForm, PasswordResetCodeForm
from myapp.models import MyUser, PasswordResetCode, UserProfile, ProAccount

# Set up logging
logger = logging.getLogger(__name__)

# pylint: disable=no-member


def signup(request):
    """
    Handle the signup process for new users.

    If the user is already logged in, redirect them to the homepage.
    If the request is a POST, attempt to create a new user with the provided
    data. If the form is valid, log in the user and redirect to the homepage.
    Otherwise, render the signup form with error messages.
    """
    if request.user.is_authenticated:
        return redirect(reverse_lazy("index"))

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data["email"]
            user.save()
            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )
            return redirect(reverse_lazy("index"))

        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, error)
    else:
        form = CustomUserCreationForm()

    logger.info("Rendering signup.html")
    return render(request, "myapp/accounts/signup.html", {"form": form})


def login_view(request):
    """
    Handle user login.

    If the user is already logged in, redirect them to the homepage.
    If the request is a POST, authenticate the user with the provided
    credentials. If successful, log in the user and redirect to the homepage.
    Otherwise, display an error message and re-render the login form.
    """
    if request.user.is_authenticated:
        return redirect(reverse_lazy("index"))

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse_lazy("index"))

        messages.error(request, "Invalid login credentials. Please try again.")
    return render(request, "myapp/accounts/login.html")


def logout_view(request):
    """
    Log the user out and redirect to the homepage.
    """
    logout(request)
    return redirect("index")


def generate_code():
    """
    Generate a 6-digit numeric code for password reset.
    """
    return "".join(secrets.choice("0123456789") for _ in range(6))


def password_reset_request(request):
    """
    Handle password reset requests.

    If the request is a POST, validate the provided email and generate a
    password reset code if the email is associated with an account. Send
    the reset code via email and redirect to the code entry page.
    If no account is found, display an error message.
    """
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
                        logger.info(
                            "Password reset code sent to %s", user.email
                        )
                        messages.success(
                            request,
                            f"A password reset code has been sent to {email}",
                        )
                    except Exception as e:
                        logger.error(
                            "Failed to send password reset code to %s. Error: %s",
                            user.email,
                            str(e),
                        )
            else:
                messages.error(
                    request,
                    "No account found with the provided email address.",
                )

            return redirect("password_reset_code")
    else:
        form = PasswordResetForm()
    return render(
        request, "myapp/accounts/password_reset.html", {"form": form}
    )


def password_reset_code(request):
    """
    Handle the password reset code verification.

    If the request is a POST, validate the provided code. If valid, redirect
    to the password reset confirmation page. If invalid or expired, display
    an error message and allow the user to try again.
    """
    if request.method == "POST":
        form = PasswordResetCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            try:
                reset_code = PasswordResetCode.objects.get(
                    code=code,
                    created_at__gte=timezone.now() - timedelta(minutes=3),
                )
                return redirect(
                    "password_reset_confirm",
                    uidb64=urlsafe_base64_encode(
                        force_bytes(reset_code.user.pk)
                    ),
                    token=default_token_generator.make_token(reset_code.user),
                )
            except PasswordResetCode.DoesNotExist:
                messages.error(
                    request, "Invalid or expired code. Please try again."
                )
                return redirect("password_reset_code")
    else:
        form = PasswordResetCodeForm()
    return render(
        request, "myapp/accounts/password_reset_code.html", {"form": form}
    )


def password_reset_confirm(request, uidb64=None, token=None):
    """
    Handle password reset confirmation.

    Validate the user ID and token. If valid, allow the user to reset their
    password. If the password is successfully reset, redirect to the login page.
    If invalid, display an error message.
    """
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
                    messages.error(
                        request, "The old and new password are the same."
                    )
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
                            (
                                "The password should not contain your "
                                "first name, last name, or username."
                            ),
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
    messages.error(request, "The reset link is no longer valid.")
    return redirect("password_reset")


def password_reset_complete(request):
    """
    Display a success message when the password reset process is complete.
    """
    messages.success(request, "Your password has been reset successfully.")
    return redirect("login")


@login_required
def delete_account(request):
    """
    Handle account deletion for the logged-in user.

    If the request is a POST, attempt to delete the user's account, including
    their associated ProAccount and UserProfile, if any. Log the deletion process
    and display appropriate messages based on success or failure.
    """
    if request.method == "POST":
        user = request.user

        logger.info("Attempting to delete account for user: %d", user.id)

        try:
            with transaction.atomic():
                try:
                    pro_account = ProAccount.objects.get(user=user)
                    services_count = pro_account.services.count()
                    pro_account.services.clear()
                    logger.debug(
                        "Cleared %d services from pro account", services_count
                    )
                    pro_account.delete()
                    logger.debug("Deleted pro account")
                except ProAccount.DoesNotExist:
                    logger.debug("User did not have a pro account")

                try:
                    user_profile = UserProfile.objects.get(user=user)
                    user_profile.delete()
                    logger.debug("Deleted user profile")
                except UserProfile.DoesNotExist:
                    logger.debug("User did not have a profile")

                PasswordResetCode.objects.filter(user=user).delete()
                logger.debug("Deleted any existing password reset codes")

                user.delete()
                logger.info("Successfully deleted user account: %d", user.id)

                messages.success(
                    request, "Your account has been successfully deleted."
                )
                logout(request)
                return redirect("index")

        except Exception as e:
            logger.error(
                "Error deleting account for user %d: %s", user.id, str(e)
            )
            messages.error(
                request,
                "An error occurred while deleting your account. Please try again.",
            )

    return render(request, "myapp/accounts/delete_account.html")


@login_required
@require_POST
def delete_pro_account(request):
    """
    Handle the deletion of a user's ProAccount.

    If the request is a POST, attempt to delete the ProAccount, including
    associated services and user profile picture, if any. Update the user's
    account to reflect the deletion and log the process. Return a JSON response
    indicating success or failure.
    """
    try:
        with transaction.atomic():
            pro_account = ProAccount.objects.get(user=request.user)

            logger.debug(
                "Attempting to delete pro account for user: %d",
                request.user.id,
            )

            services_count = pro_account.services.count()
            pro_account.services.clear()
            logger.debug(
                "Cleared %d services from pro account", services_count
            )

            try:
                profile = request.user.profile
                if profile.profile_picture:
                    profile.profile_picture.delete(save=False)
                profile.delete()
                logger.debug("Deleted user profile and profile picture")
            except UserProfile.DoesNotExist:
                logger.debug("User did not have a profile")

            pro_account.delete()
            logger.debug("Deleted pro account")

            request.user.is_pro = False
            request.user.pro_account_created_at = None
            request.user.save()
            logger.debug(
                "Updated user model: is_pro set to False, pro_account_created_at set to None"
            )

            if not ProAccount.objects.filter(user=request.user).exists():
                logger.debug(
                    "Confirmed: Pro account no longer exists in database"
                )
            else:
                logger.error(
                    "Error: Pro account still exists in database after deletion attempt"
                )

            messages.success(
                request, "Your pro account has been successfully deleted."
            )
            return JsonResponse({"success": True})
    except ProAccount.DoesNotExist:
        logger.warning(
            "Attempted to delete non-existent pro account for user: %d",
            request.user.id,
        )
        return JsonResponse(
            {"success": False, "error": "Pro account not found."}
        )
    except Exception as e:
        logger.error(
            "Error deleting pro account for user %d: %s",
            request.user.id,
            str(e),
        )
        return JsonResponse(
            {
                "success": False,
                "error": "An error occurred while deleting your pro account. Please try again.",
            }
        )
