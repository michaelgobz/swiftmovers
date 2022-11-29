from collections import defaultdict

from django.db.models import F

from ....orders.models import Order, OrderLine
from ....payments.models import TransactionItem
from ...core.dataloaders import DataLoader


class OrderLinesByVariantIdAndChannelIdLoader(DataLoader):
    context_key = "orderliness_by_variant_and_channel"

    def batch_load(self, keys):
        channel_ids = [key[1] for key in keys]
        variant_ids = [key[0] for key in keys]
        order_lines = (
            OrderLine.objects.using(self.database_connection_name)
            .filter(order__channel_id__in=channel_ids, variant_id__in=variant_ids)
            .annotate(channel_id=F("order__channel_id"))
        )

        order_line_by_variant_and_channel_map = defaultdict(list)
        for order_line in order_lines:
            key = (order_line.variant_id, order_line.channel_id)
            order_line_by_variant_and_channel_map[key].append(order_line)
        return [order_line_by_variant_and_channel_map[key] for key in keys]


class OrderByIdLoader(DataLoader):
    context_key = "order_by_id"

    def batch_load(self, keys):
        orders = Order.objects.using(self.database_connection_name).in_bulk(keys)
        return [orders.get(order_id) for order_id in keys]


class OrdersByUserLoader(DataLoader):
    context_key = "order_by_user"

    def batch_load(self, keys):
        orders = Order.objects.using(self.database_connection_name).filter(
            user_id__in=keys
        )
        orders_by_user_map = defaultdict(list)
        for order in orders:
            orders_by_user_map[order.user_id].append(order)
        return [orders_by_user_map.get(user_id, []) for user_id in keys]


class OrderLineByIdLoader(DataLoader):
    context_key = "orderline_by_id"

    def batch_load(self, keys):
        order_lines = OrderLine.objects.using(self.database_connection_name).in_bulk(
            keys
        )
        return [order_lines.get(line_id) for line_id in keys]


class OrderLinesByOrderIdLoader(DataLoader):
    context_key = "orderlines_by_order"

    def batch_load(self, keys):
        lines = (
            OrderLine.objects.using(self.database_connection_name)
            .filter(order_id__in=keys)
            .order_by("created_at")
        )
        line_map = defaultdict(list)
        for line in lines.iterator():
            line_map[line.order_id].append(line)
        return [line_map.get(order_id, []) for order_id in keys]


class TransactionItemsByOrderIDLoader(DataLoader):
    context_key = "transaction_items_by_order_id"

    def batch_load(self, keys):
        transactions = (
            TransactionItem.objects.using(self.database_connection_name)
            .filter(order_id__in=keys)
            .order_by("pk")
        )
        transactions_map = defaultdict(list)
        for transaction in transactions:
            transactions_map[transaction.order_id].append(transaction)
        return [transactions_map.get(order_id, []) for order_id in keys]
