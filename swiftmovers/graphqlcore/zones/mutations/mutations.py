import datetime
from typing import DefaultDict, Dict, Iterable, List

import graphene
import pytz
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from ....zones import models
from ....checkouts.models import DeliveryCheckout
from ....core.tracing import traced_atomic_transaction
from ...core.utils.date_time import convert_to_utc_date_time
from ....orders.models import Order
from ...shipping.tasks import drop_invalid_shipping_methods_relations_for_given_channels
from ...accounts.enums import CountryCodeEnum
from ...core.mutations.base import BaseMutation, ModelMutation, ModelDeleteMutation
from ...core.types import ZoneError, ZoneErrorCode, NonNullList
from ...core.utils import get_duplicated_values, get_duplicates_items
from ..utils.validators import check_for_duplicates
from ..types import Zone
from .utils import delete_invalid_warehouse_to_shipping_zone_relations


class ZoneInput(graphene.InputObjectType):
    is_active = graphene.Boolean(description="isActive flag.")
    add_shipping_local_area = NonNullList(
        graphene.ID,
        description="List of shipping local area to assign to the zone.",
        required=False,
    )
    # TODO: add warehouse and storage options


class ZoneCreateInput(ZoneInput):
    name = graphene.String(description="Name of the zone.", required=True)
    slug = graphene.String(description="Slug of the zone.", required=True)
    currency_code = graphene.String(
        description="Currency of the zone.", required=True
    )
    default_country = CountryCodeEnum(
        description=(
            "Default country for the zone. Default country can be "
        ),
        required=True,
    )


class ZoneCreate(ModelMutation):
    class Arguments:
        input = ZoneCreateInput(
            required=True, description="Fields required to create channel."
        )

    class Meta:
        description = "Creates new Zone."
        model = models.Zone
        object_type = Zone
        error_type_class = ZoneError
        error_type_field = "zone_errors"

    @classmethod
    def get_type_for_model(cls):
        return Zone

    @classmethod
    def clean_input(cls, info, instance, data, input_cls=None):
        cleaned_input = super().clean_input(info, instance, data)
        slug = cleaned_input.get("slug")
        if slug:
            cleaned_input["slug"] = slugify(slug)

        return cleaned_input

    @classmethod
    @traced_atomic_transaction()
    def _save_m2m(cls, info, instance, cleaned_data):
        super()._save_m2m(info, instance, cleaned_data)
        shipping_local_areas = cleaned_data.get("add_shipping_local_area")
        if shipping_local_areas:
            instance.shipping_zones.add(*shipping_local_areas)
        warehouses = cleaned_data.get("add_warehouses")
        if warehouses:
            instance.warehouses.add(*warehouses)

    @classmethod
    def post_save_action(cls, info, instance, cleaned_input):
        info.context.plugins.channel_created(instance)


class ZoneUpdateInput(ZoneInput):
    name = graphene.String(description="Name of the channel.")
    slug = graphene.String(description="Slug of the channel.")
    default_country = CountryCodeEnum(
        description=(
            "Default country for the channel. Default country can be "
        )
    )
    remove_shipping_local_areas = NonNullList(
        graphene.ID,
        description="List of shipping zones to unassign from the zone.",
        required=False,
    )


