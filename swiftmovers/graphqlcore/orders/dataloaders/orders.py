from collections import defaultdict

from django.db.models import F

from ....orders.models import Order, OrderLine
from ....payments.models import TransactionItem
from ...core.dataloaders import DataLoader


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
