from typing import TYPE_CHECKING, List,  Union

from django.core.exceptions import ValidationError

from graphene.utils.str_converters import to_camel_case

from ...accounts.error_codes import AccountErrorCode


if TYPE_CHECKING:
    from django.db.models import QuerySet

    from ...accounts.models import User


class UserDeleteMixin:
    class Meta:
        abstract = True

    @classmethod
    def clean_instance(cls, info, instance):
        user = info.context.user
        if instance == user:
            raise ValidationError(
                {
                    "id": ValidationError(
                        "You cannot delete your own account.",
                        code=AccountErrorCode.DELETE_OWN_ACCOUNT,
                    )
                }
            )
        elif instance.is_superuser:
            raise ValidationError(
                {
                    "id": ValidationError(
                        "Cannot delete this account.",
                        code=AccountErrorCode.DELETE_SUPERUSER_ACCOUNT,
                    )
                }
            )


class CustomerDeleteMixin(UserDeleteMixin):
    class Meta:
        abstract = True

    @classmethod
    def clean_instance(cls, info, instance):
        super().clean_instance(info, instance)
        if instance.is_staff:
            raise ValidationError(
                {
                    "id": ValidationError(
                        "Cannot delete a staff account.",
                        code=AccountErrorCode.DELETE_STAFF_ACCOUNT,
                    )
                }
            )

    @classmethod
    def post_process(cls, info, deleted_count=1):
        print(cls.__base__.mro())
        # TODO: preform a post process


def get_required_fields_camel_case(required_fields: set) -> set:
    """Return set of AddressValidationRules required fields in camel case."""
    return {validation_field_to_camel_case(field) for field in required_fields}


def get_upper_fields_camel_case(upper_fields: set) -> set:
    """Return set of AddressValidationRules upper fields in camel case."""
    return {validation_field_to_camel_case(field) for field in upper_fields}


def validation_field_to_camel_case(name: str) -> str:
    """Convert name of the field from snake case to camel case."""
    name = to_camel_case(name)
    if name == "streetAddress":
        return "streetAddress1"
    return name


def get_allowed_fields_camel_case(allowed_fields: set) -> set:
    """Return set of AddressValidationRules allowed fields in camel case."""
    fields = {validation_field_to_camel_case(field) for field in allowed_fields}
    if "streetAddress1" in fields:
        fields.add("streetAddress2")
    return fields


def get_user_permissions(user: "User") -> "QuerySet":
    """Return all user permissions - from user groups and user_permissions field."""
    pass


