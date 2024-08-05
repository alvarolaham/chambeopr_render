import json
import logging
import secrets
import os
from collections import defaultdict
from datetime import timedelta

from django.core.files.storage import default_storage, FileSystemStorage
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.http import require_POST

from .forms import (
    CustomUserCreationForm,
    OnboardingForm,
    PasswordResetCodeForm,
    ProAccountForm,
    ProfilePictureForm,
)
from .models import (
    MyUser,
    PasswordResetCode,
    ProAccount,
    Service,
    UserProfile,
    ZipCode,
)
from django.views.decorators.csrf import csrf_exempt


logger = logging.getLogger(__name__)

# Define a temporary storage location
temp_storage = FileSystemStorage(location='temp/')

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

def index(request):
    logger.info("Rendering index.html")
    context = {"services": SERVICES}
    return render(request, "myapp/index.html", context)

def signup(request):
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
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = CustomUserCreationForm()
    logger.info("Rendering signup.html")
    return render(request, "myapp/accounts/signup.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse_lazy("index"))

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse_lazy("index"))
        else:
            messages.error(
                request, "Invalid login credentials. Please try again."
            )
    return render(request, "myapp/accounts/login.html")

def logout_view(request):
    logout(request)
    return redirect("index")

@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user

        # Log the deletion attempt
        logger.info(f"Attempting to delete account for user: {user.id}")

        try:
            # Delete ProAccount if it exists
            try:
                pro_account = ProAccount.objects.get(user=user)

                # Remove all associated services
                services_count = pro_account.services.count()
                pro_account.services.clear()
                logger.debug(
                    f"Cleared {services_count} services from pro account"
                )

                # Delete the pro account
                pro_account.delete()
                logger.debug("Deleted pro account")

            except ProAccount.DoesNotExist:
                logger.debug("User did not have a pro account")

            # Delete UserProfile if it exists
            try:
                user_profile = UserProfile.objects.get(user=user)
                user_profile.delete()
                logger.debug("Deleted user profile")
            except UserProfile.DoesNotExist:
                logger.debug("User did not have a profile")

            # Delete PasswordResetCode if any exist
            PasswordResetCode.objects.filter(user=user).delete()
            logger.debug("Deleted any existing password reset codes")

            # Finally, delete the user account
            user.delete()
            logger.info(f"Successfully deleted user account: {user.id}")

            messages.success(
                request, "Your account has been successfully deleted."
            )
            logout(request)
            return redirect("index")

        except Exception as e:
            logger.error(
                f"Error deleting account for user {user.id}: {str(e)}"
            )
            messages.error(
                request,
                "An error occurred while deleting your account. Please try again.",
            )

    return render(request, "myapp/accounts/delete_account.html")

def home_services(request):
    services = SERVICES["home_services"]
    services.sort()
    return render(
        request, "myapp/services/home_services.html", {"services": services}
    )

def car_and_vehicle_services(request):
    services = SERVICES["car_and_vehicle_services"]
    services.sort()
    return render(
        request,
        "myapp/services/car_and_vehicle_services.html",
        {"services": services},
    )

def pet_services(request):
    services = SERVICES["pet_services"]
    services.sort()
    return render(
        request, "myapp/services/pet_services.html", {"services": services}
    )

def moving_services(request):
    services = SERVICES["moving_services"]
    services.sort()
    return render(
        request, "myapp/services/moving_services.html", {"services": services}
    )

def professional_services(request):
    services = SERVICES["professional_services"]
    services.sort()
    return render(
        request,
        "myapp/services/professional_services.html",
        {"services": services},
    )

def events_services(request):
    services = SERVICES["events_services"]
    services.sort()
    return render(
        request, "myapp/services/events_services.html", {"services": services}
    )

def search_services(request):
    query = request.GET.get("q", "").lower()
    filtered_services = {
        category: [service for service in services if query in service.lower()]
        for category, services in SERVICES.items()
    }
    filtered_services = {k: v for k, v in filtered_services.items() if v}

    return JsonResponse({"filtered_services": filtered_services})

