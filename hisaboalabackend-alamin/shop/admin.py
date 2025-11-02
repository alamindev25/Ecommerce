from django.contrib import admin
from .models import Shop, ShopProduct, ProductPrice


class ProductPriceInline(admin.TabularInline):
    model = ProductPrice
    extra = 1


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'district', 'upozila', 'phone', 'created_at']
    list_filter = ['district', 'upozila', 'created_at']
    search_fields = ['name', 'owner__phone', 'phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ShopProduct)
class ShopProductAdmin(admin.ModelAdmin):
    list_display = ['shop', 'subcategory', 'current_stock', 'stock_display', 'base_price']
    list_filter = ['shop', 'subcategory__category']
    search_fields = ['shop__name', 'subcategory__name']
    inlines = [ProductPriceInline]
    readonly_fields = ['stock_display', 'base_price']


@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ['product', 'unit', 'price', 'base_price']
    list_filter = ['unit', 'product__subcategory__category']
    search_fields = ['product__shop__name', 'product__subcategory__name']
    readonly_fields = ['base_price']
