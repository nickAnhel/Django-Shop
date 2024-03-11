import csv
from datetime import datetime
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils.safestring import mark_safe
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ["product"]


def order_stripe_payment(obj: Order):
    url = obj.get_stripe_url()

    if obj.stripe_id:
        html = f"<a href={url} target='_blank'>{obj.stripe_id}</a>"
        return mark_safe(html)

    return ""


def export_to_csv(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
) -> HttpResponse:
    opts = modeladmin.model._meta
    content_dispodition = f"attachment; filename={opts.verbose_name}.csv"

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = content_dispodition

    writer = csv.writer(response)
    fields = [
        field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many
    ]

    writer.writerow([field.verbose_name for field in fields])

    for obj in queryset:
        data_row = []

        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime):
                value = value.strftime("%d/%m/%Y")
            data_row.append(value)

        writer.writerow(data_row)

    return response


order_stripe_payment.short_description = "Stripe payment"
export_to_csv.short_description = "Export to CSV"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "first_name",
        "last_name",
        "email",
        "address",
        "postal_code",
        "city",
        "paid",
        order_stripe_payment,
        "created",
        "updated",
    ]
    list_filter = ["paid", "created", "updated"]
    inlines = [OrderItemInline]
    actions = [export_to_csv]