def generate_code():
    return "".join(secrets.choice("0123456789") for _ in range(6))

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
                        logger.info(
                            f"Password reset code sent to {user.email}"
                        )
                        messages.success(
                            request,
                            f"A password reset code has been sent to {email}",
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to send password reset code to {user.email}. Error: {str(e)}"
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
                            "The password should not contain your \
                            first name, last name, or username.",
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

from collections import defaultdict

@login_required
def become_a_pro(request):
    if request.user.is_pro == True:
        return redirect("dashboard")
    else:
        try:
            pro_account = ProAccount.objects.get(user=request.user)
        except ProAccount.DoesNotExist:
            pro_account = None

        if request.method == "POST":
            form = ProAccountForm(request.POST, instance=pro_account)
            if form.is_valid():
                pro_account = form.save(commit=False)
                pro_account.user = request.user
                pro_account.become_a_pro_completed = (
                    True  # Add this field to ProAccount model
                )
                pro_account.save()

                # Handle services
                services = json.loads(request.POST.get("services", "[]"))
                pro_account.services.clear()  # Remove existing services
                for service_name in services:
                    service, created = Service.objects.get_or_create(
                        name=service_name
                    )
                    pro_account.services.add(service)

                messages.success(
                    request, "Pro account information saved successfully!"
                )
                return redirect("onboarding")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = ProAccountForm(instance=pro_account)

        # Fetch services from the database and organize them by category
        services = Service.objects.all()
        categorized_services = defaultdict(list)
        for service in services:
            categorized_services[service.category].append(service.name)

        # Convert defaultdict to regular dict
        categorized_services = dict(categorized_services)

        # Fetch zip codes from the database
        zip_codes = ZipCode.objects.values_list("code", flat=True)
        pr_zip_codes = list(zip_codes)

        context = {
            "form": form,
            "services": categorized_services,  # Pass the categorized services to the template
            "pr_zip_codes": pr_zip_codes,  # Pass the zip codes to the template
        }

        return render(request, "myapp/accounts/become_a_pro.html", context)

@login_required
@require_POST
def delete_pro_account(request):
    try:
        pro_account = ProAccount.objects.get(user=request.user)

        logger.debug(
            f"Attempting to delete pro account for user: {request.user.id}"
        )

        # Remove all associated services
        services_count = pro_account.services.count()
        pro_account.services.clear()
        logger.debug(f"Cleared {services_count} services from pro account")

        # Delete the profile picture if it exists
        try:
            profile = request.user.profile
            if profile.profile_picture:
                profile.profile_picture.delete(save=False)  # Delete the file
            profile.delete()  # Delete the profile instance
            logger.debug("Deleted user profile and profile picture")
        except UserProfile.DoesNotExist:
            logger.debug("User did not have a profile")

        # Delete the pro account
        pro_account.delete()
        logger.debug("Deleted pro account")

        # Update user model
        request.user.is_pro = False
        request.user.pro_account_created_at = None
        request.user.save()
        logger.debug(
            "Updated user model: is_pro set to False, pro_account_created_at set to None"
        )

        # Verify deletion
        if not ProAccount.objects.filter(user=request.user).exists():
            logger.debug("Confirmed: Pro account no longer exists in database")
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
            f"Attempted to delete non-existent pro account for user: {request.user.id}"
        )
        return JsonResponse(
            {"success": False, "error": "Pro account not found."}
        )
    except Exception as e:
        logger.error(
            f"Error deleting pro account for user {request.user.id}: {str(e)}"
        )
        return JsonResponse(
            {
                "success": False,
                "error": "An error occurred while deleting your pro account. Please try again.",
            }
        )

@login_required
def get_services(request):
    pro_account = request.user.proaccount
    services = pro_account.services.all().values("id", "name")
    return JsonResponse(list(services), safe=False)

@login_required
@require_POST
def save_rates(request):
    try:
        pro_account = request.user.proaccount
        rates = json.loads(request.body)
        pro_account.rates = json.dumps(rates)  # Store as JSON string
        pro_account.save()
        return JsonResponse({"success": True})
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON data"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

