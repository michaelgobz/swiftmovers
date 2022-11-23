from enum import Enum


class CheckoutErrorCode(Enum):
    BILLING_ADDRESS_NOT_SET = "billing_address_not_set"
    CHECKOUT_NOT_FULLY_PAID = "checkout_not_fully_paid"
    GRAPHQL_ERROR = "graphql_error"
    INVALID = "invalid"
    INVALID_SHIPPING_METHOD = "invalid_shipping_method"
    NOT_FOUND = "not_found"
    PAYMENT_ERROR = "payment_error"
    QUANTITY_GREATER_THAN_LIMIT = "quantity_greater_than_limit"
    REQUIRED = "required"
    SHIPPING_ADDRESS_NOT_SET = "shipping_address_not_set"
    SHIPPING_METHOD_NOT_APPLICABLE = "shipping_method_not_applicable"
    DELIVERY_METHOD_NOT_APPLICABLE = "delivery_method_not_applicable"
    SHIPPING_METHOD_NOT_SET = "shipping_method_not_set"
    SHIPPING_NOT_REQUIRED = "shipping_not_required"
    UNIQUE = "unique"
    ZERO_QUANTITY = "zero_quantity"


class OrderCreateFromCheckoutErrorCode(Enum):
    GRAPHQL_ERROR = "graphql_error"
    CHECKOUT_NOT_FOUND = "checkout_not_found"
    SHIPPING_METHOD_NOT_SET = "shipping_method_not_set"
    BILLING_ADDRESS_NOT_SET = "billing_address_not_set"
    SHIPPING_ADDRESS_NOT_SET = "shipping_address_not_set"
    INVALID_SHIPPING_METHOD = "invalid_shipping_method"
    EMAIL_NOT_SET = "email_not_set"
