from django.contrib import admin
from .models import (
     Customer,
    Product,

)
 
# Register your models here.

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display =['id', 'user', 'name', 'division','district','thana','villorroad','zipcode']

@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display =['id', 'title','selling_price','discounted_price','description','brand','category','product_image']