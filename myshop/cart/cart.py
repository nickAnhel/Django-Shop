from decimal import Decimal
from typing import Generator
from django.conf import settings
from django.http import HttpRequest

from shop.models import Product


class Cart:
    def __init__(self, request: HttpRequest) -> None:
        """
        Initializes cart
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(
        self, product: Product, quantity: int = 1, override_quantty: bool = False
    ) -> None:
        """
        Adds product to cart or update it's amount
        """
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": str(product.price)}

        if override_quantty:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity

        self.save()

    def save(self) -> None:
        """
        Marks session as changed to ensure the preservation
        """
        self.session.modified = True

    def remove(self, product: Product) -> None:
        """
        Removes product from the cart
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self) -> Generator[dict, None, None]:
        """
        Iterates the cart
        """
        products_ids = self.cart.keys()
        products = Product.objects.filter(id__in=products_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]["product"] = product

        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self) -> int:
        """
        Counts cart products
        """
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self) -> Decimal:
        """
        Returns total price of products in the cart
        """
        return sum(
            Decimal(item["price"]) * item["quantity"] for item in self.cart.values()
        )

    def clear(self) -> None:
        """
        Clears the cart
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()