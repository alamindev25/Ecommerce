from rest_framework import serializers
from .models import CostCategory, CostHistory

class CostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CostCategory
        fields = '__all__'

class CostHistorySerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    cost_category_name = serializers.CharField(source='cost_category.name', read_only=True)

    class Meta:
        model = CostHistory
        fields = ['id', 'shop', 'shop_name', 'cost_category_name', 'amount', 'description', 'date']
