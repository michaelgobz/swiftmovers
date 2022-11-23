import logging

# logger = logging.getLogger(__name__)
# TODO: add support for login


class AddressType:
    BILLING = "billing"
    SHIPPING = "shipping"

    CHOICES = [
        (BILLING, "Billing"),
        (SHIPPING, "Shipping"),
    ]
