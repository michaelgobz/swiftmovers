import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from django.conf import settings
from django.http import HttpRequest
from django.utils.functional import empty

from ...account.models import User
from ...app.models import App

if TYPE_CHECKING:
    from .dataloaders import DataLoader


class SwiftmoversContext(HttpRequest):
    _cached_user: Optional[User]
    decoded_auth_token: Optional[Dict[str, Any]]
    allow_replica: bool = True
    dataloaders: Dict[str, "DataLoader"]
    app: Optional[App]
    user: Optional[User]  # type: ignore[assignment]
    requestor: Union[App, User, None]
    request_time: datetime.datetime


def disallow_replica_in_context(context: SwiftmoversContext) -> None:
    """Set information in context to use database replicas or not.

    Part of the database read replicas in Swiftmovers.
    When Swiftmovers builds a response for mutation `context` stores information
    `allow_replica=False`. That means that all data should be provided from
    the master database.
    When Swiftmovers builds a response for query, set `allow_replica`=True in `context`.
    That means that all data should be provided from reading replica of the database.
    Database read replica couldn't be used to save any data.
    """
    context.allow_replica = False


def get_database_connection_name(context: SwiftmoversContext) -> str:
    """Retrieve connection name based on request context.

    Part of the database read replicas in Swiftmovers.
    Return proper connection name based on `context`.
    For more info check `disallow_replica_in_context`
    Add `.using(connection_name)` to use connection name in QuerySet.
    Queryset to main database: `User.objects.all()`.
    Queryset to read replica: `User.objects.using(connection_name).all()`.
    """
    allow_replica = getattr(context, "allow_replica", True)
    if allow_replica:
        return settings.DATABASE_CONNECTION_REPLICA_NAME
    return settings.DATABASE_CONNECTION_DEFAULT_NAME


def setup_context_user(context: SwiftmoversContext) -> None:
    if hasattr(context.user, "_wrapped") and (
        context.user._wrapped is empty or context.user._wrapped is None  # type: ignore
    ):
        context.user._setup()  # type: ignore
        context.user = context.user._wrapped  # type: ignore
