from unittest.mock import ANY, patch

import graphene

from .....core.notify_events import NotifyEventType
from .....core.tests.utils import get_site_context_payload
from .....order import events as order_events
from .....order.notifications import get_default_order_payload
from .....payment import ChargeStatus
from .....payment.models import Payment
from ....payment.types import PaymentChargeStatusEnum
from ....tests.utils import get_graphql_content

ORDER_CAPTURE_MUTATION = """
        mutation captureOrder($id: ID!, $amount: PositiveDecimal!) {
            orderCapture(id: $id, amount: $amount) {
                order {
                    paymentStatus
                    paymentStatusDisplay
                    isPaid
                    totalCharged {
                        amount
                    }
                    totalCaptured {
                        amount
                    }
                }
                errors{
                    field
                    message
                    code
                }
            }
        }
"""


@patch("swiftmovers.giftcard.utils.fulfill_non_shippable_gift_cards")
@patch("swiftmovers.plugins.manager.PluginsManager.notify")
def test_order_capture(
    mocked_notify,
    fulfill_non_shippable_gift_cards_mock,
    staff_api_client,
    permission_manage_orders,
    payment_txn_preauth,
    staff_user,
    site_settings,
):
    # given
    order = payment_txn_preauth.order

    order_id = graphene.Node.to_global_id("Order", order.id)
    amount = float(payment_txn_preauth.total)
    variables = {"id": order_id, "amount": amount}

    # when
    response = staff_api_client.post_graphql(
        ORDER_CAPTURE_MUTATION, variables, permissions=[permission_manage_orders]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["orderCapture"]["order"]
    order.refresh_from_db()
    assert data["paymentStatus"] == PaymentChargeStatusEnum.FULLY_CHARGED.name
    payment_status_display = dict(ChargeStatus.CHOICES).get(ChargeStatus.FULLY_CHARGED)
    assert data["paymentStatusDisplay"] == payment_status_display
    assert data["isPaid"]
    assert data["totalCaptured"]["amount"] == float(amount)
    assert data["totalCharged"]["amount"] == float(amount)

    event_captured, event_order_fully_paid = order.events.all()

    assert event_captured.type == order_events.OrderEvents.PAYMENT_CAPTURED
    assert event_captured.user == staff_user
    assert event_captured.parameters == {
        "amount": str(amount),
        "payment_gateway": "mirumee.payments.dummy",
        "payment_id": "",
    }

    assert event_order_fully_paid.type == order_events.OrderEvents.ORDER_FULLY_PAID
    assert event_order_fully_paid.user == staff_user

    payment = Payment.objects.get()
    expected_payment_payload = {
        "order": get_default_order_payload(order),
        "recipient_email": order.get_customer_email(),
        "payment": {
            "created": payment.created_at,
            "modified": payment.modified_at,
            "charge_status": payment.charge_status,
            "total": payment.total,
            "captured_amount": payment.captured_amount,
            "currency": payment.currency,
        },
        **get_site_context_payload(site_settings.site),
    }

    mocked_notify.assert_called_once_with(
        NotifyEventType.ORDER_PAYMENT_CONFIRMATION,
        expected_payment_payload,
        channel_slug=order.channel.slug,
    )
    fulfill_non_shippable_gift_cards_mock.assert_called_once_with(
        order, list(order.lines.all()), site_settings, staff_api_client.user, None, ANY
    )
