import hashlib
import logging
import traceback

from django.conf import settings
from graphql import GraphQLDocument
from graphql.error import GraphQLError
from graphql.error import format_error as format_graphql_error


unhandled_errors_logger = logging.getLogger("saleor.graphql.errors.unhandled")
handled_errors_logger = logging.getLogger("saleor.graphql.errors.handled")


ERROR_COULD_NO_RESOLVE_GLOBAL_ID = (
    "Could not resolve to a node with the global id list of '%s'."
)
REVERSED_DIRECTION = {
    "-": "",
    "": "-",
}


def get_user_or_app_from_context(context):
    # order is important
    # app can be None but user if None then is passed as anonymous
    return context.app or context.user


def query_identifier(document: GraphQLDocument) -> str:
    """Generate a fingerprint for a GraphQL query.

    For queries identifier is sorted set of all root objects separated by `,`.
    e.g
    query AnyQuery {
        product {
            id
        }
        order {
            id
        }
        Product2: product {
            id
        }
        Myself: me {
            email
        }
    }
    identifier: me, order, product

    For mutations identifier is mutation type name.
    e.g.
    mutation CreateToken{
        tokenCreate(...){
            token
        }
        deleteWarehouse(...){
            ...
        }
    }
    identifier: deleteWarehouse, tokenCreate
    """
    labels = []
    for definition in document.document_ast.definitions:
        if getattr(definition, "operation", None) in {
            "query",
            "mutation",
        }:
            selections = definition.selection_set.selections
            for selection in selections:
                labels.append(selection.name.value)
    if not labels:
        return "undefined"
    return ", ".join(sorted(set(labels)))


def query_fingerprint(document: GraphQLDocument) -> str:
    """Generate a fingerprint for a GraphQL query."""
    label = "unknown"
    for definition in document.document_ast.definitions:
        if getattr(definition, "operation", None) in {
            "query",
            "mutation",
            "subscription",
        }:
            if definition.name:
                label = f"{definition.operation}:{definition.name.value}"
            else:
                label = definition.operation
            break
    query_hash = hashlib.md5(document.document_string.encode("utf-8")).hexdigest()
    return f"{label}:{query_hash}"


def format_error(error, handled_exceptions):
    if isinstance(error, GraphQLError):
        result = format_graphql_error(error)
    else:
        result = {"message": str(error)}

    if "extensions" not in result:
        result["extensions"] = {}

    exc = error
    while isinstance(exc, GraphQLError) and hasattr(exc, "original_error"):
        exc = exc.original_error
    if isinstance(exc, AssertionError):
        exc = GraphQLError(str(exc))
    if isinstance(exc, handled_exceptions):
        handled_errors_logger.info("A query had an error", exc_info=exc)
    else:
        unhandled_errors_logger.error("A query failed unexpectedly", exc_info=exc)

    result["extensions"]["exception"] = {"code": type(exc).__name__}
    if settings.DEBUG:
        lines = []

        if isinstance(exc, BaseException):
            for line in traceback.format_exception(type(exc), exc, exc.__traceback__):
                lines.extend(line.rstrip().splitlines())
        result["extensions"]["exception"]["stacktrace"] = lines
    return result
