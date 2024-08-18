"""
This module contains view functions for the dashboard of a pro account user.

It includes functions for rendering the dashboard, updating various account details,
and managing profile pictures.
"""

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
    pro_account = ProAccountChecker.get_pro_account(request.user)
    if not pro_account:
        return redirect("become_a_pro")

    services = ProAccountChecker.get_pro_services(request.user)
    rates = json.loads(pro_account.rates) if pro_account.rates else {}

    # Categorizing services for display
    categorized_services = defaultdict(list)
    for service in Service.objects.all():
        categorized_services[service.category].append(service)

    context = {
        "business_name": pro_account.business_name or "No business name set",
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
    """
    Update the phone number for a pro account.

    Args:
        request: The HTTP request object containing the new phone number.

    Returns:
        JsonResponse: A JSON object indicating success or failure.
    """
    try:
        pro_account = request.user.proaccount
        data = json.loads(request.body)
        phone_number = data.get("phone_number", "").strip()

        pro_account.phone_number = phone_number if phone_number else None
        pro_account.save()

        return JsonResponse({"success": True})
    except (ValidationError, json.JSONDecodeError) as error:
        logger.error("Error updating phone number: %s", str(error))
        return JsonResponse({"success": False, "error": str(error)})


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
        
        # Rest of the function...
        
        if not isinstance(services, list):  # Check if the services are a list
            return JsonResponse({"success": False, "error": "Invalid data format"}, status=400)

        # Validate services before updating
        valid_services = Service.objects.filter(id__in=services)
        valid_service_ids = set(valid_services.values_list("id", flat=True))
        invalid_services = set(services) - valid_service_ids

        if invalid_services:
            logger.error(f"Invalid service IDs: {list(invalid_services)}")
            return JsonResponse(
                {"success": False, "error": f"Invalid service IDs: {list(invalid_services)}"},
                status=400,
            )

        # Update services and save to pro account
        pro_account.services.set(valid_services)
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
    """
    Update the profile visibility setting for a pro account.

    Args:
        request: The HTTP request object containing the new profile visibility setting.

    Returns:
        JsonResponse: A JSON object indicating success or failure.
    """
    try:
        pro_account = request.user.proaccount
        data = json.loads(request.body)

        if "profile_visibility" in data:
            pro_account.profile_visibility = data["profile_visibility"]
        pro_account.save()

        return JsonResponse({"success": True})
    except (ValidationError, json.JSONDecodeError) as error:
        logger.error("Error updating profile visibility: %s", str(error))
        return JsonResponse({"success": False, "error": str(error)})
