from rest_framework import serializers
from .models import Shop, ShopProduct, ProductPrice
from product.models import SubCategory, Unit
from product.serializers import UnitSerializer

class ShopSerializer(serializers.ModelSerializer):
    """Serializer for Shop model"""
    owner_name = serializers.CharField(source='owner.phone', read_only=True)
    
    class Meta:
        model = Shop
        fields = ['id', 'name', 'district', 'upozila', 'address', 'logo', 
                 'cover_photo', 'phone', 'owner', 'owner_name', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']


class ProductPriceSerializer(serializers.ModelSerializer):
    """Serializer for ProductPrice model"""
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    unit_symbol = serializers.CharField(source='unit.symbol', read_only=True)
    
    class Meta:
        model = ProductPrice
        fields = ['id', 'unit', 'unit_name', 'unit_symbol', 'price']


class UpdateProductPriceSerializer(serializers.Serializer):
    """Serializer for updating product price for a specific unit"""
    product_id = serializers.IntegerField()
    unit_id = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate(self, data):
        """Validate product and unit exist and unit is allowed for this product"""
        try:
            product = ShopProduct.objects.get(id=data['product_id'])
            unit = Unit.objects.get(id=data['unit_id'])
            
            # Validate unit is allowed for this product's category
            if unit not in product.subcategory.category.transaction_units.all():
                raise serializers.ValidationError("This unit is not allowed for this product category")
                
        except ShopProduct.DoesNotExist:
            raise serializers.ValidationError("Product does not exist")
        except Unit.DoesNotExist:
            raise serializers.ValidationError("Unit does not exist")
            
        return data


class UpdateProductBasePriceSerializer(serializers.Serializer):
    """Serializer for updating product base price"""
    product_id = serializers.IntegerField()
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate_product_id(self, value):
        """Validate product exists"""
        try:
            ShopProduct.objects.get(id=value)
        except ShopProduct.DoesNotExist:
            raise serializers.ValidationError("Product does not exist")
        return value


class ShopProductSerializer(serializers.ModelSerializer):
    """Serializer for ShopProduct model"""
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    category_name = serializers.CharField(source='subcategory.category.name', read_only=True)
    category_slug = serializers.CharField(source='subcategory.category.slug', read_only=True)
    base_unit_symbol = serializers.CharField(source='subcategory.category.base_unit.symbol', read_only=True)
    stock_display = serializers.CharField(read_only=True)
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    prices = ProductPriceSerializer(many=True, read_only=True)
    allowed_units = serializers.SerializerMethodField()
    
    class Meta:
        model = ShopProduct
        fields = ['id', 'shop', 'subcategory', 'subcategory_name', 'category_name', 
                 'category_slug', 'current_stock', 'pieces_count', 'base_unit_symbol', 'stock_display', 
                 'base_price', 'prices', 'allowed_units']
        read_only_fields = ['shop']
    
    def get_allowed_units(self, obj):
        """Get allowed units for this product category"""
        # Only include allowed_units if specifically requested
        request = self.context.get('request')
        if request and request.query_params.get('include_units') == 'true':
            allowed_units = obj.subcategory.category.transaction_units.all()
            return UnitSerializer(allowed_units, many=True).data
        return None


class AddProductToShopSerializer(serializers.Serializer):
    """Serializer for adding product to shop"""
    subcategory = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all())
    initial_stock = serializers.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Stock amount for new products (no transaction created)")
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, help_text="Quantity to buy (required)")
    buying_price_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, help_text="Price per unit for buying (required)")
    payment_method = serializers.ChoiceField(
        choices=[('CASH', 'Cash'), ('BANK', 'Bank Transfer'), ('MOBILE', 'Mobile Banking'), ('DUE', 'Due')],
        required=True,
        help_text="Payment method (required)"
    )
    due_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0, help_text="Due amount if payment method is DUE or partial payment")
    due_date = serializers.DateField(required=False, allow_null=True, help_text="Due date for payment (optional)")
    supplier_id = serializers.IntegerField(required=False, allow_null=True, help_text="Supplier ID for the transaction")
    external_party_name = serializers.CharField(max_length=255, required=False, allow_blank=True, help_text="External party name if no supplier selected")
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True, help_text="Additional notes for the transaction")
    pieces_count = serializers.IntegerField(required=False, allow_null=True, help_text="Number of pieces for hen stock tracking")
    prices = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        required=False,
        help_text="List of price objects with unit_id and price"
    )
    
    def validate_prices(self, value):
        """Validate prices format"""
        for price_data in value:
            if 'unit_id' not in price_data or 'price' not in price_data:
                raise serializers.ValidationError("Each price must have unit_id and price")
            try:
                Unit.objects.get(id=price_data['unit_id'])
            except Unit.DoesNotExist:
                raise serializers.ValidationError(f"Unit with id {price_data['unit_id']} does not exist")
        return value
    
    def validate(self, data):
        """Validate supplier, external party, and payment data"""
        from contacts.models import Supplier
        
        supplier_id = data.get('supplier_id')
        external_party_name = data.get('external_party_name', '').strip()
        payment_method = data.get('payment_method')
        due_amount = data.get('due_amount', 0)
        due_date = data.get('due_date')
        
        # If supplier_id is provided, validate it exists
        if supplier_id:
            try:
                Supplier.objects.get(id=supplier_id)
            except Supplier.DoesNotExist:
                raise serializers.ValidationError("Supplier does not exist")
        
        # If no supplier and no external_party_name, set default
        if not supplier_id and not external_party_name:
            data['external_party_name'] = 'Unknown'
        
        # Validate due amount and payment method
        if payment_method == 'DUE' and due_amount <= 0:
            raise serializers.ValidationError("Due amount must be greater than 0 when payment method is DUE")
        
        # Calculate if this is a partial payment
        total_amount = data['quantity'] * data['buying_price_per_unit']
        if due_amount > total_amount:
            raise serializers.ValidationError("Due amount cannot be greater than total amount")
        
        return data


