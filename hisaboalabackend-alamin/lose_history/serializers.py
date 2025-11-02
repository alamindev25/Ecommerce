from rest_framework import serializers
from .models import LoseCategory, LoseHistory

class LoseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoseCategory
        fields = '__all__'

class LoseHistorySerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    lose_category_name = serializers.CharField(source='lose_category.name', read_only=True)

    class Meta:
        model = LoseHistory
        fields = ['id', 'shop', 'shop_name', 'lose_category_name', 'amount', 'description', 'date']
