from typing import Optional

from swiftmovers.zones import models
from ....core.permissions import is_staff_user
from ...core.utils import from_global_id_or_error
from ...core.validators import validate_one_of_args_is_in_query
from ..types import Zone

def resolve_zone(info, id: Optional[str], slug: Optional[str]):
    validate_one_of_args_is_in_query("id", id, "slug", slug)
    if id:
        _, db_id = from_global_id_or_error(id, Zone)
        zone = models.Zone.objects.filter(id=db_id).first()
    else:
        zone = models.Zone.objects.filter(slug=slug).first()

    if zone and Zone.is_active:
        return zone
    if is_staff_user(info.context):
        return zone

    return None


def resolve_zones():
    return models.Zone.objects.all()
