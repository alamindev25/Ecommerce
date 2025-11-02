from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated



class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Transaction model - Read only"""
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter transactions by user's shops"""
        user_shops = Shop.objects.filter(owner=self.request.user)
        queryset = Transaction.objects.filter(shop__in=user_shops)
        
        # Filter by shop if provided
        shop_id = self.request.query_params.get('shop_id')
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
            
        # Filter by transaction type if provided
        transaction_type = self.request.query_params.get('transaction_type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
            
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Get transaction details with items"""
        instance = self.get_object()
        serializer = TransactionDetailSerializer(instance)
        return Response(serializer.data)
