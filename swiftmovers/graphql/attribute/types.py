from typing import cast

import graphene
from django.db.models import QuerySet

from ...attribute import AttributeInputType, models
from ...permission.enums import (
    PagePermissions,
    PageTypePermissions,
    ProductPermissions,
    ProductTypePermissions,
)
from ..core import ResolveInfo
from ..core.connection import (
    CountableConnection,
    create_connection_slice,
    filter_connection_queryset,
)
from ..core.descriptions import (
    ADDED_IN_31,
    ADDED_IN_39,
    ADDED_IN_310,
    DEPRECATED_IN_3X_FIELD,
)
from ..core.doc_category import DOC_CATEGORY_ATTRIBUTES
from ..core.enums import MeasurementUnitsEnum
from ..core.fields import ConnectionField, FilterConnectionField, JSONString
from ..core.scalars import Date
from ..core.types import (
    BaseInputObjectType,
    BaseObjectType,
    DateRangeInput,
    DateTimeRangeInput,
    File,
    IntRangeInput,
    ModelObjectType,
    NonNullList,
)
from ..decorators import check_attribute_required_permissions
from ..meta.types import ObjectWithMetadata
from ..translations.fields import TranslationField
from ..translations.types import AttributeTranslation, AttributeValueTranslation
from .dataloaders import AttributesByAttributeId
from .descriptions import AttributeDescriptions, AttributeValueDescriptions
from .enums import AttributeEntityTypeEnum, AttributeInputTypeEnum, AttributeTypeEnum
from .filters import AttributeValueFilterInput
from .sorters import AttributeChoicesSortingInput
from .utils import AttributeAssignmentMixin


class AttributeValue(ModelObjectType[models.AttributeValue]):
    id = graphene.GlobalID(required=True)
    name = graphene.String(description=AttributeValueDescriptions.NAME)
    slug = graphene.String(description=AttributeValueDescriptions.SLUG)
    value = graphene.String(description=AttributeValueDescriptions.VALUE)
    translation = TranslationField(
        AttributeValueTranslation, type_name="attribute value"
    )
    input_type = AttributeInputTypeEnum(description=AttributeDescriptions.INPUT_TYPE)
    reference = graphene.ID(description="The ID of the attribute reference.")
    file = graphene.Field(
        File, description=AttributeValueDescriptions.FILE, required=False
    )
    rich_text = JSONString(
        description=AttributeValueDescriptions.RICH_TEXT, required=False
    )
    plain_text = graphene.String(
        description=AttributeValueDescriptions.PLAIN_TEXT, required=False
    )
    boolean = graphene.Boolean(
        description=AttributeValueDescriptions.BOOLEAN, required=False
    )
    date = Date(description=AttributeValueDescriptions.DATE, required=False)
    date_time = graphene.DateTime(
        description=AttributeValueDescriptions.DATE_TIME, required=False
    )
    external_reference = graphene.String(
        description=f"External ID of this attribute value. {ADDED_IN_310}",
        required=False,
    )

    class Meta:
        description = "Represents a value of an attribute."
        interfaces = [graphene.relay.Node]
        model = models.AttributeValue

    @staticmethod
    def resolve_input_type(root: models.AttributeValue, info: ResolveInfo):
        return (
            AttributesByAttributeId(info.context)
            .load(root.attribute_id)
            .then(lambda attribute: attribute.input_type)
        )

    @staticmethod
    def resolve_file(root: models.AttributeValue, _info: ResolveInfo):
        if not root.file_url:
            return
        return File(url=root.file_url, content_type=root.content_type)

    @staticmethod
    def resolve_reference(root: models.AttributeValue, info: ResolveInfo):
        def prepare_reference(attribute):
            if attribute.input_type != AttributeInputType.REFERENCE:
                return
            reference_field = AttributeAssignmentMixin.ENTITY_TYPE_MAPPING[
                attribute.entity_type
            ].value_field
            reference_pk = getattr(root, f"{reference_field}_id", None)
            if reference_pk is None:
                return
            reference_id = graphene.Node.to_global_id(
                attribute.entity_type, reference_pk
            )
            return reference_id

        return (
            AttributesByAttributeId(info.context)
            .load(root.attribute_id)
            .then(prepare_reference)
        )

    @staticmethod
    def resolve_date_time(root: models.AttributeValue, info: ResolveInfo):
        def _resolve_date(attribute):
            if attribute.input_type == AttributeInputType.DATE_TIME:
                return root.date_time
            return None

        return (
            AttributesByAttributeId(info.context)
            .load(root.attribute_id)
            .then(_resolve_date)
        )

    @staticmethod
    def resolve_date(root: models.AttributeValue, info: ResolveInfo):
        def _resolve_date(attribute):
            if attribute.input_type == AttributeInputType.DATE:
                return root.date_time
            return None

        return (
            AttributesByAttributeId(info.context)
            .load(root.attribute_id)
            .then(_resolve_date)
        )


