from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

from django.db.models import QuerySet

N = TypeVar("N")


@dataclass
class ZoneContext(Generic[N]):
    node: N
    zone_slug: Optional[str]


@dataclass
class ZoneQsContext:
    qs: QuerySet
    zone_slug: Optional[str]
