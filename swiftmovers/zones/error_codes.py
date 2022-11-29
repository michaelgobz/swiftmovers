from enum import Enum

"""
the conceptual idea is:
and order on a zone is taken to be a transport request or a Transport logistic 
request
"""


class ZoneErrorCode(Enum):
    ALREADY_EXISTS = "already_exists"
    GRAPHQL_ERROR = "graphql_error"
    INVALID = "invalid"
    NOT_FOUND = "not_found"
    REQUIRED = "required"
    UNIQUE = "unique"
    ZONES_CURRENCY_MUST_BE_THE_SAME = "zones_currency_must_be_the_same"
    ZONES_WITH_ORDERS = "channel_with_orders"
    DUPLICATED_INPUT_ITEM = "duplicated_input_item"
