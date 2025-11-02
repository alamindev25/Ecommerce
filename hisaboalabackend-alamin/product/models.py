from django.db import models
from django.core.validators import MinValueValidator


class Unit(models.Model):
    name = models.CharField(max_length=50) #Fullname of unit
    symbol = models.CharField(max_length=10) # Symbol of unit
    is_countable = models.BooleanField(default=False) # Is the unit countable? Like Dozen is countable but kg is not
    conversion_to_base = models.DecimalField(max_digits=10, decimal_places=2, default=1.00, validators=[MinValueValidator(0.01)]) # Conversion factor to base unit like for Dozen 12 to get 1 

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)  # For dynamic category checking
    base_unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name='base_unit_categories')
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True)
    transaction_units = models.ManyToManyField(Unit, related_name='transaction_unit_categories')
    
    def __str__(self):
        return self.name

    def requires_weight_tracking(self):
        """Determine if this category requires weight tracking based on base unit"""
        return not self.base_unit.is_countable

    def get_stock_display(self, stock):
        """Generate human-readable stock display"""
        if self.base_unit.is_countable:
            return f"{stock} pieces"
        return f"{stock} kg"

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='subcategory_icons/', blank=True, null=True)
    is_predefined = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('category', 'name')
        verbose_name_plural = "SubCategories"
        ordering = ['category__name', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"