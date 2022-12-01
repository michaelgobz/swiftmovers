# Create your models here.
from django.conf import settings
from django.db import models
from django_countries.fields import CountryField

from . import AllocationStrategy


class Zone(models.Model):
    name = models.CharField(max_length=250)
    is_active = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True)
    currency_code = models.CharField(max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH)
    default_country = CountryField()
    allocation_strategy = models.CharField(
        max_length=255,
        choices=AllocationStrategy.CHOICES,
        default=AllocationStrategy.PRIORITIZE_SORTING_ORDER,
    )

    class Meta:
        ordering = ("slug",)
        app_label = "zone"
        # Todo: Add permissions

    def __str__(self):
        return self.slug