class AttributeValueCountableConnection(CountableConnection):
    class Meta:
        doc_category = DOC_CATEGORY_ATTRIBUTES
        node = AttributeValue


class Attribute(ModelObjectType[models.Attribute]):
    id = graphene.GlobalID(required=True)
    input_type = AttributeInputTypeEnum(description=AttributeDescriptions.INPUT_TYPE)
    entity_type = AttributeEntityTypeEnum(
        description=AttributeDescriptions.ENTITY_TYPE, required=False
    )

    name = graphene.String(description=AttributeDescriptions.NAME)
    slug = graphene.String(description=AttributeDescriptions.SLUG)
    type = AttributeTypeEnum(description=AttributeDescriptions.TYPE)
    unit = MeasurementUnitsEnum(description=AttributeDescriptions.UNIT)
    choices = FilterConnectionField(
        AttributeValueCountableConnection,
        sort_by=AttributeChoicesSortingInput(description="Sort attribute choices."),
        filter=AttributeValueFilterInput(
            description="Filtering options for attribute choices."
        ),
        description=AttributeDescriptions.VALUES,
    )

    value_required = graphene.Boolean(
        description=(
            f"{AttributeDescriptions.VALUE_REQUIRED} Requires one of the following "
            f"permissions: {PagePermissions.MANAGE_PAGES.name}, "
            f"{PageTypePermissions.MANAGE_PAGE_TYPES_AND_ATTRIBUTES.name}, "
            f"{ProductPermissions.MANAGE_PRODUCTS.name}, "
            f"{ProductTypePermissions.MANAGE_PRODUCT_TYPES_AND_ATTRIBUTES.name}."
        ),
        required=True,
    )
    visible_in_storefront = graphene.Boolean(
        description=(
            f"{AttributeDescriptions.VISIBLE_IN_STOREFRONT} Requires one of the "
            f"following permissions: {PagePermissions.MANAGE_PAGES.name}, "
            f"{PageTypePermissions.MANAGE_PAGE_TYPES_AND_ATTRIBUTES.name}, "
            f"{ProductPermissions.MANAGE_PRODUCTS.name}, "
            f"{ProductTypePermissions.MANAGE_PRODUCT_TYPES_AND_ATTRIBUTES.name}."
        ),
        required=True,
    )
    filterable_in_storefront = graphene.Boolean(
        description=(
            f"{AttributeDescriptions.FILTERABLE_IN_STOREFRONT} Requires one of the "
            f"following permissions: {PagePermissions.MANAGE_PAGES.name}, "
            f"{PageTypePermissions.MANAGE_PAGE_TYPES_AND_ATTRIBUTES.name}, "
            f"{ProductPermissions.MANAGE_PRODUCTS.name}, "
            f"{ProductTypePermissions.MANAGE_PRODUCT_TYPES_AND_ATTRIBUTES.name}."
        ),
        required=True,
        deprecation_reason=DEPRECATED_IN_3X_FIELD,
    )
    filterable_in_dashboard = graphene.Boolean(
        description=(
            f"{AttributeDescriptions.FILTERABLE_IN_DASHBOARD} Requires one of the "
            f"following permissions: {PagePermissions.MANAGE_PAGES.name}, "
            f"{PageTypePermissions.MANAGE_PAGE_TYPES_AND_ATTRIBUTES.name}, "
            f"{ProductPermissions.MANAGE_PRODUCTS.name}, "
            f"{ProductTypePermissions.MANAGE_PRODUCT_TYPES_AND_ATTRIBUTES.name}."
        ),
        required=True,
    )
    available_in_grid = graphene.Boolean(
        description=(
            f"{AttributeDescriptions.AVAILABLE_IN_GRID} Requires one of the following "
            f"permissions: {PagePermissions.MANAGE_PAGES.name}, "
            f"{PageTypePermissions.MANAGE_PAGE_TYPES_AND_ATTRIBUTES.name}, "
            f"{ProductPermissions.MANAGE_PRODUCTS.name}, "
            f"{ProductTypePermissions.MANAGE_PRODUCT_TYPES_AND_ATTRIBUTES.name}."
        ),
        required=True,
        deprecation_reason=DEPRECATED_IN_3X_FIELD,
    )
    storefront_search_position = graphene.Int(
        description=(
            f"{AttributeDescriptions.STOREFRONT_SEARCH_POSITION} Requires one of the "
            f"following permissions: {PagePermissions.MANAGE_PAGES.name}, "
            f"{PageTypePermissions.MANAGE_PAGE_TYPES_AND_ATTRIBUTES.name}, "
            f"{ProductPermissions.MANAGE_PRODUCTS.name}, "
            f"{ProductTypePermissions.MANAGE_PRODUCT_TYPES_AND_ATTRIBUTES.name}."
        ),
        required=True,
        deprecation_reason=DEPRECATED_IN_3X_FIELD,
    )
    translation = TranslationField(AttributeTranslation, type_name="attribute")
    with_choices = graphene.Boolean(
        description=AttributeDescriptions.WITH_CHOICES, required=True
    )
    product_types = ConnectionField(
        "swiftmovers.graphql.product.types.ProductTypeCountableConnection",
        required=True,
    )
    product_variant_types = ConnectionField(
        "swiftmovers.graphql.product.types.ProductTypeCountableConnection",
        required=True,
    )
    external_reference = graphene.String(
        description=f"External ID of this attribute. {ADDED_IN_310}",
        required=False,
    )

    class Meta:
        description = (
            "Custom attribute of a product. Attributes can be assigned to products and "
            "variants at the product type level."
        )
        interfaces = [graphene.relay.Node, ObjectWithMetadata]
        model = models.Attribute

    @staticmethod
    def resolve_choices(root: models.Attribute, info: ResolveInfo, **kwargs):
        if root.input_type in AttributeInputType.TYPES_WITH_CHOICES:
            qs = cast(QuerySet[models.AttributeValue], root.values.all())
        else:
            qs = cast(
                QuerySet[models.AttributeValue], models.AttributeValue.objects.none()
            )

        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(
            qs, info, kwargs, AttributeValueCountableConnection
        )

    @staticmethod
    @check_attribute_required_permissions()
    def resolve_value_required(root: models.Attribute, _info: ResolveInfo):
        return root.value_required

    @staticmethod
    @check_attribute_required_permissions()
    def resolve_visible_in_storefront(root: models.Attribute, _info: ResolveInfo):
        return root.visible_in_storefront

    @staticmethod
    @check_attribute_required_permissions()
    def resolve_filterable_in_storefront(root: models.Attribute, _info: ResolveInfo):
        return root.filterable_in_storefront

    @staticmethod
    @check_attribute_required_permissions()
    def resolve_filterable_in_dashboard(root: models.Attribute, _info: ResolveInfo):
        return root.filterable_in_dashboard

    @staticmethod
    @check_attribute_required_permissions()
    def resolve_storefront_search_position(root: models.Attribute, _info: ResolveInfo):
        return root.storefront_search_position

    @staticmethod
    @check_attribute_required_permissions()
    def resolve_available_in_grid(root: models.Attribute, _info: ResolveInfo):
        return root.available_in_grid

    @staticmethod
    def resolve_with_choices(root: models.Attribute, _info: ResolveInfo):
        return root.input_type in AttributeInputType.TYPES_WITH_CHOICES

    @staticmethod
    def resolve_product_types(root: models.Attribute, info: ResolveInfo, **kwargs):
        from ..product.types import ProductTypeCountableConnection

        qs = root.product_types.all()
        return create_connection_slice(qs, info, kwargs, ProductTypeCountableConnection)

    @staticmethod
    def resolve_product_variant_types(
        root: models.Attribute, info: ResolveInfo, **kwargs
    ):
        from ..product.types import ProductTypeCountableConnection

        qs = root.product_variant_types.all()
        return create_connection_slice(qs, info, kwargs, ProductTypeCountableConnection)


