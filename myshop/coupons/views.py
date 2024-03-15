from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Coupon
from .forms import CouponAplyForm


@require_POST
def coupon_apply(request: HttpRequest) -> HttpResponseRedirect:
    now = timezone.now()
    form = CouponAplyForm(data=request.POST)

    if form.is_valid():
        code = form.cleaned_data["code"]

        try:
            coupon = Coupon.objects.get(
                code__iexact=code, valid_from__lte=now, valid_to__gte=now, active=True
            )
            request.session["coupon_id"] = coupon.id
        except Coupon.DoesNotExist:
            request.session["coupon_id"] = None

    return redirect("cart:cart_detail")
