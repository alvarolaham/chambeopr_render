import json
import logging
from django.core.files.storage import FileSystemStorage, default_storage
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.views.decorators.http import require_POST
from .models import ProAccount, UserProfile

from .services_and_categories_list import SERVICE_CATEGORIES, SERVICES


logger = logging.getLogger(__name__)

# Define a temporary storage location
temp_storage = FileSystemStorage(location="temp/")



def index(request):
    # Fetch service categories and services for the main page
    service_categories = SERVICE_CATEGORIES
    services = SERVICES

    # Fetch all ProAccount data along with related fields (business name, location, services, languages, rates)
    pro_accounts = ProAccount.objects.all().select_related('user')

    # Fetch associated UserProfile data to get profile pictures and map them to the pro_accounts
    user_profiles = UserProfile.objects.select_related('user')

    # Add profile picture URLs and starting rate for each pro account
    for pro in pro_accounts:
        # Attach profile picture if available
        user_profile = user_profiles.filter(user=pro.user).first()
        pro.profile_picture_url = user_profile.profile_picture.url if user_profile and user_profile.profile_picture else None

        # Convert rates string (if JSON format) to a dictionary and extract the first rate
        try:
            rates_dict = json.loads(pro.rates) if isinstance(pro.rates, str) else pro.rates
            if rates_dict and isinstance(rates_dict, dict):
                # Get the first key-value pair and set starting_rate to its value
                first_rate = list(rates_dict.values())[-1]
                print("first rate is", end="")
                print(first_rate)
                pro.starting_rate = float(first_rate) if first_rate else 0.0
            else:
                pro.starting_rate = 0.0
        except (ValueError, TypeError, json.JSONDecodeError):
            pro.starting_rate = 0.0

        # Split languages by comma if it's a string
        if isinstance(pro.languages, str):
            pro.languages = pro.languages.split(',')

    context = {
        "service_categories": service_categories,
        "services": services,
        "pro_accounts": pro_accounts  # Pass pro_accounts with profile pictures and rates
    }

    # Render the index page with all the context
    return render(request, "myapp/index.html", context)


def home_services(request):
    services = SERVICES["home_services"]
    services.sort(
        key=lambda service: service["name"]
    )  # Sort by the 'name' key
    category_name = "Home Services"  # Set the category name here
    return render(
        request,
        "myapp/services/home_services.html",
        {
            "services": services,
            "category_name": category_name,  # Pass the category name to the template
        },
    )


def car_and_vehicle_services(request):
    services = SERVICES["car_and_vehicle_services"]
    services.sort(key=lambda service: service["name"])
    category_name = "Car & Vehicle Services"  # Set the category name here
    return render(
        request,
        "myapp/services/car_and_vehicle_services.html",
        {
            "services": services,
            "category_name": category_name,  # Pass the category name to the template
        },
    )


def pet_services(request):
    services = SERVICES["pet_services"]
    services.sort(key=lambda service: service["name"])
    category_name = "Pet Services"  # Set the category name here
    return render(
        request,
        "myapp/services/pet_services.html",
        {
            "services": services,
            "category_name": category_name,  # Pass the category name to the template
        },
    )


def moving_services(request):
    services = SERVICES["moving_services"]
    services.sort(key=lambda service: service["name"])
    category_name = "Moving Services"  # Set the category name here
    return render(
        request,
        "myapp/services/moving_services.html",
        {
            "services": services,
            "category_name": category_name,  # Pass the category name to the template
        },
    )


def professional_services(request):
    services = SERVICES["professional_services"]
    services.sort(key=lambda service: service["name"])
    category_name = "Professional Services"  # Set the category name here
    return render(
        request,
        "myapp/services/professional_services.html",
        {
            "services": services,
            "category_name": category_name,  # Pass the category name to the template
        },
    )


def events_services(request):
    services = SERVICES["events_services"]
    services.sort(key=lambda service: service["name"])
    category_name = "Events Services"  # Set the category name here
    return render(
        request,
        "myapp/services/events_services.html",
        {
            "services": services,
            "category_name": category_name,  # Pass the category name to the template
        },
    )


def search_services(request):
    query = request.GET.get("q", "").lower()

    filtered_services = {
        category: [
            service for service in services if query in service["name"].lower()
        ]
        for category, services in SERVICES.items()
    }

    # Remove categories with no matching services
    filtered_services = {k: v for k, v in filtered_services.items() if v}

    return JsonResponse({"filtered_services": filtered_services})




@login_required
@require_POST
def save_rates(request):
    try:
        pro_account = request.user.proaccount
        rates = json.loads(request.body)

        # Ensure rates is a dictionary
        if not isinstance(rates, dict):
            return JsonResponse(
                {"success": False, "error": "Invalid rates data"}
            )

        pro_account.rates = json.dumps(rates)  # Store as JSON string
        pro_account.save()

        return JsonResponse({"success": True})
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON data"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


