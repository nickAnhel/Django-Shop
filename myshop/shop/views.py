from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404

from cart.forms import CartAddProductForm
from .models import Category, Product
from .recommender import Recommender


def product_list(request: HttpRequest, category_slug=None) -> HttpResponse:
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(
        request,
        "shop/product/list.html",
        {"category": category, "categories": categories, "products": products},
    )


def product_detail(request: HttpRequest, product_id, slug) -> HttpResponse:
    product = get_object_or_404(Product, id=product_id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()

    r = Recommender()
    recommended_products = r.suggest_products_for([product], 3)

    return render(
        request,
        "shop/product/detail.html",
        {"product": product, "cart_product_form": cart_product_form, "recommended_products": recommended_products},
    )
