"""
This module contains view functions for the dashboard of a pro account user.

It includes functions for rendering the dashboard, updating various account details,
and managing profile pictures.
"""

import re
import json
import logging
from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from myapp.views_consolidated.utility_views import ProAccountChecker
from myapp.forms import ProfilePictureForm
from myapp.models import UserProfile, Service

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """
    Render the main dashboard for pro account users.
    """
    try:
        # Check if the user has a pro account
        pro_account = ProAccountChecker.get_pro_account(request.user)
        if not pro_account:
            logger.warning(
                f"User {request.user.username} tried to access the dashboard without a pro account."
            )
            return redirect("become_a_pro")

        # Fetch services and rates
        services = ProAccountChecker.get_pro_services(request.user)
        rates = json.loads(pro_account.rates) if pro_account.rates else {}

        # Categorizing services for display
        categorized_services = defaultdict(list)

        # Try fetching all services and catch any potential errors
        try:
            all_services = Service.objects.all()
            for service in all_services:
                categorized_services[service.category].append(service)
        except Service.DoesNotExist:
            logger.error(
                f"Error fetching services for user {request.user.username}. No services found."
            )
            return render(
                request,
                "myapp/accounts/dashboard.html",
                {"error": "Could not load services."},
            )

        context = {
            "business_name": pro_account.business_name
            or "No business name set",
            "availability": pro_account.availability,
            "services": services,
            "rates": [
                {
                    "service_name": service.name,
                    "amount": rates.get(str(service.id), "Not set"),
                }
                for service in services
            ],
            "categorized_services": dict(categorized_services),
        }

        return render(request, "myapp/accounts/dashboard.html", context)

    except Exception as e:
        logger.error(
            f"Unexpected error occurred for user {request.user.username}: {str(e)}"
        )
        return render(
            request,
            "myapp/accounts/dashboard.html",
            {
                "error": "An unexpected error occurred. Please try again later.",
            },
        )


def update_business_name(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            business_name = data.get("business_name", None)

            # Convert empty string to None
            if business_name == "":
                business_name = None

            request.user.proaccount.business_name = business_name
            request.user.proaccount.save()

            return JsonResponse({"success": True})
        except json.JSONDecodeError as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False})


@login_required
@require_POST
def update_zip_code(request):
    """
    Update the zip code for a pro account.

    Args:
        request: The HTTP request object containing the new zip code.

    Returns:
        JsonResponse: A JSON object indicating success or failure.
    """
    try:
        pro_account = request.user.proaccount
        data = json.loads(request.body)
        zip_code = data.get("zip_code", "").strip()

        pro_account.zip_code = zip_code if zip_code else None
        pro_account.save()

        return JsonResponse({"success": True})
    except (ValidationError, json.JSONDecodeError) as error:
        logger.error("Error updating zip code: %s", str(error))
        return JsonResponse({"success": False, "error": str(error)})


@login_required
@require_POST
def update_languages(request):
    """
    Update the languages for a pro account.

    Args:
        request: The HTTP request object containing the new languages.

    Returns:
        JsonResponse: A JSON object indicating success or failure.
    """
    try:
        pro_account = request.user.proaccount
        data = json.loads(request.body)
        languages = data.get("languages", "").strip()

        pro_account.languages = languages if languages else None
        pro_account.save()

        return JsonResponse({"success": True})
    except (ValidationError, json.JSONDecodeError) as error:
        logger.error("Error updating languages: %s", str(error))
        return JsonResponse({"success": False, "error": str(error)})


@login_required
@require_POST
def update_phone_number(request):
    try:
        pro_account = request.user.proaccount
        data = json.loads(request.body)
        phone_number = data.get("phone_number", "").strip()

        # Remove hyphens from the phone number
        phone_number = phone_number.replace("-", "")

        # Perform phone number validation using regex
        phone_regex = re.compile(
            r"^\d{10}$"
        )  # Simple regex for 10 digit numbers
        if not phone_regex.match(phone_number):
            return JsonResponse(
                {"success": False, "error": "Invalid phone number"}, status=400
            )

        pro_account.phone_number = phone_number if phone_number else None
        pro_account.save()

        return JsonResponse({"success": True})
    except (ValidationError, json.JSONDecodeError) as error:
        logger.error(f"Error updating phone number: {str(error)}")
        return JsonResponse(
            {"success": False, "error": str(error)}, status=400
        )


@login_required
@require_POST
def update_business_email(request):
    """
    Update the business email for a pro account.

    Args:
        request: The HTTP request object containing the new business email.

    Returns:
        JsonResponse: A JSON object indicating success or failure.
    """
    try:
        pro_account = request.user.proaccount
        data = json.loads(request.body)
        business_email = data.get("business_email", "").strip()

        pro_account.business_email = business_email if business_email else None
        pro_account.save()

        return JsonResponse({"success": True})
    except (ValidationError, json.JSONDecodeError) as error:
        logger.error("Error updating business email: %s", str(error))
        return JsonResponse({"success": False, "error": str(error)})


