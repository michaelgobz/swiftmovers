from typing import TYPE_CHECKING, List, Union

from django.db import models
from django.db.models import Q
from django_countries.fields import CountryField
from django_measurement.models import MeasurementField
from measurement.measures import Weight
from prices import Money

from . import ShippingMethodType
from ..core.db.fields import SanitizedJSONField
from ..core.weight import zero_weight
from ..core.units import WeightUnits
from ..core.utils.editor import clean_editor_js

# Create your models here.

if TYPE_CHECKING:
    # flake8: noqa
    from ..checkouts.models import DeliveryCheckout
    # TODO: make the model for the orders
    # from .orders.models import DeliveryOrder


def _applicable_weight_based_methods(weight, qs):
    """Return weight based shipping methods that are applicable for the total weight."""
    qs = qs.weight_based()
    min_weight_matched = Q(minimum_order_weight__lte=weight) | Q(
        minimum_order_weight__isnull=True
    )
    max_weight_matched = Q(maximum_order_weight__gte=weight) | Q(
        maximum_order_weight__isnull=True
    )
    return qs.filter(min_weight_matched & max_weight_matched)


# shipping zone
class ShippingZone(models.Model):
    name = models.CharField(max_length=100)
    countries = CountryField(multiple=True, default=[], blank=True)
    default = models.BooleanField(default=False)
    description = models.TextField(blank=True)


# shipping method

class ShippingMethodQueryset(models.QuerySet):
    def price_based(self):
        return self.filter(type=ShippingMethodType.PRICE_BASED)

    def weight_based(self):
        return self.filter(type=ShippingMethodType.WEIGHT_BASED)

    @staticmethod
    def exclude_shipping_methods_for_excluded_products(
            qs, product_ids: List[int]
    ):
        """Exclude the ShippingMethods which have excluded given products."""
        return qs.exclude(excluded_products__id__in=product_ids)

    def applicable_shipping_methods(
            self, price: Money, weight, country_code, product_ids=None
    ):
        """Return the ShippingMethods that can be used on an order with shipment.

        It is based on the given country code, and by shipping methods that are
        applicable to the given price, weight and products.
        """
        qs = self.filter(
            shipping_zone__countries__contains=country_code,
            channel_listings__currency=price.currency,

        )
        qs = qs.prefetch_related("shipping_zone")

        # Products IDs are used to exclude shipping methods that may be not applicable
        # to some of these products, based on exclusion rules defined in shipping method
        # instances.
        if product_ids:
            qs = self.exclude_shipping_methods_for_excluded_products(qs, product_ids)

        weight_based_methods = _applicable_weight_based_methods(weight, qs)
        shipping_methods = weight_based_methods

        return shipping_methods

    def applicable_shipping_methods_for_instance(
            self,
            # TODO: add the order instance
            instance: Union["DeliveryCheckout", "Order"],

            price: Money,
            country_code=None,
            lines=None,
    ):
        if not instance.shipping_address:
            return None
        if not country_code:
            # TODO: country_code should come from argument
            country_code = instance.shipping_address.country.code  # type: ignore
        if lines is None:
            # TODO: lines should comes from args in get_valid_shipping_methods_for_order
            lines = instance.lines.prefetch_related("variant__product").all()
            instance_product_ids = set(lines.values_list("variant__product", flat=True))
        else:
            instance_product_ids = {line.product.id for line in lines}
        applicable_methods = self.applicable_shipping_methods(
            price=price,
            weight=instance.get_total_weight(lines),
            country_code=country_code or instance.shipping_address.country.code,
            product_ids=instance_product_ids,
        ).prefetch_related("postal_code_rules")

        return applicable_methods, instance.shipping_address


class ShippingMethod(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=30, choices=ShippingMethodType.CHOICES)
    shipping_zone = models.ForeignKey(
        ShippingZone, related_name="shipping_methods", on_delete=models.CASCADE
    )
    minimum_order_weight = MeasurementField(
        measurement=Weight,
        unit_choices=WeightUnits.CHOICES,  # type: ignore
        default=zero_weight,
        blank=True,
        null=True,
    )
    maximum_order_weight = MeasurementField(
        measurement=Weight,
        unit_choices=WeightUnits.CHOICES,  # type: ignore
        blank=True,
        null=True,
    )
    excluded_products = models.ManyToManyField(
        "product.Product", blank=True
    )  # type: ignore
    maximum_delivery_days = models.PositiveIntegerField(null=True, blank=True)
    minimum_delivery_days = models.PositiveIntegerField(null=True, blank=True)
    description = SanitizedJSONField(blank=True, null=True, sanitizer=clean_editor_js)

    objects = models.Manager.from_queryset(ShippingMethodQueryset)()
