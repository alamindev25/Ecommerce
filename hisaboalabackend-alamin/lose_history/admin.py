from django.contrib import admin
from .models import LoseCategory, LoseHistory

admin.site.register(LoseCategory)

@admin.register(LoseHistory)
class LoseHistoryAdmin(admin.ModelAdmin):
    list_display = ('shop', 'lose_category', 'amount', 'date', 'description')
    list_filter = ('lose_category', 'date', 'shop')
    search_fields = ('description', 'shop__name', 'lose_category__name')
    date_hierarchy = 'date'
    ordering = ('-date',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('shop', 'lose_category')
