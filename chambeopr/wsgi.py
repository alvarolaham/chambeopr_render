"""
WSGI config for chambeopr project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chambeopr.settings")

application = get_wsgi_application()

# Only add signal handling in production
if (
    "RUN_MAIN" not in os.environ
):  # This is a simple check to see if we're not in the dev server
    import signal

    def handle_signal(signal_number, frame):
        # Perform cleanup, like closing database connections
        print("Shutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
