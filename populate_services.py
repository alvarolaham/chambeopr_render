import os
import django
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chambeopr.settings")
django.setup()

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError, transaction
from termcolor import colored
from myapp.models import Service

SERVICES = {
    "home_services": [
        "Air Conditioning",
        "Babysitting",
        "Construction",
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
        "Solar Panels",
        "Swimming Pools",
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

# Flatten the SERVICES dictionary to easily check for existing services
desired_services = {
    service: category
    for category, services in SERVICES.items()
    for service in services
}

# Start a transaction
try:
    with transaction.atomic():
        # Fetch current services from the database
        current_services = Service.objects.all()
        current_service_names = set(
            current_services.values_list("name", flat=True)
        )
        desired_service_names = set(desired_services.keys())

        # Identify services to delete
        services_to_delete = current_service_names - desired_service_names

        # Delete services that are not in the desired_services dictionary
        Service.objects.filter(name__in=services_to_delete).delete()
        for service in services_to_delete:
            print(colored(f"Deleted service: {service}", "red"))

        # Update or create services as per the SERVICES dictionary
        for service, category in desired_services.items():
            obj, created = Service.objects.update_or_create(
                name=service, defaults={"category": category}
            )
            if created:
                print(
                    colored(
                        f"Successfully created service: {service} "
                        f"in category: {category}",
                        "green",
                    )
                )
            else:
                print(
                    colored(
                        f"Successfully updated service: {service} "
                        f"in category: {category}",
                        "yellow",
                    )
                )
except ObjectDoesNotExist as e:
    print(colored(f"Service not found: {e}", "red"))
except IntegrityError as e:
    print(colored(f"Integrity error: {e}", "red"))
except ValidationError as e:
    print(colored(f"Validation error: {e}", "red"))
except django.core.exceptions.Error as e:
    print(colored(f"Django error: {e}", "red"))
except Exception as e:
    print(colored(f"An unexpected error occurred: {e}", "red"))
