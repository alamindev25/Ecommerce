from rest_framework import serializers
from .models import Transaction, TransactionItem

class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model"""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'transaction_date', 'payment_method', 
                 'is_paid', 'due_date', 'notes', 'supplier', 'supplier_name', 
                 'external_party_name', 'total_amount']


class TransactionItemSerializer(serializers.ModelSerializer):
    """Serializer for TransactionItem model"""
    product_name = serializers.CharField(source='product.subcategory.name', read_only=True)
    unit_symbol = serializers.CharField(source='unit.symbol', read_only=True)
    
    class Meta:
        model = TransactionItem
        fields = ['id', 'product', 'product_name', 'unit', 'unit_symbol', 
                 'quantity', 'price_per_unit', 'total_price', 'pieces_count']


class TransactionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Transaction with items"""
    items = TransactionItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'transaction_date', 'payment_method', 
                 'is_paid', 'due_date', 'notes', 'supplier', 'supplier_name', 
                 'external_party_name', 'total_amount', 'items']
