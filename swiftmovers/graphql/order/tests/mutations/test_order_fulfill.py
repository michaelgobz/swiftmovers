from unittest.mock import ANY, patch

import graphene
import pytest

from .....core.exceptions import InsufficientStock, InsufficientStockData
from .....giftcard import GiftCardEvents
from .....giftcard.models import GiftCard, GiftCardEvent
from .....order import FulfillmentStatus, OrderStatus
from .....order.error_codes import OrderErrorCode
from .....order.models import Fulfillment, FulfillmentLine
from .....product.models import ProductVariant
from .....tests.utils import flush_post_commit_hooks
from .....warehouse.models import Allocation, Stock
from ....tests.utils import get_graphql_content

ORDER_FULFILL_QUERY = """
    mutation fulfillOrder(
        $order: ID, $input: OrderFulfillInput!
    ) {
        orderFulfill(
            order: $order,
            input: $input
        ) {
            errors {
                field
                code
                message
                warehouse
                orderLines
            }
        }
    }
"""


@patch("swiftmovers.plugins.manager.PluginsManager.product_variant_out_of_stock")
def test_order_fulfill_with_out_of_stock_webhook(
    product_variant_out_of_stock_webhooks,
    staff_api_client,
    order_with_lines,
    permission_manage_orders,
    warehouse,
):
    order = order_with_lines

    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order.id)
    _, order_line2 = order.lines.all()
    order_line2_id = graphene.Node.to_global_id("OrderLine", order_line2.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    variables = {
        "order": order_id,
        "input": {
            "notifyCustomer": True,
            "lines": [
                {
                    "orderLineId": order_line2_id,
                    "stocks": [{"quantity": 2, "warehouse": warehouse_id}],
                },
            ],
        },
    }
    staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )

    stock = order_line2.variant.stocks.filter(warehouse=warehouse).first()
    product_variant_out_of_stock_webhooks.assert_called_once_with(stock)


