from enum import Enum


class ProductErrorCode(Enum):
    GRAPHQL_ERROR = "graphql_error"
    INVALID = "invalid"
    PRODUCT_WITHOUT_CATEGORY = "product_without_category"
    NOT_FOUND = "not_found"
    REQUIRED = "required"
    UNIQUE = "unique"
