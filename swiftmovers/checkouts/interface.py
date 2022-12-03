from dataclasses import dataclass

from prices import Money, TaxedMoney


@dataclass
class CheckoutTaxedPricesData:
    """Store a checkout prices data with applied taxes.
    """

    undiscounted_price: TaxedMoney
    price_with_discounts: TaxedMoney
    price_with_sale: TaxedMoney


@dataclass
class CheckoutPricesData:
    """Store a checkout prices data without applied taxes.
    """

    undiscounted_price: Money
    price_with_discounts: Money
    price_with_sale: Money
