from django.contrib.sites.models import Site
from django.contrib.staticfiles.storage import staticfiles_storage

from ..utils import build_absolute_uri

LOGO_URL = "images/swiftmovers-logo-sign.png"


def get_site_context():
    site: Site = Site.objects.get_current()
    site_context = {
        "domain": site.domain,
        "site_name": site.name,
        "logo_url": build_absolute_uri(staticfiles_storage.url(LOGO_URL)),
    }
    return site_context
