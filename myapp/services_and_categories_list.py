""" 
This file contains the services and 
services categories and it is used 
in views.py.
"""

# Categories for index.html and index.js
SERVICE_CATEGORIES = [
    {"category": "home_services", "icon": "home", "name": "Home Services"},
    {
        "category": "car_and_vehicle_services",
        "icon": "directions_car",
        "name": "Car & Vehicle",
    },
    {"category": "pet_services", "icon": "pets", "name": "Pet Services"},
    {
        "category": "moving_services",
        "icon": "local_shipping",
        "name": "Moving",
    },
    {
        "category": "professional_services",
        "icon": "work",
        "name": "Professional",
    },
    {"category": "events_services", "icon": "event", "name": "Events"},
]

# Services for index.html and index.js
SERVICES = {
    "home_services": [
        {"name": "Air Conditioning", "icon": "ac_unit"},
        {"name": "Babysitting", "icon": "child_care"},
        {"name": "Construction", "icon": "construction"},
        {"name": "Electrician", "icon": "electrical_services"},
        {"name": "Gardening", "icon": "grass"},
        {"name": "House Cleaning", "icon": "cleaning_services"},
        {"name": "Interior Design", "icon": "design_services"},
        {"name": "Landscaping", "icon": "landscape"},
        {"name": "Painting", "icon": "format_paint"},
        {"name": "Pest Control", "icon": "bug_report"},
        {"name": "Plumbing", "icon": "plumbing"},
        {"name": "Roofing", "icon": "roofing"},
        {"name": "Security Systems", "icon": "security"},
        {"name": "Solar Panels", "icon": "solar_power"},
        {"name": "Swimming Pools", "icon": "pool"},
    ],
    "car_and_vehicle_services": [
        {"name": "Car Towing", "icon": "directions_car"},
        {"name": "Car Wash and Detailing", "icon": "local_car_wash"},
        {"name": "Mechanics", "icon": "engineering"},
    ],
    "pet_services": [
        {"name": "Pet Boarding", "icon": "pets"},
        {"name": "Pet Grooming", "icon": "cut"},
        {"name": "Pet Training", "icon": "pets"},
    ],
    "moving_services": [
        {"name": "Moving", "icon": "local_shipping"},
        {"name": "Storage", "icon": "storage"},
    ],
    "professional_services": [
        {"name": "Accounting", "icon": "account_balance"},
        {"name": "Legal Services", "icon": "gavel"},
        {"name": "Consulting", "icon": "support_agent"},
    ],
    "events_services": [
        {"name": "Event Planning", "icon": "event"},
        {"name": "Catering", "icon": "restaurant"},
        {"name": "Entertainment", "icon": "mic"},
    ],
}
