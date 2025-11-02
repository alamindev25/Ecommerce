from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404
from decimal import Decimal, ROUND_HALF_UP
from .models import Shop, ShopProduct, ProductPrice
from product.models import Unit
from transaction.models import Transaction, TransactionItem
from .serializers import *


class ShopViewSet(viewsets.ModelViewSet):
    """ViewSet for Shop model"""
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter shops by owner"""
        return Shop.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        """Set the owner to current user"""
        serializer.save(owner=self.request.user)


class ShopProductViewSet(viewsets.ModelViewSet):
    """ViewSet for ShopProduct model"""
    queryset = ShopProduct.objects.all()
    serializer_class = ShopProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter products by user's shops"""
        user_shops = Shop.objects.filter(owner=self.request.user)
        queryset = ShopProduct.objects.filter(shop__in=user_shops)
        
        # Filter by shop if provided
        shop_id = self.request.query_params.get('shop_id')
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
            
        # Filter by category if provided
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(subcategory__category_id=category_id)
            
        return queryset
    
    def perform_create(self, serializer):
        """Set the shop from request data"""
        shop_id = self.request.data.get('shop_id')
        shop = get_object_or_404(Shop, id=shop_id, owner=self.request.user)
        serializer.save(shop=shop)
    
    @action(detail=False, methods=['post'])
    def add_product(self, request):
        """Add a new product to shop with initial stock and prices"""
        serializer = AddProductToShopSerializer(data=request.data)
        if serializer.is_valid():
            shop_id = request.data.get('shop_id')
            shop = get_object_or_404(Shop, id=shop_id, owner=request.user)
            
            with transaction.atomic():
                # Get the required fields
                quantity = serializer.validated_data['quantity']
                buying_price_per_unit = serializer.validated_data['buying_price_per_unit']
                payment_method = serializer.validated_data['payment_method']
                due_amount = serializer.validated_data.get('due_amount', 0)
                due_date = serializer.validated_data.get('due_date')
                initial_stock = serializer.validated_data.get('initial_stock', 0)
                notes = serializer.validated_data.get('notes', '')
                
                # Create or get existing product
                shop_product, created = ShopProduct.objects.get_or_create(
                    shop=shop,
                    subcategory=serializer.validated_data['subcategory'],
                    defaults={'current_stock': initial_stock}  # Only set initial_stock for new products
                )
                
                # For existing products, ignore initial_stock (it's historical data)
                # Stock will be updated automatically by TransactionItem.save()
                
                # Add prices if provided
                prices_data = serializer.validated_data.get('prices', [])
                for price_data in prices_data:
                    unit = Unit.objects.get(id=price_data['unit_id'])
                    ProductPrice.objects.update_or_create(
                        product=shop_product,
                        unit=unit,
                        defaults={'price': price_data['price']}
                    )
                
                # Create transaction for the purchase
                transaction_created = False
                transaction_error = None
                
                try:
                    # Get the base unit from category
                    base_unit = shop_product.subcategory.category.base_unit
                    
                    if not base_unit:
                        raise ValueError(f"Category {shop_product.subcategory.category.name} has no base unit")
                    
                    # Handle supplier and external party
                    supplier_id = serializer.validated_data.get('supplier_id')
                    external_party_name = serializer.validated_data.get('external_party_name', 'Unknown')
                    
                    # Calculate payment status
                    total_amount = quantity * buying_price_per_unit
                    # If payment method is DUE, always mark as unpaid, otherwise check due_amount
                    is_paid = (payment_method != 'DUE') and (due_amount == 0)
                    
                    # Create the transaction
                    trans = Transaction.objects.create(
                        shop=shop,
                        transaction_type='BUY',
                        payment_method=payment_method,
                        is_paid=is_paid,
                        due_date=due_date,
                        supplier_id=supplier_id,
                        external_party_name=external_party_name,
                        notes=notes or f'Purchased {quantity} {base_unit.symbol} at {buying_price_per_unit} per unit'
                    )
                    
                    # Create transaction item with calculated total_price
                    # Ensure proper decimal formatting with exactly 2 decimal places
                    total_price = (Decimal(str(quantity)) * Decimal(str(buying_price_per_unit))).quantize(
                        Decimal('0.01'), rounding=ROUND_HALF_UP
                    )
                    transaction_item = TransactionItem(
                        transaction=trans,
                        product=shop_product,
                        unit=base_unit,
                        quantity=quantity,
                        price_per_unit=buying_price_per_unit,
                        total_price=total_price,
                        pieces_count=serializer.validated_data.get('pieces_count')
                    )
                    
                    # Validate and save
                    transaction_item.full_clean()
                    transaction_item.save()
                    transaction_created = True
                    
                except Exception as e:
                    # Log the error but don't fail the product creation
                    transaction_error = str(e)
                    print(f"Transaction creation failed: {transaction_error}")
                    import traceback
                    traceback.print_exc()
                        
                # Add transaction status to response
                response_data = ShopProductSerializer(shop_product).data
                response_data['transaction_created'] = transaction_created
                response_data['product_created'] = created
                response_data['quantity_purchased'] = quantity
                response_data['buying_price_per_unit'] = buying_price_per_unit
                response_data['payment_method'] = payment_method
                response_data['total_amount'] = quantity * buying_price_per_unit
                response_data['due_amount'] = due_amount
                response_data['is_paid'] = (payment_method != 'DUE') and (due_amount == 0)
                if transaction_error:
                    response_data['transaction_error'] = transaction_error
            
            return Response(
                response_data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """Manually update stock without creating transaction"""
        product = self.get_object()
        serializer = ManualStockUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Store old values for response
            old_stock = product.current_stock
            old_pieces_count = getattr(product, 'pieces_count', 0)
            
            # Update the product stock
            product.current_stock = serializer.validated_data['current_stock']
            
            # Update pieces_count if provided and field exists
            pieces_count = serializer.validated_data.get('pieces_count')
            if pieces_count is not None and hasattr(product, 'pieces_count'):
                product.pieces_count = pieces_count
            
            # Save the product
            product.save()
            
            # Prepare response
            response_data = ShopProductSerializer(product).data
            response_data.update({
                'manual_update': True,
                'old_stock': str(old_stock),
                'new_stock': str(product.current_stock),
                'old_pieces_count': old_pieces_count,
                'new_pieces_count': getattr(product, 'pieces_count', 0),
                'notes': serializer.validated_data.get('notes', ''),
                'stock_updated': True
            })
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def sell_product(self, request, pk=None):
        """Sell product and create sale transaction"""
        product = self.get_object()
        
        # Add product_id to request data
        data = request.data.copy()
        data['product_id'] = product.id
        
        serializer = SellProductSerializer(data=data)
        
        if serializer.is_valid():
            with transaction.atomic():
                try:
                    # Create sale transaction
                    due_amount = serializer.validated_data.get('due_amount', 0)
                    total_amount = serializer.validated_data['_total_amount']
                    
                    # Determine if payment is complete
                    payment_method = serializer.validated_data['payment_method']
                    is_paid = (payment_method != 'DUE') and (due_amount == 0)
                    
                    trans = Transaction.objects.create(
                        shop=product.shop,
                        transaction_type='SELL',
                        payment_method=serializer.validated_data['payment_method'],
                        external_party_name=serializer.validated_data.get('customer_name', ''),
                        notes=serializer.validated_data.get('notes', ''),
                        is_paid=is_paid,
                        due_date=serializer.validated_data.get('due_date')
                    )
                    
                    # Create transaction item for sell_product method
                    transaction_item = TransactionItem.objects.create(
                        transaction=trans,
                        product=product,
                        unit=serializer.validated_data['_unit'],
                        quantity=serializer.validated_data['quantity'],
                        price_per_unit=serializer.validated_data['selling_price_per_unit'],
                        pieces_count=serializer.validated_data.get('pieces_count')
                    )
                    
                    # Refresh product to get updated stock
                    product.refresh_from_db()
                    
                    # Prepare response
                    response_data = ShopProductSerializer(product).data
                    response_data.update({
                        'transaction_created': True,
                        'transaction_id': trans.id,
                        'quantity_sold': serializer.validated_data['quantity'],
                        'selling_price_per_unit': serializer.validated_data['selling_price_per_unit'],
                        'total_amount': total_amount,
                        'due_amount': due_amount,
                        'is_paid': is_paid,
                        'customer_name': serializer.validated_data.get('customer_name', ''),
                        'payment_method': serializer.validated_data['payment_method']
                    })
                    
                    return Response(response_data, status=status.HTTP_201_CREATED)
                    
                except Exception as e:
                    return Response(
                        {'error': f'Transaction creation failed: {str(e)}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def sell(self, request):
        """General selling endpoint - sell any product"""
        serializer = SellProductSerializer(data=request.data)
        
        if serializer.is_valid():
            product = serializer.validated_data['_product']
            
            # Check if user owns the shop
            if product.shop.owner != request.user:
                return Response(
                    {'error': 'You do not have permission to sell this product'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            with transaction.atomic():
                try:
                    # Create sale transaction
                    due_amount = serializer.validated_data.get('due_amount', 0)
                    total_amount = serializer.validated_data['_total_amount']
                    
                    # Determine if payment is complete
                    payment_method = serializer.validated_data['payment_method']
                    is_paid = (payment_method != 'DUE') and (due_amount == 0)
                    
                    trans = Transaction.objects.create(
                        shop=product.shop,
                        transaction_type='SELL',
                        payment_method=serializer.validated_data['payment_method'],
                        external_party_name=serializer.validated_data.get('customer_name', ''),
                        notes=serializer.validated_data.get('notes', ''),
                        is_paid=is_paid,
                        due_date=serializer.validated_data.get('due_date')
                    )
                    
                    # Create transaction item for general sell method
                    transaction_item = TransactionItem.objects.create(
                        transaction=trans,
                        product=product,
                        unit=serializer.validated_data['_unit'],
                        quantity=serializer.validated_data['quantity'],
                        price_per_unit=serializer.validated_data['selling_price_per_unit'],
                        pieces_count=serializer.validated_data.get('pieces_count')
                    )
                    
                    # Refresh product to get updated stock
                    product.refresh_from_db()
                    
                    # Prepare response
                    response_data = ShopProductSerializer(product).data
                    response_data.update({
                        'transaction_created': True,
                        'transaction_id': trans.id,
                        'quantity_sold': serializer.validated_data['quantity'],
                        'selling_price_per_unit': serializer.validated_data['selling_price_per_unit'],
                        'total_amount': total_amount,
                        'due_amount': due_amount,
                        'is_paid': is_paid,
                        'customer_name': serializer.validated_data.get('customer_name', ''),
                        'payment_method': serializer.validated_data['payment_method']
                    })
                    
                    return Response(response_data, status=status.HTTP_201_CREATED)
                    
                except Exception as e:
                    return Response(
                        {'error': f'Transaction creation failed: {str(e)}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_base_price(self, request, pk=None):
        """Update base selling price of a product"""
        product = self.get_object()
        serializer = UpdateProductBasePriceSerializer(data={
            'product_id': product.id,
            'base_price': request.data.get('base_price')
        })
        
        if serializer.is_valid():
            base_price = serializer.validated_data['base_price']
            
            # Update the base price by updating/creating price for base unit
            base_unit = product.subcategory.category.base_unit
            if not base_unit:
                return Response(
                    {'error': f'Category {product.subcategory.category.name} has no base unit'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            product_price, created = ProductPrice.objects.update_or_create(
                product=product,
                unit=base_unit,
                defaults={'price': base_price}
            )
            
            # Refresh product to get updated base_price
            product.refresh_from_db()
            
            response_data = ShopProductSerializer(product).data
            response_data['base_price_updated'] = True
            response_data['price_created'] = created
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def allowed_units(self, request, pk=None):
        """Get allowed units for this product"""
        product = self.get_object()
        
        # Get allowed units from the product's category
        allowed_units = product.subcategory.category.transaction_units.all()
        
        response_data = {
            'product_id': product.id,
            'product_name': product.subcategory.name,
            'category': product.subcategory.category.name,
            'base_unit': UnitSerializer(product.subcategory.category.base_unit).data,
            'allowed_units': UnitSerializer(allowed_units, many=True).data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)


class ProductPriceViewSet(viewsets.ModelViewSet):
    """ViewSet for ProductPrice model"""
    queryset = ProductPrice.objects.all()
    serializer_class = ProductPriceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter prices by user's products"""
        user_shops = Shop.objects.filter(owner=self.request.user)
        return ProductPrice.objects.filter(product__shop__in=user_shops)
    
    @action(detail=False, methods=['post'])
    def update_unit_price(self, request):
        """Update price for a specific product and unit"""
        serializer = UpdateProductPriceSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            unit_id = serializer.validated_data['unit_id']
            price = serializer.validated_data['price']
            
            # Get the product and ensure user owns it
            product = get_object_or_404(
                ShopProduct, 
                id=product_id, 
                shop__owner=request.user
            )
            unit = get_object_or_404(Unit, id=unit_id)
            
            # Update or create the price
            product_price, created = ProductPrice.objects.update_or_create(
                product=product,
                unit=unit,
                defaults={'price': price}
            )
            
            response_data = ProductPriceSerializer(product_price).data
            response_data['updated'] = not created
            response_data['created'] = created
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)