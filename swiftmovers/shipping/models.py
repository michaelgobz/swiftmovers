from typing import TYPE_CHECKING, List, Union

from django.db import models
from django.db.models import Q
from django_countries.fields import CountryField
from django_measurement.models import MeasurementField
from measurement.measures import Weight
from prices import Money
from django.conf import settings
from django_prices.models import MoneyField

from ..zones.models import Zone
from . import ShippingMethodType
from ..core.db.fields import SanitizedJSONField
from ..core.weight import zero_weight, convert_weight, get_default_weight_unit
from ..core.units import WeightUnits
from ..core.utils.editor import clean_editor_js
from ..core.models import ModelWithMetadata
from ..orders.models import Order

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

def _get_weight_type_display(min_weight, max_weight):
    default_unit = get_default_weight_unit()

    if min_weight.unit != default_unit:
        min_weight = convert_weight(min_weight, default_unit)
    if max_weight and max_weight.unit != default_unit:
        max_weight = convert_weight(max_weight, default_unit)

    if max_weight is None:
        return "%(min_weight)s and up" % {"min_weight": min_weight},
    return "%(min_weight)s to %(max_weight)s" % {
        "min_weight": min_weight,
        "max_weight": max_weight,
    }

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


class ShippingMethod(ModelWithMetadata):
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
    maximum_delivery_days = models.PositiveIntegerField(null=True, blank=True)
    minimum_delivery_days = models.PositiveIntegerField(null=True, blank=True)
    description = SanitizedJSONField(blank=True, null=True, sanitizer=clean_editor_js)

    objects = models.Manager.from_queryset(ShippingMethodQueryset)()

    class Meta(ModelWithMetadata.Meta):
        ordering = ("pk",)

    def __str__(self):
        return self.name

    def __repr__(self):
        if self.type == ShippingMethodType.PRICE_BASED:
            return "ShippingMethod(type=%s)" % (self.type,)
        return "ShippingMethod(type=%s weight_range=(%s)" % (
            self.type,
            _get_weight_type_display(
                self.minimum_order_weight, self.maximum_order_weight
            ),
        )

class ShippingMethodZoneListing(models.Model):
    shipping_method = models.ForeignKey(
        ShippingMethod,
        null=False,
        blank=False,
        related_name="Zone_listings",
        on_delete=models.CASCADE,
    )
    zone = models.ForeignKey(
        Zone,
        null=False,
        blank=False,
        related_name="shipping_method_listings",
        on_delete=models.CASCADE,
    )
    minimum_order_price_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
        blank=True,
        null=True,
    )
    minimum_order_price = MoneyField(
        amount_field="minimum_order_price_amount", currency_field="currency"
    )
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
    )
    maximum_order_price_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        blank=True,
        null=True,
    )
    maximum_order_price = MoneyField(
        amount_field="maximum_order_price_amount", currency_field="currency"
    )
    price = MoneyField(amount_field="price_amount", currency_field="currency")
    price_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )

    def get_total(self):
        return self.price

    class Meta:
        unique_together = [["shipping_method", "zone"]]
        ordering = ("pk",)