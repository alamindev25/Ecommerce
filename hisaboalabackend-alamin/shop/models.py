from django.db import models
from django.contrib.auth import get_user_model
from product.models import SubCategory, Unit
from django.core.validators import MinValueValidator
User = get_user_model()


class Shop(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shops')
    name = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    upozila = models.CharField(max_length=100)
    address = models.TextField()
    logo = models.ImageField(upload_to='shop_logos/', null=True, blank=True)
    cover_photo = models.ImageField(upload_to='shop_covers/', null=True, blank=True)
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ShopProduct(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.PROTECT)
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    pieces_count = models.IntegerField(default=0, validators=[MinValueValidator(0)], help_text="Number of pieces for stock tracking")

    class Meta:
        unique_together = ('shop', 'subcategory')
        ordering = ['subcategory__name']

    def __str__(self):
        return f"{self.shop.name} - {self.subcategory.name}"

    @property
    def base_price(self):
        """Get price in the category's base unit"""
        base_unit = self.subcategory.category.base_unit
        price_obj = self.prices.filter(unit=base_unit).first()
        return price_obj.price if price_obj else 0

    def stock_display(self):
        """Generate human-readable stock display"""
        category = self.subcategory.category
        return category.get_stock_display(self.current_stock)



class ProductPrice(models.Model):
    product = models.ForeignKey(ShopProduct, on_delete=models.CASCADE, related_name='prices')
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])

    class Meta:
        unique_together = ('product', 'unit')
        ordering = ['unit__name']

    def __str__(self):
        return f"{self.product} @ {self.price}/{self.unit.symbol}"

    @property
    def base_price(self):
        """Get price in the category's base unit"""
        base_unit = self.product.subcategory.category.base_unit

        # If this price is for the base unit, return it directly
        if self.unit == base_unit:
            return self.price

        # Convert to base unit using conversion factors
        return self.price / self.unit.conversion_to_base