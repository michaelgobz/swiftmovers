from urllib.parse import urljoin

import graphene
from django.conf import settings
from ..enums import ZoneErrorCode
from ..enums import (
    AccountErrorCode,
    CheckoutErrorCode,
    InvoiceErrorCode,
    LanguageCodeEnum,
    OrderErrorCode,
    PaymentErrorCode,
    MetadataErrorCode,
    itemsErrorCode,
    ShippingErrorCodes,
    WeightUnitsEnum,

)
from ..scalars import PositiveDecimal
from ...accounts.enums import AddressTypeEnum

TYPES_WITH_DOUBLE_ID_AVAILABLE = [""]

class Error(graphene.ObjectType):
    field = graphene.String(
        description=(
            "Name of a field that caused the error. A value of `null` indicates that "
            "the error isn't associated with a particular field."
        ),
        required=False,
    )
    message = graphene.String(description="The error message.")

    class Meta:
        description = "Represents an error in the input of a mutation."
class NonNullList(graphene.List):
    """A list type that automatically adds non-null constraint on contained items."""

    def __init__(self, of_type, *args, **kwargs):
        of_type = graphene.NonNull(of_type)
        super(NonNullList, self).__init__(of_type, *args, **kwargs)


class CountryDisplay(graphene.ObjectType):
    code = graphene.String(description="Country code.", required=True)
    country = graphene.String(description="Country name.", required=True)
    # TODO: Add countries taxes


class LanguageDisplay(graphene.ObjectType):
    code = LanguageCodeEnum(
        description="ISO 639 representation of the language name.", required=True
    )
    language = graphene.String(description="Full name of the language.", required=True)
class MetadataError(Error):
    code = MetadataErrorCode(description="The error code.", required=True)

class Error(graphene.ObjectType):
    field = graphene.String(
        description=(
            "Name of a field that caused the error. A value of `null` indicates that "
            "the error isn't associated with a particular field."
        ),
        required=False,
    )
    message = graphene.String(description="The error message.")

    class Meta:
        description = "Represents an error in the input of a mutation."


class AccountError(Error):
    code = AccountErrorCode(description="The error code.", required=True)
    address_type = AddressTypeEnum(
        description="A type of address that causes the error.", required=False
    )


class ZoneError(Error):
    code = ZoneErrorCode(description="The error code.", required=True)
    shipping_zones = NonNullList(
        graphene.ID,
        description="List of shipping zone IDs which causes the error.",
        required=False,
    )
    warehouses = NonNullList(
        graphene.ID,
        description="List of warehouses IDs which causes the error.",
        required=False,
    )


class CheckoutError(Error):
    code = CheckoutErrorCode(description="The error code.", required=True)
    variants = NonNullList(
        graphene.ID,
        description="List of varint IDs which causes the error.",
        required=False,
    )
    lines = NonNullList(
        graphene.ID,
        description="List of line Ids which cause the error.",
        required=False,
    )
    address_type = AddressTypeEnum(
        description="A type of address that causes the error.", required=False
    )


class ProductWithoutVariantError(Error):
    products = NonNullList(
        graphene.ID,
        description="List of products IDs which causes the error.",
    )


class OrderError(Error):
    code = OrderErrorCode(description="The error code.", required=True)
    warehouse = graphene.ID(
        description="Warehouse ID which causes the error.",
        required=False,
    )
    order_lines = NonNullList(
        graphene.ID,
        description="List of order line IDs that cause the error.",
        required=False,
    )
    variants = NonNullList(
        graphene.ID,
        description="List of product variants that are associated with the error",
        required=False,
    )
    address_type = AddressTypeEnum(
        description="A type of address that causes the error.", required=False
    )


class InvoiceError(Error):
    code = InvoiceErrorCode(description="The error code.", required=True)


class ItemsError(Error):
    code = itemsErrorCode(description="The error code.", required=True)
    attributes = NonNullList(
        graphene.ID,
        description="List of attributes IDs which causes the error.",
        required=False,
    )
    values = NonNullList(
        graphene.ID,
        description="List of attribute values IDs which causes the error.",
        required=False,
    )


class ShippingError(Error):
    code = ShippingErrorCodes(description="The error code.", required=True)
    warehouses = NonNullList(
        graphene.ID,
        description="List of warehouse IDs which causes the error.",
        required=False,
    )


class PaymentError(Error):
    code = PaymentErrorCode(description="The error code.", required=True)
    variants = NonNullList(
        graphene.ID,
        description="List of variant IDs which causes the error.",
        required=False,
    )


class SeoInput(graphene.InputObjectType):
    title = graphene.String(description="SEO title.")
    description = graphene.String(description="SEO description.")


class Weight(graphene.ObjectType):
    unit = WeightUnitsEnum(description="Weight unit.", required=True)
    value = graphene.Float(description="Weight value.", required=True)

    class Meta:
        description = "Represents weight value in a specific weight unit."


class Image(graphene.ObjectType):
    url = graphene.String(required=True, description="The URL of the image.")
    alt = graphene.String(description="Alt text for an image.")

    class Meta:
        description = "Represents an image."

    @staticmethod
    def resolve_url(root, info):
        return info.context.build_absolute_uri(urljoin(settings.MEDIA_URL, root.url))


class File(graphene.ObjectType):
    url = graphene.String(required=True, description="The URL of the file.")
    content_type = graphene.String(
        required=False, description="Content type of the file."
    )

    @staticmethod
    def resolve_url(root, info):
        return info.context.build_absolute_uri(urljoin(settings.MEDIA_URL, root.url))


class PriceInput(graphene.InputObjectType):
    currency = graphene.String(description="Currency code.", required=True)
    amount = PositiveDecimal(description="Amount of money.", required=True)


class PriceRangeInput(graphene.InputObjectType):
    gte = graphene.Float(description="Price greater than or equal to.", required=False)
    lte = graphene.Float(description="Price less than or equal to.", required=False)


class DateRangeInput(graphene.InputObjectType):
    gte = graphene.Date(description="Start date.", required=False)
    lte = graphene.Date(description="End date.", required=False)


class DateTimeRangeInput(graphene.InputObjectType):
    gte = graphene.DateTime(description="Start date.", required=False)
    lte = graphene.DateTime(description="End date.", required=False)


class IntRangeInput(graphene.InputObjectType):
    gte = graphene.Int(description="Value greater than or equal to.", required=False)
    lte = graphene.Int(description="Value less than or equal to.", required=False)


class TaxType(graphene.ObjectType):
    """Representation of tax types fetched from tax gateway."""

    description = graphene.String(description="Description of the tax type.")
    tax_code = graphene.String(
        description="External tax code used to identify given tax group."
    )
