from rest_framework import serializers
from .models import Category, SubCategory, Unit


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'base_unit', 'icon']


class SubCategorySerializer(serializers.ModelSerializer):
    """Serializer for SubCategory model"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'category', 'category_name', 'icon', 'is_predefined']


class UnitSerializer(serializers.ModelSerializer):
    """Serializer for Unit model"""
    class Meta:
        model = Unit
        fields = ['id', 'name', 'symbol', 'is_countable', 'conversion_to_base']