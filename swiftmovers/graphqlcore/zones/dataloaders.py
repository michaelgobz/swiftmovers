from django.db.models import Exists, OuterRef

from swiftmovers.zones import Zone
from ...orders.models import Order
from ..checkouts.dataloaders import CheckoutByTokenLoader, CheckoutLineByIdLoader
from ..core.dataloaders import DataLoader
from ..orders.dataloaders.orders import OrderByIdLoader, OrderLineByIdLoader


class ZoneByIdLoader(DataLoader):
    context_key = "zone_by_id"

    def batch_load(self, keys):
        zones  = Zone.objects.using(self.database_connection_name).in_bulk(keys)
        return [zones.get(zone_id) for zone_id in keys]


class ZoneBySlugLoader(DataLoader):
    context_key = "zone_by_slug"

    def batch_load(self, keys):
        zones = Zone.objects.using(self.database_connection_name).in_bulk(
            keys, field_name="slug"
        )
        return [zones.get(slug) for slug in keys]


class ZoneByCheckoutLineIDLoader(DataLoader):
    context_key = "channel_by_checkout_line"

    def batch_load(self, keys):
        def zone_by_lines(checkout_lines):
            checkout_ids = [line.checkout_id for line in checkout_lines]

            def zones_by_checkout(checkouts):
                zones_ids = [checkout.zone_id for checkout in checkouts] #TODO: add the zone id

                return ZoneByIdLoader(self.context).load_many(zones_ids)

            return (
                CheckoutByTokenLoader(self.context)
                .load_many(checkout_ids)
                .then(zones_by_checkout)
            )

        return (
            CheckoutLineByIdLoader(self.context).load_many(keys).then(zone_by_lines)
        )


class ChannelByOrderLineIdLoader(DataLoader):
    context_key = "channel_by_orderline"

    def batch_load(self, keys):
        def zones_by_lines(order_lines):
            order_ids = [line.order_id for line in order_lines]

            def zones_by_checkout(orders):
                zones_ids = [order.channel_id for order in orders]

                return ZoneByIdLoader(self.context).load_many(zones_ids)

            return (
                OrderByIdLoader(self.context)
                .load_many(order_ids)
                .then(zones_by_checkout)
            )

        return OrderLineByIdLoader(self.context).load_many(keys).then(zones_by_lines)


class ZoneWithHasOrdersByIdLoader(DataLoader):
    context_key = "zone_with_has_orders_by_id"

    def batch_load(self, keys):
        orders = Order.objects.using(self.database_connection_name).filter(
            channel=OuterRef("pk")
        )
        zones = (
            Zone.objects.using(self.database_connection_name)
            .annotate(has_orders=Exists(orders))
            .in_bulk(keys)
        )
        return [zones.get(zone_id) for zone_id in keys]