class AttributeCountableConnection(CountableConnection):
    class Meta:
        doc_category = DOC_CATEGORY_ATTRIBUTES
        node = Attribute


class AssignedVariantAttribute(BaseObjectType):
    attribute = graphene.Field(
        Attribute, description="Attribute assigned to variant.", required=True
    )
    variant_selection = graphene.Boolean(
        required=True,
        description=(
            "Determines, whether assigned attribute is "
            "allowed for variant selection. Supported variant types for "
            "variant selection are: "
            f"{AttributeInputType.ALLOWED_IN_VARIANT_SELECTION}"
        ),
    )

    class Meta:
        description = (
            "Represents assigned attribute to variant with variant selection attached."
            + ADDED_IN_31
        )
        doc_category = DOC_CATEGORY_ATTRIBUTES


class SelectedAttribute(BaseObjectType):
    attribute = graphene.Field(
        Attribute,
        default_value=None,
        description=AttributeDescriptions.NAME,
        required=True,
    )
    values = NonNullList(
        AttributeValue, description="Values of an attribute.", required=True
    )

    class Meta:
        doc_category = DOC_CATEGORY_ATTRIBUTES
        description = "Represents a custom attribute."


class AttributeInput(BaseInputObjectType):
    slug = graphene.String(required=True, description=AttributeDescriptions.SLUG)
    values = NonNullList(
        graphene.String, required=False, description=AttributeValueDescriptions.SLUG
    )
    values_range = graphene.Field(
        IntRangeInput,
        required=False,
        description=AttributeValueDescriptions.VALUES_RANGE,
    )
    date_time = graphene.Field(
        DateTimeRangeInput,
        required=False,
        description=AttributeValueDescriptions.DATE_TIME_RANGE,
    )
    date = graphene.Field(
        DateRangeInput,
        required=False,
        description=AttributeValueDescriptions.DATE_RANGE,
    )
    boolean = graphene.Boolean(
        required=False, description=AttributeDescriptions.BOOLEAN
    )

    class Meta:
        doc_category = DOC_CATEGORY_ATTRIBUTES


