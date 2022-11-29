import graphene

from ...invoices import models
from ..core.types.model import ModelObjectType
from ..meta.types import ObjectWithMetadata


class Invoice(ModelObjectType):
    number = graphene.String()
    external_url = graphene.String()
    created_at = graphene.DateTime(required=True)
    updated_at = graphene.DateTime(required=True)
    message = graphene.String()
    url = graphene.String(description="URL to download an invoice.")

    class Meta:
        description = "Represents an Invoice."
        interfaces = [ObjectWithMetadata, graphene.relay.Node]
        model = models.Invoice
