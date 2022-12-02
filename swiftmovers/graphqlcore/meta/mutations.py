import logging
from typing import List

import graphene
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db import DatabaseError
from graphql.error.base import GraphQLError

from ...checkouts import models as checkout_models
from ...core import models
from ...core.error_codes import MetadataErrorCode
from ...orders import models as order_models
from ...items import models as product_models
from ...shipping import models as shipping_models
from ..zones import ZoneContext
from ..core.mutations.base import BaseMutation
from ..core.types import MetadataError, NonNullList
from ..core.utils import from_global_id_or_error
from ..payments.utils import metadata_contains_empty_key


from .types import ObjectWithMetadata

logger = logging.getLogger(__name__)


def _save_instance(instance, metadata_field: str):
    fields = [metadata_field]

    try:
        if bool(instance._meta.get_field("updated_at")):
            fields.append("updated_at")
    except FieldDoesNotExist:
        pass

    try:
        instance.save(update_fields=fields)
    except DatabaseError as e:
        msg = (
            "Cannot update metadata for instance: %s. "
            "Updating not existing object. "
            "Details: %s.",
            instance,
            str(e),
        )
        logger.warning(msg)
        raise ValidationError(
            {
                "metadata": ValidationError(
                    msg,
                    code=MetadataErrorCode.NOT_FOUND.value,
                )
            }
        )


class MetadataPermissionOptions(graphene.types.mutation.MutationOptions):
    permission_map = {}


class BaseMetadataMutation(BaseMutation):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        arguments=None,
        permission_map=[],
        _meta=None,
        **kwargs,
    ):
        if not _meta:
            _meta = MetadataPermissionOptions(cls)
        if not arguments:
            arguments = {}
        fields = {"item": graphene.Field(ObjectWithMetadata)}

        _meta.permission_map = permission_map

        super().__init_subclass_with_meta__(_meta=_meta, **kwargs)
        cls._update_mutation_arguments_and_fields(arguments=arguments, fields=fields)

    @classmethod
    def get_instance(cls, info, **data):
        object_id = data.get("id")
        qs = data.get("qs", None)

        try:
            type_name, _ = from_global_id_or_error(object_id)
            # ShippingMethodType represents the ShippingMethod model
            if type_name == "ShippingMethodType":
                qs = shipping_models.ShippingMethod.objects

            return cls.get_node_or_error(info, object_id, qs=qs)
        except GraphQLError as e:
            if instance := cls.get_instance_by_token(object_id, qs):
                return instance
            raise ValidationError(
                {
                    "id": ValidationError(
                        str(e), code=MetadataErrorCode.GRAPHQL_ERROR.value
                    )
                }
            )

    @classmethod
    def get_instance_by_token(cls, object_id, qs):
        if not qs:
            if order := order_models.Order.objects.filter(id=object_id).first():
                return order
            if checkout := checkout_models.DeliveryCheckout.objects.filter(
                token=object_id
            ).first():
                return checkout
            return None
        if qs and "token" in [field.name for field in qs.model._meta.get_fields()]:
            return qs.filter(token=object_id).first()

    @classmethod
    def validate_model_is_model_with_metadata(cls, model, object_id):
        if not issubclass(model, models.ModelWithMetadata):
            raise ValidationError(
                {
                    "id": ValidationError(
                        f"Couldn't resolve to a item with meta: {object_id}",
                        code=MetadataErrorCode.NOT_FOUND.value,
                    )
                }
            )

    @classmethod
    def validate_metadata_keys(cls, metadata_list: List[dict]):
        if metadata_contains_empty_key(metadata_list):
            raise ValidationError(
                {
                    "input": ValidationError(
                        "Metadata key cannot be empty.",
                        code=MetadataErrorCode.REQUIRED.value,
                    )
                }
            )

    @classmethod
    def get_model_for_type_name(cls, info, type_name):
        if type_name in ["ShippingMethodType", "ShippingMethod"]:
            return shipping_models.ShippingMethod

        graphene_type = info.schema.get_type(type_name).graphene_type

        if hasattr(graphene_type, "get_model"):
            return graphene_type.get_model()

        return graphene_type._meta.model

    @classmethod
    def mutate(cls, root, info, **data):
        try:
            type_name, object_pk = cls.get_object_type_name_and_pk(data)

        except GraphQLError as e:
            error = ValidationError(
                {"id": ValidationError(str(e), code="graphql_error")}
            )
            return cls.handle_errors(error)
        except ValidationError as e:
            return cls.handle_errors(e)

        try:
            result = super().mutate(root, info, **data)
            if not result.errors:
                cls.perform_model_extra_actions(root, info, type_name, **data)
        except ValidationError as e:
            return cls.handle_errors(e)
        return result

    @classmethod
    def get_object_type_name_and_pk(cls, data):
        object_id = data.get("id")
        if not object_id:
            return None, None
        try:
            return from_global_id_or_error(object_id)
        except GraphQLError:
            if order := order_models.Order.objects.filter(id=object_id).first():
                return "Order", order.pk
            if checkout := checkout_models.DeliveryCheckout.objects.filter(
                token=object_id
            ).first():
                return "Checkout", checkout.pk
            raise ValidationError(
                {
                    "id": ValidationError(
                        "Couldn't resolve to a node.", code="graphql_error"
                    )
                }
            )

    @classmethod
    def success_response(cls, instance):
        """Return a success response."""
        # Wrap the instance with ChannelContext for models that use it.
        use_zone_context = any(
            [
                isinstance(instance, Model)
                for Model in [

                    product_models.ProductTypeKind,
                    product_models.Product,
                    product_models.ProductType,
                    shipping_models.ShippingMethod,
                    shipping_models.ShippingZone,
                ]
            ]
        )
        if use_zone_context:
            instance = ZoneContext(node=instance, zone_slug=None)
        return cls(**{"item": instance, "errors": []})


