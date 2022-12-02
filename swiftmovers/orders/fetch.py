from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, List, Optional

if TYPE_CHECKING:
    from ..zones.models import Zone
    from ..payments.models import Payment
    from ..items.models import DigitalContent, ProductVariant
    from .models import Order, OrderLine


@dataclass
class OrderInfo:
    order: "Order"
    customer_email: "str"
    Zone: "Zone"
    payment: "Payment"
    lines_data: Iterable["OrderLineInfo"]


@dataclass
class OrderLineInfo:
    line: "OrderLine"
    quantity: int
    variant: Optional["ProductVariant"] = None
    is_digital: Optional[bool] = None
    digital_content: Optional["DigitalContent"] = None
    replace: bool = False
    warehouse_pk: Optional[str] = None


def fetch_order_info(order: "Order") -> OrderInfo:
    order_lines_info = fetch_order_lines(order)
    order_data = OrderInfo(
        order=order,
        customer_email=order.get_customer_email(),
        channel=order.channel,
        payment=order.get_last_payment(),
        lines_data=order_lines_info,
    )
    return order_data


