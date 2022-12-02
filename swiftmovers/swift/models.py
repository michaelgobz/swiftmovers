from django.db import models

from uuid import uuid4


# Create your models here.

class Swift(models.Model):
    UUID = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.TextField(blank=True)
    packageWeight = models.IntegerField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_change = models.DateTimeField(auto_now=True)
    last_address = models.TextField(editable=True,default="kampala")
