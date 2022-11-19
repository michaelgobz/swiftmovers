from decimal import Decimal
from operator import attrgetter

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import JSONField  # type: ignore
from prices import Money
from django_prices.models import MoneyField
from django_mysql.models.fields import ListCharField
from ..core.taxes import zero_money
from ..checkouts.models import DeliveryCheckout
from . import (
    ChargeStatus,
    CustomPaymentChoices,
    StorePaymentMethod,
    TransactionAction,
    TransactionKind,
    TransactionStatus,
)


# Create your models here.

class TransactionItem(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=512, blank=True, default="")
    type = models.CharField(max_length=512, blank=True, default="")
    reference = models.CharField(max_length=512, blank=True, default="")
    available_actions = ListCharField(models.CharField(max_length=256,choices=TransactionAction.CHOICES,
                                      default=list), name="available_actions", max_length=256,)

    currency = models.CharField(max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH)

    amount_charged = MoneyField(amount_field="charged_value", currency_field="currency")
    charged_value = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal("0"),
    )
    amount_authorized = MoneyField(
        amount_field="authorized_value", currency_field="currency"
    )
    authorized_value = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal("0"),
    )
    amount_refunded = MoneyField(
        amount_field="refunded_value", currency_field="currency"
    )
    refunded_value = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal("0"),
    )
    amount_voided = MoneyField(amount_field="voided_value", currency_field="currency")
    voided_value = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal("0"),
    )

    checkout = models.ForeignKey(
        DeliveryCheckout,
        null=True,
        related_name="payment_transactions",
        on_delete=models.SET_NULL,
    )
    order = models.ForeignKey(
        "orders.Order",
        related_name="payment_transactions",
        null=True,
        on_delete=models.PROTECT,
    )


class TransactionEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=128,
        choices=TransactionStatus.CHOICES,
        default=TransactionStatus.SUCCESS,
    )
    reference = models.CharField(max_length=512, blank=True, default="")
    name = models.CharField(max_length=512, blank=True, default="")

    transaction = models.ForeignKey(
        TransactionItem, related_name="events", on_delete=models.CASCADE
    )