class AttributeValueSelectableTypeInput(BaseInputObjectType):
    id = graphene.ID(required=False, description="ID of an attribute value.")
    value = graphene.String(
        required=False,
        description=(
            "The value or slug of an attribute to resolve. "
            "If the passed value is non-existent, it will be created."
        ),
    )

    class Meta:
        description = (
            "Represents attribute value. If no ID provided, value will be resolved. "
            + ADDED_IN_39
        )
        doc_category = DOC_CATEGORY_ATTRIBUTES


class AttributeValueInput(BaseInputObjectType):
    id = graphene.ID(description="ID of the selected attribute.")
    values = NonNullList(
        graphene.String,
        required=False,
        description=(
            "The value or slug of an attribute to resolve. "
            "If the passed value is non-existent, it will be created. "
            + DEPRECATED_IN_3X_FIELD
        ),
    )
    dropdown = AttributeValueSelectableTypeInput(
        required=False,
        description="Attribute value ID." + ADDED_IN_39,
    )
    swatch = AttributeValueSelectableTypeInput(
        required=False,
        description="Attribute value ID." + ADDED_IN_39,
    )
    multiselect = NonNullList(
        AttributeValueSelectableTypeInput,
        required=False,
        description="List of attribute value IDs." + ADDED_IN_39,
    )
    numeric = graphene.String(
        required=False,
        description="Numeric value of an attribute." + ADDED_IN_39,
    )
    file = graphene.String(
        required=False,
        description="URL of the file attribute. Every time, a new value is created.",
    )
    content_type = graphene.String(required=False, description="File content type.")
    references = NonNullList(
        graphene.ID,
        description="List of entity IDs that will be used as references.",
        required=False,
    )
    rich_text = JSONString(required=False, description="Text content in JSON format.")
    plain_text = graphene.String(required=False, description="Plain text content.")
    boolean = graphene.Boolean(
        required=False, description=AttributeValueDescriptions.BOOLEAN
    )
    date = Date(required=False, description=AttributeValueDescriptions.DATE)
    date_time = graphene.DateTime(
        required=False, description=AttributeValueDescriptions.DATE_TIME
    )

    class Meta:
        doc_category = DOC_CATEGORY_ATTRIBUTES
