from django.urls import reverse
from django.utils.functional import SimpleLazyObject

from .core.spec.schema import build_federated_schema
from .accounts.schema import AccountMutations, AccountQueries
from .core.enums import unit_enums

API_PATH = SimpleLazyObject(lambda: reverse("api"))


class Query(
    AccountQueries
):
    pass

class Mutation (
    AccountMutations
):
    pass

schema = build_federated_schema(
    Query,
    mutation=Mutation,
    types=unit_enums,
    # TODO: add the types and subscriptions
)
