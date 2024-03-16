import redis
from django.conf import settings

from .models import Product


r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


class Recommender:
    def get_product_key(self, product_id: int) -> str:
        return f"product:{product_id}:purchased_with"

    def products_bought(self, products: list[Product]) -> None:
        product_ids = [p.id for p in products]

        for product_id in product_ids:
            for with_id in product_ids:
                if product_id != with_id:
                    # Increment score for product purchased together
                    r.zincrby(self.get_product_key(product_id), 1, with_id)

    def suggest_products_for(self, products: list[Product], max_results: int = 6):
        product_ids = [p.id for p in products]

        if len(products) == 1:
            suggestions = r.zrange(self.get_product_key(product_ids[0]), 0, -1, desc=True)[:max_results]

        else:
            # Generate the temporary key for products
            flat_ids = "".join([str(id) for id in product_ids])
            tmp_key = f"tmp_{flat_ids}"

            # Multiple products, combine scores of all products
            # Store the resulting sorted set in a temporary key
            keys = [self.get_product_key(id) for id in product_ids]
            r.zunionstore(tmp_key, keys)

            # Remove ids for the products the recommendation is for
            r.zrem(tmp_key, *product_ids)

            # Get the product ids by their score, descendant sort
            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_results]

            # Remove the temporary key
            r.delete(tmp_key)

        suggested_products_ids = [int(id) for id in suggestions]

        # Get suggested products and sort by order of appearance
        suggested_products = list(Product.objects.filter(id__in=suggested_products_ids))
        suggested_products.sort(key=lambda x: suggested_products_ids.index(x.id))

        return suggested_products
