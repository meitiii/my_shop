from django.contrib import admin
from .models import Order, OrderItem, Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'discount_percent',
        'discount_amount',
        'valid_from',
        'valid_to',
        'active',
    )

    list_filter = (
        'active',
        'valid_from',
        'valid_to',
    )

    search_fields = (
        'code',
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('variant', 'price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'status',
        'total_price',
        'created_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'user__username',
        'id',
    )

    inlines = [OrderItemInline]