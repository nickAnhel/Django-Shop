from django.urls import reverse
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.admin.views.decorators import staff_member_required

from cart.cart import Cart
from .models import OrderItem, Order
from .forms import OrderCreateForm
from .tasks import order_created


def order_create(request: HttpRequest) -> HttpResponse:
    cart = Cart(request)

    if request.method == "POST":
        form = OrderCreateForm(data=request.POST)

        if form.is_valid():
            order = form.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                )

            cart.clear()

            # launch asynchronous task
            order_created.delay(order.id)

            # return render(request, "orders/order/created.html", {"order": order})

            # Add order to session
            request.session["order_id"] = order.id
            # Redirect to payment
            return redirect(reverse("payment:process"))

    else:
        form = OrderCreateForm()

    return render(request, "orders/order/create.html", {"form": form})


@staff_member_required
def admin_order_detail(request: HttpRequest, order_id: int) -> HttpResponse:
    order = get_object_or_404(Order, id=order_id)
    return render(request, "admin/orders/order/detail.html", {"order": order})
