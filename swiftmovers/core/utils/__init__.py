import socket
from typing import Optional
from django.utils.encoding import iri_to_uri
from urllib.parse import urljoin
from django.conf import settings
from django.contrib.sites.models import Site


def build_absolute_uri(location: str) -> Optional[str]:
    """Create absolute uri from location.

    If provided location is absolute uri by itself, it returns unchanged value,
    otherwise if provided location is relative, absolute uri is built and returned.
    """
    host = Site.objects.get_current().domain
    protocol = "https" if settings.ENABLE_SSL else "http"
    current_uri = "%s://%s" % (protocol, host)
    location = urljoin(current_uri, location)
    return iri_to_uri(location)


def is_valid_ipv4(ip: str) -> bool:
    """Check whether the passed IP is a valid V4 IP address."""
    try:
        socket.inet_pton(socket.AF_INET, ip)
    except socket.error:
        return False
    return True


def is_valid_ipv6(ip: str) -> bool:
    """Check whether the passed IP is a valid V6 IP address."""
    try:
        socket.inet_pton(socket.AF_INET6, ip)
    except socket.error:
        return False
    return True