@pytest.mark.parametrize("fulfillment_auto_approve", [True, False])
@patch("swiftmovers.graphql.order.mutations.order_fulfill.create_fulfillments")
def test_order_fulfill(
    mock_create_fulfillments,
    fulfillment_auto_approve,
    staff_api_client,
    staff_user,
    order_with_lines,
    permission_manage_orders,
    warehouse,
    site_settings,
):
    site_settings.fulfillment_auto_approve = fulfillment_auto_approve
    site_settings.save(update_fields=["fulfillment_auto_approve"])
    order = order_with_lines
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line, order_line2 = order.lines.all()
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    order_line2_id = graphene.Node.to_global_id("OrderLine", order_line2.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    variables = {
        "order": order_id,
        "input": {
            "notifyCustomer": True,
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": 3, "warehouse": warehouse_id}],
                },
                {
                    "orderLineId": order_line2_id,
                    "stocks": [{"quantity": 2, "warehouse": warehouse_id}],
                },
            ],
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert not data["errors"]

    fulfillment_lines_for_warehouses = {
        warehouse.pk: [
            {"order_line": order_line, "quantity": 3},
            {"order_line": order_line2, "quantity": 2},
        ]
    }
    mock_create_fulfillments.assert_called_once_with(
        staff_user,
        None,
        order,
        fulfillment_lines_for_warehouses,
        ANY,
        site_settings,
        True,
        allow_stock_to_be_exceeded=False,
        approved=fulfillment_auto_approve,
        tracking_number="",
    )


@pytest.mark.parametrize("fulfillment_auto_approve", [True, False])
@patch("swiftmovers.graphql.order.mutations.order_fulfill.create_fulfillments")
def test_order_fulfill_with_tracking_number(
    mock_create_fulfillments,
    fulfillment_auto_approve,
    staff_api_client,
    staff_user,
    order_with_lines,
    permission_manage_orders,
    warehouse,
    site_settings,
):
    site_settings.fulfillment_auto_approve = fulfillment_auto_approve
    site_settings.save(update_fields=["fulfillment_auto_approve"])
    order = order_with_lines
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line, order_line2 = order.lines.all()
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    order_line2_id = graphene.Node.to_global_id("OrderLine", order_line2.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    variables = {
        "order": order_id,
        "input": {
            "notifyCustomer": True,
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": 3, "warehouse": warehouse_id}],
                },
                {
                    "orderLineId": order_line2_id,
                    "stocks": [{"quantity": 2, "warehouse": warehouse_id}],
                },
            ],
            "trackingNumber": "test_tracking_number",
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert not data["errors"]

    fulfillment_lines_for_warehouses = {
        warehouse.pk: [
            {"order_line": order_line, "quantity": 3},
            {"order_line": order_line2, "quantity": 2},
        ]
    }
    mock_create_fulfillments.assert_called_once_with(
        staff_user,
        None,
        order,
        fulfillment_lines_for_warehouses,
        ANY,
        site_settings,
        True,
        allow_stock_to_be_exceeded=False,
        approved=fulfillment_auto_approve,
        tracking_number="test_tracking_number",
    )


def test_order_fulfill_with_stock_exceeded_with_flag_disabled(
    staff_api_client,
    staff_user,
    order_with_lines,
    permission_manage_orders,
    warehouse,
):
    order = order_with_lines
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line, order_line2 = order.lines.all()
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    order_line2_id = graphene.Node.to_global_id("OrderLine", order_line2.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)

    # set stocks to out of quantity and assert
    Stock.objects.filter(warehouse=warehouse).update(quantity=0)

    # make first stock quantity < 0
    stock = Stock.objects.filter(warehouse=warehouse).first()
    stock.quantity = -99
    stock.save()

    for stock in Stock.objects.filter(warehouse=warehouse):
        assert stock.quantity <= 0

    variables = {
        "order": order_id,
        "input": {
            "notifyCustomer": False,
            "allowStockToBeExceeded": False,
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": 3, "warehouse": warehouse_id}],
                },
                {
                    "orderLineId": order_line2_id,
                    "stocks": [{"quantity": 2, "warehouse": warehouse_id}],
                },
            ],
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert data["errors"]

    errors = data["errors"]
    assert errors[0]["code"] == "INSUFFICIENT_STOCK"
    assert errors[0]["message"] == "Insufficient product stock."
    assert errors[1]["orderLines"] == [order_line2_id]

    assert errors[1]["code"] == "INSUFFICIENT_STOCK"
    assert errors[1]["message"] == "Insufficient product stock."
    assert errors[1]["orderLines"] == [order_line2_id]


def test_order_fulfill_with_stock_exceeded_with_flag_enabled(
    staff_api_client,
    staff_user,
    order_with_lines,
    permission_manage_orders,
    warehouse,
):
    order = order_with_lines
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line, order_line2 = order.lines.all()
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    order_line2_id = graphene.Node.to_global_id("OrderLine", order_line2.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)

    # set stocks to out of quantity and assert
    Stock.objects.filter(warehouse=warehouse).update(quantity=0)
    for stock in Stock.objects.filter(warehouse=warehouse):
        assert stock.quantity == 0

    variables = {
        "order": order_id,
        "input": {
            "notifyCustomer": False,
            "allowStockToBeExceeded": True,
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": 3, "warehouse": warehouse_id}],
                },
                {
                    "orderLineId": order_line2_id,
                    "stocks": [{"quantity": 2, "warehouse": warehouse_id}],
                },
            ],
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert not data["errors"]

    order.refresh_from_db()

    assert order.status == OrderStatus.FULFILLED

    order_lines = order.lines.all()
    assert order_lines[0].quantity_fulfilled == 3
    assert order_lines[0].quantity_unfulfilled == 0

    assert order_lines[1].quantity_fulfilled == 2
    assert order_lines[1].quantity_unfulfilled == 0

    # check if stocks quantity are < 0 after fulfillments
    for stock in Stock.objects.filter(warehouse=warehouse):
        assert stock.quantity < 0


def test_order_fulfill_with_allow_stock_to_be_exceeded_flag_enabled_and_deleted_stocks(
    staff_api_client, staff_user, permission_manage_orders, order_fulfill_data
):
    order = order_fulfill_data.order

    Stock.objects.filter(warehouse=order_fulfill_data.warehouse).delete()

    response = staff_api_client.post_graphql(
        ORDER_FULFILL_QUERY,
        order_fulfill_data.variables,
        permissions=[permission_manage_orders],
    )
    get_graphql_content(response)
    order.refresh_from_db()

    assert order.status == OrderStatus.FULFILLED
    order_lines = order.lines.all()
    assert order_lines[0].quantity_fulfilled == 3
    assert order_lines[0].quantity_unfulfilled == 0

    assert order_lines[1].quantity_fulfilled == 2
    assert order_lines[1].quantity_unfulfilled == 0


def test_order_fulfill_with_allow_stock_to_be_exceeded_flag_disabled_deleted_stocks(
    staff_api_client, staff_user, permission_manage_orders, order_fulfill_data
):
    order = order_fulfill_data.order
    order_fulfill_data.variables["input"]["allowStockToBeExceeded"] = False

    Stock.objects.filter(warehouse=order_fulfill_data.warehouse).delete()

    response = staff_api_client.post_graphql(
        ORDER_FULFILL_QUERY,
        order_fulfill_data.variables,
        permissions=[permission_manage_orders],
    )
    get_graphql_content(response)
    order.refresh_from_db()

    assert not order.status == OrderStatus.FULFILLED

    order_lines = order.lines.all()
    assert order_lines[0].quantity_fulfilled == 0
    assert order_lines[0].quantity_unfulfilled == 3

    assert order_lines[1].quantity_fulfilled == 0
    assert order_lines[1].quantity_unfulfilled == 2


def test_order_fulfill_with_allow_stock_to_be_exceeded_flag_enabled_and_deleted_variant(
    staff_api_client, staff_user, permission_manage_orders, order_fulfill_data
):
    order = order_fulfill_data.order

    order.lines.first().variant.delete()

    response = staff_api_client.post_graphql(
        ORDER_FULFILL_QUERY,
        order_fulfill_data.variables,
        permissions=[permission_manage_orders],
    )
    get_graphql_content(response)
    order.refresh_from_db()

    assert order.status == OrderStatus.FULFILLED
    order_lines = order.lines.all()
    assert order_lines[0].quantity_fulfilled == 3
    assert order_lines[0].quantity_unfulfilled == 0

    assert order_lines[1].quantity_fulfilled == 2
    assert order_lines[1].quantity_unfulfilled == 0


def test_order_fulfill_with_allow_stock_to_be_exceeded_flag_disabled_deleted_variant(
    staff_api_client, staff_user, permission_manage_orders, order_fulfill_data
):
    order = order_fulfill_data.order
    order_fulfill_data.variables["input"]["allowStockToBeExceeded"] = False

    order.lines.first().variant.delete()

    response = staff_api_client.post_graphql(
        ORDER_FULFILL_QUERY,
        order_fulfill_data.variables,
        permissions=[permission_manage_orders],
    )
    get_graphql_content(response)
    order.refresh_from_db()

    assert not order.status == OrderStatus.FULFILLED

    order_lines = order.lines.all()
    assert order_lines[0].quantity_fulfilled == 0
    assert order_lines[0].quantity_unfulfilled == 3

    assert order_lines[1].quantity_fulfilled == 0
    assert order_lines[1].quantity_unfulfilled == 2


@patch("swiftmovers.graphql.order.mutations.order_fulfill.create_fulfillments")
def test_order_fulfill_above_available_quantity(
    mock_create_fulfillments,
    staff_api_client,
    staff_user,
    order_with_lines,
    permission_manage_orders,
    warehouse,
):
    order = order_with_lines
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line, order_line2 = order.lines.all()
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    order_line2_id = graphene.Node.to_global_id("OrderLine", order_line2.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    fulfillment = Fulfillment.objects.create(
        order=order, status=FulfillmentStatus.WAITING_FOR_APPROVAL
    )
    FulfillmentLine.objects.create(
        order_line=order_line,
        quantity=1,
        stock=warehouse.stock_set.first(),
        fulfillment_id=fulfillment.pk,
    )
    variables = {
        "order": order_id,
        "input": {
            "notifyCustomer": True,
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": 4, "warehouse": warehouse_id}],
                },
                {
                    "orderLineId": order_line2_id,
                    "stocks": [{"quantity": 2, "warehouse": warehouse_id}],
                },
            ],
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    error = data["errors"][0]
    assert error["field"] == "orderLineId"
    assert error["code"] == OrderErrorCode.FULFILL_ORDER_LINE.name

    mock_create_fulfillments.assert_not_called()


@patch("swiftmovers.graphql.order.mutations.order_fulfill.create_fulfillments")
def test_order_fulfill_as_app(
    mock_create_fulfillments,
    app_api_client,
    order_with_lines,
    permission_manage_orders,
    warehouse,
    site_settings,
):
    order = order_with_lines
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line, order_line2 = order.lines.all()
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    order_line2_id = graphene.Node.to_global_id("OrderLine", order_line2.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    variables = {
        "order": order_id,
        "input": {
            "notifyCustomer": True,
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": 3, "warehouse": warehouse_id}],
                },
                {
                    "orderLineId": order_line2_id,
                    "stocks": [{"quantity": 2, "warehouse": warehouse_id}],
                },
            ],
        },
    }
    response = app_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert not data["errors"]

    fulfillment_lines_for_warehouses = {
        warehouse.pk: [
            {"order_line": order_line, "quantity": 3},
            {"order_line": order_line2, "quantity": 2},
        ]
    }
    mock_create_fulfillments.assert_called_once_with(
        None,
        app_api_client.app,
        order,
        fulfillment_lines_for_warehouses,
        ANY,
        site_settings,
        True,
        allow_stock_to_be_exceeded=False,
        approved=True,
        tracking_number="",
    )


@patch("swiftmovers.graphql.order.mutations.order_fulfill.create_fulfillments")
def test_order_fulfill_many_warehouses(
    mock_create_fulfillments,
    staff_api_client,
    staff_user,
    order_with_lines,
    permission_manage_orders,
    warehouses,
    site_settings,
):
    order = order_with_lines
    query = ORDER_FULFILL_QUERY

    warehouse1, warehouse2 = warehouses
    order_line1, order_line2 = order.lines.all()

    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line1_id = graphene.Node.to_global_id("OrderLine", order_line1.id)
    order_line2_id = graphene.Node.to_global_id("OrderLine", order_line2.id)
    warehouse1_id = graphene.Node.to_global_id("Warehouse", warehouse1.pk)
    warehouse2_id = graphene.Node.to_global_id("Warehouse", warehouse2.pk)

    variables = {
        "order": order_id,
        "input": {
            "lines": [
                {
                    "orderLineId": order_line1_id,
                    "stocks": [{"quantity": 3, "warehouse": warehouse1_id}],
                },
                {
                    "orderLineId": order_line2_id,
                    "stocks": [
                        {"quantity": 1, "warehouse": warehouse1_id},
                        {"quantity": 1, "warehouse": warehouse2_id},
                    ],
                },
            ],
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert not data["errors"]

    fulfillment_lines_for_warehouses = {
        warehouse1.pk: [
            {"order_line": order_line1, "quantity": 3},
            {"order_line": order_line2, "quantity": 1},
        ],
        warehouse2.pk: [{"order_line": order_line2, "quantity": 1}],
    }

    mock_create_fulfillments.assert_called_once_with(
        staff_user,
        None,
        order,
        fulfillment_lines_for_warehouses,
        ANY,
        site_settings,
        True,
        allow_stock_to_be_exceeded=False,
        approved=True,
        tracking_number="",
    )


@patch("swiftmovers.giftcard.utils.send_gift_card_notification")
def test_order_fulfill_with_gift_cards(
    mock_send_notification,
    staff_api_client,
    staff_user,
    order,
    gift_card_non_shippable_order_line,
    gift_card_shippable_order_line,
    permission_manage_orders,
    warehouse,
):
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line, order_line2 = (
        gift_card_non_shippable_order_line,
        gift_card_shippable_order_line,
    )
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    order_line2_id = graphene.Node.to_global_id("OrderLine", order_line2.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    variables = {
        "order": order_id,
        "input": {
            "notifyCustomer": True,
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": 1, "warehouse": warehouse_id}],
                },
                {
                    "orderLineId": order_line2_id,
                    "stocks": [{"quantity": 1, "warehouse": warehouse_id}],
                },
            ],
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    flush_post_commit_hooks()
    data = content["data"]["orderFulfill"]
    assert not data["errors"]
    gift_cards = GiftCard.objects.all()
    assert gift_cards.count() == 2
    non_shippable_gift_card = gift_cards.get(
        product_id=gift_card_non_shippable_order_line.variant.product_id
    )
    shippable_gift_card = gift_cards.get(
        product_id=gift_card_shippable_order_line.variant.product_id
    )
    assert non_shippable_gift_card.initial_balance.amount == round(
        gift_card_non_shippable_order_line.unit_price_gross.amount, 2
    )
    assert non_shippable_gift_card.current_balance.amount == round(
        gift_card_non_shippable_order_line.unit_price_gross.amount, 2
    )
    assert non_shippable_gift_card.fulfillment_line
    assert shippable_gift_card.initial_balance.amount == round(
        gift_card_shippable_order_line.unit_price_gross.amount, 2
    )
    assert shippable_gift_card.current_balance.amount == round(
        gift_card_shippable_order_line.unit_price_gross.amount, 2
    )
    assert shippable_gift_card.fulfillment_line

    assert GiftCardEvent.objects.filter(
        gift_card=shippable_gift_card, type=GiftCardEvents.BOUGHT
    )
    assert GiftCardEvent.objects.filter(
        gift_card=non_shippable_gift_card, type=GiftCardEvents.BOUGHT
    )

    mock_send_notification.assert_called_once_with(
        staff_user,
        None,
        order.user,
        order.user_email,
        non_shippable_gift_card,
        ANY,
        order.channel.slug,
        resending=False,
    )


@patch("swiftmovers.giftcard.utils.send_gift_card_notification")
def test_order_fulfill_with_gift_card_lines_waiting_for_approval(
    mock_send_notification,
    staff_api_client,
    staff_user,
    order,
    gift_card_non_shippable_order_line,
    gift_card_shippable_order_line,
    permission_manage_orders,
    warehouse,
    site_settings,
):
    query = ORDER_FULFILL_QUERY

    site_settings.fulfillment_auto_approve = False
    site_settings.save(update_fields=["fulfillment_auto_approve"])

    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line, order_line2 = (
        gift_card_non_shippable_order_line,
        gift_card_shippable_order_line,
    )
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    order_line2_id = graphene.Node.to_global_id("OrderLine", order_line2.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    quantity = 1
    variables = {
        "order": order_id,
        "input": {
            "notifyCustomer": True,
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": quantity, "warehouse": warehouse_id}],
                },
                {
                    "orderLineId": order_line2_id,
                    "stocks": [{"quantity": quantity, "warehouse": warehouse_id}],
                },
            ],
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert not data["errors"]
    # ensure gift card weren't created
    assert GiftCard.objects.count() == 0

    mock_send_notification.assert_not_called()


@patch("swiftmovers.giftcard.utils.send_gift_card_notification")
def test_order_fulfill_with_gift_cards_by_app(
    mock_send_notification,
    app_api_client,
    order,
    gift_card_shippable_order_line,
    permission_manage_orders,
    warehouse,
    site_settings,
):
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line = gift_card_shippable_order_line
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    quantity = 2
    variables = {
        "order": order_id,
        "input": {
            "notifyCustomer": True,
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": quantity, "warehouse": warehouse_id}],
                },
            ],
        },
    }
    response = app_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert not data["errors"]
    assert GiftCard.objects.count() == quantity

    mock_send_notification.assert_not_called


@patch("swiftmovers.giftcard.utils.send_gift_card_notification")
def test_order_fulfill_with_gift_cards_multiple_warehouses(
    mock_send_notification,
    app_api_client,
    order,
    gift_card_shippable_order_line,
    permission_manage_orders,
    warehouses,
    shipping_zone,
    site_settings,
):
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line = gift_card_shippable_order_line
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    warehouse1, warehouse2 = warehouses
    for warehouse in warehouses:
        warehouse.shipping_zones.add(shipping_zone)
        warehouse.save()
    stock_1 = Stock.objects.create(
        warehouse=warehouse1, product_variant=order_line.variant, quantity=1
    )
    Allocation.objects.create(
        order_line=order_line, stock=stock_1, quantity_allocated=1
    )
    stock_2 = Stock.objects.create(
        warehouse=warehouse2, product_variant=order_line.variant, quantity=1
    )
    Allocation.objects.create(
        order_line=order_line, stock=stock_2, quantity_allocated=1
    )
    warehouse1_id = graphene.Node.to_global_id("Warehouse", warehouse1.pk)
    warehouse2_id = graphene.Node.to_global_id("Warehouse", warehouse2.pk)
    quantity_1 = 2
    quantity_2 = 1
    variables = {
        "order": order_id,
        "input": {
            "notifyCustomer": True,
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [
                        {"quantity": quantity_1, "warehouse": warehouse1_id},
                        {"quantity": quantity_2, "warehouse": warehouse2_id},
                    ],
                },
            ],
        },
    }
    response = app_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert not data["errors"]
    assert GiftCard.objects.count() == quantity_1 + quantity_2

    mock_send_notification.assert_not_called


@patch("swiftmovers.graphql.order.mutations.order_fulfill.create_fulfillments")
def test_order_fulfill_without_notification(
    mock_create_fulfillments,
    staff_api_client,
    staff_user,
    order_with_lines,
    permission_manage_orders,
    warehouse,
    site_settings,
):
    order = order_with_lines
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line = order.lines.first()
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    variables = {
        "order": order_id,
        "input": {
            "notifyCustomer": False,
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": 1, "warehouse": warehouse_id}],
                }
            ],
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert not data["errors"]

    fulfillment_lines_for_warehouses = {
        warehouse.pk: [{"order_line": order_line, "quantity": 1}]
    }
    mock_create_fulfillments.assert_called_once_with(
        staff_user,
        None,
        order,
        fulfillment_lines_for_warehouses,
        ANY,
        site_settings,
        False,
        allow_stock_to_be_exceeded=False,
        approved=True,
        tracking_number="",
    )


@patch("swiftmovers.graphql.order.mutations.order_fulfill.create_fulfillments")
def test_order_fulfill_lines_with_empty_quantity(
    mock_create_fulfillments,
    staff_api_client,
    staff_user,
    order_with_lines,
    permission_manage_orders,
    warehouse,
    warehouse_no_shipping_zone,
    site_settings,
):
    order = order_with_lines
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line, order_line2 = order.lines.all()
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    order_line2_id = graphene.Node.to_global_id("OrderLine", order_line2.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    warehouse2_id = graphene.Node.to_global_id(
        "Warehouse", warehouse_no_shipping_zone.pk
    )
    assert not order.events.all()
    variables = {
        "order": order_id,
        "input": {
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [
                        {"quantity": 0, "warehouse": warehouse_id},
                        {"quantity": 0, "warehouse": warehouse2_id},
                    ],
                },
                {
                    "orderLineId": order_line2_id,
                    "stocks": [
                        {"quantity": 2, "warehouse": warehouse_id},
                        {"quantity": 0, "warehouse": warehouse2_id},
                    ],
                },
            ],
        },
    }
    variables["input"]["lines"][0]["stocks"][0]["quantity"] = 0
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert not data["errors"]

    fulfillment_lines_for_warehouses = {
        warehouse.pk: [{"order_line": order_line2, "quantity": 2}]
    }
    mock_create_fulfillments.assert_called_once_with(
        staff_user,
        None,
        order,
        fulfillment_lines_for_warehouses,
        ANY,
        site_settings,
        True,
        allow_stock_to_be_exceeded=False,
        approved=True,
        tracking_number="",
    )


@pytest.mark.parametrize("fulfillment_auto_approve", [True, False])
@patch("swiftmovers.graphql.order.mutations.order_fulfill.create_fulfillments")
def test_order_fulfill_without_sku(
    mock_create_fulfillments,
    fulfillment_auto_approve,
    staff_api_client,
    staff_user,
    order_with_lines,
    permission_manage_orders,
    warehouse,
    site_settings,
):
    ProductVariant.objects.update(sku=None)
    site_settings.fulfillment_auto_approve = fulfillment_auto_approve
    site_settings.save(update_fields=["fulfillment_auto_approve"])
    order = order_with_lines
    query = ORDER_FULFILL_QUERY
    order.lines.update(product_sku=None)
    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line, order_line2 = order.lines.all()
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    order_line2_id = graphene.Node.to_global_id("OrderLine", order_line2.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    variables = {
        "order": order_id,
        "input": {
            "notifyCustomer": True,
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": 3, "warehouse": warehouse_id}],
                },
                {
                    "orderLineId": order_line2_id,
                    "stocks": [{"quantity": 2, "warehouse": warehouse_id}],
                },
            ],
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert not data["errors"]

    fulfillment_lines_for_warehouses = {
        warehouse.pk: [
            {"order_line": order_line, "quantity": 3},
            {"order_line": order_line2, "quantity": 2},
        ]
    }
    mock_create_fulfillments.assert_called_once_with(
        staff_user,
        None,
        order,
        fulfillment_lines_for_warehouses,
        ANY,
        site_settings,
        True,
        allow_stock_to_be_exceeded=False,
        approved=fulfillment_auto_approve,
        tracking_number="",
    )


@patch("swiftmovers.graphql.order.mutations.order_fulfill.create_fulfillments")
def test_order_fulfill_zero_quantity(
    mock_create_fulfillments,
    staff_api_client,
    staff_user,
    order_with_lines,
    permission_manage_orders,
    warehouse,
):
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order_with_lines.id)
    order_line = order_with_lines.lines.first()
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    variables = {
        "order": order_id,
        "input": {
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": 0, "warehouse": warehouse_id}],
                }
            ]
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert data["errors"]
    error = data["errors"][0]
    assert error["field"] == "lines"
    assert error["code"] == OrderErrorCode.ZERO_QUANTITY.name
    assert not error["orderLines"]
    assert not error["warehouse"]

    mock_create_fulfillments.assert_not_called()


def test_order_fulfill_channel_without_shipping_zones(
    staff_api_client,
    order_with_lines,
    permission_manage_orders,
    warehouse,
):
    order = order_with_lines
    order.channel.shipping_zones.clear()
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line = order.lines.first()
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    variables = {
        "order": order_id,
        "input": {
            "notifyCustomer": True,
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": 3, "warehouse": warehouse_id}],
                },
            ],
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert len(data["errors"]) == 1
    error = data["errors"][0]
    assert error["field"] == "stocks"
    assert error["code"] == OrderErrorCode.INSUFFICIENT_STOCK.name


@patch("swiftmovers.graphql.order.mutations.order_fulfill.create_fulfillments")
def test_order_fulfill_fulfilled_order(
    mock_create_fulfillments,
    staff_api_client,
    staff_user,
    order_with_lines,
    permission_manage_orders,
    warehouse,
):
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order_with_lines.id)
    order_line = order_with_lines.lines.first()
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    variables = {
        "order": order_id,
        "input": {
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": 100, "warehouse": warehouse_id}],
                }
            ]
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert data["errors"]
    error = data["errors"][0]
    assert error["field"] == "orderLineId"
    assert error["code"] == OrderErrorCode.FULFILL_ORDER_LINE.name
    assert error["orderLines"] == [order_line_id]
    assert not error["warehouse"]

    mock_create_fulfillments.assert_not_called()


