"""
This module contains views related to the 'Become a Pro' functionality.
It handles the process of upgrading a regular user account to a pro account.
"""

import json
import logging
from collections import defaultdict
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError, DatabaseError
from django.utils import timezone
from django.core.exceptions import ValidationError
from myapp.forms import ProAccountForm
from myapp.models import ProAccount, Service, ZipCode

logger = logging.getLogger(__name__)

# pylint: disable=no-member


@login_required
def become_a_pro(request):
    """
    Handle the 'Become a Pro' process for a logged-in user.

    This view allows a regular user to upgrade their account to a pro account.
    It handles both GET and POST requests, rendering the form and processing
    form submissions respectively.
    """
    if request.user.is_pro:
        return redirect("dashboard")

    try:
        pro_account = ProAccount.objects.get(user=request.user)
    except ProAccount.DoesNotExist:
        pro_account = None

    if request.method == "POST":
        form = ProAccountForm(request.POST, instance=pro_account)
        if form.is_valid():
            try:
                with transaction.atomic():
                    pro_account = form.save(commit=False)
                    pro_account.user = request.user
                    pro_account.become_a_pro_completed = True
                    pro_account.save()

                    _handle_services(request, pro_account)
                    _update_user_pro_status(request.user)

                    messages.success(
                        request,
                        "Pro account information saved successfully!",
                    )
                    return redirect("dashboard")
            except IntegrityError as e:
                logger.error(
                    "Database integrity error while saving pro account: %s",
                    str(e),
                )
                messages.error(
                    request,
                    "An error occurred while saving your information. Please try again.",
                )
            except ValidationError as e:
                logger.error(
                    "Validation error while saving pro account: %s", str(e)
                )
                messages.error(
                    request,
                    "Invalid data provided. Please check your information and try again.",
                )
            except DatabaseError as e:
                logger.error(
                    "Database error while saving pro account: %s", str(e)
                )
                messages.error(
                    request,
                    "A database error occurred. Please try again later.",
                )
            except json.JSONDecodeError as e:
                logger.error(
                    "JSON decode error while processing services: %s", str(e)
                )
                messages.error(
                    request,
                    "An error occurred while processing your services. Please try again.",
                )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ProAccountForm(instance=pro_account)

    context = {
        "form": form,
        "services": _get_categorized_services(),
        "pr_zip_codes": _get_pr_zip_codes(),
    }
    return render(request, "myapp/accounts/become_a_pro.html", context)


def _handle_services(request, pro_account):
    """Handle the services associated with a pro account."""
    services = json.loads(request.POST.get("services", "[]"))
    pro_account.services.clear()
    for service_name in services:
        service, _ = Service.objects.get_or_create(name=service_name)
        pro_account.services.add(service)


def _update_user_pro_status(user):
    """Update the user's pro status and timestamp."""
    user.is_pro = True
    user.pro_account_created_at = timezone.now()
    user.save()


def _get_categorized_services():
    """Fetch and categorize services from the database."""
    services = Service.objects.all()
    categorized_services = defaultdict(list)
    for service in services:
        categorized_services[service.category].append(service.name)
    return dict(categorized_services)


def _get_pr_zip_codes():
    """Fetch zip codes from the database."""
    return list(ZipCode.objects.values_list("code", flat=True))
