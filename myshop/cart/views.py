from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def cart_add(request: HttpRequest, product_id: int) -> HttpResponseRedirect:
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    add_product_form = CartAddProductForm(data=request.POST)

    if add_product_form.is_valid():
        cd = add_product_form.cleaned_data
        cart.add(
            product, quantity=cd["quantity"], override_quantity=cd["override_quantity"]
        )

    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request: HttpRequest, product_id: int) -> HttpResponseRedirect:
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("cart:cart_detail")


def cart_detail(request: HttpRequest) -> HttpResponse:
    cart = Cart(request)
    for item in cart:
        item["update_quantity_form"] = CartAddProductForm(
            initial={"quantity": item["quantity"], "override_quantity": True}
        )
    return render(request, "cart/detail.html", {"cart": cart})