class SellProductSerializer(serializers.Serializer):
    """Serializer for selling products with transaction creation"""
    product_id = serializers.IntegerField(help_text="ID of the product to sell")
    quantity = serializers.DecimalField(max_digits=12, decimal_places=3, help_text="Quantity to sell")
    unit_id = serializers.IntegerField(help_text="Unit ID for the sale")
    selling_price_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="Selling price per unit")
    payment_method = serializers.ChoiceField(
        choices=[('CASH', 'Cash'), ('BANK', 'Bank Transfer'), ('MOBILE', 'Mobile Banking'), ('DUE', 'Due')],
        help_text="Payment method for the sale (required)"
    )
    customer_name = serializers.CharField(max_length=255, required=False, allow_blank=True, help_text="Customer name for the sale")
    notes = serializers.CharField(required=False, allow_blank=True, help_text="Additional notes for the sale")
    pieces_count = serializers.IntegerField(required=False, allow_null=True, help_text="Number of pieces for hen stock tracking")
    due_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0, help_text="Due amount if partial payment")
    due_date = serializers.DateField(required=False, allow_null=True, help_text="Due date for payment")

    def validate(self, data):
        """Validate the selling data"""
        try:
            # Get product and unit
            product = ShopProduct.objects.get(id=data['product_id'])
            unit = Unit.objects.get(id=data['unit_id'])
            
            # Check if product has enough stock
            requested_quantity = data['quantity']
            base_quantity = requested_quantity
            if unit != product.subcategory.category.base_unit:
                base_quantity = requested_quantity * unit.conversion_to_base
            
            if product.current_stock < base_quantity:
                raise serializers.ValidationError(f"Insufficient stock. Available: {product.current_stock} {product.subcategory.category.base_unit.symbol}, Requested: {base_quantity} {product.subcategory.category.base_unit.symbol}")
            
            # Validate unit is allowed for this category
            if unit not in product.subcategory.category.transaction_units.all():
                raise serializers.ValidationError(f"Unit {unit.name} is not allowed for {product.subcategory.category.name} category")
            
            # Validate due amount
            total_amount = data['quantity'] * data['selling_price_per_unit']
            due_amount = data.get('due_amount', 0)
            if due_amount > total_amount:
                raise serializers.ValidationError("Due amount cannot be greater than total amount")
            
            # Store validated objects for later use
            data['_product'] = product
            data['_unit'] = unit
            data['_total_amount'] = total_amount
            
        except ShopProduct.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        except Unit.DoesNotExist:
            raise serializers.ValidationError("Unit not found")
        
        return data


class StockUpdateSerializer(serializers.Serializer):
    """Serializer for updating stock with transaction creation"""
    product_id = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=3)
    unit_id = serializers.IntegerField()
    price_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = serializers.ChoiceField(choices=[('BUY', 'Purchase'), ('SELL', 'Sale')])
    supplier_id = serializers.IntegerField(required=False, allow_null=True)
    external_party_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(
        choices=[('CASH', 'Cash'), ('BANK', 'Bank Transfer'), ('MOBILE', 'Mobile Banking'), ('DUE', 'Due')],
        help_text="Payment method (required)"
    )
    
    def validate(self, data):
        """Validate the stock update data"""
        try:
            product = ShopProduct.objects.get(id=data['product_id'])
            unit = Unit.objects.get(id=data['unit_id'])
            
            # Validate unit is allowed for this category
            if unit not in product.subcategory.category.transaction_units.all():
                raise serializers.ValidationError("This unit is not allowed for this product category")
                
        except ShopProduct.DoesNotExist:
            raise serializers.ValidationError("Product does not exist")
        except Unit.DoesNotExist:
            raise serializers.ValidationError("Unit does not exist")
            
        return data


class ManualStockUpdateSerializer(serializers.Serializer):
    """Serializer for manually updating stock without creating transactions"""
    current_stock = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0, help_text="New stock quantity")
    pieces_count = serializers.IntegerField(required=False, allow_null=True, min_value=0, help_text="Number of pieces for stock tracking (optional)")
    notes = serializers.CharField(required=False, allow_blank=True, help_text="Notes for the stock update")

