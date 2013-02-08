"""
Application settings.
"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

SERSOL_KEY = getattr(settings, 'SERSOL_KEY', None)
if not SERSOL_KEY:
    raise ImproperlyConfigured("Default 360Link key required. Place SERSOL_KEY in settings.py")

PERMALINK_PREFIX = getattr(settings, 'RESOLVER_PERMALINK_PREFIX', 'ea')