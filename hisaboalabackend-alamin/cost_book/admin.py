from django.contrib import admin
from .models import CostCategory, CostHistory

admin.site.register(CostCategory)

@admin.register(CostHistory)
class CostHistoryAdmin(admin.ModelAdmin):
    list_display = ('shop', 'cost_category', 'amount', 'date', 'description')
    list_filter = ('cost_category', 'date', 'shop')
    search_fields = ('description', 'shop__name', 'cost_category__name')
    date_hierarchy = 'date'
    ordering = ('-date',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('shop', 'cost_category')
