import collections
import itertools
from typing import Dict, List, Type, Union, cast
import graphene
from django.db.models import Model
from graphene.types.resolver import get_default_resolver
from promise import Promise

from ...zones import models
from ..zones.dataloaders import ZoneWithHasOrdersByIdLoader
from ..accounts.enums import CountryCodeEnum
from ..core.fields import PermissionsField

from ..core.types import CountryDisplay, ModelObjectType, NonNullList
from ..meta.types import ObjectWithMetadata
from . import ZoneContext


class ZoneContextTypeForObjectType(graphene.ObjectType):
    """A Graphene type that supports resolvers' root as ChannelContext objects."""

    class Meta:
        abstract = True

    @staticmethod
    def resolver_with_context(
        attname, default_value, root: ZoneContext, info, **args
    ):
        resolver = get_default_resolver()
        return resolver(attname, default_value, root.node, info, **args)

    @staticmethod
    def resolve_id(root: ZoneContext, _info):
        return root.node.pk


class ZoneContextType(ZoneContextTypeForObjectType, ModelObjectType):
    """A Graphene type that supports resolvers' root as ChannelContext objects."""

    class Meta:
        abstract = True

    @classmethod
    def is_type_of(cls, root: Union[ZoneContext, Model], _info):
        # Unwrap node from ChannelContext if it didn't happen already
        if isinstance(root, ZoneContext):
            root = cast(Model, root.node)

        if isinstance(root, cls):
            return True

        if cls._meta.model._meta.proxy:
            model = root._meta.model
        else:
            model = cast(Type[Model], root._meta.model._meta.concrete_model)

        return model == cls._meta.model


class ZoneContextTypeWithMetadataForObjectType(ZoneContextTypeForObjectType):
    """A Graphene type for that uses ChannelContext as root in resolvers.

    Same as ChannelContextType, but for types that implement ObjectWithMetadata
    interface.
    """

    class Meta:
        abstract = True

    @staticmethod
    def resolve_metadata(root: ZoneContext, info):
        # Used in metadata API to resolve metadata fields from an instance.
        return ObjectWithMetadata.resolve_metadata(root.node, info)

    @staticmethod
    def resolve_metafield(root: ZoneContext, info, *, key: str):
        # Used in metadata API to resolve metadata fields from an instance.
        return ObjectWithMetadata.resolve_metafield(root.node, info, key=key)

    @staticmethod
    def resolve_metafields(root: ZoneContext, info, *, keys=None):
        # Used in metadata API to resolve metadata fields from an instance.
        return ObjectWithMetadata.resolve_metafields(root.node, info, keys=keys)

    @staticmethod
    def resolve_private_metadata(root: ZoneContext, info):
        # Used in metadata API to resolve private metadata fields from an instance.
        return ObjectWithMetadata.resolve_private_metadata(root.node, info)

    @staticmethod
    def resolve_private_metafield(root: ZoneContext, info, *, key: str):
        # Used in metadata API to resolve private metadata fields from an instance.
        return ObjectWithMetadata.resolve_private_metafield(root.node, info, key=key)

    @staticmethod
    def resolve_private_metafields(root: ZoneContext, info, *, keys=None):
        # Used in metadata API to resolve private metadata fields from an instance.
        return ObjectWithMetadata.resolve_private_metafields(root.node, info, keys=keys)


class ZoneContextTypeWithMetadata(
    ZoneContextTypeWithMetadataForObjectType, ZoneContextType
):
    """A Graphene type for that uses ZoneContext as root in resolvers.
    Same as ZoneContextType, but for types that implement ObjectWithMetadata
    interface.
    """
    class Meta:
        abstract = True


