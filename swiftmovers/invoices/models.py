from django.db import models
from django.db.models import JSONField  # type: ignore
from ..core.utils import build_absolute_uri
from ..orders.models import Order


# Create your models here.

class Invoice(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="invoices",
        null=True,
        on_delete=models.SET_NULL,
    )
    number = models.CharField(max_length=255, null=True)
    created = models.DateTimeField(null=True)
    external_url = models.URLField(null=True, max_length=2048)
    invoice_file = models.FileField(upload_to="invoices")

    objects = models.Manager()

    @property
    def url(self):
        if self.invoice_file:
            return build_absolute_uri(self.invoice_file.url)
        return self.external_url

    @url.setter
    def url(self, value):
        self.external_url = value

    def update_invoice(self, number=None, url=None):
        if number is not None:
            self.number = number
        if url is not None:
            self.external_url = url
