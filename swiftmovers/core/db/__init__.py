from typing import TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from django.http import HttpRequest


def set_mutation_flag_in_context(context: "HttpRequest"):
    context.is_mutation = True  # type: ignore


def get_database_connection_name(context: "HttpRequest"):
    """Retrieve connection name based on request context. (app or user)
    """
    is_mutation = getattr(context, "is_mutation", False)
    if not is_mutation:
        return settings.DATABASE_CONNECTION_REPLICA_NAME
    return settings.DATABASE_CONNECTION_DEFAULT_NAME
