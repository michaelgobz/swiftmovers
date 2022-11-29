import dataclasses
from operator import itemgetter

from ...accounts import models as account_models
from ...checkouts import models as checkout_models
from ...core.exceptions import PermissionDenied
from ...core.models import ModelWithMetadata
from ...orders import models as order_models
from ...payments import models as payment_models
from ...items import models as item_models
from ...shipping import models as shipping_models
from ...shipping.interface import ShippingMethodData
from ..utils import get_user_or_app_from_context


def resolve_object_with_metadata_type(instance):
    # Imports inside resolvers to avoid circular imports.
    from ...invoices import models as invoice_models
    from ..accounts import types as account_types
    from ..checkouts import types as checkout_types
    from ..orders import types as order_types
    from ..payments import types as payment_types
    from ..items import types as product_types
    from ..shipping import types as shipping_types

    if isinstance(instance, ModelWithMetadata):
        MODEL_TO_TYPE_MAP = {

            item_models.Category: product_types.Category,
            checkout_models.Checkout: checkout_types.Checkout,
            checkout_models.CheckoutLine: checkout_types.CheckoutLine,
            item_models.Collection: product_types.Collection,
            item_models.DigitalContent: product_types.DigitalContent,
            order_models.Fulfillment: order_types.Fulfillment,
            order_models.Order: order_types.Order,
            order_models.OrderLine: order_types.OrderLine,
            invoice_models.Invoice: invoice_types.Invoice,

            payment_models.Payment: payment_types.Payment,
            payment_models.TransactionItem: payment_types.TransactionItem,
            item_models.Product: product_types.Product,
            item_models.ProductType: product_types.ProductType,
            shipping_models.ShippingMethod: shipping_types.ShippingMethodType,
            shipping_models.ShippingZone: shipping_types.ShippingZone,
            account_models.User: account_types.User,

        }
        return MODEL_TO_TYPE_MAP.get(instance.__class__, None), instance.pk

    elif dataclasses.is_dataclass(instance):
        DATACLASS_TO_TYPE_MAP = {ShippingMethodData: shipping_types.ShippingMethod}
        return DATACLASS_TO_TYPE_MAP.get(instance.__class__, None), instance.id


def resolve_metadata(metadata: dict):
    return sorted(
        [{"key": k, "value": v} for k, v in metadata.items()],
        key=itemgetter("key"),
    )

