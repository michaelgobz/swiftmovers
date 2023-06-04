"""
ASGI config for swiftmovers project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from .health_check import health_check

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swiftmovers.settings')

application = get_asgi_application()
application = health_check(application, "/health/")
