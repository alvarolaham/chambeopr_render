"""
This script populates the ZipCode model in the database with predefined
zip codes for Puerto Rico. It updates existing zip codes, creates new ones,
and deletes any zip codes not in the predefined set.
"""

import os

import django
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError, transaction
from termcolor import colored

# Set up Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chambeopr.settings")
django.setup()

from myapp.models import ZipCode

PR_ZIP_CODES = {
    "Adjuntas": ["00601"],
    "P.O. Boxes Adjuntas": ["00631"],
    "Aguada": ["00602"],
    "Aguadilla": ["00603"],
    "Ramey Station": ["00604"],
    "P.O. Boxes Aguadilla": ["00605"],
    "San Antonio": ["00690"],
    "Aguas Buenas": ["00703"],
    "Aibonito": ["00705"],
    "La Plata": ["00786"],
    "Añasco": ["00610"],
    "Angeles": ["00611"],
    "Arecibo": ["00612", "00613", "00614"],
    "Bajadero": ["00616"],
    "Garrochales": ["00652"],
    "Sabana Hoyos": ["00688"],
    "Arroyo": ["00714"],
    "Barceloneta": ["00617"],
    "Barranquitas": ["00794"],
    "Bayamón": ["00956", "00957", "00959", "00961"],
    "Brach P.O. Boxes": ["00960"],
    "Gardens P.O. Boxes": ["00958"],
    "Cabo Rojo": ["00623"],
    "Boquerón": ["00622"],
    "Caguas": ["00725", "00727", "00726"],
    "Camuy": ["00627"],
    "Canóvanas": ["00729", "00745"],
    "Carolina": [
        "00979",
        "00982",
        "00983",
        "00985",
        "00987",
        "00981",
        "00984",
        "00986",
        "00988",
    ],
    "Cataño": ["00962", "00963"],
    "Cayey": ["00736", "00737"],
    "Ceiba": ["00735", "00742"],
    "Ciales": ["00638"],
    "Cidra": ["00739"],
    "Coamo": ["00769"],
    "Comerio": ["00782"],
    "Corozal": ["00783"],
    "Culebra": ["00775"],
    "Dorado": ["00646"],
    "Fajardo": ["00738", "00740"],
    "Florida": ["00650"],
    "Guánica": ["00653"],
    "Ensenada": ["00647"],
    "Guayama": ["00784", "00704", "00785"],
    "Guayanilla": ["00656"],
    "Guaynabo": ["00965", "00966", "00968", "00969", "00971", "00970"],
    "Gurabo": ["00778"],
    "Hatillo": ["00659"],
    "Hormigueros": ["00660"],
    "Humacao": ["00791", "00792", "00741"],
    "Isabela": ["00662"],
    "Jayuya": ["00664"],
    "Juana Díaz": ["00795"],
    "Juncos": ["00777"],
    "Lajas": ["00667"],
    "Lares": ["00669", "00631"],
    "Las Marías": ["00670"],
    "Las Piedras": ["00771"],
    "Loíza": ["00772"],
    "Luquillo": ["00773"],
    "Manatí": ["00674"],
    "Maricao": ["00606"],
    "Maunabo": ["00707"],
    "Mayagüez": ["00680", "00682", "00681"],
    "Moca": ["00676"],
    "Morovis": ["00687"],
    "Naguabo": ["00718", "00744"],
    "Naranjito": ["00719"],
    "Orocovis": ["00720"],
    "Patillas": ["00723"],
    "Peñuelas": ["00624"],
    "Ponce": [
        "00716",
        "00717",
        "00728",
        "00730",
        "00731",
        "00733",
        "00780",
        "00715",
        "00732",
        "00734",
    ],
    "Quebradillas": ["00678"],
    "Rincón": ["00677"],
    "Río Grande": ["00721", "00745"],
    "Palmer": ["00721"],
    "Sabana Grande": ["00637"],
    "Salinas": ["00751"],
    "San Germán": ["00683", "00636"],
    "San Juan": [
        "00921",
        "00923",
        "00924",
        "00929",
        "00915",
        "00916",
        "00920",
        "00909",
        "00910",
        "00934",
        "00936",
        "00917",
        "00919",
        "00911",
        "00912",
        "00913",
        "00914",
        "00940",
        "00901",
        "00902",
        "00906",
        "00925",
        "00926",
        "00927",
        "00928",
        "00930",
        "00907",
        "00908",
        "00931",
        "00933",
    ],
    "San Lorenzo": ["00754"],
    "San Sebastián": ["00685"],
    "Santa Isabel": ["00757"],
    "Toa Alta": ["00953", "00954"],
    "Toa Baja": ["00949", "00950", "00951"],
    "Sabana Seca": ["00952"],
    "Trujillo Alto": ["00976", "00977"],
    "Saint Just": ["00978"],
    "Utuado": ["00641", "00611"],
    "Vega Alta": ["00692"],
    "Vega Baja": ["00693", "00694"],
    "Vieques": ["00765"],
    "Villalba": ["00766"],
    "Yabucoa": ["00767"],
    "Yauco": ["00698"],
}

# Flatten the PR_ZIP_CODES dictionary to easily check for existing zip codes
desired_zipcodes = [
    zip_code for zip_codes in PR_ZIP_CODES.values() for zip_code in zip_codes
]

# Start a transaction
try:
    with transaction.atomic():
        # Fetch current zip codes from the database
        current_zipcodes = ZipCode.objects.all()
        current_zipcode_codes = set(
            current_zipcodes.values_list("code", flat=True)
        )
        desired_zipcode_codes = set(desired_zipcodes)

        # Identify zip codes to delete
        zipcodes_to_delete = current_zipcode_codes - desired_zipcode_codes

        # Delete zip codes that are not in the desired_zipcodes list
        ZipCode.objects.filter(code__in=zipcodes_to_delete).delete()
        for zip_code in zipcodes_to_delete:
            print(colored(f"Deleted zip code: {zip_code}", "red"))

        # Update or create zip codes as per the PR_ZIP_CODES list
        for zip_code in desired_zipcode_codes:
            obj, created = ZipCode.objects.update_or_create(code=zip_code)
            if created:
                print(
                    colored(
                        f"Successfully created zip code: {zip_code}", "green"
                    )
                )
            else:
                print(
                    colored(
                        f"Successfully updated zip code: {zip_code}", "yellow"
                    )
                )

except ObjectDoesNotExist as e:
    print(colored(f"Zip code not found: {e}", "red"))
except IntegrityError as e:
    print(colored(f"Integrity error: {e}", "red"))
except ValidationError as e:
    print(colored(f"Validation error: {e}", "red"))
except django.core.exceptions.Error as e:
    print(colored(f"Django error: {e}", "red"))
except Exception as e:
    print(colored(f"An unexpected error occurred: {e}", "red"))
