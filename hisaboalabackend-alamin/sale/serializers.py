from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.subcategory.name', read_only=True)
    unit_symbol = serializers.CharField(source='product.subcategory.category.base_unit.symbol', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'product', 'product_name', 'quantity', 'unit_price',
            'discount', 'total_price', 'unit_symbol'
        ]
        read_only_fields = ['total_price']

    def create(self, validated_data):
        # Calculate total_price if not provided
        if 'total_price' not in validated_data:
            quantity = validated_data['quantity']
            unit_price = validated_data['unit_price']
            discount = validated_data.get('discount', 0)
            validated_data['total_price'] = (quantity * unit_price) - discount

        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True, allow_null=True)

    class Meta:
        model = Order
        fields = [
            'id', 'shop', 'shop_name', 'customer', 'customer_name', 'order_date',
            'payment_method', 'subtotal', 'discount_total', 'final_total', 'due_amount', 'items'
        ]
        read_only_fields = ['order_date', 'subtotal', 'final_total']


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'shop', 'customer', 'payment_method', 'discount_total', 'due_amount', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        # Create order items and calculate totals
        subtotal = 0
        for item_data in items_data:
            # Calculate total_price if not provided
            if 'total_price' not in item_data:
                quantity = item_data['quantity']
                unit_price = item_data['unit_price']
                discount = item_data.get('discount', 0)
                item_data['total_price'] = (quantity * unit_price) - discount

            OrderItem.objects.create(order=order, **item_data)
            subtotal += item_data['total_price']

        # Update order totals
        order.subtotal = subtotal
        order.final_total = subtotal - order.discount_total
        order.save()

        return order

    def validate_items(self, value):
        """Validate that items list is not empty"""
        if not value:
            raise serializers.ValidationError("At least one item is required for an order.")
        return value

    def validate(self, data):
        """Validate the entire order data"""
        items_data = data.get('items', [])
        shop = data.get('shop')

        # Validate that all products belong to the same shop
        for item_data in items_data:
            product = item_data.get('product')
            if product.shop != shop:
                raise serializers.ValidationError(
                    f"Product {product.subcategory.name} does not belong to shop {shop.name}."
                )

        return data