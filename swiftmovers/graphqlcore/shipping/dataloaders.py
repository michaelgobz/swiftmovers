from collections import defaultdict

from django.db.models import Exists, OuterRef

from ...zones.models import Zone
from ...shipping.models import (
    ShippingMethod,
    ShippingZone,
)
from ..core.dataloaders import DataLoader


class ShippingMethodByIdLoader(DataLoader):
    context_key = "shippingmethod_by_id"

    def batch_load(self, keys):
        shipping_methods = ShippingMethod.objects.using(
            self.database_connection_name
        ).in_bulk(keys)
        return [shipping_methods.get(shipping_method_id) for shipping_method_id in keys]


class ShippingZoneByIdLoader(DataLoader):
    context_key = "shippingzone_by_id"

    def batch_load(self, keys):
        shipping_zones = ShippingZone.objects.using(
            self.database_connection_name
        ).in_bulk(keys)
        return [shipping_zones.get(shipping_zone_id) for shipping_zone_id in keys]


class ShippingZonesByZoneIdLoader(DataLoader):
    context_key = "shippingzone_by_zone_id"

    def batch_load(self, keys):
        shipping_zones_zone = ShippingZone.channels.through.objects.using(
            self.database_connection_name
        ).filter(zone_id__in=keys)
        shipping_zones_map = (
            ShippingZone.objects.using(self.database_connection_name)
            .filter(
                Exists(shipping_zones_zone.filter(shippingzone_id=OuterRef("pk")))
            )
            .in_bulk()
        )

        shipping_zones_by_zone_map = defaultdict(list)
        for shipping_zone_id, zone_id in shipping_zones_zone.values_list(
            "shippingzone_id", "zone_id"
        ):
            shipping_zones_by_zone_map[zone_id].append(
                shipping_zones_map[shipping_zone_id]
            )
        return [
            shipping_zones_by_zone_map.get(zone_id, []) for zone_id in keys
        ]


class ShippingMethodsByShippingZoneIdLoader(DataLoader):
    context_key = "shippingmethod_by_shippingzone"

    def batch_load(self, keys):
        shipping_methods = ShippingMethod.objects.using(
            self.database_connection_name
        ).filter(shipping_zone_id__in=keys)
        shipping_methods_by_shipping_zone_map = defaultdict(list)
        for shipping_method in shipping_methods:
            shipping_methods_by_shipping_zone_map[
                shipping_method.shipping_zone_id
            ].append(shipping_method)
        return [
            shipping_methods_by_shipping_zone_map.get(shipping_zone_id, [])
            for shipping_zone_id in keys
        ]

class ShippingMethodsByShippingZoneIdAndZoneSlugLoader(DataLoader):
    context_key = "shippingmethod_by_shippingzone_and_zone"

    def batch_load(self, keys):
        shipping_methods = (
            ShippingMethod.objects.using(self.database_connection_name)
            .filter(shipping_zone_id__in=keys)
        )

        shipping_methods_by_shipping_zone_and_channel_map = defaultdict(list)
        for shipping_method in shipping_methods:
            key = (shipping_method.shipping_zone_id, shipping_method.channel_slug)
            shipping_methods_by_shipping_zone_and_channel_map[key].append(
                shipping_method
            )
        return [
            shipping_methods_by_shipping_zone_and_channel_map.get(key, [])
            for key in keys
        ]


class ChannelsByShippingZoneIdLoader(DataLoader):
    context_key = "zones_by_shippingzone"

    def batch_load(self, keys):
        from ..zones.dataloaders import ZoneByIdLoader

        zone_and_zone_is_pairs = (
            Zone.objects.using(self.database_connection_name)
            .filter(shipping_zones__id__in=keys)
            .values_list("pk", "shipping_zones__id")
        )
        shipping_zone_zone_map = defaultdict(list)
        for zones_id, zone_id in zone_and_zone_is_pairs:
            shipping_zone_zone_map[zone_id].append(zones_id)

        def map_zones(zones):
            zone_map = {zone.pk: zone for zone in zones}
            return [
                [
                    zone_map[zone_id_id]
                    for zone_id_id in shipping_zone_zone_map.get(zone_id, [])
                ]
                for zone_id in keys
            ]

        return (
            ZoneByIdLoader(self.context)
            .load_many({pk for pk, _ in zone_and_zone_is_pairs})
            .then(map_zones)
        )