class MetadataInput(graphene.InputObjectType):
    key = graphene.String(required=True, description="Key of a metadata item.")
    value = graphene.String(required=True, description="Value of a metadata item.")


class UpdateMetadata(BaseMetadataMutation):
    class Meta:
        description = (
            "Updates metadata of an object. To use it, you need to have access to the "
            "modified object."
        )
        error_type_class = MetadataError
        error_type_field = "metadata_errors"

    class Arguments:
        id = graphene.ID(
            description="ID or token (for Order and Checkout) of an object to update.",
            required=True,
        )
        input = NonNullList(
            MetadataInput,
            description="Fields required to update the object's metadata.",
            required=True,
        )

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        instance = cls.get_instance(info, **data)
        if instance:
            metadata_list = data.pop("input")
            cls.validate_metadata_keys(metadata_list)
            items = {data.key: data.value for data in metadata_list}
            instance.store_value_in_metadata(items=items)
            _save_instance(instance, "metadata")

        return cls.success_response(instance)


class DeleteMetadata(BaseMetadataMutation):
    class Meta:
        description = (
            "Delete metadata of an object. To use it, you need to have access to the "
            "modified object."
        )
        error_type_class = MetadataError
        error_type_field = "metadata_errors"

    class Arguments:
        id = graphene.ID(
            description="ID or token (for Order and Checkout) of an object to update.",
            required=True,
        )
        keys = NonNullList(
            graphene.String,
            description="Metadata keys to delete.",
            required=True,
        )

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        instance = cls.get_instance(info, **data)
        if instance:
            metadata_keys = data.pop("keys")
            for key in metadata_keys:
                instance.delete_value_from_metadata(key)
            _save_instance(instance, "metadata")
        return cls.success_response(instance)


class UpdatePrivateMetadata(BaseMetadataMutation):
    class Meta:
        description = (
            "Updates private metadata of an object. To use it, you need to be an "
            "authenticated staff user or an app and have access to the modified object."
        )
        error_type_class = MetadataError
        error_type_field = "metadata_errors"

    class Arguments:
        id = graphene.ID(
            description="ID or token (for Order and Checkout) of an object to update.",
            required=True,
        )
        input = NonNullList(
            MetadataInput,
            description="Fields required to update the object's metadata.",
            required=True,
        )

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        instance = cls.get_instance(info, **data)
        if instance:
            metadata_list = data.pop("input")
            cls.validate_metadata_keys(metadata_list)
            items = {data.key: data.value for data in metadata_list}
            instance.store_value_in_private_metadata(items=items)
            _save_instance(instance, "private_metadata")
        return cls.success_response(instance)


class DeletePrivateMetadata(BaseMetadataMutation):
    class Meta:
        description = (
            "Delete object's private metadata. To use it, you need to be an "
            "authenticated staff user or an app and have access to the modified object."
        )
        error_type_class = MetadataError
        error_type_field = "metadata_errors"

    class Arguments:
        id = graphene.ID(
            description="ID or token (for Order and Checkout) of an object to update.",
            required=True,
        )
        keys = NonNullList(
            graphene.String,
            description="Metadata keys to delete.",
            required=True,
        )

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        instance = cls.get_instance(info, **data)
        if instance:
            metadata_keys = data.pop("keys")
            for key in metadata_keys:
                instance.delete_value_from_private_metadata(key)
            _save_instance(instance, "private_metadata")
        return cls.success_response(instance)
