import graphene
from django.conf import settings

from ...accounts import error_codes as account_error_codes
from ...zones import error_codes as zone_error_codes
from ...checkouts import error_codes as checkout_error_codes
from ...core.units import (
    AreaUnits,
    DistanceUnits,
    MeasurementUnits,
    VolumeUnits,
    WeightUnits,
)

from ...invoices import error_codes as invoice_error_codes
from ...orders import error_codes as order_error_codes
from ...payments import error_codes as payment_error_codes
from ...items import error_codes as items_error_codes
from ...shipping import error_codes as shipping_error_codes
from ...core import error_codes as core_error_codes


def str_to_enum(name):
    """Create an enum value from a string."""
    return name.replace(" ", "_").replace("-", "_").upper()


class OrderDirection(graphene.Enum):
    ASC = ""
    DESC = "-"

    @property
    def description(self):
        # Disable all the no-member violations in this function
        # pylint: disable=no-member
        if self == OrderDirection.ASC:
            return "Specifies an ascending sort order."
        if self == OrderDirection.DESC:
            return "Specifies a descending sort order."
        raise ValueError(f"Unsupported enum value: {self.value}")


class ReportingPeriod(graphene.Enum):
    TODAY = "TODAY"
    THIS_MONTH = "THIS_MONTH"


def to_enum(enum_cls, *, type_name=None, **options) -> graphene.Enum:
    """Create a Graphene enum from a class containing a set of options.

    :param enum_cls:
        The class to build the enum from.
    :param type_name:
        The name of the type. Default is the class name + 'Enum'.
    :param options:
        - description:
            Contains the type description (default is the class's docstring)
        - deprecation_reason:
            Contains the deprecation reason.
            The default is enum_cls.__deprecation_reason__ or None.
    :return:
    """

    # note this won't work until
    # https://github.com/graphql-python/graphene/issues/956 is fixed
    deprecation_reason = getattr(enum_cls, "__deprecation_reason__", None)
    if deprecation_reason:
        options.setdefault("deprecation_reason", deprecation_reason)

    type_name = type_name or (enum_cls.__name__ + "Enum")
    enum_data = [(str_to_enum(code.upper()), code) for code, name in enum_cls.CHOICES]
    return graphene.Enum(type_name, enum_data, **options)


LanguageCodeEnum = graphene.Enum(
    "LanguageCodeEnum",
    [(lang[0].replace("-", "_").upper(), lang[0]) for lang in settings.LANGUAGES],
)

# unit enums.py
MeasurementUnitsEnum = to_enum(MeasurementUnits)
DistanceUnitsEnum = to_enum(DistanceUnits)
AreaUnitsEnum = to_enum(AreaUnits)
VolumeUnitsEnum = to_enum(VolumeUnits)
WeightUnitsEnum = to_enum(WeightUnits)
unit_enums = [DistanceUnitsEnum, AreaUnitsEnum, VolumeUnitsEnum, WeightUnitsEnum]

AccountErrorCode = graphene.Enum.from_enum(account_error_codes.AccountErrorCode)
CheckoutErrorCode = graphene.Enum.from_enum(checkout_error_codes.CheckoutErrorCode)
ZoneErrorCode = graphene.Enum.from_enum(zone_error_codes.ZoneErrorCode)
MetadataErrorCode = graphene.Enum.from_enum(core_error_codes.MetadataErrorCode)

OrderErrorCode = graphene.Enum.from_enum(order_error_codes.OrderErrorCode)
InvoiceErrorCode = graphene.Enum.from_enum(invoice_error_codes.InvoiceErrorCode)
PaymentErrorCode = graphene.Enum.from_enum(payment_error_codes.PaymentErrorCode)
ShippingErrorCodes = graphene.Enum.from_enum(shipping_error_codes.ShippingErrorCode)

itemsErrorCode = graphene.Enum.from_enum(items_error_codes.ProductErrorCode)
