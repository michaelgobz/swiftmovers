from typing import TYPE_CHECKING, Collection, Union
# TODO: add the user object model

from .auth_filters import (
    AuthorizationFilters,
    is_app,
    is_staff_user,
    is_user,
    resolve_authorization_filter_fn,
)
from .enums import (
    PERMISSIONS_ENUMS,
    AccountPermissions,
    BasePermissionEnum,
    CheckoutPermissions,
    OrderPermissions,
    PaymentPermissions,
    ShippingPermissions,
    get_permission_names,
    get_permissions,
    get_permissions_codename,
    get_permissions_enum_dict,
    get_permissions_enum_list,
    get_permissions_from_codenames,
    get_permissions_from_names,
    split_permission_codename,
)

__all__ = [
    "PERMISSIONS_ENUMS",
    "is_app",
    "is_staff_user",
    "is_user",
    "CheckoutPermissions",
    "OrderPermissions",
    "PaymentPermissions",
    "ShippingPermissions",
    "get_permission_names",
    "get_permissions",
    "get_permissions_codename",
    "get_permissions_enum_dict",
    "get_permissions_enum_list",
    "get_permissions_from_codenames",
    "get_permissions_from_names",
    "split_permission_codename",
]


def one_of_permissions_or_auth_filter_required(context, permissions):
    """Determine whether user or app has rights to perform an action.

    The `context` parameter is the Context instance associated with the request.
    """
    if not permissions:
        return True

    authorization_filters = [
        p for p in permissions if isinstance(p, AuthorizationFilters)
    ]
    permissions = [p for p in permissions if not isinstance(p, AuthorizationFilters)]

    granted_by_permissions = False
    granted_by_authorization_filters = False

    from swiftmovers.graphqlcore.utils import get_user_from_context

    requestor = get_user_from_context(context)

    if requestor and permissions:
        perm_checks_results = []
        for permission in permissions:
            perm_checks_results.append(requestor.has_perm(permission))
        granted_by_permissions = any(perm_checks_results)

    if authorization_filters:
        auth_filters_results = []
        for p in authorization_filters:
            perm_fn = resolve_authorization_filter_fn(p)
            if perm_fn:
                res = perm_fn(context)
                auth_filters_results.append(bool(res))
        granted_by_authorization_filters = any(auth_filters_results)

    return granted_by_permissions or granted_by_authorization_filters


def permission_required(
        requestor: Union["User"], perms: Collection[BasePermissionEnum]
) -> bool:
    # from ...account.models import User

    if isinstance(requestor, object):
        return requestor.has_perms(perms)
    elif requestor:
        # for now MANAGE_STAFF permission for app is not supported
        if AccountPermissions.MANAGE_STAFF in perms:
            return False
        return requestor.has_perms(perms)
    return False


def has_one_of_permissions(
        requestor: Union["User"], permissions: Collection[BasePermissionEnum]
) -> bool:
    if not permissions:
        return True
    for perm in permissions:
        if permission_required(requestor, (perm,)):
            return True
    return False


def message_one_of_permissions_required(
        permissions: Collection[BasePermissionEnum],
) -> str:
    permission_msg = ", ".join([p.name for p in permissions])
    return f"\n\nRequires one of the following permissions: {permission_msg}."
