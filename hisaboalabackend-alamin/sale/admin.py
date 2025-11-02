from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price', 'get_product_name')
    fields = ('get_product_name', 'quantity', 'unit_price', 'discount', 'total_price')

    def get_product_name(self, obj):
        return obj.product.subcategory.name if obj.product else ''
    get_product_name.short_description = 'Product'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop', 'customer', 'order_date', 'payment_method', 'subtotal', 'discount_total', 'final_total', 'due_amount', 'total_items')
    list_filter = ('order_date', 'shop', 'payment_method')
    search_fields = ('shop__name', 'customer__name')
    date_hierarchy = 'order_date'
    inlines = [OrderItemInline]
    readonly_fields = ('subtotal', 'final_total', 'order_date')

    def total_items(self, obj):
        return obj.items.count()
    total_items.short_description = 'Total Items'

    def total_items(self, obj):
        return obj.items.count()
    total_items.short_description = 'Total Items'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'get_product_name', 'quantity', 'unit_price', 'discount', 'total_price')
    list_filter = ('order__shop', 'product__subcategory__category')
    search_fields = ('order__shop__name', 'product__subcategory__name')
    readonly_fields = ('total_price',)

    def get_product_name(self, obj):
        return obj.product.subcategory.name
    get_product_name.short_description = 'Product'