"""Costs map used by query complexity validator.

It's three levels deep dict of dicts:

- Type
- Fields
- Complexity

To set complexity cost for querying a field "likes" on type "User":

{
    "User": {
        "likes": {"complexity": 2}
    }
}

Querying above field will not increase query complexity by 1.

If field's complexity should be multiplied by value of argument (or arguments),
you can specify names of those arguments in "multipliers" list:

{
    "Query": {
        "products": {"complexity": 1, "multipliers": ["first", "last"]}
    }
}

This will result in following queries having cost of 100:

{ products(first: 100) { edges: { id } } }

{ products(last: 100) { edges: { id } } }

{ products(first: 10, last: 10) { edges: { id } } }

Notice that complexity is in last case is multiplied by all arguments.

Complexity is also multiplied recursively:

{
    "Query": {
        "products": {"complexity": 1, "multipliers": ["first", "last"]}
    },
    "Product": {
        "shippings": {"complexity": 1},
    }
}

This query will have cost of 200 (100 x 2 for each product):

{ products(first: 100) { complexity } }
"""

COST_MAP = {
    "Query": {
        "address": {"complexity": 1},
        "shippingZone": {"complexity": 1},
        "shippingZones": {"complexity": 1, "multipliers": ["first", "last"]},
        "user": {"complexity": 1},
    },
    "Checkout": {
        "availableCollectionPoints": {"complexity": 1},
        "availablePaymentGateways": {"complexity": 1},
        "availableShippingMethods": {"complexity": 1},
        "billingAddress": {"complexity": 1},
        "channel": {"complexity": 1},
        "giftCards": {"complexity": 1},
        "lines": {"complexity": 1},
        "shippingAddress": {"complexity": 1},
        "shippingMethod": {"complexity": 1},
        "shippingMethods": {"complexity": 1},
        "transactions": {"complexity": 1},
        "user": {"complexity": 1},
    },
}
