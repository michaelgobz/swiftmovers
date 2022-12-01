from typing import  Tuple

from ....items.models import (
    Category,
    Product,
    ProductType,
)
from ...core.dataloaders import DataLoader

ProductIdAndChannelSlug = Tuple[int, str]


class CategoryByIdLoader(DataLoader):
    context_key = "category_by_id"

    def batch_load(self, keys):
        categories = Category.objects.using(self.database_connection_name).in_bulk(keys)
        return [categories.get(category_id) for category_id in keys]


class ProductByIdLoader(DataLoader):
    context_key = "product_by_id"

    def batch_load(self, keys):
        products = Product.objects.using(self.database_connection_name).in_bulk(keys)
        return [products.get(product_id) for product_id in keys]


class ProductTypeByIdLoader(DataLoader):
    context_key = "product_type_by_id"

    def batch_load(self, keys):
        product_types = ProductType.objects.using(
            self.database_connection_name
        ).in_bulk(keys)
        return [product_types.get(product_type_id) for product_type_id in keys]


class ProductTypeByProductIdLoader(DataLoader):
    context_key = "producttype_by_product_id"

    def batch_load(self, keys):
        def with_products(products):
            product_ids = {p.id for p in products}
            product_types_map = (
                ProductType.objects.using(self.database_connection_name)
                .filter(products__in=product_ids)
                .in_bulk()
            )
            return [product_types_map[product.product_type_id] for product in products]

        return ProductByIdLoader(self.context).load_many(keys).then(with_products)
