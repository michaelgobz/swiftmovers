import graphene

from . import fields  # noqa
from .context import SwiftmoversContext

__all__ = ["SwiftmoversContext"]


class ResolveInfo(graphene.ResolveInfo):
    context: SwiftmoversContext
