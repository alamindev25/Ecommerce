from django.db import models
from shop.models import Shop
from contacts.models import Supplier
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from product.models import Unit
from shop.models import ShopProduct
from django.utils import timezone


class Transaction(models.Model):
    """Base model for buying/selling transactions"""
    TRANSACTION_TYPE = [
        ('BUY', 'Purchase'),
        ('SELL', 'Sale'),
    ]
    
    PAYMENT_METHOD = [
        ('CASH', 'Cash'),
        ('BANK', 'Bank Transfer'),
        ('MOBILE', 'Mobile Banking'),
        ('DUE', 'Due'),
    ]
    
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPE)
    transaction_date = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD, default='CASH')
    is_paid = models.BooleanField(default=True)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # For external parties (suppliers or customers)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    external_party_name = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['transaction_date']),
            models.Index(fields=['payment_method']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['shop']),
        ]
    
    def __str__(self):
        party = self.supplier.name if self.supplier else (self.external_party_name or "Unknown")
        return f"{self.get_transaction_type_display()} - {self.shop.name} with {party} on {self.transaction_date.strftime('%Y-%m-%d')}"
    
    @property
    def total_amount(self):
        """Calculate total amount for the transaction"""
        return sum(item.total_price for item in self.items.all())
    
    def update_stock(self):
        """Update stock for all items in transaction"""
        for item in self.items.all():
            item.update_stock()
    

class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ShopProduct, on_delete=models.PROTECT)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0.001)])
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    base_price_at_transaction = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    pieces_count = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)], help_text="Number of pieces for stock tracking")

    class Meta:
        ordering = ['-transaction__transaction_date']
    
    def __str__(self):
        return f"{self.quantity} {self.unit.symbol} of {self.product} @ {self.price_per_unit}"
    

    def save(self, *args, **kwargs):
        # Auto-calculate total price using quantity (kg for hen, pieces for eggs)
        self.total_price = self.quantity * self.price_per_unit
        
        # Store base price at time of transaction
        if not self.base_price_at_transaction:
            self.base_price_at_transaction = self.product.base_price
        
        super().save(*args, **kwargs)
        
        # Update stock after save
        self.update_stock()
    
    @property
    def category_slug(self):
        """Get the category slug for dynamic checking"""
        return self.product.subcategory.category.slug
    
    @property
    def requires_weight(self):
        """Check if this product category requires weight tracking"""
        return self.product.subcategory.category.requires_weight_tracking()
    
    def get_base_quantity(self):
        """Convert quantity to base units"""
        if self.unit != self.product.subcategory.category.base_unit:
            return self.quantity * self.unit.conversion_to_base
        return self.quantity
    
    def update_stock(self):
        """Update product stock based on transaction type"""
        product = self.product
        base_quantity = self.get_base_quantity()
        
        if self.transaction.transaction_type == 'BUY':
            product.current_stock += base_quantity
            # Update pieces count if provided in transaction
            if self.pieces_count and hasattr(product, 'pieces_count'):
                # For countable units, convert pieces_count to base count using unit conversion
                if self.unit.is_countable:
                    base_pieces_count = self.pieces_count * self.unit.conversion_to_base
                    product.pieces_count += int(base_pieces_count)
                else:
                    # For non-countable units (like weight), add pieces_count directly
                    product.pieces_count += self.pieces_count
        elif self.transaction.transaction_type == 'SELL':
            product.current_stock -= base_quantity
            # Update pieces count if provided in transaction
            if self.pieces_count and hasattr(product, 'pieces_count'):
                # For countable units, convert pieces_count to base count using unit conversion
                if self.unit.is_countable:
                    base_pieces_count = self.pieces_count * self.unit.conversion_to_base
                    product.pieces_count -= int(base_pieces_count)
                else:
                    # For non-countable units (like weight), subtract pieces_count directly
                    product.pieces_count -= self.pieces_count
        
        # Prevent negative stock
        if product.current_stock < 0:
            product.current_stock = 0
        if hasattr(product, 'pieces_count') and product.pieces_count < 0:
            product.pieces_count = 0
        
        # Update both fields if pieces_count exists
        if hasattr(product, 'pieces_count'):
            product.save(update_fields=['current_stock', 'pieces_count'])
        else:
            product.save(update_fields=['current_stock'])
    
    def get_price_per_base_unit(self):
        """Get price per base unit"""
        if self.unit == self.product.subcategory.category.base_unit:
            return self.price_per_unit
        return self.price_per_unit * self.unit.conversion_to_base