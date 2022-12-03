import graphene
from django_prices.templatetags import prices
from graphene import Argument, InputField, InputObjectType, String
from graphene.types.inputobjecttype import InputObjectTypeOptions
from graphene.types.utils import yank_fields_from_attrs

from .converter import convert_form_field

from ....core.prices import quantize_price
from .globals import *
from .model import *
from ..enums import *


class Money(graphene.ObjectType):
    currency = graphene.String(description="Currency code.", required=True)
    amount = graphene.Float(description="Amount of money.", required=True)

    class Meta:
        description = "Represents amount of money in specific currency."

    @staticmethod
    def resolve_amount(root, _info):
        return quantize_price(root.amount, root.currency)

    @staticmethod
    def resolve_localized(root, _info):
        return prices.amount(root)

class SortInputMeta(ObjectTypeOptions):
    sort_enum = None


class SortInputObjectType(graphene.InputObjectType):
    direction = graphene.Argument(
        OrderDirection,
        required=True,
        description="Specifies the direction in which to sort products.",
    )

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls, container=None, _meta=None, sort_enum=None, type_name=None, **options
    ):
        if not _meta:
            _meta = SortInputMeta(cls)
        if sort_enum:
            _meta.sort_enum = sort_enum

        super().__init_subclass_with_meta__(container, _meta, **options)
        if sort_enum and type_name:
            field = graphene.Argument(
                sort_enum,
                required=True,
                description=f"Sort {type_name} by the selected field.",
            )
            cls._meta.fields.update({"field": field})
class MoneyRange(graphene.ObjectType):
    start = graphene.Field(Money, description="Lower bound of a price range.")
    stop = graphene.Field(Money, description="Upper bound of a price range.")

    class Meta:
        description = "Represents a range of amounts of money."


class TaxedMoney(graphene.ObjectType):
    currency = graphene.String(description="Currency code.", required=True)
    gross = graphene.Field(
        Money, description="Amount of money including taxes.", required=True
    )
    net = graphene.Field(
        Money, description="Amount of money without taxes.", required=True
    )
    tax = graphene.Field(Money, description="Amount of taxes.", required=True)

    class Meta:
        description = (
            "Represents a monetary value with taxes. In cases where taxes were not "
            "applied, net and gross values will be equal."
        )


class TaxedMoneyRange(graphene.ObjectType):
    start = graphene.Field(TaxedMoney, description="Lower bound of a price range.")
    stop = graphene.Field(TaxedMoney, description="Upper bound of a price range.")

    class Meta:
        description = "Represents a range of monetary values."


class VAT(graphene.ObjectType):
    country_code = graphene.String(description="Country code.", required=True)
    standard_rate = graphene.Float(description="Standard VAT rate in percent.")
    reduced_rates = graphene.List(
        graphene.NonNull(lambda: ReducedRate),
        description="Country's VAT rate exceptions for specific types of goods.",
        required=True,
    )

    class Meta:
        description = "Represents a VAT rate for a country."

    @staticmethod
    def resolve_standard_rate(root, _info):
        return root.data.get("standard_rate")

    @staticmethod
    def resolve_reduced_rates(root, _info):
        reduced_rates = root.data.get("reduced_rates", {}) or {}
        return [
            ReducedRate(rate=rate, rate_type=rate_type)
            for rate_type, rate in reduced_rates.items()
        ]


class ReducedRate(graphene.ObjectType):
    rate = graphene.Float(description="Reduced VAT rate in percent.", required=True)
    rate_type = graphene.String(description="A type of goods.", required=True)

    class Meta:
        description = "Represents a reduced VAT rate for a particular type of goods."

# filters.py.py

def get_filterset_class(filterset_class=None):
    return type(
        "GraphQL{}".format(filterset_class.__name__),
        {},
    )


class FilterInputObjectType(InputObjectType):
    """Class for storing and serving django-filtres as graphQL input.

    FilterSet class which inherits from django-filters.py.py.FilterSet should be
    provided with using fitlerset_class argument.
    """

    @classmethod
    def __init_subclass_with_meta__(
        cls, _meta=None, model=None, filterset_class=None, fields=None, **options
    ):
        cls.custom_filterset_class = filterset_class
        cls.filterset_class = None
        cls.fields = fields
        cls.model = model

        if not _meta:
            _meta = InputObjectTypeOptions(cls)

        fields = cls.get_filtering_args_from_filterset()
        fields = yank_fields_from_attrs(fields, _as=InputField)
        if _meta.fields:
            _meta.fields.update(fields)
        else:
            _meta.fields = fields

        super().__init_subclass_with_meta__(_meta=_meta, **options)

    @classmethod
    def get_filtering_args_from_filterset(cls):
        """Retrieve the filtering arguments from the queryset.

        Inspect a FilterSet and produce the arguments to pass to a Graphene field.
        These arguments will be available to filter against in the GraphQL.
        """
        if not cls.custom_filterset_class:
            raise ValueError("Provide filterset class")

        cls.filterset_class = get_filterset_class(cls.custom_filterset_class)

        args = {}
        for name, filter_field in cls.filterset_class.base_filters.items():
            input_class = getattr(filter_field, "input_class", None)
            if input_class:
                field_type = convert_form_field(filter_field)
            else:
                field_type = convert_form_field(filter_field.field)
                field_type.description = getattr(filter_field, "help_text", "")
            kwargs = getattr(field_type, "kwargs", {})
            field_type.kwargs = kwargs
            args[name] = field_type
        return args


class ZoneFilterInputObjectType(FilterInputObjectType):
    Zone = Argument(
        String,
        description=(
            "Specifies the zone by which the data should be filtered. "

        ),
    )

    class Meta:
        abstract = True
