import graphene

from ..core.connections import create_connection_slice, filter_connection_queryset
from ..core.utils import from_global_id_or_error
from ..core.fields import FilterConnectionField, PermissionsField
from .sort_helpers import *
from ..core.filters import *
from .enums import CountryCodeEnum
from .mutations.mutations import (
    AccountAddressCreate,
    AccountAddressDelete,
    AccountAddressUpdate,
    AccountDelete,
    AccountRegister,
    AccountRequestDeletion,
    AccountSetDefaultAddress,
    AccountUpdate,
    ConfirmEmailChange,
    RequestEmailChange,
)

from .mutations.base import (
    ConfirmAccount,
    PasswordChange,
    RequestPasswordReset,
    SetPassword,
)

from .resolvers.resolvers import (
    resolve_address,
    resolve_address_validation_rules,
    resolve_customers,
    resolve_staff_users,
    resolve_user,
)
from .types import (
    Address,
    AddressValidationData,
    Group,
    GroupCountableConnection,
    User,
    UserCountableConnection,
)
from ..core.filters import (

)


class CustomerFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = CustomerFilter


class PermissionGroupFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = PermissionGroupFilter


class StaffUserInput(FilterInputObjectType):
    class Meta:
        filterset_class = StaffUserFilter


class AccountQueries(graphene.ObjectType):
    address_validation_rules = graphene.Field(
        AddressValidationData,
        description="Returns address validation rules.",
        country_code=graphene.Argument(
            CountryCodeEnum,
            description="Two-letter ISO 3166-1 country code.",
            required=True,
        ),
        country_area=graphene.Argument(
            graphene.String, description="Designation of a region, province or state."
        ),
        city=graphene.Argument(graphene.String, description="City or a town name."),
        city_area=graphene.Argument(
            graphene.String, description="Sub-locality like a district."
        ),
    )
    address = graphene.Field(
        Address,
        id=graphene.Argument(
            graphene.ID, description="ID of an address.", required=True
        ),
        description="Look up an address by ID.",
    )
    customers = FilterConnectionField(
        UserCountableConnection,
        filter=CustomerFilterInput(description="Filtering options for customers."),
        sort_by=UserSortingInput(description="Sort customers."),
        description="List of the shop's customers.",
    )
    permission_groups = FilterConnectionField(
        GroupCountableConnection,
        filter=PermissionGroupFilterInput(
            description="Filtering options for permission groups."
        ),
        sort_by=PermissionGroupSortingInput(description="Sort permission groups."),
        description="List of permission groups.",

    )
    permission_group = PermissionsField(
        Group,
        id=graphene.Argument(
            graphene.ID, description="ID of the group.", required=True
        ),
        description="Look up permission group by ID.",
    )
    me = graphene.Field(User, description="Return the currently authenticated user.")
    staff_users = FilterConnectionField(
        UserCountableConnection,
        filter=StaffUserInput(description="Filtering options for staff users."),
        sort_by=UserSortingInput(description="Sort staff users."),
        description="List of the shop's staff users.",
    )
    user = PermissionsField(
        User,
        id=graphene.Argument(graphene.ID, description="ID of the user."),
        email=graphene.Argument(
            graphene.String, description="Email address of the user."
        ),
        description="Look up a user by ID or email address.",
    )

    @staticmethod
    def resolve_address_validation_rules(
        _root, info, *, country_code, country_area=None, city=None, city_area=None
    ):
        return resolve_address_validation_rules(
            info,
            country_code,
            country_area=country_area,
            city=city,
            city_area=city_area,
        )

    @staticmethod
    def resolve_customers(_root, info, **kwargs):
        qs = resolve_customers(info)
        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(qs, info, kwargs, UserCountableConnection)

    @staticmethod
    def resolve_me(_root, info):
        user = info.context.user
        return user if user.is_authenticated else None

    @staticmethod
    def resolve_staff_users(_root, info, **kwargs):
        qs = resolve_staff_users(info)
        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(qs, info, kwargs, UserCountableConnection)

    @staticmethod
    def resolve_user(_root, info, *, id=None, email=None):
        return resolve_user(info, id, email)

    @staticmethod
    def resolve_address(_root, info, *, id):
        return resolve_address(info, id)


class AccountMutations(graphene.ObjectType):
    # Base mutations
    request_password_reset = RequestPasswordReset.Field()
    confirm_account = ConfirmAccount.Field()
    set_password = SetPassword.Field()
    password_change = PasswordChange.Field()
    request_email_change = RequestEmailChange.Field()
    confirm_email_change = ConfirmEmailChange.Field()

    # Account mutations
    account_address_create = AccountAddressCreate.Field()
    account_address_update = AccountAddressUpdate.Field()
    account_address_delete = AccountAddressDelete.Field()
    account_set_default_address = AccountSetDefaultAddress.Field()

    account_register = AccountRegister.Field()
    account_update = AccountUpdate.Field()
    account_request_deletion = AccountRequestDeletion.Field()
    account_delete = AccountDelete.Field()


