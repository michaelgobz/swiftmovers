from django.db import models
from uuid import uuid4
import django_mysql
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    Permission,
    PermissionsMixin,
)

from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.db.models import JSONField  # type: ignore
from django.db.models import Q, QuerySet, Value
from django.db.models.expressions import Exists, OuterRef
from django.forms.models import model_to_dict
from django.utils import timezone
from django.utils.crypto import get_random_string
from django_countries.fields import Country, CountryField
from phonenumber_field.modelfields import PhoneNumber, PhoneNumberField


# Create your models here.


class Account(models.Model):
    UUID = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    FirstName = models.TextField(blank=True)
    LastName = ""
    Address = ""
    packageWeight = models.IntegerField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_change = models.DateTimeField(auto_now=True)
    pass