class ZoneUpdate(ModelMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of a zone to update.")
        input = ZoneUpdateInput(
            description="Fields required to update a zone.", required=True
        )

    class Meta:
        description = "Update a Zone."
        model = models.Zone
        object_type = Zone
        error_type_class = ZoneError
        error_type_field = "Zone_errors"

    @classmethod
    def clean_input(cls, info, instance, data, input_cls=None):
        errors = {}
        if error := check_for_duplicates(
                data, "add_shipping_zones", "remove_shipping_zones", "shipping_zones"
        ):
            error.code = ZoneErrorCode.DUPLICATED_INPUT_ITEM.value
            errors["shipping_zones"] = error

        if error := check_for_duplicates(
                data, "add_warehouses", "remove_warehouses", "warehouses"
        ):
            error.code = ZoneErrorCode.DUPLICATED_INPUT_ITEM.value
            errors["warehouses"] = error

        if errors:
            raise ValidationError(errors)

        cleaned_input = super().clean_input(info, instance, data)
        slug = cleaned_input.get("slug")
        if slug:
            cleaned_input["slug"] = slugify(slug)

        return cleaned_input

    @classmethod
    @traced_atomic_transaction()
    def _save_m2m(cls, info, instance, cleaned_data):
        super()._save_m2m(info, instance, cleaned_data)
        cls._update_shipping_local_areas(instance, cleaned_data)
        cls._update_warehouses(instance, cleaned_data)
        if (
                "remove_shipping_zones" in cleaned_data
                or "remove_warehouses" in cleaned_data
        ):
            shipping_local_area_ids = [
                warehouse.id
                for warehouse in cleaned_data.get("remove_shipping_local_areas", [])
            ]
            delete_invalid_warehouse_to_shipping_zone_relations(
                instance, shipping_local_area_ids
            )

    @classmethod
    def _update_shipping_local_areas(cls, instance, cleaned_data):
        add_shipping_local_area = cleaned_data.get("add_shipping_local_area")
        if add_shipping_local_area:
            instance.shipping_zones.add(*add_shipping_local_area)
        remove_shipping_local_area = cleaned_data.get("remove_shipping_local_area")
        if remove_shipping_local_area:
            instance.shipping_zones.remove(*remove_shipping_local_area)
            shipping_channel_listings = instance.shipping_method_listings.filter(
                shipping_method__shipping_zone__in=remove_shipping_local_area
            )
            shipping_method_ids = list(
                shipping_channel_listings.values_list("shipping_method_id", flat=True)
            )
            shipping_channel_listings.delete()
            drop_invalid_shipping_methods_relations_for_given_channels.delay(
                shipping_method_ids, [instance.id]
            )

    @classmethod
    def post_save_action(cls, info, instance, cleaned_input):
        info.context.plugins.zone_updated(instance)


class ZoneDeleteInput(graphene.InputObjectType):
    channel_id = graphene.ID(
        required=True,
        description="ID of channel to migrate orders from origin channel.",
    )


class ZoneDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of a zone to delete.")
        input = ZoneDeleteInput(description="Fields required to delete a zone.")

    class Meta:
        description = (
            "Delete a zone. Orders associated with the deleted "
        )
        model = models.Zone
        object_type = Zone

        error_type_class = ZoneError
        error_type_field = "zone_errors"

    @classmethod
    def validate_input(cls, origin_zone, target_zone):
        if origin_zone.id == target_zone.id:
            raise ValidationError(
                {
                    "zone_id": ValidationError(
                        "Cannot migrate data to the channel that is being removed.",
                        code=ZoneErrorCode.INVALID,
                    )
                }
            )
        origin_zone_currency = origin_zone.currency_code
        target_zone_currency = target_zone.currency_code
        if origin_zone_currency != target_zone_currency:
            raise ValidationError(
                {
                    "channel_id": ValidationError(
                        f"Cannot migrate from {origin_zone_currency} "
                        f"to {target_zone_currency}. "
                        "Migration are allowed between the same currency",
                        code=ZoneErrorCode.CHANNELS_CURRENCY_MUST_BE_THE_SAME,
                    )
                }
            )

    @classmethod
    def migrate_orders_to_target_channel(cls, origin_channel_id, target_channel_id):
        Order.objects.select_for_update().filter(channel_id=origin_channel_id).update(
            channel=target_channel_id
        )

    @classmethod
    def delete_checkouts(cls, origin_zone_id):
        DeliveryCheckout.objects.select_for_update().filter(
            channel_id=origin_zone_id
        ).delete()

    @classmethod
    def perform_delete_with_order_migration(cls, origin_zone, target_zone):
        cls.validate_input(origin_zone, target_zone)

        with traced_atomic_transaction():
            origin_zone_id = origin_zone.id
            cls.delete_checkouts(origin_zone_id)
            cls.migrate_orders_to_target_channel(origin_zone_id, target_zone.id)

    @classmethod
    def perform_delete_channel_without_order(cls, origin_channel):
        if Order.objects.filter(channel=origin_channel).exists():
            raise ValidationError(
                {
                    "id": ValidationError(
                        "Cannot remove channel with orders. Try to migrate orders to "
                        "another channel by passing `targetChannel` param.",
                        code=ZoneErrorCode.CHANNEL_WITH_ORDERS,
                    )
                }
            )
        cls.delete_checkouts(origin_channel.id)

    @classmethod
    def post_save_action(cls, info, instance, cleaned_input):
        info.context.plugins.channel_deleted(instance)

    @classmethod
    @traced_atomic_transaction()
    def perform_mutation(cls, _root, info, **data):
        origin_zone = cls.get_node_or_error(info, data["id"], only_type=Zone)
        target_zone_global_id = data.get("input", {}).get("channel_id")
        if target_zone_global_id:
            target_zone = cls.get_node_or_error(
                info, target_channel_global_id, only_type=Channel
            )
            cls.perform_delete_with_order_migration(origin_zone, target_channel)
        else:
            cls.perform_delete_channel_without_order(origin_zone)
        delete_invalid_warehouse_to_shipping_zone_relations(
            origin_zone,
            origin_zone.warehouses.values("id"),
            channel_deletion=True,
        )
        return super().perform_mutation(_root, info, **data)


ErrorType = DefaultDict[str, List[ValidationError]]


class BaseChannelListingMutation(BaseMutation):
    """Base channel listing mutation with basic channel validation."""

    class Meta:
        abstract = True

    @classmethod
    def validate_duplicated_channel_ids(
            cls,
            add_channels_ids: Iterable[str],
            remove_channels_ids: Iterable[str],
            errors: ErrorType,
            error_code,
    ):
        duplicated_ids = get_duplicates_items(add_channels_ids, remove_channels_ids)
        if duplicated_ids:
            error_msg = (
                "The same object cannot be in both lists "
                "for adding and removing items."
            )
            errors["input"].append(
                ValidationError(
                    error_msg,
                    code=error_code,
                    params={"zones": list(duplicated_ids)},
                )
            )

    @classmethod
    def validate_duplicated_channel_values(
            cls, channels_ids: Iterable[str], field_name: str, errors: ErrorType, error_code
    ):
        duplicates = get_duplicated_values(channels_ids)
        if duplicates:
            errors[field_name].append(
                ValidationError(
                    "Duplicated channel ID.",
                    code=error_code,
                    params={"channels": duplicates},
                )
            )

    @classmethod
    def clean_channels(
            cls, info, input, errors: ErrorType, error_code, input_source="add_zones"
    ) -> Dict:
        add_channels = input.get(input_source, [])
        add_channels_ids = [channel["channel_id"] for channel in add_channels]
        remove_channels_ids = input.get("remove_channels", [])
        cls.validate_duplicated_channel_ids(
            add_channels_ids, remove_channels_ids, errors, error_code
        )
        cls.validate_duplicated_channel_values(
            add_channels_ids, input_source, errors, error_code
        )
        cls.validate_duplicated_channel_values(
            remove_channels_ids, "remove_channels", errors, error_code
        )

        if errors:
            return {}
        channels_to_add: List["models.Zone"] = []
        if add_channels_ids:
            channels_to_add = cls.get_nodes_or_error(  # type: ignore
                add_zones_ids, "channel_id", Zone)
        remove_channels_pks = cls.get_global_ids_or_error(
            remove_channels_ids, Zone, field="remove_channels"
        )

        cleaned_input = {input_source: [], "remove_channels": remove_channels_pks}

        for channel_listing, channel in zip(add_channels, channels_to_add):
            channel_listing["channel"] = channel
            cleaned_input[input_source].append(channel_listing)

        return cleaned_input

    @classmethod
    def clean_publication_date(
            cls, errors, error_code_enum, cleaned_input, input_source="add_channels"
    ):
        invalid_channels = []
        for add_channel in cleaned_input.get(input_source, []):
            # should update errors dict
            if "publication_date" in add_channel and "published_at" in add_channel:
                invalid_channels.append(add_channel["channel_id"])
                continue
            publication_date = add_channel.get("publication_date")
            publication_date = (
                convert_to_utc_date_time(publication_date)
                if publication_date
                else add_channel.get("published_at")
            )
            is_published = add_channel.get("is_published")
            if is_published and not publication_date:
                add_channel["published_at"] = datetime.datetime.now(pytz.UTC)
            elif "publication_date" in add_channel or "published_at" in add_channel:
                add_channel["published_at"] = publication_date
        if invalid_channels:
            error_msg = (
                "Only one of argument: publicationDate or publishedAt "
                "must be specified."
            )
            errors["publication_date"].append(
                ValidationError(
                    error_msg,
                    code=error_code_enum.INVALID.value,
                    params={"channels": invalid_channels},
                )
            )


class ZoneActivate(BaseMutation):
    channel = graphene.Field(Zone, description="Activated channel.")

    class Arguments:
        id = graphene.ID(required=True, description="ID of the channel to activate.")

    class Meta:
        description = "Activate a channel."
        error_type_class = ChannelError
        error_type_field = "channel_errors"

    @classmethod
    def clean_channel_availability(cls, channel):
        if channel.is_active:
            raise ValidationError(
                {
                    "id": ValidationError(
                        "This channel is already activated.",
                        code=ZoneErrorCode.INVALID,
                    )
                }
            )

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        zone = cls.get_node_or_error(info, data["id"], only_type=Zone)
        cls.clean_channel_availability(zone)
        zone.is_active = True
        zone.save(update_fields=["is_active"])
        info.context.plugins.channel_status_changed(zone)
        return ZoneActivate(zone=zone)


class ZoneDeactivate(BaseMutation):
    zone = graphene.Field(Zone, description="Deactivated channel.")

    class Arguments:
        id = graphene.ID(required=True, description="ID of the zone to deactivate.")

    class Meta:
        description = "Deactivate a Zone."
        error_type_class = ZoneError
        error_type_field = "Zone_errors"

    @classmethod
    def clean_zone_availability(cls, zone):
        if zone.is_active is False:
            raise ValidationError(
                {
                    "id": ValidationError(
                        "This zone is already deactivated.",
                        code=ZoneErrorCode.INVALID,
                    )
                }
            )

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        zone = cls.get_node_or_error(info, data["id"], only_type=Zone)
        cls.clean_channel_availability(zone)
        zone.is_active = False
        zone.save(update_fields=["is_active"])
        info.context.plugins.channel_status_changed(zone)
        return ZoneDeactivate(channel=zone)