@login_required
def onboarding(request):
    if request.user.is_pro:
        return redirect("dashboard")
    try:
        pro_account = request.user.proaccount
    except ProAccount.DoesNotExist:
        return redirect("become_a_pro")

    if not pro_account.become_a_pro_completed:
        messages.error(
            request, "Please complete the 'Become a Pro' step first."
        )
        return redirect("become_a_pro")

    if request.method == "POST":
        form = OnboardingForm(request.POST, instance=pro_account)
        if form.is_valid():
            pro_account = form.save(commit=False)
            pro_account.rates = form.cleaned_data["rates"]
            pro_account.availability = form.cleaned_data["availability"]
            pro_account.onboarding_completed = True

            # Save the temporary profile picture if it exists
            temp_profile_picture = request.session.get("temp_profile_picture")
            if temp_profile_picture:
                with temp_storage.open(temp_profile_picture) as temp_file:
                    profile = request.user.profile
                    profile.profile_picture.save(
                        os.path.basename(temp_profile_picture), ContentFile(temp_file.read())
                    )
                temp_storage.delete(
                    temp_profile_picture
                )  # Ensure the temp file is deleted
                del request.session[
                    "temp_profile_picture"
                ]  # Ensure the session data is cleared

            pro_account.save()

            if (
                pro_account.become_a_pro_completed
                and pro_account.onboarding_completed
            ):
                request.user.is_pro = True
                request.user.pro_account_created_at = timezone.now()
                request.user.save()

            messages.success(request, "Profile updated successfully!")
            return JsonResponse(
                {"success": True, "redirect_url": reverse_lazy("dashboard")}
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors})

    form = OnboardingForm(instance=pro_account)
    return render(
        request,
        "myapp/accounts/onboarding.html",
        {"form": form, "business_name": pro_account.business_name},
    )

@login_required
def get_rates_and_services(request):
    try:
        pro_account = request.user.proaccount
        services = pro_account.services.all().values("id", "name")
        rates = json.loads(pro_account.rates) if pro_account.rates else {}
        return JsonResponse(
            {
                "services": list(services),
                "rates": rates,
                "availability": pro_account.availability,
            }
        )
    except ProAccount.DoesNotExist:
        return JsonResponse({"error": "Pro account not found"}, status=404)

@login_required
@require_POST
def update_availability(request):
    try:
        pro_account = request.user.proaccount
        data = json.loads(request.body)
        pro_account.availability = data.get("availability", "")
        pro_account.save()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

@login_required
@require_POST
def update_services(request):
    try:
        pro_account = request.user.proaccount
        data = json.loads(request.body)
        services = data.get("services", [])
        pro_account.services.set(
            services
        )  # This assumes services are passed as a list of IDs
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

# Make sure the dashboard view includes all necessary context
@login_required
def dashboard(request):
    try:
        pro_account = request.user.proaccount
    except ProAccount.DoesNotExist:
        return redirect("become_a_pro")

    services = pro_account.services.all()

    return render(
        request,
        "myapp/accounts/dashboard.html",
        {
            "business_name": pro_account.business_name,
            "availability": pro_account.availability,
            "services": services,
        },
    )

@login_required
@csrf_exempt
def upload_profile_picture(request):
    if request.method == "POST":
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)

        form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            temp_file = form.cleaned_data["profile_picture"]
            temp_file_path = temp_storage.save(f"temp/{temp_file.name}", temp_file)
            request.session["temp_profile_picture"] = temp_file_path
            logger.info(f"Temp file saved at: {temp_file_path}")
            return JsonResponse({"success": True, "temp_file_path": temp_file_path})
        else:
            logger.error(f"Form errors: {form.errors}")
            return JsonResponse({"success": False, "errors": form.errors})

    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
@csrf_exempt
def upload_profile_picture_dashboard(request):
    if request.method == "POST":
        form = ProfilePictureForm(request.POST, request.FILES)
        if form.is_valid():
            profile = request.user.profile
            profile_picture = form.cleaned_data["profile_picture"]

            # Move from temporary storage to default storage (S3)
            temp_file_path = request.session.get("temp_profile_picture")
            if temp_file_path:
                try:
                    with temp_storage.open(temp_file_path) as temp_file:
                        profile.profile_picture.save(
                            os.path.basename(temp_file_path), ContentFile(temp_file.read())
                        )
                    temp_storage.delete(temp_file_path)
                    del request.session["temp_profile_picture"]
                    logger.info(f"Profile picture saved to S3 from {temp_file_path}")
                except Exception as e:
                    logger.error(f"Error moving temp file to S3: {e}")
                    return JsonResponse({"success": False, "error": str(e)})

            profile.save()
            return JsonResponse({"success": True, "profile_picture_url": profile.profile_picture.url})
        else:
            logger.error(f"Form errors: {form.errors}")
            return JsonResponse({"success": False, "errors": form.errors})

    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
def delete_profile_picture(request):
    if request.method == "POST":
        user = request.user
        user.profile.profile_picture.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)

@login_required
def get_user_profile_pic(request):
    try:
        profile = request.user.profile
        profile_pic_url = (
            profile.profile_picture.url if profile.profile_picture else None
        )
    except MyUser.profile.RelatedObjectDoesNotExist:
        profile_pic_url = None

    return JsonResponse({"profile_pic_url": profile_pic_url})
