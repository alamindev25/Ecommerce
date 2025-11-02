from django.contrib import admin
from .models import Transaction, TransactionItem


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 1
    readonly_fields = ['total_price', 'category_slug', 'requires_weight']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['shop', 'transaction_type', 'transaction_date', 'payment_method', 
                   'is_paid', 'total_amount']
    list_filter = ['transaction_type', 'payment_method', 'is_paid', 'shop']
    search_fields = ['shop__name', 'external_party_name', 'supplier__name']
    readonly_fields = ['total_amount', 'created_at']
    inlines = [TransactionItemInline]
    date_hierarchy = 'transaction_date'


@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'product', 'unit', 'quantity', 'price_per_unit', 
                   'total_price', 'pieces_count']
    list_filter = ['transaction__transaction_type', 'unit', 'product__subcategory__category']
    search_fields = ['product__subcategory__name', 'transaction__shop__name']
    readonly_fields = ['total_price', 'category_slug', 'requires_weight']