@login_required
@require_POST
def update_availability(request):
    """
    Update the availability for a pro account.

    Args:
        request: The HTTP request object containing the new availability.

    Returns:
        JsonResponse: A JSON object indicating success or failure.
    """
    try:
        pro_account = request.user.proaccount
        data = json.loads(request.body)
        pro_account.availability = data.get("availability", "")
        pro_account.save()
        return JsonResponse({"success": True})
    except (ValidationError, json.JSONDecodeError) as error:
        logger.error("Error updating availability: %s", str(error))
        return JsonResponse({"success": False, "error": str(error)})


@login_required
@require_POST
def update_services(request):
    try:
        pro_account = request.user.proaccount
        data = json.loads(request.body)
        services = data.get("services", [])

        # Convert all IDs to integers
        services = [int(service_id) for service_id in services]

        logger.info(f"Received services data after conversion: {services}")

        if not isinstance(services, list):  # Check if the services are a list
            return JsonResponse(
                {"success": False, "error": "Invalid data format"}, status=400
            )

        # Validate services before updating
        valid_services = Service.objects.filter(id__in=services)
        valid_service_ids = set(valid_services.values_list("id", flat=True))
        invalid_services = set(services) - valid_service_ids

        if invalid_services:
            logger.error(f"Invalid service IDs: {list(invalid_services)}")
            return JsonResponse(
                {
                    "success": False,
                    "error": f"Invalid service IDs: {list(invalid_services)}",
                },
                status=400,
            )

        # Fetch current rates
        current_rates = json.loads(pro_account.rates) if pro_account.rates else {}

        # Remove rates for services that are no longer selected
        updated_rates = {str(service_id): current_rates.get(str(service_id), "0") 
                         for service_id in valid_service_ids}

        # Update services and save rates
        pro_account.services.set(valid_services)
        pro_account.rates = json.dumps(updated_rates)  # Save the updated rates as JSON
        pro_account.save()

        return JsonResponse({"success": True})

    except (ValidationError, json.JSONDecodeError) as error:
        logger.error(f"Error updating services: {str(error)}")
        return JsonResponse({"success": False, "error": str(error)})



@login_required
@require_POST
def upload_profile_picture_dashboard(request):
    """
    Handle the upload of a new profile picture for the user.

    Args:
        request: The HTTP request object containing the uploaded file.

    Returns:
        JsonResponse: A JSON object indicating success or failure.
    """
    if request.method == "POST":
        form = ProfilePictureForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                profile = request.user.profile
            except ObjectDoesNotExist:
                profile = UserProfile.objects.create(user=request.user)

            profile_picture = form.cleaned_data["profile_picture"]
            profile.profile_picture.save(profile_picture.name, profile_picture)

            logger.info(
                "Profile picture saved: %s", profile.profile_picture.url
            )
            return JsonResponse(
                {
                    "success": True,
                    "profile_picture_url": profile.profile_picture.url,
                }
            )
        logger.error("Form errors: %s", form.errors)
        return JsonResponse({"success": False, "errors": form.errors})

    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
@require_POST
def delete_profile_picture(request):
    """
    Delete the profile picture for the current user.

    Args:
        request: The HTTP request object.

    Returns:
        JsonResponse: A JSON object indicating success or failure.
    """
    if request.method == "POST":
        user = request.user
        user.profile.profile_picture.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)


@login_required
def get_user_profile_pic(request):
    """
    Retrieve the URL of the current user's profile picture.

    Args:
        request: The HTTP request object.

    Returns:
        JsonResponse: A JSON object containing the profile picture URL or None if not set.
    """
    try:
        profile = request.user.profile
        profile_pic_url = (
            profile.profile_picture.url if profile.profile_picture else None
        )
    except ObjectDoesNotExist:
        profile_pic_url = None

    return JsonResponse({"profile_pic_url": profile_pic_url})


@login_required
@require_POST
def update_profile_visibility(request):
    try:
        pro_account = request.user.proaccount
        data = json.loads(request.body)

        # Ensure profile_visibility is a boolean
        if "profile_visibility" in data and isinstance(
            data["profile_visibility"], bool
        ):
            pro_account.profile_visibility = data["profile_visibility"]
        else:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Invalid value for profile visibility",
                },
                status=400,
            )

        pro_account.save()
        return JsonResponse({"success": True})

    except (ValidationError, json.JSONDecodeError) as error:
        logger.error(f"Error updating profile visibility: {str(error)}")
        return JsonResponse(
            {"success": False, "error": str(error)}, status=400
        )