class Zone(ModelObjectType):
    id = graphene.GlobalID(required=True)
    slug = graphene.String(
        required=True,
        description="Slug of the zone.",
    )

    name = PermissionsField(
        graphene.String,
        description="Name of the zone.",
        required=True,
    )
    is_active = PermissionsField(
        graphene.Boolean,
        description="Whether the zone is active.",
        required=True,
        # TODO: add the active permissions
    )
    currency_code = PermissionsField(
        graphene.String,
        description="A currency that is assigned to the zone.",
        required=True,
    )
    has_orders = PermissionsField(
        graphene.Boolean,
        description="Whether a zone has associated orders.",
        required=True,
    )
    default_country = PermissionsField(
        CountryDisplay,
        description=(
            "Default country for the zone. Default country can be "
            "used in checkout to determine the stock quantities or calculate taxes "
        ),
        required=True,
    )
    countries = NonNullList(
        CountryDisplay,
        description="List of shippable countries for the zone."
    )

    available_shipping_methods_per_country = graphene.Field(
        NonNullList("saleor.graphql.shipping.types.ShippingMethodsPerCountry"),
        countries=graphene.Argument(NonNullList(CountryCodeEnum)),
        description="Shipping methods that are available for the zone."

    )

    class Meta:
        description = "Represents zone."
        model = models.Zone
        interfaces = [graphene.relay.Node]

    @staticmethod
    def resolve_has_orders(root: models.Zone, info):
        return (

            ZoneWithHasOrdersByIdLoader(info.context)
            .load(root.id)
            .then(lambda zone: zone.has_orders)

        )

    @staticmethod
    def resolve_default_country(root: models.Zone, _info):
        return CountryDisplay(
            code=root.default_country.code, country=root.default_country.name
        )

    @staticmethod
    def resolve_countries(root: models.Zone, info):
        from ..shipping.dataloaders import ShippingZonesByZoneIdLoader

        def get_countries(shipping_zones):
            countries = []
            for s_zone in shipping_zones:
                countries.extend(s_zone.countries)
            sorted_countries = list(set(countries))
            sorted_countries.sort(key=lambda country: country.name)
            return [
                CountryDisplay(code=country.code, country=country.name)
                for country in sorted_countries
            ]

        return (
            ShippingZonesByZoneIdLoader(info.context)
            .load(root.id)
            .then(get_countries)
        )

    @staticmethod
    def resolve_available_shipping_methods_per_country(
        root: models.Zone, info, **data
    ):
        from ...shipping.utils import convert_to_shipping_method_data
        from ..shipping.dataloaders import (
            ShippingMethodsByShippingZoneIdLoader,
            ShippingZonesByZoneIdLoader,
        )

        shipping_zones_loader = ShippingZonesByZoneIdLoader(info.context).load(
            root.id
        )
        shipping_zone_countries: Dict[int, List[str]] = collections.defaultdict(list)
        requested_countries = data.get("countries", [])

        def _group_shipping_methods_by_country(data):
            shipping_methods, shipping_channel_listings = data
            shipping_listing_map = {
                listing.shipping_method_id: listing
                for listing in shipping_channel_listings
            }

            shipping_methods_per_country = collections.defaultdict(list)
            for shipping_method in shipping_methods:
                countries = shipping_zone_countries.get(
                    shipping_method.shipping_zone_id, []
                )
                for country in countries:
                    shipping_method_dataclass = convert_to_shipping_method_data(
                        shipping_method, shipping_listing_map.get(shipping_method.id)
                    )
                    if not shipping_method_dataclass:
                        continue
                    shipping_methods_per_country[country.code].append(
                        shipping_method_dataclass
                    )

            if requested_countries:
                results = [
                    {
                        "country_code": code,
                        "shipping_methods": shipping_methods_per_country.get(code, []),
                    }
                    for code in requested_countries
                    if code in shipping_methods_per_country
                ]
            else:
                results = [
                    {
                        "country_code": code,
                        "shipping_methods": shipping_methods_per_country[code],
                    }
                    for code in shipping_methods_per_country.keys()
                ]
            results.sort(key=lambda item: item["country_code"])

            return results

        def filter_shipping_methods(shipping_methods):
            shipping_methods = list(itertools.chain.from_iterable(shipping_methods))
            return Promise.all([shipping_methods]).then(
                _group_shipping_methods_by_country
            )

        def get_shipping_methods(shipping_zones):
            shipping_zones_keys = [shipping_zone.id for shipping_zone in shipping_zones]
            for shipping_zone in shipping_zones:
                shipping_zone_countries[shipping_zone.id] = shipping_zone.countries

            return (
                ShippingMethodsByShippingZoneIdLoader(info.context)
                .load_many(shipping_zones_keys)
                .then(filter_shipping_methods)
            )

        return shipping_zones_loader.then(get_shipping_methods)
