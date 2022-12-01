"""
we use weight here because thats the  most known concept

"""
from django.contrib.sites.models import Site
from measurement.measures import Weight


def zero_weight():
    """Represent the zero weight value."""
    return Weight(kg=0)


def convert_weight(weight: Weight, unit: str) -> Weight:
    """Covert weight to given unit and round it to 3 digits after decimal point."""
    converted_weight = getattr(weight, unit)
    weight = Weight(**{unit: converted_weight})
    weight.value = round(weight.value, 3)
    return weight


def get_default_weight_unit():
    site = Site.objects.get_current()
    return site.settings.default_weight_unit
