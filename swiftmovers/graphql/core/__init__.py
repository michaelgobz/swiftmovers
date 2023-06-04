import graphene

from . import fields  # noqa
from .context import swiftmoversContext

__all__ = ["swiftmoversContext"]


class ResolveInfo(graphene.ResolveInfo):
    context: swiftmoversContext
