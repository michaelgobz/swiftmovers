from typing import TYPE_CHECKING, Optional

from django.core.exceptions import ValidationError
from django_prices.utils.formatting import get_currency_fraction
from graphql.error import GraphQLError

if TYPE_CHECKING:
    from decimal import Decimal

def validate_one_of_args_is_in_mutation(error_class, *args):
    try:
        validate_one_of_args_is_in_query(*args)
    except GraphQLError as e:
        raise ValidationError(str(e), code=error_class.GRAPHQL_ERROR)


def validate_one_of_args_is_in_query(*args):
    # split args into a list with 2-element tuples:
    # [(arg1_name, arg1_value), (arg2_name, arg2_value), ...]
    splitted_args = [args[i : i + 2] for i in range(0, len(args), 2)]  # noqa: E203
    # filter true-ish values from each tuple
    filter_args = list(filter(lambda item: bool(item[1]) is True, splitted_args))

    if len(filter_args) > 1:
        rest_args = ", ".join([f"'{item[0]}'" for item in filter_args[1:]])
        raise GraphQLError(
            f"Argument '{filter_args[0][0]}' cannot be combined with {rest_args}"
        )

    if not filter_args:
        required_args = ", ".join([f"'{item[0]}'" for item in splitted_args])
        raise GraphQLError(f"At least one of arguments is required: {required_args}.")


def validate_price_precision(value: Optional["Decimal"], currency: str):
    """Validate if price amount does not have too many decimal places.

    Price amount can't have more decimal places than currency allow to.
    Works only with decimal created from a string.
    """

    # check no needed when there is no value
    if not value:
        return
    currency_fraction = get_currency_fraction(currency)
    value = value.normalize()
    if value.as_tuple().exponent < -currency_fraction:
        raise ValidationError(
            f"Value cannot have more than {currency_fraction} decimal places."
        )


def validate_decimal_max_value(value: "Decimal", max_value=10**9):
    """Validate if price amount is not higher than the limit for precision field.

    Decimal fields in database have value limits.
    By default, its 10^9 for fields with precision 12.
    """
    if value >= max_value:
        raise ValidationError(f"Value must be lower than {max_value}.")

def validate_end_is_after_start(start_date, end_date):
    """Validate if the end date provided is after start date."""

    # check is not needed if no end date
    if end_date is None:
        return

    if start_date > end_date:
        raise ValidationError("End date cannot be before the start date.")