class Payment(models.Model):
    """A model that represents a single payment.

    All payment process related pieces of information are stored
    at the gateway level, we are operating on the reusable token
    which is a unique identifier of the customer for given gateway.

    Several payment methods can be used within a single order. Each payment
    method may consist of multiple transactions.

    with different metadata
    """

    gateway = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    to_confirm = models.BooleanField(default=False)
    partial = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    charge_status = models.CharField(
        max_length=20, choices=ChargeStatus.CHOICES, default=ChargeStatus.NOT_CHARGED
    )
    token = models.CharField(max_length=512, blank=True, default="")
    total = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal("0.0"),
    )
    captured_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal("0.0"),
    )
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH
    )

    checkout = models.ForeignKey(
        DeliveryCheckout, null=True, related_name="payments", on_delete=models.SET_NULL
    )
    order = models.ForeignKey(
        "orders.Order",
        related_name="payments",
        null=True,
        on_delete=models.PROTECT,
    )
    store_payment_method = models.CharField(
        max_length=11,
        choices=StorePaymentMethod.CHOICES,
        default=StorePaymentMethod.NONE,
    )

    billing_email = models.EmailField(blank=True)
    billing_first_name = models.CharField(max_length=256, blank=True)
    billing_last_name = models.CharField(max_length=256, blank=True)
    billing_company_name = models.CharField(max_length=256, blank=True)
    billing_address_1 = models.CharField(max_length=256, blank=True)
    billing_address_2 = models.CharField(max_length=256, blank=True)
    billing_city = models.CharField(max_length=256, blank=True)
    billing_city_area = models.CharField(max_length=128, blank=True)
    billing_postal_code = models.CharField(max_length=256, blank=True)
    billing_country_code = models.CharField(max_length=2, blank=True)
    billing_country_area = models.CharField(max_length=256, blank=True)

    cc_first_digits = models.CharField(max_length=6, blank=True, default="")
    cc_last_digits = models.CharField(max_length=4, blank=True, default="")
    cc_brand = models.CharField(max_length=40, blank=True, default="")
    cc_exp_month = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)], null=True, blank=True
    )
    cc_exp_year = models.PositiveIntegerField(
        validators=[MinValueValidator(1000)], null=True, blank=True
    )

    payment_method_type = models.CharField(max_length=256, blank=True)

    customer_ip_address = models.GenericIPAddressField(blank=True, null=True)
    extra_data = models.TextField(blank=True, default="")
    return_url = models.URLField(blank=True, null=True)
    psp_reference = models.CharField(
        max_length=512, null=True, blank=True, db_index=True
    )

    def __repr__(self):
        return "Payment(gateway=%s, is_active=%s, created=%s, charge_status=%s)" % (
            self.gateway,
            self.is_active,
            self.created_at,
            self.charge_status,
        )

    def get_last_transaction(self):
        return max(self.transactions.all(), default=None, key=attrgetter("pk"))

    def get_total(self):
        return Money(self.total, self.currency)

    def get_authorized_amount(self):
        money = zero_money(self.currency)

        # Query all the transactions which should be prefetched
        # to optimize db queries
        transactions = self.transactions.all()

        # There is no authorized amount anymore when capture is succeeded
        # since capture can only be made once, even it is a partial capture
        if any(
                [
                    txn.kind == TransactionKind.CAPTURE and txn.is_success
                    for txn in transactions
                ]
        ):
            return money

        # Filter the succeeded auth transactions
        authorized_txns = [
            txn
            for txn in transactions
            if txn.kind == TransactionKind.AUTH
               and txn.is_success
               and not txn.action_required
        ]

        # Calculate authorized amount from all succeeded auth transactions
        for txn in authorized_txns:
            money += Money(txn.amount, self.currency)

        # If multiple partial capture is supported later though it's unlikely,
        # the authorized amount should exclude the already captured amount here
        return money

    def get_captured_amount(self):
        return Money(self.captured_amount, self.currency)

    def get_charge_amount(self):
        """Retrieve the maximum capture possible."""
        return self.total - self.captured_amount

    @property
    def is_authorized(self):
        return any(
            [
                txn.kind == TransactionKind.AUTH
                and txn.is_success
                and not txn.action_required
                for txn in self.transactions.all()
            ]
        )

    @property
    def not_charged(self):
        return self.charge_status == ChargeStatus.NOT_CHARGED

    def can_authorize(self):
        return self.is_active and self.not_charged

    def can_capture(self):
        if not (self.is_active and self.not_charged):
            return False
        return True

    def can_void(self):
        return self.not_charged and self.is_authorized

    def can_refund(self):
        can_refund_charge_status = (
            ChargeStatus.PARTIALLY_CHARGED,
            ChargeStatus.FULLY_CHARGED,
            ChargeStatus.PARTIALLY_REFUNDED,
        )
        return self.charge_status in can_refund_charge_status

    def can_confirm(self):
        return self.is_active and self.not_charged

    def is_manual(self):
        return self.gateway == CustomPaymentChoices.MANUAL


class Transaction(models.Model):
    """Represents a single payment operation.

    Transaction is an attempt to transfer money between your customer
    and siftmovers, with a chosen payment method.
    """

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    payment = models.ForeignKey(
        Payment, related_name="transactions", on_delete=models.PROTECT
    )
    token = models.CharField(max_length=512, blank=True, default="")
    kind = models.CharField(max_length=25, choices=TransactionKind.CHOICES)
    is_success = models.BooleanField(default=False)
    action_required = models.BooleanField(default=False)
    action_required_data = JSONField(
        blank=True, default=dict, encoder=DjangoJSONEncoder
    )
    currency = models.CharField(max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH)
    amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=Decimal("0.0"),
    )
    error = models.TextField(null=True)
    customer_id = models.CharField(max_length=256, null=True)
    gateway_response = JSONField(encoder=DjangoJSONEncoder)
    already_processed = models.BooleanField(default=False)
