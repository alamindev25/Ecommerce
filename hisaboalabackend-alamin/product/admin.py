from django.contrib import admin
from .models import Unit, Category, SubCategory


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol', 'is_countable', 'conversion_to_base']
    list_filter = ['is_countable']
    search_fields = ['name', 'symbol']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'base_unit', 'requires_weight_tracking']
    list_filter = ['base_unit__is_countable']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['transaction_units']
    
    def requires_weight_tracking(self, obj):
        return obj.requires_weight_tracking()
    requires_weight_tracking.boolean = True
    requires_weight_tracking.short_description = 'Requires Weight'


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_predefined']
    list_filter = ['category', 'is_predefined']
    search_fields = ['name', 'category__name']
