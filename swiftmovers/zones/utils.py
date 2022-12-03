import warnings
from ..zones.execptions import ZoneNotDefined, NoDefaultZone
from .models import Zone


def get_default_channel() -> Zone:
    """Return a default Zone
    """

    try:
        channel = Zone.get()
    except Zone.MultipleObjectsReturned:
        zones = list(Zone.objects.filter(is_active=True))
        if len(zones) == 1:

            return zones[0]
        raise ZoneNotDefined()
    except Zone.DoesNotExist:
        raise NoDefaultZone()
    else:
        return channel
