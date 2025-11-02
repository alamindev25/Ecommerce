from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Category model - Read only"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class SubCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for SubCategory model - Read only"""
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter subcategories by category if provided"""
        queryset = SubCategory.objects.all()
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


class UnitViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Unit model - Read only"""
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter units by category if provided"""
        queryset = Unit.objects.all()
        category_id = self.request.query_params.get('category_id')
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            queryset = category.transaction_units.all()
        return queryset
    

# API Views for specific operations
class CategorySubCategoriesAPIView(APIView):
    """Get subcategories for a specific category"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        subcategories = SubCategory.objects.filter(category=category)
        serializer = SubCategorySerializer(subcategories, many=True)
        return Response(serializer.data)


class CategoryUnitsAPIView(APIView):
    """Get available units for a specific category"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        units = category.transaction_units.all()
        serializer = UnitSerializer(units, many=True)
        return Response(serializer.data)