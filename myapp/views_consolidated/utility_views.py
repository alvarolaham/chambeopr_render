# utility_views.py

import json
import logging
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from PIL import Image
from io import BytesIO
from myapp.models import ProAccount, MyUser
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)


@login_required
def get_services(request):
    pro_account = request.user.proaccount
    services = pro_account.services.all().values("id", "name")
    return JsonResponse(list(services), safe=False)


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


def resize_and_save_image(profile_picture):
    temp_storage = FileSystemStorage(location="temp/")
    try:
        if profile_picture.size > 2 * 1024 * 1024:  # 2MB
            logger.info("Image size is greater than 2MB, resizing...")

            # Resize the image
            image = Image.open(profile_picture)
            image = image.convert("RGB")
            output = BytesIO()
            image.thumbnail(
                (1024, 1024)
            )  # Resize while maintaining aspect ratio
            image.save(
                output, format="JPEG", quality=85
            )  # Save resized image to BytesIO
            output.seek(0)

            # Save resized image to temporary storage
            temp_file = ContentFile(output.read(), name=profile_picture.name)
            temp_file_path = temp_storage.save(
                f"temp/{profile_picture.name}", temp_file
            )
        else:
            logger.info("Image size is within limit, saving directly...")
            temp_file_path = temp_storage.save(
                f"temp/{profile_picture.name}", profile_picture
            )
        return temp_file_path
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return None


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


class ProAccountChecker:
    @staticmethod
    def get_pro_account(user):
        try:
            return user.proaccount
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_pro_services(user):
        pro_account = ProAccountChecker.get_pro_account(user)
        if pro_account:
            services = pro_account.services.all()
            logger.info(f"Services for {user.username}: {services}")  # Log the services being returned
            return services
        logger.warning(f"No ProAccount found for user {user.username}")
        return None

