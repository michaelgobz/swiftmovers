from django.urls import reverse
from django.utils.functional import SimpleLazyObject

from .core.spec.schema import build_federated_schema

API_PATH = SimpleLazyObject(lambda: reverse("api"))


class Query:
    pass


class Mutation:
    pass


schema = build_federated_schema(
    Query,
    mutation=Mutation,
    types=None,
    # TODO: add the types and subscriptions
)