@patch("swiftmovers.graphql.order.mutations.order_fulfill.create_fulfillments")
def test_order_fulfill_unpaid_order_and_disallow_unpaid(
    mock_create_fulfillments,
    staff_api_client,
    order_with_lines,
    permission_manage_orders,
    warehouse,
    site_settings,
):
    site_settings.fulfillment_allow_unpaid = False
    site_settings.save(update_fields=["fulfillment_allow_unpaid"])
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order_with_lines.id)
    order_line = order_with_lines.lines.first()
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    variables = {
        "order": order_id,
        "input": {
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": 100, "warehouse": warehouse_id}],
                }
            ]
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert data["errors"]
    error = data["errors"][0]
    assert error["field"] == "order"
    assert error["code"] == OrderErrorCode.CANNOT_FULFILL_UNPAID_ORDER.name

    mock_create_fulfillments.assert_not_called()


@patch(
    "swiftmovers.graphql.order.mutations.order_fulfill.create_fulfillments", autospec=True
)
def test_order_fulfill_warehouse_with_insufficient_stock_exception(
    mock_create_fulfillments,
    staff_api_client,
    order_with_lines,
    permission_manage_orders,
    warehouse_no_shipping_zone,
):
    order = order_with_lines
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line = order.lines.first()
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    warehouse_id = graphene.Node.to_global_id(
        "Warehouse", warehouse_no_shipping_zone.pk
    )
    variables = {
        "order": order_id,
        "input": {
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": 1, "warehouse": warehouse_id}],
                }
            ]
        },
    }

    mock_create_fulfillments.side_effect = InsufficientStock(
        [
            InsufficientStockData(
                variant=order_line.variant,
                order_line=order_line,
                warehouse_pk=warehouse_no_shipping_zone.pk,
                available_quantity=0,
            )
        ]
    )

    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert data["errors"]
    error = data["errors"][0]
    assert error["field"] == "stocks"
    assert error["code"] == OrderErrorCode.INSUFFICIENT_STOCK.name
    assert error["orderLines"] == [order_line_id]
    assert error["warehouse"] == warehouse_id


