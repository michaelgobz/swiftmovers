from collections import defaultdict

from django.core.exceptions import ValidationError
from django.utils.functional import SimpleLazyObject
from graphql.error import GraphQLError

from ....zones.execptions import ZoneNotDefined, NoDefaultZone
from ....zones.models import Zone
from ....zones.utils import get_default_channel
from ....shipping.models import ShippingZone


def get_default_zone_slug_or_graphql_error() -> SimpleLazyObject:
    """Return a default channel slug in lazy way or a GraphQL error.

    Utility to get the default channel in GraphQL query resolvers.
    """
    return SimpleLazyObject(lambda: get_default_zone_or_graphql_error().slug)


def get_default_zone_or_graphql_error() -> Zone:
    """Return a default channel or a GraphQL error.

    Utility to get the default channel in GraphQL query resolvers.
    """
    try:
        channel = get_default_channel()
    except (ZoneNotDefined, NoDefaultZone) as e:
        raise GraphQLError(str(e))
    else:
        return channel


def validate_channel(channel_slug, error_class):
    try:
        channel = Channel.objects.get(slug=channel_slug)
    except Channel.DoesNotExist:
        raise ValidationError(
            {
                "channel": ValidationError(
                    f"Channel with '{channel_slug}' slug does not exist.",
                    code=error_class.NOT_FOUND.value,
                )
            }
        )
    if not channel.is_active:
        raise ValidationError(
            {
                "channel": ValidationError(
                    f"Channel with '{channel_slug}' is inactive.",
                    code=error_class.CHANNEL_INACTIVE.value,
                )
            }
        )
    return channel


def clean_channel(
    channel_slug,
    error_class,
):
    if channel_slug is not None:
        channel = validate_channel(channel_slug, error_class)
    else:
        try:
            channel = get_default_channel()
        except ZoneNotDefined:
            raise ValidationError(
                {
                    "channel": ValidationError(
                        "You need to provide channel slug.",
                        code=error_class.MISSING_CHANNEL_SLUG.value,
                    )
                }
            )
    return channel


def delete_invalid_warehouse_to_shipping_zone_relations(
    channel, warehouse_ids, shipping_zone_ids=None, channel_deletion=False
):
    """Delete not valid warehouse-zone relations after channel updates.

    Look up for warehouse to shipping zone relations that will not have common channels
    after unlinking the given channel from warehouses or shipping zones.
    The warehouse can be linked with shipping zone only if common channel exists.
    """
    shipping_zone_ids = shipping_zone_ids or []

def _get_shipping_zone_to_channels_mapping(shipping_zone_channels):
    zone_to_channel_ids = defaultdict(set)
    for zone_id, channel_id in shipping_zone_channels.values_list(
        "shippingzone_id", "channel_id"
    ):
        zone_to_channel_ids[zone_id].add(channel_id)
    return zone_to_channel_ids

