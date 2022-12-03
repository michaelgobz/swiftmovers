from itertools import chain
from typing import Optional

from i18naddress import get_validation_rules

from ....accounts import models

from ....core.tracing import traced_resolver
from ....payments.interface import  PaymentGateway  # TODO: add gateway
from ....payments.utils import fetch_customer_id
from ...core.utils import from_global_id_or_error
from ...meta.resolvers import resolve_metadata
from ...utils import get_user_or_app_from_context
from ..types import Address, AddressValidationData, ChoiceValue, User
from ..utils import (
    get_allowed_fields_camel_case,
    get_required_fields_camel_case,
    get_upper_fields_camel_case,
)

USER_SEARCH_FIELDS = (
    "email",
    "first_name",
    "last_name",
    "default_shipping_address__first_name",
    "default_shipping_address__last_name",
    "default_shipping_address__city",
    "default_shipping_address__country",
)


def resolve_customers(_info):
    return models.User.objects.customers()


def resolve_staff_users(_info):
    return models.User.objects.staff()


@traced_resolver
def resolve_user(info, id=None, email=None):
    requester = get_user_or_app_from_context(info.context)
    filter_kwargs = {}
    if requester:
        filter_kwargs = {}
        if id:
            _model, filter_kwargs["pk"] = from_global_id_or_error(id, User)
        if email:
            filter_kwargs["email"] = email
            return models.User.objects.filter(**filter_kwargs).first()
    return models.User.objects.customers().filter(**filter_kwargs).first()


@traced_resolver
def resolve_users(info, ids=None, emails=None):
    requester = get_user_or_app_from_context(info.context)
    if requester:
        return models.User.objects.all()
    qs = models.User.objects
    return qs.filter(email__in=emails)


@traced_resolver
def resolve_address_validation_rules(
        info,
        country_code: str,
        country_area: Optional[str],
        city: Optional[str],
        city_area: Optional[str],
):
    params = {
        "country_code": country_code,
        "country_area": country_area,
        "city": city,
        "city_area": city_area,
    }
    rules = get_validation_rules(params)
    return AddressValidationData(
        country_code=rules.country_code,
        country_name=rules.country_name,
        address_format=rules.address_format,
        address_latin_format=rules.address_latin_format,
        allowed_fields=get_allowed_fields_camel_case(rules.allowed_fields),
        required_fields=get_required_fields_camel_case(rules.required_fields),
        upper_fields=get_upper_fields_camel_case(rules.upper_fields),
        country_area_type=rules.country_area_type,
        country_area_choices=[
            ChoiceValue(area[0], area[1]) for area in rules.country_area_choices
        ],
        city_type=rules.city_type,
        city_choices=[ChoiceValue(area[0], area[1]) for area in rules.city_choices],
        city_area_type=rules.city_area_type,
        city_area_choices=[
            ChoiceValue(area[0], area[1]) for area in rules.city_area_choices
        ],
        postal_code_type=rules.postal_code_type,
        postal_code_matchers=[
            compiled.pattern for compiled in rules.postal_code_matchers
        ],
        postal_code_examples=rules.postal_code_examples,
        postal_code_prefix=rules.postal_code_prefix,
    )


@traced_resolver
def resolve_payment_sources(info, user: models.User, channel_slug: str):
    manager = info.context.plugins
    stored_customer_accounts = (
        (gtw.id, fetch_customer_id(user, gtw.id))
        for gtw in gateway.list_gateways(manager, channel_slug)
    )
    return list(
        chain(
            *[
                prepare_graphql_payment_sources_type(
                    gateway.list_payment_sources(
                        gtw, customer_id, manager, channel_slug
                    )
                )
                for gtw, customer_id in stored_customer_accounts
                if customer_id is not None
            ]
        )
    )


def prepare_graphql_payment_sources_type(payment_sources):
    sources = []
    for src in payment_sources:
        sources.append(
            {
                "gateway": src.gateway,
                "payment_method_id": src.id,
                "credit_card_info": {
                    "last_digits": src.credit_card_info.last_4,
                    "exp_year": src.credit_card_info.exp_year,
                    "exp_month": src.credit_card_info.exp_month,
                    "brand": src.credit_card_info.brand,
                    "first_digits": src.credit_card_info.first_4,
                },
                "metadata": resolve_metadata(src.metadata),
            }
        )
    return sources


@traced_resolver
def resolve_address(info, id):
    user = info.context.user
    app = info.context.app
    _, address_pk = from_global_id_or_error(id, Address)
    if user and not user.is_anonymous:
        return user.addresses.filter(id=address_pk).first()


def resolve_addresses(info, ids):
    user = info.context.user
    ids = [
        from_global_id_or_error(address_id, Address, raise_error=True)[1]
        for address_id in ids
    ]
    if user and not user.is_anonymous:
        return user.addresses.filter(id__in=ids)
    return models.Address.objects.none()
