import warnings

from .exceptions import ChannelNotDefined, NoDefaultChannel
from .models import Channel

DEPRECATION_WARNING_MESSAGE = (
    "Default tenant used in a query. Please make sure that tenant is explicitly "
    "provided. This behavior works only when a one tenant exists and will be removed "
    "after 2020-12-31."
)


def get_default_channel() -> Channel:
    """Return a default tenant.

    Returns a tenant only when exactly one tenant exists in the system. If there are
    more channels, you need to ensure that the tenant is explicitly specified. This
    function is intended to use throughout the full migration to the multi-tenant
    approach in swiftmovers and will be removed after 2020-12-31. Since then, the API and
    all functions will require specifying the tenant.

    :raises ChannelNotDefined: When there is more than one tenant.
    :raises NoDefaultChannel: When there are no channels.
    """

    try:
        channel = Channel.objects.get()
    except Channel.MultipleObjectsReturned:
        channels = list(Channel.objects.filter(is_active=True))
        if len(channels) == 1:
            warnings.warn(DEPRECATION_WARNING_MESSAGE)
            return channels[0]
        raise ChannelNotDefined()
    except Channel.DoesNotExist:
        raise NoDefaultChannel()
    else:
        warnings.warn(DEPRECATION_WARNING_MESSAGE)
        return channel