@patch(
    "swiftmovers.graphql.order.mutations.order_fulfill.create_fulfillments", autospec=True
)
def test_order_fulfill_warehouse_duplicated_warehouse_id(
    mock_create_fulfillments,
    staff_api_client,
    order_with_lines,
    permission_manage_orders,
    warehouse,
):
    order = order_with_lines
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line = order.lines.first()
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    variables = {
        "order": order_id,
        "input": {
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [
                        {"quantity": 1, "warehouse": warehouse_id},
                        {"quantity": 2, "warehouse": warehouse_id},
                    ],
                }
            ]
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert data["errors"]
    error = data["errors"][0]
    assert error["field"] == "warehouse"
    assert error["code"] == OrderErrorCode.DUPLICATED_INPUT_ITEM.name
    assert not error["orderLines"]
    assert error["warehouse"] == warehouse_id
    mock_create_fulfillments.assert_not_called()


@patch(
    "swiftmovers.graphql.order.mutations.order_fulfill.create_fulfillments", autospec=True
)
def test_order_fulfill_warehouse_duplicated_order_line_id(
    mock_create_fulfillments,
    staff_api_client,
    order_with_lines,
    permission_manage_orders,
    warehouse,
):
    order = order_with_lines
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line = order.lines.first()
    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    variables = {
        "order": order_id,
        "input": {
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": 3, "warehouse": warehouse_id}],
                },
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": 3, "warehouse": warehouse_id}],
                },
            ]
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert data["errors"]
    error = data["errors"][0]
    assert error["field"] == "orderLineId"
    assert error["code"] == OrderErrorCode.DUPLICATED_INPUT_ITEM.name
    assert error["orderLines"] == [order_line_id]
    assert not error["warehouse"]
    mock_create_fulfillments.assert_not_called()


