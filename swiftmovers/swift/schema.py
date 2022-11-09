import graphene
from graphene_django import DjangoObjectType

from .models import Swift


class SwiftType(DjangoObjectType):
    class Meta:
        model = Swift


class Query(graphene.ObjectType):
    swifts = graphene.List(SwiftType)

    @staticmethod
    def resolve_swift(info, **kwargs):
        return Swift.objects.all()