@patch("swiftmovers.graphql.order.mutations.order_fulfill.create_fulfillments")
def test_order_fulfill_preorder(
    mock_create_fulfillments,
    staff_api_client,
    staff_user,
    order_with_lines,
    permission_manage_orders,
    warehouse,
):
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order_with_lines.id)
    order_line = order_with_lines.lines.first()
    variant = order_line.variant
    variant.is_preorder = True
    variant.save(update_fields=["is_preorder"])

    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    variables = {
        "order": order_id,
        "input": {
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": 0, "warehouse": warehouse_id}],
                }
            ]
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert data["errors"]
    error = data["errors"][0]
    assert error["field"] == "orderLineId"
    assert error["code"] == OrderErrorCode.FULFILL_ORDER_LINE.name
    assert error["orderLines"]

    mock_create_fulfillments.assert_not_called()


def test_order_fulfill_preorder_waiting_fulfillment(
    staff_api_client,
    order_with_lines,
    permission_manage_orders,
    warehouse,
    site_settings,
):
    """If fulfillment_auto_approve is set to False,
    it's possible to fulfill lines to WAITING_FOR_APPROVAL status."""
    site_settings.fulfillment_auto_approve = False
    site_settings.save(update_fields=["fulfillment_auto_approve"])
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order_with_lines.id)
    order_line = order_with_lines.lines.first()
    variant = order_line.variant
    variant.is_preorder = True
    variant.save(update_fields=["is_preorder"])

    order_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)
    variables = {
        "order": order_id,
        "input": {
            "lines": [
                {
                    "orderLineId": order_line_id,
                    "stocks": [{"quantity": 3, "warehouse": warehouse_id}],
                }
            ]
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    content = get_graphql_content(response)
    data = content["data"]["orderFulfill"]
    assert not data["errors"]
    assert (
        order_with_lines.fulfillments.first().status
        == FulfillmentStatus.WAITING_FOR_APPROVAL
    )


@patch("swiftmovers.order.actions.send_fulfillment_confirmation_to_customer", autospec=True)
def test_create_digital_fulfillment(
    mock_email_fulfillment,
    digital_content,
    staff_api_client,
    order_with_lines,
    warehouse,
    permission_manage_orders,
):
    order = order_with_lines
    query = ORDER_FULFILL_QUERY
    order_id = graphene.Node.to_global_id("Order", order.id)
    order_line = order.lines.first()
    order_line.variant = digital_content.product_variant
    order_line.save()
    order_line.allocations.all().delete()

    stock = digital_content.product_variant.stocks.get(warehouse=warehouse)
    Allocation.objects.create(
        order_line=order_line, stock=stock, quantity_allocated=order_line.quantity
    )

    second_line = order.lines.last()
    first_line_id = graphene.Node.to_global_id("OrderLine", order_line.id)
    second_line_id = graphene.Node.to_global_id("OrderLine", second_line.id)
    warehouse_id = graphene.Node.to_global_id("Warehouse", warehouse.pk)

    variables = {
        "order": order_id,
        "input": {
            "notifyCustomer": True,
            "lines": [
                {
                    "orderLineId": first_line_id,
                    "stocks": [{"quantity": 1, "warehouse": warehouse_id}],
                },
                {
                    "orderLineId": second_line_id,
                    "stocks": [{"quantity": 1, "warehouse": warehouse_id}],
                },
            ],
        },
    }
    response = staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_orders]
    )
    get_graphql_content(response)

    assert mock_email_fulfillment.call_count == 1
